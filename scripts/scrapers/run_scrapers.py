#!/usr/bin/env python3
"""
run_scrapers.py — Orchestrator: run all Li Auto scrapers and import results into KB.

Usage:
    python scripts/scrapers/run_scrapers.py [--sources lixiang autohome ru news] [--import]

Steps:
    1. Run selected scrapers → scraped_content table
    2. (Optional) --import: process scraped_content → chunks + embeddings

GPU: NOT required. All scraping is CPU/network-bound.
     GPU 1 is free for the API server during scraping.
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("run_scrapers")

DB_PATH = Path(__file__).resolve().parents[2] / "knowledge-base" / "kb.db"


def run_scraper(name: str) -> int:
    if name == "lixiang":
        from lixiang_com import LixiangComScraper
        return LixiangComScraper(DB_PATH).run()
    elif name == "autohome":
        from autohome_scraper import AutohomeScraper
        return AutohomeScraper(DB_PATH).run()
    elif name == "ru":
        from ru_sources_scraper import RuSourcesScraper
        return RuSourcesScraper(DB_PATH).run()
    elif name == "drom":
        from drom_scraper import DromScraper
        return DromScraper(DB_PATH).run()
    elif name == "drom_reviews":
        from drom_reviews_scraper import DromReviewsScraper
        return DromReviewsScraper(DB_PATH).run()
    elif name == "drive2":
        from drive2_scraper import Drive2Scraper
        return Drive2Scraper(DB_PATH).run()
    elif name == "liforum":
        from liforum_scraper import LiforumScraper
        return LiforumScraper(DB_PATH).run()
    elif name == "dongchedi":
        from dongchedi_scraper import DongchediScraper
        return DongchediScraper(DB_PATH).run()
    elif name == "carnewschina":
        from carnewschina_scraper import CarNewsChinaScraper
        return CarNewsChinaScraper(DB_PATH).run()
    elif name == "wikipedia":
        from wikipedia_scraper import WikipediaScraper
        return WikipediaScraper(DB_PATH).run()
    elif name == "electrek":
        from electrek_scraper import ElectrekScraper
        return ElectrekScraper(DB_PATH).run()
    elif name == "ru_auto":
        from ru_auto_scraper import RuAutoScraper
        return RuAutoScraper(DB_PATH).run()
    elif name == "autoreview":
        from autoreview_scraper import AutoreviewScraper
        return AutoreviewScraper(DB_PATH).run()
    elif name == "news":
        from liautocn_news import LiAutoNewsScaper
        return LiAutoNewsScaper(DB_PATH).run()
    elif name == "getcar":
        from getcar_scraper import GetCarScraper
        return GetCarScraper(DB_PATH).run()
    elif name == "autochina_blog":
        from autochina_blog_scraper import AutoChinaBlogScraper
        return AutoChinaBlogScraper(DB_PATH).run()
    elif name == "ev_forums":
        from ev_forums_scraper import EVForumsScraper
        return EVForumsScraper(DB_PATH).run()
    elif name == "autonews":
        from autonews_scraper import AutonewsScraper
        return AutonewsScraper(DB_PATH).run()
    else:
        log.error("Unknown scraper: %s", name)
        return 0


def show_stats() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT source_name, lang, COUNT(*) n, SUM(imported) imported
            FROM scraped_content
            GROUP BY source_name, lang
            ORDER BY source_name
        """).fetchall()
    if not rows:
        print("No scraped content yet.")
        return
    print("\nScraped content stats:")
    print(f"{'Source':<20} {'Lang':<5} {'Total':>7} {'Imported':>9}")
    print("-" * 45)
    for source, lang, total, imported in rows:
        print(f"{source:<20} {lang:<5} {total:>7} {imported or 0:>9}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Li Auto KB scrapers")
    ALL_SCRAPERS = [
        "lixiang", "autohome", "ru", "drom", "drom_reviews",
        "drive2", "liforum", "dongchedi", "carnewschina",
        "wikipedia", "electrek", "ru_auto", "autoreview", "news",
        "getcar", "autochina_blog", "ev_forums", "autonews",
    ]
    parser.add_argument(
        "--sources", nargs="+",
        choices=ALL_SCRAPERS + ["all"],
        default=["all"],
        help="Scrapers to run",
    )
    parser.add_argument("--stats", action="store_true", help="Show stats and exit")
    parser.add_argument("--import-kb", action="store_true",
                        help="Import scraped_content → KB chunks (runs after scraping)")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    sources = args.sources
    if "all" in sources:
        sources = ALL_SCRAPERS

    total_new = 0
    for name in sources:
        log.info("=" * 50)
        log.info("Running scraper: %s", name)
        try:
            new = run_scraper(name)
            total_new += new
            log.info("Scraper %s: %d new items", name, new)
        except Exception as exc:
            log.error("Scraper %s failed: %s", name, exc, exc_info=True)

    log.info("=" * 50)
    log.info("Total new items scraped: %d", total_new)
    show_stats()

    if args.import_kb:
        log.info("Importing scraped content to KB...")
        import_scraped_to_kb()


def _detect_model(url: str, title: str) -> str:
    """Detect Li Auto model (l7 / l9 / l7_l9) from URL and title."""
    text = (url + " " + title).lower()
    has_l7 = "l7" in text
    has_l9 = "l9" in text
    if has_l7 and has_l9:
        return "l7_l9"
    if has_l7:
        return "l7"
    if has_l9:
        return "l9"
    return "l7_l9"


def import_scraped_to_kb() -> None:
    """
    Import scraped_content rows (imported=0) into KB chunks.

    Each scraped item becomes a chunk in the KB with:
    - source = source_name
    - layer  = 'web_scraped'
    - Translations scheduled via translate_kb.py
    """
    import hashlib
    from datetime import datetime

    # Reset imported=0 for items not yet in chunks (safety re-import)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE scraped_content SET imported=0, chunk_id=NULL
            WHERE imported=1 AND (chunk_id IS NULL OR chunk_id NOT IN (SELECT id FROM chunks))
        """)
        pending = conn.execute(
            "SELECT id, url, source_name, lang, title, content, content_class FROM scraped_content WHERE imported=0"
        ).fetchall()

    log.info("Pending import: %d items", len(pending))
    imported = 0

    with sqlite3.connect(DB_PATH) as conn:
        for row in pending:
            row_id, url, source, lang, title, content = row[:6]
            content_class = row[6] if len(row) > 6 else 'description'
            # Generate chunk_id
            hash_src = f"{source}_{url}_{content[:200]}"
            chunk_hash = hashlib.sha256(hash_src.encode()).hexdigest()[:8]
            chunk_id = f"web_{source}_{lang}_{chunk_hash}"

            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            model = _detect_model(url, title or "")
            now = datetime.now().isoformat()

            # Skip if already exists in chunks
            exists = conn.execute("SELECT 1 FROM chunks WHERE id=?", (chunk_id,)).fetchone()
            if exists:
                conn.execute("UPDATE scraped_content SET imported=1, chunk_id=? WHERE id=?",
                             (chunk_id, row_id))
                continue

            try:
                # Insert chunk (all NOT NULL fields filled)
                # Map content_class to layer: owner_review/troubleshooting stay web_scraped,
                # maintenance → closest layer from content, etc.
                ctype = content_class if content_class and content_class != 'news' else 'description'

                conn.execute("""
                    INSERT OR IGNORE INTO chunks
                    (id, brand, model, source_language, layer, content_type,
                     title, content, source, source_url,
                     page_start, page_end, has_procedures, has_warnings,
                     content_hash, created_at, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (chunk_id, "li_auto", model, lang, "web_scraped", ctype,
                      title or "", content, source, url,
                      0, 0, 0, 0,
                      content_hash, now, now))

                # Insert chunk_content
                conn.execute("""
                    INSERT OR IGNORE INTO chunk_content (chunk_id, lang, title, content)
                    VALUES (?,?,?,?)
                """, (chunk_id, lang, title or "", content))

                # Mark imported
                conn.execute("UPDATE scraped_content SET imported=1, chunk_id=? WHERE id=?",
                             (chunk_id, row_id))
                imported += 1
            except Exception as exc:
                log.warning("Failed to import %s: %s", url, exc)

    log.info("Imported %d new chunks to KB", imported)
    log.info("Next: run build_embeddings.py to embed new chunks")
    log.info("Next: run translate_kb.py to add translations")


if __name__ == "__main__":
    main()
