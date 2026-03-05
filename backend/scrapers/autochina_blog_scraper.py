#!/usr/bin/env python3
"""
autochina_blog_scraper.py — Scraper for autochina.blog Li Auto technical reviews (EN).

AutoChina Blog has detailed technical reviews of Li L7/L9/i8/MEGA
with engine specs, battery data, and comparison articles.
"""
from __future__ import annotations

import logging
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

SEED_URLS = [
    "https://autochina.blog/?s=li+auto",
    "https://autochina.blog/?s=lixiang",
    "https://autochina.blog/?s=li+l9",
    "https://autochina.blog/?s=li+l7",
    # Known valuable articles
    "https://autochina.blog/lixiang-l9-chinese-hybrid-suv-tech-innovations/",
    "https://autochina.blog/li-l7-electric-suv-review-premium-chinese-ev/",
    "https://autochina.blog/li-i8-review-autochina-blog/",
    "https://autochina.blog/li-mega-2025-electric-minivan-review-price-range/",
]


class AutoChinaBlogScraper(BaseScraper):
    source_name = "autochina_blog"
    lang = "en"
    delay_range = (2.0, 4.0)
    min_content_length = 500

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        for url in SEED_URLS:
            if '?s=' not in url:
                article_urls.add(url.split('#')[0])
                continue
            log.info("Searching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link or '?' in link:
                        continue
                    # Strip fragments (#respond, #comments)
                    clean = link.split('#')[0]
                    if clean.startswith("https://autochina.blog/") and clean.count('/') >= 4:
                        if any(kw in clean.lower() for kw in ['li-', 'lixiang', 'li_', 'mega']):
                            # Exclude non-Li Auto brands (Geely Galaxy L7, etc.)
                            if 'geely' not in clean.lower() and 'galaxy' not in clean.lower():
                                article_urls.add(clean.rstrip('/') + '/')
                self._sleep()
            except Exception as exc:
                log.warning("Search error: %s — %s", url, exc)

        log.info("Found %d article URLs", len(article_urls))

        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                content_parts = []
                for selector in [".entry-content p", ".post-content p", "article p"]:
                    for el in page.css(selector):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 30:
                            content_parts.append(text)
                    if content_parts:
                        break

                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=30)

                content = "\n\n".join(content_parts)
                if len(content) < 300:
                    continue

                # Clean noise
                content = _clean_noise(content)

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="en", title=title.strip()[:200], content=content,
                )
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


def _clean_noise(text: str) -> str:
    noise = [
        r'Subscribe to our.*$', r'Share this.*$', r'Leave a comment.*$',
        r'Related Posts.*$', r'You may also like.*$', r'©.*$',
        r'Also read:.*$', r'Follow us on.*$',
    ]
    for p in noise:
        text = re.sub(p, '', text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = AutoChinaBlogScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
