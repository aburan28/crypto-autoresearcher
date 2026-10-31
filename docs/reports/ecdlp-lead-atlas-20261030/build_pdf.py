#!/usr/bin/env python3
"""README.md -> report.pdf with reportlab (no Typst/LaTeX needed). Run from this directory.

The figure is redrawn from dispositions.json, the same counts dispositions.svg shows.
"""
import json
import os
import re

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/freefont"
pdfmetrics.registerFont(TTFont("FreeSans", os.path.join(FONT_DIR, "FreeSans.ttf")))
pdfmetrics.registerFont(TTFont("FreeSansBold", os.path.join(FONT_DIR, "FreeSansBold.ttf")))
pdfmetrics.registerFont(TTFont("FreeMono", os.path.join(FONT_DIR, "FreeMono.ttf")))
pdfmetrics.registerFontFamily("FreeSans", normal="FreeSans", bold="FreeSansBold")

SS = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=SS["BodyText"], fontName="FreeSans", fontSize=9.5,
                      leading=12.5)
H = {1: ParagraphStyle("h1", parent=BODY, fontName="FreeSansBold", fontSize=15, leading=19,
                       spaceAfter=6),
     2: ParagraphStyle("h2", parent=BODY, fontName="FreeSansBold", fontSize=12, leading=15,
                       spaceBefore=8, spaceAfter=4)}
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.5, leading=10.5)
COLORS = {"closed_obstructed": "#3b5b92", "closed_known": "#6f8fc2",
          "closed_dominated": "#a9bde0", "exhausted_at_scale": "#8c8c8c",
          "open_next_step": "#d9822b", "open_blocked": "#c0392b",
          "open_unexamined": "#f2c14e"}


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]*)`", r'<font face="FreeMono">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])", r"<i>\1</i>", text)
    return text


def figure():
    d = json.load(open(os.path.join(HERE, "dispositions.json")))
    fams, disp, table = d["families"], d["dispositions"], d["table"]
    unit, row_h, left = 11, 18, 70
    width = 17 * cm
    height = row_h * len(fams) + 60
    g = Drawing(width, height)
    g.add(String(0, height - 12, f"ECDLP lead atlas, 2026-10-30: {d['leads']} leads by "
                 "family and disposition", fontName="FreeSansBold", fontSize=10))
    for i, f in enumerate(fams):
        y = height - 34 - i * row_h
        g.add(String(left - 6, y + 3, f, fontName="FreeSans", fontSize=8, textAnchor="end"))
        x = left
        for k in disp:
            n = table[f][k]
            if n:
                g.add(Rect(x, y, n * unit, row_h - 6, fillColor=colors.HexColor(COLORS[k]),
                           strokeColor=None))
                x += n * unit
        g.add(String(x + 4, y + 3, str(sum(table[f].values())), fontName="FreeSans",
                     fontSize=8))
    lx, ly = 0, 6
    for k in disp:
        g.add(Rect(lx, ly, 7, 7, fillColor=colors.HexColor(COLORS[k]), strokeColor=None))
        label = k.replace("_", " ")
        g.add(String(lx + 10, ly + 1, label, fontName="FreeSans", fontSize=7))
        lx += 16 + 3.6 * len(label)
    return g


def table(lines):
    rows = [[Paragraph(inline(c.strip()), CELL) for c in ln.strip().strip("|").split("|")]
            for ln in lines if not re.match(r"^\|[\s:|-]+\|$", ln.strip())]
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8ccd2")),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f5")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def build():
    md = open(os.path.join(HERE, "README.md")).read().splitlines()
    story, i = [], 0
    while i < len(md):
        ln = md[i]
        m = re.match(r"^(#+) (.*)$", ln)
        if m:
            story.append(Paragraph(inline(m.group(2)), H[min(len(m.group(1)), 2)]))
        elif ln.startswith("!["):
            story += [figure(), Spacer(1, 6)]
        elif ln.startswith("|"):
            block = []
            while i < len(md) and md[i].startswith("|"):
                block.append(md[i])
                i += 1
            story += [table(block), Spacer(1, 6)]
            continue
        elif re.match(r"^(\s*)([-*]|\d+\.) ", ln):
            items = []
            while i < len(md) and re.match(r"^(\s*)([-*]|\d+\.) ", md[i]):
                depth = len(re.match(r"^(\s*)", md[i]).group(1)) // 2
                text = re.sub(r"^\s*([-*]|\d+\.) ", "", md[i])
                items.append(ListItem(Paragraph(inline(text), BODY), leftIndent=12 + 12 * depth))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=10))
            continue
        elif ln.strip():
            story.append(Paragraph(inline(ln), BODY))
            story.append(Spacer(1, 4))
        i += 1

    def footer(canvas, doc):
        canvas.setFont("FreeSans", 7)
        canvas.drawString(2 * cm, 1.2 * cm, "docs/reports/ecdlp-lead-atlas-20261030/report.pdf"
                          " - rendered from README.md by build_pdf.py (reportlab) - derived, "
                          "no new measurement")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))

    SimpleDocTemplate(os.path.join(HERE, "report.pdf"), pagesize=A4, leftMargin=2 * cm,
                      rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                      title="ECDLP lead atlas review 2026-10-30").build(
        story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", os.path.join(HERE, "report.pdf"))


if __name__ == "__main__":
    build()
