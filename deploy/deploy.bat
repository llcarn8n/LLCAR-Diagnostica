@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title LLCAR Diagnostica — Deploy

echo.
echo ================================================================
echo   LLCAR Diagnostica KB — Setup on New Machine
echo   github: your-repo / internal transfer
echo ================================================================
echo.

REM ── Detect script location ──────────────────────────────────────
set "ROOT=%~dp0.."
cd /d "%ROOT%"
echo [*] Project root: %ROOT%
echo.

REM ── STEP 0: Check prerequisites ─────────────────────────────────
echo ================================================================
echo  STEP 0 — Check prerequisites
echo ================================================================

REM Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] Python not found. Install Python 3.11+ from python.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [OK] %PY_VER%

REM Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] Node.js not found. Install from nodejs.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do set NODE_VER=%%v
echo  [OK] Node.js %NODE_VER%

REM GPU check (optional but recommended)
python -c "import torch; print(' [OK] CUDA available:', torch.cuda.is_available())" 2>nul || (
    echo  [!] torch not yet installed — will install below
)
echo.

REM ── STEP 1: Python virtual environment ──────────────────────────
echo ================================================================
echo  STEP 1 — Python virtual environment
echo ================================================================

if exist ".venv\Scripts\activate.bat" (
    echo  [OK] .venv already exists — skipping creation
) else (
    echo  Creating .venv ...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo  [!!] Failed to create venv
        pause & exit /b 1
    )
    echo  [OK] .venv created
)
call .venv\Scripts\activate.bat
echo  [OK] .venv activated
echo.

REM ── STEP 2: PyTorch (CUDA) ───────────────────────────────────────
echo ================================================================
echo  STEP 2 — PyTorch with CUDA
echo ================================================================
echo.
echo  Choose your CUDA version:
echo    1) CUDA 12.1  (RTX 30xx/40xx, most common)
echo    2) CUDA 12.4  (RTX 40xx latest)
echo    3) CUDA 13.0  (RTX 30xx/40xx, newest drivers - original machine)
echo    4) CPU only   (no GPU — slow search, no embeddings)
echo    5) Skip       (torch already installed)
echo.
set /p CUDA_CHOICE="Enter choice [1-5]: "

if "%CUDA_CHOICE%"=="1" (
    echo  Installing torch cu121...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
) else if "%CUDA_CHOICE%"=="2" (
    echo  Installing torch cu124...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --quiet
) else if "%CUDA_CHOICE%"=="3" (
    echo  Installing torch cu130...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130 --quiet
) else if "%CUDA_CHOICE%"=="4" (
    echo  Installing torch CPU only...
    pip install torch torchvision torchaudio --quiet
) else if "%CUDA_CHOICE%"=="5" (
    echo  Skipping torch installation.
) else (
    echo  Invalid choice — skipping torch.
)
echo.

REM ── STEP 3: Python dependencies ─────────────────────────────────
echo ================================================================
echo  STEP 3 — Python dependencies
echo ================================================================
echo  Installing from deploy\requirements.txt ...
pip install -r deploy\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [!!] pip install failed — check logs above
    pause & exit /b 1
)
echo  [OK] Python dependencies installed
echo.

REM ── STEP 4: Node.js (Three.js for frontend) ─────────────────────
echo ================================================================
echo  STEP 4 — Node.js / Three.js
echo ================================================================
if exist "node_modules\three\build\three.module.js" (
    echo  [OK] Three.js already installed
) else (
    echo  Installing Three.js ...
    npm install three --no-fund --no-audit --quiet
    if %errorlevel% neq 0 (
        echo  [!!] npm install failed
    ) else (
        echo  [OK] Three.js installed
    )
)
echo.

REM ── STEP 5: Download HF models ──────────────────────────────────
echo ================================================================
echo  STEP 5 — Download Hugging Face models
echo ================================================================
echo.
echo  REQUIRED models (needed for search):
echo    - perplexity-ai/pplx-embed-context-v1-4b  (~8 GB, for indexing)
echo    - perplexity-ai/pplx-embed-v1-4b           (~8 GB, for query)
echo    - BAAI/bge-m3                               (~2 GB, ColBERT rerank)
echo.
echo  OPTIONAL models:
echo    - Petr117/m2m-diagnostica-automotive        (~2 GB, translations)
echo.
set /p DL_MODELS="Download models now? (y/n): "

if /i "%DL_MODELS%"=="y" (
    echo  Downloading models (this may take 30-60 min depending on connection)...
    echo  Tip: models are cached to %%USERPROFILE%%\.cache\huggingface\hub\
    echo.

    python -c "
from huggingface_hub import snapshot_download
import os

models = [
    ('BAAI/bge-m3', '~2 GB - ColBERT reranker'),
    ('perplexity-ai/pplx-embed-v1-4b', '~8 GB - query embeddings'),
    ('perplexity-ai/pplx-embed-context-v1-4b', '~8 GB - document embeddings'),
]
for model_id, desc in models:
    print(f'Downloading {model_id} ({desc})...')
    try:
        snapshot_download(repo_id=model_id, local_files_only=False)
        print(f'  OK: {model_id}')
    except Exception as e:
        print(f'  ERROR: {e}')
"
) else (
    echo  Skipped. Run manually:
    echo    python -c "from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-m3')"
)
echo.

REM ── STEP 6: Verify knowledge-base files ─────────────────────────
echo ================================================================
echo  STEP 6 — Check knowledge-base files
echo ================================================================
if exist "knowledge-base\kb.db" (
    echo  [OK] kb.db found
) else (
    echo  [!!] kb.db NOT FOUND
    echo       Copy from source machine:
    echo         knowledge-base\kb.db          (4.2 GB)
    echo         knowledge-base\lancedb\        (0.6 GB)
    echo         mineru-output\                 (2 GB, images)
)
if exist "knowledge-base\lancedb\content_emb.lance" (
    echo  [OK] LanceDB content_emb found
) else (
    echo  [!!] LanceDB NOT FOUND — copy knowledge-base\lancedb\ from source
)
echo.

REM ── STEP 7: Update API config path ──────────────────────────────
echo ================================================================
echo  STEP 7 — Config paths
echo ================================================================
echo  Checking api\config.py ...
python -c "
import sys, os
sys.path.insert(0, 'api')
try:
    import config
    print('  [OK] api/config.py loaded')
except Exception as e:
    print('  [!] config error:', e)
"
echo.

REM ── STEP 8: Run verification ─────────────────────────────────────
echo ================================================================
echo  STEP 8 — Final verification
echo ================================================================
python deploy\check_deploy.py
echo.

REM ── DONE ────────────────────────────────────────────────────────
echo ================================================================
echo  Setup complete!
echo.
echo  To start the application:
echo    start-diagnostica.bat      (or see below for manual start)
echo.
echo  Manual start:
echo    Terminal 1: .venv\Scripts\activate ^&^& uvicorn api.server:app --host 0.0.0.0 --port 8000
echo    Terminal 2: npx http-server -p 8080
echo    Browser:    http://localhost:8080/frontend/
echo ================================================================
echo.
pause
