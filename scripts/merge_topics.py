#!/usr/bin/env python3
"""
merge_topics.py — Merge and deduplicate topics from 4 analysis agents.

Input: 4 JSON files (topics_from_articles_ru, topics_from_telegram,
       topics_from_articles_en, topics_from_new_scraped)
Output:
  - research/UNIFIED_TOPICS.md — for human review
  - research/unified_topics.json — for KB import
"""
import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict

RESEARCH = Path(__file__).resolve().parents[1] / "research"

FILES = [
    ("topics_from_articles_ru.json", "ru_articles"),
    ("topics_from_telegram.json", "telegram"),
    ("topics_from_articles_en.json", "en_articles"),
    ("topics_from_new_scraped.json", "new_scraped"),
]

# Similarity keywords for dedup — topics sharing these core concepts are candidates
DEDUP_GROUPS = {
    "air_suspension": ["пневмоподвеск", "air suspension", "amk", "wabco", "компрессор пневмо", "suspension failure", "suspension break"],
    "brakes": ["тормоз", "brake", "суппорт", "caliper", "zf", "spongy", "визг тормоз", "brake pad", "brake noise"],
    "multimedia_ota": ["мультимедиа", "multimedia", "ota", "зависан", "freeze", "infotainment", "прошивк", "firmware"],
    "timing_chain": ["цепь грм", "timing chain", "1.5t", "масложор", "oil consumption", "engine failure"],
    "door_handle": ["дверн", "door handle", "ручк двер", "handle freez"],
    "mega_recall": ["mega", "мега", "recall", "отзыв.*mega", "пожар.*mega", "fire.*mega", "11.?411", "coolant corrosion"],
    "lower_control_arm": ["рычаг", "control arm", "шаровая", "ball joint", "стук подвеск", "front wheel noise"],
    "air_filter": ["воздушный фильтр", "air filter", "фильтр пневмо", "filter clog", "засор"],
    "battery_supplier": ["catl", "sunwoda", "батарея поставщик", "battery supplier", "аккумулятор.*поставщик"],
    "russification": ["русификац", "russificat", "локализац", "localizat", "carmods", "интерфейс.*язык"],
    "maintenance": ["то-1", "to-1", "обслуживан", "maintenance", "масло.*двс", "engine oil", "регламент то", "service schedule"],
    "sales_market": ["продаж", "sales", "рынок", "market", "deliveries", "price war", "ценовая война"],
    "adas_autopilot": ["adas", "autopilot", "noa", "phantom brak", "автопилот"],
    "lidar": ["lidar", "лидар", "hesai", "at128"],
    "charging_800v": ["5c заряд", "5c charg", "800v", "суперчардж", "supercharg"],
    "steering": ["рулевая колонк", "steering column", "eps", "руль.*стук"],
    "wptc_heater": ["wptc", "отопител пневмо", "heater failure", "ptc нагреватель"],
    "range_erev": ["запас хода.*erev", "erev.*расход", "erev.*range"],
    "i_series_bev": ["bev transition", "серия i.*bev", "i8.*bev", "i6.*bev"],
    "l9_2026_update": ["livis 2026", "l9 2026", "m100 chip", "emb brake", "steer-by-wire"],
    "ai_strategy": ["livis glass", "humanoid robot", "nexus robot", "mind gpt", "embodied ai"],
    "service_network": ["сервис.*сеть", "service network", "дилер.*li", "сто.*lixiang", "запчаст.*li"],
    "cdc_damper": ["cdc", "амортизатор cdc", "damper.*cdc"],
    "winter_issues": ["зимн.*эксплуат", "winter.*operation", "мороз.*проблем", "-30.*проблем", "-40"],
    "nfc_key": ["nfc", "ключ.*карт", "key card", "цифровой ключ"],
    "spontaneous_combustion": ["самовозгоран", "spontaneous combust", "пожар", "fire incident", "thermal runaway"],
    "global_expansion": ["экспорт", "export", "global expansion", "europe", "middle east", "казахстан", "kazakhstan"],
    "tax_power": ["налог", "tax", "транспортный налог", "vehicle tax", "nominal.*power"],
}


def load_topics():
    """Load all topic files."""
    all_topics = []
    for fname, source_tag in FILES:
        path = RESEARCH / fname
        if not path.exists():
            print(f"WARNING: {path} not found, skipping")
            continue
        with open(path, "r", encoding="utf-8") as f:
            topics = json.load(f)
        for t in topics:
            t["_source_file"] = source_tag
        all_topics.extend(topics)
        print(f"Loaded {len(topics)} topics from {fname}")
    return all_topics


def classify_topic(topic):
    """Classify topic into dedup groups based on text content.
    Returns list of (group, score) sorted by score desc.
    Score = number of keyword matches in that group.
    """
    # Use title + summary for classification (not key_facts — too noisy)
    text = " ".join([
        topic.get("title_ru", ""),
        topic.get("title_en", ""),
        topic.get("summary_ru", "")[:300],
        topic.get("summary_en", "")[:300],
    ]).lower()

    scores = {}
    for group, keywords in DEDUP_GROUPS.items():
        score = 0
        for kw in keywords:
            if re.search(kw, text, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[group] = score

    # Return only the BEST group (highest score), or top-2 if tied
    if not scores:
        return []
    max_score = max(scores.values())
    best = [g for g, s in scores.items() if s == max_score]
    return best[:1]  # Only assign to ONE group


def merge_topics(topics_list):
    """Group topics by dedup group and merge."""
    # Classify each topic
    for t in topics_list:
        t["_groups"] = classify_topic(t)

    # Build group -> topics mapping
    group_map = defaultdict(list)
    ungrouped = []

    for t in topics_list:
        if t["_groups"]:
            for g in t["_groups"]:
                group_map[g].append(t)
        else:
            ungrouped.append(t)

    # For each group, pick the best topic and merge others' data into it
    merged = []
    used_ids = set()

    for group_name, group_topics in sorted(group_map.items()):
        # Skip topics already used in another group
        candidates = [t for t in group_topics if t["topic_id"] not in used_ids]
        if not candidates:
            continue

        # Pick the one with most key_facts as primary
        candidates.sort(key=lambda t: len(t.get("key_facts", [])), reverse=True)
        primary = candidates[0]

        # Merge data from others
        all_facts = list(primary.get("key_facts", []))
        all_sources = list(primary.get("source_urls", []))
        all_articles = list(primary.get("source_articles", []))
        all_models = set(primary.get("models", []))
        all_systems = set(primary.get("systems", []))
        contributing_files = {primary["_source_file"]}

        for other in candidates[1:]:
            # Add unique facts
            for fact in other.get("key_facts", []):
                if fact not in all_facts and not any(
                    _similar(fact, f) for f in all_facts
                ):
                    all_facts.append(fact)
            # Add unique sources
            for url in other.get("source_urls", []):
                if url not in all_sources:
                    all_sources.append(url)
            for aid in other.get("source_articles", []):
                if aid not in all_articles:
                    all_articles.append(aid)
            all_models.update(other.get("models", []))
            all_systems.update(other.get("systems", []))
            contributing_files.add(other["_source_file"])

        # Build merged topic
        merged_topic = {
            "topic_id": f"unified_{group_name}",
            "dedup_group": group_name,
            "title_ru": primary.get("title_ru", ""),
            "title_en": primary.get("title_en", ""),
            "category": primary.get("category", "troubleshooting"),
            "models": sorted(all_models),
            "systems": sorted(all_systems),
            "layer": primary.get("layer", ""),
            "season": primary.get("season", "all"),
            "summary_ru": primary.get("summary_ru", ""),
            "summary_en": primary.get("summary_en", ""),
            "key_facts": all_facts[:15],  # cap at 15
            "repair_cost_range": primary.get("repair_cost_range", ""),
            "source_urls": all_sources,
            "source_articles": all_articles,
            "contributing_sources": sorted(contributing_files),
            "merged_from": [t["topic_id"] for t in candidates],
            "confidence": _calc_confidence(len(contributing_files), len(all_sources)),
        }

        # Use longer summary if available from other source
        for other in candidates[1:]:
            if len(other.get("summary_ru", "")) > len(merged_topic["summary_ru"]):
                merged_topic["summary_ru"] = other["summary_ru"]
            if len(other.get("summary_en", "")) > len(merged_topic["summary_en"]):
                merged_topic["summary_en"] = other["summary_en"]

        merged.append(merged_topic)
        for t in candidates:
            used_ids.add(t["topic_id"])

    # Add ungrouped topics that weren't used
    for t in ungrouped:
        if t["topic_id"] in used_ids:
            continue
        merged.append({
            "topic_id": f"unified_unique_{t['topic_id']}",
            "dedup_group": "unique",
            "title_ru": t.get("title_ru", ""),
            "title_en": t.get("title_en", ""),
            "category": t.get("category", ""),
            "models": t.get("models", []),
            "systems": t.get("systems", []),
            "layer": t.get("layer", ""),
            "season": t.get("season", "all"),
            "summary_ru": t.get("summary_ru", ""),
            "summary_en": t.get("summary_en", ""),
            "key_facts": t.get("key_facts", [])[:15],
            "repair_cost_range": t.get("repair_cost_range", ""),
            "source_urls": t.get("source_urls", []),
            "source_articles": t.get("source_articles", []),
            "contributing_sources": [t["_source_file"]],
            "merged_from": [t["topic_id"]],
            "confidence": "MEDIUM" if len(t.get("source_urls", [])) >= 2 else "LOW",
        })
        used_ids.add(t["topic_id"])

    # Also add remaining grouped topics not yet used
    for t in topics_list:
        if t["topic_id"] not in used_ids:
            merged.append({
                "topic_id": f"unified_extra_{t['topic_id']}",
                "dedup_group": "extra",
                "title_ru": t.get("title_ru", ""),
                "title_en": t.get("title_en", ""),
                "category": t.get("category", ""),
                "models": t.get("models", []),
                "systems": t.get("systems", []),
                "layer": t.get("layer", ""),
                "season": t.get("season", "all"),
                "summary_ru": t.get("summary_ru", ""),
                "summary_en": t.get("summary_en", ""),
                "key_facts": t.get("key_facts", [])[:15],
                "repair_cost_range": t.get("repair_cost_range", ""),
                "source_urls": t.get("source_urls", []),
                "source_articles": t.get("source_articles", []),
                "contributing_sources": [t["_source_file"]],
                "merged_from": [t["topic_id"]],
                "confidence": "MEDIUM",
            })

    return merged


def _similar(a, b):
    """Check if two facts are roughly the same."""
    a_clean = re.sub(r'[^\w\s]', '', a.lower())[:60]
    b_clean = re.sub(r'[^\w\s]', '', b.lower())[:60]
    # Simple overlap check
    words_a = set(a_clean.split())
    words_b = set(b_clean.split())
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b) / max(len(words_a), len(words_b))
    return overlap > 0.6


def _calc_confidence(n_sources, n_urls):
    if n_sources >= 3 and n_urls >= 4:
        return "CONFIRMED"
    if n_sources >= 2 and n_urls >= 3:
        return "HIGH"
    if n_sources >= 2 or n_urls >= 2:
        return "MEDIUM"
    return "LOW"


def generate_md(merged):
    """Generate UNIFIED_TOPICS.md for review."""
    lines = [
        "# Unified Topic Catalog — Li Auto KB Enrichment",
        "",
        f"**Total: {len(merged)} unified topics** (merged from 120 raw topics across 4 sources)",
        "",
        "## Sources",
        "| Source | File | Raw Topics |",
        "|--------|------|------------|",
        "| RU articles (autonews, drom, getcar, autoreview) | topics_from_articles_ru.json | 35 |",
        "| Telegram (@lixiangautorussia) | topics_from_telegram.json | 25 |",
        "| EN articles (cnevpost, carnewschina, carscoops) | topics_from_articles_en.json | 25 |",
        "| New scraped (kursiv, autoplt, 110km, lixiang_sto) | topics_from_new_scraped.json | 35 |",
        "",
        "## Confidence Distribution",
    ]

    conf_counts = defaultdict(int)
    for t in merged:
        conf_counts[t["confidence"]] += 1
    for conf in ["CONFIRMED", "HIGH", "MEDIUM", "LOW"]:
        if conf in conf_counts:
            lines.append(f"- **{conf}**: {conf_counts[conf]}")

    # Category distribution
    cat_counts = defaultdict(int)
    for t in merged:
        cat_counts[t["category"]] += 1
    lines.extend(["", "## By Category"])
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{cat}**: {cnt}")

    # Main table
    lines.extend([
        "",
        "---",
        "",
        "## All Topics",
        "",
    ])

    # Group by category
    by_cat = defaultdict(list)
    for t in merged:
        by_cat[t["category"]].append(t)

    cat_order = ["troubleshooting", "safety", "owner_experience", "maintenance",
                 "technology", "market", "specs", "comparison"]
    for cat in cat_order:
        if cat not in by_cat:
            continue
        lines.append(f"### {cat.upper()}")
        lines.append("")

        for t in by_cat[cat]:
            lines.append(f"#### {t['topic_id']}: {t['title_ru']}")
            lines.append(f"*{t['title_en']}*")
            lines.append("")
            lines.append(f"- **Confidence**: {t['confidence']}")
            lines.append(f"- **Models**: {', '.join(t['models'])}")
            lines.append(f"- **Systems**: {', '.join(t['systems'])}")
            lines.append(f"- **Layer**: {t['layer']}")
            lines.append(f"- **Season**: {t['season']}")
            if t.get("repair_cost_range"):
                lines.append(f"- **Cost**: {t['repair_cost_range']}")
            lines.append(f"- **Sources**: {len(t['source_urls'])} URLs from {', '.join(t['contributing_sources'])}")
            lines.append(f"- **Merged from**: {', '.join(t['merged_from'])}")
            lines.append("")
            lines.append(f"**RU**: {t['summary_ru'][:500]}")
            lines.append("")
            lines.append(f"**EN**: {t['summary_en'][:500]}")
            lines.append("")
            if t["key_facts"]:
                lines.append("**Key facts:**")
                for fact in t["key_facts"][:10]:
                    lines.append(f"- {fact}")
            lines.append("")
            if t["source_urls"]:
                lines.append("**Sources:**")
                for url in t["source_urls"][:8]:
                    lines.append(f"- {url}")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Remaining categories not in order
    for cat in sorted(by_cat.keys()):
        if cat in cat_order:
            continue
        lines.append(f"### {cat.upper()}")
        lines.append("")
        for t in by_cat[cat]:
            lines.append(f"#### {t['topic_id']}: {t['title_ru']}")
            lines.append(f"*{t['title_en']}*")
            lines.append("")
            lines.append(f"- **Confidence**: {t['confidence']}")
            lines.append(f"- **Models**: {', '.join(t['models'])}")
            lines.append(f"- **Sources**: {len(t['source_urls'])} URLs from {', '.join(t['contributing_sources'])}")
            lines.append(f"- **Merged from**: {', '.join(t['merged_from'])}")
            lines.append("")
            lines.append(f"**RU**: {t['summary_ru'][:300]}")
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main():
    print("Loading topics...")
    all_topics = load_topics()
    print(f"Total raw topics: {len(all_topics)}")

    print("\nMerging and deduplicating...")
    merged = merge_topics(all_topics)
    print(f"After merge: {len(merged)} unified topics")

    # Sort by confidence then category
    conf_order = {"CONFIRMED": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    merged.sort(key=lambda t: (conf_order.get(t["confidence"], 9), t["category"], t["topic_id"]))

    # Save JSON
    json_path = RESEARCH / "unified_topics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(merged)} topics to {json_path}")

    # Save MD
    md_path = RESEARCH / "UNIFIED_TOPICS.md"
    md_content = generate_md(merged)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved review MD to {md_path}")

    # Stats
    print("\n=== STATS ===")
    conf_counts = defaultdict(int)
    cat_counts = defaultdict(int)
    for t in merged:
        conf_counts[t["confidence"]] += 1
        cat_counts[t["category"]] += 1

    print("Confidence:")
    for c in ["CONFIRMED", "HIGH", "MEDIUM", "LOW"]:
        print(f"  {c}: {conf_counts.get(c, 0)}")

    print("Categories:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")


if __name__ == "__main__":
    main()
