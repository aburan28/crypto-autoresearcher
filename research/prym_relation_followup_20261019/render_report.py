#!/usr/bin/env python3
"""Render the intake report and its diagram; performs no scientific execution.

Requires ReportLab. Rebuild from this directory with python3 render_report.py.
"""
from html import escape
import json
import math
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent
NODES = [
    (20, 40, 220, 80, ["E / F_p, G=<P>, Q=[k]P", "Source labels must survive"], False),
    (290, 40, 220, 80, ["J(D), with E and Prym factors", "i=pullback, n=norm; n i=[d]"], False),
    (560, 40, 220, 80, ["Prym A: auxiliary geometry", "Deck action is negation"], False),
    (290, 230, 220, 95, ["Compact source-labelled router", "PROPOSED / NOT IMPLEMENTED", "Must escape fixed-branch scope"], True),
    (20, 230, 220, 95, ["Public E relation and blind descent", "Witness, projected rank, recovery", "REQUIRED / NOT MEASURED"], True),
    (560, 230, 220, 95, ["Matched current IC baseline", "Complete S, memory and rho gap", "UNBOUND / UNMEASURED"], True),
]
# x1,y1,x2,y2,label,label_x,label_y,is_proposed
EDGES = [
    (240, 80, 290, 80, "i", 261, 65, False),
    (510, 80, 560, 80, "zero on i(G)", 535, 24, False),
    (400, 120, 400, 230, "geometry / representation", 400, 176, True),
    (650, 120, 465, 230, "candidate constraints", 619, 183, True),
    (290, 275, 240, 275, "witness", 263, 256, True),
]


def write_svg():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" viewBox="0 0 800 400">',
           '<rect width="800" height="400" fill="white"/>',
           '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#29485a"/></marker></defs>']
    for x1, y1, x2, y2, label, tx, ty, proposed in EDGES:
        dash = ' stroke-dasharray="6 4"' if proposed else ''
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#29485a" stroke-width="1.6" marker-end="url(#arrow)"{dash}/>')
        out.append(f'<text x="{tx}" y="{ty}" text-anchor="middle" font-family="sans-serif" font-size="10">{escape(label)}</text>')
    for x, y, w, h, lines, proposed in NODES:
        dash = ' stroke-dasharray="6 4"' if proposed else ''
        fill = '#fff4dc' if proposed else '#edf4f8'
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="#29485a"{dash}/>')
        for j, line in enumerate(lines):
            out.append(f'<text x="{x+w/2}" y="{y+27+j*18}" text-anchor="middle" font-family="sans-serif" font-size="11">{escape(line)}</text>')
    for j, line in enumerate([
        'Solid: algebraic interface constraints, not new reviewed results. Dashed: proposed or required work.',
        'The zero Prym projection blocks that direct route; it does not exclude auxiliary relation search.',
        'Issue #2414 | No new scientific run, measured advantage or hypothesis transition.'
    ]):
        out.append(f'<text x="400" y="{354+j*17}" text-anchor="middle" font-family="sans-serif" font-size="10">{escape(line)}</text>')
    out.append('</svg>')
    (ROOT / 'diagram.svg').write_text('\n'.join(out)+'\n')


class Diagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 500, 250

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(self.width/800, self.height/400)
        def text(x, y, s, size=10):
            c.setFillColor(colors.HexColor('#172f3d'))
            c.setFont('Helvetica', size)
            c.drawCentredString(x, 400-y, s)
        for x1, y1, x2, y2, label, tx, ty, proposed in EDGES:
            c.setStrokeColor(colors.HexColor('#29485a'))
            c.setDash(6, 4) if proposed else c.setDash()
            c.line(x1, 400-y1, x2, 400-y2)
            angle = math.atan2(y2-y1, x2-x1)
            c.setDash()
            for delta in (-0.45, 0.45):
                c.line(x2, 400-y2, x2-8*math.cos(angle+delta),
                       400-y2+8*math.sin(angle+delta))
            text(tx, ty, label)
        for x, y, w, h, lines, proposed in NODES:
            c.setDash(6, 4) if proposed else c.setDash()
            c.setStrokeColor(colors.HexColor('#29485a'))
            c.setFillColor(colors.HexColor('#fff4dc' if proposed else '#edf4f8'))
            c.roundRect(x, 400-y-h, w, h, 7, fill=1)
            for j, line in enumerate(lines):
                text(x+w/2, y+27+j*18, line, 11)
        text(400, 354, 'Solid: algebraic interface constraints. Dashed: proposed / required; no new reviewed result.')
        text(400, 371, 'Zero natural Prym projection does not exclude auxiliary relation search.')
        text(400, 388, 'Issue #2414 | No new run, measured advantage or hypothesis transition.')
        c.restoreState()


def inline(s):
    # Keep readable link labels in the derived PDF; exact targets live in README.
    s = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', s)
    s = escape(s.replace('`', ''))
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)


def main():
    tracking = json.loads((ROOT / 'tracking.json').read_text())
    assert tracking['claims']['new_scientific_run'] is False
    write_svg()
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 12
    story = [Paragraph('Issue #2414: Prym-assisted relation follow-up', styles['Title']),
             Paragraph('Design intake only. Source: README.md and tracking.json. No new scientific run or measured advantage.', styles['BodyText']),
             Spacer(1, 10), Diagram(), Spacer(1, 12)]
    paragraph = []
    def flush():
        if paragraph:
            story.append(Paragraph(inline(' '.join(paragraph)), styles['BodyText']))
            story.append(Spacer(1, 5))
            paragraph.clear()
    for line in (ROOT / 'README.md').read_text().splitlines():
        if not line.strip():
            flush()
        elif line.startswith('#'):
            flush()
            style = styles['Heading1' if line.startswith('# ') else 'Heading2']
            story.append(Paragraph(inline(line.lstrip('# ')), style))
        elif line.startswith('- ') or re.match(r'^\d+\. ', line):
            flush()
            paragraph.append(line)
        else:
            paragraph.append(line)
    flush()
    SimpleDocTemplate(str(ROOT / 'report.pdf'), title='Prym-assisted prime-field relation generation',
                      author='Crypto Autoresearcher design intake',
                      rightMargin=42, leftMargin=42, topMargin=36, bottomMargin=36).build(story)


if __name__ == '__main__':
    main()
