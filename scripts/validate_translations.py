#!/usr/bin/env python3
"""
validate_translations.py — Validate and compare translations across all KB sources.

Compares:
  1. Coverage: which chunks have EN/RU translations
  2. Claude Haiku (stored in chunk_content) vs fine-tuned M2M model
  3. Term match rate for automotive glossary

Usage:
    python scripts/validate_translations.py
    python scripts/validate_translations.py --n-samples 20 --source pdf_l7_zh_full
    python scripts/validate_translations.py --no-model   # coverage report only (fast)

Output:
    logs/validation_report.md — full report
    logs/validation_samples.jsonl — per-sample comparison data
"""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import io
import time
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("validate")

ROOT     = Path(__file__).resolve().parent.parent
KB_DIR   = ROOT / "knowledge-base"
LOG_DIR  = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

FINETUNED_MODEL = "Petr117/m2m-diagnostica-automotive"


# ---------------------------------------------------------------------------
# Coverage report
# ---------------------------------------------------------------------------

def coverage_report(conn: sqlite3.Connection) -> str:
    """Generate markdown coverage table per source."""
    rows = conn.execute("""
        SELECT
            c.source,
            c.source_language,
            COUNT(DISTINCT c.id) as total,
            COUNT(DISTINCT CASE WHEN cc_en.lang='en' THEN c.id END) as has_en,
            COUNT(DISTINCT CASE WHEN cc_ru.lang='ru' THEN c.id END) as has_ru
        FROM chunks c
        LEFT JOIN chunk_content cc_en ON cc_en.chunk_id = c.id AND cc_en.lang = 'en'
        LEFT JOIN chunk_content cc_ru ON cc_ru.chunk_id = c.id AND cc_ru.lang = 'ru'
        GROUP BY c.source, c.source_language
        ORDER BY total DESC
    """).fetchall()

    lines = [
        "## Translation Coverage by Source\n",
        "| Source | Lang | Total | EN | EN% | RU | RU% | Missing |",
        "|--------|------|-------|----|----|-----|-----|---------|",
    ]
    total_chunks = total_en = total_ru = 0
    for src, slang, total, has_en, has_ru in rows:
        en_pct = 100 * has_en / total if total else 0
        ru_pct = 100 * has_ru / total if total else 0
        missing = total - max(has_en, has_ru)
        lines.append(
            f"| {src[:35]} | {slang} | {total} | {has_en} | {en_pct:.0f}% | {has_ru} | {ru_pct:.0f}% | {missing} |"
        )
        total_chunks += total
        total_en += has_en
        total_ru += has_ru

    lines.append(
        f"| **TOTAL** | - | **{total_chunks}** | **{total_en}** | **{100*total_en/total_chunks:.0f}%** "
        f"| **{total_ru}** | **{100*total_ru/total_chunks:.0f}%** | **{total_chunks - max(total_en, total_ru)}** |"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Translator quality comparison
# ---------------------------------------------------------------------------

def load_finetuned(device: str):
    import torch
    from transformers import M2M100ForConditionalGeneration, AutoTokenizer
    log.info("Loading fine-tuned model %s on %s...", FINETUNED_MODEL, device)
    tok   = AutoTokenizer.from_pretrained(FINETUNED_MODEL)
    model = M2M100ForConditionalGeneration.from_pretrained(
        FINETUNED_MODEL,
        torch_dtype=torch.float16 if "cuda" in device else torch.float32,
    ).to(device)
    model.eval()
    log.info("Model loaded.")
    return model, tok


def translate_m2m(model, tok, texts: list[str], tgt_lang: str, device: str) -> list[str]:
    """Translate list of texts with T5-prefix style."""
    import torch
    prefixed = [f"translate to {tgt_lang}: {t}" for t in texts]
    enc = tok(prefixed, return_tensors="pt", padding=True, truncation=True,
              max_length=256).to(device)
    with torch.no_grad():
        ids = model.generate(**enc, max_new_tokens=256, num_beams=4)
    return [tok.decode(i, skip_special_tokens=True) for i in ids]


def bleu_score(hyps: list[str], refs: list[str]) -> float:
    import sacrebleu
    return round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2)


def term_match_rate(text: str, terms: list[str]) -> float:
    text_low = text.lower()
    matched = sum(1 for t in terms if t.lower() in text_low)
    return matched / len(terms) if terms else 0.0


def load_glossary_terms(lang: str) -> list[str]:
    """Load target-language glossary terms for term matching."""
    gpath = ROOT / "дополнительно" / "полный глоссарий" / "полный глоссарий" / "automotive-glossary-5lang.json"
    if not gpath.exists():
        return []
    glossary = json.loads(gpath.read_text(encoding="utf-8"))
    terms = []
    for entry in glossary.get("terms", []):
        val = entry.get(lang) or entry.get(f"translation_{lang}")
        if val:
            terms.append(str(val))
    return terms[:200]  # limit to 200 most common


# ---------------------------------------------------------------------------
# Sample comparison
# ---------------------------------------------------------------------------

def compare_samples(
    conn: sqlite3.Connection,
    model, tok,
    device: str,
    n_samples: int,
    source_filter: str | None,
    tgt_lang: str = "ru",
) -> list[dict]:
    """
    Pull n_samples ZH chunks that have Claude translations, run fine-tuned M2M,
    compute BLEU vs Claude reference.
    """
    source_clause = f"AND c.source = '{source_filter}'" if source_filter else ""
    rows = conn.execute(f"""
        SELECT c.id, c.title, c.content, cc.title as cc_title, cc.content as cc_content
        FROM chunks c
        JOIN chunk_content cc ON cc.chunk_id = c.id
        WHERE c.source_language = 'zh'
          AND cc.lang = '{tgt_lang}'
          AND cc.translated_by LIKE 'claude-%'
          AND length(c.content) BETWEEN 50 AND 500
          {source_clause}
        ORDER BY RANDOM()
        LIMIT {n_samples}
    """).fetchall()

    if not rows:
        log.warning("No samples found for comparison (lang=%s source=%s)", tgt_lang, source_filter)
        return []

    zh_texts   = [r[2] for r in rows]
    claude_refs = [r[4] for r in rows]

    log.info("Translating %d samples with fine-tuned M2M...", len(rows))
    t0 = time.time()
    # Process in mini-batches to avoid OOM
    m2m_hyps: list[str] = []
    bs = 4
    for i in range(0, len(zh_texts), bs):
        batch = zh_texts[i:i+bs]
        m2m_hyps.extend(translate_m2m(model, tok, batch, tgt_lang, device))
    elapsed = time.time() - t0
    log.info("Done in %.1f s (%.2f s/sample)", elapsed, elapsed / len(rows))

    ru_terms = load_glossary_terms(tgt_lang)
    results = []
    for row, zh, ref, m2m in zip(rows, zh_texts, claude_refs, m2m_hyps):
        chunk_id, title = row[0], row[1]
        results.append({
            "chunk_id":    chunk_id,
            "title":       title,
            "zh_source":   zh[:300],
            "claude_ref":  ref[:300],
            "m2m_output":  m2m[:300],
            "bleu_m2m":    bleu_score([m2m], [ref]),
            "term_claude": round(term_match_rate(ref, ru_terms), 3),
            "term_m2m":    round(term_match_rate(m2m, ru_terms), 3),
        })

    corpus_bleu = bleu_score(m2m_hyps, claude_refs)
    log.info("Corpus BLEU (M2M vs Claude/%s): %.2f", tgt_lang, corpus_bleu)
    return results


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_report(
    coverage_md: str,
    samples: list[dict],
    args: argparse.Namespace,
    conn: sqlite3.Connection,
) -> str:
    # Summary stats
    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    total_cache  = conn.execute("SELECT COUNT(*) FROM translation_cache").fetchone()[0]
    cc_en = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE lang='en'").fetchone()[0]
    cc_ru = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE lang='ru'").fetchone()[0]

    lines = [
        "# KB Translation Validation Report\n",
        f"**Date**: 2026-02-28  ",
        f"**Total chunks**: {total_chunks}  ",
        f"**Translation cache entries**: {total_cache}  ",
        f"**chunk_content EN**: {cc_en}  ",
        f"**chunk_content RU**: {cc_ru}  ",
        "",
        coverage_md,
        "",
    ]

    if samples:
        corpus_bleu = bleu_score([s["m2m_output"] for s in samples],
                                 [s["claude_ref"] for s in samples])
        avg_term_claude = sum(s["term_claude"] for s in samples) / len(samples)
        avg_term_m2m    = sum(s["term_m2m"]    for s in samples) / len(samples)

        lines += [
            f"## Fine-tuned M2M vs Claude Reference ({args.tgt_lang.upper()})\n",
            f"| Metric | Claude (ref) | Fine-tuned M2M |",
            f"|--------|-------------|----------------|",
            f"| Corpus BLEU | 100 (reference) | {corpus_bleu} |",
            f"| Avg term match | {avg_term_claude:.1%} | {avg_term_m2m:.1%} |",
            f"| Samples | {len(samples)} | {len(samples)} |",
            "",
            "### Sample Translations\n",
        ]

        for i, s in enumerate(samples[:10]):
            lines += [
                f"#### Sample {i+1} — {s['title'][:60]}",
                f"**ZH**: {s['zh_source'][:200]}",
                "",
                f"**Claude (ref)**: {s['claude_ref'][:200]}",
                "",
                f"**M2M fine-tuned** (BLEU={s['bleu_m2m']}): {s['m2m_output'][:200]}",
                "",
                "---",
                "",
            ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate KB translations: coverage + Claude vs M2M comparison.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default="knowledge-base/kb.db")
    parser.add_argument("--no-model", action="store_true",
                        help="Coverage report only — skip model loading")
    parser.add_argument("--n-samples", type=int, default=20,
                        help="Number of chunks to compare")
    parser.add_argument("--source", default=None,
                        help="Filter to specific source (e.g. pdf_l7_zh_full)")
    parser.add_argument("--tgt-lang", default="ru",
                        help="Target language for comparison (ru/en)")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    db_path = ROOT / args.db_path
    if not db_path.exists():
        log.error("kb.db not found: %s", db_path)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path), timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")

    coverage_md = coverage_report(conn)
    log.info("Coverage report ready.")

    samples: list[dict] = []
    if not args.no_model:
        model, tok = load_finetuned(args.device)
        samples = compare_samples(conn, model, tok, args.device,
                                  args.n_samples, args.source, args.tgt_lang)

    report_md = build_report(coverage_md, samples, args, conn)
    conn.close()

    out_md = LOG_DIR / "validation_report.md"
    out_md.write_text(report_md, encoding="utf-8")
    log.info("Report written: %s", out_md)

    if samples:
        out_jsonl = LOG_DIR / "validation_samples.jsonl"
        with open(out_jsonl, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        log.info("Samples written: %s", out_jsonl)

    # Print summary
    print("\n" + "=" * 60)
    print(coverage_md[:800])


if __name__ == "__main__":
    main()
