from pathlib import Path
import html,json,re
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,Table,TableStyle,KeepTogether
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from reportlab.graphics import renderSVG
import fitz

REPORT=Path(__file__).resolve().parents[1];ART=REPORT/'artifacts'
d=Drawing(510,172)
def box(x,y,w,h,title,detail,color):
    d.add(Rect(x,y,w,h,fillColor=colors.HexColor(color),strokeColor=colors.HexColor('#758294'),radius=5))
    d.add(String(x+w/2,y+h-15,title,fontName='Helvetica-Bold',fontSize=9,textAnchor='middle'))
    d.add(String(x+w/2,y+13,detail,fontName='Helvetica',fontSize=8,textAnchor='middle'))
def arrow(x1,y,x2,color):
    d.add(Line(x1,y,x2,y,strokeColor=colors.HexColor(color),strokeWidth=1.5))
    d.add(Polygon([x2,y,x2-6,y+3,x2-6,y-3],fillColor=colors.HexColor(color),strokeColor=None))
box(0,106,135,46,'Ordinary local inputs','mutation / add / delete','#e8f4ec')
box(180,106,145,46,'Pre/post manifests','ordinary changes detected','#e8f4ec')
box(370,106,135,46,'CLI exit 3','receipt invalidated','#e8f4ec')
arrow(135,130,180,'#357953');arrow(325,130,370,'#357953')
box(0,22,135,46,'Hidden local helper','False changes to True','#fff1df')
box(180,22,145,46,'Skipped by manifest','blanket dot-dir pruning','#fde9e7')
box(370,22,135,46,'CLI exit 0','strict receipt accepted','#fde9e7')
arrow(135,46,180,'#aa4e37');arrow(325,46,370,'#aa4e37')
d.add(String(252,87,'Real Lean checks the changed True proposition in both layouts.',fontSize=9,textAnchor='middle'))
d.add(String(252,4,'TASK-20261018-695548 / frozen candidate only / no kernel refutation',fontSize=8,textAnchor='middle'))
renderSVG.drawToFile(d,str(ART/'diagram.svg'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReview',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallReview',fontName='Helvetica',fontSize=7,leading=9))
styles.add(ParagraphStyle(name='CodeReview',fontName='Courier',fontSize=7,leading=9,spaceAfter=8))
def markup(t):
    t=html.escape(t)
    t=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',t)
    t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1',t)
    return t
story=[];lines=(REPORT/'report.md').read_text().splitlines();i=0;diagram_added=False
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line.startswith('# '):story +=[Paragraph(markup(line[2:]),styles['Title']),Spacer(1,8)];i+=1;continue
    if line.startswith('## '):story +=[Spacer(1,6),Paragraph(markup(line[3:]),styles['Heading2'])];i+=1;continue
    if line.startswith('```'):
        i+=1;code=[]
        while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
        story.append(Preformatted('\n'.join(code),styles['CodeReview']));i+=1;continue
    if line.startswith('|'):
        data=[]
        while i<len(lines) and lines[i].startswith('|'):
            row=[c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',c) for c in row):
                data.append([Paragraph(markup(c),styles['SmallReview']) for c in row])
            i+=1
        table=Table(data,colWidths=[85,118,222,85],repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf3')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#bdc7d1')),
          ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
        story += [table,Spacer(1,10)];continue
    block=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```')):block.append(lines[i]);i+=1
    story.append(Paragraph(markup(' '.join(block)),styles['BodyReview']))
    if not diagram_added and line.startswith('**Own-joint'):
        story +=[Spacer(1,7),d,Spacer(1,12)];diagram_added=True
def footer(canvas,doc):
    canvas.setFont('Helvetica',7);canvas.drawString(42,24,'TASK-20261018-695548 | Frozen repair candidate | Own-joint verdict: breaks')
    canvas.drawRightString(552,24,str(doc.page))
SimpleDocTemplate(str(REPORT/'report.pdf'),pagesize=(595,842),rightMargin=42,leftMargin=42,
 topMargin=38,bottomMargin=40,title='Independent Lean workflow repair review').build(story,onFirstPage=footer,onLaterPages=footer)
doc=fitz.open(REPORT/'report.pdf');observations=[]
for n,page in enumerate(doc):
    text=page.get_text();assert text.strip()
    png=ART/f'report-page-{n+1}.png';page.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(png)
    observations.append({'page':n+1,'characters':len(text),'image':png.name,'text':text})
(ART/'pdf-inspection-text.json').write_text(json.dumps(observations,indent=2)+'\n')
print(json.dumps({'pages':len(doc),'pdf':str(REPORT/'report.pdf'),'diagram':str(ART/'diagram.svg')}))
