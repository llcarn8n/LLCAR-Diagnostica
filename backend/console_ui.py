#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
     🎮 LLCAR Console UI v3 — с просмотром каналов и выбором файлов
═══════════════════════════════════════════════════════════════════════════════

НОВОЕ:
    ✅ Просмотр содержимого Telegram-канала (список файлов)
    ✅ Интерактивный выбор файлов для скачивания
    ✅ Реальная интеграция с main_v2 и TelegramDownloader
    ✅ Прогресс скачивания в реальном времени
    ✅ Чтение конфигурации из config.py
    ✅ Рабочие пункты меню (не заглушки)
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Set
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn,
        TextColumn, TimeRemainingColumn, DownloadColumn,
    )
    from rich.align import Align
    from rich.style import Style
    from rich import box
except ImportError:
    print("❌ Установите rich: pip install rich>=13.7.0")
    sys.exit(1)

# ═══ Цветовая схема ═══
NEON_CYAN = "#00FFFF"
GLOW_CYAN = "bold bright_cyan"
DARK_PANEL = "#0a0a0a"

console = Console()

LOGO_ASCII = r"""[bold bright_cyan]
╔══════════════════════════════════════════════════════════════╗
║     ██╗     ██╗      ██████╗ █████╗ ██████╗                 ║
║     ██║     ██║     ██╔════╝██╔══██╗██╔══██╗                ║
║     ██║     ██║     ██║     ███████║██████╔╝                ║
║     ██║     ██║     ██║     ██╔══██║██╔══██╗                ║
║     ███████╗███████╗╚██████╗██║  ██║██║  ██║                ║
║     ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝                ║
║           L O N G   L I F E   C A R   M A N U A L S        ║
╚══════════════════════════════════════════════════════════════╝
[/bold bright_cyan]"""


class ConsoleUI:
    """Интерактивная консоль с просмотром каналов и выбором файлов"""

    def __init__(self):
        self.console = Console()
        self.running = False

        # Загружаем конфиг
        self._load_config()

        # Telegram клиент (создаётся по запросу)
        self._tg_downloader = None

        # Очередь загрузок и система тегов
        try:
            from downloaders.download_queue import DownloadQueue
            self._queue = DownloadQueue(db_path=Path('./data/queue.json'))
        except ImportError:
            self._queue = None

        try:
            from utils.file_tagger import FileTagger
            self._tagger = FileTagger(db_path=Path('./data/tags.json'))
        except ImportError:
            self._tagger = None

    # ══════════════════════════════════════════════════════════════════
    #  КОНФИГУРАЦИЯ
    # ══════════════════════════════════════════════════════════════════

    def _load_config(self):
        """Загружает конфиг из config.py"""
        try:
            from config import (
                TELEGRAM_CHANNELS, TELEGRAM_API_ID, TELEGRAM_API_HASH,
                TELEGRAM_PHONE, BASE_DOWNLOAD_PATH, ALLOWED_EXTENSIONS,
                KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE, MAX_FILE_SIZE_MB,
                TELEGRAM_MESSAGE_LIMIT,
            )
            self.cfg = {
                'channels': TELEGRAM_CHANNELS,
                'api_id': TELEGRAM_API_ID,
                'api_hash': TELEGRAM_API_HASH,
                'phone': TELEGRAM_PHONE,
                'download_path': BASE_DOWNLOAD_PATH,
                'extensions': ALLOWED_EXTENSIONS,
                'kw_include': KEYWORDS_INCLUDE,
                'kw_exclude': KEYWORDS_EXCLUDE,
                'max_size_mb': MAX_FILE_SIZE_MB,
                'msg_limit': TELEGRAM_MESSAGE_LIMIT,
            }
            self.config_loaded = True
        except ImportError as e:
            self.console.print(f"[yellow]⚠️ config.py: {e}[/yellow]")
            self.cfg = {}
            self.config_loaded = False

    async def _get_tg_downloader(self):
        """Лениво создаёт и подключает Telegram загрузчик"""
        if self._tg_downloader is not None:
            return self._tg_downloader

        if not self.config_loaded:
            self.console.print("[red]❌ config.py не загружен![/red]")
            return None

        from downloaders.telegram_downloader import TelegramDownloader

        self._tg_downloader = TelegramDownloader(
            api_id=self.cfg['api_id'],
            api_hash=self.cfg['api_hash'],
            phone=self.cfg['phone'],
            download_path=self.cfg['download_path'] / '_telegram_raw',
        )

        self.console.print("[dim]Подключение к Telegram...[/dim]")
        if not await self._tg_downloader.connect():
            self.console.print("[red]❌ Не удалось подключиться к Telegram![/red]")
            self._tg_downloader = None
            return None

        return self._tg_downloader

    async def _disconnect_tg(self):
        if self._tg_downloader:
            await self._tg_downloader.disconnect()
            self._tg_downloader = None

    # ══════════════════════════════════════════════════════════════════
    #  ОТРИСОВКА
    # ══════════════════════════════════════════════════════════════════

    def _show_logo(self):
        self.console.clear()
        self.console.print(Panel(
            Align.center(LOGO_ASCII),
            style=f"on {DARK_PANEL}",
            border_style=GLOW_CYAN,
            box=box.DOUBLE,
        ))

    def _show_main_menu(self):
        self._show_logo()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(
            f"  [dim]{now}[/dim]   "
            f"[bright_cyan]Каналов: {len(self.cfg.get('channels', []))}[/bright_cyan]"
        )
        self.console.print()

        menu = Table(show_header=False, box=None, padding=(0, 2))
        menu.add_column(style=GLOW_CYAN)
        menu.add_row("┌───────────────────────────────────────────────────┐")
        menu.add_row("│  [bold cyan]1[/] ▸ 📋  Просмотр содержимого канала           │")
        menu.add_row("│  [bold cyan]2[/] ▸ 📥  Скачать выбранные файлы               │")
        menu.add_row("│  [bold cyan]3[/] ▸ 🔗  Скачать по Telegram-ссылке            │")
        menu.add_row("│  [bold cyan]4[/] ▸ 🚀  Автоматическая загрузка (всё)         │")
        menu.add_row("│  [bold cyan]5[/] ▸ ⏸️   Управление очередью загрузок          │")
        menu.add_row("│  [bold cyan]6[/] ▸ 🏷️   Теги и поиск файлов                  │")
        menu.add_row("│  [bold cyan]7[/] ▸ 📊  Статистика                            │")
        menu.add_row("│  [bold cyan]8[/] ▸ ⚙️   Настройки и источники                │")
        menu.add_row("│  [bold cyan]0[/] ▸ 🚪  Выход                                │")
        menu.add_row("└───────────────────────────────────────────────────┘")

        self.console.print(Panel(
            menu,
            title="[bold bright_cyan]╣ ГЛАВНОЕ МЕНЮ ╠[/]",
            border_style=GLOW_CYAN, box=box.DOUBLE,
        ))
        self.console.print()

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 1: ПРОСМОТР СОДЕРЖИМОГО КАНАЛА
    # ══════════════════════════════════════════════════════════════════

    async def browse_channel(self):
        """
        Показывает содержимое Telegram-канала:
            — список файлов с размерами
            — пометка ✅ / ⬜ (скачано / не скачано)
            — фильтры по расширению и ключевым словам
        """
        self._show_logo()
        self.console.print(Panel(
            "[bold bright_cyan]📋 ПРОСМОТР СОДЕРЖИМОГО КАНАЛА[/]",
            border_style=GLOW_CYAN,
        ))

        channels = self.cfg.get('channels', [])
        if not channels:
            self.console.print("[red]Нет каналов в config.py![/red]")
            input("\nEnter...")
            return None

        # Выбор канала
        self.console.print("\n[bright_cyan]Доступные каналы:[/]")
        for i, ch in enumerate(channels, 1):
            self.console.print(f"  [cyan]{i}[/]. @{ch}")
        self.console.print(f"  [cyan]{len(channels)+1}[/]. Ввести вручную")
        self.console.print()

        choice = IntPrompt.ask(
            "Номер канала",
            default=1,
        )

        if 1 <= choice <= len(channels):
            channel = channels[choice - 1]
        elif choice == len(channels) + 1:
            channel = Prompt.ask("Введите @username канала").lstrip('@')
        else:
            return None

        # Подключаемся
        dl = await self._get_tg_downloader()
        if not dl:
            input("\nEnter...")
            return None

        # Сканируем
        self.console.print()
        with Progress(
            SpinnerColumn(style=GLOW_CYAN),
            TextColumn("[bold cyan]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Сканирование @{channel}...", total=None)

            files = await dl.list_channel_files(
                channel_username=channel,
                allowed_extensions=self.cfg.get('extensions'),
                max_size_mb=self.cfg.get('max_size_mb', 500),
                message_limit=self.cfg.get('msg_limit'),
                keywords_include=self.cfg.get('kw_include'),
                keywords_exclude=self.cfg.get('kw_exclude'),
            )
            progress.remove_task(task)

        if not files:
            self.console.print("[yellow]Файлы не найдены[/yellow]")
            input("\nEnter...")
            return None

        # Показываем таблицу
        self._display_file_list(files, channel)
        return (channel, files)

    def _display_file_list(self, files, channel: str):
        """Отображает таблицу файлов"""
        table = Table(
            title=f"[bold cyan]@{channel} — {len(files)} файлов[/]",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            border_style=NEON_CYAN,
        )
        table.add_column("№", style="dim", width=5, justify="right")
        table.add_column("Ст.", width=3)
        table.add_column("ID", style="dim cyan", width=8)
        table.add_column("Имя файла", style="bright_white", min_width=30, max_width=55)
        table.add_column("Размер", style="yellow", width=10, justify="right")
        table.add_column("Расш.", style="dim", width=6)
        table.add_column("Дата", style="dim", width=12)

        for i, f in enumerate(files, 1):
            status = "[green]✅[/]" if f.is_downloaded else "[dim]⬜[/]"
            date_str = f.date.strftime('%Y-%m-%d') if f.date else ''

            name = f.filename
            if len(name) > 55:
                name = name[:52] + '...'

            table.add_row(
                str(i),
                status,
                str(f.message_id),
                name,
                f.size_str,
                f.extension,
                date_str,
            )

        self.console.print()
        self.console.print(table)

        # Сводка
        downloaded = sum(1 for f in files if f.is_downloaded)
        new = len(files) - downloaded
        total_size = sum(f.size for f in files if not f.is_downloaded)

        self.console.print()
        self.console.print(
            f"  [green]✅ Скачано: {downloaded}[/]  "
            f"[cyan]⬜ Новых: {new}[/]  "
            f"[yellow]💾 Нескачанный объём: "
            f"{self._fmt_size(total_size)}[/]"
        )

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 2: ВЫБОР И СКАЧИВАНИЕ
    # ══════════════════════════════════════════════════════════════════

    async def download_selected(self):
        """
        Интерактивный выбор и скачивание файлов:
            1. Просматриваем канал
            2. Пользователь вводит номера файлов
            3. Скачиваем только выбранные
        """
        # Сначала показываем канал
        result = await self.browse_channel()
        if not result:
            return

        channel, files = result

        # Фильтруем только нескачанные
        new_files = [f for f in files if not f.is_downloaded]
        if not new_files:
            self.console.print("\n[green]✅ Все файлы уже скачаны![/green]")
            input("\nEnter...")
            return

        self.console.print()
        self.console.print(Panel(
            "[bold cyan]Выберите файлы для скачивания[/]\n\n"
            "  [cyan]all[/]    — скачать все новые\n"
            "  [cyan]1,3,5[/]  — скачать файлы №1, №3, №5\n"
            "  [cyan]1-10[/]   — скачать файлы с №1 по №10\n"
            "  [cyan]0[/]      — отмена",
            border_style=NEON_CYAN,
        ))

        selection = Prompt.ask("[cyan]Выбор[/]", default="0")

        if selection.strip() == '0':
            return

        # Парсим выбор
        selected_indices = self._parse_selection(selection, len(files))

        if not selected_indices:
            self.console.print("[yellow]Ничего не выбрано[/yellow]")
            input("\nEnter...")
            return

        # Собираем message_id выбранных файлов
        selected_files = [files[i] for i in selected_indices]
        # Фильтруем уже скачанные
        to_download = [f for f in selected_files if not f.is_downloaded]

        if not to_download:
            self.console.print("[green]Все выбранные файлы уже скачаны![/]")
            input("\nEnter...")
            return

        total_size = sum(f.size for f in to_download)
        self.console.print(
            f"\n[cyan]Будет скачано: {len(to_download)} файлов "
            f"({self._fmt_size(total_size)})[/]"
        )

        if not Confirm.ask("Начать скачивание?", default=True):
            return

        # Скачиваем
        dl = await self._get_tg_downloader()
        if not dl:
            return

        message_ids = [f.message_id for f in to_download]

        self.console.print()
        with Progress(
            SpinnerColumn(style=GLOW_CYAN),
            TextColumn("[bold]{task.description}[/]"),
            BarColumn(complete_style="cyan"),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                "Скачивание...",
                total=len(message_ids),
            )

            def on_progress(fname, current, total):
                progress.update(task, description=f"📄 {fname[:40]}")

            results = await dl.download_selected_files(
                channel_username=channel,
                message_ids=message_ids,
                progress_callback=on_progress,
            )

            progress.update(task, completed=len(message_ids))

        self.console.print(
            f"\n[green]✅ Скачано: {len(results)} файлов[/]"
        )
        input("\nEnter...")

    def _parse_selection(self, text: str, total: int) -> List[int]:
        """
        Парсит пользовательский ввод выбора файлов.
            'all' → все
            '1,3,5' → [0, 2, 4]
            '1-10' → [0..9]
            '1-5,8,10-12' → [0..4, 7, 9..11]
        """
        text = text.strip().lower()
        if text == 'all':
            return list(range(total))

        indices = set()
        for part in text.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    a, b = part.split('-', 1)
                    a, b = int(a.strip()), int(b.strip())
                    for idx in range(a, b + 1):
                        if 1 <= idx <= total:
                            indices.add(idx - 1)
                except ValueError:
                    pass
            else:
                try:
                    idx = int(part)
                    if 1 <= idx <= total:
                        indices.add(idx - 1)
                except ValueError:
                    pass

        return sorted(indices)

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 3: АВТОМАТИЧЕСКАЯ ЗАГРУЗКА
    # ══════════════════════════════════════════════════════════════════

    async def run_auto_download(self):
        """Запуск полностью автоматической загрузки через main_v2"""
        self._show_logo()
        self.console.print(Panel(
            "[bold cyan]🚀 АВТОМАТИЧЕСКАЯ ЗАГРУЗКА[/]\n\n"
            "Будут обработаны все источники из config.py:\n"
            "  📱 Telegram каналы\n"
            "  🌐 Web-сайты\n"
            "  🐙 GitHub\n"
            "  🧲 Торренты",
            border_style=GLOW_CYAN,
        ))

        channels = self.cfg.get('channels', [])
        self.console.print(
            f"\n[cyan]Telegram каналов: {len(channels)}[/]"
        )
        for ch in channels:
            self.console.print(f"  • @{ch}")

        if not Confirm.ask("\nЗапустить загрузку?", default=True):
            return

        # Отключаем свой TG-клиент чтобы не было конфликта
        await self._disconnect_tg()

        self.console.print(
            "\n[dim]Запуск main_v2.py...[/dim]\n"
        )

        # Запускаем main_v2 напрямую
        try:
            # Способ 1: Импорт и вызов
            from main_v2 import main as main_v2_run
            await main_v2_run()
        except ImportError:
            # Способ 2: Subprocess
            self.console.print("[yellow]Запуск через subprocess...[/]")
            import subprocess
            proc = subprocess.Popen(
                [sys.executable, '-X', 'utf8', 'main_v2.py'],
                cwd=str(Path(__file__).parent),
            )
            proc.wait()

        self.console.print("\n[green]✅ Загрузка завершена[/]")
        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 4: СТАТИСТИКА
    # ══════════════════════════════════════════════════════════════════

    async def show_statistics(self):
        """Показывает реальную статистику из файловой системы"""
        self._show_logo()

        download_path = self.cfg.get('download_path', Path('./downloads'))

        # Считаем файлы на диске
        total_files = 0
        total_size = 0
        by_ext: Dict[str, int] = {}

        if download_path.exists():
            for fp in download_path.rglob('*'):
                if fp.is_file():
                    total_files += 1
                    sz = fp.stat().st_size
                    total_size += sz
                    ext = fp.suffix.lower()
                    by_ext[ext] = by_ext.get(ext, 0) + 1

        # Таблица
        table = Table(
            title="[bold cyan]📊 Статистика библиотеки[/]",
            box=box.ROUNDED, border_style=NEON_CYAN,
        )
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="bright_white", justify="right")

        table.add_row("Всего файлов", str(total_files))
        table.add_row("Общий размер", self._fmt_size(total_size))
        table.add_row("Папка", str(download_path))

        self.console.print(table)

        if by_ext:
            ext_table = Table(
                title="[cyan]По типам файлов[/]",
                box=box.SIMPLE, border_style="dim",
            )
            ext_table.add_column("Расширение", style="cyan")
            ext_table.add_column("Кол-во", justify="right")

            for ext, count in sorted(
                by_ext.items(), key=lambda x: -x[1]
            )[:10]:
                ext_table.add_row(ext or '(нет)', str(count))

            self.console.print()
            self.console.print(ext_table)

        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 5: НАСТРОЙКИ
    # ══════════════════════════════════════════════════════════════════

    async def show_settings(self):
        """Показывает текущие настройки из config.py"""
        self._show_logo()

        table = Table(
            title="[bold cyan]⚙️ Текущая конфигурация[/]",
            box=box.ROUNDED, border_style=NEON_CYAN,
        )
        table.add_column("Параметр", style="cyan", width=25)
        table.add_column("Значение", style="bright_white")

        table.add_row(
            "Telegram каналы",
            ', '.join(f'@{c}' for c in self.cfg.get('channels', [])),
        )
        table.add_row(
            "Расширения",
            ', '.join(self.cfg.get('extensions', [])),
        )
        table.add_row(
            "Макс. размер файла",
            f"{self.cfg.get('max_size_mb', '?')} МБ",
        )
        table.add_row(
            "Лимит сообщений",
            str(self.cfg.get('msg_limit', 'Без ограничений')),
        )
        table.add_row(
            "Папка загрузок",
            str(self.cfg.get('download_path', '?')),
        )

        kw_inc = self.cfg.get('kw_include')
        if kw_inc:
            table.add_row("Ключевые слова (+)", ', '.join(kw_inc[:5]))

        kw_exc = self.cfg.get('kw_exclude')
        if kw_exc:
            table.add_row("Ключевые слова (-)", ', '.join(kw_exc[:5]))

        self.console.print(table)
        self.console.print(
            "\n[dim]Для изменения настроек отредактируйте config.py[/dim]"
        )
        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 5: УПРАВЛЕНИЕ ОЧЕРЕДЬЮ ЗАГРУЗОК
    # ══════════════════════════════════════════════════════════════════

    async def manage_queue(self):
        """Управление очередью загрузок с паузой/возобновлением"""
        if not self._queue:
            self.console.print("[red]DownloadQueue не загружен[/]")
            input("\nEnter...")
            return

        self._show_logo()

        from downloaders.download_queue import DownloadStatus

        stats = self._queue.get_stats()

        table = Table(
            title="[cyan]📋 Очередь загрузок[/]",
            box=box.ROUNDED, border_style=NEON_CYAN,
        )
        table.add_column("Статус", width=12)
        table.add_column("Кол-во", justify="right")

        status_icons = {
            'pending': '⏳ Ожидание',
            'downloading': '📥 Загрузка',
            'paused': '⏸️ Пауза',
            'completed': '✅ Готово',
            'failed': '❌ Ошибка',
        }

        for status, label in status_icons.items():
            count = stats.get(status, 0)
            style = 'green' if status == 'completed' else 'yellow' if status == 'pending' else 'red' if status == 'failed' else ''
            table.add_row(label, f"[{style}]{count}[/]")

        self.console.print(table)

        paused_text = "[red]⏸️ ПАУЗА[/]" if stats['paused_global'] else "[green]▶️ АКТИВНА[/]"
        self.console.print(f"\n  Очередь: {paused_text}")

        # Показываем активные задачи
        active = self._queue.get_active_tasks()
        if active:
            self.console.print(f"\n[cyan]Активные задачи ({len(active)}):[/]")
            for i, task in enumerate(active[:15], 1):
                status_icon = '📥' if task.status == DownloadStatus.DOWNLOADING else '⏳'
                self.console.print(
                    f"  {status_icon} {i}. {task.filename[:50]} "
                    f"({task.progress_pct:.0f}%)"
                )

        self.console.print(Panel(
            "[cyan]p[/] — пауза всего  │  [cyan]r[/] — возобновить  │  "
            "[cyan]c[/] — очистить готовые  │  [cyan]0[/] — назад",
            border_style="dim",
        ))

        action = Prompt.ask("[cyan]Действие[/]", default="0")

        if action == 'p':
            self._queue.pause_all()
            self.console.print("[yellow]⏸️ Очередь на паузе[/]")
        elif action == 'r':
            self._queue.resume_all()
            self.console.print("[green]▶️ Очередь возобновлена[/]")
        elif action == 'c':
            self._queue.clear_completed()
            self.console.print("[dim]Очищено[/dim]")

        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 6: ТЕГИ И ПОИСК ФАЙЛОВ
    # ══════════════════════════════════════════════════════════════════

    async def manage_tags(self):
        """Управление тегами и поиск файлов"""
        if not self._tagger:
            self.console.print("[red]FileTagger не загружен[/]")
            input("\nEnter...")
            return

        self._show_logo()
        self.console.print(Panel(
            "[bold cyan]🏷️ ТЕГИ И ПОИСК ФАЙЛОВ[/]",
            border_style=GLOW_CYAN,
        ))

        self.console.print(
            "  [cyan]1[/] — Показать все теги\n"
            "  [cyan]2[/] — Поиск по тегу\n"
            "  [cyan]3[/] — Авто-теги для всех файлов\n"
            "  [cyan]0[/] — Назад"
        )

        choice = Prompt.ask("[cyan]Выбор[/]", default="0")

        if choice == '1':
            all_tags = self._tagger.get_all_tags()
            if all_tags:
                table = Table(title="[cyan]Все теги[/]", box=box.SIMPLE)
                table.add_column("Тег", style="cyan")
                table.add_column("Файлов", justify="right")
                for tag, count in list(all_tags.items())[:30]:
                    table.add_row(tag, str(count))
                self.console.print(table)
            else:
                self.console.print("[dim]Тегов пока нет[/]")

        elif choice == '2':
            query = Prompt.ask("[cyan]Введите тег для поиска[/]")
            files = self._tagger.find_by_tags([query])
            if files:
                self.console.print(f"\n[green]Найдено {len(files)} файлов:[/]")
                for f in files[:20]:
                    tags = ', '.join(self._tagger.get_tags(f))
                    self.console.print(f"  📄 {f}")
                    self.console.print(f"      [dim]{tags}[/]")
            else:
                self.console.print("[yellow]Ничего не найдено[/]")

        elif choice == '3':
            download_path = self.cfg.get('download_path', Path('./downloads'))
            all_files = [
                fp.name for fp in download_path.rglob('*') if fp.is_file()
            ]
            count = self._tagger.auto_tag_all(all_files)
            self.console.print(f"[green]✅ Авто-теги для {count} файлов[/]")

        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  ПУНКТ 3: СКАЧИВАНИЕ ПО TELEGRAM-ССЫЛКЕ
    # ══════════════════════════════════════════════════════════════════

    async def download_by_link(self):
        """Скачивание по Telegram-ссылке"""
        self._show_logo()
        self.console.print(Panel(
            "[bold cyan]🔗 СКАЧИВАНИЕ ПО ССЫЛКЕ[/]\n\n"
            "Поддерживаемые форматы:\n"
            "  • https://t.me/channel/12345\n"
            "  • https://t.me/c/1234567890/12345\n"
            "  • Несколько ссылок через пробел или Enter",
            border_style=GLOW_CYAN,
        ))

        self.console.print(
            "\nВставьте ссылку (или несколько, по одной на строку).\n"
            "Пустая строка — завершить ввод:\n"
        )

        # Собираем ссылки (многострочный ввод)
        lines = []
        while True:
            line = input("  > ").strip()
            if not line:
                break
            lines.append(line)

        if not lines:
            return

        text = ' '.join(lines)

        # Парсим
        from downloaders.telegram_downloader import TelegramLinkParser
        parsed = TelegramLinkParser.parse_multiple(text)

        if not parsed:
            self.console.print("[yellow]Ссылки не распознаны[/]")
            input("\nEnter...")
            return

        self.console.print(
            f"\n[cyan]Распознано ссылок: {len(parsed)}[/]"
        )
        for p in parsed:
            ch = p.get('channel', p.get('channel_id', '?'))
            self.console.print(f"  • @{ch} #{p['message_id']}")

        if not Confirm.ask("\nСкачать?", default=True):
            return

        # Скачиваем
        dl = await self._get_tg_downloader()
        if not dl:
            return

        links = []
        for p in parsed:
            ch = p.get('channel', str(p.get('channel_id', '')))
            links.append(f"https://t.me/{ch}/{p['message_id']}")

        results = await dl.download_by_links(links)
        self.console.print(f"\n[green]✅ Скачано: {len(results)} файлов[/]")

        # Автотеги
        if self._tagger and results:
            for r in results:
                self._tagger.auto_tag(r['filename'])
            self._tagger.save()
            self.console.print("[dim]🏷️ Авто-теги добавлены[/]")

        input("\nEnter...")

    # ══════════════════════════════════════════════════════════════════
    #  УТИЛИТЫ
    # ══════════════════════════════════════════════════════════════════

    def _fmt_size(self, size_bytes: int) -> str:
        for unit in ('Б', 'КБ', 'МБ', 'ГБ'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"

    # ══════════════════════════════════════════════════════════════════
    #  ГЛАВНЫЙ ЦИКЛ
    # ══════════════════════════════════════════════════════════════════

    async def run(self):
        """Главный цикл консоли"""
        self.running = True

        while self.running:
            try:
                self._show_main_menu()

                choice = Prompt.ask(
                    "[bold cyan]Выберите[/]",
                    choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
                    default="1",
                )

                if choice == "0":
                    await self._disconnect_tg()
                    self.console.print("\n[cyan]👋 До встречи![/]\n")
                    self.running = False

                elif choice == "1":
                    result = await self.browse_channel()
                    if result:
                        # Предлагаем скачать
                        _, files = result
                        new = [f for f in files if not f.is_downloaded]
                        if new:
                            self.console.print()
                            if Confirm.ask(
                                f"[cyan]Скачать {len(new)} новых файлов?[/]",
                                default=False,
                            ):
                                # Переходим к выбору
                                await self._download_from_browse(result)
                    input("\nEnter...")

                elif choice == "2":
                    await self.download_selected()

                elif choice == "3":
                    await self.download_by_link()

                elif choice == "4":
                    await self.run_auto_download()

                elif choice == "5":
                    await self.manage_queue()

                elif choice == "6":
                    await self.manage_tags()

                elif choice == "7":
                    await self.show_statistics()

                elif choice == "8":
                    await self.show_settings()

            except KeyboardInterrupt:
                self.console.print(
                    "\n[yellow]⚠️ Прервано (Ctrl+C)[/yellow]\n"
                )
                await self._disconnect_tg()
                self.running = False

            except Exception as e:
                self.console.print(f"\n[red]❌ Ошибка: {e}[/red]\n")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
                input("Enter...")

    async def _download_from_browse(self, browse_result):
        """Скачать файлы после просмотра"""
        channel, files = browse_result
        new_files = [f for f in files if not f.is_downloaded]

        self.console.print(Panel(
            "[cyan]all[/] — все новые  │  "
            "[cyan]1,3,5[/] — по номерам  │  "
            "[cyan]1-10[/] — диапазон  │  "
            "[cyan]0[/] — отмена",
            border_style="dim cyan",
        ))

        selection = Prompt.ask("[cyan]Выбор[/]", default="all")
        if selection.strip() == '0':
            return

        selected_indices = self._parse_selection(selection, len(files))
        to_download = [
            files[i] for i in selected_indices
            if not files[i].is_downloaded
        ]

        if not to_download:
            self.console.print("[green]Нечего скачивать[/]")
            return

        dl = await self._get_tg_downloader()
        if not dl:
            return

        ids = [f.message_id for f in to_download]
        total_size = sum(f.size for f in to_download)

        self.console.print(
            f"\n[cyan]📥 Скачивание {len(ids)} файлов "
            f"({self._fmt_size(total_size)})...[/]\n"
        )

        results = await dl.download_selected_files(channel, ids)
        self.console.print(f"\n[green]✅ Скачано: {len(results)}[/]")


# ═══════════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    ui = ConsoleUI()
    await ui.run()


if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[dim]Выход...[/dim]")
        sys.exit(0)
