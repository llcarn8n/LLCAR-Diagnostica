#!/usr/bin/env python3
"""
Simple OCR: Load model, process all table images, save to SQLite.
Uses the exact model loading pattern that works in debug_ocr_one.py.
"""
import json, re, sqlite3, sys, time, os, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = Path(__file__).resolve().parent.parent
KB_DB = BASE / "knowledge-base" / "kb.db"
CL_DIR = BASE / "mineru-output" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c"
CL_PATH = CL_DIR / "ocr" / "941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c_content_list.json"
IMG_BASE = CL_DIR / "ocr"

# System mappings
SYSTEMS = {
    '\u52a8\u529b\u7535\u6c60\u7cfb\u7edf': 'Power Battery System',
    '\u52a8\u529b\u9a71\u52a8\u7cfb\u7edf': 'Power Drive System',
    '\u8fdb\u6c14\u88c5\u7f6e': 'Intake System',
    '\u6392\u6c14\u88c5\u7f6e': 'Exhaust System',
    '\u71c3\u6cb9\u4f9b\u7ed9\u88c5\u7f6e': 'Fuel Supply System',
    '\u53d1\u52a8\u673a\u88c5\u7f6e': 'Engine Assembly',
    '\u60ac\u7f6e\u88c5\u7f6e': 'Engine/Drivetrain Mounts',
    '\u524d\u60ac\u67b6\u88c5\u7f6e': 'Front Suspension',
    '\u540e\u60ac\u67b6\u88c5\u7f6e': 'Rear Suspension',
    '\u8f6c\u5411\u88c5\u7f6e': 'Steering System',
    '\u884c\u8f66\u5236\u52a8\u88c5\u7f6e': 'Service Brake System',
    '\u7a7a\u8c03\u70ed\u7ba1\u7406\u7cfb\u7edf': 'HVAC & Thermal Management',
    '\u7535\u5668\u9644\u4ef6\u7cfb\u7edf': 'Electrical Accessories',
    '\u5185\u9970\u7cfb\u7edf': 'Interior Trim System',
    '\u7535\u6e90\u548c\u4fe1\u53f7\u5206\u914d\u7cfb\u7edf': 'Power & Signal Distribution',
    '\u706f\u5177\u7cfb\u7edf': 'Lighting System',
    '\u5ea7\u6905\u7cfb\u7edf': 'Seat System',
    '\u88ab\u52a8\u5b89\u5168\u7cfb\u7edf': 'Passive Safety System',
    '\u5916\u9970\u7cfb\u7edf': 'Exterior Trim System',
    '\u81ea\u52a8\u9a7e\u9a76\u7cfb\u7edf': 'Autonomous Driving System',
    '\u667a\u80fd\u7a7a\u95f4\u7cfb\u7edf': 'Smart Cabin / Infotainment',
    '\u5f00\u95ed\u4ef6\u7cfb\u7edf': 'Closures (Doors, Hood, Tailgate)',
    '\u8f66\u8eab\u88c5\u7f6e': 'Body Structure',
    '\u6574\u8f66\u9644\u4ef6\u88c5\u7f6e': 'Vehicle Accessories & Consumables',
}

OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- 序号 (index number)
- 热点ID (hotspot ID)
- 零件号码 (part number)
- 零件名称 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}]

If the image is not a parts table, return: []"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def load_tables():
    """Load table entries from content_list.json."""
    with open(CL_PATH, 'r', encoding='utf-8') as f:
        cl = json.load(f)
    tables = []
    for entry in cl:
        if entry.get('type') == 'table':
            tables.append({
                'img_path': entry.get('img_path', ''),
                'page_idx': entry.get('page_idx', 0),
            })
    return tables


def build_page_system_map(cl_path):
    """Build page_idx -> system mapping from content_list text entries."""
    with open(cl_path, 'r', encoding='utf-8') as f:
        cl = json.load(f)

    page_map = {}
    current_system_zh = ''
    current_system_en = ''
    current_sub_zh = ''
    current_sub_en = ''

    for entry in cl:
        if entry.get('type') != 'text':
            continue
        text = entry.get('text', '').strip()
        page = entry.get('page_idx', 0)
        level = entry.get('text_level', 0)

        # Check if it's a system name
        for zh, en in SYSTEMS.items():
            if zh in text:
                current_system_zh = zh
                current_system_en = en
                current_sub_zh = ''
                current_sub_en = ''
                break

        page_map[page] = {
            'system_zh': current_system_zh,
            'system_en': current_system_en,
            'subsystem_zh': current_sub_zh,
            'subsystem_en': current_sub_en,
        }

    return page_map


def setup_db(db_path):
    """Create parts table if needed."""
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_number TEXT NOT NULL,
        part_name_zh TEXT NOT NULL,
        part_name_en TEXT,
        hotspot_id TEXT,
        system_zh TEXT,
        system_en TEXT,
        subsystem_zh TEXT,
        subsystem_en TEXT,
        page_idx INTEGER,
        source_image TEXT,
        confidence REAL DEFAULT 1.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_system ON parts(system_zh)")
    conn.commit()
    return conn


def get_processed_images(conn):
    """Get set of already-processed source_image values."""
    try:
        rows = conn.execute("SELECT DISTINCT source_image FROM parts").fetchall()
        return {r[0] for r in rows}
    except:
        return set()


def parse_response(response):
    """Parse JSON from model response."""
    # Strip markdown code block
    text = response.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        # Remove first and last ``` lines
        lines = [l for l in lines if not l.strip().startswith('```')]
        text = '\n'.join(lines)

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try extracting array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # Line-by-line
    rows = []
    for line in text.split('\n'):
        line = line.strip().rstrip(',')
        if line.startswith('{'):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def main():
    args = parse_args()

    # Step 1: Load tables and page mapping
    print("Loading table entries...", flush=True)
    tables = load_tables()
    print(f"  Found {len(tables)} tables", flush=True)

    page_map = build_page_system_map(CL_PATH)
    print(f"  Page->system mapping: {len(page_map)} pages", flush=True)

    # Step 2: Setup DB
    conn = setup_db(KB_DB)
    processed = get_processed_images(conn) if args.resume else set()
    if processed:
        print(f"  Already processed: {len(processed)} images", flush=True)

    # Filter
    pending = []
    for t in tables:
        img_rel = t['img_path']
        if args.resume and img_rel in processed:
            continue
        pending.append(t)

    if args.limit:
        pending = pending[:args.limit]

    print(f"  Tables to process: {len(pending)}", flush=True)

    if not pending:
        print("Nothing to do!")
        return

    # Step 3: Load model (same as working debug script)
    import torch
    from PIL import Image as PILImage
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    print(f"\nLoading Qwen2.5-VL-7B on {args.device}...", flush=True)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct", use_fast=False
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct",
        torch_dtype=torch.bfloat16,
        device_map=args.device,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    )
    model.eval()

    vram = torch.cuda.memory_allocated(0) / 1024**3
    print(f"Model loaded in {time.time()-t0:.1f}s, VRAM: {vram:.1f} GB", flush=True)

    # Step 4: Process tables
    total_parts = 0
    total_ok = 0
    total_empty = 0
    total_error = 0
    t_start = time.time()

    for i, entry in enumerate(pending):
        img_rel = entry['img_path']
        page_idx = entry['page_idx']

        # Resolve image path
        img_path = IMG_BASE / img_rel
        if not img_path.exists():
            img_path = BASE / img_rel
        if not img_path.exists():
            print(f"  {i+1}/{len(pending)}  SKIP (not found): {img_rel}", flush=True)
            total_error += 1
            continue

        # Get system info
        sys_info = page_map.get(page_idx, {
            'system_zh': '', 'system_en': '', 'subsystem_zh': '', 'subsystem_en': ''
        })

        try:
            # Load and resize image
            pil_img = PILImage.open(img_path).convert("RGB")
            w, h = pil_img.size
            max_side = 1024
            if max(w, h) > max_side:
                scale = max_side / max(w, h)
                pil_img = pil_img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)

            # OCR
            messages = [{"role": "user", "content": [
                {"type": "image"}, {"type": "text", "text": OCR_PROMPT}
            ]}]
            text = processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = processor(
                text=[text], images=[pil_img], return_tensors="pt", padding=True
            ).to(args.device)

            with torch.no_grad():
                output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)

            input_len = inputs["input_ids"].shape[1]
            generated = output_ids[0, input_len:]
            response = processor.decode(generated, skip_special_tokens=True).strip()

            # Free memory
            del inputs, output_ids
            torch.cuda.empty_cache()

            # Parse
            rows = parse_response(response)

            if rows:
                total_ok += 1
                for row in rows:
                    pn = str(row.get('part_number', '')).strip()
                    pname = str(row.get('part_name', '')).strip()
                    hotspot = str(row.get('hotspot', '')).strip()
                    if pn and pname:
                        total_parts += 1
                        if not args.dry_run:
                            conn.execute(
                                """INSERT INTO parts (part_number, part_name_zh, hotspot_id,
                                   system_zh, system_en, subsystem_zh, subsystem_en,
                                   page_idx, source_image)
                                   VALUES (?,?,?,?,?,?,?,?,?)""",
                                (pn, pname, hotspot,
                                 sys_info['system_zh'], sys_info['system_en'],
                                 sys_info['subsystem_zh'], sys_info['subsystem_en'],
                                 page_idx, img_rel)
                            )
            else:
                total_empty += 1

            # Commit every 10 tables
            if not args.dry_run and (i + 1) % 10 == 0:
                conn.commit()

        except Exception as exc:
            total_error += 1
            print(f"  {i+1}/{len(pending)}  ERROR: {exc}", flush=True)
            torch.cuda.empty_cache()
            continue

        # Progress
        elapsed = time.time() - t_start
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(pending) - i - 1) / rate if rate > 0 else 0
        print(
            f"  {i+1}/{len(pending)}  parts={total_parts}  ok={total_ok}  "
            f"empty={total_empty}  err={total_error}  "
            f"{rate:.2f} tbl/s  ETA {eta:.0f}s  [{sys_info['system_en']}]",
            flush=True
        )

    # Final commit
    if not args.dry_run:
        conn.commit()

    conn.close()

    elapsed_total = time.time() - t_start
    print(f"\n{'='*60}", flush=True)
    print(f"  Done in {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)", flush=True)
    print(f"  Tables: {len(pending)} (ok={total_ok}, empty={total_empty}, err={total_error})", flush=True)
    print(f"  Parts extracted: {total_parts}", flush=True)
    if args.dry_run:
        print(f"  *** DRY RUN - no DB writes ***", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == '__main__':
    main()
