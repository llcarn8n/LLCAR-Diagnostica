#!/usr/bin/env python3
"""
export_manuals_md.py — Export KB manual chunks as Markdown files with image references.

Generates one .md file per source (= per original PDF/document) in knowledge-base/manuals/.
Images are referenced as relative paths to mineru-output/ directory.
"""
import sqlite3
import os
import re
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge-base', 'kb.db')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge-base', 'manuals')
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _fix_content_image_paths(content: str, out_dir: str) -> str:
    """Fix image paths in content to be relative from out_dir to project root."""
    if not content or 'mineru-output/' not in content:
        return content

    def _replace_img(m):
        alt = m.group(1)
        path = m.group(2)
        # Strip any absolute prefix, keep from mineru-output/ onwards
        if 'mineru-output/' in path:
            rel = 'mineru-output/' + path.split('mineru-output/', 1)[1]
            # Compute relative path from out_dir to project_root/rel
            full = os.path.join(PROJECT_ROOT, rel)
            rel_path = os.path.relpath(full, out_dir).replace(os.sep, '/')
            return f'![{alt}]({rel_path})'
        return m.group(0)

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _replace_img, content)


def main():
    conn = sqlite3.connect(DB_PATH)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Get all manual sources
    sources = conn.execute("""
        SELECT source, model, source_language, COUNT(*) as cnt
        FROM chunks
        WHERE layer != 'web_scraped'
        GROUP BY source
        ORDER BY model, source
    """).fetchall()

    for src, model, src_lang, chunk_count in sources:
        # Get all chunks for this source, ordered by page
        chunks = conn.execute("""
            SELECT c.id, c.title, c.content, c.layer, c.page_start, c.page_end,
                   c.content_type, c.has_procedures, c.has_warnings
            FROM chunks c
            WHERE c.source = ?
            ORDER BY c.page_start, c.id
        """, (src,)).fetchall()

        fname = f"{model}_{src}.md"
        filepath = os.path.join(OUT_DIR, fname)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {src}\n\n")
            f.write(f"**Model:** Li Auto {model.upper()} | ")
            f.write(f"**Language:** {src_lang} | ")
            f.write(f"**Chunks:** {chunk_count}\n\n")
            f.write("---\n\n")

            current_layer = None

            for chunk_id, title, content, layer, pg_start, pg_end, ctype, has_proc, has_warn in chunks:
                # Layer section header
                if layer != current_layer:
                    current_layer = layer
                    f.write(f"\n# [{layer.upper()}]\n\n")

                # Chunk header
                title_str = title or "(untitled)"
                page_info = ""
                if pg_start:
                    page_info = f" (p.{pg_start}"
                    if pg_end and pg_end != pg_start:
                        page_info += f"-{pg_end}"
                    page_info += ")"

                badges = ""
                if has_proc:
                    badges += " [PROCEDURE]"
                if has_warn:
                    badges += " [WARNING]"

                f.write(f"## {title_str}{page_info}{badges}\n\n")
                f.write(f"*chunk_id: {chunk_id}*\n\n")

                # Content (fix embedded image paths to relative)
                if content:
                    f.write(_fix_content_image_paths(content, OUT_DIR))
                    f.write("\n\n")

                # Images for this chunk
                images = conn.execute("""
                    SELECT image_path, caption
                    FROM chunk_images
                    WHERE chunk_id = ?
                    ORDER BY image_path
                """, (chunk_id,)).fetchall()

                if images:
                    for img_path, caption in images:
                        # Normalize: ensure path starts with mineru-output/
                        if 'mineru-output/' in img_path:
                            img_path = 'mineru-output/' + img_path.split('mineru-output/', 1)[1]
                        # Compute relative path from OUT_DIR to project_root/img_path
                        full_img = os.path.join(PROJECT_ROOT, img_path)
                        rel_path = os.path.relpath(full_img, OUT_DIR)
                        rel_path = rel_path.replace(os.sep, '/')
                        caption_text = (caption[:120] if caption else "image").replace('\n', ' ')
                        f.write(f"![{caption_text}]({rel_path})\n\n")

                f.write("---\n\n")

        size_kb = os.path.getsize(filepath) / 1024
        print(f"  {fname}: {chunk_count} chunks, {size_kb:.0f} KB")

    # Generate INDEX
    _write_index(sources)

    total = sum(s[3] for s in sources)
    print(f"\nDone! {len(sources)} files, {total} chunks total")
    conn.close()


def _write_index(sources):
    descriptions = {
        'mineru_l7_zh_owners': "L7 Owner's Manual (MinerU OCR, ZH)",
        'pdf_l7_zh_full': "L7 Full Technical Manual (PDF, ZH)",
        'pdf_l7_zh': "L7 Technical Manual sections (PDF, ZH)",
        'web_l7_zh': "L7 Web content (lixiang.com, ZH)",
        'mineru_l7_zh_config': "L7 Configuration Guide (MinerU OCR, ZH)",
        'mineru_l9_ru': "L9 User Manual (MinerU OCR, RU)",
        'mineru_l9_zh_owners': "L9 Owner's Manual (MinerU OCR, ZH)",
        'pdf_l9_ru': "L9 User Manual (PDF, RU)",
        'pdf_l9_zh_full': "L9 Full Technical Manual (PDF, ZH)",
        'parts_l9_zh': "L9 Parts Catalog (ZH)",
        'pdf_l9_zh': "L9 Technical Manual sections (PDF, ZH)",
        'mineru_l9_zh_parts': "L9 Parts sections (MinerU OCR, ZH)",
        'mineru_l9_en_config': "L9 Configuration Guide (MinerU OCR, EN)",
        'mineru_l9_en': "L9 English sections (MinerU OCR, EN)",
        'dtc_database': "DTC Error Codes Database (L7+L9)",
    }

    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write("# User Manuals Index\n\n")
        f.write("Manual chunks exported from KB as Markdown files with image references.\n\n")
        f.write("**Images are referenced as relative paths to `mineru-output/` directory.**\n\n")
        f.write("| # | File | Model | Language | Chunks | Description |\n")
        f.write("|---|------|-------|----------|--------|-------------|\n")

        for i, (src, model, src_lang, cnt) in enumerate(sources, 1):
            fname = f"{model}_{src}.md"
            desc = descriptions.get(src, src)
            f.write(f"| {i} | [{fname}]({fname}) | {model.upper()} | {src_lang} | {cnt} | {desc} |\n")

        total = sum(s[3] for s in sources)
        f.write(f"\n**Total: {total} manual chunks, 4,475 unique images**\n\n")
        f.write("## Image References\n\n")
        f.write("All images are stored in `mineru-output/` directory at project root.\n")
        f.write("MD files use relative paths like `../../mineru-output/.../image.jpg`.\n")
        f.write("To view images correctly, open MD files from `knowledge-base/manuals/` directory.\n")

    print("  INDEX.md created")


if __name__ == '__main__':
    main()
