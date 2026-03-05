#!/usr/bin/env python3
"""
electrek_scraper.py — Scraper for English EV news sites about Li Auto.

Sources:
  - electrek.co — top EV news site
  - insideevs.com — EV reviews & news
  - cleantechnica.com — clean energy & EV news
  - carscoops.com — auto news with Li Auto coverage

All static-rendered, no JS needed.
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes

log = logging.getLogger(__name__)

LISTING_URLS = [
    # Electrek — paginated search
    ("https://electrek.co/?s=li+auto", "en", "electrek", "Li Auto search"),
    ("https://electrek.co/page/2/?s=li+auto", "en", "electrek", "Li Auto search p2"),
    ("https://electrek.co/?s=li+auto+l7", "en", "electrek", "Li Auto L7 search"),
    ("https://electrek.co/?s=li+auto+l9", "en", "electrek", "Li Auto L9 search"),
    ("https://electrek.co/?s=lixiang", "en", "electrek", "Lixiang search"),
    # InsideEVs
    ("https://insideevs.com/search/li-auto/", "en", "insideevs", "Li Auto search"),
    ("https://insideevs.com/tag/li-auto/", "en", "insideevs", "Li Auto tag"),
    # CleanTechnica
    ("https://cleantechnica.com/?s=li+auto", "en", "cleantechnica", "Li Auto search"),
    ("https://cleantechnica.com/?s=li+auto+l7+l9", "en", "cleantechnica", "Li Auto L7 L9"),
    # CarScoops — paginated search
    ("https://www.carscoops.com/?s=li+auto", "en", "carscoops", "Li Auto search"),
    ("https://www.carscoops.com/page/2/?s=li+auto", "en", "carscoops", "Li Auto p2"),
    ("https://www.carscoops.com/?s=li+auto+l9", "en", "carscoops", "Li Auto L9"),
    ("https://www.carscoops.com/?s=li+auto+l7", "en", "carscoops", "Li Auto L7"),
    ("https://www.carscoops.com/?s=li+auto+mega", "en", "carscoops", "Li Auto MEGA"),
]


class ElectrekScraper(BaseScraper):
    source_name = "ev_news_en"
    lang = "en"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Phase 1: discover articles from search/tag pages
        for url, lang, source_tag, title_hint in LISTING_URLS:
            log.info("Listing [%s]: %s", source_tag, url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                for link in page.css("a::attr(href)").getall():
                    if not link or not link.startswith("http"):
                        continue
                    link = link.split("#")[0].rstrip("/")
                    link_lower = link.lower()

                    # Filter: must be article with date pattern and Li Auto keyword
                    has_date = bool(re.search(r"/\d{4}/\d{2}/", link))
                    has_keyword = ("li-auto" in link_lower or "li_auto" in link_lower or
                                   "lixiang" in link_lower or "li-l7" in link_lower or
                                   "li-l9" in link_lower or "ideal-" in link_lower)
                    not_nav = not any(x in link_lower for x in ["/tag/", "/category/",
                                     "/author/", "/page/", "?s="])

                    if has_date and has_keyword and not_nav:
                        article_urls.add((link, lang, source_tag))

                self._sleep()
            except Exception as exc:
                log.warning("Listing error: %s — %s", url, exc)

        log.info("Discovered %d article URLs", len(article_urls))

        # Phase 2: scrape individual articles
        for url, lang, source_tag in sorted(article_urls)[:80]:
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = (page.css("h1.entry-title::text").get()
                         or page.css("h1::text").get()
                         or page.css("meta[property='og:title']::attr(content)").get()
                         or page.css("title::text").get() or "")
                title = re.sub(r"\s*[|—\-]\s*(Electrek|InsideEVs|CleanTechnica|Carscoops).*$",
                               "", title, flags=re.I).strip()
                if not title:
                    slug = url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").title()

                # Extract article content
                paragraphs = []
                for el in page.css("article p, .entry-content p, .post-content p, "
                                   ".article-body p, .article__content p"):
                    text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                    if len(text) > 30:
                        paragraphs.append(text)

                if not paragraphs:
                    paragraphs = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(paragraphs)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=f"{source_tag}_en",
                    lang=lang, title=title[:200], content=content,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = ElectrekScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
