"""Render an observational report from already recorded data; no experiments."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Rect, String
import json

directory=Path(__file__).resolve().parent
styles=getSampleStyleSheet()
items=[Paragraph('Recorded Prym geometry census',styles['Title']),Spacer(1,12)]
for text in [
 'EXP-ECDLP-da4ba3 / H-ECDLP-9e7a19 / GOAL-ECDLP-001',
 'RUN-ECDLP-dad803: observations only; no scientific verdict or ECDLP claim.',
 'One trial requested and completed; zero failed or timed out. Independent checker passed: 128 covers and 24 synthetic controls; zero failed checks.',
 'Clean producer revision e2442834348a7ff60ee50c4618268555d0d5f2fc. Exact command, fixed input hashes, dependencies and host: immutable run manifest/environment.',
 'Measured producer: wall 2.040924355 s, CPU 2.059629574 s, peak RSS 53,055,488 bytes. Checker: wall 0.500340244 s, CPU 0.499568460 s, peak RSS 50,208,768 bytes.',
 'Graph: exact recorded overlaps, n=8 covers per arm per prime. Derived totals: primary 3/64; companion 4/64. No sampling intervals; finite census.',
]:items.extend([Paragraph(text,styles['BodyText']),Spacer(1,8)])
drawing=Drawing(460,150)
points=json.loads((directory/'graph-source.json').read_text())['points']
for j,row in enumerate(points):
 x=20+(j%8)*55+(0 if row['panel']=='primary' else 17)
 height=row['shared_count']*25
 from reportlab.lib.colors import HexColor
 drawing.add(Rect(x,30,13,height,fillColor=HexColor('#2454ad' if row['panel']=='primary' else '#c24b24'),strokeWidth=0))
 drawing.add(String(x+3,35+height,str(row['shared_count']),fontSize=8))
 if row['panel']=='primary':drawing.add(String(x+5,15,str(row['p']),fontSize=8))
drawing.add(String(10,137,'RUN-ECDLP-dad803; blue=primary, orange=companion; n=8 each; x=prime p',fontSize=8))
items.extend([drawing,Spacer(1,12)])
for text in [
 'Both field degrees and enumeration orders agreed with independent counts. F43 (0,1) is calibration. The 128 covers are a new catalogue, unrelated to the unsourced historical 32-cover quotation.',
 'Fp/Fp2 certify two genus-3 traces only. No independent complete genus-3 Frobenius certificate, Jacobian map, subgroup action, relation-generation or recovery result.',
 'Sources: ../../runs/RUN-ECDLP-dad803/{raw-result.json,verification.json,manifest.yaml,execution-receipt.json}; publication commit 49c499a9. Full report and graph-source.json beside this PDF.',
]:items.extend([Paragraph(text,styles['BodyText']),Spacer(1,8)])
SimpleDocTemplate(str(directory/'report.pdf'),pagesize=A4).build(items)
