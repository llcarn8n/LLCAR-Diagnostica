#!/usr/bin/env python3
"""
dongchedi_scraper.py — Scraper for dongchedi.com (懂车帝, Douyin/ByteDance auto platform).

Extracts: Li L7/L9 specs, user reviews, comparison articles.
Uses StealthyFetcher — site is heavily JS-rendered.
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, stealth_fetch, extract_text_nodes

log = logging.getLogger(__name__)

# Dongchedi series IDs (from URL analysis):
# Li L9: series 5005  /auto/series/5005
# Li L7: series 5233  /auto/series/5233
SEED_URLS = [
    # L9 overview
    ("https://www.dongchedi.com/auto/series/5005", "zh", "理想L9 概览"),
    # L7 overview
    ("https://www.dongchedi.com/auto/series/5233", "zh", "理想L7 概览"),
    # L9 params/specs
    ("https://www.dongchedi.com/auto/params-carIds-x-5005", "zh", "理想L9 参数配置"),
    # L7 params/specs
    ("https://www.dongchedi.com/auto/params-carIds-x-5233", "zh", "理想L7 参数配置"),
    # L9 user reviews (koubei)
    ("https://www.dongchedi.com/auto/series/koubei-5005", "zh", "理想L9 口碑评价"),
    # L7 user reviews
    ("https://www.dongchedi.com/auto/series/koubei-5233", "zh", "理想L7 口碑评价"),
]


class DongchediScraper(BaseScraper):
    source_name = "dongchedi_cn"
    lang = "zh"
    delay_range = (3.0, 6.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Phase 1: scrape seed pages and discover article links
        for url, lang, title_hint in SEED_URLS:
            log.info("Seed: %s", url)
            try:
                page = stealth_fetch(url, timeout=40)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                # Yield the seed page itself
                if not self._already_scraped(url):
                    title = page.css("title::text").get() or title_hint
                    title = re.sub(r"\s*[_\-|—].*$", "", title).strip() or title_hint
                    content = self._extract_content(page)
                    if len(content) > 150:
                        yield ScrapedItem(
                            url=url, source_name=self.source_name,
                            lang=lang, title=title[:200], content=content,
                        )

                # Discover article/review links
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full = link if link.startswith("http") else f"https://www.dongchedi.com{link}"
                    # Article links: /auto/article/NNNN or /motor/article/NNNN
                    if "/article/" in full:
                        article_urls.add(full)
                    # Review detail links
                    if "/koubei/" in full and full != url:
                        article_urls.add(full)

                self._sleep()
            except Exception as exc:
                log.warning("Seed error: %s — %s", url, exc)

        log.info("Discovered %d article/review URLs", len(article_urls))

        # Phase 2: scrape articles
        for url in sorted(article_urls)[:30]:  # limit to avoid overload
            if self._already_scraped(url):
                continue
            try:
                page = stealth_fetch(url, timeout=35)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""
                title = re.sub(r"\s*[_\-|—].*$", "", title).strip()
                content = self._extract_content(page)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="zh", title=title[:200], content=content,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)

    def _extract_content(self, page) -> str:
        sections = []

        # Spec table rows
        for row in page.css("table tr, .param-item, .config-item"):
            cells = [" ".join(c.css("::text").getall()).strip() for c in row.css("th, td, .name, .value")]
            cells = [c for c in cells if c]
            if cells:
                sections.append(" | ".join(cells))

        # Article/review paragraphs
        for el in page.css("article p, .article-content p, .content p, "
                           ".koubei-text, .review-content, .detail-content p"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if len(text) > 20:
                sections.append(text)

        # Headings
        for el in page.css("h1, h2, h3"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if text and len(text) > 3:
                sections.append(f"## {text}")

        if len("\n".join(sections)) < 200:
            sections = extract_text_nodes(page, min_len=15)

        return "\n".join(sections)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = DongchediScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
