#!/usr/bin/env python3
"""Check image sizes in the test folder."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image

IMG_DIR = "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/images"

images = sorted(os.listdir(IMG_DIR))
print(f"Total images: {len(images)}")
print()
print(f"{'Image':<50} {'Size':>15} {'WxH':>15}")
print("-"*82)
for img_name in images[:30]:
    img_path = os.path.join(IMG_DIR, img_name)
    size_kb = os.path.getsize(img_path) / 1024
    try:
        with Image.open(img_path) as img:
            w, h = img.size
        print(f"{img_name[:48]:<50} {size_kb:>12.1f}KB {w}x{h:>6}")
    except Exception as e:
        print(f"{img_name[:48]:<50} ERROR: {e}")
