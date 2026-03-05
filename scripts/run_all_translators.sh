#!/usr/bin/env bash
# run_all_translators.sh — Bridge-translation launcher (ZH→EN→{RU,AR,ES}).
#
# Strategy:
#   Phase 1: ZH → EN  (direct, best quality for first hop)
#   Phase 2: EN → RU, EN → AR, EN → ES  (bridge: use EN as pivot)
#   Bonus:   RU → EN  (for RU-source chunks)
#
# Why bridge? Claude Haiku translates better from EN than from ZH.
# Sequential only — SQLite WAL doesn't support parallel writers.
#
# Usage:
#   bash scripts/run_all_translators.sh            # full run
#   bash scripts/run_all_translators.sh --skip-zh  # skip Phase 1 if ZH→EN done
#   bash scripts/run_all_translators.sh --dry-run
#
# Output files (knowledge-base/):
#   training_pairs_zh_en.jsonl   Phase 1: ZH → EN  (direct)
#   training_pairs_en_ru.jsonl   Phase 2: EN → RU  (bridge)
#   training_pairs_en_ar.jsonl   Phase 2: EN → AR  (bridge)
#   training_pairs_en_es.jsonl   Phase 2: EN → ES  (bridge)
#   training_pairs_ru_en.jsonl   Bonus:   RU → EN
#   training_pairs_all.jsonl     Merged all above

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KB_DIR="$PROJECT_ROOT/knowledge-base"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# Defaults
TIER="${TIER:-all}"
SKIP_ZH=""
DRY_RUN=""
BRAND="${BRAND:-li_auto}"
MAX_TERMS=500

for arg in "$@"; do
    case "$arg" in
        --skip-zh)  SKIP_ZH="yes" ;;
        --dry-run)  DRY_RUN="--dry-run" ;;
        --tier=*)   TIER="${arg#*=}" ;;
        --brand=*)  BRAND="${arg#*=}" ;;
    esac
done

BASE_ARGS="--tier $TIER --brand $BRAND --max-glossary-terms $MAX_TERMS $DRY_RUN"

run_translator() {
    local src_lang="$1"   # source language (for file name only — script auto-detects source)
    local tgt_lang="$2"   # target language
    local out_file="$3"
    local log_file="$LOG_DIR/translate_${src_lang}_${tgt_lang}.log"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $(date +%H:%M:%S)  ${src_lang} → ${tgt_lang}"
    echo "  Output : $out_file"
    echo "  Log    : $log_file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python "$SCRIPT_DIR/translate_kb.py" \
        $BASE_ARGS \
        --target-langs "$tgt_lang" \
        --training-pairs "$out_file" \
        2>&1 | tee "$log_file"

    local n=$(wc -l < "$out_file" 2>/dev/null || echo 0)
    echo "  ✓ Done. Training pairs: $n"
}

echo "╔══════════════════════════════════════════════════╗"
echo "║     KB Bridge Translation — All Languages        ║"
echo "║  Strategy: ZH→EN, then EN→{RU,AR,ES}            ║"
echo "╚══════════════════════════════════════════════════╝"
echo "  Brand: $BRAND | Tier: $TIER | $(date)"
echo ""

# ── PHASE 1: ZH → EN (direct) ─────────────────────────────────────────────
if [ -z "$SKIP_ZH" ]; then
    echo "═══ PHASE 1: ZH → EN (direct) ═══"
    run_translator "zh" "en" "$KB_DIR/training_pairs_zh_en.jsonl"
else
    echo "═══ PHASE 1: ZH → EN — SKIPPED (--skip-zh) ═══"
fi

# ── PHASE 2: EN → {RU, AR, ES} (bridge) ──────────────────────────────────
echo ""
echo "═══ PHASE 2: EN → {RU, AR, ES} (bridge) ═══"

run_translator "en" "ru" "$KB_DIR/training_pairs_en_ru.jsonl"
run_translator "en" "ar" "$KB_DIR/training_pairs_en_ar.jsonl"
run_translator "en" "es" "$KB_DIR/training_pairs_en_es.jsonl"

# ── BONUS: RU → EN (for RU-source chunks) ────────────────────────────────
echo ""
echo "═══ BONUS: RU → EN (Russian-source chunks) ═══"
run_translator "ru" "en" "$KB_DIR/training_pairs_ru_en.jsonl"

# ── MERGE ─────────────────────────────────────────────────────────────────
ALL="$KB_DIR/training_pairs_all.jsonl"
echo ""
echo "═══ Merging all files → $ALL ═══"

# Collect existing files
FILES=()
for f in \
    "$KB_DIR/training_pairs_zh_en.jsonl" \
    "$KB_DIR/training_pairs_en_ru.jsonl" \
    "$KB_DIR/training_pairs_en_ar.jsonl" \
    "$KB_DIR/training_pairs_en_es.jsonl" \
    "$KB_DIR/training_pairs_ru_en.jsonl"
do
    [ -f "$f" ] && FILES+=("$f")
done

if [ ${#FILES[@]} -gt 0 ]; then
    cat "${FILES[@]}" > "$ALL"
fi

TOTAL=$(wc -l < "$ALL" 2>/dev/null || echo 0)

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║                 SUMMARY                          ║"
echo "╚══════════════════════════════════════════════════╝"
printf "  %-35s %6s\n" "File" "Lines"
printf "  %-35s %6s\n" "────────────────────────────────" "──────"
for f in "${FILES[@]}"; do
    n=$(wc -l < "$f" 2>/dev/null || echo 0)
    printf "  %-35s %6d\n" "$(basename $f)" "$n"
done
printf "  %-35s %6s\n" "────────────────────────────────" "──────"
printf "  %-35s %6d\n" "training_pairs_all.jsonl (TOTAL)" "$TOTAL"
echo ""
echo "  Done at $(date)"
