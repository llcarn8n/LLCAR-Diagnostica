#!/usr/bin/env python3
"""A/B test: PaddleOCR-ch (baseline) vs MinerU-OCR (ru+en+zh) vs Qwen3-VL (Ollama).

Three OCR engines on the same set of images:
  A: PaddleOCR lang=ch (current, garbles Russian)
  B: MinerU PaddleOCR lang=ru+en+zh (via ~/.venv311)
  C: Qwen3-VL 30B via Ollama (vision LLM, best quality)

Usage:
  python scripts/ocr_ab_test.py --select        # show selected images
  python scripts/ocr_ab_test.py --run-b --n 20  # run engine B only
  python scripts/ocr_ab_test.py --run-c --n 20  # run engine C only
  python scripts/ocr_ab_test.py --run-all --n 20
  python scripts/ocr_ab_test.py --report        # print comparison
"""

import os
import sys
import io
import sqlite3
import json
import time
import subprocess
import base64
import argparse
import re
import random
import statistics
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DB_PATH = "knowledge-base/kb.db"
AB_PATH = "knowledge-base/ocr_ab_results.json"
VENV311 = "C:/Users/BAZA/.venv311/Scripts/python.exe"
OLLAMA_URL = "http://localhost:11434"
QWEN_MODEL = "qwen3-vl:30b"


# ─────────────────────────────────────────────
# IMAGE SELECTION
# ─────────────────────────────────────────────

def select_test_images(n=20, seed=42):
    """Stratified selection from DB by PaddleOCR text length."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("""
        SELECT image_path, ocr_text, LENGTH(COALESCE(ocr_text,'')) as len
        FROM chunk_images GROUP BY image_path ORDER BY image_path
    """)
    all_imgs = [(r[0], r[1] or "", r[2] or 0) for r in c.fetchall()]
    conn.close()

    random.seed(seed)
    buckets = {
        "empty":  [x for x in all_imgs if x[2] == 0],
        "short":  [x for x in all_imgs if 1 <= x[2] < 50],
        "medium": [x for x in all_imgs if 50 <= x[2] < 200],
        "long":   [x for x in all_imgs if x[2] >= 200],
    }
    ratios = {"empty": 0.15, "short": 0.30, "medium": 0.35, "long": 0.20}
    selected = []
    for key, ratio in ratios.items():
        pool = buckets[key]
        k = min(max(1, round(n * ratio)), len(pool))
        selected += random.sample(pool, k)

    # top up if needed
    if len(selected) < n:
        used = set(x[0] for x in selected)
        extras = [x for x in all_imgs if x[0] not in used]
        random.shuffle(extras)
        selected += extras[:n - len(selected)]

    return selected[:n]


def resolve_path(img_path):
    p = Path(img_path)
    if p.exists(): return p
    p2 = Path("knowledge-base") / img_path
    if p2.exists(): return p2
    return None


# ─────────────────────────────────────────────
# ENGINE B: MinerU PaddleOCR (ru+en+zh)
# ─────────────────────────────────────────────

ENGINE_B_SCRIPT = """
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

# Multilingual: English + Russian + Chinese (MinerU config: ["en","ru","zh"])
# PaddleOCR 3.x uses separate models per language.
# We use 'latin' script model for Russian (covers Cyrillic)
# Plus Chinese model for ZH. Two-pass approach.
ocr_zh = PaddleOCR(lang='ch',  use_textline_orientation=True, device='gpu:0',
                   text_det_thresh=0.3, text_det_box_thresh=0.5)
ocr_ru = PaddleOCR(lang='ru',  use_textline_orientation=True, device='gpu:0',
                   text_det_thresh=0.3, text_det_box_thresh=0.5)

images = json.loads(sys.argv[1])
results = {}
for img_path in images:
    from pathlib import Path
    p = Path(img_path)
    if not p.exists():
        p = Path('knowledge-base') / img_path
    if not p.exists():
        results[img_path] = {'b_zh': '', 'b_ru': '', 'error': 'not found'}
        continue

    def extract(ocr):
        try:
            res = ocr.predict(str(p))
            lines = []
            for r in res:
                for txt, sc in zip(r.get('rec_texts',[]), r.get('rec_scores',[])):
                    if sc >= 0.4 and txt.strip():
                        lines.append(txt.strip())
            return '\\n'.join(lines)
        except Exception as e:
            return f'ERROR:{e}'

    results[img_path] = {'b_zh': extract(ocr_zh), 'b_ru': extract(ocr_ru)}

print(json.dumps(results, ensure_ascii=False))
"""


def run_engine_b(images):
    """Run MinerU PaddleOCR (multilingual) in .venv311."""
    print(f"\n[Engine B] PaddleOCR ru+en+zh in .venv311 ({len(images)} images)...")
    img_paths = [img[0] for img in images]

    env = os.environ.copy()
    env["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

    # Write temp script
    script_path = Path("knowledge-base/ocr_b_worker.py")
    script_path.write_text(ENGINE_B_SCRIPT, encoding="utf-8")

    t0 = time.time()
    try:
        result = subprocess.run(
            [VENV311, str(script_path), json.dumps(img_paths)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env, timeout=600
        )
        elapsed = time.time() - t0
        if result.returncode != 0:
            print(f"  [B] ERROR (exit {result.returncode}): {result.stderr[-500:]}")
            return {}

        # Parse JSON output (last line of stdout)
        lines = [l for l in result.stdout.strip().split("\n") if l.startswith("{")]
        if not lines:
            print(f"  [B] No JSON output found")
            print(f"  stdout: {result.stdout[-300:]}")
            return {}

        data = json.loads(lines[-1])
        print(f"  [B] Done: {len(data)} images in {elapsed:.1f}s")

        # Merge zh + ru results
        merged = {}
        for path, vals in data.items():
            zh = vals.get("b_zh", "")
            ru = vals.get("b_ru", "")
            # Combine: prefer longer, deduplicate
            if not ru:
                merged[path] = zh
            elif not zh:
                merged[path] = ru
            else:
                # Both have content - merge unique lines
                zh_lines = set(zh.split("\n"))
                ru_lines = ru.split("\n")
                extra = [l for l in ru_lines if l not in zh_lines and l.strip()]
                merged[path] = zh + ("\n" + "\n".join(extra) if extra else "")
        return merged

    except subprocess.TimeoutExpired:
        print("  [B] TIMEOUT after 600s")
        return {}
    except Exception as e:
        print(f"  [B] Exception: {e}")
        return {}
    finally:
        script_path.unlink(missing_ok=True)


# ─────────────────────────────────────────────
# ENGINE C: Qwen3-VL via Ollama
# ─────────────────────────────────────────────

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_engine_c_one(img_path, full_path):
    """Run Qwen3-VL on one image via Ollama API."""
    import urllib.request
    import urllib.error

    try:
        b64 = encode_image(full_path)
    except Exception as e:
        return f"ERROR:encode:{e}"

    prompt = (
        "Extract all text visible in this image. "
        "The image may contain Chinese, Russian, or English text. "
        "Output only the extracted text, preserving line breaks. "
        "If there is no readable text, output EMPTY."
    )

    payload = {
        "model": QWEN_MODEL,
        "prompt": prompt,
        "images": [b64],
        "stream": False,
        "options": {"temperature": 0.0},
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result.get("response", "").strip()
            if text.upper() == "EMPTY" or text.lower() == "empty.":
                return ""
            return text
    except urllib.error.URLError as e:
        return f"ERROR:ollama:{e}"
    except Exception as e:
        return f"ERROR:{e}"


def run_engine_c(images):
    """Run Qwen3-VL on all test images."""
    print(f"\n[Engine C] Qwen3-VL 30B via Ollama ({len(images)} images)...")

    # Check Ollama is running
    import urllib.request
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5)
    except Exception:
        print("  [C] ERROR: Ollama not running. Start with: ollama serve")
        return {}

    results = {}
    for i, (img_path, _, paddle_len) in enumerate(images):
        full = resolve_path(img_path)
        if full is None:
            results[img_path] = ""
            print(f"  [C] [{i+1}/{len(images)}] SKIP not found: {img_path[-40:]}")
            continue

        t0 = time.time()
        text = run_engine_c_one(img_path, full)
        elapsed = time.time() - t0

        results[img_path] = text if not text.startswith("ERROR:") else ""
        status = "ERR" if text.startswith("ERROR:") else f"{len(text)}ch"
        print(f"  [C] [{i+1}/{len(images)}] {elapsed:.1f}s | paddle={paddle_len}ch qwen={status} | {img_path[-35:]}")

    return results


# ─────────────────────────────────────────────
# METRICS & REPORT
# ─────────────────────────────────────────────

def tokenize(text):
    """Split text into comparable tokens."""
    return set(re.findall(r"[\w\u4e00-\u9fff\u0400-\u04ff]+", text.lower()))


def jaccard(a, b):
    ta, tb = tokenize(a), tokenize(b)
    u = ta | tb
    return len(ta & tb) / len(u) if u else 1.0


def score_quality(text):
    """Heuristic quality score: penalize garbled text."""
    if not text:
        return 0.0
    score = 1.0
    # Penalty: mixed Latin/Cyrillic in same word (garbling sign)
    garble = re.findall(r"[A-Za-z][а-яА-Я]|[а-яА-Я][A-Za-z]", text)
    score -= 0.1 * min(len(garble), 5)
    # Penalty: very low real word ratio (noise)
    words = re.findall(r"[а-яА-Я\u4e00-\u9fff\w]{2,}", text)
    noise = re.findall(r"[^а-яА-Я\u4e00-\u9fffA-Za-z0-9\s\n\.,;:!?()\/\-]", text)
    if len(words) + len(noise) > 0:
        score -= 0.3 * (len(noise) / (len(words) + len(noise)))
    return max(0.0, score)


def build_report(ab_data):
    items = ab_data["items"]
    engines = ["A (Paddle-ch)", "B (MinerU ru+zh)", "C (Qwen3-VL)"]
    keys = ["paddle", "mineru", "qwen"]

    print("\n" + "=" * 68)
    print("OCR A/B/C TEST REPORT")
    print("=" * 68)
    print(f"Test images: {len(items)}")
    print()

    # Aggregate stats per engine
    for key, label in zip(keys, engines):
        vals = [x.get(key, "") or "" for x in items]
        cov = sum(1 for v in vals if v)
        total_ch = sum(len(v) for v in vals)
        avg_q = statistics.mean(score_quality(v) for v in vals)
        print(f"{label}")
        print(f"  Coverage:    {cov}/{len(items)} ({cov/len(items)*100:.0f}%)")
        print(f"  Total chars: {total_ch:,}")
        print(f"  Avg chars:   {total_ch/len(items):.0f}")
        print(f"  Quality*:    {avg_q:.2f}  (*heuristic: 1=clean, 0=garbled)")
        print()

    # Pairwise Jaccard
    print("─" * 50)
    print("Pairwise agreement (Jaccard, higher=more similar):")
    for (k1, l1), (k2, l2) in [
        (("paddle","A"), ("mineru","B")),
        (("paddle","A"), ("qwen","C")),
        (("mineru","B"), ("qwen","C")),
    ]:
        jacs = [jaccard(x.get(k1,"") or "", x.get(k2,"") or "") for x in items]
        avg = statistics.mean(jacs)
        print(f"  {l1} vs {l2}: {avg:.3f}")
    print()

    # Per-image comparison table (top differences)
    print("─" * 50)
    print("Per-image detail (sorted by Paddle chars, top 10):")
    print(f"{'Image':<38} {'A-ch':>6} {'B-ru':>6} {'C-vl':>6} {'QvB':>6}")
    print("-" * 65)
    sorted_items = sorted(items, key=lambda x: x.get("paddle_len", 0), reverse=True)
    for x in sorted_items[:15]:
        pa = x.get("paddle", "") or ""
        mb = x.get("mineru", "") or ""
        qc = x.get("qwen", "") or ""
        jac_qb = jaccard(mb, qc)
        print(f"  {x['img'][-36:]:<36} {len(pa):>6} {len(mb):>6} {len(qc):>6} {jac_qb:>6.2f}")

    # Example comparisons
    print()
    print("─" * 50)
    # Find image where B or C clearly better than A
    improved = [(x, len(x.get("mineru","") or ""), len(x.get("qwen","") or ""),
                 len(x.get("paddle","") or "")) for x in items]
    improved.sort(key=lambda t: max(t[1],t[2]) - t[3], reverse=True)

    print("TOP 3: Where MinerU/Qwen clearly beat PaddleOCR-ch")
    for x, mb_len, qc_len, pa_len in improved[:3]:
        print(f"\n  Image: {x['img'][-45:]}")
        print(f"  [A Paddle-ch] {pa_len}ch: {repr((x.get('paddle') or '')[:80])}")
        print(f"  [B MinerU]    {mb_len}ch: {repr((x.get('mineru') or '')[:80])}")
        print(f"  [C Qwen3-VL]  {qc_len}ch: {repr((x.get('qwen') or '')[:80])}")

    # Verdict
    totals = {
        k: sum(len(x.get(k, "") or "") for x in items)
        for k in keys
    }
    quality = {
        k: statistics.mean(score_quality(x.get(k, "") or "") for x in items)
        for k in keys
    }
    cov = {
        k: sum(1 for x in items if x.get(k, ""))
        for k in keys
    }

    print()
    print("=" * 68)
    print("VERDICT")
    print("=" * 68)
    best_chars = max(keys, key=lambda k: totals[k])
    best_quality = max(keys, key=lambda k: quality[k])
    best_cov = max(keys, key=lambda k: cov[k])
    labels_map = dict(zip(keys, engines))
    print(f"Most text extracted: {labels_map[best_chars]} ({totals[best_chars]:,} chars)")
    print(f"Best quality score:  {labels_map[best_quality]} (score={quality[best_quality]:.2f})")
    print(f"Best coverage:       {labels_map[best_cov]} ({cov[best_cov]}/{len(items)})")

    if best_quality == "qwen":
        print("\nRECOMMENDATION: Use Qwen3-VL for final OCR pass on all 1079 images.")
        print("  It understands context, handles Russian correctly, no garbling.")
    elif best_quality == "mineru":
        print("\nRECOMMENDATION: Re-run OCR with MinerU (ru+en+zh) on all images.")
    else:
        print("\nRECOMMENDATION: PaddleOCR-ch is already the best for this data.")

    print()
    print("* Quality score heuristic: detects Latin/Cyrillic mixing (garbling)")
    print("  and noise character ratio. Not a ground-truth metric.")


# ─────────────────────────────────────────────
# LOAD / SAVE
# ─────────────────────────────────────────────

def load_ab():
    if Path(AB_PATH).exists():
        with open(AB_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"items": []}


def save_ab(ab):
    with open(AB_PATH, "w", encoding="utf-8") as f:
        json.dump(ab, f, ensure_ascii=False, indent=2)


def get_or_create_items(ab, images):
    """Ensure items exist for all test images."""
    existing = {x["img"]: x for x in ab.get("items", [])}
    items = []
    for img_path, paddle_text, paddle_len in images:
        if img_path not in existing:
            existing[img_path] = {
                "img": img_path,
                "paddle": paddle_text or "",
                "paddle_len": paddle_len,
                "mineru": None,
                "qwen": None,
            }
        else:
            existing[img_path]["paddle"] = paddle_text or ""
            existing[img_path]["paddle_len"] = paddle_len
        items.append(existing[img_path])
    ab["items"] = items
    return items


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="OCR A/B/C test")
    parser.add_argument("--select", action="store_true", help="Show selected images")
    parser.add_argument("--run-b", action="store_true", help="Run Engine B (MinerU ru+zh)")
    parser.add_argument("--run-c", action="store_true", help="Run Engine C (Qwen3-VL)")
    parser.add_argument("--run-all", action="store_true", help="Run both B and C")
    parser.add_argument("--report", action="store_true", help="Print report")
    parser.add_argument("--n", type=int, default=20, help="Number of test images")
    args = parser.parse_args()

    images = select_test_images(args.n)
    ab = load_ab()
    items = get_or_create_items(ab, images)

    if args.select or (not any([args.run_b, args.run_c, args.run_all, args.report])):
        print(f"Selected {len(images)} test images:")
        for img, text, length in images:
            status = f"paddle={length}ch" if length else "paddle=empty"
            print(f"  {status:>14} | {img[-50:]}")
        return

    if args.run_b or args.run_all:
        results_b = run_engine_b(images)
        for item in items:
            if item["img"] in results_b:
                item["mineru"] = results_b[item["img"]]
        save_ab(ab)
        print(f"\n[B] Results saved to {AB_PATH}")

    if args.run_c or args.run_all:
        results_c = run_engine_c(images)
        for item in items:
            if item["img"] in results_c:
                item["qwen"] = results_c[item["img"]]
        save_ab(ab)
        print(f"\n[C] Results saved to {AB_PATH}")

    if args.report or args.run_all or args.run_b or args.run_c:
        ab = load_ab()
        if ab["items"]:
            build_report(ab)
        else:
            print("No results yet. Run --run-b or --run-c first.")


if __name__ == "__main__":
    main()
