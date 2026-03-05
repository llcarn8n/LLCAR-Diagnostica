#!/usr/bin/env python3
"""
launch_finetune_hf_job.py — Submit fine-tuning job to HF Jobs infrastructure.

Steps:
    1. Upload training pairs to HF Hub dataset (Petr117/diagnostica-training-pairs)
    2. Submit finetune_m2m.py to HF Jobs on L4 GPU
    3. Monitor job progress

Usage:
    python scripts/launch_finetune_hf_job.py
    python scripts/launch_finetune_hf_job.py --dry-run        # show what would run
    python scripts/launch_finetune_hf_job.py --skip-upload    # if dataset already on Hub
    python scripts/launch_finetune_hf_job.py --flavor l40sx1  # use L40S instead of L4
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger("launcher")

ROOT    = Path(__file__).parent.parent
KB_DIR  = ROOT / "knowledge-base"

# HF Job config
HF_DATASET_REPO   = "Petr117/diagnostica-training-pairs"
HF_MODEL_REPO     = "Petr117/m2m-diagnostica-automotive"
DEFAULT_FLAVOR    = "l4x1"         # 24GB L4 — sufficient for M2M100 1.1B FP16
FINETUNE_SCRIPT   = ROOT / "scripts" / "finetune_m2m.py"


def count_training_pairs() -> int:
    """Count available training pairs."""
    total = 0
    for f in sorted(KB_DIR.glob("training_pairs_*.jsonl")):
        if f.name == "training_pairs_all.jsonl":
            continue
        try:
            total += sum(1 for _ in open(f, encoding="utf-8"))
        except Exception:
            pass
    return total


def upload_dataset(dry_run: bool = False) -> bool:
    """Upload training pairs to HF Hub."""
    n = count_training_pairs()
    log.info("Training pairs available: %d", n)

    if n < 1000:
        log.warning("Only %d pairs — recommend waiting for ≥1000 before fine-tuning", n)

    if dry_run:
        log.info("[DRY-RUN] Would upload %d pairs to %s", n, HF_DATASET_REPO)
        return True

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "upload_training_data.py"),
        "--all",
        "--repo", HF_DATASET_REPO,
    ]
    log.info("Uploading dataset: %s", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode == 0


def read_finetune_script() -> str:
    """Read finetune_m2m.py for submission."""
    return FINETUNE_SCRIPT.read_text(encoding="utf-8")


def submit_hf_job(flavor: str, dry_run: bool = False) -> None:
    """Submit fine-tuning to HF Jobs via Python API."""
    from huggingface_hub import HfApi
    import json

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        log.error("HF_TOKEN environment variable not set")
        sys.exit(1)

    script_content = read_finetune_script()

    env = {
        "DATASET_REPO":      HF_DATASET_REPO,
        "OUTPUT_MODEL_REPO": HF_MODEL_REPO,
        "NUM_EPOCHS":        "3",
        "BATCH_SIZE":        "8",
        "GRAD_ACCUM":        "4",
        "MAX_SOURCE_LEN":    "512",
        "MAX_TARGET_LEN":    "512",
        "LR":                "5e-5",
    }

    log.info("=" * 60)
    log.info("  HF Jobs Fine-tuning Submission")
    log.info("  Base model  : utrobinmv/m2m_translate_en_ru_zh_large_4096")
    log.info("  Dataset     : %s", HF_DATASET_REPO)
    log.info("  Output      : %s", HF_MODEL_REPO)
    log.info("  GPU flavor  : %s", flavor)
    log.info("  Epochs      : %s  |  eff. batch : %s",
             env["NUM_EPOCHS"], str(int(env["BATCH_SIZE"]) * int(env["GRAD_ACCUM"])))
    log.info("=" * 60)

    if dry_run:
        log.info("[DRY-RUN] Would submit UV job with script: finetune_m2m.py")
        log.info("[DRY-RUN] Env: %s", json.dumps(env, indent=2))
        return

    # Submit via HF Jobs Python API (huggingface_hub)
    # Note: this uses the same mechanism as the MCP hf_jobs tool
    api = HfApi(token=hf_token)

    log.info("Submitting job to HF Jobs...")

    # Use the Jobs API directly
    job = api.run_as_job(
        command=[
            "python",
            "-c",
            # UV inline script execution pattern
            f"import base64,tempfile,os,subprocess,sys\n"
            f"s=base64.b64decode({repr(__import__('base64').b64encode(script_content.encode()).decode())!r}).decode()\n"
            f"f=tempfile.NamedTemporaryFile(suffix='.py',delete=False,mode='w')\n"
            f"f.write(s);f.close()\n"
            f"os.environ.update({repr(env)})\n"
            f"subprocess.run([sys.executable,f.name],check=True)",
        ],
        flavor=flavor,
        secrets={"HF_TOKEN": hf_token},
    )
    log.info("Job submitted! ID: %s", job.job_id)
    log.info("Monitor at: https://huggingface.co/jobs/%s", job.job_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",      action="store_true", help="Show plan, don't execute")
    parser.add_argument("--skip-upload",  action="store_true", help="Skip dataset upload")
    parser.add_argument("--flavor",       default=DEFAULT_FLAVOR,
                        help=f"HF Jobs GPU flavor (default: {DEFAULT_FLAVOR})")
    args = parser.parse_args()

    log.info("Training pairs: %d", count_training_pairs())

    # Step 1: Upload dataset
    if not args.skip_upload:
        ok = upload_dataset(dry_run=args.dry_run)
        if not ok:
            log.error("Dataset upload failed")
            sys.exit(1)
    else:
        log.info("Skipping upload (--skip-upload)")

    # Step 2: Submit job
    submit_hf_job(flavor=args.flavor, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
