#!/usr/bin/env python3
"""
check_deploy.py — Verify LLCAR Diagnostica is correctly set up on this machine.

Run after deploy.bat, or standalone:
    python deploy/check_deploy.py
    python deploy/check_deploy.py --start-api   # also start API and test it
"""
from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
OK = "[OK]"
WARN = "[!!]"
INFO = "[ ]"

passed = 0
failed = 0
warnings = 0


def check(label: str, condition: bool, fatal: bool = False, hint: str = "") -> bool:
    global passed, failed, warnings
    if condition:
        print(f"  {OK}  {label}")
        passed += 1
    else:
        marker = WARN
        print(f"  {marker}  {label}")
        if hint:
            print(f"        -> {hint}")
        if fatal:
            failed += 1
        else:
            warnings += 1
    return condition


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


# ── 1. Python ──────────────────────────────────────────────────────
section("1. Python & Core Packages")

check("Python 3.11+",
      sys.version_info >= (3, 11),
      fatal=True,
      hint=f"Current: {sys.version.split()[0]}  Need: 3.11+")

try:
    import torch
    cuda_ok = torch.cuda.is_available()
    check(f"torch {torch.__version__}", True)
    check("CUDA available", cuda_ok,
          hint="GPU needed for embeddings. CPU fallback available but very slow.")
    if cuda_ok:
        for i in range(torch.cuda.device_count()):
            p = torch.cuda.get_device_properties(i)
            free = torch.cuda.mem_get_info(i)[0] / 1_073_741_824
            print(f"        GPU {i}: {p.name}  {free:.1f}/{p.total_memory//1_073_741_824} GB free")
except ImportError:
    check("torch installed", False, fatal=True,
          hint="Run: pip install torch --index-url https://download.pytorch.org/whl/cu121")

for pkg in ["fastapi", "uvicorn", "lancedb", "transformers", "sentence_transformers",
            "accelerate", "huggingface_hub", "numpy", "pydantic"]:
    try:
        import importlib
        mod = importlib.import_module(pkg.replace("-", "_"))
        ver = getattr(mod, "__version__", "?")
        check(f"{pkg} ({ver})", True)
    except ImportError:
        check(pkg, False, hint=f"pip install {pkg}")

# FlagEmbedding check via metadata (import may fail on transformers version mismatch)
try:
    import importlib.metadata as _meta
    ver = _meta.version("FlagEmbedding")
    check(f"FlagEmbedding ({ver})", True)
except Exception:
    check("FlagEmbedding", False, hint="pip install FlagEmbedding")


# ── 2. Node.js / Three.js ─────────────────────────────────────────
section("2. Node.js / Frontend")

import shutil
node_ok = shutil.which("node") is not None
check("node available", node_ok, hint="Install from nodejs.org")
npm_ok = shutil.which("npm") is not None
check("npm available", npm_ok)

three_js = ROOT / "node_modules" / "three" / "build" / "three.module.js"
check("Three.js installed", three_js.exists(),
      hint="Run: npm install three  (from project root)")


# ── 3. Knowledge Base ─────────────────────────────────────────────
section("3. Knowledge Base Files")

import sqlite3

kb_db = ROOT / "knowledge-base" / "kb.db"
check("kb.db exists", kb_db.exists(), fatal=True,
      hint="Copy knowledge-base/kb.db (4.2 GB) from source machine")

if kb_db.exists():
    try:
        with sqlite3.connect(kb_db) as conn:
            chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            cc = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]
            col = conn.execute("SELECT COUNT(*) FROM colbert_vectors").fetchone()[0]
        check(f"chunks: {chunks:,}", chunks > 10000,
              hint="Expected 11,000+")
        check(f"chunk_content (translations): {cc:,}", cc > 20000)
        check(f"colbert_vectors: {col:,}", col > 10000)
    except Exception as e:
        check("kb.db readable", False, fatal=True, hint=str(e))

ldb_dir = ROOT / "knowledge-base" / "lancedb"
check("lancedb/ dir exists", ldb_dir.exists(),
      hint="Copy knowledge-base/lancedb/ (0.6 GB) from source machine")

for table in ["content_emb.lance", "title_emb.lance", "image_emb.lance"]:
    check(f"  lancedb/{table}", (ldb_dir / table).exists())


# ── 4. HuggingFace Models ─────────────────────────────────────────
section("4. HuggingFace Models")

try:
    from huggingface_hub import try_to_load_from_cache
    HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"

    models_needed = [
        ("BAAI/bge-m3",                          "bge-m3",                 "ColBERT reranker"),
        ("perplexity-ai/pplx-embed-v1-4b",        "pplx-embed-v1-4b",      "query embeddings"),
        ("perplexity-ai/pplx-embed-context-v1-4b","pplx-embed-context-v1-4b","doc embeddings"),
    ]
    models_optional = [
        ("Petr117/m2m-diagnostica-automotive",    "m2m-diagnostica",        "translation model"),
    ]

    def model_cached(repo_id: str) -> bool:
        slug = "models--" + repo_id.replace("/", "--")
        d = HF_CACHE / slug
        if not d.exists():
            return False
        return any(d.rglob("*.safetensors")) or any(d.rglob("*.bin"))

    for repo_id, slug, desc in models_needed:
        check(f"{slug}  ({desc})", model_cached(repo_id),
              hint=f"python -c \"from huggingface_hub import snapshot_download; snapshot_download('{repo_id}')\"")

    for repo_id, slug, desc in models_optional:
        ok = model_cached(repo_id)
        marker = OK if ok else "[ ]"
        print(f"  {marker}  {slug}  ({desc}) — optional")

except Exception as e:
    print(f"  [!]  HF cache check failed: {e}")


# ── 5. API Server ─────────────────────────────────────────────────
section("5. API Server (localhost:8000)")

def test_api() -> bool:
    try:
        r = urllib.request.urlopen("http://localhost:8000/health", timeout=3)
        data = json.loads(r.read())
        chunks = data.get("chunks_total", 0)
        ldb = data.get("lancedb_available", False)
        print(f"        chunks_total: {chunks:,}")
        print(f"        lancedb:      {'available' if ldb else 'NOT available'}")
        return True
    except Exception as e:
        return False

api_running = test_api()
check("API running at :8000", api_running,
      hint="Start: uvicorn api.server:app --host 0.0.0.0 --port 8000")


# ── 6. Web Server ─────────────────────────────────────────────────
section("6. Web Server (localhost:8080)")

def test_web() -> bool:
    try:
        urllib.request.urlopen("http://localhost:8080/frontend/", timeout=3)
        return True
    except:
        return False

web_ok = test_web()
check("Web server at :8080", web_ok,
      hint="Start: npx http-server -p 8080  (from project root)")

if web_ok:
    # Check app.js is served (not js/app.js)
    try:
        urllib.request.urlopen("http://localhost:8080/frontend/app.js", timeout=3)
        check("frontend/app.js served", True)
    except:
        check("frontend/app.js served", False,
              hint="index.html may reference js/app.js — should be app.js")

    try:
        urllib.request.urlopen(
            "http://localhost:8080/node_modules/three/build/three.module.js", timeout=3)
        check("Three.js served via HTTP", True)
    except:
        check("Three.js served via HTTP", False,
              hint="npm install three  (from project root)")


# ── 7. Quick search test ──────────────────────────────────────────
if api_running:
    section("7. Search API smoke test")
    try:
        body = json.dumps({"query": "brake", "lang": "en", "top_k": 3}).encode()
        req = urllib.request.Request(
            "http://localhost:8000/search", data=body,
            headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read())
        n = len(data.get("results", []))
        check(f"Search 'brake' -> {n} results", n > 0,
              hint="API returned 0 results - check embeddings")
        if n > 0:
            r0 = data["results"][0]
            score = r0.get("score", 0)
            print(f"        top score: {score:.3f}  (expect > 0.3 for hybrid_colbert)")
    except Exception as e:
        check("Search test", False, hint=str(e))


# ── Summary ───────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"  RESULT: {passed} passed, {warnings} warnings, {failed} fatal errors")
print('=' * 60)

if failed > 0:
    print(f"\n  {failed} fatal issue(s) must be fixed before the app will work.")
    sys.exit(1)
elif warnings > 0:
    print(f"\n  {warnings} warning(s) — app may work with reduced functionality.")
else:
    print("\n  All checks passed! App should be ready.")
    print("  Open: http://localhost:8080/frontend/")

print()
