#!/bin/bash
# run_mineru_all.sh — Process all PDFs with MinerU
# IMPORTANT: Use Windows-style C:/ paths for magic-pdf.exe (Windows executable)

MAGIC_PDF="/c/Diagnostica-KB-Package/.venv-mineru/Scripts/magic-pdf"
PDFS_DIR="C:/Diagnostica-KB-Package/pdfs"
OUT_DIR="C:/Diagnostica-KB-Package/mineru-output"

mkdir -p "/c/Diagnostica-KB-Package/mineru-output"

echo "=== MinerU batch processing ==="
echo "Started: $(date)"

run_mineru() {
    local label="$1"; local pdf="$2"; local mode="$3"; local lang="$4"
    echo ""; echo "--- $label ---"
    if [ -n "$lang" ]; then
        "$MAGIC_PDF" -p "$pdf" -o "$OUT_DIR" -m "$mode" -l "$lang" \
          && echo "  DONE: $label" || echo "  FAILED: $label"
    else
        "$MAGIC_PDF" -p "$pdf" -o "$OUT_DIR" -m "$mode" \
          && echo "  DONE: $label" || echo "  FAILED: $label"
    fi
}

run_mineru "[1] L7参数配置中文 (ZH)"      "$PDFS_DIR/857694655-241015-L7参数配置中文.pdf"           ocr  ch
run_mineru "[2] L9零件手册 (ZH)"          "$PDFS_DIR/941362155-2022-2023款理想L9零件手册.pdf"       ocr  ch
run_mineru "[3] Li L9英文版 (EN)"          "$PDFS_DIR/Li L9英文版.pdf"                               auto ""
run_mineru "[4] L9 Config (ZH)"           "$PDFS_DIR/240322-Li-L9-Configuration.pdf"                auto ch
run_mineru "[5] Lixiang L9 Owner Manual"  "$PDFS_DIR/Lixiang L9 Owner's Manual.pdf"                 auto ""
run_mineru "[6] Lixiang L7 Owner Manual"  "$PDFS_DIR/Lixiang L7 Owner's Manual.pdf"                 auto ""
run_mineru "[7] L9 RU Manual"             "$PDFS_DIR/Lixiang L9 Руководство пользователя.pdf"       auto ru

echo ""; echo "=== ALL DONE: $(date) ==="
echo ""; echo "=== Output summary ==="
for d in /c/Diagnostica-KB-Package/mineru-output/*/; do
    name=$(basename "$d")
    md=$(find "$d" -name "*.md" 2>/dev/null | head -1)
    if [ -n "$md" ]; then
        lines=$(wc -l < "$md")
        echo "  OK: $name ($lines lines)"
    else
        echo "  NO MD: $name"
    fi
done
