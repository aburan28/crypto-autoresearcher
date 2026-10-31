"""Derived report and editable vector figures from the frozen CCR observations."""
import csv,html,json,re
from pathlib import Path
from reportlab import rl_config
rl_config.useA85=0
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
P=Path(__file__).resolve().parent
A=json.load(open(P/'AUDIT.json'));B=json.load(open(P/'BUNDLE.json'));R=list(csv.DictReader(open(P/'comparison.csv')))
assert len(R)==21 and sum(int(r['S1_roots']) for r in R)==112 and sum(int(r['corrected_unique_kernels']) for r in R)==112
assert sum(int(r['literal_unique_kernels']) for r in R)==9 and all(int(r['literal_unique_kernels_degree_at_least5'])==0 for r in R)
BLUE='#287ca4';ORANGE='#c46b35';NAVY='#19384d';GRAY='#536c7c'
def label(r):return f"{'P' if r['label']=='published' else 'O'} {int(r['p']).bit_length()}/{r['ordinal']}"
def svg_bars():
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="650" viewBox="0 0 920 650"><rect width="920" height="650" fill="white"/>',f'<g font-family="Arial" fill="{NAVY}"><text x="20" y="28" font-size="21">Distinct cyclic kernels recovered at the seven declared degrees</text><text x="20" y="51" font-size="14">Corrected conversion recovers all 112 available kernels; literal conversion recovers nine, all at degree 3.</text>']
    for i,r in enumerate(R):
        y=74+i*23;n=int(r['corrected_unique_kernels']);m=int(r['literal_unique_kernels']);out.append(f'<text x="20" y="{y+13}" font-size="14">{label(r)}</text><rect x="150" y="{y}" width="{45*n}" height="9" fill="{BLUE}"/><rect x="150" y="{y+10}" width="{45*m}" height="7" fill="{ORANGE}"/><text x="{160+45*n}" y="{y+13}" font-size="13">{n} / {m}</text>')
    out.append(f'<rect x="20" y="584" width="14" height="10" fill="{BLUE}"/><text x="41" y="594" font-size="14">Corrected</text><rect x="160" y="584" width="14" height="10" fill="{ORANGE}"/><text x="181" y="594" font-size="14">Literal draft</text><text x="350" y="594" font-size="14">P=published; O=reconstructed omission</text>')
    out.append('<text x="20" y="622" font-size="12">CCR-ROOT-MATCHING-01. Units: distinct kernels summed across degrees 3,5,7,11,13,17,19.</text><text x="20" y="642" font-size="12">n=21 fixed identities,147 cells,848 cohort pair reconstructions. Deterministic exact counts; no error bars.</text></g></svg>');return ''.join(out)
DIAGRAM={'nodes':[{'id':'input','label':'21 frozen identities; no labels/orders enter observer'},{'id':'projections','label':'S1,Anew,Bnew projected root sets; exact minimality + all roots'},{'id':'source','label':'Paper: no S1 root -> next auxiliary prime; choose nonrepeated root'},{'id':'pairs','label':'424 pairs per arm; corrected/literal conversions retained'},{'id':'kernels','label':'Division polynomial + cyclic closure + Frobenius/trace binding'},{'id':'history','label':'Original executable, q-series builder and stopping policy unknown'}],'edges':[['input','projections'],['projections','source'],['source','pairs'],['pairs','kernels'],['kernels','history']],'isogeny_map_claim':False,'historical_use':'unestablished'}
def svg_workflow():
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="255" viewBox="0 0 920 255"><rect width="920" height="255" fill="white"/>',f'<g font-family="Arial" fill="{NAVY}" font-size="16">']
    for x,y,w,a,b in [(15,20,270,'21 inputs / seven degrees','No labels or orders in observer'),(325,20,270,'Independent projected roots','No cohort collisions;112 S1 roots'),(635,20,270,'Try every root pairing','424 pairs per conversion arm'),(325,150,270,'112 corrected cyclic kernels','Closure and trace independently checked'),(635,150,270,'Historical selector unresolved','Original caller and configuration missing')]:out.append(f'<rect x="{x}" y="{y}" width="{w}" height="66" rx="7" fill="#eaf1f6"/><text x="{x+12}" y="{y+27}">{a}</text><text x="{x+12}" y="{y+50}" font-size="12">{b}</text>')
    out.append(f'<path d="M285 52 H325 M595 52 H635 M770 86 V119 H460 V150 M595 182 H635" fill="none" stroke="{GRAY}" stroke-width="2"/><text x="15" y="244" font-size="12">Evidence flow only. No evaluable isogeny transfer map or historical-use attribution is asserted.</text></g></svg>');return ''.join(out)
class Bars(Flowable):
    def __init__(self):super().__init__();self.width=490;self.height=335
    def draw(self):
        c=self.canv;c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica-Bold',10);c.drawString(0,321,'Distinct cyclic kernels recovered: corrected / literal conversion')
        for i,r in enumerate(R):
            y=301-i*12;n=int(r['corrected_unique_kernels']);m=int(r['literal_unique_kernels']);c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica',7);c.drawString(0,y,label(r));c.setFillColor(colors.HexColor(BLUE));c.rect(80,y,24*n,5,fill=1,stroke=0);c.setFillColor(colors.HexColor(ORANGE));c.rect(80,y-5,24*m,4,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(86+24*n,y,str(n)+' / '+str(m))
        c.setFillColor(colors.HexColor(BLUE));c.rect(0,32,9,7,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(14,32,'Corrected');c.setFillColor(colors.HexColor(ORANGE));c.rect(95,32,9,7,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(109,32,'Literal draft');c.drawString(205,32,'P=published; O=reconstructed omission')
        c.drawString(0,17,'Unit: distinct kernels summed over seven degrees. n=21 curves,147 cells; exact counts, no error bars.')
        c.drawString(0,5,'CCR-ROOT-MATCHING-01;848 cohort pair reconstructions; all nine literal kernels occur at degree 3.')
class Workflow(Flowable):
    def __init__(self):super().__init__();self.width=490;self.height=123
    def draw(self):
        c=self.canv
        for x,y,w,title,sub in [(0,74,145,'21 frozen curve inputs','Seven declared degrees'),(169,74,145,'112 rational S1 values','No cohort projection collisions'),(338,74,150,'All root pairings','424 per conversion arm'),(169,0,145,'112 corrected kernels','Cyclic + trace binding checked'),(338,0,150,'Selector unresolved','Original caller unestablished')]:
            c.setFillColor(colors.HexColor('#eaf1f6'));c.roundRect(x,y,w,42,4,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica-Bold',7.4);c.drawString(x+7,y+26,title);c.setFont('Helvetica',6.7);c.drawString(x+7,y+12,sub)
        c.setStrokeColor(colors.HexColor(GRAY));c.line(145,95,168,95);c.line(314,95,337,95);c.line(412,74,412,58);c.line(412,58,241,58);c.line(241,58,241,43);c.line(314,21,337,21)
REPORT=f'''# CCR root matching on all 21 NIST/ANSI curve candidates

2026-10-27. T-5518. Observation report; no formal hypothesis decision. The missing historical selector remains unidentified. The corrected CCR root-pairing reconstruction recovers every one of 112 rational cyclic kernels across all 147 fixed-cohort cells. All eleven reconstructed omissions and all ten publications enter a favorable case at degree seven or higher. None exhibits the projected-coordinate collisions tested here.

## Source-based question and exact scope

The 24-page Charlap-Coley-Robbins draft describes independently finding roots for the half-kernel sum S1 and quotient coefficients Anew,Bnew, trying possible pairings, and validating the reconstructed kernel. Page6 explicitly advances to the next auxiliary prime if no base-field S1 root exists and uses a non-repeated S1 root. Page18 tries pairings rather than prescribing rejection after one failed guess. These are auxiliary-prime and root-selection rules; they are not a documented curve-rejection criterion. Morain1995 printed page275 corrects the coefficient conversion; his example over F101 supplies a control. No original 1997 executable is authenticated.

CCR-ROOT-MATCHING-01 freezes degrees3,5,7,11,13,17,19 and the same21 curve identities, ten publications and eleven reconstructed omissions across six streams. [comparison.csv](comparison.csv) preserves full UIDs, fields, model coefficients, orders, seeds and ordinals; [cells.csv](cells.csv) records every curve/degree result. Cohort SHA-256: `{B['cohort_sha256']}`. The native observer receives only index,p,A,B,ell. Known orders and labels enter the independent post-audit only.

Fresh projected polynomials are computed in the full ell-division algebra, not by executing the historical one-time q-series coefficient builder. Independent annihilation identities plus Krylov-rank proofs establish exact minimality. Full degree ell+1 on every cohort projection proves distinct algebraic coordinate values; the rational root sets agree with the corresponding mathematical projection polynomials. Special controls can have fewer distinct values and retain their collisions. The actual historical coefficient tables, root enumeration and stopping policy remain unknown.

## Measured and independently verified outcomes

- Successful native attempt03 completes147 cohort cells and five controls. There are67 favorable cohort cells and112 rational S1 values. All112 have non-repeated source fibers and recover a cyclic kernel with the corrected conversion. Projection-collision cells: zero.
- Each conversion arm tries all424 cohort root tuples. Corrected conversion yields172 successful division-factor pairings and112 distinct cyclic kernels; all112 have coherent quotient coefficients. At degree3, several Anew/Bnew pairings reconstruct the same degree-one kernel, so pairings are not counted as distinct kernels.
- Literal-draft conversion yields69 factor pairings but only nine distinct cyclic kernels, all at degree3 where kernel recovery depends on S1 alone. It recovers zero kernels at degrees5,7,11,13,17,19. Every cohort curve has a favorable case at degree7 or higher, including all publications. Thus this literal error still does not explain the historical split.
- Including controls:456 exact projection-minimality proofs,735 independent scalar-coordinate checks,932 pair reconstructions and249 cyclic-pair Frobenius/trace checks. FLINT independently proves all rational-root sets complete. Integer arithmetic reconstructs division polynomials, both moment conversions, Newton kernels, all remainders and cyclic closure. For a cyclic kernel, Frobenius x-coordinates yield a sign-ambiguous trace set containing the independently known trace; no sign-resolution or full point count is claimed.
- The published-example A/A captures match exactly after normalizing only their observer index. Arithmetic controls include20 packed-versus-naive products, two rejected false certificates, and a deficient-rank annihilator control.

![Recorded kernels](kernel-recovery.svg)

## Controls and the actual non-repeated-root rule

Morain's published example is y^2=x^3+x+1 over F101 at degree7, with S1=31,Anew=19,Bnew=26 and kernel x^3+70x^2+47x+10. Corrected recovery reproduces it and rejects incorrect pairings; the literal arm recovers no degree7 kernel. A favorable degree19 control on the same curve exercises the entire higher recurrence before cohort calls.

The j0 control y^2=x^3+1 over F101 has projection degrees[7,7,4] instead of[8,8,8]. Its three rational S1 values have division-fiber degrees[6,3,3]. The first value combines two subgroup fibers and lacks a recovered cyclic degree7 kernel. The source's non-repeated-root rule excludes that value; the other two recover valid kernels. This is a detectable coordinate complication, not a claim that the documented algorithm rejects this control curve. The j1728 control y^2=x^3+x has degrees[8,4,8] and no rational roots at degree7. Neither special control belongs to the cohort.

All three control orders were directly enumerated:105,102,100, traces-3,0,2. Local LMFDB av_fq classes1.101.d,1.101.a,1.101.ac respectively have matching trace polynomials1+3T+101T^2,1+101T^2,1-2T+101T^2. These are isogeny-class consistency checks, not individual-model identifications. Source postgresql://devmirror.lmfdb.xyz:5432/lmfdb/public.av_fq_isog; extraction ended2026-10-19T16:45:49.243703+00:00. All four selected-index manifests were complete before querying. CONTROL-COUNTS.json retains exact models, labels and provenance. No challenge-curve catalog crosswalk is claimed.

![Evidence flow](workflow.svg)

## Retained failures and diagnostic resource data

Attempt01 passes the published-example gate but its fixed32-case generic collision search finds no required collision. It stops before any cohort call. Attempt02 changes that control to explicit special-j curves, then starts all147 cohort cells:101 finish and46 remain partial because GP factorial() returns a real value. The process exits0 and prints its final marker despite those internal errors; both stderr and per-cell completion framing are therefore required. Attempt03 uses exact integer factorials, adds the favorable maximum-degree control, and completes all147 cells without those errors. Every previous capture remains retained. A static pre-run amendment corrected GP's second-derivative syntax before any observer call. The earlier API calibration evaluated only a small noncohort example; its full stream was not retained locally and it is not counted as a frozen cohort trial.

There are three recorded external GP observer invocations. Across retained attempts,294 cohort cells start,248 complete and46 remain partial; these are case counts, not process counts. Attempt03 wall time4.730161s,user CPU4.643442s,system CPU0.022960s are measured diagnostics on modern macOS ARM64 under uncontrolled load, not performance comparisons or historical timing. Initial independent audit wall time80.286795s is also diagnostic; verifier CPU time was not captured. Operational errors do not count as curve rejections.

## Evidence, replay and remaining limits

The raw export seals{B['sealed_files']} files; archive bytes{B['archive_bytes']:,}, SHA-256`{B['archive_sha256']}`. After extraction, run `python3 -B evidence/verify.py` with python-flint0.9.0. Replay checks manifests, all three attempt receipts/framing, the complete final arithmetic audit, and the full fixed-cohort bindings. It invokes no external scientific producer or network; FLINT arithmetic runs in process. The full replay passed after archive extraction into a different directory. Publisher PDFs/images and interpreter/FLINT binaries remain outside the export; exact source URLs and digests are retained.

This reconstruction excludes no cohort candidate under the documented non-repeated-root and pairing predicates at the seven tested degrees. It supplies no transfer, endomorphism exclusion or historical selector. It does not execute the original q-series builder, historical root ordering, all larger degrees, full eigenvalue sign recovery, CRT/resource policies or candidate visitation. Existing canonical/Atkin, FreeLIP, SEA and ECPP graphs retain their separate sealed scopes; this report adds separate figures and changes no official hypothesis status.

Primary sources: [CCR draft](https://www.lix.polytechnique.fr/Labo/Francois.Morain/Introuvables/Drafts/ccr.pdf), pages6,8-9,18; [Morain1995](https://jtnb.centre-mersenne.org/item/10.5802/jtnb.143.pdf), printed274-275. CCR is cited as1991/1992, while recovered scan metadata is2018; exact draft version is unestablished. The printed correction is dated1995. Source behavior is distinct from proven original-program use.

Canonical object-store delivery stopped at HeadObject403. Exact archive bytes were pushed in Git under the existing large-file-ok PR exception; no remote store success is claimed. Inherited immutable A/A record collisions still prevent a clean merge-readiness claim. The scientific goal remains open.
'''
def readable(s):
    s=re.sub(r'\b(tries|has|and|its|Its|across|Across|Page|page|cells|controls|pairs|orders|attempts|CPU|wall|exits|fibers|all|All|of|at|over|including|degrees|degree|printed|pages|ended|classes|Morain|Attempt|attempt|Fixed)(?=\d)',r'\1 ',s)
    s=re.sub(r'(Degrees|controls|cells|attempts|CPU|wall):(?=\d)',r'\1: ',s)
    return s.replace('F101','F_101').replace('python-flint0.9.0','python-flint 0.9.0').replace('cohort147','cohort 147')
def pdf():
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=7,textColor=colors.HexColor(NAVY)));styles.add(ParagraphStyle(name='Tiny',fontSize=7.5,leading=10,spaceAfter=4));body=styles['BodySmall'];story=[]
    def p(s):story.append(Paragraph(readable(s),body))
    def h(s):story.append(Paragraph(s,styles['Heading2']))
    story.append(Paragraph('CCR root matching on all 21 candidates',styles['Title']));p('2026-10-27 | T-5518 | Observation report; no formal hypothesis decision.')
    p('<b>The historical selector remains unknown.</b> Corrected recovery finds all112 available cyclic kernels across147 curve/degree cells. All11 omissions and all10 publications enter a favorable case at degree7 or higher. No cohort projection collision is found.')
    h('1. Two conversions, every root pairing')
    p('Degrees:3,5,7,11,13,17,19. The observer receives p,A,B,ell,index; labels and known orders enter independent post-audit only. Fresh mathematical projection root sets replace historical q-series tables. This is a bounded reconstruction, not the original executable.')
    story.append(Bars())
    p('Each arm tries424 cohort root tuples. Corrected conversion has172 successful factor pairings but112 distinct cyclic kernels. Literal conversion has69 factor pairings but only nine distinct kernels, all at degree3. There are no literal successes at degree5 or higher.')
    p('At degree3 the kernel depends on S1 alone; different quotient-coefficient pairs can produce the same kernel. Counting those as independent successful kernels would inflate the result. The chart plots distinct kernels per curve/degree, summed over the declared levels.')
    story.append(PageBreak());story.append(Paragraph('2. Source predicates and independent checks',styles['Heading1']))
    p('CCR page6 advances to the next auxiliary prime when no base-field S1 root exists, then selects a non-repeated root. Page18 tries pairings of independently found Anew and Bnew roots and tests the putative division factor. It does not prescribe rejecting a curve after one bad guess.')
    p('<b>Independently verified:</b> full division polynomials and scalar x-coordinates; projected-polynomial annihilation plus Krylov-rank minimality; complete rational root sets; both power-sum conversions; every Newton kernel and division remainder; cyclic closure; sign-ambiguous Frobenius trace sets containing known traces.')
    p('Including controls:456 projection-minimality proofs,735 scalar-coordinate checks,932 pair reconstructions and249 cyclic-pair trace checks. Cohort projection degrees are always ell+1, so none has the tested coordinate collisions or repeated S1 values. All112 rational S1 values recover a corrected cyclic kernel.')
    h('Controls expose the condition that is absent from the cohort')
    data=[['F101 model','Projection degrees at7','Observed result'],['A=1,B=1 (ordinary)','8,8,8','Published S1=31,Anew=19,Bnew=26 kernel reproduced'],['A=0,B=1 (j0)','7,7,4','S1 fibers6,3,3: repeated value rejected by source root rule; other two recover'],['A=1,B=0 (j1728)','8,4,8','Projection collision; no rational roots at7']]
    table=Table([[Paragraph(html.escape(readable(v)),styles['Tiny']) for v in row] for row in data],colWidths=[120,110,260]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf1f6')),('GRID',(0,0),(-1,-1),.3,colors.lightgrey),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(table);story.append(Spacer(1,8))
    p('The j0 control has one unfiltered S1 value without a cyclic kernel. The paper already excludes that repeated root. This demonstrates the coordinate complication; it is not evidence that the documented method rejects the control curve. No cohort case has it.')
    p('A favorable degree19 control exercises the highest recurrence index before cohort calls. The published-example A/A captures match exactly after normalizing only index. Direct control orders105,102,100 agree with local LMFDB isogeny classes1.101.d,1.101.a,1.101.ac; those rows do not identify individual models.')
    story.append(Workflow());story.append(PageBreak())
    story.append(Paragraph('3. Complete custody and remaining limits',styles['Heading1']))
    p('Attempt01 stops at its required collision-control gate, before any cohort call. Its32-case generic scan found no collision. Attempt02 starts147 cohort cells;101 complete and46 remain partial because GP factorial() yields a real value. The process still exits0 and prints its final marker: stderr and per-cell framing are essential.')
    p('Attempt03 uses exact integer factorials and the maximum-degree control. All147 cohort cells and five controls finish. Every unsuccessful capture and amendment remains in the export; operational failures are not curve rejections. A pre-run derivative-syntax correction started no observer call.')
    p('Three external GP observer processes are recorded. Across retained attempts:294 cohort cells started,248 completed,46 partial. Final native diagnostic wall/user CPU/system CPU:4.730161/4.643442/0.022960 seconds. Independent audit wall:80.286795 seconds; its CPU time was not captured. These modern ARM64 observations are not performance or historical-runtime comparisons.')
    h('Raw evidence and replay')
    p(f'Archive: {B["sealed_files"]} sealed files; {B["archive_bytes"]:,} bytes.<br/>SHA-256: {B["archive_sha256"]}')
    p('After extraction, use python-flint0.9.0 and run:<br/><font face="Courier">python3 -B evidence/verify.py</font><br/>The full audit passed after extraction into a different directory. No external producer or network is invoked. FLINT runs in process. Exact fields/models/orders/seeds/UIDs are in comparison.csv and the sealed cohort.')
    p('Local LMFDB manifests were complete before querying. The av_fq source was postgresql://devmirror.lmfdb.xyz:5432/lmfdb/public.av_fq_isog, extraction ended2026-10-19T16:45:49.243703+00:00. CONTROL-COUNTS.json binds exact models, direct counts, labels and provenance. No challenge crosswalk is claimed.')
    h('What remains unestablished')
    p('Original q-series builder and tables; executable lineage; historical root enumeration; larger auxiliary degrees; full sign recovery, CRT/resource policy and candidate visitation. The documented root and pairing rules tested here do not separate the labels. No transfer or endomorphism selection rule is identified.')
    p('Primary sources: CCR draft pages6,8-9,18 in Morain\'s author archive; Morain1995, printed274-275, doi:10.5802/jtnb.143. Full URLs and digests are in report.md and source receipts. The CCR scan version remains uncertain. Publisher PDFs/images and interpreter binaries are excluded explicitly.')
    p('Canonical store push was refused at HeadObject403. Git retains the exact archive under the existing PR exception. Inherited immutable A/A-record collisions remain; no green merge-readiness claim or formal hypothesis change is made.')
    def foot(c,doc):c.setFont('Helvetica',7);c.setFillColor(colors.HexColor(GRAY));c.drawString(50,30,'T-5518 | CCR-ROOT-MATCHING-01 | Fixed 21 identities;147 cells; no historical-use attribution');c.drawRightString(560,30,str(doc.page))
    SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),leftMargin=50,rightMargin=60,topMargin=42,bottomMargin=44,title='CCR root matching on the fixed NIST/ANSI cohort',author='Research observation record',invariant=1).build(story,onFirstPage=foot,onLaterPages=foot)
def main():
    (P/'kernel-recovery.svg').write_text(svg_bars());(P/'workflow.svg').write_text(svg_workflow());(P/'workflow.diagram.json').write_text(json.dumps(DIAGRAM,indent=2)+'\n');(P/'report.md').write_text(readable(REPORT));pdf()
if __name__=='__main__':main()
