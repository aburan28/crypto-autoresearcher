#!/usr/bin/env python3
"""Render the evidence-flow diagram and PDF; no experiment or metric replay."""
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

root = Path(__file__).resolve().parent
paths = [root/name for name in ('evidence-flow.svg', 'report.pdf', 'render-receipt.json')]
if any(path.exists() for path in paths):
    raise SystemExit('Refusing to overwrite an existing communication artifact')
matrix = json.loads((root/'matrix.json').read_text())
receipt = json.loads((root/'integrity.json').read_text())
if hashlib.sha256((root/'matrix.json').read_bytes()).hexdigest() != receipt['matrix_sha256']:
    raise SystemExit('Matrix/receipt mismatch')
drawing = Drawing(480, 112)
labels = [('Immutable Git', '15 source blobs'), ('Exact excerpts', '6 selected rows'),
          ('Evidence roles', 'Pointers + gaps'), ('Review needed', 'No promotion')]
for i, (title, subtitle) in enumerate(labels):
    x = i*122
    drawing.add(Rect(x, 35, 112, 62, fillColor=colors.HexColor('#edf3f8'), strokeColor=colors.HexColor('#35516a')))
    drawing.add(String(x+56, 72, title, textAnchor='middle', fontName='Helvetica-Bold', fontSize=10))
    drawing.add(String(x+56, 52, subtitle, textAnchor='middle', fontSize=9))
    if i < 3:
        drawing.add(Line(x+113, 66, x+121, 66, strokeColor=colors.HexColor('#35516a')))
drawing.add(String(0, 10, 'Identity is checked. Scientific content and complete coverage are not established.', fontSize=9))
renderSVG.drawToFile(drawing, str(paths[0]))
styles = getSampleStyleSheet()
story = [Paragraph('Historical claim evidence register', styles['Title']),
         Paragraph('Initial partial seed | 2026-10-29 | Conductor T-777', styles['Normal']), Spacer(1, 14), drawing]
sections = [
    ('Observation', f"The integrity reader bound {receipt['claim_rows']} selected rows to {receipt['available_sources']} available Git blobs ({receipt['source_bytes_read']:,} bytes). One elaborated-types record is unavailable. The total historical claim denominator is unknown."),
    ('Mathematical scope', 'Four known-label polynomial identities over arbitrary commutative rings are linked to their historical source, native job, axiom output and scoped reviews. This does not validate the newer integration head or prove graph, probability, cancellation or cost bridges.'),
    ('Execution and interpretation', 'The BINSTD row links the archived deterministic reconstruction and witnesses; original timing and complete execution binding remain separate. The crypto row records the cover assessment\'s stated classification/implementation boundary without revalidating catalog counts.'),
    ('Validation boundary', 'Eleven real-Git unit tests exercise integrity controls. Integrity success never promotes a scientific claim, even with every evidence role populated. The historical artifacts remain immutable. Hosted checks and independent code review are pending at initial publication.'),
    ('Next work', 'Expand the claim inventory, bind missing elaborated types and execution/protocol inputs, obtain scoped independent reviews, then update affected canonical dashboards from accepted evidence. Full historical validation remains open.'),
]
for heading, body in sections:
    story.extend([Spacer(1, 9), Paragraph(heading, styles['Heading3']), Paragraph(escape(body), styles['BodyText'])])
story.extend([Spacer(1, 12), Paragraph('Source: matrix.json and integrity.json in this directory. See README.md for immutable bindings and reproduction commands.', styles['Normal'])])
SimpleDocTemplate(str(paths[1]), pagesize=(612, 792), rightMargin=54, leftMargin=54, topMargin=36, bottomMargin=36).build(story)
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'matrix.json', root/'integrity.json', root/'render_report.py', *paths[:2]]}
paths[2].write_text(json.dumps(dict(renderer='reportlab', version=reportlab.Version, sha256=hashes), indent=2)+'\n')
