#!/usr/bin/env python3
"""
Translation A/B Test — Automotive Diagnostics Project
Compares three MT models on 30 automotive sentences (RU→EN, EN→RU, ZH→RU).

Models tested:
  - utrobinmv/m2m_translate_en_ru_zh_large_4096  (Utrobin M2M-1B)
  - facebook/nllb-200-distilled-600M              (NLLB-200 distilled)
  - google/madlad400-3b-mt                        (MADLAD-400 3B)

Metrics: sacrebleu BLEU + terminology match against unified trilingual glossary.

Usage:
    python translation_ab_test.py
    python translation_ab_test.py --models utrobin nllb --device cuda:0
    python translation_ab_test.py --output results/ab_test_2026.json
"""

import argparse
import gc
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Force UTF-8 output on Windows so Cyrillic and arrow characters render correctly
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Optional imports — checked at runtime so the script can report clearly
# ---------------------------------------------------------------------------
try:
    import torch
except ImportError:
    torch = None  # type: ignore

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, M2M100ForConditionalGeneration
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    import sacrebleu
    SACREBLEU_AVAILABLE = True
except ImportError:
    SACREBLEU_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


# ===========================================================================
# Test data — 30 automotive sentence pairs
# ===========================================================================

TEST_DATA: Dict[str, List[Dict[str, str]]] = {
    "RU→EN": [
        {
            "source": "Замените тормозную жидкость каждые 2 года или 40000 км пробега.",
            "reference": "Replace brake fluid every 2 years or 40,000 km of mileage.",
        },
        {
            "source": "Момент затяжки болтов крепления суппорта: 35 Нм.",
            "reference": "Caliper mounting bolt torque: 35 Nm.",
        },
        {
            "source": "Проверьте уровень масла в двигателе при холодном двигателе.",
            "reference": "Check engine oil level with the engine cold.",
        },
        {
            "source": "Датчик массового расхода воздуха расположен после воздушного фильтра.",
            "reference": "The mass air flow sensor is located after the air filter.",
        },
        {
            "source": "При появлении кода ошибки P0420 проверьте каталитический нейтрализатор.",
            "reference": "When error code P0420 appears, check the catalytic converter.",
        },
        {
            "source": "Рекомендуемое давление в шинах: 2.3 бар (передние), 2.5 бар (задние).",
            "reference": "Recommended tire pressure: 2.3 bar (front), 2.5 bar (rear).",
        },
        {
            "source": "Турбокомпрессор охлаждается маслом и антифризом.",
            "reference": "The turbocharger is cooled by oil and coolant.",
        },
        {
            "source": "Снимите декоративную крышку двигателя, потянув её вверх.",
            "reference": "Remove the engine decorative cover by pulling it upward.",
        },
        {
            "source": "Блок управления двигателем (ECU) расположен под приборной панелью.",
            "reference": "The engine control unit (ECU) is located under the dashboard.",
        },
        {
            "source": "Замена ремня ГРМ требуется каждые 90000 км.",
            "reference": "Timing belt replacement is required every 90,000 km.",
        },
    ],
    "EN→RU": [
        {
            "source": "The high-voltage battery pack requires inspection every 12 months.",
            "reference": "Высоковольтная аккумуляторная батарея требует проверки каждые 12 месяцев.",
        },
        {
            "source": "WARNING: Do not open the inverter cover while the vehicle is powered on.",
            "reference": "ВНИМАНИЕ: Не открывайте крышку инвертора при включённом питании автомобиля.",
        },
        {
            "source": "DTC P0300 indicates random/multiple cylinder misfire detected.",
            "reference": "Код ошибки P0300 указывает на обнаружение случайных/множественных пропусков зажигания.",
        },
        {
            "source": "Apply 0W-20 synthetic motor oil. Capacity: 4.5 liters.",
            "reference": "Используйте синтетическое моторное масло 0W-20. Объём: 4,5 литра.",
        },
        {
            "source": "The regenerative braking system recovers kinetic energy during deceleration.",
            "reference": "Система рекуперативного торможения преобразует кинетическую энергию при замедлении.",
        },
        {
            "source": "Inspect the brake pads for wear. Minimum thickness: 2 mm.",
            "reference": "Проверьте тормозные колодки на износ. Минимальная толщина: 2 мм.",
        },
        {
            "source": "The coolant temperature sensor sends data to the ECU via CAN bus.",
            "reference": "Датчик температуры охлаждающей жидкости передаёт данные в ЭБУ по шине CAN.",
        },
        {
            "source": "Disconnect the negative battery terminal before performing electrical work.",
            "reference": "Отсоедините отрицательную клемму аккумулятора перед выполнением электрических работ.",
        },
        {
            "source": "The differential oil should be changed every 60,000 km.",
            "reference": "Масло в дифференциале следует менять каждые 60000 км.",
        },
        {
            "source": "ABS module failure may cause the stability control warning light to illuminate.",
            "reference": "Неисправность блока ABS может привести к загоранию индикатора системы стабилизации.",
        },
    ],
    "ZH→RU": [
        {
            "source": "更换制动液时，请使用DOT4标准制动液。",
            "reference": "При замене тормозной жидкости используйте тормозную жидкость стандарта DOT4.",
        },
        {
            "source": "发动机冷却液温度过高时，请立即停车检查。",
            "reference": "При слишком высокой температуре охлаждающей жидкости двигателя немедленно остановитесь для проверки.",
        },
        {
            "source": "前大灯高度调节范围为0至3档。",
            "reference": "Диапазон регулировки высоты передних фар составляет от 0 до 3 уровней.",
        },
        {
            "source": "请定期检查轮胎磨损情况和胎压。",
            "reference": "Регулярно проверяйте состояние износа шин и давление в них.",
        },
        {
            "source": "高压电池组位于车辆底部。",
            "reference": "Высоковольтная батарея расположена в нижней части автомобиля.",
        },
        {
            "source": "空调滤芯建议每12个月或20000公里更换一次。",
            "reference": "Фильтр кондиционера рекомендуется менять каждые 12 месяцев или 20000 км.",
        },
        {
            "source": "车辆启动前，请确保所有车门已关闭。",
            "reference": "Перед запуском автомобиля убедитесь, что все двери закрыты.",
        },
        {
            "source": "电动助力转向系统故障时，方向盘会变重。",
            "reference": "При неисправности электроусилителя руля рулевое колесо становится тяжёлым.",
        },
        {
            "source": "增程器在电量低于30%时自动启动。",
            "reference": "Генератор-расширитель запаса хода автоматически запускается при заряде ниже 30%.",
        },
        {
            "source": "请使用原厂推荐的0W-20全合成机油。",
            "reference": "Используйте рекомендованное заводом полностью синтетическое масло 0W-20.",
        },
    ],
}


# ===========================================================================
# Language code mappings
# ===========================================================================

# NLLB uses flores-200 BCP-47 codes
NLLB_LANG_CODES: Dict[str, str] = {
    "ru": "rus_Cyrl",
    "en": "eng_Latn",
    "zh": "zho_Hans",
}

# Utrobin uses text prefix "translate to {lang}: " (T5-style, from model card)
UTROBIN_LANG_CODES: Dict[str, str] = {
    "ru": "ru",
    "en": "en",
    "zh": "zh",
}

# MADLAD-400 uses "<2XX>" prefix tokens inserted into the source text
MADLAD_LANG_PREFIXES: Dict[str, str] = {
    "ru": "<2ru>",
    "en": "<2en>",
    "zh": "<2zh>",
}

# Direction strings → (src_lang, tgt_lang)
DIRECTION_LANGS: Dict[str, Tuple[str, str]] = {
    "RU→EN": ("ru", "en"),
    "EN→RU": ("en", "ru"),
    "ZH→RU": ("zh", "ru"),
}


# ===========================================================================
# Model registry
# ===========================================================================

MODEL_REGISTRY: Dict[str, Dict] = {
    "utrobin": {
        "display_name": "Utrobin M2M",
        "hf_id": "utrobinmv/m2m_translate_en_ru_zh_large_4096",
        "type": "m2m",
    },
    "nllb": {
        "display_name": "NLLB-600M",
        "hf_id": "facebook/nllb-200-distilled-600M",
        "type": "nllb",
    },
    "madlad": {
        "display_name": "MADLAD-3B",
        "hf_id": "google/madlad400-3b-mt",
        "type": "madlad",
    },
}


# ===========================================================================
# Glossary utilities
# ===========================================================================

GLOSSARY_PATHS = [
    Path(__file__).parent.parent / "knowledge-base" / "glossary-unified-trilingual.json",
    Path(__file__).parent.parent / "дополнительно" / "полный глоссарий" / "полный глоссарий" / "automotive-glossary-5lang.json",
]


def load_glossary() -> List[Dict[str, str]]:
    """
    Load glossary terms from the first available path.
    Returns a list of dicts with keys: 'en', 'ru', 'zh' (and optionally others).
    """
    for path in GLOSSARY_PATHS:
        if path.exists():
            print(f"[glossary] Loading from: {path}")
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            # Support both root-level list and {"terms": [...]} shape
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "terms" in data:
                return data["terms"]
            print("[glossary] Unexpected structure — no 'terms' key and not a list.")
            return []
    print("[glossary] WARNING: No glossary file found. Terminology match will be 0.0.")
    return []


def _normalize(text: str) -> str:
    """Lower-case, strip punctuation edges for robust term matching."""
    return text.lower().strip(" .,;:!?()")


def terminology_match(
    source_text: str,
    translation: str,
    src_lang: str,
    tgt_lang: str,
    glossary: List[Dict[str, str]],
) -> float:
    """
    Check what fraction of glossary terms present in the source were
    translated consistently with the glossary in the translation output.

    Returns a score in [0.0, 1.0].  Returns NaN (float('nan')) when no
    glossary terms are found in the source at all.
    """
    if not glossary:
        return float("nan")

    source_lower = _normalize(source_text)
    translation_lower = _normalize(translation)

    found_in_source = 0
    matched_in_translation = 0

    for entry in glossary:
        src_term = entry.get(src_lang, "")
        tgt_term = entry.get(tgt_lang, "")
        if not src_term or not tgt_term:
            continue

        src_term_norm = _normalize(src_term)
        tgt_term_norm = _normalize(tgt_term)

        if not src_term_norm:
            continue

        # Check if source term appears in the source sentence
        if src_term_norm in source_lower:
            found_in_source += 1
            # Check if target term appears in the translation
            if tgt_term_norm in translation_lower:
                matched_in_translation += 1

    if found_in_source == 0:
        return float("nan")

    return matched_in_translation / found_in_source


def aggregate_term_match(scores: List[float]) -> Optional[float]:
    """Return mean of non-NaN scores, or None if all are NaN."""
    valid = [s for s in scores if not (s != s)]  # s != s is True for NaN
    if not valid:
        return None
    return sum(valid) / len(valid)


# ===========================================================================
# Translation helpers — one per model family
# ===========================================================================

def _progress(iterable, desc: str, total: int):
    """Wrap an iterable with tqdm if available, else return as-is."""
    if TQDM_AVAILABLE:
        return tqdm(iterable, desc=desc, total=total, unit="sent", ncols=90)
    return iterable


def translate_utrobin(
    model,
    tokenizer,
    sentences: List[str],
    src_lang: str,
    tgt_lang: str,
    device: str,
) -> Tuple[List[str], List[float]]:
    """
    Translate with the Utrobin M2M model.
    Language is specified as a text prefix: "translate to {lang}: {text}"
    (T5-style, as per model card — no forced_bos_token_id needed).
    """
    tgt_code = UTROBIN_LANG_CODES[tgt_lang]
    prefix = f"translate to {tgt_code}: "

    translations: List[str] = []
    times: List[float] = []

    for sent in _progress(sentences, f"Utrobin {src_lang}→{tgt_lang}", len(sentences)):
        src_text = prefix + sent
        inputs = tokenizer(src_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        t0 = time.perf_counter()
        with torch.no_grad() if torch else _noop_ctx():
            output_ids = model.generate(**inputs, max_new_tokens=512, num_beams=4, early_stopping=True)
        elapsed = time.perf_counter() - t0

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        translations.append(decoded)
        times.append(elapsed)

    return translations, times


def translate_nllb(
    model,
    tokenizer,
    sentences: List[str],
    src_lang: str,
    tgt_lang: str,
    device: str,
) -> Tuple[List[str], List[float]]:
    """
    Translate with the NLLB-200 model.
    Uses flores-200 language codes via tokenizer.src_lang / forced_bos_token_id.
    """
    src_code = NLLB_LANG_CODES[src_lang]
    tgt_code = NLLB_LANG_CODES[tgt_lang]

    translations: List[str] = []
    times: List[float] = []

    for sent in _progress(sentences, f"NLLB {src_lang}→{tgt_lang}", len(sentences)):
        tokenizer.src_lang = src_code
        inputs = tokenizer(sent, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_code)

        t0 = time.perf_counter()
        with torch.no_grad() if torch else _noop_ctx():
            output_ids = model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_new_tokens=512,
                num_beams=4,
                early_stopping=True,
            )
        elapsed = time.perf_counter() - t0

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        translations.append(decoded)
        times.append(elapsed)

    return translations, times


def translate_madlad(
    model,
    tokenizer,
    sentences: List[str],
    src_lang: str,
    tgt_lang: str,
    device: str,
) -> Tuple[List[str], List[float]]:
    """
    Translate with the MADLAD-400 model.
    Prepends the target-language prefix token directly to the source string.
    Source language is inferred — no explicit src_lang token needed.
    """
    prefix = MADLAD_LANG_PREFIXES[tgt_lang]

    translations: List[str] = []
    times: List[float] = []

    for sent in _progress(sentences, f"MADLAD {src_lang}→{tgt_lang}", len(sentences)):
        prefixed = f"{prefix} {sent}"
        inputs = tokenizer(prefixed, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        t0 = time.perf_counter()
        with torch.no_grad() if torch else _noop_ctx():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=512,
                num_beams=4,
                early_stopping=True,
            )
        elapsed = time.perf_counter() - t0

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        translations.append(decoded)
        times.append(elapsed)

    return translations, times


# Context manager shim so `with torch.no_grad()` works when torch is None
class _noop_ctx:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


TRANSLATE_FN = {
    "m2m": translate_utrobin,
    "nllb": translate_nllb,
    "madlad": translate_madlad,
}


# ===========================================================================
# BLEU computation
# ===========================================================================

def compute_bleu(hypotheses: List[str], references: List[str]) -> float:
    """
    Compute corpus-level sacrebleu BLEU.
    Returns 0.0 if sacrebleu is not available.
    """
    if not SACREBLEU_AVAILABLE:
        return float("nan")

    # sacrebleu expects [[ref1, ref2, ...], ...] per sentence (list of ref lists)
    # or a single list of references — API changed across versions; handle both.
    try:
        result = sacrebleu.corpus_bleu(hypotheses, [references])
        return result.score
    except Exception as exc:
        print(f"[bleu] Error computing BLEU: {exc}")
        return float("nan")


# ===========================================================================
# GPU memory cleanup
# ===========================================================================

def release_model(model, tokenizer) -> None:
    """Delete model/tokenizer and free GPU VRAM."""
    del model
    del tokenizer
    if torch is not None:
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    else:
        gc.collect()


# ===========================================================================
# Table printing
# ===========================================================================

def _fmt_bleu(v) -> str:
    if v != v:  # NaN
        return "  N/A  "
    return f"{v:6.1f}"


def _fmt_term(v) -> str:
    if v is None or v != v:
        return "  N/A  "
    return f"{v * 100:5.1f}%"


def _fmt_time(v: float) -> str:
    return f"{v:.3f}s"


def print_table(direction: str, results: List[Dict]) -> None:
    """Print a results table for one translation direction."""
    col_model = 14
    col_bleu = 9
    col_term = 13
    col_time = 10

    h_model = "Model".ljust(col_model)
    h_bleu = "BLEU".center(col_bleu)
    h_term = "Term Match".center(col_term)
    h_time = "Avg Time".center(col_time)

    sep = (
        "+"
        + "-" * (col_model + 2)
        + "+"
        + "-" * (col_bleu + 2)
        + "+"
        + "-" * (col_term + 2)
        + "+"
        + "-" * (col_time + 2)
        + "+"
    )

    print(f"\nDirection: {direction}")
    print(sep)
    print(f"| {h_model} | {h_bleu} | {h_term} | {h_time} |")
    print(sep)
    for row in results:
        name = row["model_display"].ljust(col_model)
        bleu = _fmt_bleu(row["bleu"]).center(col_bleu)
        term = _fmt_term(row["term_match"]).center(col_term)
        avg_t = _fmt_time(row["avg_time_s"]).center(col_time)
        print(f"| {name} | {bleu} | {term} | {avg_t} |")
    print(sep)


# ===========================================================================
# Core test runner
# ===========================================================================

def run_model_test(
    model_key: str,
    device: str,
    glossary: List[Dict[str, str]],
) -> Dict:
    """
    Load model, translate all directions, compute metrics, unload model.
    Returns a results dict ready for JSON serialisation.
    """
    if not HF_AVAILABLE:
        raise RuntimeError(
            "transformers library is not installed. "
            "Run: pip install transformers sentencepiece sacrebleu tqdm"
        )

    meta = MODEL_REGISTRY[model_key]
    hf_id = meta["hf_id"]
    model_type = meta["type"]
    display_name = meta["display_name"]

    print(f"\n{'='*60}")
    print(f"Loading model: {display_name}  ({hf_id})")
    print(f"Device: {device}")
    print("="*60)

    t_load_start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(hf_id)
    # Utrobin uses M2M100ForConditionalGeneration (m2m_100 arch) with T5Tokenizer
    # and text prefix for language control. AutoModelForSeq2SeqLM also works.
    if model_type == "m2m":
        model = M2M100ForConditionalGeneration.from_pretrained(hf_id)
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(hf_id)
    model.eval()

    if torch is not None:
        model = model.to(device)

    t_load_end = time.perf_counter()
    print(f"Model loaded in {t_load_end - t_load_start:.1f}s")

    translate_fn = TRANSLATE_FN[model_type]

    model_results: Dict = {
        "model_key": model_key,
        "model_display": display_name,
        "hf_id": hf_id,
        "device": device,
        "load_time_s": round(t_load_end - t_load_start, 2),
        "directions": {},
    }

    for direction, pairs in TEST_DATA.items():
        src_lang, tgt_lang = DIRECTION_LANGS[direction]
        sources = [p["source"] for p in pairs]
        references = [p["reference"] for p in pairs]

        print(f"\n  Running direction: {direction}")
        try:
            hypotheses, times = translate_fn(
                model, tokenizer, sources, src_lang, tgt_lang, device
            )
        except Exception as exc:
            print(f"  [ERROR] Translation failed for {direction}: {exc}")
            model_results["directions"][direction] = {
                "error": str(exc),
                "bleu": float("nan"),
                "term_match": None,
                "avg_time_s": 0.0,
                "sentences": [],
            }
            continue

        bleu = compute_bleu(hypotheses, references)

        term_scores: List[float] = []
        for src, hyp in zip(sources, hypotheses):
            score = terminology_match(src, hyp, src_lang, tgt_lang, glossary)
            term_scores.append(score)

        avg_term = aggregate_term_match(term_scores)
        avg_time = sum(times) / len(times) if times else 0.0

        sentence_details = []
        for i, (src, ref, hyp, t_sec, ts) in enumerate(
            zip(sources, references, hypotheses, times, term_scores)
        ):
            sentence_details.append({
                "id": i + 1,
                "source": src,
                "reference": ref,
                "hypothesis": hyp,
                "time_s": round(t_sec, 4),
                "term_match": None if (ts != ts) else round(ts, 4),
            })

        model_results["directions"][direction] = {
            "bleu": round(bleu, 2) if bleu == bleu else None,
            "term_match": round(avg_term, 4) if avg_term is not None else None,
            "avg_time_s": round(avg_time, 4),
            "sentences": sentence_details,
        }

        print(
            f"  {direction}: BLEU={_fmt_bleu(bleu).strip()}, "
            f"TermMatch={_fmt_term(avg_term).strip()}, "
            f"AvgTime={_fmt_time(avg_time)}"
        )

    print(f"\nUnloading {display_name}...")
    release_model(model, tokenizer)

    return model_results


# ===========================================================================
# Aggregated summary table
# ===========================================================================

def build_summary(all_results: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Restructure raw per-model results into a per-direction summary
    suitable for table printing and JSON output.
    """
    summary: Dict[str, List[Dict]] = {}

    for direction in TEST_DATA.keys():
        rows = []
        for model_result in all_results:
            dir_data = model_result["directions"].get(direction, {})
            rows.append({
                "model_key": model_result["model_key"],
                "model_display": model_result["model_display"],
                "bleu": dir_data.get("bleu") if dir_data.get("bleu") is not None else float("nan"),
                "term_match": dir_data.get("term_match"),
                "avg_time_s": dir_data.get("avg_time_s", 0.0),
            })
        summary[direction] = rows

    return summary


# ===========================================================================
# CLI
# ===========================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translation A/B test for automotive diagnostics (RU/EN/ZH)"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=list(MODEL_REGISTRY.keys()),
        default=list(MODEL_REGISTRY.keys()),
        metavar="MODEL",
        help=f"Models to test. Choices: {', '.join(MODEL_REGISTRY.keys())}. Default: all three.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help='Compute device, e.g. "cpu", "cuda:0", "cuda:1". Default: cpu.',
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save JSON results. Default: ab_test_results_<timestamp>.json next to script.",
    )
    parser.add_argument(
        "--no-glossary",
        action="store_true",
        help="Skip glossary loading (terminology match will be skipped).",
    )
    return parser.parse_args()


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> int:
    args = parse_args()

    # ------------------------------------------------------------------
    # Dependency checks
    # ------------------------------------------------------------------
    missing = []
    if not HF_AVAILABLE:
        missing.append("transformers  (pip install transformers)")
    if not SACREBLEU_AVAILABLE:
        missing.append("sacrebleu     (pip install sacrebleu)")
    if not TQDM_AVAILABLE:
        print("[warning] tqdm not installed — progress bars disabled. "
              "Install with: pip install tqdm")

    if missing:
        print("\n[ERROR] Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall all requirements with:")
        print("  pip install transformers sentencepiece sacrebleu tqdm torch")
        return 1

    # ------------------------------------------------------------------
    # Device validation
    # ------------------------------------------------------------------
    device = args.device
    if torch is None:
        print("[warning] PyTorch not found — running in CPU-only mode via transformers.")
        device = "cpu"
    elif device.startswith("cuda") and not torch.cuda.is_available():
        print(f"[warning] CUDA requested ({device}) but not available. Falling back to CPU.")
        device = "cpu"

    # ------------------------------------------------------------------
    # Glossary
    # ------------------------------------------------------------------
    glossary: List[Dict[str, str]] = []
    if not args.no_glossary:
        glossary = load_glossary()
        print(f"[glossary] {len(glossary)} terms loaded.")
    else:
        print("[glossary] Skipped (--no-glossary).")

    # ------------------------------------------------------------------
    # Run tests
    # ------------------------------------------------------------------
    print(f"\n=== TRANSLATION A/B TEST ===")
    print(f"Models : {', '.join(args.models)}")
    print(f"Device : {device}")
    print(f"Directions: {', '.join(TEST_DATA.keys())}")
    print(f"Sentences per direction: {len(next(iter(TEST_DATA.values())))}")

    all_results: List[Dict] = []
    failed_models: List[str] = []

    for model_key in args.models:
        try:
            result = run_model_test(model_key, device, glossary)
            all_results.append(result)
        except Exception as exc:
            print(f"\n[ERROR] Model '{model_key}' failed entirely: {exc}")
            failed_models.append(model_key)
            # Attempt cleanup even on hard failure
            gc.collect()
            if torch is not None and torch.cuda.is_available():
                torch.cuda.empty_cache()

    if not all_results:
        print("\n[ERROR] All models failed. No results to display.")
        return 1

    # ------------------------------------------------------------------
    # Print summary tables
    # ------------------------------------------------------------------
    summary = build_summary(all_results)

    print("\n\n" + "=" * 60)
    print("=== TRANSLATION A/B TEST RESULTS ===")
    print("=" * 60)

    for direction, rows in summary.items():
        print_table(direction, rows)

    # Overall best model per direction
    print("\n--- Best model per direction (by BLEU) ---")
    for direction, rows in summary.items():
        valid_rows = [r for r in rows if r["bleu"] == r["bleu"]]  # exclude NaN
        if valid_rows:
            best = max(valid_rows, key=lambda r: r["bleu"])
            print(f"  {direction}: {best['model_display']} (BLEU {best['bleu']:.1f})")
        else:
            print(f"  {direction}: no valid BLEU scores")

    if failed_models:
        print(f"\n[warning] These models failed and are excluded: {', '.join(failed_models)}")

    # ------------------------------------------------------------------
    # Save JSON
    # ------------------------------------------------------------------
    if args.output:
        out_path = Path(args.output)
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_path = Path(__file__).parent / f"ab_test_results_{timestamp}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    output_payload = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "device": device,
            "models_tested": args.models,
            "models_failed": failed_models,
            "glossary_terms_loaded": len(glossary),
            "sacrebleu_available": SACREBLEU_AVAILABLE,
        },
        "summary": {
            direction: [
                {
                    "model": r["model_display"],
                    "bleu": r["bleu"] if r["bleu"] == r["bleu"] else None,
                    "term_match_pct": (
                        round(r["term_match"] * 100, 1)
                        if r["term_match"] is not None
                        else None
                    ),
                    "avg_time_s": r["avg_time_s"],
                }
                for r in rows
            ]
            for direction, rows in summary.items()
        },
        "detailed_results": all_results,
    }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output_payload, fh, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
