"""Dump structure of the template docx to a UTF-8 text file for inspection."""
from docx import Document
from docx.shared import Pt

doc = Document('Experiment 2 .docx')
out = []

out.append("=== SECTIONS ===")
for s in doc.sections:
    out.append(f"page {s.page_width}x{s.page_height} margins L{s.left_margin} R{s.right_margin} T{s.top_margin} B{s.bottom_margin}")

out.append("\n=== PARAGRAPHS ===")
for i, p in enumerate(doc.paragraphs):
    if not p.text.strip():
        continue
    runs = []
    for r in p.runs[:3]:
        sz = r.font.size.pt if r.font.size else None
        runs.append(f"({r.font.name},sz={sz},b={r.font.bold},i={r.font.italic})")
    out.append(f"[{i}] style={p.style.name!r} align={p.alignment} runs={runs}")
    out.append(f"    {p.text}")

out.append("\n=== TABLES ===")
for ti, t in enumerate(doc.tables):
    out.append(f"--- table {ti}: {len(t.rows)} rows x {len(t.columns)} cols")
    for r in t.rows:
        out.append("   | " + " | ".join(c.text.strip().replace("\n", " / ") for c in r.cells))

out.append("\n=== INLINE IMAGES ===")
from docx.oxml.ns import qn
count = 0
for p in doc.paragraphs:
    blips = p._element.findall('.//' + qn('a:blip'))
    for b in blips:
        rid = b.get(qn('r:embed'))
        size = b.getparent().getparent().find(qn('a:ext'))
        cx = b.getparent().getparent().find(qn('a:ext'))
        out.append(f"  para with image rid={rid} ext={cx.get('cx') if cx is not None else '?'}x{cx.get('cy') if cx is not None else '?'}")
        count += 1
out.append(f"total inline images: {count}")

with open('_docx_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("written _docx_analysis.txt")
