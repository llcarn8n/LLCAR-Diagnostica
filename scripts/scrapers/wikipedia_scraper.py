#!/usr/bin/env python3
"""
wikipedia_scraper.py — Scraper for Wikipedia articles about Li Auto L7/L9.

Uses Wikipedia REST API (not web scraping) — no blocking, reliable.
Extracts: specifications, history, technical details from EN/ZH/RU Wikipedia.
"""
from __future__ import annotations

import logging
import re
import sys
import os
import json
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem

log = logging.getLogger(__name__)

# (wiki_lang, article_title, title_hint)
WIKI_ARTICLES = [
    # English
    ("en", "Li_Auto", "Li Auto"),
    ("en", "Li_L7", "Li L7"),
    ("en", "Li_L9", "Li L9"),
    ("en", "Li_Auto_L9", "Li Auto L9"),
    ("en", "Li_Auto_L7", "Li Auto L7"),
    ("en", "Li_Auto_Inc.", "Li Auto Inc"),
    # Chinese
    ("zh", "理想汽车", "理想汽车"),
    ("zh", "理想L9", "理想L9"),
    ("zh", "理想L7", "理想L7"),
    # Russian
    ("ru", "Li_Auto", "Li Auto"),
    ("ru", "Li_L9", "Li L9"),
    ("ru", "Li_L7", "Li L7"),
]


class WikipediaScraper(BaseScraper):
    source_name = "wikipedia"
    lang = "en"
    delay_range = (1.0, 2.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        import httpx

        for wiki_lang, title, title_hint in WIKI_ARTICLES:
            url = f"https://{wiki_lang}.wikipedia.org/wiki/{title}"
            if self._already_scraped(url):
                log.info("Skip: %s", url)
                continue

            # Use Wikipedia REST API for plain text extract
            api_url = (f"https://{wiki_lang}.wikipedia.org/api/rest_v1"
                       f"/page/summary/{title}")
            log.info("API fetch: %s", api_url)

            try:
                r = httpx.get(api_url, timeout=15, follow_redirects=True,
                              headers={
                                  "User-Agent": "LLCAR-KB-Bot/1.0 (diagnostica research project; "
                                                "petr@example.com) httpx/0.28",
                                  "Accept": "application/json",
                              })
                if r.status_code == 404:
                    log.info("Article not found: %s/%s", wiki_lang, title)
                    continue
                if r.status_code != 200:
                    log.warning("HTTP %d for %s", r.status_code, api_url)
                    continue

                data = r.json()
                extract = data.get("extract", "")
                display_title = data.get("displaytitle", "") or data.get("title", title_hint)
                # Clean HTML from display_title
                display_title = re.sub(r"<[^>]+>", "", display_title).strip()

                if len(extract) < 100:
                    log.info("Short extract (%d) for %s/%s, trying full content", len(extract), wiki_lang, title)
                    # Try full mobile-sections API for more content
                    full_url = (f"https://{wiki_lang}.wikipedia.org/api/rest_v1"
                                f"/page/mobile-sections/{title}")
                    r2 = httpx.get(full_url, timeout=20, follow_redirects=True,
                                   headers={
                                       "User-Agent": "LLCAR-KB-Bot/1.0 (diagnostica research project) httpx/0.28",
                                       "Accept": "application/json",
                                   })
                    if r2.status_code == 200:
                        full_data = r2.json()
                        sections_text = []
                        # Lead section
                        lead = full_data.get("lead", {})
                        lead_text = self._html_to_text(lead.get("sections", [{}])[0].get("text", ""))
                        if lead_text:
                            sections_text.append(lead_text)
                        # Remaining sections
                        for sec in full_data.get("remaining", {}).get("sections", []):
                            heading = sec.get("line", "")
                            if heading in ("References", "External links", "See also",
                                           "Notes", "Further reading",
                                           "Примечания", "Ссылки", "Литература",
                                           "参考资料", "外部链接", "参见"):
                                continue
                            text = self._html_to_text(sec.get("text", ""))
                            if text:
                                sections_text.append(f"\n## {heading}\n{text}")
                        extract = "\n".join(sections_text)

                if len(extract) < 50:
                    log.info("Still too short for %s/%s, skipping", wiki_lang, title)
                    continue

                yield ScrapedItem(
                    url=url,
                    source_name=f"wikipedia_{wiki_lang}",
                    lang=wiki_lang,
                    title=display_title[:200],
                    content=extract,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Error: %s/%s — %s", wiki_lang, title, exc)

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text, preserving some structure."""
        if not html:
            return ""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        # Remove references, edit links
        for tag in soup.select(".reference, .mw-editsection, sup.reference, .noprint"):
            tag.decompose()

        lines = []
        for el in soup.find_all(["p", "li", "th", "td", "h2", "h3", "h4"]):
            text = el.get_text(separator=" ", strip=True)
            text = re.sub(r"\[\d+\]", "", text).strip()
            if len(text) > 10:
                if el.name in ("h2", "h3", "h4"):
                    lines.append(f"### {text}")
                elif el.name == "li":
                    lines.append(f"- {text}")
                else:
                    lines.append(text)
        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = WikipediaScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
