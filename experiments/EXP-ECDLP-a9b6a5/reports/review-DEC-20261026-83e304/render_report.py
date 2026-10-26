"""Rebuild the scoped decision figure/PDF from immutable observations and report source."""
from pathlib import Path
from io import BytesIO
from html import escape
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

HERE=Path(__file__).resolve().parent
source=json.loads((HERE/'graph-source.json').read_text())
cells=source['cells']
labels=[f"B{13 if c['instance_id']=='b13' else 16}\n{'m16' if c['arm']=='m16_candidate' else 'm8 ref'}" for c in cells]
fig,axes=plt.subplots(1,2,figsize=(8.1,3.15),layout='constrained')
x=list(range(len(cells)))
bar=axes[0].bar(x,[c['counted']['accepted'] for c in cells],color=['#176b9a' if c['arm']=='m16_candidate' else '#a5aab1' for c in cells],width=.6)
axes[0].bar_label(bar,padding=3,fontsize=9)
axes[0].set_title('Accepted rows',fontsize=11);axes[0].set_ylabel('Count');axes[0].set_ylim(0,max(1,max(c['counted']['accepted'] for c in cells))*1.2)
width=.34
r=axes[1].bar([i-width/2 for i in x],[c['counted']['rank'] for c in cells],width,label='Affine rank',color='#246648')
u=axes[1].bar([i+width/2 for i in x],[c['counted']['U'] for c in cells],width,label='Unknown columns U',color='#c9d2d8')
axes[1].bar_label(r,padding=2,fontsize=8);axes[1].bar_label(u,padding=2,fontsize=8);axes[1].set_ylim(0,22);axes[1].set_yticks([0,5,10,15,20])
axes[1].set_title('Rank and unknown columns',fontsize=11);axes[1].set_ylabel('Count');axes[1].legend(frameon=False,fontsize=8,loc='upper left')
for ax in axes:
 ax.set_xticks(x,labels);ax.tick_params(axis='both',labelsize=8);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
fig.suptitle('Exact conditioned support; no performance comparison',fontsize=12)
fig.savefig(HERE/'graph.svg',format='svg',metadata={'Date':None})
png=BytesIO();fig.savefig(png,format='png',dpi=220);plt.close(fig);png.seek(0)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=6));styles.add(ParagraphStyle(name='CaptionSmall',fontName='Helvetica',fontSize=8,leading=10,textColor=colors.HexColor('#374151'),spaceAfter=8))
flow=[];inserted=False
for line in (HERE/'report.md').read_text().splitlines():
 if not line.strip():continue
 if line.startswith('# '):flow.append(Paragraph(escape(line[2:]),styles['Title']))
 elif line.startswith('## '):
  if not inserted:
   flow.extend([Spacer(1,5),Image(png,width=510,height=198),Paragraph(escape(source['caption']),styles['CaptionSmall'])]);inserted=True
  flow.append(Paragraph(escape(line[3:]),styles['Heading2']))
 else:flow.append(Paragraph(escape(line.lstrip('- ')),styles['BodySmall']))
SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=38,title='Prym width16 scoped evidence review',author='Coordinator').build(flow)
print(HERE/'graph.svg');print(HERE/'report.pdf')
