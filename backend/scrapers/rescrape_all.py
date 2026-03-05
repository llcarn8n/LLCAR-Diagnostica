#!/usr/bin/env python3
"""
rescrape_all.py — Re-scrape all articles through the new _extract_article system.

Fetches each URL from scraped_content, extracts with auto method,
compares with existing content, and updates if better.
"""
import sqlite3
import sys
import os
import time
import re
import hashlib

# Add api/ to path so we can reuse helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
import trafilatura
from bs4 import BeautifulSoup

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scraped_articles.db')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,zh;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_html(url: str, timeout: int = 30) -> str:
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=HEADERS, verify=False) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def detect_lang(text: str) -> str:
    sample = text[:500]
    ru_count = sum(1 for c in sample if '\u0400' <= c <= '\u04FF')
    zh_count = sum(1 for c in sample if '\u4E00' <= c <= '\u9FFF')
    if zh_count > 20:
        return "zh"
    if ru_count > 20:
        return "ru"
    return "en"


def extract_article(html: str, url: str, method: str = "auto") -> dict:
    """Extract article title+content from HTML. Methods: auto, trafilatura, bs4_article, bs4, regex"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower().replace("www.", "")
    soup = BeautifulSoup(html, 'html.parser')

    def _bs4_site_specific():
        # Drom.ru single review
        if "drom.ru" in domain and "/reviews/" in url and url.count("/") > 5:
            editable = soup.select_one('.b-editable-area')
            if editable and len(editable.get_text()) > 200:
                content = editable.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Drom.ru review listing (5kopeek)
        if "drom.ru" in domain and "5kopeek" in url:
            import json as _json
            for script in soup.find_all('script', type='application/json'):
                try:
                    if script.string and len(script.string) > 10000:
                        data = _json.loads(script.string)
                        short_reviews = data.get('shortReviews', [])
                        if short_reviews:
                            parts = []
                            for rev in short_reviews:
                                adv = rev.get('advantages', '')
                                dis = rev.get('disadvantages', '')
                                brk = rev.get('breakages', '')
                                txt = ""
                                if adv: txt += f"Достоинства: {adv}\n"
                                if dis: txt += f"Недостатки: {dis}\n"
                                if brk: txt += f"Поломки: {brk}\n"
                                if txt:
                                    parts.append(txt.strip())
                            if parts:
                                return {"title": f"Отзывы владельцев", "content": "\n\n---\n\n".join(parts)}
                except Exception:
                    pass

        # Carnewschina
        if "carnewschina" in domain:
            article = soup.select_one('article .entry-content, .post-content, article')
            if article:
                for tag in article.select('script, style, nav, .sharedaddy, .jp-relatedposts, .comments'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1.entry-title, h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Getcar.ru
        if "getcar" in domain:
            article = soup.select_one('.post-content, .entry-content, article')
            if article:
                for tag in article.select('script, style, nav, .related, .comments'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # topelectricsuv / insideevs
        if any(s in domain for s in ["topelectricsuv", "insideevs"]):
            article = soup.select_one('article .entry-content, .post-content, .article-body, article')
            if article:
                for tag in article.select('script, style, nav, .ad, .related, .comments, .social'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Lixiang.com (JS-rendered, likely empty from httpx)
        if "lixiang.com" in domain:
            return None

        # Russian news sites
        if any(s in domain for s in ["autoreview.ru", "autonews.ru", "motor.ru", "autostat.ru",
                                      "chinamobil.ru", "kitaec.ua", "avtotachki.com"]):
            selectors = [
                'article .article-body', 'article .post-content', '.article-content',
                '.post-body', '.entry-content', 'article .content', '.article__content',
                '.b-text', '.material-content', '.news-text', '.post__text',
            ]
            for sel in selectors:
                el = soup.select_one(sel)
                if el and len(el.get_text()) > 200:
                    for tag in el.select('script, style, nav, .ad, .related, .comments, .social, .share'):
                        tag.decompose()
                    content = el.get_text(separator='\n', strip=True)
                    h1 = soup.select_one('h1')
                    title = h1.get_text(strip=True) if h1 else ""
                    return {"title": title, "content": content}

        # Autochina blog
        if "autochina" in domain or "cnevpost" in domain:
            article = soup.select_one('article .entry-content, .post-content, article')
            if article:
                for tag in article.select('script, style, nav, .related, .comments, .social'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Carscoops
        if "carscoops" in domain:
            article = soup.select_one('.entry-content, .article-body, article')
            if article:
                for tag in article.select('script, style, nav, .related, .comments, .social, .ad'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Electrek
        if "electrek" in domain:
            article = soup.select_one('.article-content, .entry-content, article .post-content')
            if article:
                for tag in article.select('script, style, nav, .related, .comments, .social'):
                    tag.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        return None

    def _trafilatura_extract(precision=False):
        kwargs = {
            "include_comments": False,
            "include_tables": True,
            "deduplicate": True,
            "no_fallback": precision,
            "favor_precision": precision,
        }
        text = trafilatura.extract(html, **kwargs) or ""
        title = ""
        meta = trafilatura.extract(html, output_format="xml", **kwargs)
        if meta:
            m = re.search(r'<title>(.*?)</title>', meta or "")
            if m:
                title = m.group(1).strip()
        if not title:
            h1 = soup.select_one('h1')
            if h1:
                title = h1.get_text(strip=True)
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()
        return {"title": title, "content": text}

    def _bs4_generic():
        for tag in soup.select('script, style, nav, header, footer, .sidebar, .menu, .nav, .comments, .ad'):
            tag.decompose()
        candidates = soup.select('article, main, .content, .post, .entry, [role="main"]')
        best = ""
        for cand in candidates:
            text = cand.get_text(separator='\n', strip=True)
            if len(text) > len(best):
                best = text
        if not best:
            body = soup.find('body')
            if body:
                divs = body.find_all('div', recursive=False)
                for div in divs:
                    text = div.get_text(separator='\n', strip=True)
                    if len(text) > len(best):
                        best = text
        title = ""
        h1 = soup.select_one('h1')
        if h1:
            title = h1.get_text(strip=True)
        if not title and soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        return {"title": title, "content": best or ""}

    def _regex_extract():
        m_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S | re.I)
        title = re.sub(r'<[^>]+>', '', m_h1.group(1)).strip() if m_h1 else ""
        if not title:
            m_t = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
            if m_t:
                title = re.sub(r'\s+', ' ', m_t.group(1)).strip()
        parts = []
        for m in re.finditer(r'<p[^>]*>(.*?)</p>', html, re.S | re.I):
            text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            text = re.sub(r'\s+', ' ', text)
            if len(text) > 40:
                parts.append(text)
        return {"title": title, "content": "\n\n".join(parts)}

    # --- Execute ---
    if method == "auto":
        result = _bs4_site_specific()
        if result and len(result.get("content", "")) > 100:
            result["method_used"] = "bs4_article"
            return result
        result = _trafilatura_extract(precision=False)
        if len(result.get("content", "")) > 100:
            result["method_used"] = "trafilatura"
            return result
        result = _bs4_generic()
        if len(result.get("content", "")) > 100:
            result["method_used"] = "bs4"
            return result
        result = _regex_extract()
        result["method_used"] = "regex"
        return result
    elif method == "trafilatura":
        result = _trafilatura_extract(precision=False)
        result["method_used"] = "trafilatura"
        return result
    elif method == "bs4_article":
        result = _bs4_site_specific()
        if result and len(result.get("content", "")) > 50:
            result["method_used"] = "bs4_article"
            return result
        result = _bs4_generic()
        result["method_used"] = "bs4"
        return result
    elif method == "bs4":
        result = _bs4_generic()
        result["method_used"] = "bs4"
        return result
    elif method == "regex":
        result = _regex_extract()
        result["method_used"] = "regex"
        return result
    else:
        raise ValueError(f"Unknown method: {method}")


def clean_content(content: str) -> str:
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if any(p in line.lower() for p in [
            'cookie', 'javascript', 'подписаться', 'subscribe',
            'политика конфиденциальности', 'privacy policy',
            'все права защищены', 'all rights reserved',
        ]):
            continue
        if len(line) < 5 and not any(c.isdigit() for c in line):
            continue
        cleaned.append(line)
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return '\n'.join(cleaned)


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, url, source_name, lang, title, LENGTH(content) as old_len FROM scraped_content ORDER BY id"
    ).fetchall()
    print(f"Total articles to re-scrape: {len(rows)}")

    stats = {"updated": 0, "kept": 0, "failed": 0, "skipped": 0}
    changes = []

    for i, (item_id, url, source, lang, old_title, old_len) in enumerate(rows):
        prefix = f"[{i+1}/{len(rows)}] id={item_id} ({source})"
        try:
            html = fetch_html(url)
            result = extract_article(html, url, "auto")
            content = clean_content(result.get("content", ""))
            title = result.get("title", "") or old_title
            method_used = result.get("method_used", "auto")

            if len(content) < 50:
                print(f"{prefix} SKIP: content too short ({len(content)} chars)")
                stats["skipped"] += 1
                continue

            new_len = len(content)
            diff = new_len - old_len
            pct = (diff / old_len * 100) if old_len > 0 else 0

            # Update if content changed significantly or is cleaner
            new_lang = detect_lang(content) if not lang else lang
            conn.execute(
                "UPDATE scraped_content SET title=?, content=?, lang=?, scraped_at=datetime('now') WHERE id=?",
                (title[:300], content, new_lang, item_id)
            )
            conn.commit()

            status = "UPDATED"
            if abs(pct) < 5:
                status = "~same"
                stats["kept"] += 1
            else:
                stats["updated"] += 1
                changes.append((item_id, source, old_len, new_len, pct, method_used, title[:50]))

            sign = "+" if diff > 0 else ""
            print(f"{prefix} {status}: {old_len:,d} -> {new_len:,d} ({sign}{pct:.0f}%) [{method_used}]")

        except Exception as exc:
            err_msg = str(exc)[:60]
            print(f"{prefix} FAIL: {err_msg}")
            stats["failed"] += 1

        # Rate limiting
        time.sleep(1.5)

    conn.close()

    print(f"\n{'='*60}")
    print(f"DONE: updated={stats['updated']}, kept={stats['kept']}, failed={stats['failed']}, skipped={stats['skipped']}")
    if changes:
        print(f"\n=== Significant changes ({len(changes)}) ===")
        for cid, src, old, new, pct, meth, title in sorted(changes, key=lambda x: abs(x[4]), reverse=True)[:20]:
            sign = "+" if pct > 0 else ""
            print(f"  id={cid} | {src:18s} | {old:>6,d} -> {new:>6,d} ({sign}{pct:.0f}%) | {meth} | {title}")


if __name__ == "__main__":
    main()
