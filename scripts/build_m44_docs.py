"""
Builds Milestone 4.4 Technical Documentation in Markdown, DOCX, and PDF formats.
Integrates Sections 1 through 22 from modular generator parts.
"""
import os
import sys
import re
import time
from pathlib import Path

# Third-party document generators
import markdown
import fitz
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import modular documentation sections
import scripts.doc_part1 as p1
import scripts.doc_part2 as p2
import scripts.doc_part3 as p3
import scripts.doc_part4 as p4
import scripts.doc_part5 as p5
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

MD_PATH = DOCS_DIR / "M4.4_TECHNICAL_DOCUMENTATION.md"
DOCX_PATH = DOCS_DIR / "M4.4_TECHNICAL_DOCUMENTATION.docx"
PDF_PATH = DOCS_DIR / "M4.4_TECHNICAL_DOCUMENTATION.pdf"

print("=" * 70)
print("BUILDING MILESTONE 4.4 TECHNICAL DOCUMENTATION SUITE")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. ASSEMBLE FULL MARKDOWN DOCUMENT
# ----------------------------------------------------------------------
print("\n[Step 1/3] Assembling full technical documentation in Markdown...")

ALL_SECTIONS = [
    p1.TITLE_AND_TOC,
    p1.SECTION_1,
    p1.SECTION_2,
    p1.SECTION_3,
    p2.SECTION_4,
    p2.SECTION_5,
    p2.SECTION_6,
    p2.SECTION_7,
    p3.SECTION_8,
    p3.SECTION_9,
    p3.SECTION_10,
    p4.SECTION_11,
    p4.SECTION_12,
    p4.SECTION_13,
    p4.SECTION_14,
    p5.SECTION_15,
    p5.SECTION_16,
    p5.SECTION_17,
    p5.SECTION_18,
    p5.SECTION_19,
    p5.SECTION_20,
    p5.SECTION_21,
    p5.SECTION_22
]

full_markdown = "\n\n".join(ALL_SECTIONS)

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(full_markdown)

md_size_kb = len(full_markdown.encode('utf-8')) / 1024
print(f" -> Created: {MD_PATH}")
print(f" -> Total Characters: {len(full_markdown):,}")
print(f" -> File Size: {md_size_kb:.1f} KB")

# ----------------------------------------------------------------------
# 2. GENERATE PROFESSIONAL MICROSOFT WORD (DOCX) DOCUMENT
# ----------------------------------------------------------------------
print("\n[Step 2/3] Generating professional DOCX specification...")

doc = docx.Document()

# Configure page margins: 1 inch (72pt)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Configure default font
normal_style = doc.styles['Normal']
normal_style.font.name = 'Calibri'
normal_style.font.size = Pt(10.5)
normal_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

# Helper XML styling functions
def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D1D5DB", sz="4"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), sz)
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), color)
            tblBorders.append(border)
        border = OxmlElement('w:insideV')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
        tblPr[0].append(tblBorders)

def add_formatted_runs(paragraph, text_line, base_size=10.5, default_bold=False):
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\))', text_line)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**') and len(token) >= 4:
            run = paragraph.add_run(token[2:-2])
            run.bold = True
            run.font.size = Pt(base_size)
        elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
            run = paragraph.add_run(token[1:-1])
            run.italic = True
            run.font.size = Pt(base_size)
        elif token.startswith('`') and token.endswith('`') and len(token) >= 2:
            run = paragraph.add_run(token[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(max(8.5, base_size - 1))
            run.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)
        elif token.startswith('[') and '](' in token and token.endswith(')'):
            m = re.match(r'\[(.*?)\]\((.*?)\)', token)
            if m:
                label, url = m.groups()
                run = paragraph.add_run(label)
                run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
                run.underline = True
                run.font.size = Pt(base_size)
            else:
                run = paragraph.add_run(token)
                run.font.size = Pt(base_size)
        else:
            run = paragraph.add_run(token)
            run.font.size = Pt(base_size)
            if default_bold:
                run.bold = True

lines = full_markdown.splitlines()
idx = 0
num_lines = len(lines)

while idx < num_lines:
    line = lines[idx]
    stripped = line.strip()

    # Skip empty lines
    if not stripped:
        idx += 1
        continue

    # 1. Code blocks (```)
    if stripped.startswith("```"):
        lang = stripped[3:].strip()
        code_lines = []
        idx += 1
        while idx < num_lines and not lines[idx].strip().startswith("```"):
            code_lines.append(lines[idx])
            idx += 1
        idx += 1 # skip closing ```
        
        # Render code block in single-cell shaded table
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.1
        code_text = "\n".join(code_lines)
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        
        # Add a subtle border
        set_table_borders(tbl, color="CBD5E1", sz="6")
        doc.add_paragraph() # spacer
        continue

    # 2. Markdown Tables (| col1 | col2 |)
    if stripped.startswith("|") and stripped.endswith("|") and idx + 1 < num_lines and "---" in lines[idx + 1]:
        raw_headers = [c.strip() for c in stripped.split("|")[1:-1]]
        idx += 2 # skip header and separator line
        table_rows = []
        while idx < num_lines and lines[idx].strip().startswith("|") and lines[idx].strip().endswith("|"):
            row_cols = [c.strip() for c in lines[idx].strip().split("|")[1:-1]]
            table_rows.append(row_cols)
            idx += 1

        num_cols = len(raw_headers)
        tbl = doc.add_table(rows=len(table_rows) + 1, cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="D1D5DB", sz="4")

        # Style header row
        hdr_row = tbl.rows[0]
        for col_idx, h_text in enumerate(raw_headers):
            cell = hdr_row.cells[col_idx]
            set_cell_background(cell, "1E3A8A") # Navy header
            set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, h_text, base_size=9.5, default_bold=True)
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) # White text

        # Style data rows
        for r_idx, r_data in enumerate(table_rows):
            row = tbl.rows[r_idx + 1]
            bg_color = "F9FAFB" if (r_idx % 2 == 1) else "FFFFFF"
            for col_idx in range(num_cols):
                cell = row.cells[col_idx]
                if bg_color != "FFFFFF":
                    set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                val_text = r_data[col_idx] if col_idx < len(r_data) else ""
                add_formatted_runs(p, val_text, base_size=9.0)

        doc.add_paragraph() # spacer
        continue

    # 3. Headings
    if stripped.startswith("# "):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped[2:])
        run.bold = True
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Deep Navy
        idx += 1
        continue
    elif stripped.startswith("## "):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped[3:])
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        idx += 1
        continue
    elif stripped.startswith("### "):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped[4:])
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB) # Slate Blue
        idx += 1
        continue
    elif stripped.startswith("#### "):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped[5:])
        run.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x37, 0x41, 0x51)
        idx += 1
        continue

    # 4. Blockquotes / Callout boxes (> ...)
    if stripped.startswith("> "):
        callout_lines = []
        while idx < num_lines and lines[idx].strip().startswith(">"):
            c_line = lines[idx].strip()[1:].strip()
            callout_lines.append(c_line)
            idx += 1
        
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "EFF6FF") # Soft Blue
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        c_text = " ".join(callout_lines)
        add_formatted_runs(p, c_text, base_size=10.0)
        
        # Add thick blue left border
        tblPr = tbl._element.xpath('w:tblPr')
        if tblPr:
            tblBorders = OxmlElement('w:tblBorders')
            border = OxmlElement('w:left')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '24') # thick border
            border.set(qn('w:color'), '2563EB')
            tblBorders.append(border)
            tblPr[0].append(tblBorders)
            
        doc.add_paragraph() # spacer
        continue

    # 5. Lists (- or * or numbered)
    if stripped.startswith("- ") or stripped.startswith("* "):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        add_formatted_runs(p, stripped[2:], base_size=10.0)
        idx += 1
        continue
    elif re.match(r'^\d+\.\s', stripped):
        p = doc.add_paragraph(style='List Number')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        m = re.match(r'^\d+\.\s*(.*)', stripped)
        add_formatted_runs(p, m.group(1), base_size=10.0)
        idx += 1
        continue

    # 6. Horizontal Rules (---)
    if stripped == "---":
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run("?" * 45)
        run.font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)
        idx += 1
        continue

    # 7. Standard Paragraphs
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    add_formatted_runs(p, stripped, base_size=10.5)
    idx += 1

doc.save(DOCX_PATH)
docx_size_kb = os.path.getsize(DOCX_PATH) / 1024
print(f" -> Created: {DOCX_PATH}")
print(f" -> File Size: {docx_size_kb:.1f} KB")

# ----------------------------------------------------------------------
# 3. GENERATE COMPLETE PDF DOCUMENT VIA FITZ STORY
# ----------------------------------------------------------------------
print("\n[Step 3/3] Generating mentor-ready PDF document...")

# Convert Markdown to HTML with tables & code fences
html_body = markdown.markdown(
    full_markdown,
    extensions=['tables', 'fenced_code']
)

# Professional CSS stylesheet for PDF publication
full_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.45;
    color: #1F2937;
  }}
  h1 {{
    color: #1E3A8A;
    font-size: 18pt;
    border-bottom: 2px solid #1E3A8A;
    padding-bottom: 4px;
    margin-top: 22pt;
    margin-bottom: 8pt;
  }}
  h2 {{
    color: #1E3A8A;
    font-size: 14pt;
    border-bottom: 1px solid #E5E7EB;
    padding-bottom: 3px;
    margin-top: 16pt;
    margin-bottom: 6pt;
  }}
  h3 {{
    color: #2563EB;
    font-size: 11.5pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
  }}
  h4 {{
    color: #374151;
    font-size: 10pt;
    font-weight: bold;
    margin-top: 8pt;
    margin-bottom: 3pt;
  }}
  p {{
    margin-top: 2pt;
    margin-bottom: 6pt;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 8pt;
    margin-bottom: 10pt;
    font-size: 8.5pt;
  }}
  th, td {{
    border: 1px solid #D1D5DB;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background-color: #1E3A8A;
    color: #FFFFFF;
    font-weight: bold;
  }}
  tr:nth-child(even) {{
    background-color: #F9FAFB;
  }}
  pre {{
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 3pt;
    padding: 6pt 8pt;
    font-family: Courier, monospace;
    font-size: 8pt;
    line-height: 1.3;
    white-space: pre-wrap;
    word-break: break-all;
    margin-top: 6pt;
    margin-bottom: 8pt;
  }}
  code {{
    font-family: Courier, monospace;
    background-color: #F3F4F6;
    color: #991B1B;
    padding: 1pt 3pt;
    font-size: 8.5pt;
  }}
  pre code {{
    background-color: transparent;
    color: #1E293B;
    padding: 0;
  }}
  blockquote {{
    border-left: 4px solid #2563EB;
    background-color: #EFF6FF;
    margin-left: 0;
    margin-right: 0;
    padding: 6pt 10pt;
    font-style: normal;
    color: #1E3A8A;
  }}
  ul, ol {{
    margin-top: 2pt;
    margin-bottom: 6pt;
    padding-left: 18pt;
  }}
  li {{
    margin-bottom: 2pt;
  }}
  hr {{
    border: none;
    border-top: 1px solid #D1D5DB;
    margin: 14pt 0;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>'''

story = fitz.Story(html=full_html)
writer = fitz.DocumentWriter(str(PDF_PATH))
# Standard Letter: 612 x 792 pt, 0.75 in (54 pt) margins
mediabox = fitz.Rect(0, 0, 612, 792)
content_rect = fitz.Rect(45, 45, 567, 747)

story.write(writer, lambda n, f: (mediabox, content_rect, fitz.Identity))
writer.close()

# Verify PDF page count
pdf_doc = fitz.open(PDF_PATH)
pdf_pages = len(pdf_doc)
pdf_doc.close()

pdf_size_kb = os.path.getsize(PDF_PATH) / 1024
print(f" -> Created: {PDF_PATH}")
print(f" -> Page Count: {pdf_pages} pages")
print(f" -> File Size: {pdf_size_kb:.1f} KB")

print("\n" + "=" * 70)
print("SUCCESS: ALL 3 M4.4 TECHNICAL DOCUMENTATION ARTIFACTS GENERATED!")
print("=" * 70)
