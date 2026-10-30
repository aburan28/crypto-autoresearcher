"""Render the immutable review addendum from its recorded status data."""
from pathlib import Path
import json
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

P = Path(__file__).resolve().parent
d = json.loads((P / 'review-status.json').read_text())
nodes = [('Frozen V2', 'R1 provenance defect', '#f5e4e4'),
         ('Successor V3', d['review_label'], '#e3f3e9'),
         ('Live application', 'not admitted / not applied', '#fff0d5')]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="120"><rect width="900" height="120" fill="white"/>']
for i, (title, subtitle, color) in enumerate(nodes):
    x = 10 + i * 300
    svg += [f'<rect x="{x}" y="10" width="280" height="72" rx="6" fill="{color}" stroke="#526579"/>',
            f'<text x="{x+140}" y="38" text-anchor="middle" font-family="sans-serif" font-size="16">{escape(title)}</text>',
            f'<text x="{x+140}" y="65" text-anchor="middle" font-family="sans-serif" font-size="13">{escape(subtitle)}</text>']
svg += ['<text x="450" y="110" text-anchor="middle" font-family="sans-serif" font-size="13">Attribution fidelity only. No theorem, experiment, performance or live-ledger validation.</text></svg>']
with (P / 'review-boundary.svg').open('x') as f:
    f.write('\n'.join(svg) + '\n')
assert not (P / 'review-report.pdf').exists()
c = canvas.Canvas(str(P / 'review-report.pdf'), pagesize=(612,792), invariant=1)
c.setTitle('BINSTD attribution review and provenance correction')
c.setFont('Helvetica-Bold',16)
c.drawString(36,754,'BINSTD attribution review and correction')
c.setFont('Helvetica',9)
c.drawString(36,735,'2026-10-29 | T-782 | TASK-20261029-d6606a | APPLICATION PENDING')
for i, (title, subtitle, color) in enumerate(nodes):
    x = 36 + i * 182
    c.setFillColor(HexColor(color)); c.setStrokeColor(HexColor('#526579'))
    c.roundRect(x,657,174,58,5,fill=1,stroke=1)
    c.setFillColor(HexColor('#182b40')); c.setFont('Helvetica-Bold',10)
    c.drawCentredString(x+87,693,title); c.setFont('Helvetica',8)
    c.drawCentredString(x+87,674,subtitle)
y = 633
for section in d['sections']:
    c.setFont('Helvetica-Bold',10); c.drawString(36,y,section['title']); y -= 16
    c.setFont('Helvetica',9)
    for line in simpleSplit(section['body'],'Helvetica',9,540):
        c.drawString(36,y,line); y -= 12
    y -= 12
assert y > 45, y
c.setFont('Helvetica',7)
c.drawString(36,26,'Exact source, candidate, review and control bindings accompany this report. Original reviews are retained.')
c.save()
print('Rendered one-page review report; bottom position:',y)
