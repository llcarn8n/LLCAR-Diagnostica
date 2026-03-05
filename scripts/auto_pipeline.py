#!/usr/bin/env python3
"""
auto_pipeline.py — Watch translate_kb.py completion and auto-launch next stages.

Stages triggered automatically:
  1. translate_kb.py v9 finishes  → bake_translations.py (FTS rebuild)
  2. Round 2 fine-tuning finishes → validate (compare BLEU R1 vs R2)
  3. bridge_translate.py          → EN→AR, EN→ES on GPU 0
  4. After bridge done            → upload + Round 3 fine-tuning

Usage:
    python scripts/auto_pipeline.py
    python scripts/auto_pipeline.py --skip-bridge   # skip AR/ES
"""
from __future__ import annotations

import argparse
import io
import logging
import subprocess
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("autopipeline")

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
KB_DIR  = ROOT / "knowledge-base"
LOG_DIR = ROOT / "logs"


def run(cmd: list[str], log_file: Path, env_extra: dict | None = None) -> int:
    """Run a command, tee to log_file, return exit code."""
    import os
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    log.info("Running: %s → %s", " ".join(cmd), log_file.name)
    with open(log_file, "w", encoding="utf-8") as lf:
        proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
    return proc.returncode


def translate_is_done() -> bool:
    """Detect translate_kb.py v9 completion by absence of lock / checking log."""
    log_path = LOG_DIR / "translate_tier_all_v9.log"
    if not log_path.exists():
        return False
    try:
        with open(log_path, "rb") as f:
            f.seek(-500, 2)
            tail = f.read().decode("utf-8", errors="replace")
        return "Estimated cost" in tail or "Translated" in tail
    except Exception:
        return False


def finetune_r2_is_done() -> bool:
    """Detect Round 2 fine-tuning completion."""
    log_path = LOG_DIR / "finetune_round2.log"
    if not log_path.exists():
        return False
    try:
        with open(log_path, "rb") as f:
            f.seek(-1000, 2)
            tail = f.read().decode("utf-8", errors="replace")
        return "Fine-tuning complete" in tail or "Model published" in tail
    except Exception:
        return False


def coverage_pct() -> float:
    """Quick ZH->EN coverage from DB."""
    import sqlite3
    try:
        conn = sqlite3.connect(str(ROOT / "knowledge-base" / "kb.db"), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        total_zh = conn.execute("SELECT COUNT(*) FROM chunks WHERE source_language='zh'").fetchone()[0]
        done_en = conn.execute(
            "SELECT COUNT(DISTINCT c.id) FROM chunks c "
            "JOIN chunk_content cc ON cc.chunk_id=c.id "
            "WHERE c.source_language='zh' AND cc.lang='en'"
        ).fetchone()[0]
        conn.close()
        return 100 * done_en / total_zh if total_zh else 0
    except Exception:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-bridge", action="store_true",
                        help="Skip EN→AR/ES bridge translations")
    parser.add_argument("--skip-r3", action="store_true",
                        help="Skip Round 3 fine-tuning")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("  Auto-pipeline started. Monitoring completion...")
    log.info("  Press Ctrl+C to stop.")
    log.info("=" * 60)

    bridge_done = False
    r2_reported = False
    translate_done_reported = False

    while True:
        # ----------------------------------------------------------------
        # Stage A: Round 2 fine-tuning done → validate
        # ----------------------------------------------------------------
        if not r2_reported and finetune_r2_is_done():
            r2_reported = True
            log.info("✅ Round 2 fine-tuning COMPLETE!")
            log.info("Running model comparison R1 vs R2...")
            run(
                [sys.executable, str(SCRIPTS / "compare_models.py")],
                LOG_DIR / "compare_r1_vs_r2.log",
            )
            log.info("Comparison saved to logs/compare_r1_vs_r2.log")

        # ----------------------------------------------------------------
        # Stage B: translate_kb.py done → bake + bridge translations
        # ----------------------------------------------------------------
        if not translate_done_reported and translate_is_done():
            translate_done_reported = True
            pct = coverage_pct()
            log.info("✅ translate_kb.py COMPLETE! ZH→EN coverage: %.0f%%", pct)

            # Bake translations into FTS
            log.info("Running bake_translations.py...")
            run(
                [sys.executable, str(SCRIPTS / "bake_translations.py")],
                LOG_DIR / "bake_final.log",
            )
            log.info("✅ bake_translations done.")

            # Bridge: EN→AR, EN→ES
            if not args.skip_bridge:
                log.info("Starting bridge_translate.py (EN→AR+ES) on %s ...", args.device)
                rc = run(
                    [
                        sys.executable, str(SCRIPTS / "bridge_translate.py"),
                        "--device", args.device,
                        "--batch-size", "16",
                        "--training-pairs", str(KB_DIR / "training_pairs_bridge.jsonl"),
                    ],
                    LOG_DIR / "bridge_translate.log",
                )
                if rc == 0:
                    log.info("✅ Bridge translations complete!")
                    bridge_done = True
                else:
                    log.error("bridge_translate.py failed (rc=%d)", rc)

        # ----------------------------------------------------------------
        # Stage C: Bridge done → Round 3 fine-tuning
        # ----------------------------------------------------------------
        if bridge_done and not args.skip_r3 and translate_done_reported:
            bridge_done = False  # prevent re-triggering
            log.info("Uploading expanded dataset for Round 3...")

            # Upload all training pairs (tier1 + bridge)
            run(
                [
                    sys.executable, str(SCRIPTS / "upload_training_data.py"),
                    "--all", "--repo", "Petr117/diagnostica-training-pairs",
                ],
                LOG_DIR / "upload_r3_dataset.log",
            )

            log.info("Starting Round 3 fine-tuning...")
            import os
            hf_token = open(Path.home() / ".cache/huggingface/token").read().strip()
            rc = run(
                [sys.executable, str(SCRIPTS / "finetune_m2m.py")],
                LOG_DIR / "finetune_round3.log",
                env_extra={"HF_TOKEN": hf_token, "CUDA_VISIBLE_DEVICES": "0"},
            )
            if rc == 0:
                log.info("✅ Round 3 fine-tuning COMPLETE! Model updated at Petr117/m2m-diagnostica-automotive")
            else:
                log.error("Round 3 fine-tuning failed (rc=%d)", rc)
            log.info("Pipeline fully complete! Exiting.")
            break

        # ----------------------------------------------------------------
        # Done check — if everything already complete
        # ----------------------------------------------------------------
        if r2_reported and translate_done_reported and (args.skip_bridge or bridge_done or args.skip_r3):
            log.info("All stages complete!")
            break

        time.sleep(30)  # poll every 30s


if __name__ == "__main__":
    main()
