"""Second pass: image positions, table styles, headers/footers."""
from docx import Document
from docx.oxml.ns import qn

doc = Document('Experiment 2 .docx')
out = []

out.append("=== IMAGE POSITIONS (paragraph index -> rid, size EMU) ===")
for i, p in enumerate(doc.paragraphs):
    for blip in p._element.findall('.//' + qn('a:blip')):
        rid = blip.get(qn('r:embed'))
        ext = blip.getparent().getparent().find(qn('a:ext'))
        cx = ext.get('cx') if ext is not None else '?'
        cy = ext.get('cy') if ext is not None else '?'
        dims = ""
        if cx is not None and cx.isdigit():
            dims = f" ({int(cx)//914400:.2f}x{int(cy)//914400:.2f} in)"
        out.append(f"  para[{i}] rid={rid} size={cx}x{cy} EMU{dims}")

out.append("\n=== TABLE STYLES ===")
for ti, t in enumerate(doc.tables):
    out.append(f"  table {ti}: style={t.style.name if t.style else None}")
    tblPr = t._element.tblPr
    borders = tblPr.find(qn('w:tblBorders')) if tblPr is not None else None
    out.append(f"    has tblBorders: {borders is not None}")

out.append("\n=== HEADERS / FOOTERS ===")
for si, s in enumerate(doc.sections):
    hdr = s.header
    ftr = s.footer
    out.append(f"section {si}: header_linked={hdr.is_linked_to_previous}, footer_linked={ftr.is_linked_to_previous}")
    for p in hdr.paragraphs:
        if p.text.strip():
            out.append(f"  header text: {p.text}")
    for p in ftr.paragraphs:
        if p.text.strip():
            out.append(f"  footer text: {p.text}")
    # check for page numbers (fldSimple PAGE)
    for fld in ftr._element.findall('.//' + qn('w:fldSimple')):
        out.append(f"  footer field: {fld.get(qn('w:instr'))}")

out.append("\n=== STYLE DEFINITIONS (key ones) ===")
for sname in ['Normal', 'Heading 1', 'ds-markdown-paragraph']:
    try:
        st = doc.styles[sname]
        f = st.font
        out.append(f"  {sname}: font={f.name}, size={f.size.pt if f.size else None}, bold={f.bold}")
        rpr = st.element.find(qn('w:rPr'))
        if rpr is not None:
            rf = rpr.find(qn('w:rFonts'))
            if rf is not None:
                out.append(f"    rFonts: ascii={rf.get(qn('w:ascii'))} eastAsia={rf.get(qn('w:eastAsia'))} hAnsi={rf.get(qn('w:hAnsi'))}")
    except KeyError:
        out.append(f"  {sname}: NOT FOUND")

with open('_docx_analysis2.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("written")
