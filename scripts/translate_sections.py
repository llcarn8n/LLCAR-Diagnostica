#!/usr/bin/env python3
"""
LLCAR Diagnostica — Phase 2: Section Translation Pipeline.

Translates manual sections from ZH→RU using MADLAD-400-3B-MT (Google, Apache 2.0).
Applies glossary post-processing for automotive term consistency.

Output: manual-sections-{vehicle}-ru.json (translated)

Usage:
    python translate_sections.py                          # Translate all ZH→RU
    python translate_sections.py --input l7-zh            # Translate single file
    python translate_sections.py --model utrobin          # Use Utrobin T5
    python translate_sections.py --backend ct2            # Use CTranslate2 backend
    python translate_sections.py --dry-run                # Show what would be translated
"""

import sys
import io
import json
import re
import time
import argparse
from pathlib import Path
from datetime import date

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge-base"
GLOSSARY_PATH = KB_DIR / "glossary-unified-trilingual.json"
GLOSSARY_ALIGNMENT_PATH = KB_DIR / "glossary-alignment.json"

# Translation targets: input → output filename
TRANSLATION_TARGETS = {
    "l7-zh": {
        "input": "manual-sections-l7-zh.json",
        "output": "manual-sections-l7-ru.json",
        "src_lang": "zh",
        "tgt_lang": "ru",
    },
    "l9-zh-parts": {
        "input": "manual-sections-l9-zh-parts.json",
        "output": "manual-sections-l9-ru-parts.json",
        "src_lang": "zh",
        "tgt_lang": "ru",
    },
}

# Model configs
MODEL_CONFIGS = {
    "madlad": {
        "hf_id": "google/madlad400-3b-mt",
        "ct2_id": "Nextcloud-AI/madlad400-3b-mt-ct2-int8",
        "max_length": 512,
        "src_prefix": "<2ru> ",  # MADLAD uses target-language prefix
    },
    "utrobin": {
        "hf_id": "utrobinmv/t5_translate_en_ru_zh_large_1024",
        "ct2_id": None,
        "max_length": 1024,
        "src_prefix": "translate to ru: ",
    },
}

# ============================================================
# Glossary loader
# ============================================================
_glossary_cache = None


def load_glossary():
    """Load ZH→RU glossary for post-processing from unified + alignment."""
    global _glossary_cache
    if _glossary_cache is not None:
        return _glossary_cache

    _glossary_cache = {}

    # Load unified trilingual glossary
    if GLOSSARY_PATH.exists():
        with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for term in data.get("terms", []):
            zh = term.get("zh", "").strip()
            ru = term.get("ru", "").strip()
            if zh and ru and len(zh) >= 2:
                _glossary_cache[zh] = ru
        print(f"  Unified glossary loaded: {len(_glossary_cache)} terms")

    # Also load alignment glossary for additional terms
    if GLOSSARY_ALIGNMENT_PATH.exists():
        with open(GLOSSARY_ALIGNMENT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        added = 0
        for term in data.get("terms", []):
            zh = term.get("zh", "").strip()
            ru = term.get("ru", "").strip()
            if zh and ru and len(zh) >= 2 and zh not in _glossary_cache:
                _glossary_cache[zh] = ru
                added += 1
        if added:
            print(f"  Alignment glossary added: {added} terms")

    if not _glossary_cache:
        print("  [WARN] No glossary found, skipping post-processing")

    return _glossary_cache


# ============================================================
# Translation backends
# ============================================================
class TranslatorHF:
    """HuggingFace Transformers backend."""

    def __init__(self, model_key="madlad"):
        config = MODEL_CONFIGS[model_key]
        self.model_key = model_key
        self.max_length = config["max_length"]
        self.src_prefix = config["src_prefix"]

        print(f"  Loading model: {config['hf_id']}...")
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        self.tokenizer = AutoTokenizer.from_pretrained(config["hf_id"])
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            config["hf_id"],
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()

        device = next(self.model.parameters()).device
        print(f"  Model loaded on: {device}")

    def translate(self, text, src_lang="zh", tgt_lang="ru"):
        """Translate a single text chunk."""
        import torch

        input_text = f"{self.src_prefix}{text}"
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding=True,
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_length,
                num_beams=4,
                length_penalty=1.0,
                early_stopping=True,
            )

        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result

    def translate_batch(self, texts, src_lang="zh", tgt_lang="ru", batch_size=4):
        """Translate a batch of texts."""
        import torch

        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            input_texts = [f"{self.src_prefix}{t}" for t in batch]

            inputs = self.tokenizer(
                input_texts,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True,
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    num_beams=4,
                    length_penalty=1.0,
                    early_stopping=True,
                )

            for output in outputs:
                result = self.tokenizer.decode(output, skip_special_tokens=True)
                results.append(result)

        return results


class TranslatorCT2:
    """CTranslate2 backend (faster inference)."""

    # Local path for CT2 model (avoids Cyrillic path issues on Windows)
    LOCAL_CT2_DIR = "C:/tmp/madlad-ct2"

    def __init__(self, model_key="madlad"):
        config = MODEL_CONFIGS[model_key]
        ct2_id = config.get("ct2_id")
        if not ct2_id:
            raise ValueError(f"No CTranslate2 model for '{model_key}'")

        self.model_key = model_key
        self.max_length = config["max_length"]
        self.src_prefix = config["src_prefix"]

        import ctranslate2
        import sentencepiece as spm

        # Use local model dir if available (avoids Cyrillic path issues)
        model_dir = self.LOCAL_CT2_DIR
        if not Path(model_dir).exists():
            print(f"  Local model not found at {model_dir}, downloading...")
            from huggingface_hub import snapshot_download
            model_dir = snapshot_download(ct2_id)

        print(f"  Loading CT2 model from: {model_dir}...")
        self.translator = ctranslate2.Translator(
            model_dir,
            device="cuda",
            compute_type="int8",
        )

        # Load SentencePiece tokenizer
        sp_path = None
        for name in ["spiece.model", "sentencepiece.model", "tokenizer.model"]:
            p = Path(model_dir) / name
            if p.exists():
                sp_path = p
                break

        if sp_path:
            self.sp = spm.SentencePieceProcessor(str(sp_path))
        else:
            from transformers import AutoTokenizer
            self._hf_tokenizer = AutoTokenizer.from_pretrained(config["hf_id"])
            self.sp = None

        print(f"  CT2 model loaded (INT8, CUDA)")

    def _tokenize(self, text):
        if self.sp:
            return self.sp.encode(text, out_type=str)
        else:
            return self._hf_tokenizer.tokenize(text)

    def _detokenize(self, tokens):
        if self.sp:
            return self.sp.decode(tokens)
        else:
            return self._hf_tokenizer.convert_tokens_to_string(tokens)

    def translate(self, text, src_lang="zh", tgt_lang="ru"):
        input_text = f"{self.src_prefix}{text}"
        tokens = self._tokenize(input_text)
        results = self.translator.translate_batch(
            [tokens],
            beam_size=4,
            max_decoding_length=self.max_length,
        )
        return self._detokenize(results[0].hypotheses[0])

    def translate_batch(self, texts, src_lang="zh", tgt_lang="ru", batch_size=2):
        input_texts = [f"{self.src_prefix}{t}" for t in texts]
        all_tokens = [self._tokenize(t) for t in input_texts]

        results = []
        for i in range(0, len(all_tokens), batch_size):
            batch = all_tokens[i:i + batch_size]
            batch_results = self.translator.translate_batch(
                batch,
                beam_size=4,
                max_decoding_length=256,
            )
            for r in batch_results:
                results.append(self._detokenize(r.hypotheses[0]))

        return results


# ============================================================
# Text chunking for translation
# ============================================================
def chunk_for_translation(text, max_chars=600):
    """Split text into chunks suitable for translation."""
    if not text or len(text) <= max_chars:
        return [text] if text else []

    chunks = []
    paragraphs = text.split("\n\n")
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append(current.strip())

    # Further split any oversized chunks by sentences
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            final_chunks.append(chunk)
        else:
            # Split by sentence boundaries
            sentences = re.split(r'(?<=[。！？\.\!\?])\s*', chunk)
            sub = ""
            for sent in sentences:
                if len(sub) + len(sent) > max_chars and sub:
                    final_chunks.append(sub.strip())
                    sub = sent
                else:
                    sub = sub + " " + sent if sub else sent
            if sub.strip():
                final_chunks.append(sub.strip())

    return final_chunks


# ============================================================
# Glossary post-processing
# ============================================================
def apply_glossary(text, glossary):
    """Replace known terms with glossary translations."""
    if not glossary:
        return text

    # Sort by length (longest first) to avoid partial matches
    for zh_term in sorted(glossary.keys(), key=len, reverse=True):
        ru_term = glossary[zh_term]
        # Only replace if the Chinese term appears in text (shouldn't after translation,
        # but sometimes untranslated terms leak through)
        if zh_term in text:
            text = text.replace(zh_term, ru_term)

    return text


# ============================================================
# Section translation
# ============================================================
def translate_sections(input_path, output_path, translator, src_lang, tgt_lang):
    """Translate all sections in a manual JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    glossary = load_glossary()
    sections = data.get("sections", [])
    total_sections = len(sections)
    total_chars_in = 0
    total_chars_out = 0

    print(f"\n  Translating {total_sections} sections ({src_lang}→{tgt_lang})...")

    for idx, section in enumerate(sections):
        section_id = section.get("sectionId", f"s{idx}")
        content = section.get("content", "")
        title = section.get("title", "")

        if not content and not title:
            continue

        start = time.time()

        # Translate title
        if title:
            translated_title = translator.translate(title, src_lang, tgt_lang)
            translated_title = apply_glossary(translated_title, glossary)
            section["title_original"] = title
            section["title"] = translated_title

        # Translate content in chunks
        if content:
            chunks = chunk_for_translation(content)
            total_chars_in += len(content)

            if chunks:
                translated_chunks = translator.translate_batch(chunks, src_lang, tgt_lang)
                translated_content = "\n\n".join(translated_chunks)
                translated_content = apply_glossary(translated_content, glossary)

                section["content_original_zh"] = content[:500]  # Keep first 500 chars of original
                section["content"] = translated_content
                total_chars_out += len(translated_content)

        # Translate table headers
        for table in section.get("tables", []):
            headers = table.get("headers", [])
            if headers:
                translated_headers = translator.translate_batch(
                    [h for h in headers if h],
                    src_lang, tgt_lang,
                )
                j = 0
                for i, h in enumerate(headers):
                    if h:
                        headers[i] = translated_headers[j]
                        j += 1

        elapsed = time.time() - start
        content_kb = len(content) / 1024
        print(f"    [{idx + 1}/{total_sections}] {section_id}: {content_kb:.0f}KB → {elapsed:.1f}s")

    # Update metadata
    data["language"] = tgt_lang
    data["translation"] = {
        "source_language": src_lang,
        "target_language": tgt_lang,
        "model": translator.model_key,
        "date": str(date.today()),
        "total_chars_in": total_chars_in,
        "total_chars_out": total_chars_out,
        "glossary_terms_applied": len(glossary),
    }

    # Append "_translated" to title
    if "title" in data:
        data["title"] = data["title"] + " (перевод)"

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n  Saved: {output_path}")
    print(f"  Input: {total_chars_in / 1024:.0f}KB, Output: {total_chars_out / 1024:.0f}KB")
    return data


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="LLCAR Diagnostica: Translate manual sections ZH→RU"
    )
    parser.add_argument(
        "--input", type=str, default=None,
        help=f"Translation target key. Available: {', '.join(TRANSLATION_TARGETS.keys())}"
    )
    parser.add_argument(
        "--model", type=str, default="madlad",
        choices=list(MODEL_CONFIGS.keys()),
        help="Translation model to use (default: madlad)"
    )
    parser.add_argument(
        "--backend", type=str, default="hf",
        choices=["hf", "ct2"],
        help="Inference backend: hf (transformers) or ct2 (CTranslate2)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be translated without running"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("LLCAR Diagnostica — Phase 2: Translation Pipeline")
    print(f"Model: {args.model}, Backend: {args.backend}")
    print("=" * 60)

    # Determine targets
    if args.input:
        if args.input not in TRANSLATION_TARGETS:
            print(f"ERROR: Unknown target '{args.input}'. Available: {list(TRANSLATION_TARGETS.keys())}")
            return
        targets = {args.input: TRANSLATION_TARGETS[args.input]}
    else:
        targets = TRANSLATION_TARGETS

    # Show targets
    for key, target in targets.items():
        input_path = KB_DIR / target["input"]
        output_path = KB_DIR / target["output"]
        exists = "OK" if input_path.exists() else "NOT FOUND"
        size = f"{input_path.stat().st_size / 1024:.0f}KB" if input_path.exists() else "-"
        print(f"  {key}: {target['input']} ({size}) [{exists}] → {target['output']}")

    if args.dry_run:
        print("\n  [DRY RUN] No translation performed.")
        return

    # Initialize translator
    print(f"\n--- Loading {args.model} ({args.backend}) ---")
    if args.backend == "ct2":
        translator = TranslatorCT2(args.model)
    else:
        translator = TranslatorHF(args.model)

    # Translate each target
    for key, target in targets.items():
        input_path = KB_DIR / target["input"]
        output_path = KB_DIR / target["output"]

        if not input_path.exists():
            print(f"\n  SKIP: {input_path} not found")
            continue

        print(f"\n{'=' * 60}")
        print(f"Translating: {key}")
        print(f"{'=' * 60}")

        translate_sections(
            input_path, output_path,
            translator,
            target["src_lang"],
            target["tgt_lang"],
        )

    print(f"\n{'=' * 60}")
    print("Translation complete!")
    for f in sorted(KB_DIR.glob("manual-sections-*-ru*.json")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.1f} KB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
