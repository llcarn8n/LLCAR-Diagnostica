#!/usr/bin/env python3
"""
complaints_12365auto_scraper.py — Scraper for 12365auto.com (Chinese vehicle complaint platform).

China's official vehicle quality complaint platform (车质网).
Structured complaints with model, issue type, mileage, date.

Li Auto series IDs:
  L7: c-3432  L9: c-3424  L8: c-3425  L6: c-3867
"""
from __future__ import annotations

import logging
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://www.12365auto.com"

# Complaint listing pages for each model (page 1-5)
LISTING_URLS = []
for series_id in ["c-3432", "c-3424", "c-3425", "c-3867"]:
    for page_num in range(1, 6):
        LISTING_URLS.append(f"{BASE}/series/{series_id}-{page_num}-1.shtml")

# Model name mapping from series ID
SERIES_NAMES = {
    "3432": "L7", "3424": "L9", "3425": "L8", "3867": "L6",
}


class Complaints12365AutoScraper(BaseScraper):
    source_name = "12365auto_cn"
    lang = "zh"
    delay_range = (3.0, 5.0)  # respectful rate
    min_content_length = 50   # complaints can be short
    min_relevance = 0.0
    skip_relevance_filter = True  # all complaints are relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        complaint_urls = set()

        for listing_url in LISTING_URLS:
            log.info("Listing: %s", listing_url)
            try:
                page = static_fetch(listing_url, timeout=20)
                if page.status != 200:
                    log.info("Status %d for %s, skipping", page.status, listing_url)
                    continue

                # Find complaint detail links
                for href in page.css("a::attr(href)").getall():
                    if not href:
                        continue
                    # Complaint URLs look like /zlts/20250718/1463194.shtml
                    if "/zlts/" in href:
                        full = href if href.startswith("http") else f"{BASE}{href}"
                        complaint_urls.add(full.split('#')[0])

                self._sleep()
            except Exception as exc:
                log.warning("Listing error: %s — %s", listing_url, exc)

        log.info("Found %d complaint URLs", len(complaint_urls))

        for url in sorted(complaint_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                # Extract complaint content
                content_parts = []

                # Structured info (model, date, mileage, issue type)
                for el in page.css(".complaint-info li, .tsnr li, table td"):
                    text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                    if len(text) > 5:
                        content_parts.append(text)

                # Main complaint text
                for sel in [".complaint-content", ".tsnr-con", ".complaint-detail",
                            ".zlts-content", "article"]:
                    for el in page.css(f"{sel} p, {sel}"):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 10:
                            content_parts.append(text)
                    if len(content_parts) > 3:
                        break

                content = "\n".join(content_parts)
                if len(content) < 30:
                    continue

                # Detect model from URL or title
                model = ""
                for sid, name in SERIES_NAMES.items():
                    if sid in url or name in title:
                        model = name
                        break

                if model:
                    title = f"[{model}] {title}"

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="zh", title=title.strip()[:200], content=content[:3000],
                )
                self._sleep()
            except Exception as exc:
                log.warning("Complaint error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = Complaints12365AutoScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
