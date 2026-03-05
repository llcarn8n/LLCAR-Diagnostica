"""
═══════════════════════════════════════════════════════════════════════════════
                    СКАЧИВАНИЕ С ТОРРЕНТ-ТРЕКЕРОВ
═══════════════════════════════════════════════════════════════════════════════
"""

import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from urllib.parse import urljoin

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class TorrentInfo:
    """Информация о торренте"""
    id: str
    title: str
    url: str
    torrent_url: str
    size: int
    size_str: str
    seeds: int
    leeches: int
    downloads: int
    category: str
    date: str


class RuTrackerDownloader:
    """Загрузчик для RuTracker.org"""
    
    NAME = "RuTracker"
    BASE_URL = "https://rutracker.org"
    LOGIN_URL = "https://rutracker.org/forum/login.php"
    SEARCH_URL = "https://rutracker.org/forum/tracker.php"
    
    CATEGORIES = {
        'auto_repair': '1355',
        'auto_books': '1354',
    }
    
    def __init__(
        self,
        username: str,
        password: str,
        download_path: Path,
        proxy: Optional[str] = None
    ):
        self.username = username
        self.password = password
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_logged_in = False
        
        self.stats = {
            'searches': 0,
            'torrents_found': 0,
            'torrents_downloaded': 0,
            'errors': 0,
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Заголовки запроса"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        }
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Создаёт сессию"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=60)
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_headers()
            )
    
    async def disconnect(self):
        """Закрывает сессию"""
        if self.session:
            await self.session.close()
            self.session = None
            self.is_logged_in = False
    
    async def login(self) -> bool:
        """Авторизация"""
        if not self.session:
            await self.connect()
        
        try:
            logger.info(f"🔐 Авторизация на {self.NAME}...")
            
            login_data = {
                'login_username': self.username,
                'login_password': self.password,
                'login': 'Вход',
            }
            
            async with self.session.post(
                self.LOGIN_URL,
                data=login_data,
                proxy=self.proxy,
                allow_redirects=True
            ) as response:
                text = await response.text()
                
                if 'logged-in-username' in text or 'profile.php' in text:
                    self.is_logged_in = True
                    logger.info(f"✅ Авторизация успешна")
                    return True
                
                if 'Неверный пароль' in text:
                    logger.error("❌ Неверный логин или пароль")
                    return False
                
                if self.username.lower() in text.lower():
                    self.is_logged_in = True
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
            return False
    
    async def search(
        self,
        query: str,
        max_results: int = 50,
        min_seeds: int = 0
    ) -> List[TorrentInfo]:
        """Поиск раздач"""
        
        if not self.is_logged_in:
            if not await self.login():
                return []
        
        results = []
        self.stats['searches'] += 1
        
        try:
            logger.info(f"🔍 Поиск: {query}")
            
            params = {
                'nm': query,
                'o': '10',
                's': '2',
                'f': ','.join(self.CATEGORIES.values()),
            }
            
            async with self.session.get(
                self.SEARCH_URL,
                params=params,
                proxy=self.proxy
            ) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'lxml')
                
                rows = soup.select('tr.tCenter.hl-tr')
                
                for row in rows[:max_results]:
                    try:
                        torrent = self._parse_search_row(row)
                        if torrent and torrent.seeds >= min_seeds:
                            results.append(torrent)
                    except:
                        pass
                
                self.stats['torrents_found'] += len(results)
                logger.info(f"📋 Найдено: {len(results)}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            self.stats['errors'] += 1
        
        return results
    
    def _parse_search_row(self, row) -> Optional[TorrentInfo]:
        """Парсит строку результатов"""
        try:
            title_elem = row.select_one('a.tLink')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            topic_url = urljoin(self.BASE_URL, title_elem['href'])
            
            topic_id = re.search(r't=(\d+)', topic_url)
            topic_id = topic_id.group(1) if topic_id else ''
            
            size_elem = row.select_one('td.tor-size')
            size_str = size_elem.get_text(strip=True) if size_elem else '0'
            size = self._parse_size(size_str)
            
            seeds_elem = row.select_one('td.seedmed, span.seedmed')
            seeds = int(seeds_elem.get_text(strip=True)) if seeds_elem else 0
            
            leeches_elem = row.select_one('td.leechmed')
            leeches = int(leeches_elem.get_text(strip=True)) if leeches_elem else 0
            
            torrent_url = f"{self.BASE_URL}/forum/dl.php?t={topic_id}"
            
            return TorrentInfo(
                id=topic_id,
                title=title,
                url=topic_url,
                torrent_url=torrent_url,
                size=size,
                size_str=self._format_size(size),
                seeds=seeds,
                leeches=leeches,
                downloads=0,
                category='',
                date='',
            )
        except:
            return None
    
    async def download_torrent(self, torrent: TorrentInfo, filename: Optional[str] = None) -> Optional[Path]:
        """Скачивает .torrent файл"""
        if not self.is_logged_in:
            if not await self.login():
                return None
        
        try:
            if not filename:
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', torrent.title)[:150]
                filename = f"{safe_name}.torrent"
            
            filepath = self.download_path / filename
            
            if filepath.exists():
                return filepath
            
            async with self.session.get(torrent.torrent_url, proxy=self.proxy) as response:
                if response.status != 200:
                    return None
                
                content = await response.read()
                
                if not content.startswith(b'd8:announce') and b'BitTorrent' not in content:
                    return None
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(content)
                
                self.stats['torrents_downloaded'] += 1
                logger.info(f"✅ {filename}")
                
                return filepath
                
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            self.stats['errors'] += 1
            return None
    
    def _parse_size(self, size_str: str) -> int:
        """Парсит размер"""
        size_str = size_str.upper().strip()
        multipliers = {
            'KB': 1024, 'КБ': 1024,
            'MB': 1024**2, 'МБ': 1024**2,
            'GB': 1024**3, 'ГБ': 1024**3,
        }
        match = re.match(r'([\d.,]+)\s*([A-ZА-Я]+)', size_str)
        if match:
            number = float(match.group(1).replace(',', '.'))
            unit = match.group(2)
            return int(number * multipliers.get(unit, 1))
        return 0
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"