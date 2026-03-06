#!/usr/bin/env python3
"""
drive2_scraper.py — Scraper for drive2.ru Li Auto owner logbooks.

Extracts: owner experience logs, maintenance reports, fault documentation.

Drive2.ru blocks basic HTTP requests (403). Strategy:
1. Try curl_cffi with browser TLS fingerprint impersonation
2. Try stealth_fetch (patchright anti-detection browser)
3. Fall back to static_fetch (will likely 403)
"""
from __future__ import annotations

import logging
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, stealth_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

# Starting points — model experience pages + known valuable threads
# Research-informed: added specific repair logs found by 6 research agents
SEED_URLS = [
    # L7 experience logs
    ("https://www.drive2.ru/experience/liauto/g657426865501256680", "Li L7 бортжурналы"),
    # L9 experience logs
    ("https://www.drive2.ru/experience/liauto/g657427415257062407", "Li L9 бортжурналы"),
    # L7 owner cars
    ("https://www.drive2.ru/cars/liauto/li_l7/", "Li L7 автомобили владельцев"),
    # L9 owner cars
    ("https://www.drive2.ru/cars/liauto/l9/", "Li L9 автомобили владельцев"),
    # Known active logbooks
    ("https://www.drive2.ru/r/liauto/l9/639530389613845759/logbook/", "Li L9 бортжурнал #1"),
    ("https://www.drive2.ru/r/liauto/l9/663903538744663042/logbook/", "Li L9 BAT Mobile"),
    ("https://www.drive2.ru/r/liauto/l7/663933225558607229/logbook/", "Li L7 бортжурнал"),
    ("https://www.drive2.ru/r/liauto/l7/669696865511418474/logbook/", "Li L7 2024"),
    ("https://www.drive2.ru/r/liauto/l9/659259476506856329/logbook/", "Li L9 LiXOЙ"),
    # Research-discovered high-value repair logs:
    ("https://www.drive2.ru/l/700705017560044478/", "Ремонт пневмоподвески L7/L9"),
    ("https://www.drive2.ru/l/697330341496494867/", "Решаем проблемы с пневмоподвеской"),
    ("https://www.drive2.ru/l/688364373927796623/", "Ошибка пневмоподвески Li 7"),
    ("https://www.drive2.ru/l/681493250887921808/", "Вскрытие двигателя L9 — масложор"),
    ("https://www.drive2.ru/l/674845603586396382/", "Положили мотор на L9"),
    ("https://www.drive2.ru/l/717411272110386402/", "Почему двигатель выходит из строя"),
    ("https://www.drive2.ru/l/714032747756141707/", "OTA 7.4 проблемы прошивки"),
    ("https://www.drive2.ru/l/706362004884950860/", "Мультимедиа зависания"),
    ("https://www.drive2.ru/l/679038866056810905/", "Тормоза — визг и износ"),
    ("https://www.drive2.ru/l/688693127904509635/", "ZF суппорты проблемы"),
    ("https://www.drive2.ru/l/694649732147982468/", "Зимняя эксплуатация — все проблемы"),
    ("https://www.drive2.ru/l/720585012423953978/", "OTA обновления — блокировка"),
]


def _smart_fetch(url: str, timeout: int = 30):
    """Try best available fetch method for drive2.ru.
    Priority: curl_cffi (fast, browser TLS) > stealth_fetch (slow, headless) > static_fetch."""

    # Method 1: curl_cffi with Chrome TLS fingerprint
    try:
        from curl_cffi import requests as curl_requests
        r = curl_requests.get(url, impersonate="chrome", timeout=timeout,
                              allow_redirects=True)
        if r.status_code == 200:
            from base_scraper import _BS4Page
            return _BS4Page(r.status_code, r.text, str(r.url))
        log.debug("curl_cffi returned %d for %s", r.status_code, url)
    except ImportError:
        log.debug("curl_cffi not installed, trying stealth_fetch")
    except Exception as exc:
        log.debug("curl_cffi failed for %s: %s", url, exc)

    # Method 2: stealth_fetch (patchright / scrapling)
    page = stealth_fetch(url, timeout=timeout)
    if page.status == 200:
        return page

    # Method 3: static_fetch (will likely 403 but try anyway)
    log.warning("All stealth methods failed for %s, trying static_fetch", url)
    return static_fetch(url, timeout=timeout)


class Drive2Scraper(BaseScraper):
    source_name = "drive2_ru"
    lang = "ru"
    delay_range = (3.0, 7.0)  # more conservative for drive2
    min_content_length = 200
    skip_relevance_filter = True  # owner content is always relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        # Phase 1: crawl seed pages and discover article links
        article_urls = set()
        logbook_urls = set()

        for url, title_hint in SEED_URLS:
            log.info("Crawling seed: %s", url)
            try:
                page = _smart_fetch(url, timeout=30)
                if page.status != 200:
                    log.warning("HTTP %d for %s (drive2 may be blocking)", page.status, url)
                    continue

                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full_url = link if link.startswith("http") else f"https://www.drive2.ru{link}"

                    # Blog posts: /b/XXXXX/ format (bortzhurnal entries)
                    if re.search(r'/b/\d+/?$', full_url):
                        article_urls.add(full_url.rstrip('/'))
                    # Logbook entries: /l/XXXXX/
                    elif re.search(r'/l/\d+/?$', full_url):
                        article_urls.add(full_url.rstrip('/'))
                    # Logbook listing pages: /logbook/
                    elif '/logbook/' in full_url and full_url not in [u for u, _ in SEED_URLS]:
                        logbook_urls.add(full_url)

                self._sleep()
            except Exception as exc:
                log.warning("Seed error: %s — %s", url, exc)

        # Phase 1.5: crawl logbook listing pages for more entries
        for url in sorted(logbook_urls):
            log.info("Crawling logbook listing: %s", url)
            try:
                page = _smart_fetch(url, timeout=30)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full_url = link if link.startswith("http") else f"https://www.drive2.ru{link}"
                    if re.search(r'/[bl]/\d+/?$', full_url):
                        article_urls.add(full_url.rstrip('/'))
                self._sleep()
            except Exception as exc:
                log.warning("Logbook listing error: %s — %s", url, exc)

        log.info("Discovered %d article URLs", len(article_urls))

        # Phase 2: scrape individual articles
        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue

            try:
                page = _smart_fetch(url, timeout=30)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""
                title = title.strip()

                # Extract article content from drive2 post structure
                content_parts = []

                # Try drive2-specific selectors
                for selector in [
                    ".c-post__body p",
                    ".c-post__body .c-text-block",
                    "article .c-text-block",
                    "article p",
                    ".js-eo__text",
                    ".c-article-text p",
                ]:
                    for el in page.css(selector):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 20:
                            content_parts.append(text)
                    if content_parts:
                        break

                # Fallback: extract all text
                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(content_parts)
                if len(content) < 200:
                    continue

                # Try to extract metadata from the page
                meta_parts = []

                # Car model from breadcrumbs or title
                for model in ['L9', 'L7', 'L8', 'L6', 'MEGA']:
                    if model.lower() in (title + url).lower():
                        meta_parts.append(f"Модель: Li {model}")
                        break

                # Mileage if mentioned
                m = re.search(r'(\d[\d\s]*)\s*(км|тыс\.?\s*км)', content[:500], re.IGNORECASE)
                if m:
                    meta_parts.append(f"Пробег: {m.group(0).strip()}")

                # Prepend metadata
                if meta_parts:
                    content = "[" + " | ".join(meta_parts) + "]\n\n" + content

                yield ScrapedItem(
                    url=url,
                    source_name=self.source_name,
                    lang="ru",
                    title=title[:200],
                    content=content,
                )

            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = Drive2Scraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
