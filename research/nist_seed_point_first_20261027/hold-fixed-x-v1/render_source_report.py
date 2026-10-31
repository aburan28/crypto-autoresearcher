#!/usr/bin/env python3
"""Render a prospective source report. No curve inputs are read or evaluated."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

HERE = Path(__file__).resolve().parent
boxes = [(12, 55, 135, 'Pinned identities', '21 canonical curves'),
         (175, 55, 145, 'Fixed pairing rule', '24 planned rows'),
         (348, 55, 145, 'Membership + controls', 'NOT EXECUTED')]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="510" height="125" viewBox="0 0 510 125">',
       '<rect width="510" height="125" fill="white"/>',
       '<text x="12" y="20" font-family="Helvetica" font-size="12" fill="#193c55">Prospective workflow - no new membership outcomes</text>']
d = Drawing(510,125)
d.add(String(12,105,'Prospective workflow - no new membership outcomes',fontName='Helvetica',fontSize=12,fillColor=colors.HexColor('#193c55')))
for x,y,w,title,sub in boxes:
    svg += [f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="6" fill="#eef3f6" stroke="#557287"/>',
            f'<text x="{x+w/2}" y="{y+20}" text-anchor="middle" font-family="Helvetica" font-size="11">{escape(title)}</text>',
            f'<text x="{x+w/2}" y="{y+38}" text-anchor="middle" font-family="Helvetica" font-size="10">{escape(sub)}</text>']
    d.add(Rect(x,125-y-52,w,52,rx=6,ry=6,fillColor=colors.HexColor('#eef3f6'),strokeColor=colors.HexColor('#557287')))
    d.add(String(x+w/2,125-y-20,title,textAnchor='middle',fontName='Helvetica',fontSize=11))
    d.add(String(x+w/2,125-y-38,sub,textAnchor='middle',fontName='Helvetica',fontSize=10))
for x1,x2 in [(147,175),(320,348)]:
    svg.append(f'<path d="M{x1},81 L{x2-6},81 M{x2-11},77 L{x2-6},81 L{x2-11},85" stroke="#557287" fill="none"/>')
    d.add(Line(x1,44,x2-6,44,strokeColor=colors.HexColor('#557287')))
    d.add(Polygon([x2-11,48,x2-6,44,x2-11,40],strokeColor=colors.HexColor('#557287'),fillColor=None))
svg.append('</svg>')
(HERE/'planned-workflow.svg').write_text('\n'.join(svg)+'\n')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='SourceBody',parent=styles['BodyText'],fontSize=9.5,leading=13,spaceAfter=8))
story=[]
def p(text,style='SourceBody'): story.append(Paragraph(text,styles[style]))
p('Fixed-x test: source and protocol validation','Title')
p('27 October 2026 | Source-only record | GOAL-NISTSEED-ab8949 remains unresolved')
p('<b>No new study memberships have been evaluated.</b> This report records a prospective exact checker and its static validation. It is not approval, a run result, a historical reconstruction or an independent review.')
story.extend([d,Spacer(1,12)])
p('Planned test','Heading2')
p('Hold the next published Gx fixed across the earlier named qualifying candidates in the same timestamp stream. Retain 11 canonical omissions, 10 published self checks and 3 distinct P-224 opposite-sign sensitivities. The 24 rows are correlated. Repeat as deterministic A/A and retain planted positive, negative, zero-boundary, source-corruption and circularity controls.')
p('Static observations','Heading2')
p('The exact four-file Coordinator delivery was preserved. Original source hash and Python syntax passed. The repository protocol validator found two enum errors; both failures remain visible. Coordinator-approved pre-freeze corrections preserve all planned rows and use exact committed-byte admission for bound files while recording unrelated dirty paths. The corrected draft passes the actual protocol validator with zero findings. No checker import or main invocation occurred.')
p('Corrected checker SHA-256: 7c70b0b9e4843efa19c7301cb1884229621a525812528ace70bf913eb4580de1')
p('Interpretation and remaining gates','Heading2')
p('A canonical omission admitting the held x would obstruct membership alone under the stated visitation/traversal assumptions. Zero such witnesses would be necessary-condition compatibility only. Full fixed(x,y) predicates already determine b and cannot independently establish chronology. The broader 69-position census and the full commonality objective remain outside this finite necessary test.')
p('Source commit and prospective freeze must precede data; lawful admission, approval, execution, export and independent review are still required. A 60-second runtime estimate is explicitly unmeasured. The separate process watchdog is prospective protection, not a scientific spending cap.')
p('Sources and preserved failures','Heading2')
p('Primary: Anthropic, Claude reveals ECDSA curve origins (16 October 2026), its point recipe and open questions. Internal: prior point-first, base-point workflow and direct-stream reports, exact parameter records, protocol schema and validator. The bundled Python lacked jsonschema; native Python supplied it. A singular draft fixture was replaced before data. Coordination API/CLI timeouts stopped writes; the same task/epoch was re-confirmed before materialization. Exact details, hashes and original/corrected source are adjacent.')
def footer(canvas,doc):
    canvas.setFont('Helvetica',8)
    canvas.drawString(48,28,'SOURCE ONLY | planned counts are not observed outcomes | TASK-20261027-82d8a8')
doc=SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=35,bottomMargin=45)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'report':'report.pdf','new_study_memberships':0,'planned_main_rows':24}))
