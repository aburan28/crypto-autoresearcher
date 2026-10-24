from pathlib import Path
import re,json,html
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,KeepTogether
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from reportlab.graphics import renderSVG
import fitz
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
nodes=[(0,'Frozen full inputs','255 files match','separate external binding','#dceaf5'),(190,'Real Lean checks','19 mapped + 65 targets','build / exact name / axioms','#e1f1e4'),(380,'Receipt and coverage','F1 omitted modules','F2 contradictory receipt','#fae0db'),(570,'Input provenance','F3 imported source change','four hashes miss helper','#fae0db')]
d=Drawing(760,132)
for x,title,line1,line2,color in nodes:
 d.add(Rect(x+1,33,179,85,rx=5,ry=5,fillColor=colors.HexColor(color),strokeColor=colors.HexColor('#334155')))
 d.add(String(x+10,96,title,fontName='Helvetica-Bold',fontSize=10));d.add(String(x+10,74,line1,fontSize=9));d.add(String(x+10,55,line2,fontSize=8))
 if x<570:
  d.add(Line(x+181,75,x+188,75,strokeColor=colors.HexColor('#334155')));d.add(Polygon([x+188,75,x+184,78,x+184,72],fillColor=colors.HexColor('#334155')))
d.add(String(2,11,'J3: passing kernel checks do not establish coverage, authentic execution, source fidelity or scientific promotion.',fontSize=10))
renderSVG.drawToFile(d,str(A/'diagram.svg'))
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyReview',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=7));styles['Heading1'].fontSize=17;styles['Heading1'].leading=21;styles['Heading2'].fontSize=12;styles['Heading2'].leading=15;styles['Heading1'].keepWithNext=True;styles['Heading2'].keepWithNext=True
story=[];paragraph=[]
def fmt(s):
 s=html.escape(s);s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`(.+?)`',r'<font name="Courier" size="8.2">\1</font>',s);return s
for line in (D/'report.md').read_text().splitlines()+['']:
 if not line or line.startswith('#'):
  if paragraph:story.append(Paragraph(fmt(' '.join(paragraph)),styles['BodyReview']));paragraph=[]
  if line.startswith('# '):story.append(Paragraph(fmt(line[2:]),styles['Heading1']));small=Drawing(480,84);small.add(d);small.scale(480/760,480/760);story.append(small);story.append(Spacer(1,12))
  elif line.startswith('## '):story.append(Paragraph(fmt(line[3:]),styles['Heading2']))
 else:paragraph.append(line)
def footer(c,doc):
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#475569'));c.drawString(45,25,'TASK-20261018-dae80c · Independent J3 review · frozen initial verdict: breaks');c.drawRightString(550,25,str(doc.page))
SimpleDocTemplate(str(A/'report.pdf'),pagesize=(595,842),rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer)
pdf=fitz.open(A/'report.pdf');pages=[]
for i,p in enumerate(pdf):
 image=A/f'report-page-{i+1}.png';p.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(image);pages.append({'page':i+1,'text_characters':len(p.get_text()),'image':str(image.name)})
(A/'pdf-pages.json').write_text(json.dumps(pages,indent=2)+'\n');print('PDF pages',len(pdf))
