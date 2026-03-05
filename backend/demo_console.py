#!/usr/bin/env python3
"""
Демонстрация консоли LLCAR - показывает как выглядит интерфейс
"""

from console_ui import ConsoleUI, console, LOGO_ASCII
from rich.panel import Panel
from rich.align import Align
from rich import box
import time

def demo():
    """Демонстрация интерфейса"""
    ui = ConsoleUI()

    # Демо 1: Логотип и заголовок
    console.clear()
    console.print("\n[bold bright_cyan]╔══════════════════════════════════════════════════════════╗")
    console.print("[bold bright_cyan]║       ДЕМОНСТРАЦИЯ КОНСОЛИ LLCAR v2.1                   ║")
    console.print("[bold bright_cyan]╚══════════════════════════════════════════════════════════╝\n")

    ui.show_logo()
    time.sleep(2)

    # Демо 2: Главное меню
    console.print("\n[bold bright_cyan]▸ Главное меню[/bold bright_cyan]\n")
    ui.show_main_menu()
    console.print("\n[dim]Нажмите Enter для продолжения...[/dim]")
    input()

    # Демо 3: Настройка источников
    console.clear()
    console.print("\n[bold bright_cyan]▸ Настройка источников[/bold bright_cyan]\n")

    # Добавим тестовые данные
    ui.download_stats['telegram']['downloaded'] = 54
    ui.download_stats['telegram']['total_size'] = 5 * 1024 * 1024 * 1024  # 5 GB
    ui.download_stats['telegram']['errors'] = 2

    ui.download_stats['web']['downloaded'] = 12
    ui.download_stats['web']['total_size'] = 250 * 1024 * 1024  # 250 MB
    ui.download_stats['web']['errors'] = 0

    ui.show_sources_config()
    console.print("\n[dim]Нажмите Enter для продолжения...[/dim]")
    input()

    # Демо 4: Статистика
    console.clear()
    console.print("\n[bold bright_cyan]▸ Статистика загрузок[/bold bright_cyan]\n")

    ui.show_statistics({
        'organized': 66,
    })
    console.print("\n[dim]Нажмите Enter для продолжения...[/dim]")
    input()

    # Демо 5: Прогресс загрузки
    console.clear()
    ui.show_logo()
    console.print("\n[bold bright_cyan]▸ Пример загрузки файла[/bold bright_cyan]\n")

    ui.show_download_progress(
        'telegram',
        'Volkswagen Golf III Vento (1991-1997).pdf',
        75
    )

    time.sleep(2)

    # Финал
    console.clear()
    ui.show_logo()
    console.print("\n" + "═" * 70)
    console.print(Align.center(
        "[bold bright_green]✓ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА[/bold bright_green]"
    ))
    console.print("═" * 70 + "\n")

    console.print(Panel(
        "[bold bright_cyan]Консоль готова к использованию![/bold bright_cyan]\n\n"
        "Запустите: [bold white]python -X utf8 console_ui.py[/bold white]\n"
        "Или: [bold white]start_console.bat[/bold white]\n\n"
        "[dim]Все функции интегрированы и готовы к работе[/dim]",
        style="on #0a0a0a",
        border_style="bright_green",
        box=box.DOUBLE
    ))

    console.print()

if __name__ == '__main__':
    demo()
