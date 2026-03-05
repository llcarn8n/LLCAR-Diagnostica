#!/usr/bin/env python3
"""
build_system_manifest.py — Генератор единого манифеста system-components.json

5 диагностических групп:
  electric   = ev + battery
  fuel       = engine + drivetrain
  suspension = chassis + brakes
  cabin      = body + interior + hvac
  tech       = infotainment + adas + sensors + lighting

Для каждого компонента:
  - mesh name, glossary_id, displayName, subsystem
  - DTC коды (если есть)
  - KB чанки (chunk_id, title) из chunk_glossary
  - Фото (image_path, caption) из chunk_images

Входные файлы:
  - frontend/data/architecture/layer-definitions.json
  - frontend/data/architecture/li7-component-map-v2.json
  - frontend/data/architecture/li9-component-map-v2.json
  - frontend/data/architecture/kb-layer-bridge.json
  - knowledge-base/kb.db (для чанков и фото)

Выходной файл:
  - frontend/data/architecture/system-components.json
"""

import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ARCH_DIR = os.path.join(PROJECT_ROOT, "frontend", "data", "architecture")
KB_DB = os.path.join(PROJECT_ROOT, "knowledge-base", "kb.db")

LAYER_DEFS = os.path.join(ARCH_DIR, "layer-definitions.json")
LI7_MAP = os.path.join(ARCH_DIR, "li7-component-map-v2.json")
LI9_MAP = os.path.join(ARCH_DIR, "li9-component-map-v2.json")
KB_BRIDGE = os.path.join(ARCH_DIR, "kb-layer-bridge.json")
OUTPUT = os.path.join(ARCH_DIR, "system-components.json")

# ─── 5 диагностических групп ────────────────────────────
GROUP_DEFS = {
    "electric": {
        "order": 1,
        "color": "#66BB6A",
        "icon": "battery-charging",
        "label": {
            "en": "Electric System",
            "ru": "Электрическая система",
            "zh": "电气系统",
            "ar": "النظام الكهربائي",
            "es": "Sistema eléctrico",
        },
        "description": {
            "en": "HV battery, BMS, charging, inverters, electric motors, 12V system, wiring",
            "ru": "ВВ батарея, БМС, зарядка, инверторы, электромоторы, 12В система, проводка",
        },
        "viz_layers": ["ev"],
        "kb_layers": ["ev", "battery"],
    },
    "fuel": {
        "order": 2,
        "color": "#FF7043",
        "icon": "engine",
        "label": {
            "en": "Engine & Drivetrain",
            "ru": "Двигатель и трансмиссия",
            "zh": "发动机与传动系统",
            "ar": "المحرك ونظام الدفع",
            "es": "Motor y tren motriz",
        },
        "description": {
            "en": "ICE, fuel system, exhaust, transmission, clutch, driveshaft, differential",
            "ru": "ДВС, топливная система, выхлоп, КПП, сцепление, карданный вал, дифференциал",
        },
        "viz_layers": ["engine", "drivetrain"],
        "kb_layers": ["engine", "drivetrain"],
    },
    "suspension": {
        "order": 3,
        "color": "#EF5350",
        "icon": "steering-wheel",
        "label": {
            "en": "Chassis & Braking",
            "ru": "Подвеска и тормоза",
            "zh": "底盘与制动",
            "ar": "الهيكل والفرامل",
            "es": "Chasis y frenos",
        },
        "description": {
            "en": "Suspension, steering, brakes, ABS/ESC, wheels, tires",
            "ru": "Подвеска, рулевое, тормоза, АБС/ESC, колёса, шины",
        },
        "viz_layers": ["brakes"],
        "kb_layers": ["chassis", "brakes"],
    },
    "cabin": {
        "order": 4,
        "color": "#4FC3F7",
        "icon": "car-body",
        "label": {
            "en": "Body & Cabin",
            "ru": "Кузов и салон",
            "zh": "车身与座舱",
            "ar": "الهيكل والمقصورة",
            "es": "Carrocería y habitáculo",
        },
        "description": {
            "en": "Body panels, doors, glazing, interior, seats, HVAC, thermal management",
            "ru": "Панели кузова, двери, остекление, салон, сиденья, климат, терморегулирование",
        },
        "viz_layers": ["body", "interior", "hvac"],
        "kb_layers": ["body", "interior", "hvac"],
    },
    "tech": {
        "order": 5,
        "color": "#FFA726",
        "icon": "radar",
        "label": {
            "en": "Tech & Sensors",
            "ru": "Электроника и датчики",
            "zh": "科技与传感器",
            "ar": "التقنية والمستشعرات",
            "es": "Tecnología y sensores",
        },
        "description": {
            "en": "ADAS, cameras, radars, LiDAR, infotainment, lighting electronics, displays",
            "ru": "ADAS, камеры, радары, LiDAR, мультимедиа, электроника освещения, дисплеи",
        },
        "viz_layers": ["sensors"],
        "kb_layers": ["infotainment", "adas", "sensors", "lighting"],
    },
}

# Маппинг 8 viz-слоёв → 5 групп
VIZ_TO_GROUP = {
    "ev": "electric",
    "engine": "fuel",
    "drivetrain": "fuel",
    "brakes": "suspension",
    "body": "cabin",
    "interior": "cabin",
    "hvac": "cabin",
    "sensors": "tech",
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def query_kb(db_path):
    """Получаем из KB: чанки по glossary_id, фото по chunk_id, статистику."""
    result = {
        "available": False,
        "glossary_chunks": defaultdict(list),     # glossary_id -> [{chunk_id, title, layer}]
        "chunk_images": defaultdict(list),         # chunk_id -> [{image_path, caption}]
        "chunks_by_layer": {},
        "total_images": 0,
    }
    if not os.path.exists(db_path):
        return result

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # chunk_glossary -> привязка glossary_id к чанкам
        cur.execute("""
            SELECT cg.glossary_id, cg.chunk_id, c.title, c.layer, c.model
            FROM chunk_glossary cg
            JOIN chunks c ON c.id = cg.chunk_id
            WHERE cg.glossary_id LIKE '%@%'
        """)
        for row in cur.fetchall():
            result["glossary_chunks"][row["glossary_id"]].append({
                "chunk_id": row["chunk_id"],
                "title": row["title"],
                "layer": row["layer"],
                "model": row["model"],
            })

        # chunk_images
        cur.execute("SELECT chunk_id, image_path, caption FROM chunk_images")
        for row in cur.fetchall():
            result["chunk_images"][row["chunk_id"]].append({
                "image_path": row["image_path"],
                "caption": row["caption"],
            })
        result["total_images"] = sum(len(v) for v in result["chunk_images"].values())

        # Статистика чанков по layer
        cur.execute("SELECT layer, COUNT(*) as cnt FROM chunks GROUP BY layer")
        for row in cur.fetchall():
            result["chunks_by_layer"][row["layer"]] = row["cnt"]

        result["available"] = True
        conn.close()
    except Exception as e:
        print(f"  [WARN] KB error: {e}")

    return result


def build_manifest():
    print("=== build_system_manifest.py (5-group) ===")
    print()

    # 1. Загрузка
    print("[1/5] Загрузка входных файлов...")
    layer_defs = load_json(LAYER_DEFS)
    li7_map = load_json(LI7_MAP)
    li9_map = load_json(LI9_MAP)
    kb_bridge = load_json(KB_BRIDGE)
    print(f"  layer-definitions: {len(layer_defs['layers'])} viz-слоёв")
    print(f"  li7: {li7_map['statistics']['total_meshes']} мешей")
    print(f"  li9: {li9_map['statistics']['total_meshes']} мешей")
    print()

    # 2. KB данные
    print("[2/5] Чтение KB (чанки, фото, glossary)...")
    kb = query_kb(KB_DB)
    if kb["available"]:
        total_chunks = sum(kb["chunks_by_layer"].values())
        print(f"  KB: {total_chunks} чанков, {len(kb['glossary_chunks'])} glossary привязок, {kb['total_images']} фото")
    else:
        print("  KB недоступна")
    print()

    # 3. Сборка по 5 группам
    print("[3/5] Группировка компонентов в 5 групп...")
    groups_data = {}
    glossary_ids_all = set()
    total_l7 = 0
    total_l9 = 0
    total_images_linked = 0
    total_chunks_linked = 0

    for group_id, gdef in GROUP_DEFS.items():
        group_entry = {
            "order": gdef["order"],
            "color": gdef["color"],
            "icon": gdef["icon"],
            "label": gdef["label"],
            "description": gdef["description"],
            "viz_layers": gdef["viz_layers"],
            "kb_layers": gdef["kb_layers"],
            "components": {"l7": [], "l9": []},
            "kb_stats": {"chunks": 0, "images": 0},
        }

        # Считаем KB-статистику группы
        if kb["available"]:
            for kbl in gdef["kb_layers"]:
                group_entry["kb_stats"]["chunks"] += kb["chunks_by_layer"].get(kbl, 0)

        # Собираем меши из viz-слоёв, принадлежащих этой группе
        viz_layers_for_group = gdef["viz_layers"]

        # L7
        for mesh_name, comp in li7_map.get("components", {}).items():
            if comp.get("layer") in viz_layers_for_group:
                entry = _build_component_entry(mesh_name, comp, kb)
                group_entry["components"]["l7"].append(entry)
                if entry.get("glossary_id"):
                    glossary_ids_all.add(entry["glossary_id"])
                total_images_linked += len(entry.get("images", []))
                total_chunks_linked += len(entry.get("kb_refs", []))

        # L9
        for mesh_name, comp in li9_map.get("components", {}).items():
            if comp.get("layer") in viz_layers_for_group:
                entry = _build_component_entry(mesh_name, comp, kb)
                group_entry["components"]["l9"].append(entry)
                if entry.get("glossary_id"):
                    glossary_ids_all.add(entry["glossary_id"])
                total_images_linked += len(entry.get("images", []))
                total_chunks_linked += len(entry.get("kb_refs", []))

        l7_count = len(group_entry["components"]["l7"])
        l9_count = len(group_entry["components"]["l9"])
        total_l7 += l7_count
        total_l9 += l9_count

        # Подсчёт фото в группе
        img_count = sum(
            len(c.get("images", []))
            for vehicle in ["l7", "l9"]
            for c in group_entry["components"][vehicle]
        )
        group_entry["kb_stats"]["images"] = img_count

        groups_data[group_id] = group_entry
        print(f"  {group_id}: L7={l7_count}, L9={l9_count}, KB chunks={group_entry['kb_stats']['chunks']}, images={img_count}")

    print()

    # 4. Валидация
    print("[4/5] Валидация...")
    warnings = []
    unmapped_l7 = [m for m, c in li7_map.get("components", {}).items() if c.get("layer") not in VIZ_TO_GROUP]
    unmapped_l9 = [m for m, c in li9_map.get("components", {}).items() if c.get("layer") not in VIZ_TO_GROUP]
    if unmapped_l7:
        warnings.append(f"L7: {len(unmapped_l7)} мешей вне групп (layer not in viz_to_group)")
    if unmapped_l9:
        warnings.append(f"L9: {len(unmapped_l9)} мешей вне групп")
    no_glossary_l7 = sum(1 for g in groups_data.values() for c in g["components"]["l7"] if not c.get("glossary_id"))
    no_glossary_l9 = sum(1 for g in groups_data.values() for c in g["components"]["l9"] if not c.get("glossary_id"))
    if no_glossary_l7:
        warnings.append(f"L7: {no_glossary_l7} компонентов без glossary_id")
    if no_glossary_l9:
        warnings.append(f"L9: {no_glossary_l9} компонентов без glossary_id")
    for w in warnings:
        print(f"  [WARN] {w}")
    if not warnings:
        print("  OK")
    print()

    # 5. Запись
    print("[5/5] Генерация system-components.json...")
    manifest = {
        "meta": {
            "version": "3.0",
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "vehicles": ["l7", "l9"],
            "group_count": 5,
            "description": "5-group diagnostic manifest: electric, fuel, suspension, cabin, tech",
        },
        "kb_layer_bridge": kb_bridge["mapping"],
        "viz_to_group": VIZ_TO_GROUP,
        "groups": groups_data,
        "statistics": {
            "total_meshes_l7": total_l7,
            "total_meshes_l9": total_l9,
            "total_glossary_terms": len(glossary_ids_all),
            "total_images_linked": total_images_linked,
            "total_kb_refs_linked": total_chunks_linked,
            "kb_layers": len(kb_bridge["mapping"]),
            "groups": len(groups_data),
        },
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"  {OUTPUT}")
    print(f"  Размер: {size_kb:.1f} KB")
    print()

    # Report
    print("=" * 50)
    print("ОТЧЁТ")
    print("=" * 50)
    print(f"  Групп:              {len(groups_data)}")
    print(f"  L7 meshes:          {total_l7}")
    print(f"  L9 meshes:          {total_l9}")
    print(f"  Glossary IDs:       {len(glossary_ids_all)}")
    print(f"  KB refs привязано:  {total_chunks_linked}")
    print(f"  Фото привязано:     {total_images_linked}")
    print(f"  Предупреждений:     {len(warnings)}")

    return len(warnings) == 0


def _build_component_entry(mesh_name, comp, kb):
    """Собирает единую запись компонента с KB-данными и фото."""
    glossary_id = comp.get("glossary_id", "")
    entry = {
        "mesh": mesh_name,
        "glossary_id": glossary_id,
        "displayName": comp.get("displayName", mesh_name),
        "viz_layer": comp.get("layer", ""),
    }

    if comp.get("dtcCodes"):
        entry["dtcCodes"] = comp["dtcCodes"]

    if comp.get("specs"):
        entry["specs"] = comp["specs"]

    # KB привязки через glossary_id
    if glossary_id and kb["available"]:
        chunks = kb["glossary_chunks"].get(glossary_id, [])
        if chunks:
            # Берём уникальные чанки (дедупликация по chunk_id)
            seen = set()
            unique_refs = []
            for ch in chunks:
                if ch["chunk_id"] not in seen:
                    seen.add(ch["chunk_id"])
                    unique_refs.append({
                        "chunk_id": ch["chunk_id"],
                        "title": ch["title"],
                    })
            entry["kb_refs"] = unique_refs[:10]  # макс 10 на компонент

            # Фото из привязанных чанков
            images = []
            seen_img = set()
            for ch in chunks:
                for img in kb["chunk_images"].get(ch["chunk_id"], []):
                    img_path = img["image_path"]
                    if img_path not in seen_img:
                        seen_img.add(img_path)
                        images.append({
                            "path": img_path,
                            "caption": (img["caption"] or "")[:120],
                        })
            if images:
                entry["images"] = images[:5]  # макс 5 фото на компонент

    return entry


if __name__ == "__main__":
    success = build_manifest()
    sys.exit(0 if success else 1)
