#!/bin/bash
# Запускает MinerU через изолированный venv (.venv-mineru, Python 3.11)
# Использование: bash scripts/run_mineru.sh -p <pdf_path> -o <output_dir> [-m auto] [-b pipeline] [-l ru]
# Пример: bash scripts/run_mineru.sh -p "knowledge-base/raw-pdfs/manual.pdf" -o "mineru-output" -l ru

VENV_DIR="/c/Diagnostica-KB-Package/.venv-mineru"
PYTHON="$VENV_DIR/Scripts/python.exe"
MAGIC_PDF="$VENV_DIR/Scripts/magic-pdf.exe"

# Проверяем что venv существует
if [ ! -f "$PYTHON" ]; then
    echo "ERROR: venv not found at $VENV_DIR"
    echo "Create it with: py -3.11 -m venv /c/Diagnostica-KB-Package/.venv-mineru"
    exit 1
fi

# Проверяем что magic-pdf установлен
if [ ! -f "$MAGIC_PDF" ]; then
    echo "ERROR: magic-pdf.exe not found in venv"
    echo "Install with: $VENV_DIR/Scripts/pip.exe install 'magic-pdf[full]'"
    exit 1
fi

# Запускаем magic-pdf с увеличенным лимитом рекурсии
PYTHONRECURSIONLIMIT=10000 "$MAGIC_PDF" "$@"
