"""
Wrapper to run MinerU via isolated Python 3.11 venv (.venv-mineru).
Fixes RecursionError in BeautifulSoup deepcopy for complex tables.

Usage:
    python scripts/run_mineru.py -p <pdf_path> -o <output_dir> [-m auto] [-l ru]

Examples:
    python scripts/run_mineru.py -p knowledge-base/raw-pdfs/manual.pdf -o mineru-output -l ru
    python scripts/run_mineru.py -p manual.pdf -o out -l en

CLI: magic-pdf.exe (NOT mineru.exe - CLI was renamed in v1.3+)
MinerU venv: C:/Diagnostica-KB-Package/.venv-mineru (Python 3.11, magic-pdf 1.3.12)
Config: C:/Users/BAZA/.magic-pdf/magic-pdf.json
Models: ~/.cache/huggingface/hub/models--opendatalab--PDF-Extract-Kit-1.0/...
"""
import sys
import subprocess
import os
from pathlib import Path

# Path to MinerU venv - Python 3.11 isolated environment
VENV_DIR = Path("C:/Diagnostica-KB-Package/.venv-mineru")
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
VENV_MAGIC_PDF = VENV_DIR / "Scripts" / "magic-pdf.exe"


def check_venv():
    """Verify venv exists and magic-pdf is installed."""
    if not VENV_PYTHON.exists():
        print(f"ERROR: venv not found at {VENV_DIR}")
        print("Create it with:")
        print("  py -3.11 -m venv C:/Diagnostica-KB-Package/.venv-mineru")
        print("  C:/Diagnostica-KB-Package/.venv-mineru/Scripts/pip.exe install 'magic-pdf[full]'")
        sys.exit(1)

    if not VENV_MAGIC_PDF.exists():
        print(f"ERROR: magic-pdf.exe not found in venv at {VENV_MAGIC_PDF}")
        print("Install magic-pdf with:")
        print(f"  {VENV_PYTHON} -m pip install 'magic-pdf[full]'")
        sys.exit(1)


def run_magic_pdf(args):
    """Run magic-pdf CLI in venv with all passed arguments."""
    env = os.environ.copy()
    env["PYTHONRECURSIONLIMIT"] = "10000"

    cmd = [str(VENV_MAGIC_PDF)] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        print("magic-pdf CLI options:")
        subprocess.run([str(VENV_MAGIC_PDF), "--help"] if VENV_MAGIC_PDF.exists() else ["echo", "venv not ready"])
        sys.exit(0)

    check_venv()
    sys.exit(run_magic_pdf(args))
