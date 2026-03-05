import json, os, re

print("=== INTEGRATION TESTS ===")

kb_path = "Diagnostica/knowledge-base"

# 1. Check component-knowledge.js can find the right files
print("\n--- File Path Resolution ---")
for model in ["li7", "li9"]:
    prefix = "l7" if model == "li7" else "l9"

    config_file = os.path.join(kb_path, f"{prefix}-config.json")
    exists = os.path.exists(config_file)
    print(f"  {model} config ({prefix}-config.json): {'PASS' if exists else 'FAIL'}")

    comp_file = os.path.join(kb_path, f"{model}-component-map.json")
    exists = os.path.exists(comp_file)
    print(f"  {model} component-map ({model}-component-map.json): {'PASS' if exists else 'FAIL'}")

# 2. Check model GLB paths referenced in diagnostica.html
print("\n--- GLB Model References ---")
with open("examples/diagnostica.html", "r", encoding="utf-8") as f:
    html = f.read()

glb_refs = re.findall(r'["\']([^"\']*\.glb)["\']', html)
print(f"  GLB references: {glb_refs}")
for ref in glb_refs:
    print(f"    Model path: {ref}")

# 3. Glossary term count
print("\n--- Glossary Validation ---")
with open(os.path.join(kb_path, "automotive-glossary-trilingual.json"), "r", encoding="utf-8") as f:
    glossary = json.load(f)
actual_terms = sum(len(cat.get("terms", [])) for cat in glossary.get("categories", {}).values())
meta_terms = glossary.get("meta", {}).get("total_terms", 0)
print(f"  Meta says {meta_terms} terms, actual count is {actual_terms}")
if meta_terms != actual_terms:
    print(f"  WARN: meta.total_terms needs update to {actual_terms}")

# 4. Check Three.js version
pkg_path = "node_modules/three/package.json"
if os.path.exists(pkg_path):
    with open(pkg_path, "r") as f:
        pkg = json.load(f)
    version = pkg.get("version", "unknown")
    print(f"\n--- Three.js ---")
    print(f"  Version: {version}")

# 5. Check Draco decoder files
draco_path = "node_modules/three/examples/jsm/libs/draco"
if os.path.exists(draco_path):
    files = os.listdir(draco_path)
    print(f"\n--- Draco Decoder ---")
    print(f"  Files ({len(files)}): {files}")
else:
    print(f"\n  FAIL: Draco decoder not found at {draco_path}")

# 6. Check DRACOLoader.js exists in Three.js
draco_loader = "node_modules/three/examples/jsm/loaders/DRACOLoader.js"
if os.path.exists(draco_loader):
    print(f"  DRACOLoader.js: PASS")
else:
    print(f"  DRACOLoader.js: FAIL - not found")

# 7. File size summary
print("\n--- Artifact Sizes ---")
artifacts = [
    "examples/diagnostica.html",
    "js/claude-api.js",
    "js/component-knowledge.js",
    "Diagnostica/knowledge-base/li7-component-map.json",
    "Diagnostica/knowledge-base/li9-component-map.json",
    "Diagnostica/knowledge-base/automotive-glossary-trilingual.json",
    "Diagnostica/scripts/generate_component_maps.py",
    "Diagnostica/scripts/extract_pdf_data.py",
    "Diagnostica/architecture/pipeline-design.md",
]
total_size = 0
for art in artifacts:
    if os.path.exists(art):
        size = os.path.getsize(art)
        total_size += size
        lines = len(open(art, "r", encoding="utf-8").readlines())
        print(f"  {art}: {size/1024:.1f}KB, {lines} lines")
    else:
        print(f"  {art}: NOT FOUND")

print(f"\n  Total: {total_size/1024:.1f}KB ({total_size/1024/1024:.2f}MB)")

# 8. Check all knowledge-base files
print("\n--- Knowledge Base Inventory ---")
for fname in sorted(os.listdir(kb_path)):
    fpath = os.path.join(kb_path, fname)
    size = os.path.getsize(fpath)
    print(f"  {fname}: {size/1024:.1f}KB")

print("\n=== INTEGRATION TESTS COMPLETE ===")
