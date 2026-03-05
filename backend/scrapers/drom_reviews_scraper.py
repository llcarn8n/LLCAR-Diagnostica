#!/usr/bin/env python3
"""
drom_reviews_scraper.py — Scraper for drom.ru Li L7/L9 structured owner reviews.

Extracts:
- Individual owner reviews with ratings, pros/cons
- "5 копеек" problem reports (breakdowns, issues)
- Structured metadata: mileage, year, rating, problem category
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

# Review listing pages
REVIEW_LISTING_PAGES = [
    # L9 reviews
    ("https://www.drom.ru/reviews/li/l9/", "ru", "Li L9 отзывы"),
    ("https://www.drom.ru/reviews/li/l9/page2/", "ru", "Li L9 отзывы стр.2"),
    ("https://www.drom.ru/reviews/li/l9/page3/", "ru", "Li L9 отзывы стр.3"),
    ("https://www.drom.ru/reviews/li/l9/page4/", "ru", "Li L9 отзывы стр.4"),
    ("https://www.drom.ru/reviews/li/l9/page5/", "ru", "Li L9 отзывы стр.5"),
    # L7 reviews
    ("https://www.drom.ru/reviews/li/l7/", "ru", "Li L7 отзывы"),
    ("https://www.drom.ru/reviews/li/l7/page2/", "ru", "Li L7 отзывы стр.2"),
    ("https://www.drom.ru/reviews/li/l7/page3/", "ru", "Li L7 отзывы стр.3"),
    # L6, L8 reviews
    ("https://www.drom.ru/reviews/li/l6/", "ru", "Li L6 отзывы"),
    ("https://www.drom.ru/reviews/li/l8/", "ru", "Li L8 отзывы"),
]

# "5 копеек" problem pages — structured breakdowns
PROBLEM_PAGES = [
    # All problems
    ("https://www.drom.ru/reviews/li/l7/5kopeek/", "ru", "Li L7 все проблемы"),
    ("https://www.drom.ru/reviews/li/l9/5kopeek/", "ru", "Li L9 все проблемы"),
    # Breakdowns only
    ("https://www.drom.ru/reviews/li/l7/5kopeek/?only=breakagies", "ru", "Li L7 поломки"),
    ("https://www.drom.ru/reviews/li/l9/5kopeek/?only=breakagies", "ru", "Li L9 поломки"),
    # Service/maintenance
    ("https://www.drom.ru/reviews/li/l7/5kopeek/?only=to", "ru", "Li L7 ТО"),
    ("https://www.drom.ru/reviews/li/l9/5kopeek/?only=to", "ru", "Li L9 ТО"),
    # L6, L8
    ("https://www.drom.ru/reviews/li/l6/5kopeek/", "ru", "Li L6 проблемы"),
    ("https://www.drom.ru/reviews/li/l8/5kopeek/", "ru", "Li L8 проблемы"),
]


def _extract_structured_review(page) -> dict:
    """Extract structured data from a drom.ru review page."""
    data = {
        'rating': '',
        'pros': '',
        'cons': '',
        'mileage': '',
        'year': '',
        'model': '',
    }

    # Try to extract rating
    rating_el = page.css(".b-review-mark__value::text").get()
    if rating_el:
        data['rating'] = rating_el.strip()

    # Extract pros/cons blocks
    for block in page.css(".b-review-plus-minus"):
        label = block.css("dt::text").get() or ""
        text = " ".join(block.css("dd::text").getall())
        if 'достоинств' in label.lower() or 'плюс' in label.lower():
            data['pros'] = text.strip()
        elif 'недостат' in label.lower() or 'минус' in label.lower():
            data['cons'] = text.strip()

    # Try to find mileage
    for text in page.css(".b-review-subheader ::text").getall():
        m = re.search(r'(\d[\d\s]*)\s*(км|тыс)', text, re.IGNORECASE)
        if m:
            data['mileage'] = m.group(0).strip()
            break

    # Try to find year
    for text in page.css(".b-review-subheader ::text, h1::text").getall():
        m = re.search(r'20[12]\d', text)
        if m:
            data['year'] = m.group(0)
            break

    # Model from URL or title
    title = page.css("h1::text").get() or ""
    for model in ['L9', 'L7', 'L8', 'L6', 'MEGA']:
        if model.lower() in title.lower():
            data['model'] = model
            break

    return data


def _format_structured_review(content: str, meta: dict) -> str:
    """Format review with structured metadata header."""
    parts = []

    if meta.get('model'):
        parts.append(f"Модель: Li {meta['model']}")
    if meta.get('year'):
        parts.append(f"Год: {meta['year']}")
    if meta.get('mileage'):
        parts.append(f"Пробег: {meta['mileage']}")
    if meta.get('rating'):
        parts.append(f"Оценка: {meta['rating']}/5")

    header = " | ".join(parts) if parts else ""

    sections = []
    if header:
        sections.append(f"[{header}]")

    if meta.get('pros'):
        sections.append(f"Достоинства: {meta['pros']}")
    if meta.get('cons'):
        sections.append(f"Недостатки: {meta['cons']}")

    if sections:
        sections.append("")  # separator
    sections.append(content)

    return "\n".join(sections)


class DromReviewsScraper(BaseScraper):
    source_name = "drom_reviews"
    lang = "ru"
    delay_range = (2.0, 5.0)
    min_content_length = 200
    skip_relevance_filter = True  # owner reviews are always relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        review_urls = set()

        # Phase 1: discover review links from listing pages
        for url, lang, label in REVIEW_LISTING_PAGES:
            log.info("Listing: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("Listing %s returned %d", url, page.status)
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link or "5kopeek" in link or "?order=" in link:
                        continue
                    if re.search(r"/reviews/li/\w+/\d+/?$", link):
                        if link.startswith("http"):
                            review_urls.add(link.rstrip("/"))
                        elif link.startswith("/"):
                            review_urls.add(f"https://www.drom.ru{link.rstrip('/')}")
                self._sleep()
            except Exception as exc:
                log.warning("Listing error: %s — %s", url, exc)

        log.info("Found %d review URLs", len(review_urls))

        # Phase 2: scrape "5 копеек" problem pages (structured problems)
        for url, lang, label in PROBLEM_PAGES:
            if self._already_scraped(url):
                continue
            log.info("Problems page: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                # Extract problem entries
                problems = []
                for entry in page.css(".b-media-cont, .review-entry, .b-review-5kop"):
                    text = " ".join(entry.css("::text").getall()).strip()
                    if len(text) > 50:
                        problems.append(text)

                # Fallback: extract all text nodes
                if not problems:
                    content = "\n".join(extract_text_nodes(page, min_len=20))
                else:
                    content = "\n\n---\n\n".join(problems)

                if len(content) > 200:
                    title = page.css("title::text").get() or label
                    yield ScrapedItem(
                        url=url, source_name=self.source_name,
                        lang="ru", title=title.strip()[:200], content=content,
                    )
                self._sleep()
            except Exception as exc:
                log.warning("Problems page error: %s — %s", url, exc)

        # Phase 3: scrape individual reviews with structured extraction
        for url in sorted(review_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""
                raw_content = "\n".join(extract_text_nodes(page, min_len=15))
                if len(raw_content) < 200:
                    continue

                # Extract structured metadata
                meta = _extract_structured_review(page)
                content = _format_structured_review(raw_content, meta)

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="ru", title=title.strip()[:200], content=content,
                )
            except Exception as exc:
                log.warning("Review error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = DromReviewsScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
