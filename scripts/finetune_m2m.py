#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "transformers>=4.40.0",
#   "datasets>=2.18.0",
#   "accelerate>=0.27.0",
#   "sentencepiece>=0.2.0",
#   "sacrebleu>=2.3.0",
#   "evaluate>=0.4.0",
#   "torch>=2.1.0",
#   "huggingface_hub>=0.22.0",
# ]
# ///
"""
finetune_m2m.py — Fine-tune utrobinmv/m2m_translate_en_ru_zh_large_4096
on Diagnostica automotive KB training pairs.

Designed for HF Jobs (UV script) or local GPU run.

Usage (local):
    python scripts/finetune_m2m.py

Usage (HF Jobs via MCP):
    Submit via hf_jobs uv operation with l4x1 or a10g-small flavor.

Environment variables:
    HF_TOKEN          — required for push_to_hub
    DATASET_REPO      — HF dataset repo (default: Petr117/diagnostica-training-pairs)
    OUTPUT_MODEL_REPO — HF model repo (default: Petr117/m2m-diagnostica-automotive)
    NUM_EPOCHS        — training epochs (default: 3)
    BATCH_SIZE        — per-device batch size (default: 8)
    MAX_SOURCE_LEN    — max source tokens (default: 512)
    MAX_TARGET_LEN    — max target tokens (default: 512)

Model: utrobinmv/m2m_translate_en_ru_zh_large_4096
  - Architecture: M2M100ForConditionalGeneration (1.1B params)
  - Supported langs: zh, ru, en
  - Apache 2.0 license
  - Fine-tuned on CCMatrix; we adapt for automotive domain

Strategy: full fine-tune with FP16 + gradient checkpointing.
Requires ~18-22GB VRAM (l4x1 / a10g-small / A100 all work).
"""

from __future__ import annotations

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("finetune")

# ---------------------------------------------------------------------------
# Config from env
# ---------------------------------------------------------------------------
BASE_MODEL      = os.environ.get("BASE_MODEL", "utrobinmv/m2m_translate_en_ru_zh_large_4096")
DATASET_REPO    = os.environ.get("DATASET_REPO",      "Petr117/diagnostica-training-pairs")
DATASET_LOCAL   = os.environ.get("DATASET_LOCAL",     "")    # path to local .jsonl file
OUTPUT_REPO     = os.environ.get("OUTPUT_MODEL_REPO", "Petr117/m2m-diagnostica-automotive")
NUM_EPOCHS      = int(os.environ.get("NUM_EPOCHS",    "3"))
BATCH_SIZE      = int(os.environ.get("BATCH_SIZE",    "8"))
GRAD_ACCUM      = int(os.environ.get("GRAD_ACCUM",    "4"))   # effective batch = 32
MAX_SOURCE_LEN  = int(os.environ.get("MAX_SOURCE_LEN","512"))
MAX_TARGET_LEN  = int(os.environ.get("MAX_TARGET_LEN","512"))
LR              = float(os.environ.get("LR",          "5e-5"))
OUTPUT_DIR      = os.environ.get("OUTPUT_DIR",        "/tmp/m2m-finetune")
TEST_SIZE       = float(os.environ.get("TEST_SIZE",   "0.05"))  # fraction held out for eval when using local JSONL

# WDDM/TDR fix: TdrDelay=60 is now active in registry — GPU 0 (display) is safe to use.
# Both GPUs are available for DDP training.
# GPU 0 (PCIe 01:00.0) — primary display adapter (WDDM, TDR safe with TdrDelay=60)
# GPU 1 (PCIe 05:00.0) — secondary compute GPU
# Default: use both GPUs (0,1) for DDP via torchrun.
# Override: set CUDA_VISIBLE_DEVICES=1 to use only GPU 1.
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

# M2M100 language codes
LANG_CODE = {
    "zh": "zh",
    "en": "en",
    "ru": "ru",
    "ar": "ar",
    "es": "es",
}


def main():
    import torch
    from datasets import load_dataset
    from transformers import (
        M2M100ForConditionalGeneration,
        AutoTokenizer,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        DataCollatorForSeq2Seq,
        EarlyStoppingCallback,
    )
    import evaluate

    # ---- Environment check ------------------------------------------------
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log.info("Device: %s", device)
    if device == "cuda":
        log.info("GPU: %s  |  VRAM: %.1f GB", torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9)

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        log.warning("HF_TOKEN not set — push_to_hub will fail if repo is private")

    # ---- Load model & tokenizer -------------------------------------------
    log.info("Loading tokenizer: %s", BASE_MODEL)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    log.info("Loading model: %s", BASE_MODEL)
    model = M2M100ForConditionalGeneration.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    model.gradient_checkpointing_enable()
    log.info("Model params: %.1fM", sum(p.numel() for p in model.parameters()) / 1e6)

    # ---- Load dataset -----------------------------------------------------
    if DATASET_LOCAL:
        import json as _json  # noqa: PLC0415
        from datasets import Dataset, DatasetDict  # noqa: PLC0415
        log.info("Loading local dataset: %s", DATASET_LOCAL)
        records = []
        with open(DATASET_LOCAL, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line:
                    continue
                r = _json.loads(_line)
                # Normalize: support both old (source/translation) and new (source_text/target_text) schemas
                src = r.get("source") or r.get("source_text", "")
                tgt = r.get("translation") or r.get("target_text", "")
                if src and tgt and r.get("source_lang") and r.get("target_lang"):
                    records.append({
                        "source_lang":  r["source_lang"],
                        "target_lang":  r["target_lang"],
                        "source":       src,
                        "translation":  tgt,
                    })
        log.info("Loaded %d records from local JSONL", len(records))
        raw_full = Dataset.from_list(records)
        split = raw_full.train_test_split(test_size=TEST_SIZE, seed=42)
        raw_ds = DatasetDict({"train": split["train"], "test": split["test"]})
    else:
        log.info("Loading dataset: %s", DATASET_REPO)
        try:
            raw_ds = load_dataset(DATASET_REPO, token=hf_token)
        except Exception as e:
            log.error("Failed to load dataset: %s", e)
            log.error("Run upload_training_data.py first to push training pairs to HF Hub")
            sys.exit(1)

    log.info("Train: %d  |  Test: %d", len(raw_ds["train"]), len(raw_ds["test"]))

    # Show language pair distribution
    from collections import Counter
    pairs = Counter(
        f"{r['source_lang']}->{r['target_lang']}"
        for r in raw_ds["train"]
    )
    log.info("Language pairs in train: %s", dict(sorted(pairs.items())))

    # ---- Preprocessing ----------------------------------------------------
    # utrobin model uses T5Tokenizer with "translate to {lang}: " prefix style.
    # T5Tokenizer has NO src_lang / as_target_tokenizer — use direct batched tokenization.
    def preprocess(examples):
        """Tokenize source → target pairs using T5-style prefix."""
        inputs  = []
        targets = []

        for src_lang, tgt_lang, src_text, tgt_text in zip(
            examples["source_lang"],
            examples["target_lang"],
            examples["source"],
            examples["translation"],
        ):
            tgt_code = LANG_CODE.get(tgt_lang, tgt_lang)
            inputs.append(f"translate to {tgt_code}: {src_text}")
            targets.append(tgt_text)

        model_inputs = tokenizer(
            inputs,
            max_length=MAX_SOURCE_LEN,
            truncation=True,
            padding=False,
        )

        label_encodings = tokenizer(
            targets,
            max_length=MAX_TARGET_LEN,
            truncation=True,
            padding=False,
        )

        # Replace padding token id with -100 so it's ignored in loss
        model_inputs["labels"] = [
            [tok if tok != tokenizer.pad_token_id else -100 for tok in ids]
            for ids in label_encodings["input_ids"]
        ]
        return model_inputs

    log.info("Tokenizing dataset...")
    tokenized = raw_ds.map(
        preprocess,
        batched=True,
        batch_size=256,
        remove_columns=raw_ds["train"].column_names,
        desc="Tokenizing",
    )

    # ---- Metrics ----------------------------------------------------------
    sacrebleu = evaluate.load("sacrebleu")

    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        # Replace -100 in labels
        labels = [[l for l in label if l != -100] for label in labels]
        decoded_preds  = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = [[tokenizer.decode(l, skip_special_tokens=True)] for l in labels]
        result = sacrebleu.compute(predictions=decoded_preds, references=decoded_labels)
        return {"bleu": round(result["score"], 2)}

    # ---- Training args ----------------------------------------------------
    # WDDM/TDR notes:
    #   per_device_eval_batch_size reduced to 2 (from 8) to prevent VRAM spikes during
    #   autoregressive generation at eval time. With predict_with_generate=True and
    #   generation_max_length=512, batch_size=8 can peak >22GB which stalls the GPU
    #   long enough for WDDM TDR to fire. Smaller eval batch = shorter kernel duration.
    #   generation_max_length capped at 128: typical automotive translations are short;
    #   512 is excessive and forces many unnecessary decoding steps per eval batch.
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=2,           # was 8; reduced to avoid VRAM spike at eval
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        warmup_ratio=0.1,
        weight_decay=0.01,
        fp16=False,
        bf16=(device == "cuda"),    # adafactor + fp16 GradScaler incompatible; BF16 works
        predict_with_generate=True,
        generation_max_length=128,              # was 512; automotive translations rarely exceed 128 tokens
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        push_to_hub=bool(hf_token),
        hub_model_id=OUTPUT_REPO if hf_token else None,
        hub_token=hf_token,
        hub_strategy="every_save",
        logging_steps=50,
        report_to="none",
        dataloader_num_workers=0,    # Windows: spawn multiprocessing breaks with >0
        save_total_limit=2,
        optim="adafactor",        # memory-efficient optimizer for seq2seq
    )

    # ---- Data collator ----------------------------------------------------
    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
    )

    # ---- Trainer ----------------------------------------------------------
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["test"],
        processing_class=tokenizer,   # transformers 5.x: tokenizer → processing_class
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    # ---- Train! -----------------------------------------------------------
    log.info("=" * 60)
    log.info("  Starting fine-tuning")
    log.info("  Base model  : %s", BASE_MODEL)
    log.info("  Dataset     : %s  (%d train / %d test)",
             DATASET_REPO, len(tokenized["train"]), len(tokenized["test"]))
    log.info("  Output      : %s", OUTPUT_REPO)
    log.info("  Epochs      : %d  |  Batch : %dx%d=%d",
             NUM_EPOCHS, BATCH_SIZE, GRAD_ACCUM, BATCH_SIZE * GRAD_ACCUM)
    log.info("=" * 60)

    trainer.train()

    # ---- Save & push ------------------------------------------------------
    log.info("Saving model to %s", OUTPUT_DIR)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    if hf_token:
        log.info("Pushing final model to HF Hub: %s", OUTPUT_REPO)
        trainer.push_to_hub(commit_message="Fine-tuned on Diagnostica automotive KB")
        log.info("Model published: https://huggingface.co/%s", OUTPUT_REPO)
    else:
        log.warning("HF_TOKEN not set — model saved locally only at %s", OUTPUT_DIR)

    log.info("Fine-tuning complete!")


if __name__ == "__main__":
    main()
