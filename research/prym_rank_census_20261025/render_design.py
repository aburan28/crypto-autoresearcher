"""Render prospective implementation status; never runs the collector."""
import json
from pathlib import Path
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def main():
    d = Path(__file__).resolve().parent
    source = dict(schema='prym-rank-census-design/v1', experiment='EXP-ECDLP-d6d8e8',
                  state='implemented; no scientific trial',
                  nodes=['8 fresh public curves', 'fixed base + public sources', '64 sampled branches/source',
                         '3584 census branches/source', 'independent full replay + rank',
                         'launch gate: artifact identity absent'],
                  evidence=['input-validation.json', 'software-tests.txt', 'infrastructure-status.json'],
                  proposed_attempts=1867776, measured_scientific_attempts=0)
    (d/'diagram-source.json').write_text(json.dumps(source, indent=2)+'\n')
    drawing = Drawing(470, 235)
    boxes = [(5, 185, 210, 35, source['nodes'][0]), (255, 185, 210, 35, source['nodes'][1]),
             (5, 115, 210, 35, source['nodes'][2]), (255, 115, 210, 35, source['nodes'][3]),
             (105, 50, 270, 35, source['nodes'][4]), (35, 0, 400, 28, source['nodes'][5])]
    for i, (x, y, w, h, label) in enumerate(boxes):
        drawing.add(Rect(x, y, w, h, fillColor=colors.HexColor('#fff0d3' if i==5 else '#eaf1fa'),
                         strokeColor=colors.HexColor('#65758a')))
        drawing.add(String(x+7, y+h/2-3, label, fontSize=9))
    for x1, y1, x2, y2 in [(215,202,255,202),(360,185,110,150),(360,185,360,150),
                             (110,115,180,85),(360,115,300,85),(240,50,240,28)]:
        drawing.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#65758a')))
    renderSVG.drawToFile(drawing, str(d/'diagram.svg'))
    styles = getSampleStyleSheet()
    paragraphs = [
        ('Prym rank census: implemented, awaiting artifact-store access', 'Title'),
        ('EXP-ECDLP-d6d8e8 / H-ECDLP-51f052 / issue #2414. Prospective implementation report, 2026-10-25. '
         'No scientific trial or verdict. Six planted software tests pass; independent public-input checks pass.', 'BodyText'),
        ('Question: does full finite branch enumeration yield more useful rank than the 64-branch sampler? '
         'Both arms use the same native base and sources 1..64. Publicly exposed columns are removed in both. '
         'U=0 is calibration; no stopping when rank becomes full.', 'BodyText'),
        ('Fixed workload: eight fresh nonanomalous curves at p=101,211,431,4099, A=2, two first-eligible B each. '
         '135 candidate inputs inspected. Derived workload: 8 x 64 x (64+3584) = 1,867,776 attempts. '
         'Measured scientific attempts: zero.', 'BodyText'),
        ('Measurements: all statuses, witnesses, rank progression, first full-rank location, exact finite right kernels, '
         'partial operation vectors and wall/CPU/RSS diagnostics. Independent checker replays every branch and verifies '
         'sample-rowspace containment. Replaying is not a prescribed-computation proof.', 'BodyText'),
        ('Execution gate: repository policy requires large raw data in the canonical S3 artifact store. '
         'Normal AWS access returned exit 255: Unable to locate credentials. The runtime has no configured identity. '
         'The contract remains review_required. No approval or scientific launch occurred.', 'BodyText'),
        ('Limits: raw counters omit pow internals, Python bookkeeping, byte movement, process-group peak and independent '
         'count verification. No complete S, IC gain, asymptotic or deployed-curve claim. New rank results require a native '
         'admitted run after access and archival gates; blind recovery additionally needs worker isolation.', 'BodyText'),
        ('Internal sources: README.md, config.json, fixtures.json, input-validation.json, software-tests.txt, '
         'infrastructure-status.json; prior RUN-ECDLP-d25f6a. Diagram source: diagram-source.json. '
         'Current main merged at ab0609ebe; earlier evidence remains unchanged.', 'BodyText')]
    story = []
    for i, (text, style) in enumerate(paragraphs):
        story.extend([Paragraph(text, styles[style]), Spacer(1, 9)])
        if i==2:
            story.extend([drawing, Spacer(1, 8)])
    SimpleDocTemplate(str(d/'report.pdf'), topMargin=35, bottomMargin=35).build(story)


if __name__ == '__main__':
    main()
