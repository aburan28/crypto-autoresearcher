"""Render a derived handoff report; no experiment or scientific state transition."""
from pathlib import Path
import html
import json
import xml.etree.ElementTree as ET
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
receipt = json.loads((ROOT/'verification/odd-torsion-20261017.json').read_text())
claims = [json.loads(p.read_text()) for p in (ROOT/'claims').glob('C-*.json')]
assert receipt['verification']['status'] == 'machine_verified'
assert receipt['semantic_review']['status'] == 'pending'

nodes = [
    (10, 150, 215, 58, '#e8eef4', ['19 imported advisory records', 'Scope, assumptions, source digests']),
    (275, 150, 215, 58, '#e8eef4', ['Ten research questions remain open', 'No official state promotion']),
    (10, 48, 215, 58, '#dff0e8', ['Odd-torsion conditional statement', 'Lean kernel check; zero-axiom audit']),
    (275, 48, 215, 58, '#fff0db', ['Concrete-model and semantic review', 'Separate, unresolved obligations']),
]
drawing = Drawing(500, 230)
svg = ET.Element('svg', xmlns='http://www.w3.org/2000/svg', width='750', height='345', viewBox='0 0 500 230')
for x,y,w,h,c,lines in nodes:
    drawing.add(Rect(x,y,w,h,fillColor=colors.HexColor(c),strokeColor=colors.HexColor('#758b9a'),radius=4))
    ET.SubElement(svg,'rect',x=str(x),y=str(230-y-h),width=str(w),height=str(h),rx='4',fill=c,stroke='#758b9a')
    for i,text in enumerate(lines):
        yy=y+h-20-i*16
        drawing.add(String(x+10,yy,text,fontName='DV',fontSize=8.5,fillColor=colors.HexColor('#17394a')))
        t=ET.SubElement(svg,'text',x=str(x+10),y=str(230-yy),fill='#17394a',**{'font-family':'sans-serif','font-size':'9'});t.text=text
for x1,y1,x2,y2 in [(225,179,275,179),(225,77,275,77),(117,150,117,106)]:
    drawing.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#506b7b')))
    ET.SubElement(svg,'line',x1=str(x1),y1=str(230-y1),x2=str(x2),y2=str(230-y2),stroke='#506b7b')
ET.ElementTree(svg).write(HERE/'evidence-flow.svg',encoding='utf-8',xml_declaration=True)
styles=getSampleStyleSheet();styles['Heading1'].fontName='DVB';styles['Heading1'].fontSize=16;styles['Heading1'].leading=22;styles.add(ParagraphStyle(name='BodyX',fontName='DV',fontSize=9.5,leading=14.5,spaceAfter=10));styles.add(ParagraphStyle(name='SmallX',fontName='DV',fontSize=7.3,leading=10.5,spaceAfter=6));story=[];md=[]
def p(text):
    story.append(Paragraph(html.escape(text),styles['BodyX']));md.extend([text,''])
def h(text):
    story.append(Paragraph(html.escape(text),styles['Heading1']));md.extend(['# '+text,''])
h('Scoped evidence handoff and odd torsion proof')
p('17 October 2026. This report records a software import and a named formal verification result. It makes no scientific promotion, cryptanalytic speedup claim, or conclusion that any of the ten research directions is exhausted.')
p(f'The portable register imports {len(claims)} advisory records without changing their bytes. It exposes ten open questions, four original proof obligations, explicit inference limits and next tests. It separates a structural check from optional artifact verification using authorized source roots.')
story.append(drawing);md.extend(['![Evidence and proof boundaries](evidence-flow.svg)',''])
p('The diagram distinguishes imported records, an independently checkable formal statement, and the remaining model/review obligations. No comparable scientific runtime measurements were collected in this change, so a process diagram is used instead of a speed graph.')
p('Raw evidence packets previously labelled private are not uploaded to the public repository. Their archive digests and source-file bindings remain available. Structural CI does not imply that those private artifacts were accessed; the explicit artifact-check mode refuses missing access.')
p('The new reader uses explicit exceptions rather than optimization-removable assertions, validates references and recorded values, and publishes new records atomically without overwriting other writers. Its guards reject fabricated Lean labels and broad-direction closure attempts.')
p('Discovery pointers in AGENTS.md and README.md make the handoff available after checkout or merge. Existing agents and remote machines are not automatically notified or synchronized.')
story.append(PageBreak())
h('The exact formal result and remaining work')
p('Let addition be associative and commutative with a two-sided zero. Define scalar multiples by repeated addition. Assume r=k+k+1, rP=0, T+T=0 and T is nonzero. Then r(P+T)=T, so P+T is not in the kernel of multiplication by r. Finiteness, inverse operations and primality of r are unnecessary for this conditional statement.')
p('The existing repository verifier built the dependency-free project, checked the requested declaration as a theorem, ran the project and target axiom audits, and returned machine_verified. The project audit requires an empty axiom dependency list. It checked the equality lemma, kernel exclusion and the explicit control model.')
p('The two-element XOR model supplies a positive instance. Real kernel tests reject false strengthenings without oddness or nonzero torsion, and reject submitting a definition as though it were a theorem. Earlier development compilation failure logs are separate from the accepted verifier receipt; they are not mathematical negative evidence.')
p('The formal object has explicit additive-law fields. No concrete elliptic-curve representation, rational torsion certificate or factor-base membership checker is imported. Independent semantic-fidelity review remains pending. The imported curve-application record retains its original not_formalized label; this new generic proof does not silently promote it.')
p('This scoped obstruction leaves T-closed mixed-domain constructions and tuple symmetries open. Next: review the exact theorem statement and construct a checked bridge to an intended curve/domain. The coprime-order, scalar-twist and Boolean-checker obligations remain separate pending tasks.')
p('No canonical frontier graph is changed: this branch changes neither a pipeline cost bound nor an official research claim. The new diagram communicates the proof and evidence boundaries only.')
for text in [
    'Task: formal/targets/scoped-odd-torsion-translation.yaml',
    'Theorem: ScopedObstructions.AdditiveModel.odd_translation_outside_kernel',
    'Proof: formal/scoped-obstructions/ScopedObstructions/Torsion.lean',
    'Receipt: research/ten-lead-evidence/verification/odd-torsion-20261017.json',
    'Source commit: '+receipt['provenance']['source_commit'],
    'Lean: '+receipt['provenance']['lean_version'],
    'Problem: problems/ten-lead-proof-scope-and-artifact-access.md',
]:story.append(Paragraph(html.escape(text),styles['SmallX']));md.extend([text,''])
def footer(c,d):
    c.setFont('DV',7);c.drawString(40,25,'Scoped evidence and formal verification | 17 October 2026');c.drawRightString(555,25,str(d.page))
SimpleDocTemplate(str(HERE/'report.pdf'),title='Scoped evidence handoff and odd torsion proof',pagesize=(595,842),leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
(HERE/'report.md').write_text('\n'.join(md).rstrip()+'\n')
print('Rendered report.pdf and editable evidence-flow.svg')
