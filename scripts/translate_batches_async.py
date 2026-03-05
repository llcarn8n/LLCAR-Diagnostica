#!/usr/bin/env python3
"""Translate remaining batch_NNN.json files using Anthropic API (async, parallel).

Reads batch files, translates ZH/RU/EN text using Claude Sonnet,
writes batch_NNN_out.json for import_translations.py.

Usage:
  set ANTHROPIC_API_KEY=sk-ant-...
  python scripts/translate_batches_async.py
  python scripts/translate_batches_async.py --workers 6 --dry-run
"""

import os
import sys
import io
import json
import time
import asyncio
import argparse
import re
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BATCH_DIR = Path("knowledge-base/translate_batches")
GLOSSARY_PATH = BATCH_DIR / "glossary_compact.json"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192
CONCURRENCY = 4  # parallel API calls (reduced to avoid rate limits)


def load_glossary():
    with open(GLOSSARY_PATH, encoding="utf-8") as f:
        terms = json.load(f)
    return terms


def format_glossary(terms, src_lang, tgt_langs):
    """Format 200-term glossary for the prompt."""
    lines = []
    for term in terms:
        src = term.get(src_lang, "")
        tgts = [f"{l}={term.get(l,'')}" for l in tgt_langs if term.get(l)]
        if src and tgts:
            lines.append(f"  {src} → {', '.join(tgts)}")
    return "\n".join(lines)


def find_missing_batches():
    """Return sorted list of batch numbers that need translation."""
    done = set()
    for f in BATCH_DIR.iterdir():
        m = re.match(r"batch_(\d+)_out\.json", f.name)
        if m:
            done.add(int(m.group(1)))

    missing = []
    for f in sorted(BATCH_DIR.iterdir()):
        m = re.match(r"batch_(\d+)\.json$", f.name)
        if m:
            num = int(m.group(1))
            if num not in done:
                missing.append(num)
    return sorted(missing)


def build_prompt(chunks, glossary_text, src_lang, tgt_lang):
    """Build prompt for single target language translation."""
    lang_names = {"zh": "Chinese", "en": "English", "ru": "Russian"}
    src_name = lang_names.get(src_lang, src_lang)
    tgt_name = lang_names.get(tgt_lang, tgt_lang)

    chunks_json = json.dumps(chunks, ensure_ascii=False, indent=2)

    prompt = f"""You are a professional automotive technical translator.

Translate each chunk from {src_name} to {tgt_name}.
Preserve all formatting, numbers, and technical terms exactly.

GLOSSARY (use these exact translations for technical terms):
{glossary_text}

INPUT CHUNKS (JSON array of {len(chunks)} items):
{chunks_json}

OUTPUT REQUIREMENTS:
- Return ONLY a valid JSON array with exactly {len(chunks)} objects
- No markdown, no explanation, no code fences — raw JSON only
- Each object: {{"id": "<original id>", "lang": "{tgt_lang}", "title": "<translated title>", "content": "<translated content>"}}
- Escape all special characters in strings: use \\n for newlines, \\" for quotes
- Preserve line breaks as \\n in the content field
- Keep numbers, units, model names (Li Auto L9, etc.) unchanged

START YOUR RESPONSE WITH [ AND END WITH ]"""

    return prompt


def extract_json_array(raw):
    """Extract JSON array from response, handling markdown code blocks."""
    # Remove markdown code fences
    cleaned = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()

    # Try direct parse first
    if cleaned.startswith('['):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # Find JSON array with regex
    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if not match:
        return None

    extracted = match.group(0)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        pass

    return None


async def call_api_one_language(client, batch_num, chunks, glossary, src_lang, tgt_lang, semaphore):
    """Single API call for one source→target language pair. Returns list of translated items or None."""
    glossary_text = format_glossary(glossary, src_lang, [tgt_lang])
    prompt = build_prompt(chunks, glossary_text, src_lang, tgt_lang)

    start = time.time()
    async with semaphore:
        try:
            msg = await client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            elapsed = time.time() - start
            raw = msg.content[0].text.strip()
            stop_reason = msg.stop_reason

            if stop_reason == "max_tokens":
                print(f"  [{batch_num:03d}→{tgt_lang}] WARN: Response truncated (max_tokens hit)")
                (BATCH_DIR / f"batch_{batch_num:03d}_{tgt_lang}_raw.txt").write_text(raw, encoding="utf-8")
                return None

            results = extract_json_array(raw)
            if results is None:
                print(f"  [{batch_num:03d}→{tgt_lang}] ERROR: No JSON array in response ({elapsed:.1f}s)")
                (BATCH_DIR / f"batch_{batch_num:03d}_{tgt_lang}_raw.txt").write_text(raw, encoding="utf-8")
                return None

            # Validate count
            if len(results) != len(chunks):
                print(f"  [{batch_num:03d}→{tgt_lang}] WARN: Expected {len(chunks)} items, got {len(results)} ({elapsed:.1f}s)")
            else:
                print(f"  [{batch_num:03d}→{tgt_lang}] OK: {len(results)} items, {elapsed:.1f}s")

            return results

        except Exception as e:
            elapsed = time.time() - start
            print(f"  [{batch_num:03d}→{tgt_lang}] API error ({elapsed:.1f}s): {e}")
            return None


async def translate_batch(client, batch_num, glossary, semaphore, dry_run=False):
    """Translate one batch file. Returns (batch_num, success, elapsed)."""
    batch_path = BATCH_DIR / f"batch_{batch_num:03d}.json"
    out_path = BATCH_DIR / f"batch_{batch_num:03d}_out.json"

    if out_path.exists():
        print(f"  [{batch_num:03d}] Already done, skipping.")
        return batch_num, True, 0

    try:
        with open(batch_path, encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"  [{batch_num:03d}] ERROR reading input: {e}")
        return batch_num, False, 0

    if not chunks:
        print(f"  [{batch_num:03d}] Empty batch, skipping.")
        return batch_num, False, 0

    src_lang = chunks[0].get("src", "zh")
    tgt_langs = chunks[0].get("tgt", ["en"])
    if isinstance(tgt_langs, str):
        tgt_langs = [tgt_langs]

    if dry_run:
        print(f"  [{batch_num:03d}] DRY RUN: {len(chunks)} chunks, {src_lang}→{tgt_langs}")
        return batch_num, True, 0

    start = time.time()
    all_results = []

    # Translate one target language at a time (avoids max_tokens truncation for multi-target)
    for tgt_lang in tgt_langs:
        items = await call_api_one_language(client, batch_num, chunks, glossary, src_lang, tgt_lang, semaphore)
        if items is None:
            elapsed = time.time() - start
            print(f"  [{batch_num:03d}] FAILED on {src_lang}→{tgt_lang}")
            return batch_num, False, elapsed
        all_results.extend(items)

    elapsed = time.time() - start

    # Write combined output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"  [{batch_num:03d}] DONE: {len(all_results)} total translations, {elapsed:.1f}s")
    return batch_num, True, elapsed


async def main_async(args):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.AsyncAnthropic(api_key=api_key)
    glossary = load_glossary()
    missing = find_missing_batches()

    if not missing:
        print("All batches already translated!")
        return

    print(f"Batches to translate: {len(missing)} ({missing[0]}–{missing[-1]})")
    print(f"Concurrency: {args.workers}")
    print(f"Model: {MODEL}")
    if args.dry_run:
        print("DRY RUN MODE - no API calls")
    print()

    semaphore = asyncio.Semaphore(args.workers)
    tasks = [
        translate_batch(client, num, glossary, semaphore, dry_run=args.dry_run)
        for num in missing
    ]

    start_all = time.time()
    results = await asyncio.gather(*tasks)

    success = sum(1 for _, ok, _ in results if ok)
    failed = [(num, elapsed) for num, ok, elapsed in results if not ok]
    total_time = time.time() - start_all

    print(f"\n{'='*50}")
    print(f"Translation complete")
    print(f"{'='*50}")
    print(f"Success: {success}/{len(missing)}")
    print(f"Failed:  {len(failed)}")
    if failed:
        print(f"Failed batches: {[n for n, _ in failed]}")
    print(f"Total time: {total_time/60:.1f}min")


def main():
    parser = argparse.ArgumentParser(description="Translate batch files async")
    parser.add_argument("--workers", type=int, default=CONCURRENCY, help="Parallel API calls")
    parser.add_argument("--dry-run", action="store_true", help="No API calls, just validate")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
