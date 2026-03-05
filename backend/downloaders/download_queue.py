"""
═══════════════════════════════════════════════════════════════════════════════
    downloaders/download_queue.py — очередь с паузой/возобновлением
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
import time
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Callable

logger = logging.getLogger(__name__)


class DownloadStatus(str, Enum):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class DownloadPriority(int, Enum):
    LOW = 0
    NORMAL = 5
    HIGH = 10
    URGENT = 20


@dataclass
class DownloadTask:
    """Одна задача на скачивание"""
    id: str                      # Уникальный ID
    source: str                  # 'telegram', 'web', 'github'
    channel: str = ''            # Канал / URL
    message_id: int = 0          # ID сообщения (для Telegram)
    url: str = ''                # URL (для web/github)
    filename: str = ''
    expected_size: int = 0
    downloaded_size: int = 0
    status: DownloadStatus = DownloadStatus.PENDING
    priority: int = DownloadPriority.NORMAL
    error_message: str = ''
    retries: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: float = 0
    completed_at: float = 0
    local_path: str = ''

    @property
    def progress_pct(self) -> float:
        if self.expected_size <= 0:
            return 0
        return min(100.0, self.downloaded_size / self.expected_size * 100)

    @property
    def is_active(self) -> bool:
        return self.status in (DownloadStatus.PENDING, DownloadStatus.DOWNLOADING)


class DownloadQueue:
    """
    Очередь загрузок с паузой, возобновлением, приоритетами.

    ФИЧИ (из telegram-files):
        ✅ Пауза / возобновление отдельных файлов
        ✅ Пауза / возобновление всей очереди
        ✅ Приоритеты (urgent > high > normal > low)
        ✅ Автоматический retry при ошибках
        ✅ Персистентность (сохраняется на диск)
        ✅ Параллельная загрузка (N воркеров)
        ✅ Callback для отслеживания прогресса

    Использование:
        queue = DownloadQueue(db_path=Path('./data/queue.json'))

        # Добавляем задачи
        queue.add_task(DownloadTask(
            id='tg_123_456',
            source='telegram',
            channel='avtomanualy',
            message_id=456,
            filename='manual.pdf',
            expected_size=15_000_000,
        ))

        # Запускаем обработку
        await queue.start(download_fn=my_download_function)

        # Пауза одного файла
        queue.pause_task('tg_123_456')

        # Пауза всего
        queue.pause_all()

        # Возобновление
        queue.resume_all()
    """

    def __init__(
        self,
        db_path: Path = Path('./data/queue.json'),
        max_workers: int = 2,
        auto_save_interval: int = 10,
    ):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.auto_save_interval = auto_save_interval

        self._tasks: Dict[str, DownloadTask] = {}
        self._lock = asyncio.Lock()
        self._paused = False
        self._running = False
        self._workers: List[asyncio.Task] = []

        # Callbacks
        self._on_progress: Optional[Callable] = None
        self._on_complete: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

        self._load()

    # ── Персистентность ──────────────────────────────────────────

    def _load(self):
        """Загружает очередь с диска (восстановление после перезапуска)"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for task_data in data.get('tasks', []):
                    task = DownloadTask(**task_data)
                    # Восстанавливаем прерванные загрузки
                    if task.status == DownloadStatus.DOWNLOADING:
                        task.status = DownloadStatus.PENDING
                    self._tasks[task.id] = task

                self._paused = data.get('paused', False)

                active = sum(1 for t in self._tasks.values() if t.is_active)
                logger.info(
                    f"Очередь загружена: {len(self._tasks)} задач, "
                    f"{active} активных"
                )
            except Exception as e:
                logger.warning(f"Ошибка загрузки очереди: {e}")

    def _save(self):
        """Сохраняет очередь на диск"""
        try:
            data = {
                'tasks': [asdict(t) for t in self._tasks.values()],
                'paused': self._paused,
                'saved_at': time.time(),
            }
            tmp = self.db_path.with_suffix('.json.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1, default=str)
            tmp.replace(self.db_path)
        except Exception as e:
            logger.warning(f"Ошибка сохранения очереди: {e}")

    # ── Управление задачами ──────────────────────────────────────

    def add_task(self, task: DownloadTask) -> str:
        """Добавляет задачу в очередь"""
        if task.id in self._tasks:
            existing = self._tasks[task.id]
            if existing.status == DownloadStatus.COMPLETED:
                return task.id  # Уже скачано
            if existing.status == DownloadStatus.FAILED:
                existing.status = DownloadStatus.PENDING
                existing.retries = 0
                return task.id

        self._tasks[task.id] = task
        logger.debug(f"Задача: {task.filename}")
        return task.id

    def add_tasks(self, tasks: List[DownloadTask]) -> int:
        """Добавляет несколько задач, возвращает кол-во добавленных"""
        added = 0
        for task in tasks:
            if task.id not in self._tasks:
                self._tasks[task.id] = task
                added += 1
            elif self._tasks[task.id].status == DownloadStatus.FAILED:
                self._tasks[task.id].status = DownloadStatus.PENDING
                added += 1
        self._save()
        return added

    def pause_task(self, task_id: str):
        """Ставит на паузу одну задачу"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.status in (DownloadStatus.PENDING, DownloadStatus.DOWNLOADING):
                task.status = DownloadStatus.PAUSED
                logger.info(f"Пауза: {task.filename}")
                self._save()

    def resume_task(self, task_id: str):
        """Снимает с паузы одну задачу"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.status == DownloadStatus.PAUSED:
                task.status = DownloadStatus.PENDING
                logger.info(f"Возобновлено: {task.filename}")
                self._save()

    def cancel_task(self, task_id: str):
        """Отменяет задачу"""
        if task_id in self._tasks:
            self._tasks[task_id].status = DownloadStatus.CANCELLED
            self._save()

    def pause_all(self):
        """Ставит на паузу ВСЮ очередь"""
        self._paused = True
        for task in self._tasks.values():
            if task.status == DownloadStatus.PENDING:
                task.status = DownloadStatus.PAUSED
        logger.info("Вся очередь на паузе")
        self._save()

    def resume_all(self):
        """Снимает паузу со всей очереди"""
        self._paused = False
        for task in self._tasks.values():
            if task.status == DownloadStatus.PAUSED:
                task.status = DownloadStatus.PENDING
        logger.info("Очередь возобновлена")
        self._save()

    def set_priority(self, task_id: str, priority: int):
        """Меняет приоритет задачи"""
        if task_id in self._tasks:
            self._tasks[task_id].priority = priority

    # ── Получение следующей задачи ───────────────────────────────

    def _next_task(self) -> Optional[DownloadTask]:
        """Возвращает задачу с наивысшим приоритетом"""
        if self._paused:
            return None

        pending = [
            t for t in self._tasks.values()
            if t.status == DownloadStatus.PENDING
        ]

        if not pending:
            return None

        # Сортируем: сначала по приоритету (↓), потом по времени создания (↑)
        pending.sort(key=lambda t: (-t.priority, t.created_at))
        return pending[0]

    # ── Запуск обработки ─────────────────────────────────────────

    async def start(
        self,
        download_fn: Callable,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """
        Запускает обработку очереди.

        Args:
            download_fn:  async fn(task: DownloadTask) -> bool
            on_progress:  fn(task_id, downloaded, total)
            on_complete:  fn(task: DownloadTask)
            on_error:     fn(task: DownloadTask, error: str)
        """
        self._on_progress = on_progress
        self._on_complete = on_complete
        self._on_error = on_error
        self._running = True

        logger.info(f"Очередь запущена ({self.max_workers} воркера)")

        # Запускаем N воркеров
        self._workers = [
            asyncio.create_task(self._worker(i, download_fn))
            for i in range(self.max_workers)
        ]

        # Автосохранение
        saver = asyncio.create_task(self._auto_saver())

        try:
            await asyncio.gather(*self._workers)
        finally:
            self._running = False
            saver.cancel()
            self._save()

    async def stop(self):
        """Останавливает очередь"""
        self._running = False
        for w in self._workers:
            w.cancel()
        self._save()

    async def _worker(self, worker_id: int, download_fn: Callable):
        """Один воркер — берёт задачи из очереди и скачивает"""
        while self._running:
            async with self._lock:
                task = self._next_task()
                if task:
                    task.status = DownloadStatus.DOWNLOADING
                    task.started_at = time.time()

            if not task:
                await asyncio.sleep(1)
                continue

            logger.info(
                f"  [W{worker_id}] {task.filename} "
                f"(приоритет: {task.priority})"
            )

            try:
                success = await download_fn(task)

                if success:
                    task.status = DownloadStatus.COMPLETED
                    task.completed_at = time.time()
                    logger.info(f"  [W{worker_id}] Завершено: {task.filename}")
                    if self._on_complete:
                        self._on_complete(task)
                else:
                    task.retries += 1
                    if task.retries >= task.max_retries:
                        task.status = DownloadStatus.FAILED
                        task.error_message = 'Превышено кол-во попыток'
                        if self._on_error:
                            self._on_error(task, task.error_message)
                    else:
                        task.status = DownloadStatus.PENDING
                        logger.info(
                            f"  [W{worker_id}] Retry {task.retries}/"
                            f"{task.max_retries}: {task.filename}"
                        )
                        await asyncio.sleep(2 ** task.retries)

            except asyncio.CancelledError:
                task.status = DownloadStatus.PAUSED
                raise
            except Exception as e:
                task.retries += 1
                task.error_message = str(e)

                if task.retries >= task.max_retries:
                    task.status = DownloadStatus.FAILED
                    logger.error(f"  [W{worker_id}] Ошибка {task.filename}: {e}")
                else:
                    task.status = DownloadStatus.PENDING
                    await asyncio.sleep(2 ** task.retries)

    async def _auto_saver(self):
        """Периодически сохраняет очередь"""
        while self._running:
            await asyncio.sleep(self.auto_save_interval)
            self._save()

    # ── Информация ───────────────────────────────────────────────

    def get_stats(self) -> Dict:
        counts = {}
        for status in DownloadStatus:
            counts[status.value] = sum(
                1 for t in self._tasks.values()
                if t.status == status
            )

        total_size = sum(
            t.expected_size for t in self._tasks.values()
            if t.status == DownloadStatus.COMPLETED
        )

        return {
            'total': len(self._tasks),
            'paused_global': self._paused,
            'total_completed_size': total_size,
            **counts,
        }

    def get_active_tasks(self) -> List[DownloadTask]:
        return [t for t in self._tasks.values() if t.is_active]

    def get_all_tasks(self) -> List[DownloadTask]:
        return sorted(
            self._tasks.values(),
            key=lambda t: (-t.priority, t.created_at),
        )

    def clear_completed(self):
        """Очищает завершённые задачи"""
        to_remove = [
            tid for tid, t in self._tasks.items()
            if t.status in (DownloadStatus.COMPLETED, DownloadStatus.CANCELLED)
        ]
        for tid in to_remove:
            del self._tasks[tid]
        self._save()
