#!/usr/bin/env python3
"""
project_status.py - Polnaya analitika proekta LLCAR Diagnostica KB.

Zapusk:
    python scripts/project_status.py
    python scripts/project_status.py --json          # JSON-vyvod
    python scripts/project_status.py --check-api     # proverit API server
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

# Force UTF-8 output
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────────
ROOT = Path("C:/Diagnostica-KB-Package")
DB   = ROOT / "knowledge-base" / "kb.db"
LDB  = ROOT / "knowledge-base" / "lancedb"
API_URL = "http://localhost:8000"
# ──────────────────────────────────────────────

SEP  = "-" * 62
SEP2 = "=" * 62


def _db() -> sqlite3.Connection:
    return sqlite3.connect(DB)


def section(title: str) -> None:
    print(f"\n{SEP2}")
    print(f"  {title}")
    print(SEP2)


def row(label: str, value, ok: bool | None = None) -> None:
    marker = ""
    if ok is True:
        marker = "  [OK]"
    elif ok is False:
        marker = "  [!!]"
    print(f"  {label:<38} {value}{marker}")


# ────────────────────────────────────────────────────────────────────
# 1. SQLITE DATABASE
# ────────────────────────────────────────────────────────────────────

def check_sqlite() -> dict:
    out = {}
    if not DB.exists():
        print(f"  ❌ kb.db не найден: {DB}")
        return out

    db_mb = DB.stat().st_size / 1_048_576
    row("kb.db размер", f"{db_mb:.0f} MB", ok=True)

    with _db() as conn:
        tables = {r[0]: r[1] for r in conn.execute(
            "SELECT name, COALESCE((SELECT COUNT(*) FROM sqlite_master s2 "
            "WHERE s2.type='table' AND s2.name=m.name), 0) "
            "FROM sqlite_master m WHERE m.type='table' ORDER BY name"
        ).fetchall()}

        def count(tbl: str) -> int:
            try:
                return conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            except Exception:
                return -1

        # Chunks
        chunks = count("chunks")
        out["chunks"] = chunks
        row("chunks (всего)",            f"{chunks:,}", ok=chunks > 0)

        web = count_where(conn, "chunks", "layer = 'web_scraped'")
        out["web_scraped"] = web
        row("  └─ web_scraped",          f"{web:,}")

        # Per-layer breakdown
        layers = conn.execute(
            "SELECT layer, COUNT(*) FROM chunks GROUP BY layer ORDER BY COUNT(*) DESC"
        ).fetchall()
        for lyr, cnt in layers:
            row(f"  └─ {lyr}", f"{cnt:,}")

        # Chunk content
        cc = count("chunk_content")
        out["chunk_content"] = cc
        row("chunk_content (переводы)", f"{cc:,}", ok=cc > 0)

        langs = conn.execute(
            "SELECT lang, COUNT(*) FROM chunk_content GROUP BY lang ORDER BY COUNT(*) DESC"
        ).fetchall()
        for lang, cnt in langs:
            row(f"  └─ [{lang}]", f"{cnt:,}")

        # Translation cache
        tc = count("translation_cache")
        out["translation_cache"] = tc
        row("translation_cache",         f"{tc:,}", ok=tc > 0)

        tc_langs = conn.execute(
            "SELECT target_lang, COUNT(*) FROM translation_cache "
            "GROUP BY target_lang ORDER BY COUNT(*) DESC"
        ).fetchall()
        for lang, cnt in tc_langs:
            row(f"  └─ [{lang}]", f"{cnt:,}")

        # ColBERT
        cv = count("colbert_vectors")
        out["colbert_vectors"] = cv
        row("colbert_vectors",           f"{cv:,}", ok=cv > 0)

        # Images
        ci = count("chunk_images")
        captioned = count_where(conn, "chunk_images", "caption IS NOT NULL AND caption != ''")
        out["chunk_images"] = ci
        out["captioned"] = captioned
        row("chunk_images",              f"{ci:,}", ok=ci > 0)
        row("  └─ с caption",           f"{captioned:,} / {ci:,}", ok=captioned == ci)

        # DTC / Glossary
        dtc = count("chunk_dtc")
        gls = count("chunk_glossary")
        out["dtc_links"] = dtc
        out["glossary_links"] = gls
        row("DTC links",                 f"{dtc:,}")
        row("Glossary links",            f"{gls:,}")

        # Scraped content
        sc = count("scraped_content")
        sc_imp = count_where(conn, "scraped_content", "imported = 1")
        out["scraped_content"] = sc
        row("scraped_content",           f"{sc:,} (imported: {sc_imp})")

    return out


def count_where(conn, tbl: str, where: str) -> int:
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {where}").fetchone()[0]
    except Exception:
        return -1


# ────────────────────────────────────────────────────────────────────
# 2. LANCEDB
# ────────────────────────────────────────────────────────────────────

def check_lancedb() -> dict:
    out = {}
    if not LDB.exists():
        row("LanceDB директория", "❌ не найдена")
        return out

    ldb_mb = sum(f.stat().st_size for f in LDB.rglob("*") if f.is_file()) / 1_048_576
    row("LanceDB размер", f"{ldb_mb:.0f} MB")

    try:
        import lancedb
        db = lancedb.connect(str(LDB))
        tables = db.table_names()
        out["tables"] = tables

        for tname in tables:
            try:
                tbl = db.open_table(tname)
                n = tbl.count_rows()
                out[tname] = n
                row(f"  └─ {tname}", f"{n:,} строк", ok=n > 0)
            except Exception as e:
                row(f"  └─ {tname}", f"❌ {e}")
    except ImportError:
        row("lancedb", "❌ модуль не установлен")
    except Exception as e:
        row("LanceDB", f"❌ {e}")

    return out


# ────────────────────────────────────────────────────────────────────
# 3. API СЕРВЕР
# ────────────────────────────────────────────────────────────────────

def check_api() -> dict:
    out = {}
    try:
        import urllib.request
        req = urllib.request.urlopen(f"{API_URL}/health", timeout=5)
        data = json.loads(req.read().decode())
        out = data
        row("API сервер", f"{API_URL}  ✅")
        row("  chunks_total",   f"{data.get('chunks_total', '?'):,}")
        row("  lancedb",        "✅" if data.get("lancedb_available") else "❌")
        row("  embed_models",   "✅" if data.get("embed_models_available") else "❌")
        row("  colbert_rows",   f"{data.get('colbert_rows', '?'):,}")
        row("  content_rows",   f"{data.get('content_rows', '?'):,}")
        meta = data.get("kb_meta", {})
        row("  pplx model",     meta.get("pplx_model_id", "?")[-30:])
        row("  query model",    meta.get("pplx_query_model_id", "?")[-30:])
        row("  bge model",      meta.get("bge_model_id", "?"))
        row("  built",          meta.get("embeddings_build_timestamp", "?")[:19])
    except Exception as e:
        row("API сервер", f"❌ недоступен ({e})")
        out["status"] = "offline"
    return out


# ────────────────────────────────────────────────────────────────────
# 4. FINE-TUNING МОДЕЛИ
# ────────────────────────────────────────────────────────────────────

def check_finetune() -> dict:
    out = {}
    finetune_dir = Path("C:/tmp")

    hf_cache = Path("C:/Users/BAZA/.cache/huggingface/hub")
    pplx_v1 = hf_cache / "models--perplexity-ai--pplx-embed-v1-4b"
    pplx_ctx = hf_cache / "models--perplexity-ai--pplx-embed-context-v1-4b"
    row("pplx-embed-v1-4b (скачан)",     "✅" if pplx_v1.exists() else "❌",
        ok=pplx_v1.exists())
    row("pplx-embed-context-v1-4b",      "✅" if pplx_ctx.exists() else "❌",
        ok=pplx_ctx.exists())

    best_bleu = 0.0
    best_round = None

    for r_num in range(1, 10):
        rdir = finetune_dir / f"m2m-finetune-r{r_num}"
        if not rdir.exists():
            continue

        # Ищем trainer_state.json в checkpoint-подпапках
        state_file = None
        for ckpt in sorted(rdir.iterdir()):
            f = ckpt / "trainer_state.json" if ckpt.is_dir() else None
            if f and f.exists():
                state_file = f
                break

        bleu_scores = []
        best_ckpt = "?"
        if state_file:
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
                bleu_scores = [e.get("eval_bleu", 0) for e in state.get("log_history", [])
                               if "eval_bleu" in e]
                best_ckpt = Path(state.get("best_model_checkpoint", "")).name
            except Exception:
                pass

        if bleu_scores:
            top = max(bleu_scores)
            marker = " ← ЛУЧШИЙ" if top > best_bleu else ""
            if top > best_bleu:
                best_bleu = top
                best_round = r_num
            bleu_str = " / ".join(f"{b:.2f}" for b in bleu_scores)
            hf_note = " [→ HF]" if r_num == 6 else ""
            row(f"  Round {r_num} BLEU",
                f"{bleu_str}  best={best_ckpt}{marker}{hf_note}")
            out[f"r{r_num}_bleu"] = top
        else:
            row(f"  Round {r_num}", "нет trainer_state")

    if best_round:
        row("Лучший round", f"R{best_round}  BLEU={best_bleu:.2f}", ok=True)
        out["best_round"] = best_round
        out["best_bleu"] = best_bleu

    return out


# ────────────────────────────────────────────────────────────────────
# 5. ОБУЧАЮЩИЕ ДАННЫЕ
# ────────────────────────────────────────────────────────────────────

def check_training_data() -> dict:
    out = {}
    files = [
        ROOT / "knowledge-base" / "training_pairs_tier1.jsonl",
        ROOT / "knowledge-base" / "training_pairs_bridge.jsonl",
        ROOT / "training_pairs_session15.jsonl",
    ]
    total = 0
    for f in files:
        if f.exists():
            lines = sum(1 for _ in f.open(encoding="utf-8", errors="ignore"))
            total += lines
            mb = f.stat().st_size / 1_048_576
            row(f"  {f.name}", f"{lines:,} пар  ({mb:.1f} MB)")
        else:
            row(f"  {f.name}", "❌ не найден")
    row("Всего обучающих пар", f"{total:,}", ok=total > 0)
    out["total_pairs"] = total
    return out


# ────────────────────────────────────────────────────────────────────
# 6. SCRAPERS
# ────────────────────────────────────────────────────────────────────

def check_scrapers() -> dict:
    scrapers_dir = ROOT / "scripts" / "scrapers"
    scraper_files = list(scrapers_dir.glob("*.py")) if scrapers_dir.exists() else []
    row("Scrapers dir", str(scrapers_dir), ok=scrapers_dir.exists())
    row("Скраперы", ", ".join(f.stem for f in scraper_files if f.stem != "base_scraper"))

    with _db() as conn:
        try:
            rows = conn.execute(
                "SELECT source_name, lang, COUNT(*) n, SUM(imported) imp "
                "FROM scraped_content GROUP BY source_name, lang ORDER BY source_name"
            ).fetchall()
            if rows:
                for src, lang, n, imp in rows:
                    row(f"  {src} [{lang}]", f"{n} items, {imp or 0} imported")
        except Exception:
            pass
    return {}


# ────────────────────────────────────────────────────────────────────
# 7. GPU и ОКРУЖЕНИЕ
# ────────────────────────────────────────────────────────────────────

def check_env() -> dict:
    out = {}

    # Python
    row("Python", sys.version.split()[0])

    # PyTorch / CUDA
    try:
        import torch
        row("torch", torch.__version__)
        cuda_ok = torch.cuda.is_available()
        row("CUDA доступен", "✅" if cuda_ok else "❌", ok=cuda_ok)
        if cuda_ok:
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                free = torch.cuda.mem_get_info(i)[0] / 1_073_741_824
                total = props.total_memory / 1_073_741_824
                row(f"  GPU {i}: {props.name}", f"{free:.1f}/{total:.0f} GB free")
                out[f"gpu{i}"] = props.name
    except ImportError:
        row("torch", "❌ не установлен")

    # Disk
    try:
        import shutil
        usage = shutil.disk_usage(ROOT)
        free_gb  = usage.free  / 1_073_741_824
        total_gb = usage.total / 1_073_741_824
        row("Диск (свободно)", f"{free_gb:.0f} / {total_gb:.0f} GB", ok=free_gb > 10)
    except Exception:
        pass

    return out


# ────────────────────────────────────────────────────────────────────
# 8. FRONTEND И ЗАПУСК
# ────────────────────────────────────────────────────────────────────

def check_frontend() -> dict:
    fe = ROOT / "frontend"
    screens = list((fe / "screens").glob("*.js")) if (fe / "screens").exists() else []
    row("frontend/index.html", "✅" if (fe / "index.html").exists() else "❌",
        ok=(fe / "index.html").exists())
    row("Screens", ", ".join(f.stem for f in screens))

    node_modules = ROOT / "node_modules" / "three"
    row("Three.js (node_modules)",
        "✅" if node_modules.exists() else "❌ — npm install",
        ok=node_modules.exists())

    # Проверим порт 8080
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8080/frontend/", timeout=3)
        row("Web server :8080", "✅  http://localhost:8080/frontend/", ok=True)
    except Exception:
        row("Web server :8080", "❌ не запущен (npx http-server -p 8080)")

    return {}


# ────────────────────────────────────────────────────────────────────
# 9. ЛОГИ
# ────────────────────────────────────────────────────────────────────

def check_logs() -> None:
    logs_dir = ROOT / "logs"
    if not logs_dir.exists():
        return
    files = sorted(logs_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    total_mb = sum(f.stat().st_size for f in files if f.is_file()) / 1_048_576
    row("Logs dir размер", f"{total_mb:.0f} MB  ({len(files)} файлов)")
    for f in files[:8]:
        mb = f.stat().st_size / 1_048_576
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d %H:%M")
        row(f"  {f.name[:40]}", f"{mb:.1f} MB  [{mtime}]")


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="LLCAR Diagnostica KB — аналитика проекта")
    parser.add_argument("--json",      action="store_true", help="вывод в JSON")
    parser.add_argument("--check-api", action="store_true", help="только проверка API")
    args = parser.parse_args()

    if args.check_api:
        section("KB API")
        check_api()
        return

    report: dict = {"timestamp": datetime.now().isoformat()}

    print(f"\n{SEP2}")
    print(f"  LLCAR Diagnostica KB — Полная аналитика")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP2)

    section("1. SQLITE DATABASE")
    report["sqlite"] = check_sqlite()

    section("2. LANCEDB ВЕКТОРНАЯ БД")
    report["lancedb"] = check_lancedb()

    section("3. KB API СЕРВЕР")
    report["api"] = check_api()

    section("4. FINE-TUNING МОДЕЛИ ПЕРЕВОДА")
    report["finetune"] = check_finetune()

    section("5. ОБУЧАЮЩИЕ ДАННЫЕ")
    report["training"] = check_training_data()

    section("6. SCRAPERS")
    check_scrapers()

    section("7. ОКРУЖЕНИЕ (Python / GPU / Диск)")
    report["env"] = check_env()

    section("8. FRONTEND И ВЕБ-СЕРВЕР")
    check_frontend()

    section("9. ЛОГИ")
    check_logs()

    # ── ИТОГ ──────────────────────────────────────────────────────
    section("ИТОГ")
    api_ok    = report["api"].get("lancedb_available", False)
    chunks    = report["sqlite"].get("chunks", 0)
    cc        = report["sqlite"].get("chunk_content", 0)
    images    = report["sqlite"].get("chunk_images", 0)
    cap       = report["sqlite"].get("captioned", 0)
    cv        = report["sqlite"].get("colbert_vectors", 0)
    best_bleu = report["finetune"].get("best_bleu", 0)
    best_r    = report["finetune"].get("best_round", "?")

    row("Chunks в KB",         f"{chunks:,}", ok=chunks > 10000)
    row("Переводы",            f"{cc:,} ({cc // max(chunks, 1):.1f} языка/чанк)", ok=cc > 20000)
    row("Изображения / caption", f"{images:,} / {cap:,}", ok=cap == images)
    row("ColBERT vectors",     f"{cv:,}", ok=cv > 10000)
    row("Лучшая модель",       f"Round {best_r}, BLEU={best_bleu:.2f}", ok=best_bleu > 10)
    row("API онлайн",          "✅ http://localhost:8000" if api_ok else "❌ офлайн", ok=api_ok)
    print()

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
