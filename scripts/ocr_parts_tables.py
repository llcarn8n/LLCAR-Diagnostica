#!/usr/bin/env python3
"""
LLCAR Diagnostica — OCR parts tables with Qwen2.5-VL-7B.

Reads 352 table images from the L9 parts catalog (MinerU content_list.json),
sends each to Qwen2.5-VL-7B with a structured extraction prompt, and stores
the parsed parts data in the SQLite `parts` table.

Model: same Qwen2.5-VL-7B-Instruct as caption_images.py (already cached).

Usage:
    python scripts/ocr_parts_tables.py                     # full run
    python scripts/ocr_parts_tables.py --limit 5 --dry-run # test 5 tables
    python scripts/ocr_parts_tables.py --device cuda:1     # specific GPU
    python scripts/ocr_parts_tables.py --resume             # skip already-processed images
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ocr_parts")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent
_KB_DB = _BASE_DIR / "knowledge-base" / "kb.db"
_CONTENT_LIST = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
    / "941362155-2022-2023款理想L9零件手册_content_list.json"
)
_IMAGE_BASE = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
)

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

# ---------------------------------------------------------------------------
# System / subsystem mappings (from gen_l9_catalog.py)
# ---------------------------------------------------------------------------
SYSTEMS = {
    '动力电池系统': 'Power Battery System',
    '动力驱动系统': 'Power Drive System',
    '进气装置': 'Intake System',
    '排气装置': 'Exhaust System',
    '燃油供给装置': 'Fuel Supply System',
    '发动机装置': 'Engine Assembly',
    '悬置装置': 'Engine/Drivetrain Mounts',
    '前悬架装置': 'Front Suspension',
    '后悬架装置': 'Rear Suspension',
    '转向装置': 'Steering System',
    '行车制动装置': 'Service Brake System',
    '空调热管理系统': 'HVAC & Thermal Management',
    '电器附件系统': 'Electrical Accessories',
    '内饰系统': 'Interior Trim System',
    '电源和信号分配系统': 'Power & Signal Distribution',
    '灯具系统': 'Lighting System',
    '座椅系统': 'Seat System',
    '被动安全系统': 'Passive Safety System',
    '外饰系统': 'Exterior Trim System',
    '自动驾驶系统': 'Autonomous Driving System',
    '智能空间系统': 'Smart Cabin / Infotainment',
    '开闭件系统': 'Closures (Doors, Hood, Tailgate)',
    '车身装置': 'Body Structure',
    '整车附件装置': 'Vehicle Accessories & Consumables',
}

SUBS = {
    '动力电池装置': 'Power Battery Assembly',
    '驱动轴装置': 'Drive Shaft Assembly',
    '前电驱动装置': 'Front Electric Drive Assembly',
    '后电驱动装置': 'Rear Electric Drive Assembly',
    '电源装置': 'Power Supply Unit',
    '增程器': 'Range Extender',
    '空气滤清器部件': 'Air Filter Assembly',
    '进气管路部件': 'Intake Duct Assembly',
    '燃油箱及管路部件': 'Fuel Tank & Lines',
    '燃油箱总成': 'Fuel Tank Assembly',
    '发动机总成部件': 'Engine Assembly Parts',
    '发动机总成附件部件': 'Engine Assembly Accessories',
    '扭矩限制器部件': 'Torque Limiter Assembly',
    '气缸盖部件': 'Cylinder Head Assembly',
    '气缸体部件': 'Cylinder Block Assembly',
    '凸轮轴部件': 'Camshaft Assembly',
    '机油泵部件': 'Oil Pump Assembly',
    '配气机构部件': 'Valve Train Assembly',
    '进排歧管部件': 'Intake/Exhaust Manifold',
    '油底壳及润滑部件': 'Oil Pan & Lubrication',
    '机油滤清器部件': 'Oil Filter Assembly',
    '曲轴通风系统部件': 'Crankcase Ventilation',
    '正时齿轮机构部件': 'Timing Gear Mechanism',
    '皮带轮及张紧轮部件': 'Pulley & Tensioner',
    '燃油管路及连接部件': 'Fuel Lines & Connectors',
    '电子节气门体部件': 'Electronic Throttle Body',
    '增压部件': 'Turbocharger Assembly',
    '蒸发器部件': 'Evaporator Assembly',
    '隔热罩部件': 'Heat Shield Assembly',
    '冷却系统装置部件': 'Cooling System Assembly',
    '水泵部件': 'Water Pump Assembly',
    '发动机系统传感器部件': 'Engine Sensors',
    '火花塞及点火线圈部件': 'Spark Plugs & Ignition Coils',
    '前悬置部件': 'Front Engine Mount',
    '后悬置部件': 'Rear Engine Mount',
    '左前摆臂部件': 'Left Front Control Arm',
    '右前摆臂': 'Right Front Control Arm',
    '前稳定杆部件': 'Front Stabilizer Bar',
    '前减振器部件': 'Front Shock Absorber',
    '后副车架部件': 'Rear Subframe',
    '右后摆臂部件': 'Right Rear Control Arm',
    '左后摆臂部件': 'Left Rear Control Arm',
    '后稳定杆部件': 'Rear Stabilizer Bar',
    '后减震器部件': 'Rear Shock Absorber',
    '悬架空气供给装置': 'Air Suspension Supply System',
    '空气悬架供给部件': 'Air Suspension Supply Parts',
    '空气控制部件': 'Air Control Assembly',
    '空气压缩部件': 'Air Compressor Assembly',
    '车轮装置': 'Wheel Assembly',
    '前制动部件': 'Front Brake Assembly',
    '后制动部件': 'Rear Brake Assembly',
    '制动踏板部件': 'Brake Pedal Assembly',
    '制动管路部件': 'Brake Lines',
    'ESP控制部件': 'ESP Control Unit',
    '随车工具装置': 'On-Board Tool Kit',
    '前端冷却部件装置': 'Front-End Cooling Assembly',
    '电机冷却装置': 'Motor Cooling Assembly',
    '电池及暖风冷却装置': 'Battery & Heater Cooling',
    '后电机冷却管路装置': 'Rear Motor Cooling Lines',
    '前电机冷却管路装置': 'Front Motor Cooling Lines',
    '电池冷却管路装置': 'Battery Cooling Lines',
    '暖风加热管路装置': 'Heater Lines Assembly',
    '发动机冷却管路装置': 'Engine Cooling Lines',
    'HAVC装置': 'HVAC Assembly',
    'HVAC装置': 'HVAC Assembly',
    'HVAC总成部件': 'HVAC Assembly Parts',
    '前HVAC本体部件': 'Front HVAC Body',
    '后HVAC本体部件': 'Rear HVAC Body',
    '制冷压缩机装置': 'Refrigeration Compressor',
    '冷凝器装置': 'Condenser Assembly',
    '空调管路装置': 'AC Lines Assembly',
    '空调控制装置': 'AC Control Assembly',
    '电气设备装置': 'Electrical Equipment',
    '电喇叭装置': 'Electric Horn',
    '门窗开关装置': 'Door/Window Switch',
    '组合开关装置': 'Combination Switch',
    '开关装置': 'Switch Assembly',
    '刮水器装置': 'Wiper Assembly',
    '风窗洗涤器装置': 'Windshield Washer',
    '地毯装置': 'Carpet Assembly',
    '副仪表板装置': 'Center Console Assembly',
    '副仪表板总成部件': 'Center Console Assembly Parts',
    '副仪表板后端上盖板本体部件': 'Center Console Rear Upper Cover',
    '副仪表板冰箱本体部件': 'Center Console Refrigerator',
    '副仪表板上本体部件': 'Center Console Upper Body',
    '副仪表板本体骨架部件': 'Center Console Frame',
    '仪表板装置': 'Dashboard Assembly',
    '仪表板总成部件': 'Dashboard Assembly Parts',
    '仪表板本体部件': 'Dashboard Body Parts',
    '仪表板管梁装置': 'Dashboard Cross-Beam',
    '隔热垫装置': 'Heat Insulation Pads',
    '后端隔热垫部件': 'Rear End Heat Insulation Pad',
    '立柱门槛内饰板装置': 'Pillar/Sill Interior Trim Panel',
    '左侧围内饰板部件': 'Left Side Interior Trim Panel',
    '右侧围内饰板部件': 'Right Side Interior Trim Panel',
    '顶棚及尾门内饰板部件': 'Headliner & Tailgate Interior Panel',
    '后侧围内饰板装置': 'Rear Side Interior Trim',
    '右后侧围内饰板装置': 'Right Rear Side Trim',
    '左后侧围内饰板装置': 'Left Rear Side Trim',
    '行李箱装置': 'Luggage Compartment',
    '顶棚装饰板装置': 'Headliner Trim',
    '前门装饰板装置': 'Front Door Trim Panel',
    '左前门装饰板部件': 'Left Front Door Trim',
    '右前门装饰板部件': 'Right Front Door Trim',
    '后门装饰板装置': 'Rear Door Trim Panel',
    '左后门装饰板部件': 'Left Rear Door Trim',
    '右后门装饰板部件': 'Right Rear Door Trim',
    '后背门内饰板装置': 'Tailgate Interior Trim',
    '前空调第二排吹脚风道装置': 'Front AC 2nd Row Foot Duct',
    '后空调顶棚风道装置': 'Rear AC Roof Duct',
    '后空调吹脚风道装置': 'Rear AC Foot Duct',
    '外循环风道装置': 'Fresh Air Duct',
    '遮阳板装置': 'Sun Visor Assembly',
    '顶棚拉手装置': 'Roof Grab Handles',
    '车辆识别代号标牌装置': 'VIN Plate Assembly',
    '高压线束装置': 'HV Wiring Harness',
    '低压线束装置': 'LV Wiring Harness',
    '前舱线束部件': 'Front Bay Harness',
    '车身线束部件': 'Body Harness',
    '侧门线束部件': 'Side Door Harness',
    '顶棚线束部件': 'Roof Harness',
    '蓄电池线束部件': '12V Battery Harness',
    '仪表板线束部件': 'Dashboard Harness',
    '轮速传感器线束部件': 'Wheel Speed Sensor Harness',
    '后背门线束部件': 'Tailgate Harness',
    '前保险杠线束部件': 'Front Bumper Harness',
    '后保险杠线束部件': 'Rear Bumper Harness',
    'DCDC搭铁线束': 'DC-DC Ground Harness',
    '油箱线束总成': 'Fuel Tank Harness',
    '后电机线束总成': 'Rear Motor Harness',
    '蓄电池装置': '12V Battery Assembly',
    '电路保护装置': 'Circuit Protection (Fuses/Relays)',
    '外部灯具装置': 'Exterior Lighting',
    '前组合灯部件': 'Front Combination Lamp',
    '后组合灯部件': 'Rear Combination Lamp',
    '后雾灯及回复反射器部件': 'Rear Fog Lamp & Reflector',
    '高位制动灯部件': 'High-Mount Stop Lamp',
    '牌照灯部件': 'License Plate Lamp',
    '内部灯具装置': 'Interior Lighting',
    '顶灯部件': 'Dome Lamp',
    '门灯及侧围灯部件': 'Door & Side Body Lamps',
    '仪表灯部件': 'Instrument Lighting',
    '驾驶员座椅总成部件': 'Driver Seat Assembly',
    '驾驶员座椅分总成': 'Driver Seat Sub-Assembly',
    '驾驶员座椅骨架部件': 'Driver Seat Frame',
    '副驾驶员座椅总成部件': 'Passenger Seat Assembly',
    '副驾驶员座椅分总成': 'Passenger Seat Sub-Assembly',
    '副驾驶员座椅骨架': 'Passenger Seat Frame',
    '第二排左侧座椅部件': '2nd Row Left Seat',
    '第二排左侧座椅骨架部件': '2nd Row Left Seat Frame',
    '第二排左侧座椅分总成部件': '2nd Row Left Seat Sub-Assembly',
    '第二排右侧座椅部件': '2nd Row Right Seat',
    '第二排右侧座椅骨架部件': '2nd Row Right Seat Frame',
    '第二排右侧座椅分总成部件': '2nd Row Right Seat Sub-Assembly',
    '第三排右侧座椅部件': '3rd Row Right Seat',
    '第三排右侧座椅分总成部件': '3rd Row Right Seat Sub-Assembly',
    '第三排左侧座椅部件': '3rd Row Left Seat',
    '第三排左侧座椅分总成部件': '3rd Row Left Seat Sub-Assembly',
    '第三排座椅坐垫部件': '3rd Row Seat Cushion',
    '第三排座椅坐垫分总成部件': '3rd Row Seat Cushion Sub-Assembly',
    '方向盘': 'Steering Wheel (Airbag)',
    '安全带装置': 'Seat Belt Assembly',
    '安全气囊装置': 'Airbag Assembly',
    '被动安全附件装置': 'Passive Safety Accessories',
    '车身外装饰件装置': 'Body Exterior Trim',
    '翼子板装饰件装置': 'Fender Trim',
    '激光雷达装饰板装置': 'LiDAR Trim Cover',
    '发动机舱上护板装置': 'Engine Bay Upper Guard',
    '扰流板装置': 'Spoiler Assembly',
    '前围通风饰板装置': 'Front Cowl Vent Trim',
    'LOGO装置': 'Logo/Emblem Assembly',
    '背门外饰板装置': 'Tailgate Exterior Trim',
    '前挡风玻璃装置': 'Front Windshield',
    '后挡风玻璃装置': 'Rear Windshield',
    '天窗装置': 'Sunroof Assembly',
    '天窗总成部件': 'Sunroof Assembly Parts',
    '天窗本体部件': 'Sunroof Body Parts',
    '内后视镜装置': 'Interior Rearview Mirror',
    '左侧外后视镜本体部件': 'Left Exterior Mirror Body',
    '右侧外后视镜本体部件': 'Right Exterior Mirror Body',
    '外后视镜部件': 'Exterior Mirror Assembly',
    '前保险杠装置': 'Front Bumper Assembly',
    '前保险杠本体部件': 'Front Bumper Body',
    '前保险杠总成部件': 'Front Bumper Assembly Parts',
    '主动格栅装置': 'Active Grille Shutter',
    '后保险杠装置': 'Rear Bumper Assembly',
    '后保险杠总成部件': 'Rear Bumper Assembly Parts',
    '后保险杠本体部件': 'Rear Bumper Body',
    '车身底部装饰件装置': 'Underbody Trim',
    '轮罩装置': 'Wheel Arch Liner',
    '轮眉装置': 'Fender Flare',
    '前端框架装置': 'Front-End Module Frame',
    '前组合灯安装支架装置': 'Front Lamp Mounting Bracket',
    '大腿防护横梁装置': 'Pedestrian Protection Beam',
    '侧踏板装置': 'Running Board / Side Step',
    '侧围下裙板装置': 'Side Sill Skirt',
    '车门下装饰板装置': 'Door Lower Trim Panel',
    '侧围通风框装置': 'Side Vent Grille Frame',
    '自动驾驶装置': 'ADAS Hardware Assembly',
    '多媒体装置': 'Multimedia System',
    '摄像头装置': 'Camera Assembly',
    '音响装置': 'Audio System',
    'PEPS装置': 'PEPS (Keyless Entry/Start)',
    '车辆控制装置': 'Vehicle Control Unit',
    '左前门装置': 'Left Front Door Assembly',
    '右前门装置': 'Right Front Door Assembly',
    '左后门装置': 'Left Rear Door Assembly',
    '右后门装置': 'Right Rear Door Assembly',
    '侧围角窗及饰件装置': 'Quarter Window & Trim',
    '发动机盖附件装置': 'Hood Accessories',
    '背门附件装置': 'Tailgate Accessories',
    '前门附件装置': 'Front Door Accessories',
    '左前门密封件部件': 'Left Front Door Seals',
    '左前门玻璃及堵盖部件': 'Left Front Door Glass & Plugs',
    '右前门密封件部件': 'Right Front Door Seals',
    '右前门玻璃及堵盖部件': 'Right Front Door Glass & Plugs',
    '后门附件装置': 'Rear Door Accessories',
    '左后门锁部件': 'Left Rear Door Lock',
    '左后门密封件部件': 'Left Rear Door Seals',
    '左后门玻璃及堵盖部件': 'Left Rear Door Glass & Plugs',
    '右后门锁部件': 'Right Rear Door Lock',
    '右后门密封件部件': 'Right Rear Door Seals',
    '右后门玻璃及堵盖部件': 'Right Rear Door Glass & Plugs',
    '背门装置': 'Tailgate Assembly',
    '发动机盖装置': 'Hood Assembly',
    '车身总成部件': 'Body Assembly Parts',
    '车身前端部件': 'Front Body Structure',
    '前围板部件': 'Firewall / Cowl Panel',
    '左前机舱纵梁部件': 'Left Front Engine Bay Rail',
    '右前机舱纵梁部件': 'Right Front Engine Bay Rail',
    '顶盖外板部件': 'Roof Outer Panel',
    '前地板部件': 'Front Floor Panel',
    '后地板部件': 'Rear Floor Panel',
    '中后地板部件': 'Center-Rear Floor Panel',
    '翼子板部件': 'Fender Panel',
    '防撞梁部件': 'Impact/Crash Beam',
    '加油口盖部件': 'Fuel Filler Door',
    '堵盖及贴片部件': 'Plugs & Adhesive Patches',
    '左侧围内板部件': 'Left Side Inner Panel',
    '右侧围内板部件': 'Right Side Inner Panel',
    '右侧围外板部件': 'Right Side Outer Panel',
    '左侧围外板部件': 'Left Side Outer Panel',
    '胶水': 'Adhesives / Sealant',
    '密封圈': 'O-rings / Gaskets',
    '线束修复': 'Wiring Harness Repair',
    '养护': 'Maintenance Fluids',
    '油漆': 'Paint',
    '油脂': 'Grease / Lubricants',
    '其他': 'Other Consumables',
    '机舱线束保险丝': 'Engine Bay Fuses',
    '后部保险丝盒': 'Rear Fuse Box',
    '抽芯铆钉': 'Blind Rivets / Fasteners',
}

# Merge for lookups
ALL_NAMES = {**SYSTEMS, **SUBS}

# Prompt for Qwen2.5-VL to extract table rows
OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has 4 columns:
- 序号 (index number)
- 热点ID (hotspot ID)
- 零件号码 (part number)
- 零件名称 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}]

Rules:
- Extract EVERY row, including those that span multiple lines
- Part numbers typically start with X01-, a 7-digit number, or Q-prefixed codes
- If a cell is empty, use an empty string ""
- If the image is not a parts table, return: []"""


# ===========================================================================
# Page → system/subsystem mapping
# ===========================================================================

def build_page_system_map(content_list: list[dict]) -> dict[int, dict]:
    """
    Build a mapping from page_idx to {system_zh, system_en, subsystem_zh, subsystem_en}.

    Walks through content_list text entries in order, tracking the current
    system (text_level=1 matching SYSTEMS dict) and subsystem (other text entries).
    Each page inherits the most recently seen system/subsystem.
    """
    page_map: dict[int, dict] = {}
    current_sys_zh = ""
    current_sys_en = ""
    current_sub_zh = ""
    current_sub_en = ""

    for item in content_list:
        if item.get("type") != "text":
            continue
        text = item.get("text", "").strip()
        page = item.get("page_idx", -1)
        if not text or page < 0:
            continue

        # Clean text for matching (remove dates, suffixes, etc.)
        clean = _clean_for_match(text)

        if clean in SYSTEMS:
            current_sys_zh = clean
            current_sys_en = SYSTEMS[clean]
            current_sub_zh = ""
            current_sub_en = ""
        elif clean in SUBS:
            current_sub_zh = clean
            current_sub_en = SUBS[clean]

        if current_sys_zh:
            page_map[page] = {
                "system_zh": current_sys_zh,
                "system_en": current_sys_en,
                "subsystem_zh": current_sub_zh,
                "subsystem_en": current_sub_en,
            }

    # Forward-fill: pages without explicit entries inherit from nearest prior page
    if page_map:
        max_page = max(item.get("page_idx", 0) for item in content_list if item.get("page_idx") is not None)
        last_info = None
        for p in range(max_page + 1):
            if p in page_map:
                last_info = page_map[p]
            elif last_info:
                page_map[p] = last_info

    return page_map


def _clean_for_match(text: str) -> str:
    """Clean text for system/subsystem dict matching."""
    c = text.strip()
    # Remove trailing date/version patterns
    c = re.sub(r'\s*[\(-]?\d{4}[-/]\d{1,2}[-/]\d{1,2}\)?', '', c)
    c = re.sub(r'-\d+$', '', c)
    c = re.sub(r'-新$', '', c)
    c = re.sub(r'\.svg\.svg$', '', c)
    c = c.strip(' -')
    return c


# ===========================================================================
# Model loading (mirrors caption_images.py)
# ===========================================================================

def load_model(device: str) -> tuple[Any, Any]:
    """Load Qwen2.5-VL-7B-Instruct. Returns (model, processor)."""
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    log.info("Loading %s on %s …", MODEL_ID, device)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(
        MODEL_ID, trust_remote_code=True, use_fast=False,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    )
    model.eval()

    elapsed = time.time() - t0
    vram = 0.0
    if torch.cuda.is_available():
        dev_idx = int(device.split(":")[-1]) if ":" in device else 0
        vram = torch.cuda.memory_allocated(dev_idx) / 1024 ** 3
    log.info("Model loaded in %.1f s (VRAM: %.1f GB)", elapsed, vram)
    return model, processor


def ocr_table_image(
    model: Any,
    processor: Any,
    image_path: Path,
    device: str,
) -> list[dict]:
    """
    Run Qwen2.5-VL on a single table image.
    Returns list of dicts: [{idx, hotspot, part_number, part_name}]
    """
    import torch
    from PIL import Image as PILImage

    try:
        pil_image = PILImage.open(image_path).convert("RGB")
    except Exception as exc:
        log.warning("Cannot read image %s: %s", image_path, exc)
        return []

    # Resize to fit in GPU memory (~8 GB free after model load)
    w, h = pil_image.size
    max_side = 1024
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        pil_image = pil_image.resize(
            (int(w * scale), int(h * scale)), PILImage.LANCZOS
        )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": OCR_PROMPT},
            ],
        }
    ]

    try:
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        inputs = processor(
            text=[text], images=[pil_image], return_tensors="pt", padding=True,
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs, max_new_tokens=2048, do_sample=False,
            )

        input_len = inputs["input_ids"].shape[1]
        generated = output_ids[0, input_len:]
        response = processor.decode(generated, skip_special_tokens=True).strip()

        # Free GPU memory
        del inputs, output_ids
        torch.cuda.empty_cache()

        return _parse_json_response(response)

    except Exception as exc:
        log.error("Inference failed for %s: %s", image_path, exc)
        # Still try to free memory on error
        torch.cuda.empty_cache()
        return []


def _parse_json_response(response: str) -> list[dict]:
    """Parse JSON array from model response, handling common issues."""
    # Try direct parse
    try:
        data = json.loads(response)
        if isinstance(data, list):
            return [_normalize_row(r) for r in data if isinstance(r, dict)]
    except json.JSONDecodeError:
        pass

    # Try extracting JSON array from surrounding text
    match = re.search(r'\[.*\]', response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return [_normalize_row(r) for r in data if isinstance(r, dict)]
        except json.JSONDecodeError:
            pass

    # Try line-by-line JSON objects
    rows = []
    for line in response.split('\n'):
        line = line.strip().rstrip(',')
        if line.startswith('{'):
            try:
                obj = json.loads(line)
                rows.append(_normalize_row(obj))
            except json.JSONDecodeError:
                continue
    return rows


def _normalize_row(row: dict) -> dict:
    """Normalize a parsed row dict to have consistent keys."""
    return {
        "idx": str(row.get("idx", row.get("序号", ""))),
        "hotspot": str(row.get("hotspot", row.get("热点ID", row.get("hotspot_id", "")))),
        "part_number": str(row.get("part_number", row.get("零件号码", ""))).strip(),
        "part_name": str(row.get("part_name", row.get("零件名称", ""))).strip(),
    }


# ===========================================================================
# Database
# ===========================================================================

def create_parts_table(conn: sqlite3.Connection) -> None:
    """Create the parts table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parts (
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
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_system ON parts(system_zh)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_name ON parts(part_name_zh)")
    conn.commit()


def insert_parts(
    conn: sqlite3.Connection,
    rows: list[dict],
    system_info: dict,
    page_idx: int,
    source_image: str,
) -> int:
    """Insert parsed part rows into the parts table. Returns count inserted."""
    inserted = 0
    for row in rows:
        pn = row.get("part_number", "").strip()
        name = row.get("part_name", "").strip()
        if not pn or not name:
            continue

        # Try to find English translation from SUBS dict
        name_en = SUBS.get(name, "")

        conn.execute(
            """INSERT INTO parts
               (part_number, part_name_zh, part_name_en, hotspot_id,
                system_zh, system_en, subsystem_zh, subsystem_en,
                page_idx, source_image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pn,
                name,
                name_en or None,
                row.get("hotspot", "") or None,
                system_info.get("system_zh", ""),
                system_info.get("system_en", ""),
                system_info.get("subsystem_zh", ""),
                system_info.get("subsystem_en", ""),
                page_idx,
                source_image,
            ),
        )
        inserted += 1
    return inserted


def get_processed_images(conn: sqlite3.Connection) -> set[str]:
    """Get set of source_image values already in parts table."""
    try:
        cur = conn.execute("SELECT DISTINCT source_image FROM parts WHERE source_image IS NOT NULL")
        return {row[0] for row in cur.fetchall()}
    except sqlite3.OperationalError:
        return set()


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="OCR parts tables from L9 catalog with Qwen2.5-VL-7B",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(_KB_DB), help="Path to kb.db")
    parser.add_argument("--device", default="cuda:0", help="CUDA device")
    parser.add_argument("--limit", type=int, default=None, help="Max tables to process")
    parser.add_argument("--dry-run", action="store_true", help="Run OCR but don't write to DB")
    parser.add_argument("--resume", action="store_true", help="Skip already-processed images")
    parser.add_argument("--output-log", default=None, help="JSONL log file for raw OCR results")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("kb.db not found at %s", db_path)
        sys.exit(1)

    if not _CONTENT_LIST.exists():
        log.error("content_list.json not found at %s", _CONTENT_LIST)
        sys.exit(1)

    # Load content list
    with open(_CONTENT_LIST, "r", encoding="utf-8") as f:
        content_list = json.load(f)

    # Collect table entries
    tables = [
        {"img_path": item["img_path"], "page_idx": item.get("page_idx", -1)}
        for item in content_list
        if item.get("type") == "table" and item.get("img_path")
    ]
    log.info("Found %d table entries in content_list.json", len(tables))

    # Build page→system mapping
    page_map = build_page_system_map(content_list)
    log.info("Page→system mapping covers %d pages", len(page_map))

    # Open DB and create table
    conn = sqlite3.connect(str(db_path), timeout=120)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    create_parts_table(conn)

    # Resume: skip already-processed
    processed = set()
    if args.resume:
        processed = get_processed_images(conn)
        if processed:
            log.info("Resume mode: %d images already processed, skipping", len(processed))

    # Filter tables
    pending = [t for t in tables if t["img_path"] not in processed]
    if args.limit:
        pending = pending[:args.limit]

    if not pending:
        log.info("No tables to process.")
        conn.close()
        return

    log.info("Tables to process: %d", len(pending))

    # Load model
    model, processor = load_model(args.device)

    # Open optional log
    log_fh = None
    if args.output_log:
        log_fh = open(args.output_log, "a", encoding="utf-8")

    t_start = time.time()
    total_parts = 0
    total_tables_ok = 0
    total_tables_empty = 0

    for i, table_info in enumerate(pending):
        img_rel = table_info["img_path"]
        page_idx = table_info["page_idx"]
        img_path = _IMAGE_BASE / img_rel

        if not img_path.exists():
            log.warning("Image not found: %s", img_path)
            continue

        # Get system info for this page
        sys_info = page_map.get(page_idx, {
            "system_zh": "", "system_en": "",
            "subsystem_zh": "", "subsystem_en": "",
        })

        # OCR
        rows = ocr_table_image(model, processor, img_path, args.device)

        if rows:
            total_tables_ok += 1
            if not args.dry_run:
                inserted = insert_parts(conn, rows, sys_info, page_idx, img_rel)
                total_parts += inserted
                # Commit every 10 tables
                if (i + 1) % 10 == 0:
                    conn.commit()
            else:
                total_parts += len([r for r in rows if r.get("part_number")])

            if log_fh:
                log_fh.write(json.dumps({
                    "image": img_rel,
                    "page_idx": page_idx,
                    "system": sys_info.get("system_en", ""),
                    "subsystem": sys_info.get("subsystem_en", ""),
                    "parts_count": len(rows),
                    "parts": rows,
                }, ensure_ascii=False) + "\n")
        else:
            total_tables_empty += 1

        # Progress
        elapsed = time.time() - t_start
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(pending) - i - 1) / rate if rate > 0 else 0
        log.info(
            "  %d/%d  parts=%d  ok=%d  empty=%d  %.2f tbl/s  ETA %.0fs  [%s / %s]",
            i + 1, len(pending), total_parts, total_tables_ok, total_tables_empty,
            rate, eta, sys_info.get("system_en", "?"), sys_info.get("subsystem_en", "?"),
        )

    # Final commit
    if not args.dry_run:
        conn.commit()

    conn.close()
    if log_fh:
        log_fh.close()

    elapsed_total = time.time() - t_start
    log.info("=" * 60)
    log.info("  Done in %.1f s", elapsed_total)
    log.info("  Tables processed: %d (ok=%d, empty=%d)", len(pending), total_tables_ok, total_tables_empty)
    log.info("  Parts extracted: %d", total_parts)
    if args.dry_run:
        log.info("  *** DRY RUN — no DB writes ***")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
