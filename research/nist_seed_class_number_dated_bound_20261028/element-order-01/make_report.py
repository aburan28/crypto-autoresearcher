"""Present retained first-prime class-element observations, no new trials."""
import csv,json
from pathlib import Path
from reportlab import rl_config
rl_config.invariant=1;rl_config.useA85=0
from reportlab.lib.colors import HexColor,white
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.graphics.shapes import Drawing,Rect,String,Line
from reportlab.graphics import renderSVG
P=Path(__file__).resolve().parent;O=P/'report-01';O.mkdir(exist_ok=True);R=json.loads((P/'runs/element-01/RESULT.json').read_text());rows=R['rows'];inputs=json.loads((P/'INPUTS.json').read_text())['rows']
def name(r):return r['name'].replace('skip-'+r['stream'].split(':')[0]+'-','omitted '+r['stream'].split(':')[1]+' / ')
fields=list(rows[0])+['p','A','b','n','seed_hex','ordinal']
with (O/'cohort.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for r,s in zip(rows,inputs):w.writerow({**r,**{k:s[k] for k in ['p','b','n','seed_hex','ordinal']},'A':'-3'})
d=Drawing(500,288);left=155
d.add(String(0,277,'First odd split prime used for the single-element witness',fontName='Helvetica-Bold',fontSize=10));d.add(String(0,264,'Teal: omitted; blue: published. Every known-D_K row passes order >= 200.',fontSize=7.7))
for i,r in enumerate(rows):
 y=249-i*10.7;d.add(String(left-8,y,name(r),textAnchor='end',fontSize=7.4))
 if r['prime']:
  width=r['prime']*12;d.add(Rect(left,y-1,width,6,fillColor=HexColor('#176c64' if r['label']=='omitted' else '#466d9b'),strokeColor=None));d.add(String(left+width+4,y,str(r['prime']),fontSize=7.4))
 else:d.add(String(left+5,y,'UNKNOWN D_K',fontSize=7.4))
d.add(Line(left,25,465,25,strokeColor=HexColor('#555555')));d.add(String(left,10,'Prime q (integer); first-prime policy is a fixed research choice.',fontSize=7.7));renderSVG.drawToFile(d,str(O/'first-prime.svg'))
diagram=Drawing(500,72)
for x,t,b,c in [(0,'Class number bound','19 fields: h(K) >= 2^24','#e8f3ee'),(173,'Individual class element','19 fields: order >= 200','#e8f3ee'),(346,'Historical use','1997 caller: unknown','#fff3dd')]:
 diagram.add(Rect(x,10,154,52,fillColor=HexColor(c),strokeColor=HexColor('#506070')));diagram.add(String(x+77,43,t,textAnchor='middle',fontName='Helvetica-Bold',fontSize=8.3));diagram.add(String(x+77,25,b,textAnchor='middle',fontSize=8))
renderSVG.drawToFile(diagram,str(O/'evidence-boundary.svg'))
table='\n'.join('| '+name(r)+' | '+r['label']+' | '+str(r['prime'] or 'unknown')+' | '+str(r['powers_checked'])+' | '+r['status']+' |' for r in rows)
md=f'''# A single class-group witness also passes on all eleven omissions

28 October 2026 UTC, T-5518; NIST-CLASS-ELEMENT-ORDER-01, run element-01. Observation report only; no official hypothesis or goal transition.

## Recorded result

All eleven reconstructed omissions and eight publications have a directly checked ideal-class element of order at least 200, using the first odd split rational prime. No retries are needed under this fixed policy. Both implementations agree on all 3,781 reduced powers per arm (19*199), all controls and all 21 summaries. Published P-384/P-521 retain UNKNOWN_D_K; all six streams stay present. No chosen element returns to the identity among powers 1..199.

| Curve / block | Label | First odd split q | Powers checked | Result |
|---|---|---:|---:|---|
{table}

The full UID/model/p/n/seed/ordinal, source discriminant and transcript hashes are in cohort.csv. Every reduced triple is retained under runs/element-01/python and gp, one JSON file per curve and arm; largest file24,158 bytes. The quantitative first-prime.svg is drawn only from recorded q values. Its prime-selection policy is a research choice because the source leaves that choice unspecified; no fitted acceptance threshold or historical distribution is inferred.

## Source and the distinction tested

[ETSI TS102176-1 V1.2.1, July 2005](https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf), Annex D.1 and D.3, printed 43-46, asks for one ideal-class element of order at least MinClass=200. The proposed test composes that element through powers 1..199 and fails if identity appears. It tells generation to restart if a suitable element cannot be found, but expressly leaves element selection and the unsuccessful-selection limit unspecified. This is a real operational gap in that later document, not authenticated evidence about the 1997 NIST caller.

The previous direct h(K)>=2^24 result does not alone imply that a single element has order>=200: a large finite abelian group can have small exponent. The new test checks the additional single-element witness directly. Existence of this witness clears the source's threshold on every omitted curve; a hypothetical low-order first witness would not prove that no other witness exists.

The lifting rationale in Annex D.3 concerns a lift to characteristic zero preserving the CM endomorphism ring. It supplies no concrete discrete-log transfer algorithm. Merely lifting finite-field equation coefficients to rational integers does not establish preservation of the CM ring or subgroup transport. [Baier2002 section2.3.5](https://d-nb.info/964515040/34) describes the same class-number concern as controversial. These later sources do not establish1997 adoption, nor rule out all other transfer ideas.

## Two exact paths

Both arms choose the first odd split prime q<=10000, then the least positive odd b<2q with b^2 congruent D_K modulo4q. Python directly constructs each q^m ideal by Hensel lifting b and independently implements Gauss reduction. If a=q^m and c=(b^2-D_K)/(4a), the next root is b+2a*k with k=-c/b moduloq. This preserves the selected prime-ideal orientation. GP repeatedly composes the original Qfb(q,b,c) with qfbcomp. [Official PARI documentation](https://pari.math.u-bordeaux.fr/dochtml/html-stable/Arithmetic_functions.html) specifies composition and reduction. Every reduced triple, not merely the final order flag, agrees.

The exact imported19 fundamental discriminants and21 identities are byte-identical to the completed P-256 source amendment. Both arms recheck discriminant/factor relations; GP proves all supplied factors prime. Curve point counts and ordinary status are inherited from prior certified records; this is no new point-count computation. No class-number algorithm assuming GRH is used.

## Controls, execution and custody

Known D=-23 has selected-element order3, so passes threshold3 and returns at3 for threshold4; D=-15 returns at2; D=-7 returns at1. Nonfundamental D=-75 is rejected, deterministic A/A agrees, and unexpected-exception/early-return guards each exit1 without completion. Two initial control-only GP syntax failures are retained in preflight; renaming the built-in powers function to classpowers fixed the parser before freeze. No cohort input ran in those preflights.

Protocol SHA0636225ef6ce97eaa0c831093b946a6da960edd0e04c366d12db65e68f86ec60 was frozen and committed at a49aa5259d before cohort data; a successful S3 resume checkpoint and gate preceded launch. Exact command: python3 research/nist_seed_class_number_dated_bound_20261028/element-order-01/run.py . Python3.13.1 and PARI2.17.3 on shared macOS, one thread each;180s timeout per arm,30s guards,no retries. Raw commit c8163cfe2b precedes this report. Flow:2 requested/attempted/completed full-cohort evaluations,0 unexpected failures/timeouts,2 deliberate guard failures retained separately. The unified export passes file verification. Process CPU/wall values are diagnostic,L0; no performance claim. Source, executable, input, output and analysis hashes are retained in protocol/manifests/export/receipts.

## Inference boundary and next discriminator

Zero omissions fails the class-number bounds or this first-element threshold 200 check. Thus neither property supplies the missing exclusions. This result does not authenticate NIST's choice of class element, retries, arithmetic backend, failure behavior or use of any class-group test; it is not a claim that every historical implementation would succeed. Unknown P-384/P-521 do not affect the all-eleven witness result. Reconstructed omissions are not original rejection logs.

Canonical signed-action/SEA diagrams were checked and remain unchanged. evidence-boundary.svg keeps the independently tested number-of-classes and order-of-one-element facts separate from missing historical-use evidence. Existing P-224 cube/splitting lead stays open. The source-based next check is the actual May1997 generic polynomial-degree routines against later documented splitting-degree fixes, with no assumption that a later bug already existed or was called by NIST. Any actual curve test requires a newly frozen source condition and all 21 accounting. Full historical-selector goal remains active and unresolved. No outgoing contacts, subagents or memory writes.
'''
(O/'report.md').write_text(md)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BX',fontName='Helvetica',fontSize=9.2,leading=12.3,spaceAfter=8));styles.add(ParagraphStyle(name='SX',fontName='Helvetica',fontSize=7.6,leading=9.7,spaceAfter=6))
def para(s,small=False):return Paragraph(s,styles['SX' if small else 'BX'])
story=[Paragraph('One ideal-class element: fixed bound 200',styles['Title']),para('28 October 2026 UTC | T-5518 | NIST-CLASS-ELEMENT-ORDER-01 | observed exact arithmetic'),para('<b>All eleven omissions pass on the first witness.</b> The first odd split prime gives an ideal class of order at least 200 for eleven omissions and eight publications. Both methods agree on 3,781 reduced powers per arm. Published P-384/P-521 remain UNKNOWN_D_K; all 21 rows and six streams are retained.'),diagram,Spacer(1,8),d,Spacer(1,6),para('<b>What changed.</b> ETSI (July 2005), Annex D.1/D.3, asks for one element of order at least 200, and leaves element selection and retry limits unspecified. A large class number alone does not prove a large-order individual element. This test checks the latter directly, using a fixed first-prime policy before observing any cohort powers.'),para('<b>Lifting limit.</b> The cited rationale concerns a characteristic-zero lift preserving the CM endomorphism ring. Lifting equation coefficients to integers does not establish that property or a discrete-log transfer. No 1997 NIST adoption or historical rejection policy follows.'),para('Primary source: ETSI TS102176-1 V1.2.1 (2005-07), Annex D.1/D.3, printed 43-46. d-nb.info/964515040/34 section2.3.5 gives the 2002 discussion; PARI Arithmetic_functions.html documents exact form composition. Full URLs, paths and limits are in report.md.',True),PageBreak(),Paragraph('Full cohort, independent arithmetic and limits',styles['Heading1'])]
data=[['Curve / block','Label','q','Powers','Element order']]+[[name(r),r['label'],str(r['prime'] or '?'),str(r['powers_checked']),'>=200' if r['prime'] else 'UNKNOWN D_K'] for r in rows]
t=Table(data,colWidths=[219,58,28,48,147],rowHeights=[19]+[14]*21);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('BACKGROUND',(0,0),(-1,0),HexColor('#e4eaf0')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f4f6f8')]),('VALIGN',(0,0),(-1,-1),'MIDDLE')]));story.extend([t,Spacer(1,10),para('<b>Independent paths.</b> Python constructs prime-power ideals by Hensel lifting and elementary Gauss reduction. PARI repeatedly composes the original form. Every reduced triple agrees, through powers 1..199; zero identity returns on the 19 nonmissing rows. Input discriminants are rechecked; GP proves source-factor primality. Complete models, UIDs and transcripts are linked in cohort.csv.'),para('<b>Controls and process outcomes.</b> Exact orders 1, 2, 3, passing/failing threshold controls, nonfundamental input and deterministic A/A pass. Exception and early-return guards fail closed. Two control-only GP parser failures and their repair precede freeze and remain retained. Both whole-cohort arms complete; no unexpected trial failure, timeout or retry. Export file verification passes. Desktop clocks are diagnostic only.'),para('<b>Boundary.</b> First-prime selection is a fixed research policy; ETSI does not prescribe it. These observations exclude no omissions at threshold 200, but establish no original NIST invocation, retry/error policy or historical class-group implementation. Neither class number nor this element-order property identifies the missing selector. The P-224 splitting lead and other source-defined mechanisms remain open.'),para('Frozen protocol 0636225ef6ce97eaa0c831093b946a6da960edd0e04c366d12db65e68f86ec60; freeze commit a49aa5259d; raw commit c8163cfe2b. Exact commands, source/runtime hashes, controls and all 42 per-curve transcript files are retained. Historical goal active/unresolved; no official status promotion.',True)])
def footer(c,doc):c.setFont('Helvetica',7);c.drawString(48,24,'NIST-CLASS-ELEMENT-ORDER-01 | run element-01 | first-prime policy; no historical-use claim');c.drawRightString(564,24,str(doc.page))
SimpleDocTemplate(str(O/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=32,bottomMargin=36).build(story,onFirstPage=footer,onLaterPages=footer)
print('Rendered',O)
