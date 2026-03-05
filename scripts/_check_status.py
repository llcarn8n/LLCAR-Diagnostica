import json, os
p = r"C:\LLCAR-Transfer\reocr_retry.jsonl"
if not os.path.exists(p):
    print("Log not found yet - OCR still initializing")
else:
    lines = open(p, encoding="utf-8").readlines()
    succ = sum(1 for l in lines if json.loads(l).get("ocr_count", 0) > 0)
    total_new = sum(json.loads(l).get("new_count", 0) for l in lines)
    total_skip = sum(json.loads(l).get("skip_count", 0) for l in lines)
    print(f"Entries processed: {len(lines)} / 132")
    print(f"Successful OCR: {succ}")
    print(f"New parts inserted: {total_new}")
    print(f"Skipped (exist): {total_skip}")
