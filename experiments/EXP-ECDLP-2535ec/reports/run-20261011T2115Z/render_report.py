from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "report.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))
styles.add(ParagraphStyle(name="Tiny", parent=styles["BodyText"], fontSize=7.2, leading=9))
styles["Title"].fontSize = 18
styles["Title"].leading = 22

doc = SimpleDocTemplate(
    str(OUT), pagesize=letter, rightMargin=0.55 * inch, leftMargin=0.55 * inch,
    topMargin=0.48 * inch, bottomMargin=0.48 * inch,
)
story = []
story.append(Paragraph("EXP-ECDLP-2535ec run report", styles["Title"]))
story.append(Paragraph("Observation-only record for RUN-ECDLP-b2d284", styles["Small"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "This report records the supervisor path and its sealed infrastructure receipt. "
    "It does not assign evidence strength, change the hypothesis or experiment state, "
    "or interpret a scientific outcome.", styles["BodyText"]))
story.append(Spacer(1, 7))
story.append(Paragraph("<b>Scope and custody</b>", styles["Heading2"]))
story.append(Paragraph(
    "Goal GOAL-ECDLP-001; question RQ-ECDLP-002; hypothesis H-ECDLP-bd1572; "
    "experiment EXP-ECDLP-2535ec. Successor plan SHA-256: "
    "2e9841e4fc754b4b5898bc1a1794eabd54d9ff468b2b188cfee3a90e689f74ae. "
    "Correction CORR-20261011-d20976; queue BATCH-1adefe; task "
    "TASK-20261011-a71042; claim owner executor-ecdlp-2535ec, epoch 1. "
    "Run-record commit: 111d82295f.", styles["Small"]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>Trial accounting</b>", styles["Heading2"]))
story.append(Paragraph(
    "One trial was requested, zero completed, one stopped during infrastructure setup, "
    "and zero timed out. The supervisor loaded the plan, admitted the claim, and "
    "created the run receipt. It recorded status infrastructure_error with detail "
    "<i>Exception occurred in preexec_fn.</i> while installing the declared "
    "address-space guard. The producer and checker did not start.", styles["Small"]))
story.append(Spacer(1, 4))

labels = [
    "queue\nadmitted", "claim\nepoch 1", "supervisor\nadmitted", "preexec_fn\nfailed",
    "producer\nnot started", "checker\nnot started", "output\nnot emitted",
]
cells = []
for i, label in enumerate(labels):
    if i < 3:
        bg, fg = colors.HexColor("#d9f2df"), colors.HexColor("#26834a")
    elif i == 3:
        bg, fg = colors.HexColor("#ffe3b3"), colors.HexColor("#b26a00")
    else:
        bg, fg = colors.HexColor("#f0f2f4"), colors.HexColor("#8a949e")
    cells.append(Table([[Paragraph(label.replace("\n", "<br/>"), styles["Tiny"])]], colWidths=[0.84 * inch], rowHeights=[0.48 * inch], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 1.2, fg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])))
    if i < len(labels) - 1:
        cells.append(Paragraph("&#8594;", styles["Heading2"]))
pipeline = Table([cells], colWidths=[0.84 * inch if i % 2 == 0 else 0.17 * inch for i in range(len(cells))])
pipeline.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
story.append(pipeline)
story.append(Paragraph("RUN-ECDLP-b2d284 execution pipeline; green = reached, amber = infrastructure stop, gray = not reached.", styles["Tiny"]))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Command and parameters</b>", styles["Heading2"]))
story.append(Paragraph(
    "PYTHONPATH=. python3 tools/experiment_execution.py run --plan "
    "experiments/EXP-ECDLP-2535ec/trial-plan-v2.json --owner "
    "executor-ecdlp-2535ec --epoch 1", styles["Tiny"]))
story.append(Paragraph(
    "The producer command declared d={3,4,5}, bits={30,40}, A={150,300}, "
    "B_s={512,2048}, and seeds {1,2,3}. These are requested parameters, not "
    "measured values.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Measurements and controls</b>", styles["Heading2"]))
story.append(Paragraph(
    "No measurement rows, sample counts, arm yields, controls, manifest, or "
    "raw-result.json were emitted. Therefore no quantitative plot or uncertainty "
    "calculation is present. The editable visual data are in graph-data.json and "
    "the corresponding SVG is graph.svg. The recorded host was Darwin with Python "
    "3.12.8; CPU time, hostname, and a runtime lock hash were absent and remain "
    "missing.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Interpretation boundary</b>", styles["Heading2"]))
story.append(Paragraph(
    "The run is operationally incomplete. This report records that boundary only; "
    "scientific interpretation belongs to a later independent review/archive task.", styles["Small"]))

doc.build(story)
print(OUT)
