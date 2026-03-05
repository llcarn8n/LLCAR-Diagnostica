#!/usr/bin/env python3
"""Verify translation quality using Claude Haiku via Anthropic API.

Samples N translations from chunk_content, sends source+translation to Claude
for quality assessment. Saves results to knowledge-base/verification_results.jsonl.
"""

import sqlite3
import json
import sys
import io
import os
import time
import random
import argparse
from datetime import datetime, timezone

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DB_PATH = "knowledge-base/kb.db"
RESULTS_FILE = "knowledge-base/verification_results.jsonl"

VERIFY_PROMPT = """You are a professional translation quality assessor for automotive technical manuals (Li Auto L7/L9).

SOURCE ({src_lang}):
Title: {src_title}
Content: {src_content}

TRANSLATION ({tgt_lang}):
Title: {tgt_title}
Content: {tgt_content}

Evaluate the translation on these criteria (1-5 scale each):
1. **accuracy** - Does the translation convey the same meaning? Are technical details correct?
2. **terminology** - Are automotive terms translated correctly and consistently?
3. **numbers** - Are ALL numbers, measurements, DTC codes, part numbers preserved exactly?
4. **fluency** - Is the translation natural and readable in the target language?
5. **completeness** - Is any content missing or added compared to the source?

Respond ONLY with valid JSON (no markdown, no explanation):
{{"accuracy": N, "terminology": N, "numbers": N, "fluency": N, "completeness": N, "overall": N, "issues": ["issue1", "issue2"]}}

Where "overall" is the average of all 5 scores (rounded to 1 decimal).
If there are no issues, use "issues": [].
"""


def get_anthropic_client(api_key):
    """Initialize Anthropic client."""
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def sample_translations(conn, n=50, lang=None):
    """Sample N random translations with their source texts."""
    c = conn.cursor()

    query = """
        SELECT cc.chunk_id, cc.lang, cc.title, cc.content,
               ch.title as src_title, ch.content as src_content,
               ch.source_language as src_lang
        FROM chunk_content cc
        JOIN chunks ch ON ch.id = cc.chunk_id
        WHERE cc.lang != ch.source_language
    """
    params = []
    if lang:
        query += " AND cc.lang = ?"
        params.append(lang)

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(n)

    c.execute(query, params)
    rows = c.fetchall()

    samples = []
    for row in rows:
        samples.append({
            "chunk_id": row[0],
            "tgt_lang": row[1],
            "tgt_title": row[2],
            "tgt_content": row[3],
            "src_title": row[4],
            "src_content": row[5],
            "src_lang": row[6],
        })
    return samples


def verify_one(client, sample, model="claude-haiku-4-5-20251001"):
    """Send one translation to Claude for verification."""
    prompt = VERIFY_PROMPT.format(
        src_lang=sample["src_lang"],
        src_title=sample["src_title"],
        src_content=sample["src_content"][:2000],  # truncate very long content
        tgt_lang=sample["tgt_lang"],
        tgt_title=sample["tgt_title"],
        tgt_content=sample["tgt_content"][:2000],
    )

    response = client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # Parse JSON response
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        import re
        m = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if m:
            result = json.loads(m.group())
        else:
            result = {"error": text, "overall": 0}

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify translation quality via Claude API")
    parser.add_argument("--api-key", type=str, help="Anthropic API key (or set ANTHROPIC_API_KEY env)")
    parser.add_argument("--samples", type=int, default=50, help="Number of samples to verify (default: 50)")
    parser.add_argument("--lang", type=str, default=None, help="Filter by target language (en/ru)")
    parser.add_argument("--model", type=str, default="claude-haiku-4-5-20251001", help="Model to use")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --api-key or set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")

    # Sample translations
    samples = sample_translations(conn, n=args.samples, lang=args.lang)
    print(f"Sampled {len(samples)} translations for verification")
    if not samples:
        print("No translations found!")
        conn.close()
        return

    # Initialize Anthropic client
    client = get_anthropic_client(api_key)

    # Verify each sample
    results = []
    scores = {"accuracy": [], "terminology": [], "numbers": [], "fluency": [], "completeness": [], "overall": []}
    issues_all = []
    errors = 0

    now = datetime.now(timezone.utc).isoformat()

    with open(RESULTS_FILE, "a", encoding="utf-8") as out_f:
        for i, sample in enumerate(samples):
            try:
                result = verify_one(client, sample, model=args.model)

                # Collect scores
                for key in scores:
                    if key in result:
                        scores[key].append(result[key])

                if result.get("issues"):
                    for issue in result["issues"]:
                        issues_all.append({
                            "chunk_id": sample["chunk_id"],
                            "lang": sample["tgt_lang"],
                            "issue": issue,
                        })

                # Save result
                record = {
                    "chunk_id": sample["chunk_id"],
                    "src_lang": sample["src_lang"],
                    "tgt_lang": sample["tgt_lang"],
                    "scores": result,
                    "verified_at": now,
                    "model": args.model,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                results.append(record)

                overall = result.get("overall", "?")
                issues_count = len(result.get("issues", []))
                src_preview = sample["src_title"][:30] if sample["src_title"] else sample["src_content"][:30]
                print(
                    f"  [{i+1}/{len(samples)}] {sample['chunk_id'][:12]}.. "
                    f"{sample['src_lang']}->{sample['tgt_lang']} "
                    f"score={overall} issues={issues_count} | {src_preview}"
                )

            except Exception as e:
                print(f"  [{i+1}/{len(samples)}] ERROR: {e}")
                errors += 1
                time.sleep(1)

    conn.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Samples verified: {len(results)}/{len(samples)}")
    print(f"Errors: {errors}")
    print()

    for key in ["accuracy", "terminology", "numbers", "fluency", "completeness", "overall"]:
        vals = scores[key]
        if vals:
            avg = sum(vals) / len(vals)
            low = min(vals)
            high = max(vals)
            below_3 = sum(1 for v in vals if v < 3)
            print(f"  {key:15s}: avg={avg:.2f}  min={low}  max={high}  below_3={below_3}")

    print()
    if issues_all:
        print(f"Total issues found: {len(issues_all)}")
        # Show top issues
        from collections import Counter
        issue_counts = Counter(i["issue"] for i in issues_all)
        print("Top issues:")
        for issue, count in issue_counts.most_common(10):
            print(f"  [{count}x] {issue}")
    else:
        print("No issues found!")

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
