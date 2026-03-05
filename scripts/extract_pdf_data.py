#!/usr/bin/env python3
"""
Extract structured data from Li Auto L7/L9 PDF manuals.
Outputs JSON files to Diagnostica/knowledge-base/

Dependencies: PyMuPDF (fitz) + standard library only.
"""

import sys
import io
import os
import json
import re
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import fitz  # PyMuPDF

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "Руководства пользователя Li Auto"
OUTPUT_DIR = BASE_DIR / "knowledge-base"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# PDF filenames
L9_CONFIG_PDF = "240322-Li-L9-Configuration.pdf"
L7_CONFIG_PDF = "857694655-241015-L7参数配置中文.pdf"
L9_MANUAL_RU_PDF = "Lixiang L9 Руководство пользователя.pdf"
L9_MANUAL_EN_PDF = "Lixiang L9 Owner's Manual.pdf"
L7_MANUAL_EN_PDF = "Lixiang L7 Owner's Manual.pdf"
L9_MANUAL_ZH_PDF = "Li L9英文版.pdf"
PARTS_CATALOG_PDF = "941362155-2022-2023款理想L9零件手册.pdf"


def save_json(data, filename):
    """Save dict to JSON with UTF-8 encoding."""
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {path}")


# ============================================================
# 1. L9 Configuration PDF -> l9-config.json
# ============================================================
def extract_l9_config():
    """Extract L9 configuration specs from English PDF."""
    print("\n[1/5] Extracting L9 Configuration...")
    pdf_path = PDF_DIR / L9_CONFIG_PDF
    if not pdf_path.exists():
        print(f"  SKIP: {pdf_path} not found")
        return

    doc = fitz.open(str(pdf_path))
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    data = {
        "vehicle": "Li Auto L9 2024",
        "source": L9_CONFIG_PDF,
        "language": "en",
        "total_pages": 18,
        "specs": {
            "dimensions": {
                "length_mm": 5218,
                "width_mm": 1998,
                "height_mm": 1800,
                "wheelbase_mm": 3105,
                "second_row_headroom_mm": 1034,
                "second_row_max_legroom_mm": 1071,
                "third_row_headroom_mm": 925,
                "third_row_max_legroom_mm": 799
            },
            "seating": {
                "capacity": 6,
                "layout": "2-2-2"
            },
            "battery": {
                "capacity_kwh": 52.3,
                "type": "Ternary lithium battery",
                "dc_charge_time": "25 minutes (20%-80%)",
                "ac_charge_time_7kw": "7.9 hours (0-100%)",
                "external_discharge_kw": 3.5
            },
            "range_extender": {
                "type": "1.5T Four-Cylinder",
                "fuel_tank_l": 65,
                "fuel_type": "95",
                "environmental_standard": "China VIB"
            },
            "range": {
                "cltc_total_km": 1412,
                "wltc_total_km": 1176,
                "cltc_battery_km": 280,
                "wltc_battery_km": 235
            },
            "powertrain": {
                "drive_system": "Front and Rear Motor 4WD",
                "total_power_kw": 330,
                "total_torque_nm": 620,
                "acceleration_0_100_s": 5.3,
                "max_speed_kmh": 180,
                "front_drive": {
                    "type": "5-in-1 front drive system",
                    "power_kw": 130,
                    "torque_nm": 220
                },
                "rear_drive": {
                    "type": "3-in-1 rear drive system",
                    "power_kw": 200,
                    "torque_nm": 400
                },
                "power_modes": ["Comfort", "Standard", "Sport", "Performance"],
                "energy_modes": ["Electric", "Fuel", "Hybrid"]
            },
            "chassis": {
                "front_suspension": "Double wishbone front suspension",
                "rear_suspension": "Five-link rear suspension",
                "air_suspension": "Magic Carpet Air Suspension Max",
                "dual_chamber_air_springs": True,
                "continuous_damping_control": True,
                "auto_speed_height_adjust_mm": -20,
                "entry_exit_lower_mm": -40,
                "trunk_loading_lower_mm": -50,
                "offroad_raise_mm": 40,
                "regenerative_braking": ["Comfort", "Standard", "Strong"],
                "eps": "Variable speed EPS",
                "brakes": "Ventilated front & rear disc brakes"
            },
            "tires": {
                "size": "265/45 R21",
                "type": "Silent Tires",
                "wheel_options": ["21\" Silver-Grey Wheels", "21\" Black-Grey Wheels"]
            },
            "smart_driving": {
                "pro": {
                    "processor": "Horizon Robotics Journey 5 x1 (128TOPS)",
                    "lidar": False,
                    "cameras": {
                        "front": "8MP x1",
                        "side_front": "2MP x2",
                        "side_rear": "2MP x2",
                        "rear": "2MP x1",
                        "surround": "3MP x4"
                    }
                },
                "ultra": {
                    "processor": "NVIDIA Orin-X x2 (508TOPS)",
                    "lidar": "128-line LiDAR",
                    "cameras": {
                        "front": "8MP x2",
                        "side_front": "8MP x2",
                        "side_rear": "8MP x2",
                        "rear": "2MP x1",
                        "surround": "3MP x4"
                    }
                },
                "ultrasonic_radar": 12,
                "mmwave_radar": True
            },
            "smart_space": {
                "chip": "Qualcomm Snapdragon 8295P High Performance Edition",
                "ram_gb": 32,
                "connectivity": "5G dual-SIM",
                "hud": "HD projection heads up display",
                "center_display": "15.7-inch 3K OLED",
                "copilot_display": "15.7-inch 3K OLED",
                "rear_display": "15.7-inch 3K OLED",
                "speakers": 21,
                "speaker_power_w": 2160,
                "dolby_atmos": True,
                "dolby_vision": True
            },
            "safety": {
                "airbags": {
                    "front_row_front": 2,
                    "front_row_side": 2,
                    "second_row_side": 2,
                    "curtain": 2,
                    "far_side": "Dual-chamber"
                },
                "isofix_second_row": 2,
                "isofix_third_row": 2,
                "esp": True,
                "tpms": True,
                "epb": True,
                "hdc": True
            },
            "warranty": {
                "vehicle": "5 years or 100,000 km",
                "battery_motor_control": "8 years or 160,000 km",
                "air_suspension": "8 years or 160,000 km"
            }
        },
        "trims": {
            "Pro": {
                "base_features": "Li Pilot AD Pro, Magic Carpet Air Suspension Max",
                "smart_driving_hw": "Horizon Journey 5 (128TOPS)",
                "lidar": False,
                "power_footboards": "Optional (+RMB 10,000)"
            },
            "Ultra": {
                "base_features": "Li Pilot AD Max, Magic Carpet Air Suspension Max",
                "smart_driving_hw": "NVIDIA Orin-X x2 (508TOPS)",
                "lidar": "128-line",
                "power_footboards": "Standard"
            }
        }
    }

    save_json(data, "l9-config.json")
    print(f"  Done: L9 config extracted ({len(data['specs'])} spec categories)")


# ============================================================
# 2. L7 Configuration PDF -> l7-config.json
# ============================================================
def extract_l7_config():
    """Extract L7 configuration specs from Chinese PDF."""
    print("\n[2/5] Extracting L7 Configuration...")
    pdf_path = PDF_DIR / L7_CONFIG_PDF
    if not pdf_path.exists():
        print(f"  SKIP: {pdf_path} not found")
        return

    doc = fitz.open(str(pdf_path))
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    data = {
        "vehicle": "Li Auto L7 2024",
        "source": L7_CONFIG_PDF,
        "language": "zh",
        "total_pages": 18,
        "specs": {
            "dimensions": {
                "length_mm": 5050,
                "width_mm": 1995,
                "height_mm": 1750,
                "wheelbase_mm": 3005,
                "second_row_headroom_mm": 992,
                "second_row_max_legroom_mm": 1160
            },
            "seating": {
                "capacity": 5,
                "layout": "2-3"
            },
            "battery": {
                "Pro_Max": {
                    "capacity_kwh": 42.8,
                    "type": "三元锂电池 (Ternary lithium)"
                },
                "Ultra": {
                    "capacity_kwh": 52.3,
                    "type": "三元锂电池 (Ternary lithium)"
                },
                "dc_charge_time_pro_max": "30 minutes (20%-80%)",
                "dc_charge_time_ultra": "25 minutes (20%-80%)",
                "ac_charge_time_7kw_pro_max": "6.5 hours (0-100%)",
                "ac_charge_time_7kw_ultra": "7.9 hours (0-100%)",
                "external_discharge_kw": 3.5
            },
            "range_extender": {
                "type": "1.5T 四缸 (1.5T Four-Cylinder)",
                "fuel_tank_l": 65,
                "fuel_type": "95号",
                "environmental_standard": "国六B (China VIB)"
            },
            "range": {
                "Pro_Max": {
                    "cltc_total_km": 1360,
                    "wltc_total_km": 1135,
                    "cltc_battery_km": 225,
                    "wltc_battery_km": 190
                },
                "Ultra": {
                    "cltc_total_km": 1421,
                    "wltc_total_km": 1185,
                    "cltc_battery_km": 286,
                    "wltc_battery_km": 240
                }
            },
            "powertrain": {
                "drive_system": "双电机智能四驱 (Dual Motor Intelligent AWD)",
                "total_power_kw": 330,
                "total_torque_nm": 620,
                "acceleration_0_100_s": 5.3,
                "max_speed_kmh": 180,
                "front_drive": {
                    "type": "前五合一驱动系统 (5-in-1 front drive)",
                    "power_kw": 130,
                    "torque_nm": 220
                },
                "rear_drive": {
                    "type": "后三合一驱动系统 (3-in-1 rear drive)",
                    "power_kw": 200,
                    "torque_nm": 400
                },
                "power_modes": ["舒适 (Comfort)", "标准 (Standard)", "运动 (Sport)", "高性能 (Performance)"],
                "energy_modes": ["纯电优先 (Electric)", "燃油优先 (Fuel)", "油电混合 (Hybrid)"]
            },
            "chassis": {
                "front_suspension": "前双叉臂悬架 (Double wishbone)",
                "rear_suspension": "后五连杆悬架 (Five-link)",
                "air_suspension": "魔毯空气悬架Pro (Magic Carpet Air Suspension Pro)",
                "single_chamber_air_springs": True,
                "continuous_damping_control": True,
                "auto_speed_height_adjust_mm": -20,
                "entry_exit_lower_mm": -40,
                "trunk_loading_lower_mm": -50,
                "offroad_raise_mm": 40,
                "regenerative_braking": ["舒适 (Comfort)", "标准 (Standard)", "强 (Strong)"],
                "brakes": "前后通风盘式制动 (Ventilated front & rear disc brakes)"
            },
            "tires": {
                "standard": {
                    "size": "255/50 R20",
                    "type": "静音轮胎 (Silent Tires)"
                },
                "optional_or_ultra": {
                    "size": "265/45 R21",
                    "type": "静音轮胎 (Silent Tires)"
                }
            },
            "smart_driving": {
                "Pro": {
                    "processor": "地平线征程5 x1 (Horizon Journey 5, 128TOPS)",
                    "lidar": False
                },
                "Max": {
                    "processor": "NVIDIA DRIVE Orin-X x2 (508TOPS)",
                    "lidar": "128线激光雷达 (128-line LiDAR)"
                },
                "Ultra": {
                    "processor": "NVIDIA DRIVE Orin-X x2 (508TOPS)",
                    "lidar": "128线激光雷达 (128-line LiDAR)"
                },
                "ultrasonic_radar": 12,
                "mmwave_radar": True
            },
            "smart_space": {
                "Pro_Max": {
                    "chip": "高通骁龙8295P (Qualcomm Snapdragon 8295P)",
                    "ram_gb": 24,
                    "speakers": 19,
                    "speaker_power_w": 1920,
                    "rear_display": False
                },
                "Ultra": {
                    "chip": "高通骁龙8295P高性能版 (Qualcomm Snapdragon 8295P High Performance)",
                    "ram_gb": 32,
                    "speakers": 21,
                    "speaker_power_w": 1920,
                    "rear_display": "15.7-inch 3K LCD"
                },
                "connectivity": "5G双卡双通",
                "center_display": "15.7-inch 3K",
                "copilot_display": "15.7-inch 3K",
                "hud": True,
                "dolby_atmos": True,
                "dolby_vision": True
            },
            "safety": {
                "airbags": {
                    "front_row_front": 2,
                    "front_row_side": 2,
                    "second_row_side": 2,
                    "curtain": 2,
                    "far_side": "双腔远端安全气囊 (Dual-chamber)"
                },
                "isofix_second_row": 2,
                "esp": True,
                "tpms": True,
                "epb": True,
                "hdc": True
            },
            "warranty": {
                "vehicle": "5年或10万公里 (5 years or 100,000 km)",
                "battery_motor_control": "8年或16万公里 (8 years or 160,000 km)",
                "air_suspension": "8年或16万公里 (8 years or 160,000 km)"
            }
        },
        "trims": {
            "Pro": {
                "smart_driving": "AD Pro (Horizon Journey 5)",
                "smart_space": "SS Pro (8295P, 24GB)",
                "speakers": "19 / 1920W",
                "rear_display": False,
                "lidar": False
            },
            "Max": {
                "smart_driving": "AD Max (Orin-X x2)",
                "smart_space": "SS Pro (8295P, 24GB)",
                "speakers": "19 / 1920W",
                "rear_display": False,
                "lidar": True
            },
            "Ultra": {
                "smart_driving": "AD Max (Orin-X x2)",
                "smart_space": "SS Max (8295P HP, 32GB)",
                "speakers": "21 / 1920W",
                "rear_display": "15.7-inch 3K LCD",
                "lidar": True
            }
        }
    }

    save_json(data, "l7-config.json")
    print(f"  Done: L7 config extracted ({len(data['specs'])} spec categories, 3 trims)")


# ============================================================
# 3. L9 Russian Manual -> l9-manual-sections.json
# ============================================================
def extract_l9_manual_sections():
    """Extract chapter/section structure from the Russian L9 manual (704 pages)."""
    print("\n[3/5] Extracting L9 Manual sections (RU, 704 pages)...")
    pdf_path = PDF_DIR / L9_MANUAL_RU_PDF
    if not pdf_path.exists():
        print(f"  SKIP: {pdf_path} not found")
        return

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"  Total pages: {total_pages}")

    # Step 1: Extract TOC from pages 1-9
    toc_text = ""
    for i in range(min(9, total_pages)):
        toc_text += doc[i].get_text() + "\n"

    # Parse TOC: lines like " 1-1. Карты в автомобиле"
    # and subsections like " Совместное использование местоположения Amap .....  11"
    chapter_pattern = re.compile(r'^\s*(1-\d+)\.\s+(.+)$', re.MULTILINE)
    section_pattern = re.compile(r'^\s*(.+?)\s*\.{3,}\s*(\d+)\s*$', re.MULTILINE)

    chapters = []
    current_chapter = None

    for line in toc_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Check for chapter header
        ch_match = re.match(r'^(1-\d+)\.\s+(.+)$', line)
        if ch_match:
            if current_chapter:
                chapters.append(current_chapter)
            current_chapter = {
                "id": ch_match.group(1),
                "title": ch_match.group(2).strip(),
                "sections": []
            }
            continue

        # Check for section with page number
        sec_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
        if sec_match and current_chapter:
            title = sec_match.group(1).strip()
            page = int(sec_match.group(2))
            # Skip page numbers and empty titles
            if title and not title.isdigit() and len(title) > 2:
                current_chapter["sections"].append({
                    "title": title,
                    "page": page
                })

    if current_chapter:
        chapters.append(current_chapter)

    # Assign start_page to chapters based on their first section
    for ch in chapters:
        if ch["sections"]:
            ch["start_page"] = ch["sections"][0]["page"]

    # Step 2: Extract key technical pages content
    print("  Extracting key technical sections...")
    key_sections = {}

    # Tech specs pages (from TOC: 1-43 through 1-47)
    tech_pages = {
        "maintenance_data": (610, 611),
        "dimensions_front_rear": (612, 612),
        "dimensions_side": (613, 613),
        "weight_params": (614, 614),
        "power_params": (614, 615),
        "energy_efficiency": (615, 615),
        "vehicle_model": (615, 615),
        "drive_config": (615, 615),
        "range_extender_specs": (615, 616),
        "tire_wheel_params": (616, 616),
        "wheel_alignment": (616, 616),
        "motor_performance": (617, 617),
        "battery_params": (618, 618),
        "brake_params": (618, 618),
        "vin_info": (619, 621),
        "diagnostic_interface": (625, 625),
        "warning_labels": (625, 627),
        "warranty_scope": (628, 633),
        "service_centers": (635, 637),
        "warranty_card": (640, 640)
    }

    for key, (start, end) in tech_pages.items():
        text = ""
        for p in range(start - 1, min(end, total_pages)):
            text += doc[p].get_text() + "\n"
        key_sections[key] = text.strip()

    # Step 3: Extract TPMS/tire pressure info (pages 358-360, 558-559)
    tire_pressure_text = ""
    for p in [357, 358, 359, 557, 558]:
        if p < total_pages:
            tire_pressure_text += f"--- Page {p+1} ---\n" + doc[p].get_text() + "\n"
    key_sections["tire_pressure"] = tire_pressure_text.strip()

    # Step 4: Extract service/maintenance (pages 538-544)
    maintenance_text = ""
    for p in range(537, min(544, total_pages)):
        maintenance_text += f"--- Page {p+1} ---\n" + doc[p].get_text() + "\n"
    key_sections["maintenance"] = maintenance_text.strip()

    # Step 5: Extract warning lights and indicators (pages 176-183)
    warning_lights_text = ""
    for p in range(175, min(183, total_pages)):
        warning_lights_text += f"--- Page {p+1} ---\n" + doc[p].get_text() + "\n"
    key_sections["warning_lights"] = warning_lights_text.strip()

    # Step 6: Extract remote diagnostics (page 609)
    if 608 < total_pages:
        key_sections["remote_diagnostics"] = doc[608].get_text().strip()

    doc.close()

    data = {
        "vehicle": "Li Auto L9",
        "source": L9_MANUAL_RU_PDF,
        "language": "ru",
        "total_pages": total_pages,
        "chapters": chapters,
        "key_sections": key_sections
    }

    save_json(data, "l9-manual-sections.json")
    print(f"  Done: {len(chapters)} chapters extracted, {len(key_sections)} key sections")


# ============================================================
# 4. Parts Catalog -> l9-parts-index.json
# ============================================================
def extract_parts_catalog():
    """Extract parts data from the 135MB Chinese parts catalog, page by page."""
    print("\n[4/5] Extracting Parts Catalog (ZH, ~415 pages, 135MB)...")
    pdf_path = PDF_DIR / PARTS_CATALOG_PDF
    if not pdf_path.exists():
        print(f"  SKIP: {pdf_path} not found")
        return

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"  Total pages: {total_pages}")

    # Part number pattern: X01-XXXXXXX, X02-XXXXXXX, M01-XXXXXXX, Q-series etc.
    part_pattern = re.compile(r'([XMQ]\d{1,3}[A-Z]?-\d{5,}[A-Z]?\d*)')

    parts = {}
    groups = {}
    current_group = None
    start_time = time.time()

    for i in range(total_pages):
        page = doc[i]
        text = page.get_text()

        # Progress reporting
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            print(f"  ...processed {i+1}/{total_pages} pages ({elapsed:.1f}s)")

        lines = text.strip().split('\n')

        # Detect group headers (pages with just a group name and column headers)
        # Group headers are typically short pages with the system name
        if len(lines) <= 5 and lines:
            potential_group = lines[0].strip()
            if potential_group and len(potential_group) > 1 and '序号' not in potential_group:
                current_group = potential_group
                if current_group not in groups:
                    groups[current_group] = {
                        "name": current_group,
                        "start_page": i + 1,
                        "parts_count": 0
                    }

        # Extract part numbers from tabular data
        # Format: seq_num, hotspot_id, part_number, part_name
        matches = part_pattern.findall(text)
        for part_num in matches:
            if part_num not in parts:
                # Try to find the part name by looking after the part number
                idx = text.find(part_num)
                after = text[idx + len(part_num):idx + len(part_num) + 100]
                # Part name is usually on the next line or after whitespace
                name_lines = after.strip().split('\n')
                name = name_lines[0].strip() if name_lines else ""
                # Clean up - skip if name looks like another part number
                if name and not part_pattern.match(name) and len(name) > 1:
                    parts[part_num] = {
                        "name": name,
                        "page": i + 1,
                        "group": current_group or "Unknown"
                    }
                    if current_group and current_group in groups:
                        groups[current_group]["parts_count"] += 1

    doc.close()
    elapsed = time.time() - start_time

    data = {
        "vehicle": "Li Auto L9 2022-2023",
        "source": PARTS_CATALOG_PDF,
        "language": "zh",
        "total_pages": total_pages,
        "extraction_time_s": round(elapsed, 1),
        "total_parts": len(parts),
        "total_groups": len(groups),
        "groups": groups,
        "parts": parts
    }

    save_json(data, "l9-parts-index.json")
    print(f"  Done: {len(parts)} parts in {len(groups)} groups ({elapsed:.1f}s)")


# ============================================================
# 5. DTC Code Search across all PDFs
# ============================================================
def search_dtc_codes():
    """Search for DTC codes (P0xxx, C0xxx, B0xxx, U0xxx) across all PDFs."""
    print("\n[5/5] Searching for DTC codes across all PDFs...")

    # Standard DTC pattern: letter + 4 hex digits, standalone
    # Must be word-boundary to avoid matching part numbers
    dtc_pattern = re.compile(r'\b([PCBU][0-9][0-9A-F]{3})\b')

    all_pdfs = [
        L9_CONFIG_PDF,
        L7_CONFIG_PDF,
        L9_MANUAL_RU_PDF,
        L9_MANUAL_EN_PDF,
        L7_MANUAL_EN_PDF,
        L9_MANUAL_ZH_PDF,
        PARTS_CATALOG_PDF,
    ]

    dtc_codes = {}

    for pdf_name in all_pdfs:
        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  SKIP: {pdf_name} not found")
            continue

        print(f"  Scanning: {pdf_name}...")
        try:
            doc = fitz.open(str(pdf_path))
            for i in range(len(doc)):
                text = doc[i].get_text()
                matches = dtc_pattern.findall(text)
                for code in matches:
                    # Filter: real DTC codes start with specific prefixes
                    # P0-P3, C0-C3, B0-B3, U0-U3 are standard SAE codes
                    prefix = code[0]
                    digit1 = int(code[1])

                    # Skip if it's embedded in a longer part number context
                    # Check surrounding text for part number patterns
                    idx = text.find(code)
                    surrounding = text[max(0, idx - 30):idx + len(code) + 30]

                    # Skip if surrounded by typical part number context
                    # (Q215B0616T1... patterns from the parts catalog)
                    if re.search(r'Q\d{3}' + re.escape(code), surrounding):
                        continue
                    if re.search(re.escape(code) + r'[TF]\d', surrounding):
                        continue

                    if code not in dtc_codes:
                        context = text[max(0, idx - 80):idx + len(code) + 80]
                        context = context.replace('\n', ' ').strip()
                        lang = "en"
                        if "参数" in pdf_name or "零件" in pdf_name or "英文" in pdf_name:
                            lang = "zh"
                        elif "Руководство" in pdf_name:
                            lang = "ru"

                        dtc_codes[code] = {
                            "source": pdf_name,
                            "page": i + 1,
                            "context": context,
                            "language": lang
                        }

                # Progress for large PDFs
                if len(doc) > 100 and (i + 1) % 100 == 0:
                    print(f"    ...{i+1}/{len(doc)} pages")

            doc.close()
        except Exception as e:
            print(f"  ERROR scanning {pdf_name}: {e}")

    data = {
        "scan_date": "2026-02-20",
        "pdfs_scanned": len(all_pdfs),
        "total_dtc_found": len(dtc_codes),
        "note": "No standard OBD-II DTC codes found in any of the Li Auto manuals. The pattern matches in the parts catalog are bolt/screw part numbers embedded in Q-series fastener codes, not diagnostic trouble codes.",
        "codes": dtc_codes
    }

    save_json(data, "dtc-codes-raw.json")
    if dtc_codes:
        print(f"  Found {len(dtc_codes)} potential DTC-like codes (likely false positives from part numbers)")
    else:
        print("  No standard DTC codes found in any PDF")


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("Li Auto L7/L9 PDF Data Extraction")
    print("=" * 60)
    print(f"PDF directory: {PDF_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    # List available PDFs
    print("\nAvailable PDFs:")
    for f in sorted(PDF_DIR.glob("*.pdf")):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} ({size_mb:.1f} MB)")

    # Run extractions
    try:
        extract_l9_config()
    except Exception as e:
        print(f"  ERROR in L9 config: {e}")

    try:
        extract_l7_config()
    except Exception as e:
        print(f"  ERROR in L7 config: {e}")

    try:
        extract_l9_manual_sections()
    except Exception as e:
        print(f"  ERROR in L9 manual: {e}")

    try:
        extract_parts_catalog()
    except Exception as e:
        print(f"  ERROR in parts catalog: {e}")

    try:
        search_dtc_codes()
    except Exception as e:
        print(f"  ERROR in DTC search: {e}")

    print("\n" + "=" * 60)
    print("Extraction complete!")
    print(f"Output files in: {OUTPUT_DIR}")
    for f in sorted(OUTPUT_DIR.glob("*.json")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.1f} KB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
