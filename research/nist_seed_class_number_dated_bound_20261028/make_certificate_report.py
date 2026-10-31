"""Render retained observations and explicitly derived inequality margins."""
import csv,hashlib,json
from pathlib import Path
from reportlab import rl_config
rl_config.invariant=1;rl_config.useA85=0
from reportlab.lib.colors import HexColor,white
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.graphics.shapes import Drawing,Rect,String,Line
from reportlab.graphics import renderSVG
P=Path(__file__).resolve().parent;N=P/'p256-import-amendment-02';O=P/'certificate-report-01';O.mkdir(exist_ok=True)
result=json.loads((N/'runs/certificate-01/RESULT.json').read_text());rows=result['rows'];inputs=json.loads((N/'INPUTS.json').read_text())['rows']
sources=[('Baier, dissertation, submitted 26 March 2002, section 2.3.5','h(K) >= 200','https://d-nb.info/964515040/34'),('ETSI TS 102 176-1 V1.2.1, July 2005, 6.1.2.3 and D.3','h(K) >= 200','https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf'),('RFC 5639, March 2010, section 2.1 item 3','h(K) > 10^7','https://www.rfc-editor.org/rfc/rfc5639.html')]
certified=[r for r in rows if r['status']=='CERTIFIED']
def margin(r):return (abs(int(r['D_K']))//(4*int(r['product']))).bit_length()-1
def name(r):return r['name'].replace('skip-'+r['stream'].split(':')[0]+'-','omitted '+r['stream'].split(':')[1]+' / ')
with (O/'cohort.csv').open('w',newline='') as f:
    fields=['index','name','curve_uid','label','stream','p','A','b','n','seed_hex','ordinal','D_K','status','lower_bound','split_primes','product','inequality_margin_bits_floor']
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r,s in zip(rows,inputs):
        x={k:r.get(k) for k in fields};x.update({k:s[k] for k in ['p','b','n','seed_hex','ordinal']});x['A']='-3';x['split_primes']=' '.join(map(str,r['split_primes']));x['inequality_margin_bits_floor']=margin(r) if r['status']=='CERTIFIED' else None;w.writerow(x)
d=Drawing(500,284);left=153;scale=320/max(margin(r) for r in certified)
d.add(String(0,272,'Certificate inequality margin for all 19 certified fields',fontName='Helvetica-Bold',fontSize=10))
d.add(String(0,260,'Teal: omitted; blue: published. Two published fields remain unknown.',fontSize=7.5))
for i,r in enumerate(certified):
    y=252-i*12;v=margin(r);color=HexColor('#176c64' if r['label']=='omitted' else '#466d9b')
    d.add(String(left-8,y+1,name(r),textAnchor='end',fontSize=7.6))
    d.add(Rect(left,y-1,v*scale,7,fillColor=color,strokeColor=None));d.add(String(left+v*scale+4,y+1,str(v),fontSize=7.3))
d.add(Line(left,19,483,19,strokeColor=HexColor('#555555')))
d.add(String(left,7,'floor(log2(|D_K| / (4Q))), derived bits; zero is the boundary',fontSize=7.8))
renderSVG.drawToFile(d,str(O/'certificate-margins.svg'))
table_md='\n'.join('| '+name(r)+' | '+r['label']+' | '+r['status']+' | '+('16,777,216' if r['lower_bound'] else 'unknown')+' |' for r in rows)
md=f'''# Dated CM class-number bounds: complete omission test

28 October 2026 UTC, T-5518. Observation report; no official research-state transition. Two frozen protocol versions and their original runs are retained.

## Observed result

All eleven reconstructed omissions and eight published controls have directly checked maximal-order class-number lower bounds h(K)>=2^24=16,777,216. Every certified row clears both dated bounds. Published P-384 and P-521 remain UNKNOWN_D_K for this method because a certified fundamental field discriminant was not imported. All 21 identities and six streams remain in the table. No row was treated as rejected on missing data.

| Curve / block | Label | Direct-certificate status | Certified lower bound |
|---|---|---|---|
{table_md}

Full field/model/order/seed/ordinal, exact UID, fundamental discriminant, first 24 split primes, exact product Q and outcome are in cohort.csv and the immutable version2 RESULT.json. The editable certificate-margins.svg plots floor(log2(|D_K|/(4Q))) derived from the recorded integers; the minimum is {min(margin(r) for r in certified)} bits. Both omitted and published rows are shown. This margin is sufficient-certificate slack, not a stronger class-number estimate.

## Fixed dated requirements

'''+ '\n'.join(f'* [{title}]({url}): {bound}.' for title,bound,url in sources)+'''

All concern the maximal CM order. Baier describes the German condition as controversial and outside the then-common international criteria. These sources postdate 1997 and do not establish NIST adoption. The requested original Brainpool 2005 PDF timed out; no claim is made about unread contents. The prior all21 h<=2000 list comparison conditionally clears200; the new nineteen certificates do not depend on that external completeness theorem or GRH.

## Certificate and order distinction

The first 24 rational split primes q_i are selected in ascending order with fixed cap10000. Let Q be their product. For fundamental D_K<0, 4Q<|D_K| implies h(K)>=2^24: distinct subset products of prime ideals have distinct classes. Otherwise cancellation would produce an integral principal ideal of squarefree norm N,1<N<=Q. A rational generator has square norm; a nonrational algebraic integer has norm at least |D_K|/4. Both contradict that N. CERTIFICATE-LEMMA.md gives the argument. This is an elementary exact certificate, not the full class-group computation.

The class map from a CM order to the maximal order is surjective, so h(O_K) divides h(End(E)). Each certified lower bound therefore also applies to the actual CM order without determining its conductor. The reverse inference from a large Frobenius-order class number would be invalid. For both P-256 rows the imported factorization gives f_pi=1, hence f_E=1. Published P-256 has3 as a ramified factor of D_K; that3 is not its CM conductor.

## Execution, controls and amendment

Version 1 protocol SHA1fa24263792c84ebf0040ffb7e1b0d03bdb0fe7d21040b5be976a5ca05e53c7e was frozen and committed at72c533ee10 before execution. Its two arms agreed on17 certificates and4 unknowns. Input assembly had omitted the separately archived P-256 first-stage pair. All first outputs and guard failures remain under runs/certificate-01 and export.json.

Version 2 SHA4371127490749adf5413200c7f60710c39347039b7ad179573ec7461438fecb4 was frozen and committed at9c3872cc7f before the two added inputs' witnesses. IMPORT-CHANGE.json pins the original P-256 source and identifies the only two changed records. Producer/audit bytes, threshold, prime-selection rule and all other rows are identical. Both full21 evaluations repeated, giving19 certificates and2 unknowns. Raw version2 commitc58405ea3f precedes this report. No threshold or feature was fitted after either output.

Python 3.13.1 uses trial division for the small primes and Euler symbols; PARI 2.17.3 independently uses nextprime and Kronecker symbols and proves all supplied discriminant factors with isprime. Both check Delta_pi=(p+1-n)^2-4p=f_pi^2 D_K, the complete factor product, square class and fundamental-discriminant relation. Original p,n and curve validity are inherited from the pinned prior records, not newly point-counted here. Source/runtime/input/analysis hashes and exact commands are retained.

Positive controls D=-23/-15,k=1 certify bounds2 (GP exact class numbers3,2); D=-7 correctly returns noncertificate; D=-75 is rejected as nonfundamental; deterministic A/A passes. Exception and early-return controls each exit1 without completion. Across both versions: 4 requested/attempted/completed whole-cohort arm evaluations,0 unexpected failures/timeouts/retries, 4 deliberate failure-guard invocations retained separately. Both experiment.export/v1 checks pass, each flow2/2 complete. CPU/wall receipts are diagnostic on a shared macOS desktop,L0; no performance comparison or attack cost claim.

## Inference and limits

For the two specified dated bounds, zero of eleven omissions fails. Thus this class-number requirement cannot account for any of those omissions; adding it to a two-rule rejection model contributes no exclusions at these bounds. This does not exclude arbitrary different thresholds, other CM predicates, operational failure during class-number validation, or a different historical implementation. Those would need source evidence and a separate prospective test. P-384/P-521 unknowns do not affect the all-eleven result. Reconstructed omissions are not documented original visitation/rejection events.

The historical selector remains unresolved. Existing general CM/transfer and P-224 splitting leads remain separate. Canonical signed-action/SEA graphs were checked and left unchanged: these observations change no isogeny edge, signed action or historical-use claim. This report and its linked result add the dated-bound outcome to the selector problem and study index. No new catalog comparison was needed: this tests exact frozen cryptographic instances, outside the local LMFDB indexes' arbitrary-field coverage.

Next historical discriminator: a dated caller or validation specification that imposes a different concrete endomorphism/class-group condition, or documents failure handling. Do not tune a new bound to these labels or repeat the completed fixed-bound test.
'''
(O/'report.md').write_text(md)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9,leading=11.5,spaceAfter=7));styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=7.5,leading=9,spaceAfter=5))
def para(s,small=False):return Paragraph(s,styles['SmallX' if small else 'BodyX'])
story=[Paragraph('Dated CM class-number bounds',styles['Title']),para('28 October 2026 UTC | T-5518 | observed exact arithmetic; historical selector unresolved'),para('<b>All eleven omissions clear both fixed bounds.</b> Direct certificates prove h(K) &gt;= 16,777,216 for eleven omitted and eight published curves. Published P-384 and P-521 remain UNKNOWN_D_K for this method; every one of the 21 identities is retained.'),para('<b>Dated criteria.</b> Baier 2002 section2.3.5 and ETSI TS 102 176-1 V1.2.1 (July 2005),6.1.2.3/D.3, require h(K) &gt;= 200. RFC 5639 (March 2010),2.1 item3, requires h(K) &gt; 10^7. All refer to the maximal CM order. These later sources do not establish 1997 NIST adoption.'),d,Spacer(1,8),para('<b>Certificate.</b> Select the first 24 split primes q_i, Q=product(q_i). If 4Q &lt; |D_K|, the 2^24 subset ideals represent distinct classes: equality would produce a principal integral ideal of squarefree norm 1 &lt; N &lt;= Q. A rational generator has square norm; a nonrational generator has norm &gt;= |D_K|/4. Both are impossible. Full proof: CERTIFICATE-LEMMA.md.'),para('<b>Inference.</b> At these dated bounds the predicate rejects zero omissions, so contributes no exclusions to a two-rule model. The class map onto the maximal-order class group is surjective; this lower bound also applies to the actual CM order. No exact class number, fitted threshold, historical adoption, or general curve-security conclusion is claimed.'),para('Sources: d-nb.info/964515040/34; ETSI TS 102 176-1 V1.2.1 (2005-07); rfc-editor.org/rfc/rfc5639.html. Full URLs and source boundaries are in report.md and SOURCE-AUDIT.json. The 19 new certificates use no external low-class-number completeness theorem or GRH.',True),PageBreak(),Paragraph('Complete cohort and retained execution',styles['Heading1'])]
data=[['Curve / block','Label','Status / lower bound']]+[[name(r),r['label'],'>=16,777,216' if r['status']=='CERTIFIED' else 'UNKNOWN D_K'] for r in rows]
t=Table(data,colWidths=[235,70,195],rowHeights=[19]+[14]*len(rows));t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('BACKGROUND',(0,0),(-1,0),HexColor('#e4eaf0')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f4f6f8')]),('VALIGN',(0,0),(-1,-1),'MIDDLE')]));story.extend([t,Spacer(1,10),para('<b>Method and controls.</b> Python 3.13.1 trial primes/Euler symbols and PARI 2.17.3 nextprime/Kronecker agree on every record. GP proves source-factor primality. Delta_pi, complete products and fundamental D_K relations check. Positive D=-23/-15, noncertificate D=-7, nonfundamental D=-75,A/A and both fail-closed guards pass. Exact models,orders,seeds,UIDs,prime lists and products: cohort.csv and version2 RESULT.json.'),para('<b>Amendment retained.</b> Version 1 gave 17 certificates / 4 unknowns because the separately archived P-256 pair was omitted from input assembly. Version 2 adds only those two original source records; unchanged producer/audit bytes and selection rule. Each protocol was frozen and committed before its affected witnesses. Across both versions: 4 full-cohort evaluations completed, 0 unexpected failures/timeouts/retries, 4 deliberate guard failures retained. Both unified exports validate. Shared-desktop clocks are diagnostic only.'),para('<b>Conductor clarification.</b> Both P-256 records have f_pi=1, hence f_E=1. The factor 3 in published P-256 D_K is ramification, not its conductor. A large Frobenius-order class number alone would not certify a large maximal-order class number.'),para('<b>Limits and next evidence.</b> No original visitation log or 1997 use is established. Different thresholds, operational failures or other CM predicates remain outside this test; a new source-defined rule needs a prospective test. P-384/P-521 unknowns do not change the all-eleven result. Existing signed-action/SEA graphs are unchanged.'),para('Protocol hashes: v1 1fa24263792c84ebf0040ffb7e1b0d03bdb0fe7d21040b5be976a5ca05e53c7e; v2 4371127490749adf5413200c7f60710c39347039b7ad179573ec7461438fecb4. Freeze commits72c533ee10/9c3872cc7f; raw commits542375f6b3/c58405ea3f. PR2602; report.md contains exact paths,commands and provenance.',True)])
def footer(canvas,doc):
    canvas.setFont('Helvetica',7);canvas.drawString(48,24,'NIST-DATED-CLASS-BOUND-01 | certificate-01 + prospective amendment02');canvas.drawRightString(564,24,str(doc.page))
SimpleDocTemplate(str(O/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=34,bottomMargin=36).build(story,onFirstPage=footer,onLaterPages=footer)
print('Report, full identity CSV, editable SVG and PDF rendered:',O)
