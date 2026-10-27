#!/usr/bin/env python3
"""Render retained replay values; this renderer performs no curve arithmetic."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, Circle, String

HERE = Path(__file__).resolve().parent
RAW = HERE / 'replay-1/point-traces.json'
data = json.loads(RAW.read_text())
assert data['status'] == 'passed'
rows = data['curve_traces']
assert len(rows) == 6

table = '| Curve | Recovered seed | First x works on final curve? | Published Gx appears at attempt |\n| --- | ---: | --- | ---: |\n'
for row in rows:
    table += f"| {row['name']} | {row['recovered_freelip_seed']} | {'yes' if row['first_candidate_works'] else 'no'} | {row['successful_attempt']} |\n"

identity_text = '\n'.join(f"- {row['name']}: `{row['curve_uid']}`; recovered point recipe {'available' if row['recovered_recipe_available'] else 'unknown'}." for row in data['published_full_points'])
report = f'''# Do the published base points fit a point-first selector?

27 October 2026 UTC. Post-observation deterministic verification of retained records; no historical selector or official scientific status is established. Conductor task T-5500, UUID 7eb3c0fb-bf10-4507-bc87-8f6ea5dc9db6. The broader GOAL-NISTSEED-ab8949 commonality objective remains unresolved.

## Question and exact scope

The user asks whether generator points might have been picked before curves, with curves retained only when the selected points lie on them. This check distinguishes three propositions: generate an x-coordinate and test it; use exactly the first x after a recovered initialization and reject the curve on failure; or maintain a point stream while trying successive curves. Full preselected (x,y) pairs are a separate algebraic case.

This is a replay of existing frozen inputs, not a prospectively discovered criterion. No new seed, prefix, packing, attempt limit or assignment of points to omitted curves was searched. The existing FreeLIP prefix protocol and build amendment remain unchanged. The independent-verifier implementation is reused, so this session is not a new independent review.

## Method and sources actually checked

The additive replay_check.py pins the old 77-case results, existing verify.py and ten published parameter records. It calls the existing verify(directory) function without invoking its writing CLI. It then exposes the same fixed 26-bit, discard-seven point-loop intermediates, retaining its original 32-attempt cap. Each candidate is tested against the final published coefficient using the existing modular-residue method. Final Gx, retry count and RNG state must agree with the retained actual-library output. The ten published full coordinate pairs are also checked against their exact recorded equations.

Primary code/reconstruction: https://www.anthropic.com/research/ecdsa-curve-origins (retrieved in the conversation; its base_point_x source and six listed counts were read). Repository inputs: research/nist_seed_freelip_prefix_20261024/PROTOCOL.md, BUILD_AMENDMENT.md, verify.py and runs/prefix-v2/results.json; research/nist_seed_skipped_curves_20261016/traits.json (internal, committed, hash-pinned). Prior workflow limits: research/nist_seed_selection_workflow_20261023/report.md and research/nist_seed_1997_selection_extension_20261023/basepoint_stream/report.md (internal, read). No search_knowledge tool was available; direct source records were used.

## Replayed observations

The existing verifier passed all 77 retained cases: 30 of 30 matching point routes, zero matches among 24 wrong-prefix/limb-width controls, and all 21 large-order state checks plus two small controls. These are rechecks of the earlier records, not 77 new legacy-library runs. All ten published full coordinate pairs satisfy their recorded curve equations.

{table}

![Fixed reconstructed point attempts](attempts.svg)

Six fixed initializations yield fourteen replayed candidate x values: eight non-residues on the final published curves precede the six published Gx matches. These are reconstructed intermediates, not authenticated historical rejection events. The full integers, full curve UIDs, residues and RNG states are in replay-1/point-traces.json. No timing, sampling probability or security advantage is inferred.

## What follows and what remains unknown

Derived: the exact model that uses only the first x after each recovered seven-output prefix cannot reproduce four of the six published May points. The arithmetic reconstruction with point retries reproduces all six. A common finite attempt cap for that reconstruction must be at least five; this does not show that a cap existed or classify any omitted curve.

Unresolved: the broader point-first chronology. Later x values could also arise if a point stream advanced while the caller tried different curve candidates. Final coordinates and the recovered stream alone do not reveal those earlier pairings. No historical point-stream assignment to the eleven omissions is known here, and none is invented. In particular, the eight non-residues on final published curves are not eight identified omitted curves.

The point recipes for P-224, P-256, P-384 and P-521 remain unknown. Their valid published points establish membership, not how or when those points were generated. For a fully preselected pair on a fixed field with a=-3, the equation determines one b via b=y^2-x^3+3x modulo p; the recovered hash construction would still require a compatible explanation.

![Arithmetic reconstruction and unresolved chronology](chronology.svg)

Next discriminator: freeze one historically grounded rule for initializing and advancing the point stream and pairing it with curve candidates. Require it to match published Gx values and the full keep/omit sequence without choosing per-curve states after seeing outcomes. Original caller source or logs could supply that rule. This report does not design or approve that future experiment.

## Preservation, controls and delivery

The first replay attempt completed with exit zero; stderr is empty. No previous run or source file was overwritten. Raw outputs, exact command, source head, dirty state, platform, Python version and hashes are retained in replay-1/started.json, existing-verifier.json, point-traces.json and completed.json, with separate stdout/stderr. New seed searches, new legacy-library invocations and ECPP/VM executions are all zero. The work is separate from BATCH-a41798's zero-run integration task.

The first PDF-rendering attempt failed before writing artifacts because the bundled Python lacked svglib. Its stdout/stderr remain retained. The renderer was repaired to use existing ReportLab primitives for the chart and Graphviz PNG for the diagram; no dependency installation or scientific rerun was needed.

The new report records coordinate arithmetic and an inference boundary. No verified historical-selection, isogeny, attack or cost edge is added to a canonical graph. The existing workflow and basepoint-stream diagrams were checked as source context; no established edge changes. Publication and PR state are recorded separately from this rendering.

## Exact published identities

{identity_text}

## Reproduction

Replay command: PYTHONDONTWRITEBYTECODE=1 python3 research/nist_seed_point_first_20261027/replay_check.py --out NEW_DIRECTORY. It refuses an existing output directory. The exact first command is in replay-1/started.json. Render with the bundled Python and render_report.py. Rendering performs no new curve computation. Source input hashes and the intermediate-value record digest remain machine-readable in the replay files.
'''
(HERE / 'report.md').write_text(report)

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="306" viewBox="0 0 720 306">', '<rect width="720" height="306" fill="#f8fafc"/>', '<text x="20" y="28" font-family="Helvetica,Arial" font-size="17" fill="#142d45">Reconstructed x candidates on each final published curve</text>', '<text x="20" y="49" font-family="Helvetica,Arial" font-size="11" fill="#536477">Six fixed point streams; 14 candidates. Historical processing order is unknown.</text>']
for i,row in enumerate(rows):
    y = 82 + i*32
    svg.append(f'<text x="20" y="{y+4}" font-family="Helvetica,Arial" font-size="13">{escape(row["name"])}</text>')
    for item in row['attempts']:
        x = 210 + (item['attempt']-1)*68
        fill = '#138574' if item['is_published_gx'] else '#c97827'
        svg.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{fill}"/><text x="{x}" y="{y+4}" text-anchor="middle" font-family="Helvetica,Arial" font-size="11" fill="white">{item["attempt"]}</text>')
    svg.append(f'<text x="585" y="{y+4}" font-family="Helvetica,Arial" font-size="12">Gx at attempt {row["successful_attempt"]}</text>')
svg.extend(['<circle cx="28" cy="282" r="6" fill="#c97827"/><text x="42" y="286" font-family="Helvetica,Arial" font-size="11">No point with this x on final curve</text>', '<circle cx="300" cy="282" r="6" fill="#138574"/><text x="314" y="286" font-family="Helvetica,Arial" font-size="11">Matches published Gx</text>', '</svg>'])
(HERE / 'attempts.svg').write_text('\n'.join(svg)+'\n')

dot = '''digraph chronology {
  graph [rankdir=LR, bgcolor="white", pad="0.15", nodesep="0.25", ranksep="0.35", fontname="Helvetica"];
  node [shape=box, style="rounded,filled", fillcolor="#eff5f8", fontname="Helvetica", fontsize=11, margin="0.12"];
  edge [fontname="Helvetica", fontsize=9, color="#52687a"];
  curve [label="Final published curve\ncoefficient b"];
  xs [label="Fixed FreeLIP stream\nx1, x2, ..."];
  test [label="Replay membership\non final curve"];
  point [label="Six exact\npublished Gx matches", fillcolor="#d9eee8"];
  caller [label="Original caller order,\ncurve/point pairing, retry rule", style="rounded,dashed", fillcolor="white"];
  curve -> test; xs -> test; test -> point;
  caller -> test [style=dashed, label="unknown"];
}
'''
(HERE / 'chronology.dot').write_text(dot)
dot_command = shutil.which('dot') or '/opt/homebrew/bin/dot'
subprocess.run([dot_command, '-Tsvg', str(HERE/'chronology.dot'), '-o', str(HERE/'chronology.svg')], check=True)
subprocess.run([dot_command, '-Tpng', '-Gdpi=180', str(HERE/'chronology.dot'), '-o', str(HERE/'chronology.png')], check=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodySmall', parent=styles['BodyText'], fontSize=9.2, leading=13, spaceAfter=7))
styles.add(ParagraphStyle(name='Identity', parent=styles['BodyText'], fontSize=7.3, leading=9, spaceAfter=3, wordWrap='CJK'))
styles['Title'].fontSize = 21
styles['Title'].leading = 25
story = []
def para(text, style='BodySmall'):
    story.append(Paragraph(text, styles[style]))
def figure(path, width):
    if path.suffix == '.png':
        from PIL import Image as PillowImage
        with PillowImage.open(path) as native:
            w, h = native.size
        story.append(Image(str(path), width=width, height=width*h/w))
        story.append(Spacer(1,8))
        return
    # The chart's own SVG uses only these three documented flat primitives.
    svg_root = ElementTree.fromstring(path.read_text())
    w, h = float(svg_root.attrib['width']), float(svg_root.attrib['height'])
    drawing = Drawing(w, h)
    for element in svg_root:
        tag = element.tag.rsplit('}',1)[-1]
        a = element.attrib
        color = colors.toColor(a.get('fill','black'))
        if tag == 'rect':
            drawing.add(Rect(float(a.get('x',0)), h-float(a.get('y',0))-float(a['height']), float(a['width']), float(a['height']), fillColor=color, strokeColor=None))
        elif tag == 'circle':
            drawing.add(Circle(float(a['cx']), h-float(a['cy']), float(a['r']), fillColor=color, strokeColor=None))
        elif tag == 'text':
            drawing.add(String(float(a['x']), h-float(a['y']), element.text or '', fontName='Helvetica', fontSize=float(a.get('font-size',12)), fillColor=color, textAnchor=a.get('text-anchor','start')))
        else:
            raise ValueError(f'Unexpected chart primitive: {tag}')
    scale = width/drawing.width
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale
    story.append(drawing)
    story.append(Spacer(1,8))

para('Do the published base points fit a point-first selector?', 'Title')
para('27 October 2026 | T-5500 | Retained-record verification')
para('<b>Observation:</b> Two of six recovered May point streams produce the published Gx on their first candidate. Four require later candidates. The wider chronology and omitted-curve pairings remain unknown.')
para('What was checked', 'Heading2')
para('The existing verifier passed all 77 retained cases, including 30 matching point routes, 24 wrong-prefix/limb-width controls with zero matches, 21 large-order checks and two small controls. No legacy-library or ECPP program was run anew. All ten published full points satisfy their recorded equations.')
grid = [['Curve', 'Recovered seed', 'First x works?', 'Gx attempt']]
for row in rows:
    grid.append([row['name'], str(row['recovered_freelip_seed']), 'yes' if row['first_candidate_works'] else 'no', str(row['successful_attempt'])])
tbl = Table(grid, colWidths=[145,105,105,95], hAlign='LEFT')
tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#193c55')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef3f6'),colors.white]),('LINEBELOW',(0,0),(-1,0),0.5,colors.HexColor('#193c55'))]))
story.extend([tbl, Spacer(1,12)])
figure(HERE/'attempts.svg',450)
para('These fourteen candidate values are a reconstruction against final published curves. The eight failed memberships are not authenticated historical rejection events or eight identified omitted curves.')
para('Inference boundary', 'Heading2')
para('A one-attempt rule at the recovered initializations/prefixes cannot reproduce four published points. Retrying x values on the same curve reproduces all six. A common finite cap for this reconstruction must allow at least five attempts. This does not identify an actual cap or the original control flow.')
story.append(PageBreak())
para('What your broader hypothesis still permits', 'Title')
para('A point stream could have advanced while the caller tried successive curve candidates. The same final x coordinates do not establish which curves were paired with earlier x values, or whether x generation preceded coefficient generation. The point recipes for P-224, P-256, P-384 and P-521 remain unknown.')
figure(HERE/'chronology.png',450)
para('A full preselected pair (x,y), with p and a=-3 fixed, determines one compatible coefficient: b = y^2 - x^3 + 3x modulo p. Its agreement with the recovered seed/hash construction still needs explanation. Choosing only x first is a different hypothesis.')
para('Exact identity scope', 'Heading2')
for row in data['published_full_points']:
    para(escape(row['name']) + ' | ' + ('recovered recipe' if row['recovered_recipe_available'] else 'recipe unknown') + '<br/>' + escape(row['curve_uid']), 'Identity')
para('Provenance and next discriminator', 'Heading2')
para('Source: Anthropic, "Claude reveals ECDSA curve origins" (16 October 2026), its public base-point code; the committed FreeLIP prefix protocol, build amendment, actual-library records and existing verifier. Input and output digests, full candidate integers, residues and RNG states are retained in the adjacent replay files. This session reuses the existing verifier; it is not a fresh independent review.')
para('Next: specify one historically grounded point-stream advancement and curve-pairing rule, then require it to reproduce both the published points and keep/omit sequence. No omitted-curve schedule was fitted here. The commonality objective remains unresolved.')

def footer(canvas, doc):
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#536477'))
    canvas.drawString(48,30,'Point-first hypothesis | deterministic replay | no historical attribution')
    canvas.drawRightString(564,30,str(doc.page))

doc = SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=48)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'rendered':'report.pdf','raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'new_curve_computations_in_renderer':0}))
