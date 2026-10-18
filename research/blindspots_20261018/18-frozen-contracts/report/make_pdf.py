"""Layout only: renders README.md (headings, bullets, paragraphs) with report/graph.png to REPORT.pdf."""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem, PageBreak
from xml.sax.saxutils import escape
st = getSampleStyleSheet(); body = ParagraphStyle("b", parent=st["BodyText"], fontSize=9, leading=12)
mono = ParagraphStyle("m", parent=body, fontName="Courier", fontSize=8)
def fmt(t):
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"`(.+?)`", r'<font face="Courier" size="8">\1</font>', t)
els = []; bul = []
def flush():
    global bul
    if bul: els.append(ListFlowable([ListItem(Paragraph(fmt(b), body)) for b in bul], bulletType="bullet", leftIndent=14)); bul = []
for line in open("README.md").read().split("\n"):
    if line.startswith("![graph]"): continue
    if line.startswith("# "): flush(); els.append(Paragraph(fmt(line[2:]), st["Title"]))
    elif line.startswith("## "):
        flush(); els.append(Paragraph(fmt(line[3:]), st["Heading2"]))
        if line[3:] == "Numbers (counted, n = 1 run per trial, no intervals apply)": pass
    elif line.startswith("- "): bul.append(line[2:])
    elif line.strip(): flush(); els.append(Paragraph(fmt(line), body)); els.append(Spacer(1, 4))
flush()
els.append(PageBreak()); els.append(Paragraph("Figure", st["Heading2"]))
w = 520; els.append(Image("report/graph.png", width=w, height=w * 840 / 1950))
els.append(Paragraph("Left: first blocking gate over 1029 ECDLP-class or named contracts (counts from raw/scan/summary.json). Right: recorded wall seconds and exit codes of the 4 replica trials (raw/receipt-card-02..05.json), n=1 each, shared 4-vCPU host, level L0. Cards CARD-BLINDSPOT-18-01..05, commit e4b1f0d13; run ids RUN-ICPERF-943efa, RUN-PFDR-936605, RUN-XEDN-132272, RUN-XEDN-f4d646.", body))
SimpleDocTemplate("REPORT.pdf", pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36, title="Blind-spot 18: frozen ECDLP contracts").build(els)
