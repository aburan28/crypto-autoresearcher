#!/usr/bin/env python3
"""Derived vector diagram and full Markdown-text PDF; no research execution."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderSVG
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.graphics.shapes import Group

ROOT=Path(__file__).resolve().parent
def diagram():
    d=Drawing(480,205)
    blue=HexColor('#23435f')
    for x, title, equation in [(5,'E / Q','y^2 = x(x^2 + A*x + B)'),(255,"E prime / Q",'v^2 = u(u^2 - 2*A*u + D)')]:
        d.add(Rect(x,95,220,70,fillColor=HexColor('#eef4f8'),strokeColor=blue))
        d.add(String(x+12,143,title,fontSize=12,fillColor=blue))
        d.add(String(x+12,119,equation,fontSize=10))
    d.add(Line(225,144,255,144,strokeColor=blue))
    d.add(Polygon([255,144,248,148,248,140],fillColor=blue))
    d.add(Line(255,110,225,110,strokeColor=blue))
    d.add(Polygon([225,110,232,114,232,106],fillColor=blue))
    d.add(String(240,182,'phi: degree 2',textAnchor='middle',fontSize=10))
    d.add(String(240,77,'dual: degree 2; dual(phi(P)) = [2]P',textAnchor='middle',fontSize=10))
    for y,text in [(55,'D=A^2-4B; B*D != 0; kernels {O,(0,0)} on each endpoint'),(37,'Odd-order subgroup maps invert up to [2]; no arbitrary residue coverage claim'),(18,'Producer certificate checks: 2 instances at p=353; independent review pending')]:
        d.add(String(240,y,text,textAnchor='middle',fontSize=9))
    return d

def counts():
    d=Drawing(480,125)
    d.add(String(0,113,'Historical scan: n in [-2000,2000], exactly 4,001 proposals',fontSize=11))
    for i,(label,value) in enumerate([('Prime-screen candidates',2),('Certified independent pairs',2),('Certified dependent pairs',0)]):
        y=84-i*24
        d.add(String(0,y,label,fontSize=9))
        d.add(Rect(180,y-2,value*95,12,fillColor=HexColor('#3a6d92'),strokeColor=None))
        d.add(String(390,y,str(value),fontSize=10))
    d.add(String(0,8,'Units: pair count. Deterministic census; no sampling uncertainty interval.',fontSize=9))
    return d

def footer(c, doc):
    c.setFont('Helvetica',8); c.drawString(42,25,'Xedni tracking snapshot | 2026-10-07 | proposed; review pending')
    c.drawRightString(553,25,str(doc.page))

def main():
    renderSVG.drawToFile(diagram(),str(ROOT/'isogeny.svg'))
    renderSVG.drawToFile(counts(),str(ROOT/'counts.svg'))
    styles=getSampleStyleSheet()
    styles['Heading1'].keepWithNext=True
    styles['Heading2'].keepWithNext=True
    styles['BodyText'].fontSize=9; styles['BodyText'].leading=13
    styles['BodyText'].spaceAfter=7
    story=[Paragraph('Xedni: certificates and bounded follow-up',styles['Title']),Spacer(1,8),diagram(),Spacer(1,12),counts(),PageBreak()]
    for line in (ROOT/'REPORT.md').read_text().splitlines():
        if not line.strip(): continue
        style=styles['Heading1'] if line.startswith('# ') else styles['Heading2'] if line.startswith('## ') else styles['BodyText']
        line=re.sub(r'^#+ ','',line).replace('**','').replace('`','')
        line=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',line)
        story.append(Paragraph(escape(line),style))
    SimpleDocTemplate(str(ROOT/'report.pdf'),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=40,title='Xedni certificates and follow-up',author='Codex').build(story,onFirstPage=footer,onLaterPages=footer)

if __name__=='__main__': main()
