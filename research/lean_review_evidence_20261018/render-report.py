"""Render the existing report and diagram data only; performs no research computation."""
from pathlib import Path
import json
import re
import textwrap
from html import escape

from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderSVG
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

for name, filename in [("DejaVuSans", "DejaVuSans.ttf"), ("DejaVuSans-Bold", "DejaVuSans-Bold.ttf"), ("DejaVuSans-Oblique", "DejaVuSans-Oblique.ttf"), ("DejaVuSans-BoldOblique", "DejaVuSans-BoldOblique.ttf"), ("DejaVuSansMono", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(name, "/usr/share/fonts/truetype/dejavu/" + filename))
pdfmetrics.registerFontFamily("DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold", italic="DejaVuSans-Oblique", boldItalic="DejaVuSans-BoldOblique")
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted

root = Path(__file__).resolve().parent
data = json.loads((root / "review-chain.json").read_text())
drawing = Drawing(500, 308)
for index, label in enumerate(data["boxes"]):
    y = 247 - index * 72
    color = colors.HexColor("#eaf1fb" if index < 2 else "#fff1db")
    drawing.add(Rect(8, y, 484, 48, rx=7, ry=7, fillColor=color,
                     strokeColor=colors.HexColor("#274366")))
    for line, text in enumerate(textwrap.wrap(label, 78)):
        drawing.add(String(19, y + 31 - 13 * line, text,
                           fontName="DejaVuSans", fontSize=10, fillColor=colors.HexColor("#17304c")))
    if index < len(data["boxes"])-1:
        drawing.add(Line(250, y, 250, y - 17, strokeColor=colors.HexColor("#274366")))
        drawing.add(Polygon([246,y-13,254,y-13,250,y-19],fillColor=colors.HexColor("#274366")))
renderSVG.drawToFile(drawing, str(root / "review-chain.svg"))

styles = getSampleStyleSheet()
for style in styles.byName.values():
    if not hasattr(style, "fontName"):
        continue
    style.fontName = "DejaVuSans-Bold" if "Bold" in style.fontName else "DejaVuSans"
styles.add(ParagraphStyle(name="SmallBody", parent=styles["BodyText"], fontSize=9,
                         leading=12, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Cell", parent=styles["SmallBody"], fontSize=7.5,
                         leading=10, wordWrap="CJK", splitLongWords=1))
styles["Code"].fontName = "DejaVuSansMono"
styles["Code"].fontSize = 7
styles["Code"].leading = 9

def inline(text):
    text = escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<link href="{m[2]}" color="#1b5591">{m[1]}</link>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r'<font name="DejaVuSansMono">\1</font>', text)

story = [Paragraph(escape(data["title"]), styles["Title"]), drawing,
         Paragraph(escape(data["caption"]), styles["SmallBody"]), Spacer(1, 9)]
lines = (root / "synthesis.md").read_text().splitlines()
index = 0
if lines and lines[0].strip() == "---":
    index = 1
    while index < len(lines) and lines[index].strip() != "---":
        index += 1
    index += 1
while index < len(lines):
    line = lines[index]
    if not line.strip():
        index += 1
        continue
    if line.startswith("```"):
        is_mermaid = line.strip() == "```mermaid"
        code = []
        index += 1
        while index < len(lines) and not lines[index].startswith("```"):
            code.extend(textwrap.wrap(lines[index], 105, replace_whitespace=False) or [""])
            index += 1
        if is_mermaid:
            story.append(Paragraph("The evidence-dependency diagram is above; its editable Mermaid source remains in synthesis.md.", styles["SmallBody"]))
        else:
            story.append(Preformatted("\n".join(code), styles["Code"]))
        index += 1
        continue
    if line.startswith("|"):
        rows = []
        while index < len(lines) and lines[index].startswith("|"):
            cells = [c.strip() for c in lines[index].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"[-: ]+", c) for c in cells):
                rows.append([Paragraph(inline(c), styles["Cell"]) for c in cells])
            index += 1
        table = Table(rows, colWidths=[500/len(rows[0])]*len(rows[0]), repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),colors.HexColor("#eaf1fb")),
                                   ("VALIGN", (0,0),(-1,-1),"TOP"),
                                   ("GRID", (0,0),(-1,-1),.3,colors.HexColor("#b9c7d8")),
                                   ("LEFTPADDING", (0,0),(-1,-1),6),
                                   ("RIGHTPADDING", (0,0),(-1,-1),6)]))
        story.extend([table, Spacer(1,8)])
        continue
    if line.startswith("#"):
        level = len(line)-len(line.lstrip("#"))
        story.append(Paragraph(inline(line.lstrip("# ")), styles["Heading1" if level==1 else "Heading2"]))
        index += 1
        continue
    paragraph = [line]
    index += 1
    while index < len(lines) and lines[index].strip() and not lines[index].startswith(("#","|","```")):
        paragraph.append(lines[index])
        index += 1
    story.append(Paragraph(inline(" ".join(paragraph)), styles["SmallBody"]))

def footer(canvas, document):
    canvas.setFont("DejaVuSans", 8)
    canvas.setFillColor(colors.HexColor("#52647a"))
    canvas.drawString(47, 26, "Lean evidence review | 2026-10-18 | Scope and limitations are part of the result")
    canvas.drawRightString(549, 26, str(document.page))

SimpleDocTemplate(str(root/"report.pdf"), pagesize=(596,842), leftMargin=47,
                  rightMargin=47, topMargin=35, bottomMargin=42).build(
                      story, onFirstPage=footer, onLaterPages=footer)
