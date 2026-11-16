from pathlib import Path
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "report_figures"


def _remove_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "none")
        borders.append(el)
    tblPr.append(borders)


def add_geu_front_page(doc: docx.Document) -> None:
    """Render the exact Graphic Era front page matching PROJECT_REPORT_Vardhaman.pdf."""
    def _center_p(text: str, size: float, bold: bool = True, italic: bool = False, space_after: float = 6, space_before: float = 0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = "Bookman Old Style"
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        return p

    _center_p("Report ON", size=15, bold=True, space_before=6, space_after=6)

    rule_img = FIG_DIR / "geu_logo_3.png"
    if rule_img.exists():
        pr1 = doc.add_paragraph()
        pr1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pr1.paragraph_format.space_after = Pt(8)
        pr1.add_run().add_picture(str(rule_img), width=Inches(6.0))

    _center_p("TARANG — Mapping the Invisible", size=16, bold=True, space_after=4)
    _center_p(
        "(A Local-First Hybrid Wi-Fi and Cellular Network Surveying Platform)",
        size=11.5,
        bold=True,
        space_after=8,
    )

    if rule_img.exists():
        pr2 = doc.add_paragraph()
        pr2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pr2.paragraph_format.space_after = Pt(14)
        pr2.add_run().add_picture(str(rule_img), width=Inches(6.0))

    _center_p(
        "Submitted in partial fulfilment of the requirement for the award of the\ndegree of",
        size=11.5,
        bold=True,
        space_after=14,
    )
    _center_p(
        "Bachelors OF COMPUTER APPLICATIONS (CyberSecurity)",
        size=11.5,
        bold=True,
        space_after=20,
    )

    _center_p("Submitted by:", size=11, bold=True, space_after=8)

    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    _remove_table_borders(tbl)
    c_left, c_right = tbl.rows[0].cells[0], tbl.rows[0].cells[1]
    c_left.width = Inches(3.0)
    c_right.width = Inches(3.0)

    pl = c_left.paragraphs[0]
    pl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rl = pl.add_run("Shivam Kumar")
    rl.bold = True
    rl.font.name = "Bookman Old Style"
    rl.font.size = Pt(11.5)

    pr = c_right.paragraphs[0]
    pr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rr = pr.add_run("University Roll No. 2105130")
    rr.bold = True
    rr.font.name = "Bookman Old Style"
    rr.font.size = Pt(11.5)

    _center_p("Under the Guidance of", size=11.5, bold=False, italic=True, space_before=22, space_after=4)
    _center_p("Mr. Mukesh Singh", size=12, bold=True, space_after=24)

    seal_img = FIG_DIR / "geu_logo_1.jpeg"
    if seal_img.exists():
        ps = doc.add_paragraph()
        ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ps.paragraph_format.space_after = Pt(18)
        ps.add_run().add_picture(str(seal_img), width=Inches(1.25))

    _center_p(
        "Department of Computer Science and Engineering\n"
        "Graphic Era (Deemed to be University)\n"
        "Dehradun, Uttarakhand\n"
        "Batch: 2024–2027 | November-2026",
        size=13,
        bold=True,
        space_after=22,
    )

    banner_img = FIG_DIR / "geu_logo_2.jpeg"
    if banner_img.exists():
        pb = doc.add_paragraph()
        pb.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pb.paragraph_format.space_after = Pt(0)
        pb.add_run().add_picture(str(banner_img), width=Inches(3.2))


if __name__ == "__main__":
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11.0)
    sec.top_margin = Inches(0.85)
    sec.bottom_margin = Inches(0.75)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)
    add_geu_front_page(doc)
    out_docx = ROOT / "docs" / "TARANG_Front_Page_Shivam_Kumar.docx"
    doc.save(str(out_docx))
    print("Saved front page to:", out_docx)
