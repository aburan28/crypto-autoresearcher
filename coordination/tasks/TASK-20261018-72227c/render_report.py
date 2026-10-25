"""Render source-only prose and diagram; performs no worksheet calculation."""
from pathlib import Path
import html
import subprocess
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image
from PIL import Image as Raster
import matplotlib

root=Path(__file__).resolve().parent
for ext in ("svg","png"):
    subprocess.run(["dot","-T"+ext,str(root/"preparation-flow.dot"),"-o",str(root/("preparation-flow."+ext))],check=True)
font=Path(matplotlib.get_data_path())/"fonts/ttf"
pdfmetrics.registerFont(TTFont("PrepSans",str(font/"DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("PrepBold",str(font/"DejaVuSans-Bold.ttf")))
styles=getSampleStyleSheet()
styles["BodyText"].fontName="PrepSans"; styles["BodyText"].fontSize=9; styles["BodyText"].leading=12
styles["Title"].fontName="PrepBold"
small=ParagraphStyle("SmallCell",parent=styles["BodyText"],fontSize=7.5,leading=10)
story=[]; table=[]
def escaped(value):
    return html.escape(value.replace("`",""))
def flush():
    if not table:
        return
    rows=[[Paragraph(escaped(c),small) for c in row] for row in table]
    box=Table(rows,colWidths=[110,190,200],repeatRows=1)
    box.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9f0f7")),("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.3,colors.lightgrey)]))
    story.append(box); story.append(Spacer(1,9)); table.clear()
for line in (root/"REPORT.md").read_text().splitlines():
    if line.startswith("|"):
        cells=[c.strip() for c in line.strip("|").split("|")]
        if not all(set(c)<=set("-:") for c in cells):
            table.append(cells)
        continue
    flush()
    if not line.strip() or line.startswith("!["):
        continue
    style=styles["Title"] if line.startswith("# ") else styles["BodyText"]
    story.append(Paragraph(escaped(line[2:] if line.startswith("# ") else line),style)); story.append(Spacer(1,7))
flush()
w,h=Raster.open(root/"preparation-flow.png").size
image_width=min(500,680*w/h)
story.append(Image(str(root/"preparation-flow.png"),width=image_width,height=image_width*h/w))
SimpleDocTemplate(str(root/"REPORT.pdf"),pagesize=(595.44,841.68),leftMargin=43,rightMargin=43,topMargin=40,bottomMargin=40).build(story)
print("Rendered source preparation report; no scientific trial.")
