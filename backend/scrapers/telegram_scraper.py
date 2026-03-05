#!/usr/bin/env python3
"""
telegram_scraper.py — Scrape text content from Telegram channels and groups.

Uses the same Telethon credentials as the file downloader (config.py).
Extracts text messages, aggregates threads, saves to scraped_articles.db.

Usage:
    # Scrape a single channel
    python telegram_scraper.py --channel lixiangautorussia --limit 500

    # Scrape all configured channels
    python telegram_scraper.py --all --limit 1000

    # Dry run (preview without saving)
    python telegram_scraper.py --channel lixiangautorussia --limit 100 --dry-run
"""

import sys
import os
import re
import asyncio
import sqlite3
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict

# Add parent to path for config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from telethon import TelegramClient
    from telethon.tl.types import (
        Channel, Chat,
    )
    from telethon.errors import (
        FloodWaitError, ChannelPrivateError,
        UsernameNotOccupiedError, ChatAdminRequiredError,
    )
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "knowledge-base" / "kb.db"

# Channels/groups relevant to Li Auto diagnostics
DEFAULT_CHANNELS = [
    'lixiangautorussia',     # 40K+ members, main Russian Li Auto group
    'li_auto_russia',        # Li Auto Russia news
    'chinacarrussia',        # Chinese cars in Russia
    'china_auto_news',       # Chinese auto news
]

# Minimum text length to consider a message worth saving
MIN_MESSAGE_LENGTH = 100
# Messages shorter than this are considered noise
NOISE_LENGTH = 30
# Maximum messages to aggregate into one "article"
MAX_THREAD_MESSAGES = 50
# Relevance keywords (case-insensitive)
RELEVANCE_KEYWORDS = [
    'li auto', 'li l7', 'li l8', 'li l9', 'li mega', 'lixiang', 'ли авто',
    'идеал', 'ideal', 'диагност', 'diagnostic', 'ошибка', 'error', 'fault',
    'код', 'code', 'dtc', 'obd', 'ремонт', 'repair', 'замена', 'replace',
    'батарея', 'battery', 'тормоз', 'brake', 'подвеска', 'suspension',
    'двигатель', 'engine', 'мотор', 'motor', 'экран', 'display', 'screen',
    'обновлен', 'update', 'прошивка', 'firmware', 'гарантия', 'warranty',
    'сервис', 'service', 'дилер', 'dealer', 'пробег', 'mileage',
    'расход', 'consumption', 'зарядка', 'charging', 'range',
    'запчасть', 'part', 'деталь', 'detail', 'артикул', 'part number',
]


def detect_lang(text: str) -> str:
    sample = text[:500]
    ru = sum(1 for c in sample if '\u0400' <= c <= '\u04FF')
    zh = sum(1 for c in sample if '\u4E00' <= c <= '\u9FFF')
    if zh > 20:
        return 'zh'
    if ru > 20:
        return 'ru'
    return 'en'


def compute_relevance(text: str) -> float:
    """Score 0.0-1.0 based on keyword matches."""
    text_lower = text.lower()
    matches = sum(1 for kw in RELEVANCE_KEYWORDS if kw in text_lower)
    # Normalize: 0 matches = 0.1 (base), 5+ matches = 1.0
    score = min(0.1 + matches * 0.18, 1.0)
    return round(score, 2)


def classify_content(text: str) -> str:
    """Classify message content type."""
    text_lower = text.lower()
    if any(w in text_lower for w in ['отзыв', 'владел', 'опыт', 'купил', 'продал', 'пробег']):
        return 'owner_review'
    if any(w in text_lower for w in ['ошибка', 'error', 'код', 'code', 'dtc', 'неисправ']):
        return 'troubleshooting'
    if any(w in text_lower for w in ['замена', 'ремонт', 'repair', 'замен', 'снятие', 'установк']):
        return 'maintenance'
    if any(w in text_lower for w in ['характеристик', 'spec', 'мощност', 'объем', 'размер']):
        return 'specs'
    if any(w in text_lower for w in ['новост', 'news', 'анонс', 'выход', 'продаж', 'цена', 'price']):
        return 'news'
    return 'discussion'


def extract_dtc_codes(text: str) -> str:
    """Find DTC codes like P0300, C0265, U0100 etc."""
    codes = re.findall(r'\b[PCBU][0-9A-F]{4}\b', text.upper())
    return ','.join(sorted(set(codes))) if codes else ''


def ensure_db():
    """Ensure scraped_content table exists (matches base_scraper.py schema)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scraped_content (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                url_hash      TEXT NOT NULL UNIQUE,
                url           TEXT NOT NULL,
                source_name   TEXT NOT NULL,
                lang          TEXT NOT NULL DEFAULT '',
                title         TEXT,
                content       TEXT NOT NULL DEFAULT '',
                scraped_at    TEXT DEFAULT (datetime('now')),
                imported      INTEGER DEFAULT 0,
                chunk_id      TEXT,
                relevance     REAL DEFAULT 0,
                dtc_codes     TEXT DEFAULT '',
                content_class TEXT DEFAULT 'news'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped_source ON scraped_content(source_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped_imported ON scraped_content(imported)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped_url_hash ON scraped_content(url_hash)")


def content_hash(text: str) -> str:
    """Hash for deduplication."""
    normalized = re.sub(r'\s+', ' ', text.strip().lower())
    return hashlib.md5(normalized.encode()).hexdigest()


class TelegramContentScraper:
    """
    Scrape text messages from Telegram channels/groups.

    Two modes:
    1. Individual messages: long, standalone messages (>MIN_MESSAGE_LENGTH chars)
    2. Thread aggregation: group reply-chain messages into one "article"
    """

    def __init__(self, api_id: int, api_hash: str, phone: str,
                 session_dir: Optional[Path] = None):
        if not HAS_TELETHON:
            raise ImportError("telethon is required: pip install telethon")

        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone

        # Session in backend/.sessions/ (same as downloader)
        if session_dir is None:
            session_dir = Path(__file__).resolve().parent.parent / '.sessions'
        session_dir.mkdir(parents=True, exist_ok=True)
        self._session_path = str(session_dir / 'telegram_scraper')

        self.client: Optional[TelegramClient] = None
        self.stats = {'messages_scanned': 0, 'saved': 0, 'skipped': 0,
                      'duplicates': 0, 'too_short': 0}

    async def connect(self) -> bool:
        try:
            self.client = TelegramClient(
                self._session_path, self.api_id, self.api_hash
            )
            await self.client.start(phone=self.phone)
            me = await self.client.get_me()
            logger.info(f"Telegram connected: {me.first_name} (@{me.username or '-'})")
            return True
        except Exception as e:
            logger.error(f"Telegram connection failed: {e}")
            return False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def get_channel_info(self, channel: str) -> Optional[Dict]:
        """Get channel/group metadata."""
        try:
            entity = await self.client.get_entity(channel)
            return {
                'id': entity.id,
                'title': getattr(entity, 'title', ''),
                'username': getattr(entity, 'username', ''),
                'participants_count': getattr(entity, 'participants_count', None),
                'is_channel': isinstance(entity, Channel) and getattr(entity, 'broadcast', False),
                'is_group': isinstance(entity, (Chat, Channel)) and not getattr(entity, 'broadcast', False),
            }
        except (UsernameNotOccupiedError, ChannelPrivateError, ChatAdminRequiredError) as e:
            logger.error(f"Cannot access {channel}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting {channel}: {e}")
            return None

    async def scrape_channel(self, channel: str, limit: int = 1000,
                             min_length: int = MIN_MESSAGE_LENGTH,
                             dry_run: bool = False,
                             search: Optional[str] = None) -> List[Dict]:
        """
        Scrape text content from a Telegram channel/group.

        Modes:
        - Standalone messages >= min_length are saved individually
        - Reply chains (threads) are aggregated into one article

        Returns list of saved articles.
        """
        if not self.client:
            raise RuntimeError("Not connected")

        # Reset per-channel stats
        self.stats = {'messages_scanned': 0, 'saved': 0, 'skipped': 0,
                      'duplicates': 0, 'too_short': 0}

        try:
            entity = await self.client.get_entity(channel)
        except Exception as e:
            logger.error(f"Cannot resolve {channel}: {e}")
            return []

        source_name = f"telegram_{channel.lstrip('@').lower()}"
        channel_title = getattr(entity, 'title', channel)
        logger.info(f"Scraping {channel_title} (@{channel}) — limit={limit}")

        ensure_db()

        # Load existing URLs to skip duplicates
        existing_urls = set()
        with sqlite3.connect(str(DB_PATH)) as conn:
            rows = conn.execute(
                "SELECT url FROM scraped_content WHERE source_name=?", (source_name,)
            ).fetchall()
            existing_urls = {r[0] for r in rows}

        # Also track content hashes for dedup
        existing_hashes = set()
        with sqlite3.connect(str(DB_PATH)) as conn:
            rows = conn.execute(
                "SELECT content FROM scraped_content WHERE source_name=?", (source_name,)
            ).fetchall()
            existing_hashes = {content_hash(r[0]) for r in rows}

        saved = []
        # Collect messages with reply_to for thread aggregation
        threads: Dict[int, List] = {}  # reply_to_msg_id -> [messages]
        standalone = []

        flood_retries = 0
        max_flood_retries = 3

        while flood_retries <= max_flood_retries:
            # Clear on retry to avoid duplicated text from partial iteration
            threads.clear()
            standalone.clear()
            self.stats['messages_scanned'] = 0

            try:
                async for message in self.client.iter_messages(entity, limit=limit, search=search or ''):
                    self.stats['messages_scanned'] += 1

                    if self.stats['messages_scanned'] % 200 == 0:
                        logger.info(f"  Scanned {self.stats['messages_scanned']} messages...")

                    # Skip media-only messages
                    text = message.message or ''
                    if len(text.strip()) < NOISE_LENGTH:
                        continue

                    # Build message dict
                    msg = {
                        'id': message.id,
                        'text': text.strip(),
                        'date': message.date,
                        'reply_to': getattr(message.reply_to, 'reply_to_msg_id', None)
                                    if message.reply_to else None,
                        'sender': '',
                        'views': getattr(message, 'views', 0) or 0,
                        'forwards': getattr(message, 'forwards', 0) or 0,
                    }

                    # Get sender name
                    try:
                        if message.sender:
                            if hasattr(message.sender, 'first_name'):
                                msg['sender'] = (message.sender.first_name or '') + ' ' + (message.sender.last_name or '')
                            elif hasattr(message.sender, 'title'):
                                msg['sender'] = message.sender.title
                            msg['sender'] = msg['sender'].strip()
                    except Exception:
                        pass

                    # Route: standalone or thread
                    if msg['reply_to']:
                        root = msg['reply_to']
                        if root not in threads:
                            threads[root] = []
                        threads[root].append(msg)
                    elif len(text) >= min_length:
                        standalone.append(msg)
                    else:
                        # Short non-reply: might be a thread root
                        if message.id not in threads:
                            threads[message.id] = []
                        threads[message.id].insert(0, msg)

                break  # Completed successfully — exit retry loop

            except FloodWaitError as e:
                flood_retries += 1
                wait = e.seconds + 1
                logger.warning(f"FloodWait {e.seconds}s — retry {flood_retries}/{max_flood_retries}")
                if flood_retries > max_flood_retries:
                    logger.error("Too many FloodWait errors, stopping iteration")
                    break
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error(f"Error iterating {channel}: {e}")
                break

        logger.info(f"  Found {len(standalone)} standalone + {len(threads)} threads")

        # Reconcile: if a standalone message has replies in threads,
        # move it to the thread as root instead of saving separately
        reconciled = []
        for msg in standalone:
            if msg['id'] in threads:
                threads[msg['id']].insert(0, msg)
            else:
                reconciled.append(msg)
        standalone = reconciled

        # Process standalone messages
        for msg in standalone:
            url = f"https://t.me/{channel.lstrip('@')}/{msg['id']}"
            if url in existing_urls:
                self.stats['duplicates'] += 1
                continue

            h = content_hash(msg['text'])
            if h in existing_hashes:
                self.stats['duplicates'] += 1
                continue

            article = self._make_article(
                text=msg['text'],
                url=url,
                source_name=source_name,
                date=msg['date'],
                title=self._extract_title(msg['text']),
                sender=msg['sender'],
                views=msg['views'],
            )

            if not dry_run:
                self._save_article(article)
                existing_urls.add(url)
                existing_hashes.add(h)

            saved.append(article)
            self.stats['saved'] += 1

        # Process threads: aggregate reply chains into articles
        for root_id, messages in threads.items():
            if not messages:
                continue

            # Sort by date ascending
            messages.sort(key=lambda m: m['date'] or datetime.min.replace(tzinfo=timezone.utc))

            # Aggregate text
            parts = []
            total_views = 0
            for m in messages[:MAX_THREAD_MESSAGES]:
                prefix = f"[{m['sender']}]" if m['sender'] else ""
                parts.append(f"{prefix} {m['text']}".strip())
                total_views = max(total_views, m.get('views', 0))

            combined = '\n\n'.join(parts)

            if len(combined) < min_length:
                self.stats['too_short'] += 1
                continue

            url = f"https://t.me/{channel.lstrip('@')}/{root_id}"
            if url in existing_urls:
                self.stats['duplicates'] += 1
                continue

            h = content_hash(combined)
            if h in existing_hashes:
                self.stats['duplicates'] += 1
                continue

            article = self._make_article(
                text=combined,
                url=url,
                source_name=source_name,
                date=messages[0]['date'],
                title=self._extract_title(combined),
                sender='',
                views=total_views,
                is_thread=True,
                thread_size=len(messages),
            )

            if not dry_run:
                self._save_article(article)
                existing_urls.add(url)
                existing_hashes.add(h)

            saved.append(article)
            self.stats['saved'] += 1

        logger.info(
            f"Done: saved={self.stats['saved']}, "
            f"duplicates={self.stats['duplicates']}, "
            f"too_short={self.stats['too_short']}, "
            f"scanned={self.stats['messages_scanned']}"
        )

        return saved

    def _extract_title(self, text: str, max_len: int = 120) -> str:
        """Extract title from first line or first sentence."""
        if not text:
            return ''
        first_line = text.split('\n')[0].strip()
        # If first line is short and looks like a title, use it
        if len(first_line) <= max_len and len(first_line) >= 5:
            return first_line
        # Otherwise use first sentence
        for sep in ['. ', '! ', '? ', '\n']:
            idx = text.find(sep)
            if 5 <= idx < max_len:
                return text[:idx + 1].strip()
        # Fallback: truncate only if needed
        if len(text) <= max_len:
            return text.strip()
        return text[:max_len].strip() + '...'

    def _make_article(self, text: str, url: str, source_name: str,
                      date, title: str, sender: str = '',
                      views: int = 0, is_thread: bool = False,
                      thread_size: int = 1) -> Dict:
        lang = detect_lang(text)
        relevance = compute_relevance(text)
        content_class = classify_content(text)
        dtc = extract_dtc_codes(text)

        # Boost relevance for popular messages
        if views > 1000:
            relevance = min(relevance + 0.1, 1.0)
        if thread_size > 5:
            relevance = min(relevance + 0.05, 1.0)

        return {
            'url': url,
            'source_name': source_name,
            'lang': lang,
            'title': title[:300],
            'content': text,
            'content_class': content_class,
            'relevance': round(relevance, 2),
            'dtc_codes': dtc,
            'date': date,
        }

    def _save_article(self, article: Dict):
        url_hash = hashlib.md5(article['url'].encode()).hexdigest()
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO scraped_content
                    (url_hash, url, source_name, lang, title, content,
                     content_class, relevance, dtc_codes, imported, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
            """, (
                url_hash,
                article['url'], article['source_name'], article['lang'],
                article['title'], article['content'], article['content_class'],
                article['relevance'], article['dtc_codes'],
            ))


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Telegram content scraper')
    parser.add_argument('--channel', '-c', help='Channel username (without @)')
    parser.add_argument('--all', action='store_true', help='Scrape all default channels')
    parser.add_argument('--limit', '-l', type=int, default=500, help='Message limit per channel')
    parser.add_argument('--min-length', type=int, default=MIN_MESSAGE_LENGTH, help='Min text length')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--search', '-s', help='Search keyword (Telegram server-side search)')
    parser.add_argument('--list-channels', action='store_true', help='List configured channels')
    args = parser.parse_args()

    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Load credentials from config
    try:
        import config
        api_id = config.TELEGRAM_API_ID
        api_hash = config.TELEGRAM_API_HASH
        phone = config.TELEGRAM_PHONE
    except (ImportError, AttributeError) as e:
        print(f"Error loading config.py: {e}")
        print("Set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE in config.py")
        sys.exit(1)

    if not api_id or not api_hash:
        print("Telegram API credentials not configured in config.py")
        sys.exit(1)

    if args.list_channels:
        print("Default channels:")
        for ch in DEFAULT_CHANNELS:
            print(f"  @{ch}")
        return

    channels = []
    if args.all:
        channels = DEFAULT_CHANNELS
    elif args.channel:
        channels = [args.channel.lstrip('@')]
    else:
        parser.print_help()
        return

    scraper = TelegramContentScraper(api_id, api_hash, phone)
    if not await scraper.connect():
        sys.exit(1)

    try:
        total_saved = 0
        for ch in channels:
            print(f"\n{'='*60}")
            print(f"Channel: @{ch}")
            print(f"{'='*60}")

            info = await scraper.get_channel_info(ch)
            if info:
                print(f"  Title: {info['title']}")
                print(f"  Members: {info.get('participants_count', '?')}")
                print(f"  Type: {'channel' if info['is_channel'] else 'group'}")

            articles = await scraper.scrape_channel(
                ch, limit=args.limit, min_length=args.min_length,
                dry_run=args.dry_run, search=args.search,
            )
            total_saved += len(articles)

            if args.dry_run and articles:
                print(f"\n  Preview ({len(articles)} articles):")
                for a in articles[:5]:
                    print(f"    [{a['content_class']}] {a['title'][:60]}  "
                          f"({len(a['content'])} chars, rel={a['relevance']})")
                if len(articles) > 5:
                    print(f"    ... and {len(articles)-5} more")

            # Rate limit between channels
            if len(channels) > 1:
                await asyncio.sleep(2)

        mode = "DRY RUN" if args.dry_run else "SAVED"
        print(f"\n{'='*60}")
        print(f"TOTAL: {total_saved} articles [{mode}]")
        print(f"Stats: {scraper.stats}")
    finally:
        await scraper.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
