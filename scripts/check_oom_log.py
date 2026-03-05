"""Check reocr_full.jsonl for OOM failures and extract failed image paths."""
import json
import sys
from pathlib import Path

log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\LLCAR-Transfer\reocr_full.jsonl")
if not log_path.exists():
    print(f"Log not found: {log_path}")
    sys.exit(1)

oom_images = []
zero_ocr = []
success = []

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        img = entry.get("image", "")
        parts = entry.get("parts", [])
        ocr_count = entry.get("ocr_count", 0)

        # Check if any part has CUDA OOM error indicator
        has_oom = False
        for p in parts:
            if isinstance(p, str) and "CUDA out of memory" in p:
                has_oom = True
                break

        # Also check if the whole entry text has OOM
        if "CUDA out of memory" in line:
            has_oom = True

        if has_oom:
            oom_images.append(entry)
        elif ocr_count == 0:
            zero_ocr.append(entry)
        else:
            success.append(entry)

print(f"Total log entries: {len(oom_images) + len(zero_ocr) + len(success)}")
print(f"OOM failures: {len(oom_images)}")
print(f"Zero OCR (no parts found): {len(zero_ocr)}")
print(f"Successful: {len(success)}")
print()

if oom_images:
    print("=== OOM FAILED IMAGES ===")
    for e in oom_images[:10]:
        print(f"  pg={e.get('page_idx'):>4}  sys={e.get('system',''):<30}  img={e.get('image','')}")
    if len(oom_images) > 10:
        print(f"  ... and {len(oom_images) - 10} more")
    print()

    # Write failed image list for retry
    out_path = log_path.parent / "oom_failed_images.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([{
            "image": e.get("image", ""),
            "page_idx": e.get("page_idx", -1),
            "system": e.get("system", ""),
            "type": e.get("type", "reocr"),
        } for e in oom_images], f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(oom_images)} failed images to {out_path}")

# Also write zero-OCR list (includes OOM + genuinely empty)
if zero_ocr:
    out_path2 = log_path.parent / "zero_ocr_images.json"
    with open(out_path2, "w", encoding="utf-8") as f:
        json.dump([{
            "image": e.get("image", ""),
            "page_idx": e.get("page_idx", -1),
            "system": e.get("system", ""),
            "type": e.get("type", "reocr"),
        } for e in zero_ocr], f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(zero_ocr)} zero-OCR images to {out_path2}")
