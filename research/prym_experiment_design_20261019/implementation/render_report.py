"""Derived figures/report from recorded status and counts only; no trials."""
import json
import textwrap
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.graphics.shapes import Drawing,Rect,String,Line
from reportlab.graphics import renderSVG

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'diagram-source.json').read_text())
diagram=Drawing(500,215)
for j,node in enumerate(data['nodes']):
 x=5+(j%2)*250;y=120 if j<2 else 12
 diagram.add(Rect(x,y,240,85,fillColor=HexColor('#e4eef5' if j<2 else '#fff1dc'),strokeColor=HexColor('#446074')))
 diagram.add(String(x+10,y+65,node['stage']+' / '+node['status'].replace('_',' '),fontSize=10))
 text=([node['run'],node['scope']] if j<2 else [node['scope'],'W rank / isolation / cost gates remain'])
 for k,line in enumerate(text):
  if len(line)>46:
   wrapped=textwrap.wrap(line,width=46);first=wrapped[0];rest=' '.join(wrapped[1:])
   diagram.add(String(x+10,y+47-12*k,first,fontSize=7))
   diagram.add(String(x+10,y+35-12*k,rest,fontSize=7))
  else:diagram.add(String(x+10,y+47-12*k,line,fontSize=7))
diagram.add(Line(375,120,375,100,strokeColor=HexColor('#b96527')))
diagram.add(String(10,107,'G and W are different cover families; no transfer map claimed.',fontSize=8))
renderSVG.drawToFile(diagram,str(HERE/'diagram.svg'))
points=json.loads((HERE/'recorded-ranks.json').read_text())['points']
graph=Drawing(480,165)
graph.add(String(5,148,'RUN-ECDLP-d25f6a: measured rank / unknown columns; exact finite matrices',fontSize=9))
for j,row in enumerate(points):
 x=7+j*19
 graph.add(Rect(x,30,6,row['U']*13,fillColor=HexColor('#b7c5d6'),strokeWidth=0))
 graph.add(Rect(x+7,30,6,row['rank']*13,fillColor=HexColor('#2454ad'),strokeWidth=0))
 graph.add(String(x,17,str(row['rank'])+'/'+str(row['U']),fontSize=6))
 graph.add(String(x,7,str(row['p']),fontSize=5))
renderSVG.drawToFile(graph,str(HERE/'recorded-ranks.svg'))
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=11;items=[]
def paragraph(text):items.extend([Paragraph(text,styles['BodyText']),Spacer(1,9)])
items.extend([Paragraph('Prym: implementation and observations',styles['Title']),Spacer(1,12)])
paragraph('2026-10-21 / issue #2414 / PR #2415 / IDEA-20260909-4c5ee9. Observations and conditional software only; no scientific-state promotion or measured attack-cost advantage.')
paragraph('G: RUN-ECDLP-dad803 completed 64 primary and 64 companion covers plus 24 synthetic controls. Independent checker passed. Recorded Frobenius overlap: 3/64 primary, 4/64 companions. Only Fp/Fp2 traces were checked; no complete genus-3 certificate or Jacobian map.')
paragraph('W2: RUN-ECDLP-d25f6a completed 98,304 fixed attempts on eight curves and three within-curve seeds, with 11 controls. Independent source/divisor and rank checker passed. Original frozen W files remain intact; W2 corrects a manifest schema omission using fresh IDs.')
items.extend([diagram,Spacer(1,10),graph,Spacer(1,8)])
paragraph('Grey bars are U (actual unknown norm columns); blue bars are rank. Values are exact, n=24 cells; seeds are not independent curves. Six cells attain rank U&gt;0; six have U=0 from the public source schedule; twelve miss U. All F4099 cells accepted zero rows. This limits the tested finite stream, not all Prym algorithms or deployed curves.')
paragraph('Source/rank observations: experiments/EXP-ECDLP-cded08/runs/RUN-ECDLP-d25f6a/{raw-result.json,verification.json}; geometry: experiments/EXP-ECDLP-da4ba3/runs/RUN-ECDLP-dad803/. Exact commands, resources, dependencies and inspected per-run reports are linked from README.md.')
items.append(PageBreak())
items.extend([Paragraph('Conditional follow-ups and release gates',styles['Title']),Spacer(1,12)])
paragraph('Integrated S software: canonical finite train/holdout streams, frozen histogram models, real/permuted/split-product/coordinate arms, identity A/A, independent full-pool algebraic census, and isolated workers. Complete geometric-orbit/stream and cost auditing still need release.')
paragraph('Integrated E software: same-base IC comparator, explicit target descent, salted challenge commitment and private verifier, exact attack-output seals, independent final source check, coordinate/null arms and finite plain rho. The concrete mitm m=2 comparator is not qualified as current best; the plain rho is not a certified optimized usable-action reference.')
paragraph('Public inputs: eight fresh S curves at p=4099,8191,16381,32749; forty E instances with subgroup bits 11,13,15,17. All search rejections are retained. Field/order/generator/base checks passed independently. EC1 identities accompany inputs; no E secrets or point-log labels were supplied.')
paragraph('S prospective revision: at p=101 the genus-2 Hasse bound allows at most 125,440 canonical candidates in the old full-source policy, less than the requested 131,072 distinct train-plus-holdout candidates. The revised fresh panel and 256-source rule precede all S labels; prior W2 outcomes are disclosed. Exhaustion still must be retained.')
paragraph('Isolation is unavailable in this runtime: Landlock ENOSYS and bubblewrap user-ID mapping failure. Workers refuse, without an unisolated fallback. The software test proves refusal here, not successful isolation. Scientific S and E have not executed and remain review_required.')
paragraph('Thirteen planted software controls pass: interpolation/census, malformed witnesses, rank, aliases, A/A/coordinate transport, finite support, V2 manifest schema, same-base IC/planted descent, seal mutations, gate and isolation refusal. These are correctness tests, not blind recovery or performance evidence.')
paragraph('Next gates: prospectively frozen nontrivial full-rank constructor or distinct repair; enforceable worker isolation; independently qualified current IC, complete S weights and reference protocols; full native plan/handoff/archive/admission. Raw vectors exclude pow internals, Python bookkeeping and independent checking; no complete S or end-to-end gain is inferred.')
paragraph('Sources: README.md, status.json, input-validation.json, software-tests.txt, diagram-source.json and recorded-ranks.json. Original design report is historical. No canonical scientific frontier graph changes follow from this observational report. PDF inspected before publication.')
SimpleDocTemplate(str(HERE/'report.pdf'),topMargin=36,bottomMargin=36).build(items)
