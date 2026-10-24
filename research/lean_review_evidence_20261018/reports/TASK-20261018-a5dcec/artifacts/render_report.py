from pathlib import Path
from xml.sax.saxutils import escape
import re,subprocess
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
ART=Path(__file__).resolve().parent
ROOT=ART.parent
for suffix in ['svg','png']:
 subprocess.run(['dot','-T'+suffix,str(ART/'review-boundary.dot'),'-o',str(ART/('review-boundary.'+suffix))],check=True)
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReviewBody',fontName='DejaVu',fontSize=9,leading=12.5,spaceAfter=7,splitLongWords=True))
styles.add(ParagraphStyle(name='ReviewTitle',fontName='DejaVuBold',fontSize=17,leading=21,spaceAfter=11))
styles.add(ParagraphStyle(name='ReviewHeading',fontName='DejaVuBold',fontSize=11,leading=14,spaceBefore=10,spaceAfter=6))
styles.add(ParagraphStyle(name='ReviewCell',fontName='DejaVu',fontSize=7.4,leading=10,splitLongWords=True))
def fmt(s):
 s=escape(s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<a href="'+m.group(2)+'" color="#245a78">'+m.group(1)+'</a>',s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'`([^`]+)`',r'\1',s)
 return s
story=[]
lines=(ROOT/'report.md').read_text().splitlines();i=0
while i<len(lines):
 l=lines[i].strip()
 if not l: i+=1;continue
 if l.startswith('# '):
  story.append(Paragraph(fmt(l[2:]),styles['ReviewTitle']))
  im=Image(str(ART/'review-boundary.png'));im.drawHeight*=480/im.drawWidth;im.drawWidth=480
  story.extend([im,Spacer(1,10)])
  i+=1;continue
 if l.startswith('## '): story.append(Paragraph(fmt(l[3:]),styles['ReviewHeading']));i+=1;continue
 if l.startswith('|'):
  data=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   vals=[x.strip() for x in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r'[-: ]+',v) for v in vals): data.append([Paragraph(fmt(v),styles['ReviewCell']) for v in vals])
   i+=1
  t=Table(data,colWidths=[165,190,144],repeatRows=1,hAlign='LEFT')
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf3')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#c8d2da')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
  story.extend([t,Spacer(1,8)]);continue
 if l.startswith('- ') or re.match(r'\d+\. ',l):
  story.append(Paragraph(fmt(l),styles['ReviewBody']));i+=1;continue
 para=[l];i+=1
 while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ')) and not re.match(r'\d+\. ',lines[i]):
  para.append(lines[i].strip());i+=1
 story.append(Paragraph(fmt(' '.join(para)),styles['ReviewBody']))
def page(canvas,doc):
 canvas.setFont('DejaVu',7)
 canvas.setFillColor(colors.HexColor('#607080'))
 canvas.drawString(42,26,'TASK-20261018-a5dcec | J2 independent review | 2026-10-18')
 canvas.drawRightString(A4[0]-42,26,str(doc.page))
SimpleDocTemplate(str(ROOT/'report.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=35,bottomMargin=40,title='Independent J2 Lean fidelity review',author='Independent reviewer TASK-20261018-a5dcec').build(story,onFirstPage=page,onLaterPages=page)
