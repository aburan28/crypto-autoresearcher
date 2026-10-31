"""Render communication artifacts only; no scientific evaluator or data runs."""
from pathlib import Path
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H = landscape(A4)
c = canvas.Canvas(str(HERE/'proposal.pdf'), pagesize=(W,H))
c.setTitle('Proposed x-sensitive Miller-primitive half-root screen')
c.setAuthor('Non-generic sweep orientation; no experiment executed')

def text(x,y,s,size=10,bold=False):
    c.setFont('DejaVuBold' if bold else 'DejaVu',size)
    c.setFillColorRGB(.09,.17,.25)
    c.drawString(x,y,s)

def para(s,y,width=130,size=10):
    for line in textwrap.wrap(s,width):
        text(35,y,line,size);y-=14
    return y

text(35,H-36,'Proposed x-sensitive Miller-primitive half-root screen',18,True)
text(35,H-59,'2026-10-27 | Read-only source orientation and hand derivations | No experiment executed',9)
box_y=H-221
boxes=[(35,'Public primitive',['Binary D recurrence','Z(R) = −D_r(R) / r','Existing zeta/cocycle prior art','O(log r) charged setup/evaluation']),
       (303,'Fixed public decoder',['c = Z(P) / y(P)','g = Z + cy[α + βc(x − x(P))]','H = (1 − χ(g(R)/g(P))) / 2','40 fixed α, β templates']),
       (571,'Mandatory fixed fixture',['E/F11: y² = x³ + x + 6, r = 13','12 generators × 13 targets × 40','6,240 planned cases before controls','Undefined values remain failures'])]
for x,title,lines in boxes:
    c.setFillColorRGB(.94,.97,.99);c.setStrokeColorRGB(.45,.58,.68)
    c.roundRect(x,box_y,235,135,8,fill=1,stroke=1)
    text(x+12,box_y+112,title,12,True)
    for i,line in enumerate(lines):text(x+12,box_y+85-i*21,line,8.5)
for x in [273,541]:
    c.setStrokeColorRGB(.45,.58,.68);c.line(x,box_y+68,x+22,box_y+68)
    p=c.beginPath();p.moveTo(x+22,box_y+68);p.lineTo(x+15,box_y+72);p.lineTo(x+15,box_y+64);p.close()
    c.setFillColorRGB(.45,.58,.68);c.drawPath(p,fill=1,stroke=0)
y=box_y-24
text(35,y,'Derived local obstruction: do not repeat the one-variable family',12,True);y-=20
y=para('On the mandatory F11 fixture, 5P=(3,6), 6P=(7,9), Z(5P)=4 and Z(6P)=6. Both have Z/y=8, but χ(6/9)=χ(8)=−1. Therefore every normalized-character decoder g=y·F(Z/y) gives opposite signs at these two lower-half points when defined. A zero or pole is undefined. The new x term escapes this particular fiber collision; its ordering is untested.',y,132,9.5)-12
text(35,y,'Cost and acceptance remain separate',12,True);y-=20
y=para('Each predicate call costs O(log r + log p) group/field operations, with inversions and χ powering charged. Conditional scalar recovery needs O(log r) calls plus target doubling and final verification. Validate full cocycle, oddness, all coordinate scalings, generator reindexing and the exact two-pulse law, including O and boundary exceptions. Truth-derived halves are validator-only controls.',y,132,9.5)-12
text(35,y,'Scope and sources',12,True);y-=19
y=para('A finite pass advances only that fixed circuit to an ordering-proof question. Failure resolves its stated template, not all coordinate circuits. No new cohort, statistical fit, scalar-table advice, performance qualification, novelty verdict or ledger status transition is supplied. Complete formulas and source hashes: proposal.md, proposal.json and source-manifest.json.',y,132,9.5)-12
text(35,y,'Prior: IDEA-20261016-09fd08; existing ordered-root audit; Voloch, Acta Arith. 79 (1997), 1–6.',8.5)
text(35,y-15,'Primary author PDF read: https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/zeta3.pdf',8)
c.showPage();c.save()
print(HERE/'proposal.pdf')
