#!/usr/bin/env python3
"""
upload_training_data.py — Upload training pairs JSONL to HF Hub as a dataset.

Usage:
    python scripts/upload_training_data.py
    python scripts/upload_training_data.py --all   # merge all training_pairs_*.jsonl
    python scripts/upload_training_data.py --repo Petr117/diagnostica-training-pairs

What it does:
    1. Reads training_pairs_*.jsonl from knowledge-base/
    2. Converts to HF Dataset (train/test split 95/5)
    3. Pushes to Hub as Petr117/diagnostica-training-pairs (private)
"""

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger("upload")

ROOT    = Path(__file__).parent.parent
KB_DIR  = ROOT / "knowledge-base"
DEFAULT_REPO = "Petr117/diagnostica-training-pairs"


def load_pairs(paths: list[Path]) -> list[dict]:
    records = []
    for p in paths:
        if not p.exists():
            log.warning("File not found: %s", p)
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    # Normalize: keep only needed fields
                    records.append({
                        "id":          r.get("id", ""),
                        "source_lang": r.get("source_lang", ""),
                        "target_lang": r.get("target_lang", ""),
                        "source":      r.get("source", ""),
                        "translation": r.get("translation", ""),
                        "source_title": r.get("source_title", ""),
                        "quality_score": float(r.get("quality_score", 0.0)),
                    })
                except json.JSONDecodeError as e:
                    log.warning("Bad JSON in %s: %s", p.name, e)
        log.info("Loaded %d records from %s", len(records), p.name)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all",  action="store_true",
                        help="Merge all training_pairs_*.jsonl files")
    parser.add_argument("--file", default=None,
                        help="Specific JSONL file to upload (default: training_pairs_tier1.jsonl)")
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help=f"HF dataset repo (default: {DEFAULT_REPO})")
    parser.add_argument("--private", action="store_true", default=True,
                        help="Make dataset private (default: True)")
    parser.add_argument("--test-size", type=float, default=0.05,
                        help="Test split fraction (default: 0.05)")
    args = parser.parse_args()

    from datasets import Dataset, DatasetDict  # noqa: PLC0415

    # Collect files
    if args.all:
        files = sorted(KB_DIR.glob("training_pairs_*.jsonl"))
        # Exclude the merged file to avoid duplicates
        files = [f for f in files if f.name != "training_pairs_all.jsonl"]
        log.info("Found %d JSONL files to merge", len(files))
    elif args.file:
        files = [Path(args.file)]
    else:
        files = [KB_DIR / "training_pairs_tier1.jsonl"]

    records = load_pairs(files)
    if not records:
        log.error("No training pairs found. Run translate_kb.py first.")
        return

    log.info("Total records: %d", len(records))

    # Show distribution
    from collections import Counter
    pairs = Counter(f"{r['source_lang']}->{r['target_lang']}" for r in records)
    for pair, count in sorted(pairs.items()):
        log.info("  %s: %d (%.1f%%)", pair, count, count * 100 / len(records))

    # Create HF Dataset
    ds = Dataset.from_list(records)

    # Train/test split
    split = ds.train_test_split(test_size=args.test_size, seed=42)
    dataset_dict = DatasetDict({"train": split["train"], "test": split["test"]})

    log.info("Train: %d  |  Test: %d", len(dataset_dict["train"]), len(dataset_dict["test"]))

    # Push to Hub
    log.info("Pushing to HF Hub: %s (private=%s)", args.repo, args.private)
    dataset_dict.push_to_hub(
        args.repo,
        private=args.private,
        commit_message=f"Update: {len(records)} pairs ({', '.join(f'{p}={c}' for p,c in sorted(pairs.items()))})",
    )
    log.info("Done! Dataset: https://huggingface.co/datasets/%s", args.repo)


if __name__ == "__main__":
    main()
