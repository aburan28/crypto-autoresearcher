#!/usr/bin/env python3
"""Render prospective design communication; never runs a scientific trial."""
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent
NODES = [
    ('G: geometry', '64 toy covers; Fp / Fp2', 'Screen, not transfer proof'),
    ('W: public witnesses', 'Maps, labels, norm rank', 'Reject leaks / tautologies'),
    ('S: companion ablation', 'Real vs shuffled selector', 'Charge training and rejects'),
    ('E: blind recovery', 'Complete S / current IC', 'Report memory and rho gap'),
]


def write_svg():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="310" viewBox="0 0 800 248">',
             '<rect width="800" height="248" fill="white"/>',
             '<defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#29485a"/></marker></defs>']
    for i, lines in enumerate(NODES):
        x = 15+200*i
        parts.append(f'<rect x="{x}" y="30" width="170" height="95" rx="6" fill="#fff4dc" stroke="#29485a" stroke-dasharray="5 3"/>')
        for j, line in enumerate(lines):
            parts.append(f'<text x="{x+85}" y="{55+24*j}" text-anchor="middle" font-family="sans-serif" font-size="11">{escape(line)}</text>')
        if i < 3:
            parts.append(f'<line x1="{x+170}" y1="77" x2="{x+197}" y2="77" stroke="#29485a" marker-end="url(#a)"/>')
    for j, line in enumerate([
        'All stages prospective / review_required. Each cover family needs its own map checks.',
        'S is a fixed-generator engineering test. A compact new router remains an open problem.',
        'Native admission + archived inputs + independent review precede execution or claims.',
        'Issue #2414 | No scientific trials or measured ECDLP improvement in this design record.'
    ]):
        parts.append(f'<text x="400" y="{159+22*j}" text-anchor="middle" font-family="sans-serif" font-size="11">{escape(line)}</text>')
    parts.append('</svg>')
    (ROOT/'diagram.svg').write_text('\n'.join(parts)+'\n')


class Diagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 500, 105

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(500/800, 105/160)
        for i, lines in enumerate(NODES):
            x = 15+200*i
            c.setStrokeColor(colors.HexColor('#29485a'))
            c.setFillColor(colors.HexColor('#fff4dc'))
            c.setDash(5, 3)
            c.roundRect(x, 35, 170, 95, 6, fill=1)
            c.setDash()
            c.setFillColor(colors.HexColor('#172f3d'))
            c.setFont('Helvetica', 11)
            for j, line in enumerate(lines):
                c.drawCentredString(x+85, 107-24*j, line)
            if i < 3:
                c.line(x+170, 82, x+195, 82)
                c.line(x+195, 82, x+189, 86)
                c.line(x+195, 82, x+189, 78)
        c.setFont('Helvetica', 10)
        c.drawCentredString(400, 13, 'Proposed tests. No measured gain. Admission and independent review remain required.')
        c.restoreState()


def inline(text):
    text = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', text)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escape(text.replace('`', '')))


def main():
    write_svg()
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 12
    story = [Paragraph('Prym experiment programme: issue #2414', styles['Title']),
             Paragraph('Prospective designs and software components. No scientific trial or measured gain.', styles['BodyText']),
             Spacer(1, 12), Diagram(), Spacer(1, 12)]
    paragraph = []
    def flush():
        if paragraph:
            story.append(Paragraph(inline(' '.join(paragraph)), styles['BodyText']))
            story.append(Spacer(1, 6))
            paragraph.clear()
    for line in (ROOT/'README.md').read_text().splitlines():
        if not line.strip():
            flush()
        elif line.startswith('# '):
            continue
        elif line.startswith('## '):
            flush()
            story.append(Paragraph(inline(line[3:]), styles['Heading2']))
        else:
            paragraph.append(line)
    flush()
    def footer(c, doc):
        c.setFont('Helvetica', 8)
        c.drawString(42, 25, 'Issue #2414 | design only | source-linked specifications in repository')
        c.drawRightString(553, 25, str(doc.page))
    SimpleDocTemplate(str(ROOT/'report.pdf'), pagesize=(595, 842),
                      rightMargin=42, leftMargin=42, topMargin=38, bottomMargin=42).build(
                          story, onFirstPage=footer, onLaterPages=footer)


if __name__ == '__main__':
    main()
