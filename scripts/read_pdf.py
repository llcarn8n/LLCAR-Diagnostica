import fitz
import sys, os

path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "english-russian.pdf")
doc = fitz.open(path)

# Extract sample pages as images for visual reading
pages_to_extract = [5, 10, 15, 20, 25, 30, 32]  # spread across the book
for i in pages_to_extract:
    if i < len(doc):
        page = doc[i]
        images = page.get_images(full=True)
        if images:
            xref = images[0][0]
            pix = fitz.Pixmap(doc, xref)
            out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"_page{i+1}_sample.png")
            pix.save(out_path)
            print(f"Page {i+1}: saved {pix.width}x{pix.height}")
            pix = None
