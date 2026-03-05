#!/usr/bin/env python3
"""
ev_forums_scraper.py — Scraper for English EV forums with Li Auto content.

Sources:
- chinacarforums.com — dedicated Li Auto section
- myevdiscussion.com — EV forum with Li Auto threads
- insideevs.com — articles about Li Auto diagnostics/problems
- topelectricsuv.com — detailed Li Auto reviews
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

# Forum listing pages and known article URLs
SOURCES = [
    # ChinaCarForums — dedicated Li Auto section
    {
        'listing': [
            "https://www.chinacarforums.com/forums/li-auto.182/",
            "https://www.chinacarforums.com/forums/li-auto.182/page-2",
        ],
        'link_pattern': r'/threads/.*\.\d+/?$',
        'base': "https://www.chinacarforums.com",
        'source_name': 'chinacarforums',
    },
    # MyEVDiscussion
    {
        'listing': [
            "https://myevdiscussion.com/search/?q=li+auto",
        ],
        'link_pattern': r'/threads/.*\.\d+/?$',
        'base': "https://myevdiscussion.com",
        'source_name': 'myevdiscussion',
    },
    # InsideEVs — specific Li Auto articles
    {
        'direct': [
            "https://insideevs.com/news/775394/li-auto-l9-russia-erev/",
        ],
        'listing': [
            "https://insideevs.com/tag/li-auto/",
        ],
        'link_pattern': r'/news/\d+/',
        'base': "https://insideevs.com",
        'source_name': 'insideevs',
        'filter_keywords': ['li auto', 'li l7', 'li l9', 'lixiang'],
    },
    # TopElectricSUV
    {
        'direct': [
            "https://topelectricsuv.com/first-look-review/li-auto-l9-hybrid/",
        ],
        'listing': [
            "https://topelectricsuv.com/?s=li+auto",
        ],
        'link_pattern': r'/[-\w]+/li[-\w]*/',
        'base': "https://topelectricsuv.com",
        'source_name': 'topelectricsuv',
    },
]


class EVForumsScraper(BaseScraper):
    source_name = "ev_forums"
    lang = "en"
    delay_range = (2.0, 5.0)
    min_content_length = 300

    def scrape(self) -> Iterator[ScrapedItem]:
        for source in SOURCES:
            src_name = source.get('source_name', 'ev_forums')
            log.info("=== Source: %s ===", src_name)

            article_urls = set()

            # Direct URLs
            for url in source.get('direct', []):
                article_urls.add(url)

            # Listing pages
            base = source.get('base', '')
            pattern = source.get('link_pattern', '')
            filter_kw = source.get('filter_keywords', [])

            for listing_url in source.get('listing', []):
                log.info("Listing: %s", listing_url)
                try:
                    page = static_fetch(listing_url, timeout=20)
                    if page.status != 200:
                        log.warning("HTTP %d for %s", page.status, listing_url)
                        continue
                    for link in page.css("a::attr(href)").getall():
                        if not link:
                            continue
                        full = link if link.startswith('http') else f"{base}{link}"
                        if pattern and re.search(pattern, full):
                            if filter_kw:
                                link_lower = full.lower()
                                if any(kw in link_lower for kw in filter_kw):
                                    article_urls.add(full)
                            else:
                                article_urls.add(full)
                    self._sleep()
                except Exception as exc:
                    log.warning("Listing error: %s — %s", listing_url, exc)

            log.info("Found %d URLs from %s", len(article_urls), src_name)

            # Scrape articles
            for url in sorted(article_urls):
                if self._already_scraped(url):
                    continue
                try:
                    page = static_fetch(url, timeout=20)
                    if page.status != 200:
                        continue

                    title = page.css("h1::text").get() or page.css("title::text").get() or ""

                    # Try multiple content selectors
                    content_parts = []
                    for selector in [
                        "article p", ".entry-content p", ".post-content p",
                        ".message-body p", ".bbWrapper p",  # forum selectors
                        ".article-body p", ".content p",
                    ]:
                        for el in page.css(selector):
                            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                            if len(text) > 25:
                                content_parts.append(text)
                        if content_parts:
                            break

                    if not content_parts:
                        content_parts = extract_text_nodes(page, min_len=25)

                    content = "\n\n".join(content_parts)
                    if len(content) < 200:
                        continue

                    # Clean common noise
                    content = _clean(content)

                    yield ScrapedItem(
                        url=url, source_name=src_name,
                        lang="en", title=title.strip()[:200], content=content,
                    )
                except Exception as exc:
                    log.warning("Article error: %s — %s", url, exc)


def _clean(text: str) -> str:
    noise = [
        r'Sign up.*$', r'Log in.*$', r'Register.*$',
        r'Subscribe.*newsletter.*$', r'Share this.*$',
        r'Related articles.*$', r'©.*$', r'Cookie.*$',
        r'Click to expand.*$', r'You must log in.*$',
    ]
    for p in noise:
        text = re.sub(p, '', text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = EVForumsScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
