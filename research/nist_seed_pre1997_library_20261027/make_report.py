"""Editable vector plots, diagram, Markdown and PDF from frozen observations."""
import csv,json,html
from pathlib import Path
from reportlab import rl_config
rl_config.useA85=0
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
HERE=Path(__file__).resolve().parent
S=json.loads((HERE/'SUMMARY.json').read_text());B=json.loads((HERE/'BUNDLE.json').read_text())
assert (S['curves'],S['omitted'],S['published'],S['native_inverse_checks'],S['independent_inverse_witnesses'])==(21,11,10,756,126)
NAVY='#15324d';BLUE='#287ca4';GREEN='#238576';GRAY='#536879'
labels=['Coefficient inverse','Coefficient square root','Order primality','All inversion modes','Independent inverse values']
def quantitative_svg():
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="345" viewBox="0 0 900 345">','<rect width="900" height="345" fill="white"/>',f'<g font-family="Arial" font-size="16" fill="{NAVY}">']
    parts.append('<text x="20" y="27" font-size="21">Every tested curve passed each applicable check</text>')
    for i,label in enumerate(labels):
        y=60+i*46;parts.append(f'<text x="20" y="{y+20}">{html.escape(label)}</text>')
        parts.append(f'<rect x="265" y="{y}" width="400" height="14" fill="{BLUE}"/><text x="680" y="{y+13}">published 10/10</text>')
        parts.append(f'<rect x="265" y="{y+17}" width="440" height="14" fill="{GREEN}"/><text x="720" y="{y+30}">omitted 11/11</text>')
    parts.append('<text x="265" y="310">Unit: unique curves passing; 21 fixed identities, six streams.</text>')
    parts.append('<text x="20" y="335" font-size="13">FREELIP-PRE1997-VALIDATION-02; WITNESS-AND-FAULT-CONTROL-01. Deterministic counts; no error bars.</text></g></svg>')
    return ''.join(parts)
workflow={'nodes':[
    {'id':'source','label':'1995 FreeLIP 1.0','detail':'two identical mirror payloads'},
    {'id':'cohort','label':'21 fixed curve identities','detail':'10 published + 11 reconstructed omissions'},
    {'id':'normal','label':'Native validation completed','detail':'both limb sizes; 756 inverse checks'},
    {'id':'witness','label':'Independent arithmetic replay','detail':'126 integer witnesses verified'},
    {'id':'asan','label':'Constructed fault control unavailable','detail':'sanitizer startup; no completed main call'},
    {'id':'history','label':'Historical selector still unknown','detail':'original generator and configuration absent'}],
    'edges':[['source','normal'],['cohort','normal'],['normal','witness'],['source','asan'],['witness','history']]}
def workflow_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300"><rect width="900" height="300" fill="white"/><g font-family="Arial" fill="{NAVY}" font-size="17">
    <path d="M270 65 H330 M270 145 H300 V85 H330 M590 85 H650 M460 110 V210 M650 105 V210" fill="none" stroke="{GRAY}" stroke-width="2"/>
    <rect x="15" y="30" width="255" height="65" rx="8" fill="#eaf1f6"/><text x="30" y="55">1995 FreeLIP 1.0</text><text x="30" y="78" font-size="13">Two matching mirror payloads</text>
    <rect x="15" y="115" width="255" height="65" rx="8" fill="#eaf1f6"/><text x="30" y="142">21 fixed curves / six streams</text><text x="30" y="165" font-size="13">10 published; 11 omitted</text>
    <rect x="330" y="40" width="260" height="70" rx="8" fill="#dff1eb"/><text x="345" y="66">Native validation completed</text><text x="345" y="91" font-size="13">756 inversion checks passed</text>
    <rect x="650" y="40" width="235" height="70" rx="8" fill="#dff1eb"/><text x="665" y="66">Independent replay</text><text x="665" y="91" font-size="13">126 actual inverse values</text>
    <rect x="305" y="210" width="290" height="65" rx="8" fill="#fff0d9"/><text x="320" y="235">Fault control unavailable</text><text x="320" y="258" font-size="13">ASan startup; pre-main censoring</text>
    <rect x="625" y="210" width="260" height="65" rx="8" fill="#eaf1f6"/><text x="640" y="235">Historical selector unknown</text><text x="640" y="258" font-size="13">Original generator not recovered</text></g></svg>'''
class Bars(Flowable):
    def __init__(self):
        super().__init__();self.width=490;self.height=190
    def draw(self):
        c=self.canv;c.setFont('Helvetica-Bold',11);c.setFillColor(colors.HexColor(NAVY));c.drawString(0,176,'Unique curves passing every applicable check')
        for i,label in enumerate(labels):
            y=146-i*28;c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica',8);c.drawString(0,y,label)
            c.setFillColor(colors.HexColor(BLUE));c.rect(145,y+1,200,7,fill=1,stroke=0)
            c.setFillColor(colors.HexColor(GREEN));c.rect(145,y-8,220,7,fill=1,stroke=0)
            c.setFont('Helvetica',7);c.setFillColor(colors.HexColor(NAVY));c.drawString(375,y+1,'published 10/10');c.drawString(375,y-8,'omitted 11/11')
        c.setFont('Helvetica',7);c.drawString(0,5,'Units: unique curves. n = 21 fixed identities, six streams; deterministic counts, no error bars.')
class Workflow(Flowable):
    def __init__(self):
        super().__init__();self.width=490;self.height=112
    def draw(self):
        c=self.canv
        for x,y,w,title,sub,fill in [(0,62,150,'1995 source + fixed cohort','21 curves; two limb widths','#eaf1f6'),(169,62,150,'Native validation','756 checks passed','#dff1eb'),(338,62,150,'Independent arithmetic','126 inverse witnesses','#dff1eb'),(169,0,150,'ASan control unavailable','Startup deadlock; pre-main','#fff0d9'),(338,0,150,'Selector unresolved','Original program absent','#eaf1f6')]:
            c.setFillColor(colors.HexColor(fill));c.roundRect(x,y,w,43,5,fill=1,stroke=0);c.setFillColor(colors.HexColor(NAVY));c.setFont('Helvetica-Bold',8);c.drawString(x+8,y+27,title);c.setFont('Helvetica',7);c.drawString(x+8,y+12,sub)
        c.setStrokeColor(colors.HexColor(GRAY));c.line(151,83,168,83);c.line(320,83,337,83);c.line(244,61,244,44);c.line(413,61,413,44)
REPORT='''# Pre-1997 FreeLIP validation on the fixed NIST/ANSI curve cohort

2026-10-27. T-5518. This is an observation report, not a formal hypothesis decision. The missing historical selector remains unresolved. Recovered FreeLIP 1.0 passes the tested validation operations on all 11 reconstructed omissions and all 10 publications, across all six streams. These are reconstructed omissions, not documented rejection events.

## What changed in the evidence

Two mirrors supplied the same 201,037-byte FreeLIP 1.0 archive. Its README is dated May 1, 1995 and both HTTP Last-Modified headers report April 30, 1996. The archive SHA-256 is `6ef1e0bb398eec0c6cbd22f51b06cbbbbd4d995673ae8da942de6f9d3a7ecec5`. Neither mirror establishes that Reiter used these exact bytes.

The previously tested FreeLIP 1.1 README is dated July 21, 1997. It reports a fixed extended-Euclidean defect that could cause incorrect answers, hangs or memory errors. Source comparison found changes in `zxxeucl`, prime iteration and other helpers, so top-level routine similarity was insufficient to reuse the earlier native result. The bodies of `zsqrtmod`, `zprobprime`, `zprime`, `zrandom`, `zrandomb` and `zrstarts` match after removing whitespace and comments. This is a scoped comparison, not whole-library equivalence.

## Executed observations

- FreeLIP 1.0, 26- and 30-bit limbs, four RNG seeds: all 21 orders pass `zprobprime(n,20)`. That is 168 unique parameterized calls and 336 calls including the predeclared A/A repeats. Both complete baseline runs match byte for byte in each configuration.
- All 21 coefficient inversions and square roots pass in both builds. Square roots use zero FreeLIP RNG calls; each 20-round primality test uses 20 calls. Both leave the separately seeded libc rand48 stream unchanged.
- At 26 bits, seven discarded draws reproduce all six May-1997 base-point x-coordinates. At 30 bits, none of those six x-coordinates matches. The 30-bit result is a configuration mismatch, not a mathematical rejection.
- Three inverse inputs per curve (`c`, nonzero `b`, and `27*b^2-108 mod p`), three output modes (distinct, in place, and pre-sized in place), two limb sizes, two versions: 756 of 756 native checks pass. Each of the 21 identities has 36 passing checks.
- 126 actual inverse integers returned by FreeLIP 1.0 match independent Python modular inversion: three inputs per curve in both limb sizes. Each identity has six independently checked integer witnesses.
- Ordinary controls pass: 68 prime/composite cases, four square-root controls, and 40 independently replayed RNG words across four build configurations.

![Recorded curve counts](curve-checks.svg)

## Preserved failures and limits

Attempt 01 stopped at the first compile because the archive omits its generated `lippar.h`. No curve ran. The source Makefile bootstraps that header as empty; the frozen attempt-02 amendment supplies it with all arithmetic choices explicit on the compiler command line.

The constructed ASan fault demonstration is unavailable. The first control timed out without producing probe output. A second control was sampled in dyld/libSystem/ASan initialization, recursively entering the sanitizer allocator and spinning in its initialization mutex, with no `main` frame. It was interrupted; its stdin remains, with missing terminal output/receipt explicitly recorded. The remaining ASan arms did not start. This is operational censoring, not evidence of a FreeLIP fault or curve rejection. All 126 value witnesses completed before that subrun.

All native arithmetic ran on modern macOS ARM64/LP64, with `SIZEOFLONG=8`, explicit 26/30-bit limbs and generic arithmetic. No original-CPU timing, original allocator behavior, or original generator is established. A read-only translation of quotient batching also passed 252 checks before the native run; it is supplementary and does not replace native evidence.

![Evidence flow](workflow.svg)

## Historical point-counter cross-check

The 1994 Lehmann-Maurer-Mueller-Shoup paper constructs eta-quotient modular equations with coefficients expressed directly in `j(E)` (page 5), so that presented path has no prerequisite that a cube root of `j` lie in the base field. It handles special j-values separately (page 4), checks both x and y in its Frobenius identity (page 6), and verifies full points after matching stored x-coordinate fingerprints (page 9). The paper describes an algorithm, not the missing generator. All 10 pages were inspected visually; OCR covered only pages 1-7.

The recovered 1995 MIRACL archive contains arithmetic/factoring software, not a recovered prime-field point counter. The available MIRACL Schoof/SEA source is dated 1999. The 1995/1996 elliptic packages inspected use characteristic two. LiDIA-history has empty GitHub and Software Heritage branch snapshots; no older implementation of the known later fixes was recovered. These are bounded searches, and network timeouts are not proof that a source never existed.

The P-224 cube/splitting pattern remains a specific field-dependent lead. This round supplies no source-based cube-root gate and no predicate that selects all publications while excluding all omissions. Another point counter, application-level selection or stopping logic, or an unrecorded criterion remains possible.

## Exact identities, custody and replay

`comparison.csv` and `SUMMARY.json` retain every full curve UID, seed stream, ordinal, field, order, c and b. The curve model is `y^2=x^3-3x+b` over `F_p`. The unchanged cohort digest is `93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545`. Published 192v2 is ordinal 6013; published 192v3 is 5228. P-224 coefficient signs identify one isomorphism class here.

The 190,218-byte evidence archive seals 3,688 files and retains 912 completed external-process receipts, including the initial compile failure and sanitizer timeout. `BUNDLE.json` binds the archive and manifest; `SOURCE.json` binds original source bytes and retrieval metadata; `SOURCE-COMPARISON.json` binds the scoped function comparisons. Library binaries and original licensed source are retained locally and are not redistributed in this derived-evidence archive.

Extract `evidence.tar.zst`, run `python3 -B evidence/verify.py`, then `python3 -B audit_bindings.py evidence`. Both passed after relocation. The first checks custody, curve identities, arithmetic witnesses, ordinary controls and recorded failures; the second binds all 756 inversion rows, four baseline captures and 126 witnesses to their exact raw stdin/stdout/process receipts. Neither command launches the historical/native libraries or needs network access.

Graphs checked: the earlier SEA root-count and workflow plots and ECPP report remain descriptions of their own sealed runs. Their observations did not change; this round adds separate library-validation plots. No official hypothesis status is changed.

Sources: [FreeLIP 1.0 FUNET mirror](https://ftp.funet.fi/pub/crypt/math/freelip_1.0.tar.gz), [matching GWDG mirror](https://ftp.gwdg.de/pub/misc/crypt/math/freelip_1.0.tar.gz), [FreeLIP 1.1 source mirror](https://github.com/lrobot/freelip), [LMMS 1994 paper](https://www.shoup.net/papers/counting.pdf). Exact dated retrieval receipts remain in local source custody and the exported metadata.
'''
def build():
    (HERE/'report.md').write_text(REPORT)
    (HERE/'curve-checks.svg').write_text(quantitative_svg())
    (HERE/'workflow.svg').write_text(workflow_svg())
    (HERE/'workflow.diagram.json').write_text(json.dumps(workflow,indent=2)+'\n')
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyStudy',fontName='Helvetica',fontSize=9,leading=13,spaceAfter=8,textColor=colors.HexColor(NAVY)))
    styles.add(ParagraphStyle(name='SmallStudy',fontName='Helvetica',fontSize=7,leading=10,spaceAfter=6,textColor=colors.HexColor(GRAY)))
    story=[]
    def para(s,style='BodyStudy'):story.append(Paragraph(s,styles[style]))
    def heading(s):story.append(Paragraph(s,styles['Heading2']))
    para('Pre-1997 FreeLIP validation', 'Title');para('Fixed NIST/ANSI cohort | 27 October 2026 | T-5518','SmallStudy')
    para('<b>The missing historical selector remains unresolved.</b> This observation report records a recovered older library and completed tests. Every tested validation operation passed on all 11 reconstructed omissions and all 10 publications, across all six streams. No formal hypothesis status changes here.')
    heading('A dated source gap is now smaller')
    para('Two mirrors supplied the same FreeLIP 1.0 archive: 201,037 bytes, README dated May 1, 1995, HTTP modification date April 30, 1996. The previously tested 1.1 README is dated July 21, 1997 and describes a fixed extended-Euclidean bug that could produce wrong answers, hangs or memory errors. The recovered source is not authenticated as Reiter\'s generator.')
    heading('Recorded observations')
    table=[['Configuration','Inverse / alias checks','May base points'],['FreeLIP 1.0 / 26 bits','189 / 189 pass','6 / 6 match'],['FreeLIP 1.0 / 30 bits','189 / 189 pass','0 / 6 match'],['FreeLIP 1.1 / 26 bits','189 / 189 pass','not rerun'],['FreeLIP 1.1 / 30 bits','189 / 189 pass','not rerun']]
    t=Table(table,colWidths=[175,160,150]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(NAVY)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf3f6'),colors.white])]))
    story.append(t);story.append(Spacer(1,10))
    para('FreeLIP 1.0 coefficient inversion, square root and four-seed order-primality checks pass on all 21 curves in both limb sizes. The A/A repeats match byte for byte. There are 168 distinct primality parameter combinations, 336 calls including repeats. Independent Python arithmetic verifies 126 returned inverse integers.')
    story.append(Bars());para('Figure 1. Recorded unique-curve outcomes. FREELIP-PRE1997-VALIDATION-02 and WITNESS-AND-FAULT-CONTROL-01. Full identities and exact arithmetic inputs are in comparison.csv.','SmallStudy')
    story.append(PageBreak())
    para('Methods, controls and preserved failures','Title')
    heading('What actually ran')
    para('Each curve contributes three inverse inputs: c, nonzero b, and the j-denominator (27 b squared - 108) mod p. Each is tested with distinct output, aliased output, and pre-sized aliased output, in both limb sizes and both source versions: 21 x 3 x 3 x 2 x 2 = 756 calls. All pass. The 126 independent integer witnesses cover FreeLIP 1.0, three inputs, and both limb sizes.')
    para('Ordinary controls pass in all four builds: 68 prime/composite cases, four square-root controls and 40 independently replayed RNG words. In 1.0, coefficient square roots consume zero FreeLIP random calls, and each 20-round primality call consumes 20. Both preserve the separate libc rand48 stream. Seven discarded 26-bit draws reproduce all six May base-point x-coordinates. The 30-bit mismatch identifies a configuration difference.')
    heading('The constructed memory-fault demonstration is unavailable')
    para('Attempt 01 stopped at its first compile because the archive expects a generated lippar.h. No curve ran. The source Makefile creates an empty bootstrap header; the frozen attempt-02 amendment supplies it, with arithmetic options explicit on the compiler command line.')
    para('The first ASan control timed out without producing probe output. A second was sampled in loader / libSystem / sanitizer initialization, recursively entering its allocator and spinning in an initialization mutex, with no main frame. It was interrupted; its stdin and missing terminal capture are recorded. Remaining ASan arms did not start. This is pre-main operational censoring, not a demonstrated FreeLIP bug or a curve rejection. All 126 independent witnesses had already completed.')
    story.append(Workflow());story.append(Spacer(1,8))
    para('Figure 2. Completed validation and independent replay are separate from the unavailable constructed fault control and unresolved historical attribution. Editable diagram data and SVG accompany this report.','SmallStudy')
    heading('Scope of the source comparison')
    para('Top-level square-root, primality and RNG routine bodies match after whitespace/comment removal. Extended Euclid, prime iteration and other helper differences required native testing. Both tested C versions use modern macOS ARM64/LP64, SIZEOFLONG=8, explicit 26/30-bit limbs and generic arithmetic. These observations do not establish original-CPU behavior, allocator behavior, original timing or an application-level selector.')
    para('Frozen native protocol: '+S['protocol_sha256'],'SmallStudy')
    story.append(PageBreak())
    para('Historical implications and replay','Title')
    heading('No recovered cube-root gate')
    para('The 1994 Lehmann-Maurer-Mueller-Shoup paper constructs eta-quotient modular equations directly from j(E) (page 5). Its presented path does not require a cube root of j in the base field. Special j-values have separate handling (page 4); Frobenius checks include x and y (page 6); fingerprint matches are followed by full-point comparison (page 9). All ten pages were read visually; OCR covers pages 1-7 only.')
    para('The recovered 1995 MIRACL package contains arithmetic/factoring software; the available prime-field Schoof/SEA source dates from 1999. The 1995/1996 elliptic packages inspected concern characteristic two. LiDIA-history and its preserved Software Heritage snapshots have empty branch maps. No older implementation of the later LiDIA fixes was recovered. These were bounded searches; access timeouts do not prove historical source absence.')
    para('<b>The P-224 cube/splitting pattern remains a specific field-dependent lead.</b> This round provides no source-based cube-root gate and no selector that rejects the eleven omissions while retaining all publications. Another point counter, application stopping logic, or an unrecorded criterion remains possible.')
    heading('Exact identity and custody')
    para('Fixed cohort: 21 identities, ten publications, eleven reconstructed omissions, six streams. Full UIDs, field p, order n, c, b, timestamps and ordinals are retained in comparison.csv and SUMMARY.json. The model is y squared = x cubed - 3x + b. Published 192v2 is ordinal 6013 and 192v3 is 5228; P-224 coefficient signs represent one class in this study.')
    para('Cohort SHA-256: '+B['source_cohort_sha256'],'SmallStudy')
    para('Archive: 190,218 bytes; 3,688 sealed files; 912 completed external-process receipts, including the compile failure and sanitizer timeout. Original library source and binaries remain in local custody; the public derived bundle contains probes, inputs, metadata, raw observations and portable auditors.')
    para('Archive SHA-256: '+B['archive_sha256'],'SmallStudy')
    heading('Portable verification')
    para('Extract evidence.tar.zst. Run <font face="Courier">python3 -B evidence/verify.py</font>, then <font face="Courier">python3 -B audit_bindings.py evidence</font>. Both passed after relocation. The first checks the sealed files, exact cohort, ordinary controls, arithmetic witnesses and recorded unavailable control. The second binds all summary rows to raw stdin, stdout and process receipts. Neither launches native libraries or accesses the network.')
    para('Earlier SEA and ECPP graphs retain their original sealed-run scope; their observations did not change. This round supplies separate library plots. Further historical attribution still requires the original generator, a dated relevant point counter, or a documented acceptance condition that survives the full cohort comparison.')
    para('Primary sources: ftp.funet.fi/pub/crypt/math/freelip_1.0.tar.gz; matching ftp.gwdg.de/pub/misc/crypt/math/freelip_1.0.tar.gz; github.com/lrobot/freelip (1.1); www.shoup.net/papers/counting.pdf (1994). Exact URLs and retrieval/source digests are in SOURCE.json and SEARCH-SOURCES.json.','SmallStudy')
    def page(c,doc):
        c.setFont('Helvetica',7);c.setFillColor(colors.HexColor(GRAY));c.drawString(50,29,'FREELIP-PRE1997-VALIDATION-02 | Observation report | Historical selector unresolved');c.drawRightString(562,29,str(doc.page))
    SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=(612,792),leftMargin=50,rightMargin=50,topMargin=40,bottomMargin=48,invariant=1,pageCompression=1).build(story,onFirstPage=page,onLaterPages=page)
    print('created report.pdf, report.md and editable vector figures')
if __name__=='__main__':build()
