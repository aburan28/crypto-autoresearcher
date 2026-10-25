"""Render only immutable W2 observations; never execute the constructor."""
from pathlib import Path
import json
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.graphics.shapes import Drawing,Rect,String
from reportlab.lib.colors import HexColor

HERE=Path(__file__).resolve().parent
raw=json.loads((HERE/'../../runs/RUN-ECDLP-d25f6a/raw-result.json').read_text())
styles=getSampleStyleSheet();items=[Paragraph('Fixed public-source witness audit',styles['Title']),Spacer(1,12)]
for paragraph in [
 'EXP-ECDLP-cded08 / H-ECDLP-51f052 / GOAL-ECDLP-001',
 'RUN-ECDLP-d25f6a: observations only; no scientific verdict or ECDLP gain claim.',
 'One trial requested and completed; zero failed or timed out. Independent checker passed with zero failed checks. All 11 software controls matched expectations.',
 'Fixed 8 curves x 3 seeds x 64 public scalars x 64 branches = 98,304 attempts. Seeds repeat each curve. The original frozen W was preserved; W2 corrects the manifest schema only.',
]:items.extend([Paragraph(paragraph,styles['BodyText']),Spacer(1,10)])
table=[['p','curve UID','U','accepted rows (seeds 0,1,2)','ranks (seeds 0,1,2)']]
for j in range(0,24,3):
 cells=raw['cells'][j:j+3];c=cells[0]
 table.append([str(c['p']),c['curve_uid'][:10],str(c['projection']['U']),','.join(str(len(v['rows'])) for v in cells),','.join(str(v['projection']['rank']) for v in cells)])
items.extend([Table(table,style=[('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),6)]),Spacer(1,12)])
drawing=Drawing(460,150)
for j,row in enumerate(raw['cells']):
 x=6+j*18
 drawing.add(Rect(x,20,6,row['projection']['U']*12,fillColor=HexColor('#b7c5d6'),strokeWidth=0))
 drawing.add(Rect(x+7,20,6,row['projection']['rank']*12,fillColor=HexColor('#2454ad'),strokeWidth=0))
 drawing.add(String(x,8,str(row['p']),fontSize=5))
drawing.add(String(5,135,'RUN-ECDLP-d25f6a; grey=U, blue=rank; columns; exact finite matrices, n=24 cells',fontSize=8))
items.extend([drawing,Spacer(1,10)])
for paragraph in [
 'All accepted rows passed independent source/divisor/E2-norm checks; exact projected ranks and full-rank base-log solutions were independently verified. Rejection arithmetic was not independently replayed. F101 U=0 cells are all-public calibration, not new unknown-log recovery.',
 'Measured producer wall 9.407047016 s; CPU 9.402666941 s; peak self RSS 43,618,304 bytes. Checker wall 0.628591363 s; CPU 0.628588297 s; peak self RSS 145,575,936 bytes. Linux x86_64, Python 3.12.14; native memory guard 2 GiB.',
 'Raw operation vectors are not complete weighted S. No current-IC speed comparison, blind recovery or deployed-curve conclusion. The finite stream misses full unknown-column rank on the complete panel; follow-up stages retain their gates.',
 'Clean source revision 3d3e2c96cfafa14709af8b526921ba27ba6b7c0c. Exact command/inputs/resources: ../../runs/RUN-ECDLP-d25f6a/{manifest.yaml,environment.json,raw-result.json,verification.json}. Raw publication 7b34b21ff. Full prose, graph.svg and graph-source.json accompany this PDF.',
]:items.extend([Paragraph(paragraph,styles['BodyText']),Spacer(1,10)])
SimpleDocTemplate(str(HERE/'report.pdf')).build(items)
