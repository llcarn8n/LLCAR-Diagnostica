#!/usr/bin/env python3
"""
LLCAR Diagnostica KB -- DeepSeek-OCR-2 Patch (Phase 2.5).

Применяет OCR-патч к изображениям с низкой уверенностью MinerU (confidence < 0.7).
Модель: deepseek-ai/DeepSeek-OCR-2 (Apache 2.0, ~16GB BF16, OCRBench ~864+)

Архитектура:
- deepseek_vl_v2 / DeepSeekOCR2
- Vision encoder: 12 слоёв, hidden_size=1280
- LLM: DeepseekV2 (MoE, 128 expert groups, multilingual)
- vocab_size: 129280 (CJK + Cyrillic + Latin)
- Вход: динамическое разрешение (0-6)x768x768 + 1x1024x1024
- Выход: Markdown / plaintext OCR

Зависимости (сверх базового окружения):
  pip install addict easydict matplotlib einops

Ограничения transformers 5.x:
  - LlamaFlashAttention2 удалена → патч в кеше HF modules (применён при установке)
  - is_torch_fx_available удалена → патч в кеше HF modules (применён при установке)
  - flash-attn НЕ установлен → используется eager attention (медленнее, но работает)

Usage:
  # Быстрый тест (только config):
  python scripts/ocr_patch.py --test-config

  # Патч одного изображения:
  python scripts/ocr_patch.py --image path/to/image.jpg --out output/

  # Пакетный патч из SQLite (confidence < threshold):
  python scripts/ocr_patch.py --db knowledge-base/kb.db --threshold 0.7 --gpu 0

Author: LLCAR Diagnostica team
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional

import torch

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_ID = "deepseek-ai/DeepSeek-OCR-2"

# Промпты для разных режимов
PROMPT_MARKDOWN = "<image>\n<|grounding|>Convert the document to markdown. "
PROMPT_FREE_OCR = "<image>\nFree OCR. "

# Порог confidence ниже которого запускается патч
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# GPU для модели (0 = первая карта; 1 = вторая карта если 0 занята)
DEFAULT_GPU_ID = 0

# Параметры инференса (режим "Gundam" — баланс скорость/качество)
DEFAULT_BASE_SIZE = 1024
DEFAULT_IMAGE_SIZE = 768
DEFAULT_CROP_MODE = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ocr_patch")


# ---------------------------------------------------------------------------
# Compatibility shims
# ---------------------------------------------------------------------------

def _patch_transformers_cache() -> None:
    """
    Проверяет и при необходимости применяет патчи к закешированным файлам
    DeepSeek-OCR-2 для совместимости с transformers >= 5.0.

    Проблемы:
    1. LlamaFlashAttention2 -- удалена из transformers 5.x
    2. is_torch_fx_available -- удалена из transformers 5.x

    Патч автоматически применяется к файлам в HF модуль-кеше.
    """
    import transformers

    hf_cache = Path.home() / ".cache" / "huggingface" / "modules" / "transformers_modules"
    model_slug = "deepseek_hyphen_ai" / Path("DeepSeek_hyphen_OCR_hyphen_2")
    model_cache = hf_cache / model_slug

    if not model_cache.exists():
        logger.debug("Кеш DeepSeek-OCR-2 не найден, патч не нужен (модель ещё не скачана)")
        return

    # Найдём все версии modeling_deepseekv2.py в кеше
    for f in model_cache.rglob("modeling_deepseekv2.py"):
        content = f.read_text(encoding="utf-8")
        changed = False

        # Патч 1: LlamaFlashAttention2 (идемпотентный — проверяем алиас)
        if (
            "LlamaFlashAttention2" in content
            and "LlamaFlashAttention2 = LlamaAttention" not in content
        ):
            content = content.replace(
                "from transformers.models.llama.modeling_llama import (\n"
                "    LlamaAttention,\n"
                "    LlamaFlashAttention2\n"
                ")",
                (
                    "from transformers.models.llama.modeling_llama import (\n"
                    "    LlamaAttention,\n"
                    ")\n"
                    "# LlamaFlashAttention2 removed in transformers>=5.0\n"
                    "LlamaFlashAttention2 = LlamaAttention"
                ),
            )
            changed = True

        # Патч 2: is_torch_fx_available (идемпотентный — заменяем голый import)
        # Заменяем только прямой import (не внутри try-блока)
        bare_import = "from transformers.utils.import_utils import is_torch_fx_available\n"
        try_import = (
            "try:\n"
            "    from transformers.utils.import_utils import is_torch_fx_available\n"
            "except ImportError:\n"
            "    def is_torch_fx_available():\n"
            "        try:\n"
            "            import torch.fx  # noqa\n"
            "            return True\n"
            "        except ImportError:\n"
            "            return False\n"
        )
        # Только если bare import существует вне try-блока (не содержит "try:\n    from")
        if bare_import in content and "try:\n    from transformers.utils.import_utils" not in content:
            content = content.replace(bare_import, try_import)
            changed = True

        if changed:
            f.write_text(content, encoding="utf-8", newline="\n")
            # Очистить .pyc
            pycache = f.parent / "__pycache__"
            if pycache.exists():
                import shutil
                shutil.rmtree(pycache, ignore_errors=True)
            logger.info(f"Применён патч совместимости к: {f}")
        else:
            logger.debug(f"Патч не нужен (уже применён): {f}")


# ---------------------------------------------------------------------------
# Model loader (lazy — не грузим при --test-config)
# ---------------------------------------------------------------------------

class DeepSeekOCRModel:
    """
    Обёртка вокруг deepseek-ai/DeepSeek-OCR-2.

    Загружает модель на указанный GPU в BF16. Поддерживает единичный
    и пакетный инференс.
    """

    def __init__(self, gpu_id: int = DEFAULT_GPU_ID):
        self.gpu_id = gpu_id
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load(self) -> None:
        """Загружает веса модели (требует ~16GB VRAM в BF16)."""
        if self._loaded:
            return

        logger.info(f"Загружаю {MODEL_ID} на GPU:{self.gpu_id} (BF16)...")
        _patch_transformers_cache()

        os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)

        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID, trust_remote_code=True
        )

        # Попытка с eager attention (без flash-attn)
        try:
            self.model = AutoModel.from_pretrained(
                MODEL_ID,
                attn_implementation="eager",
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch.bfloat16,
            )
        except TypeError:
            # Старый API без attn_implementation
            self.model = AutoModel.from_pretrained(
                MODEL_ID,
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch.bfloat16,
            )

        self.model = self.model.eval().cuda()
        self._loaded = True
        logger.info("Модель загружена успешно.")

    def infer_image(
        self,
        image_path: str,
        output_path: str,
        prompt: str = PROMPT_MARKDOWN,
        base_size: int = DEFAULT_BASE_SIZE,
        image_size: int = DEFAULT_IMAGE_SIZE,
        crop_mode: bool = DEFAULT_CROP_MODE,
    ) -> str:
        """
        Запускает OCR на одном изображении.

        Args:
            image_path: Путь к изображению (.jpg, .png, etc.)
            output_path: Директория для сохранения результата
            prompt: Промпт для модели (PROMPT_MARKDOWN или PROMPT_FREE_OCR)
            base_size: Базовый размер для глобального view (1024 = Gundam)
            image_size: Размер для crop patches (768 = Gundam)
            crop_mode: Включить режим кропинга (рекомендуется для документов)

        Returns:
            str: Распознанный текст / Markdown
        """
        if not self._loaded:
            self.load()

        Path(output_path).mkdir(parents=True, exist_ok=True)

        result = self.model.infer(
            self.tokenizer,
            prompt=prompt,
            image_file=image_path,
            output_path=output_path,
            base_size=base_size,
            image_size=image_size,
            crop_mode=crop_mode,
            save_results=True,
        )
        return result

    def unload(self) -> None:
        """Освобождает VRAM."""
        if self._loaded:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self._loaded = False
            torch.cuda.empty_cache()
            logger.info("Модель выгружена, VRAM освобожден.")


# ---------------------------------------------------------------------------
# Database integration
# ---------------------------------------------------------------------------

def get_low_confidence_chunks(
    db_path: str,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    limit: Optional[int] = None,
) -> list[dict]:
    """
    Возвращает чанки из kb.db с confidence < threshold.

    Предполагаемая схема: таблица chunks с полями:
      id, doc_id, image_path, ocr_text, confidence, ocr_patched
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT id, doc_id, image_path, ocr_text, confidence
        FROM chunks
        WHERE image_path IS NOT NULL
          AND confidence < ?
          AND (ocr_patched IS NULL OR ocr_patched = 0)
        ORDER BY confidence ASC
    """
    if limit:
        query += f" LIMIT {int(limit)}"

    try:
        rows = cur.execute(query, (threshold,)).fetchall()
        result = [dict(r) for r in rows]
        logger.info(f"Найдено {len(result)} чанков с confidence < {threshold}")
        return result
    except sqlite3.OperationalError as e:
        logger.warning(f"Не удалось запросить chunks: {e}")
        return []
    finally:
        conn.close()


def update_chunk_ocr(
    db_path: str,
    chunk_id: int,
    new_text: str,
    model_id: str = MODEL_ID,
) -> None:
    """Обновляет OCR-текст чанка и ставит флаг ocr_patched=1."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            UPDATE chunks
            SET ocr_text = ?,
                ocr_patched = 1,
                ocr_patch_model = ?
            WHERE id = ?
            """,
            (new_text, model_id, chunk_id),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Batch patch pipeline
# ---------------------------------------------------------------------------

def run_batch_patch(
    db_path: str,
    threshold: float,
    gpu_id: int,
    output_dir: str = "ocr_patch_output",
    limit: Optional[int] = None,
    dry_run: bool = False,
) -> dict:
    """
    Основной пайплайн пакетного патча.

    1. Находит чанки с confidence < threshold
    2. Загружает модель (если не dry_run)
    3. Прогоняет каждое изображение через DeepSeek-OCR-2
    4. Записывает результат обратно в SQLite

    Returns:
        dict: Статистика (patched, skipped, errors)
    """
    chunks = get_low_confidence_chunks(db_path, threshold, limit)
    stats = {"total": len(chunks), "patched": 0, "skipped": 0, "errors": 0}

    if not chunks:
        logger.info("Нет чанков для патча.")
        return stats

    if dry_run:
        logger.info(f"[DRY RUN] Было бы пропатчено: {len(chunks)} чанков")
        for c in chunks[:10]:
            logger.info(f"  chunk_id={c['id']} conf={c['confidence']:.3f} img={c['image_path']}")
        return stats

    ocr = DeepSeekOCRModel(gpu_id=gpu_id)
    ocr.load()

    try:
        for i, chunk in enumerate(chunks, 1):
            img_path = chunk["image_path"]
            chunk_id = chunk["id"]

            if not Path(img_path).exists():
                logger.warning(f"[{i}/{len(chunks)}] Файл не найден: {img_path}")
                stats["skipped"] += 1
                continue

            logger.info(
                f"[{i}/{len(chunks)}] Патч chunk_id={chunk_id} "
                f"conf={chunk['confidence']:.3f} img={Path(img_path).name}"
            )

            try:
                result = ocr.infer_image(
                    image_path=img_path,
                    output_path=output_dir,
                    prompt=PROMPT_MARKDOWN,
                )
                if result:
                    update_chunk_ocr(db_path, chunk_id, str(result))
                    stats["patched"] += 1
                else:
                    logger.warning(f"  Пустой результат для chunk_id={chunk_id}")
                    stats["skipped"] += 1
            except Exception as e:
                logger.error(f"  Ошибка при патче chunk_id={chunk_id}: {e}")
                stats["errors"] += 1

    finally:
        ocr.unload()

    logger.info(
        f"Патч завершён. Пропатчено: {stats['patched']}, "
        f"Пропущено: {stats['skipped']}, Ошибок: {stats['errors']}"
    )
    return stats


# ---------------------------------------------------------------------------
# Config test (быстрая проверка без загрузки весов)
# ---------------------------------------------------------------------------

def test_config() -> bool:
    """
    Загружает только конфиг модели (без весов) и выводит параметры.
    Используется для проверки совместимости окружения.
    """
    _patch_transformers_cache()

    logger.info(f"Тест конфигурации модели: {MODEL_ID}")

    try:
        from transformers import AutoConfig

        config = AutoConfig.from_pretrained(MODEL_ID, trust_remote_code=True)

        print("\n=== DeepSeek-OCR-2 Config ===")
        print(f"  model_type:         {config.model_type}")
        print(f"  num_hidden_layers:  {getattr(config, 'num_hidden_layers', 'N/A')}")
        print(f"  hidden_size:        {getattr(config, 'hidden_size', 'N/A')}")
        print(f"  vocab_size:         {getattr(config, 'vocab_size', 'N/A')}")
        print(f"  intermediate_size:  {getattr(config, 'intermediate_size', 'N/A')}")
        print(f"  num_attention_heads:{getattr(config, 'num_attention_heads', 'N/A')}")
        print(f"  n_routed_experts:   {getattr(config, 'n_routed_experts', 'N/A')}")
        print(f"  num_experts_per_tok:{getattr(config, 'num_experts_per_tok', 'N/A')}")

        # GPU info
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                free = torch.cuda.mem_get_info(i)[0] / 1024**3
                total = props.total_memory / 1024**3
                print(f"  GPU:{i} {props.name} -- Free: {free:.1f}GB / {total:.1f}GB")
        else:
            print("  CUDA не доступен!")

        print("=== Config OK ===\n")
        return True

    except Exception as e:
        logger.error(f"Ошибка при загрузке конфига: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="LLCAR Diagnostica -- DeepSeek-OCR-2 патч для MinerU результатов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Проверить конфиг без загрузки весов:
  python scripts/ocr_patch.py --test-config

  # Патч одного изображения:
  python scripts/ocr_patch.py --image path/to/image.jpg --out output/

  # Пакетный патч из базы данных:
  python scripts/ocr_patch.py --db knowledge-base/kb.db --threshold 0.7 --gpu 0

  # Пробный прогон (без записи в БД):
  python scripts/ocr_patch.py --db knowledge-base/kb.db --threshold 0.7 --dry-run
        """,
    )

    parser.add_argument("--test-config", action="store_true",
                        help="Загрузить только конфиг модели и выйти")
    parser.add_argument("--image", type=str,
                        help="Путь к изображению для OCR")
    parser.add_argument("--out", type=str, default="ocr_patch_output",
                        help="Директория для вывода (default: ocr_patch_output)")
    parser.add_argument("--prompt", choices=["markdown", "free"], default="markdown",
                        help="Режим OCR: markdown (default) или free")
    parser.add_argument("--db", type=str,
                        help="Путь к kb.db для пакетного патча")
    parser.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD,
                        help=f"Порог confidence (default: {DEFAULT_CONFIDENCE_THRESHOLD})")
    parser.add_argument("--gpu", type=int, default=DEFAULT_GPU_ID,
                        help=f"ID GPU (default: {DEFAULT_GPU_ID})")
    parser.add_argument("--limit", type=int, default=None,
                        help="Ограничить количество чанков для патча")
    parser.add_argument("--dry-run", action="store_true",
                        help="Показать что было бы пропатчено, без записи в БД")
    parser.add_argument("--verbose", action="store_true",
                        help="Подробный вывод")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Режим 1: только тест конфига
    if args.test_config:
        ok = test_config()
        sys.exit(0 if ok else 1)

    # Режим 2: одно изображение
    if args.image:
        prompt = PROMPT_MARKDOWN if args.prompt == "markdown" else PROMPT_FREE_OCR
        ocr = DeepSeekOCRModel(gpu_id=args.gpu)
        ocr.load()
        result = ocr.infer_image(
            image_path=args.image,
            output_path=args.out,
            prompt=prompt,
        )
        print("\n=== OCR Result ===")
        print(result)
        ocr.unload()
        return

    # Режим 3: пакетный патч из БД
    if args.db:
        stats = run_batch_patch(
            db_path=args.db,
            threshold=args.threshold,
            gpu_id=args.gpu,
            output_dir=args.out,
            limit=args.limit,
            dry_run=args.dry_run,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    # Если ничего не указано -- покажем help
    parse_args().print_help()


if __name__ == "__main__":
    main()
