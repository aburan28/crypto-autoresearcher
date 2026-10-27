"""Render only local design/status records. Never imports or runs the collector."""
from pathlib import Path
import json, html
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String, Line

D=Path(__file__).resolve().parent
B=D.parents[1]
ROOT=D.parents[6]
source=json.loads((D/'graph-source.json').read_text())
W,H=940,490
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="940" height="490" fill="#f5f7fb"/>','<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#475569"/></marker></defs>']
for edge in source['edges']:
 a,b=edge['from'],edge['to'];x1,y1=source['boxes'][a]['x']+source['boxes'][a]['w']/2,source['boxes'][a]['y']+source['boxes'][a]['h'];x2,y2=source['boxes'][b]['x']+source['boxes'][b]['w']/2,source['boxes'][b]['y']
 svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>')
for b in source['boxes']:
 fill=b['fill'];svg.append(f'<rect x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" rx="10" fill="{fill}" stroke="#cbd5e1"/>')
 for i,line in enumerate(b['lines']):
  weight='700' if i==0 else '400';size=15 if i==0 else 13
  svg.append(f'<text x="{b["x"]+16}" y="{b["y"]+24+i*21}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="#0f172a">{escape(line)}</text>')
svg+=['<text x="20" y="476" font-family="Arial,sans-serif" font-size="12" fill="#475569">Design diagram only. Counts labeled derived; no m16 outcome data. EXP-ECDLP-a9b6a5 / BATCH-49720f.</text>','</svg>']
(D/'diagram.svg').write_text('\n'.join(svg)+'\n')
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=12;styles['Title'].fontSize=20;styles['Title'].leading=23
story=[Paragraph('Prym width follow-up: local draft status',styles['Title']),Paragraph('2026-10-26 | EXP-ECDLP-a9b6a5 | GOAL-ECDLP-001 | H-ECDLP-51f052',styles['BodyText']),Spacer(1,10)]
for text in source['report_paragraphs'][:5]:story += [Paragraph(escape(text),styles['BodyText']),Spacer(1,7)]
# Draw the SVG's same graph source directly in the PDF, preserving vector text.
scale=0.555;drawing=Drawing(W*scale,H*scale)
for edge in source['edges']:
 a,b=edge['from'],edge['to'];aa,bb=source['boxes'][a],source['boxes'][b];drawing.add(Line((aa['x']+aa['w']/2)*scale,(H-aa['y']-aa['h'])*scale,(bb['x']+bb['w']/2)*scale,(H-bb['y'])*scale,strokeColor=colors.HexColor('#475569'),strokeWidth=1))
for b in source['boxes']:
 drawing.add(Rect(b['x']*scale,(H-b['y']-b['h'])*scale,b['w']*scale,b['h']*scale,rx=6,ry=6,fillColor=colors.HexColor(b['fill']),strokeColor=colors.HexColor('#cbd5e1')))
 for i,line in enumerate(b['lines']):drawing.add(String((b['x']+16)*scale,(H-b['y']-24-i*21)*scale,line,fontName='Helvetica-Bold' if i==0 else 'Helvetica',fontSize=8 if i==0 else 7,fillColor=colors.HexColor('#0f172a')))
story += [drawing,Spacer(1,4),Paragraph('Diagram of proposal, software status and gates; no new outcome graph exists because no m16 scientific stream ran.',styles['BodyText']),PageBreak(),Paragraph('Controls, custody and next gates',styles['Heading1'])]
for text in source['report_paragraphs'][5:]:story += [Paragraph(escape(text),styles['BodyText']),Spacer(1,7)]
story += [Paragraph('Sources and provenance',styles['Heading2'])]
for item in source['sources']:story += [Paragraph(escape(item),styles['BodyText']),Spacer(1,3)]
def footer(canvas,doc):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#475569'));canvas.drawString(36,24,'Unpublished local draft; no approval, science, archive or publication.');canvas.drawRightString(558,24,str(doc.page))
SimpleDocTemplate(str(D/'report.pdf'),pagesize=(594,792),leftMargin=36,rightMargin=36,topMargin=34,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
print('Rendered diagram.svg and report.pdf from graph-source.json; no science invoked.')
