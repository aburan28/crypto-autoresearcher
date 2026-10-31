"""Editable figures and report from recorded observations only."""
import csv,html,json,re
from pathlib import Path
from reportlab import rl_config
rl_config.useA85=0
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
P=Path(__file__).resolve().parent
A=json.load(open(P/'AUDIT.json'));F=json.load(open(P/'FIBER-AUDIT.json'));C=json.load(open(P/'FORMULA-AUDIT.json'));B=json.load(open(P/'BUNDLE.json'))
ROWS=list(csv.DictReader(open(P/'comparison.csv')))
assert len(ROWS)==21 and sum(int(r['fiber_checks']) for r in ROWS)==2071
assert (A['curve_level_cells'],F['rational_parameter_roots'],C['cohort_all_algebraic_kernels_fail_literal_pair'])==(1281,1185,21)
NAVY='#18364c';BLUE='#287ca4';TEAL='#238576';GRAY='#526676'
def short(r):return f"{int(r['p']).bit_length()}b / {r['ordinal']}"
def svg_graph():
    z=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650"><rect width="900" height="650" fill="white"/>',f'<g font-family="Arial" fill="{NAVY}"><text x="20" y="27" font-size="21">All checked parameter fibers are regular</text><text x="20" y="50" font-size="14">Bar length: number of source / Fricke-target / Atkin fibers checked per curve</text>']
    for i,r in enumerate(ROWS):
        y=72+24*i;n=int(r['fiber_checks']);color=BLUE if r['label']=='published' else TEAL
        z.append(f'<text x="20" y="{y+13}" font-size="14">{short(r)}</text><rect x="145" y="{y}" width="{4*n}" height="16" fill="{color}"/><text x="{155+4*n}" y="{y+13}" font-size="13">{n}; exceptions 0</text>')
    z.append(f'<rect x="20" y="598" width="15" height="12" fill="{BLUE}"/><text x="42" y="610" font-size="14">Published (10)</text><rect x="230" y="598" width="15" height="12" fill="{TEAL}"/><text x="252" y="610" font-size="14">Reconstructed omissions (11)</text>')
    z.append('<text x="20" y="637" font-size="12">CANONICAL-ATKIN-ALL-FIBERS-01; n=21 identities, 61 levels, 2071 fibers. Exact counts; no error bars.</text></g></svg>')
    return ''.join(z)
DIAGRAM={'nodes':[{'id':'input','text':'21 immutable curve identities / six streams'},{'id':'table','text':'61 canonical/Atkin source equations, levels3..293'},{'id':'first','text':'1281 coordinate specializations; both derivative gcds constant'},{'id':'fiber','text':'1185 rational parameters; 2071 fibers; zero checked exceptions'},{'id':'ccr','text':'CCR literal printed coefficients fail all21 at degree13'},{'id':'unknown','text':'Historical selector unresolved; original caller and configuration missing'}],'edges':[['input','first'],['table','first'],['first','fiber'],['input','ccr'],['fiber','unknown'],['ccr','unknown']],'historical_use':'unestablished','isogeny_map_claim':False}
def svg_workflow():
    z=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260" viewBox="0 0 900 260"><rect width="900" height="260" fill="white"/>',f'<g font-family="Arial" fill="{NAVY}" font-size="16">']
    for x,y,w,title,sub in [(15,25,260,'21 identities / six streams','10 published; 11 omitted'),(315,25,270,'61 source equations','1281 coordinate cases'),(625,25,260,'2071 parameter fibers','All checked exceptions absent'),(315,160,270,'CCR literal-formula audit','Fails all21 at degree13'),(625,160,260,'Historical selector unresolved','Original caller not established')]:
        z.append(f'<rect x="{x}" y="{y}" width="{w}" height="65" rx="7" fill="#eaf1f6"/><text x="{x+12}" y="{y+26}">{title}</text><text x="{x+12}" y="{y+49}" font-size="13">{sub}</text>')
    z.append(f'<path d="M275 55 H315 M585 55 H625 M145 90 V192 H315 M585 192 H625 M755 90 V160" stroke="{GRAY}" stroke-width="2" fill="none"/><text x="15" y="245" font-size="12">Edges describe evidence flow. They do not assert an isogeny map or historical program use.</text></g></svg>')
    return ''.join(z)
class Bars(Flowable):
    def __init__(self):super().__init__();self.width=490;self.height=342
    def draw(self):
        c=self.canv;c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica-Bold',10);c.drawString(0,327,'Recorded fibers checked per curve; every checked exception count is zero')
        for i,r in enumerate(ROWS):
            y=307-i*13;n=int(r['fiber_checks']);c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica',7.2);c.drawString(0,y,short(r));c.setFillColor(colors.HexColor(BLUE if r['label']=='published' else TEAL));c.rect(80,y-1,2.65*n,8,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(87+2.65*n,y,str(n))
        c.setFillColor(colors.HexColor(BLUE));c.rect(0,25,9,7,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(14,25,'published (10)');c.setFillColor(colors.HexColor(TEAL));c.rect(120,25,9,7,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.drawString(134,25,'reconstructed omissions (11)')
        c.setFont('Helvetica',7);c.drawString(0,10,'CANONICAL-ATKIN-ALL-FIBERS-01. Unit: fibers; n=21 curves, 61 levels. Exact counts; no error bars.')
class Workflow(Flowable):
    def __init__(self):super().__init__();self.width=490;self.height=122
    def draw(self):
        c=self.canv
        for x,y,w,title,sub in [(0,72,145,'21 immutable identities','10 published; 11 omitted'),(169,72,145,'1281 coordinate cases','61 source equations'),(338,72,150,'2071 parameter fibers','Zero checked exceptions'),(169,0,145,'Literal CCR formulas','Fail all 21 at degree 13'),(338,0,150,'Selector unresolved','Original caller missing')]:
            c.setFillColor(colors.HexColor('#eaf1f6'));c.roundRect(x,y,w,42,4,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica-Bold',7.5);c.drawString(x+7,y+26,title);c.setFont('Helvetica',7);c.drawString(x+7,y+12,sub)
        c.setStrokeColor(colors.HexColor(GRAY));c.line(145,93,168,93);c.line(314,93,337,93);c.line(72,72,72,21);c.line(72,21,168,21);c.line(314,21,337,21);c.line(413,72,413,43)
REPORT=f'''# Canonical/Atkin coordinate guards and the CCR printed-formula correction

2026-10-27. T-5518. Observation report; no formal hypothesis decision. The historical selector remains unknown. All 11 reconstructed omissions and all ten publications pass the bounded modular-coordinate predicates tested here, across all six streams. A newly recovered draft contains a real printed-formula discrepancy, but using those coefficients literally fails every cohort curve at degree13 and therefore does not preserve the publications.

## Fixed identities and scope

The source cohort SHA-256 is `{B['source_cohort_sha256']}`. [comparison.csv](comparison.csv) lists all21 full curve UIDs, fields, coefficients, orders, seeds and ordinals. The model is y^2=x^3-3x+b; b is reconstructed with c*b^2=-27 mod p. P-224's two signs are one isomorphism class and appear once. The 192-bit published ordinals5228 and6013 retain their distinct v3/v2 identities. No post-endpoint or broader69-position additions enter the cohort. These are reconstructed omissions, not documented historical rejection events.

## Canonical and Atkin equations

Morain's1995 paper, sections3.2.1-3.2.2, gives field-dependent canonical and Atkin modular-coordinate paths. The available later LiDIA tables supply61 odd-prime levels3..293:46 canonical and15 Atkin. Their lineage is fixed at commit23dac491f4cd96eb7de648a5cf90eb9ec77653c8; this is not authenticated1997 source. Each table is parsed as integer tokens, as the real reader does, retaining unconsumed opaque trailers. A native C++ control binds every coefficient at p=1009,j=34 for all61 tables to the unmodified public meq_prime reader. This control does not call the inherited eigenvalue compatibility amendment in the earlier SEA build.

Native PARI computes the full polynomial gcds of F(X,j) with each partial derivative, plus F(0,j). Independent Python specializes the raw source tables, recomputes derivatives and checks2568 exact Bezout identities including controls. All1281 cohort cells have nonzero F(0,j) and constant derivative gcds. Thus no algebraic parameter root, including any rational one, hits either tested first-stage derivative locus.

The extension follows every rational parameter root, proved complete independently using FLINT gcd(F,X^p-X). Canonical parameters generate both source and Fricke-target fibers, with target parameter ell^s/alpha and s=12/gcd(12,ell-1); Atkin parameters generate invariant fibers. For every fiber G(Y), exact certificates check gcd(G,G_Y), gcd(G,G_X), G(0) and G(1728). All1185 rational parameters and2071 resulting cohort fibers have zero checked exceptions. Source-mode extra j roots are contextual, not claims that the caller traverses them.

![Recorded fibers](curve-fibers.svg)

Constructed ordinary positive controls are independently point-counted: p1009,j779 has trace58 and a level17 derivative exception; p1009,j24 has trace-47 and both level53 exceptions. The fiber audit retains five control fibers, including three exceptional ones. The level17 X-exception search found none in the frozen j scan and records that absence rather than manufacturing a control. The real exceptions demonstrate that the tests can detect their stated condition.

## Recovered CCR draft and source-based test

Three author-hosted retrievals return the same24-page draft, SHA-256919f089a7c5de6ca3d23050151d44995c9352572b7d675671fbdc5ccb8f54d39. Morain1995 cites CCR as1991; Schoof1995 cites it as1992. The recovered scan's metadata dates its scanning to2018, so the exact draft version is not established. All24 pages were OCRed; the formulas on pages8-9 and Morain printed275 were visually compared. No historical executable attribution is inferred.

Let p_k=sum x(iP)^k for i=1..(ell-1)/2, and p_0=(ell-1)/2. The literal draft coefficients are Anew=A+5*(p2+A*p0) and Bnew=B+7*(5*p3+3*A*p1+2*B*p0). Its own equations4.4,4.7 and5.1 instead give Anew=A-10*(3*p2+A*p0) and Bnew=B-14*(5*p3+3*A*p1+2*B*p0). Morain's footnote explicitly identifies the correction. The power-sum normalization is the same in both documents.

CCR-LITERAL-COEFFICIENTS-01 freezes degree13, all21 inputs and one constructed ordinary p101,A2,B3 control before running. Native PARI evaluates x(kP), k1..6, in the full degree84 division-polynomial algebra. Independent integer arithmetic reconstructs psi13 and verifies132 multiple-coordinate relations,44 corrected identities, and exact common-zero certificates for the two literal coefficient residuals. The common-zero gcd has degree0 for every curve and the control. Derived coverage: all14 cyclic degree13 subgroups per curve over the algebraic closure,294 across the21 cohort curves; no individual subgroup enumeration or full point count is claimed.

The literal formula fails for all11 omissions and all10 publications. A universal use-and-reject rule based on it cannot reproduce the publications. This does not test a caller that conditionally enters the faulty code, alternative degrees, root-pair selection, later recurrence errors or a different implementation.

![Evidence flow](workflow.svg)

## Integrity, failures and limitations

The raw archive seals{B['sealed_files']} files and is{B['archive_bytes']:,} bytes, SHA-256`{B['archive_sha256']}`. It retains native stdout/stderr, frozen inputs, protocols, source-table bytes, GPL notice, source-reader control and failures. Three zero-run preparation mistakes concerned physical rows, opaque trailers and line wrapping. Two earlier verifier attempts assumed monic Bezout gcds and suffixed filename traces; the actual source/outputs require unit-scaled gcds and paths printed before appending_II. The amendment preserves those failures and changes no native output. A later amendment strengthens exact UID/cohort binding. Packaging initially joined a derived CSV on a nonexistent index; the corrected join uses full curve_uid without changing the sealed archive or rerunning a producer.

The native coordinate run completed in7.8944s, table-reader control in0.7459s, fiber run in358.2656s and literal CCR run in0.2349s. These are measured diagnostic wall times under uncontrolled load on modern macOS ARM64, not historical runtimes, comparisons or performance claims. Native stdout sizes are78,772,631 and21,045,312 bytes for the coordinate/fiber studies. No source-based mathematical rejection is inferred from an operational failure.

Local LMFDB manifests were checked complete first. The bounded genus1,q1009 query returned zero rows; no catalog identity was used. The av_fq extraction ended2026-10-19T16:45:49.243703+00:00 from postgresql://devmirror.lmfdb.xyz:5432/lmfdb/public.av_fq_isog. Cryptographic fields lie outside that selected index. Controls were independently enumerated over their exact fields.

This is not a full SEA replay through level293: kernel recovery, eigenvalue finding, CRT/stopping/resource policies and original candidate visitation are not established. Neither these guards nor the literal coefficient error supplies a selector, alone or in their directly tested combination. The original generator/caller/configuration and a predictive historical rule remain missing. Existing ECPP, all-root SEA and FreeLIP figures retain their prior sealed scopes; this round adds separate figures and changes no formal decision or canonical frontier claim.

## Replay and sources

Extract evidence.tar.zst, then run `python3 -B evidence/verify.py`. Add `--fibers` under Python with python-flint0.9.0 for independent rational-root completeness. The ordinary replay uses the standard library; the full root audit uses FLINT in process. Neither invokes the external PARI/C++ producers or network. FLINT wheel digest and official URL are retained in FLINT-RUNTIME.json. The public export deliberately excludes publisher PDFs, scanner images, duplicate normalized GP tables, binaries, the venv and wheel; SOURCE-BOUNDARY.json describes reconstruction and custody.

Primary sources: [Morain1995](https://jtnb.centre-mersenne.org/item/10.5802/jtnb.143.pdf), [CCR draft in the author's archive](https://www.lix.polytechnique.fr/Labo/Francois.Morain/Introuvables/Drafts/ccr.pdf), [LiDIA source](https://github.com/mkoeppe/LiDIA/tree/23dac491f4cd96eb7de648a5cf90eb9ec77653c8). Exact acquisition receipts and source hashes are retained. Object-store publication returned a guarded HeadObject403; no remote upload is verified. The existing large-file-ok PR exception retains the bytes in Git. This does not resolve store permissions or inherited PR merge collisions.
'''
def readable(s):
    words='same|as|is|the|Pages|all|All|degree|level|levels|through|of|for|and|to|has|from|at|over|neither|nor|including|printed|page|pages|equations|metadata|Morain|Schoof|cases|commit|counted|ended|default|trace|contains|correction|curve|formula|coordinate|reader|fibers|tables'
    s=re.sub(r'\b('+words+r')(?=\d)',r'\1 ',s)
    s=re.sub(r'</b>(?=\d)','</b> ',s)
    s=re.sub(r',(?=\d)',', ',s)
    return s.replace('p101,A2,B3','p=101, A=2, B=3').replace('p1009,j779','p=1009, j=779').replace('p1009,j24','p=1009, j=24').replace('F1009','F_1009').replace('F101','F_101').replace('genus1,q1009','genus 1, q=1009').replace('degree0','degree 0').replace('python-flint0.9.0','python-flint 0.9.0')
def build_pdf():
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=7,textColor=colors.HexColor(NAVY)));styles.add(ParagraphStyle(name='Small',fontSize=7.5,leading=10,spaceAfter=5));body=styles['BodySmall'];story=[]
    def p(s):story.append(Paragraph(readable(s),body))
    def h(s):story.append(Paragraph(s,styles['Heading2']))
    story.append(Paragraph('Modular-coordinate guards and a corrected early formula',styles['Title']))
    p('2026-10-27 | T-5518 | Observation report; no formal hypothesis decision.')
    p('<b>The historical selector remains unknown.</b> All11 reconstructed omissions and all10 publications pass the tested coordinate/fiber guards. Literal use of a recovered draft error fails every curve, including all publications.')
    h('1. Fixed cohort, expanded coordinate coverage')
    p('21 immutable curve identities; six recovered streams. Available later LiDIA source tables:61 odd-prime levels3 through293,46 canonical and15 Atkin. The source is not authenticated1997 code. Full identities and field/model/order/seed data are in comparison.csv.')
    p('<b>Independently verified:</b>1281 first-stage cells,2568 Bezout identities including controls; every cohort derivative gcd is constant and every F(0,j) is nonzero. FLINT independently proves completeness of1185 rational parameters. All2071 source/Fricke-target/Atkin fibers have constant checked derivative gcds and contain neither j0 nor j1728.')
    story.append(Bars())
    p('Two constructed ordinary curves over F1009 produce three first-stage exceptional guards and three exceptional fibers among five tested control fibers. Source-reader controls bind all61 tables. The negative cohort result is therefore accompanied by actual detectable exceptions.')
    story.append(PageBreak())
    story.append(Paragraph('2. The CCR coefficient correction, tested on all 21 curves',styles['Heading1']))
    p('Three author-hosted URLs supplied the same24-page Charlap-Coley-Robbins draft. Morain1995, printed page275, explicitly corrects its formulas. The recovered scan version is uncertain: papers cite the draft as1991/1992, while scan metadata is2018. Pages8-9 and the correction were visually compared after OCR.')
    p('Both texts define p_k as the sum over one representative from each pair of nonzero kernel points: p_k=sum x(iP)^k, i=1..(ell-1)/2. Thus p_0=(ell-1)/2. This convention is aligned before testing.')
    data=[['Coefficient','Literal draft, page9','Derived / Morain correction'],['Anew-A','5*(p2+A*p0)','-10*(3*p2+A*p0)'],['Bnew-B','7*(5*p3+3*A*p1+2*B*p0)','-14*(5*p3+3*A*p1+2*B*p0)']]
    table=Table([[Paragraph(html.escape(str(v)),styles['Small']) for v in row] for row in data],colWidths=[66,196,228]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf1f6')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),.3,colors.lightgrey)]));story.append(table);story.append(Spacer(1,10))
    p('The corrected coefficients follow directly from the same draft\'s equations4.4,4.7 and5.1. Frozen CCR-LITERAL-COEFFICIENTS-01 evaluates degree13 on all21 curves and one constructed ordinary F101 control.')
    p('<b>Measured / independently verified:</b>22 full degree84 division-polynomial algebras;132 multiple-coordinate relations;44 corrected k1/k2 identities; exact Bezout common-zero certificates for both literal residuals. Every common-zero gcd has degree0.')
    p('<b>Derived coverage:</b> every one of the14 cyclic degree13 subgroups over the algebraic closure per curve,294 for the cohort. This follows from the full division-polynomial certificate; individual subgroup enumeration and full point counts were not performed.')
    p('<b>Observed label result:</b> the literal formula is inconsistent for11/11 omissions and10/10 publications. A universal rejection rule based on it cannot preserve the published set. A conditional caller, different degree, root-pair policy or other implementation remains outside this test.')
    story.append(Workflow())
    p('Evidence-flow diagram only; its arrows assert no isogeny map or historical program use.')
    story.append(PageBreak())
    story.append(Paragraph('3. Custody, replay and remaining scope',styles['Heading1']))
    p(f'Raw archive: {B["sealed_files"]} sealed files; {B["archive_bytes"]:,} bytes. Protocols, all inputs, native outputs, source-table bytes and the GPL notice, controls and failed attempts are retained.')
    p('Archive SHA-256:<br/>'+B['archive_sha256'])
    p('The exact cohort digest and full UID/model/order/seed rows are retained in BUNDLE.json and comparison.csv.')
    h('Retained failures and amendments')
    p('Three preparation attempts misread table framing and stopped before native curve calls. Earlier verifier attempts assumed monic gcds and suffixed trace paths; exact output and source semantics required unit-scaled gcds and pre-suffix paths. Those attempts are preserved. UID binding was strengthened without changing outputs. One derived CSV join was repaired using curve_uid; no native producer reran and the sealed archive did not change.')
    p('Native wall times are retained in report.md as diagnostic modern ARM64 observations under uncontrolled load. They are not historical timing or performance comparisons. Operational failure does not count as mathematical rejection.')
    h('Portable verification')
    p('After extracting evidence.tar.zst:<br/><font face="Courier">python3 -B evidence/verify.py</font><br/>For root completeness, use python-flint0.9.0 and add <font face="Courier">--fibers</font>. The first audit is standard-library only; the full fiber audit uses in-process FLINT. Neither launches an external producer or contacts the network.')
    p('Local LMFDB manifests were complete. The genus1,q1009 query returned no rows; controls were counted directly and no catalog crosswalk is claimed. The av_fq extraction ended2026-10-19T16:45:49.243703+00:00; cryptographic fields are outside the selected index.')
    h('Limits and next discriminating evidence')
    p('This study tests coordinate singularities and one literal printed error. It does not execute a complete level293 point counter, recover the original caller, or establish kernel/eigenvalue/CRT stopping policy and candidate visitation. The P-224 cube/splitting observation is still distinct from proof of historical use. A dated caller/configuration or an independently predictive rule is still required.')
    p('Object-store delivery was refused by the canonical HeadObject403 guard. Git delivery uses the existing documented large-file-ok exception. No remote store success or green merge gate is claimed. The PR has inherited immutable A/A-record collisions, recorded separately.')
    p('Primary sources: Morain1995, JTNB7,255-282, doi:10.5802/jtnb.143; CCR draft in the author archive; pinned LiDIA source. Full URLs, exact source digests and public-export exclusions are in report.md and SOURCE-BOUNDARY.json.')
    def footer(c,doc):
        c.setFont('Helvetica',7);c.setFillColor(colors.HexColor(GRAY));c.drawString(50,30,'T-5518 | CANONICAL-ATKIN-GUARDS-01 / ALL-FIBERS-01 | CCR-LITERAL-COEFFICIENTS-01');c.drawRightString(560,30,str(doc.page))
    doc=SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),rightMargin=60,leftMargin=50,topMargin=42,bottomMargin=44,title='NIST/ANSI modular-coordinate guards and CCR formula audit',author='Research observation record',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
def main():
    (P/'curve-fibers.svg').write_text(svg_graph());(P/'workflow.svg').write_text(svg_workflow());(P/'workflow.diagram.json').write_text(json.dumps(DIAGRAM,indent=2)+'\n');(P/'report.md').write_text(readable(REPORT));build_pdf()
if __name__=='__main__':main()
