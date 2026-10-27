from pathlib import Path
import collections, csv, html, json
from reportlab.lib import colors
from reportlab import rl_config
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable

HERE=Path(__file__).resolve().parent
rl_config.useA85=0
rl_config.invariant=1
rows=list(csv.DictReader((HERE/'comparison.csv').open()))
audit_path=HERE/'AUDIT.json'
if not audit_path.exists():audit_path=HERE/'attempt-02/AUDIT.json'
audit=json.loads(audit_path.read_text())
assert audit['status']=='PASS' and len(rows)==21
groups=collections.defaultdict(list)
for r in rows:groups[int(r['bits'])].append(r)
pattern_rows=[]
for bits in [192,224,239,256]:
    key={192:'roots_5',224:'roots_3',239:'roots_13',256:'roots_5'}[bits]
    pub=sorted({int(r[key]) for r in groups[bits] if r['label']=='published'})
    omit=sorted({int(r[key]) for r in groups[bits] if r['label']=='omitted'})
    assert set(pub).isdisjoint(omit)
    pattern_rows.append((bits,key,pub,omit))

lines=['# All-root SEA branch audit of the fixed NIST/ANSI cohort','',
'2026-10-27. Descriptive execution and independent arithmetic observations. Historical selection remains unresolved.','',
'## Exact question and cohort','',
'Could choosing a different rational root of a modular equation lead to an exceptional invariant or failed eigenvalue calculation, explaining any of the reconstructed omissions? This audit follows every rational root at levels 3, 5 and 13 in the available LiDIA build, rather than repeating its full point counts. The cohort contains exactly 21 curves: 11 reconstructed omissions and 10 publications across all six recovered streams. The source program is not authenticated as the original generator.','',
'Exact field, a=-3 model, b, order, seed, stream timestamp, ordinal and full curve UID are retained in evidence/attempt-02/{PROTOCOL.json,cohort-inputs.json,traits.json}. comparison.csv retains every full curve UID. The cohort-input SHA-256 is 93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545. No post-endpoint candidates were added.','',
'## Measured execution and independently verified arithmetic','',
'The successful attempt completed all 63 curve/level specializations. It emitted 39 rational modular roots and completed 78 kernel/profile checks (one direct Y-coordinate profile and one pre-Dewaghe ambiguous X-coordinate profile per root); 35 specializations used the Atkin branch. All 78 quotient/root Fricke checks passed. No actual cohort specialization failed, aborted or timed out. These are counts of this observer workload, not full point counts or performance estimates.','',
'The observer receives only p, a, b and the auxiliary prime. It receives no subgroup order, known trace, seed ordinal or publication label. Only private/protected access labels are exposed in a local observer header; the linked static library is unchanged. The independent Python replay reconstructs every specialized modular polynomial from frozen coefficients, verifies squarefreeness and the complete root set using gcd(F,X^p-X), checks every kernel against an independent division-polynomial recurrence, checks the Velu quotient and its F_p isomorphism type, ties the selected root to the quotient using the Fricke involution, and checks each resulting trace relation against the certified input order. Distinct modular roots must have distinct kernels.','',
'## Controls and retained failures','',
'The first attempt invoked nine controls and stopped because the modular-table directory was absent from its minimal environment. All nine returned TABLE_UNAVAILABLE; zero cohort specializations ran in that attempt. The second attempt supplied the source-supported LIDIA_ECO path to the same frozen local tables, then ran nine controls before the 63 named cases. All three generic controls completed. Constructed j=0 controls at levels 3 and 13 reached the explicit tildeEf E4_tau division-by-zero guard; the j=1728 level-13 control reached an undefined-inverse error. Those three controls terminated with SIGABRT and are preserved as source exceptions, not mathematical rejections. The other three exceptional-invariant controls completed. Total native observer invocations: 81 = 9 + 9 + 63.','',
'Independent controls include brute-force point counts over F_1000003, an explicit order-3 kernel on y^2=x^3+1 over F_101 with its Velu quotient, a nonkernel negative control, and polynomial division controls. Local LMFDB manifests were consulted: the complete av_fq index (source public.av_fq_isog, extraction ended 2026-10-19T16:45:49.243703+00:00) has genus-1 coverage only through q=1024. It contains neither these large prime fields nor the constructed q=1000003 control. No catalog identity claim is made.','',
'The initial compile ambiguity and both offline auditor versions are retained. The stronger auditor adds modular-table reconstruction, quotient/root binding and distinct-kernel checks to the first passing auditor; it does not change or repeat any native capture.','',
'## Observed splitting patterns','',
'These are post hoc descriptions of this fixed sample, not predeclared predictive tests or historical rules. Rational root counts are exact deterministic values for the frozen models and tables; no sampling uncertainty or p-value is assigned.','',
'| Field bits | Level | Published root counts | Omitted root counts |',
'| --- | --- | --- | --- |']
for b,k,p,o in pattern_rows:lines.append(f'| {b} | {k.removeprefix("roots_")} | {p} | {o} |')
lines += ['',
'P-224 therefore retains its specific four-roots-versus-one-root lead. P-192 and P-256 retain a level-5 root-versus-no-root lead, and P-239 retains a level-13 no-root-versus-root lead. These descriptions require different field-dependent choices. A predicate in just the three root counts cannot classify the whole cohort: omitted P-192 ordinal 2198 and published P-239 ordinal 2185/P-384 ordinal 2688 all have (0,0,0). Field-dependent rules remain possible, but this source takes all of these branches successfully and does not implement those descriptions as rejection gates.','',
'## Source dating and inference boundary','',
'Measured source: passagemath/upstream-LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8; version string 2.3.0+latte-patches-2019-05-02. The full fetched Git history starts with a 2013 import of release 2.3.0. The initial-import NEWS says the point-counting package was integrated in 2.1pre2. The retained ChangeLog dates documentation of the newly inserted package to 2001-06-05. It records a splitting-degree fix and an occasional-crash comparison typo on 2001-09-15, and a schoofpart failure fix on 2004-03-15. These messages do not identify the old faulty lines, date creation of standalone ECO, or demonstrate generator use. No speculative reversal of a comparison has been presented as recovered code.','',
'For this precise build and these levels, every rational-root branch produced independently valid arithmetic for both profiles. Consequently these captures provide no omission-specific failure mechanism. They leave earlier implementations, other levels, optimizer settings and an external caller policy untested. They do not turn all later point counters into reconstructions of a 1997 program. The original selection criterion is not identified.','',
'The next source-dependent test is to recover a dated pre-fix or standalone point counter, identify the exact corrected path, freeze its prediction without label-dependent changes, and check all 21 inputs. Arbitrary field-specific Boolean fits cannot establish that history.','',
'## Evidence and reproduction','',
'The raw evidence archive includes every native capture, source/table/static-library bindings, both frozen protocols, failures, controls, observer and independent arithmetic replay. Extract evidence.tar.zst, then run `python3 -B evidence/verify.py`. The replay verifies 489 sealed files and repeats only pure Python arithmetic, launching zero native point-counting programs. The exact source/static-library build is retained for provenance; this is a portable arithmetic replay, not a claim of a portable historical build.','',
'PROTOCOL SHA-256: b80560225b69b2cbb8370f01e26946164ef03b3d30055b31e50605a3566834ab. Seal SHA-256: eee2ca89c74ec4ca9fe5dc57ac5d46821c754900f48c3b0ca35e04a2bde52b44. Archive bytes/hash are in BUNDLE.json. Canonical graphs were checked by scope: this audit records no official hypothesis decision and changes no previously established map, conductor or transfer claim, so none was revised.','',
'Primary sources:','',
'- https://github.com/passagemath/upstream-LiDIA/tree/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/ec_order','- https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/ChangeLog','- https://github.com/passagemath/upstream-LiDIA/blob/0171e66/NEWS','- Historical question: https://words.filippo.io/seeds-solved/','',
'The old Darmstadt distribution URL and Wayback index requests were inaccessible through the web reader in this search. A failed retrieval is not proof that a release or archive does not exist. The Coster/SVIC lead yielded bibliographic references but no authenticated 1997 source release, and was not executed.','']
lines.insert(lines.index('## Source dating and inference boundary')+2,
 'Compatibility amendment: the inherited static-library build includes the recorded pre-Dewaghe sign-ambiguity switch. With NIST_PRE1998_X set, test_x_coordinate_uniquely returns false, retaining both X-coordinate trace signs. This is an explicit reconstruction amendment preserved in source/pre-dewaghe-sign.patch, not authenticated 1997 source. The all-root observer itself adds access-label changes only.\n')
lines.insert(lines.index('## Evidence and reproduction')+2,
 'Top-level observer and auditor copies are browseable mirrors. Run the verifier inside the extracted evidence directory, where its sealed source/table/input paths are present.\n')
(HERE/'report.md').write_text('\n'.join(lines))

def escape(s):return html.escape(str(s))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="760" viewBox="0 0 1050 760">',
'<rect width="1050" height="760" fill="white"/>',
'<text x="30" y="32" font-family="sans-serif" font-size="20">Rational modular roots per frozen curve (count)</text>',
'<text x="30" y="57" font-family="sans-serif" font-size="13">All 21 curves; all rational-root arithmetic checks passed. Fixed-sample observations.</text>']
for x,label in [(30,'Field / ordinal / observed label'),(630,'level 3'),(760,'level 5'),(890,'level 13')]:svg.append(f'<text x="{x}" y="92" font-family="sans-serif" font-size="14">{label}</text>')
for i,r in enumerate(rows):
 y=121+27*i;color='#e4f2f7' if r['label']=='published' else '#fcf0e5'
 svg.append(f'<rect x="22" y="{y-19}" width="985" height="25" fill="{color}"/>')
 label=f"{r['bits']} / {r['ordinal']} / {r['label']} / UID {r['curve_uid'].split(':')[-1][:12]}"
 svg.append(f'<text x="30" y="{y}" font-family="monospace" font-size="13">{escape(label)}</text>')
 for x,k in [(650,'roots_3'),(780,'roots_5'),(915,'roots_13')]:
  fill=['#f4f7f8','#d0e6e9','#99c9d0','#5ba7b4','#218093'][int(r[k])]
  svg.append(f'<rect x="{x-28}" y="{y-19}" width="70" height="25" fill="{fill}"/>')
  svg.append(f'<text x="{x}" y="{y}" font-family="monospace" font-size="15">{r[k]}</text>')
svg+=['<text x="30" y="717" font-family="sans-serif" font-size="12">Source: attempt-02, case-00..20, ell 3/5/13; full UIDs in comparison.csv.</text>',
'<text x="30" y="738" font-family="sans-serif" font-size="12">Cell shading increases from 0 to 4 roots; exact counts, no statistical uncertainty estimated.</text>','</svg>']
(HERE/'root-counts.svg').write_text('\n'.join(svg)+'\n')
diagram={'nodes':[{'id':'inputs','label':'21 frozen models: p,a,b; 6 streams'}, {'id':'native','label':'63 modular specializations; every rational root; Y and X'}, {'id':'arithmetic','label':'Independent polynomial / division / Velu / Fricke checks'}, {'id':'history','label':'1997 provenance and caller policy: unresolved'}], 'edges':[['inputs','native'],['native','arithmetic'],['arithmetic','history']], 'last_edge_status':'unestablished historical inference'}
(HERE/'workflow.diagram.json').write_text(json.dumps(diagram,indent=2)+'\n')
v=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="270" viewBox="0 0 960 270"><rect width="960" height="270" fill="white"/>']
labels=['21 frozen models / 6 streams','63 specializations / all roots','Independent arithmetic: PASS','Historical use: UNESTABLISHED']
for i,label in enumerate(labels):
 y=15+i*62;stroke='#25677b' if i<3 else '#9c5e28'
 v.append(f'<rect x="190" y="{y}" width="580" height="40" rx="7" fill="white" stroke="{stroke}" stroke-width="2"/>')
 v.append(f'<text x="480" y="{y+26}" text-anchor="middle" font-size="17" font-family="sans-serif">{label}</text>')
 if i<3:v.append(f'<path d="M480 {y+40} L480 {y+61}" stroke="{stroke}" stroke-width="2" '+('stroke-dasharray="4 4" ' if i==2 else '')+'/>')
v.append('</svg>');(HERE/'workflow.svg').write_text('\n'.join(v)+'\n')

styles=getSampleStyleSheet();styles['BodyText'].fontSize=9.4;styles['BodyText'].leading=13
styles['Heading1'].fontSize=18;styles['Heading1'].leading=22
styles['Heading2'].fontSize=12;styles['Heading2'].leading=16
doc=SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=36,bottomMargin=36)
story=[]
def p(text,style='BodyText'):story.append(Paragraph(escape(text),styles[style]));story.append(Spacer(1,6))
p('All-root SEA branch audit','Heading1');p('Fixed NIST/ANSI cohort | 27 October 2026')
p('Observations only: all 21 curves pass the tested arithmetic. Historical selection remains unresolved.')
p('Workload and controls','Heading2')
p('63 specializations = 21 curves x levels 3, 5, 13. All rational roots were tested with direct Y-coordinate and pre-Dewaghe ambiguous X-coordinate profiles. The native observer received only p, a, b and the auxiliary prime.')
p('Measured: 39 rational modular roots, 78 kernel/profile checks, 35 Atkin specializations. Independently verified: 78 division-polynomial, Velu/isomorphism and quotient/root Fricke checks. Zero actual cohort failures or timeouts.')
p('81 native invocations were retained: 9 initial missing-table controls, then 9 controls and 63 named cases. Three exceptional-invariant controls reached source errors and SIGABRT; none of the 21 cohort curves did. The first compile failure and both offline auditor versions are retained.')
p('Independent polynomial arithmetic reconstructed every specialized table polynomial, enumerated the complete rational-root set with gcd(F,X^p-X), checked distinct kernels and trace relations, and verified quotients. Controls included direct finite-field point counting and explicit positive/negative order-3 kernels.')
p('Source and inference','Heading2')
p('LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8; version string 2.3.0+latte-patches-2019-05-02. Access labels alone were changed in an observer header; the static library was unchanged. This is a later lineage, not authenticated 1997 generator code.')
p('The inherited build already includes an explicit pre-Dewaghe compatibility amendment: NIST_PRE1998_X disables unique X-sign resolution, retaining both signs. The patch is archived; it is a reconstruction amendment, not authenticated 1997 source. The observer adds access-label changes only.')
p('All-root success leaves no omission-specific exceptional path in this build at these levels. Earlier code, other levels, optimizer settings and caller policies remain untested. It does not establish a historical exclusion criterion.')
p('Provenance gap: the full fetched Git history starts with a 2013 import. NEWS says ECO was integrated in 2.1pre2; ChangeLog dates documentation to June 2001 and records September 2001 splitting-degree/crash fixes and a March 2004 schoofpart fix. The old faulty lines were not recovered.')
p('Evidence: attempt-02/PROTOCOL.json, runs/case-00..20-ell-{03,05,13}, AUDIT.json; source-history/ChangeLog and git-history.txt. Complete capture and replay: evidence.tar.zst, BUNDLE.json.')
story.append(PageBreak())
p('Every curve, including ordinary behavior','Heading1')
p('Heatmap of exact rational modular root counts: darker cells mean more roots (scale 0 to 4). Published labels are blue; reconstructed omissions are orange. Labels describe recovered streams, not documented historical rejection events.')
data=[['Field','Ordinal','Observed label','l=3','l=5','l=13']]+[[r['bits'],r['ordinal'],r['label'],r['roots_3'],r['roots_5'],r['roots_13']] for r in rows]
t=Table(data,colWidths=[50,58,155,60,60,60],repeatRows=1,rowHeights=23)
cmd=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17495e')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('ALIGN',(3,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]
for i,r in enumerate(rows,1):
 cmd.append(('BACKGROUND',(0,i),(2,i),colors.HexColor('#e4f2f7' if r['label']=='published' else '#fcf0e5')))
 for j,k in enumerate(['roots_3','roots_5','roots_13'],3):
  fill=colors.HexColor(['#f4f7f8','#d0e6e9','#99c9d0','#5ba7b4','#218093'][int(r[k])])
  cmd.append(('BACKGROUND',(j,i),(j,i),fill))
t.setStyle(TableStyle(cmd));story.append(t);story.append(Spacer(1,9))
p('Measured native root counts; independently checked against the complete linear-factor polynomial. Exact deterministic values; no sampling uncertainty estimated. Full field/model/order/seed/UID in frozen inputs and comparison.csv.')
story.append(PageBreak())
p('Patterns retained as leads','Heading1')
p('Post hoc observations: P-224 has four level-3 roots for its publication and one for each omission. P-192 and P-256 publications have one level-5 root, with none for their omissions. P-239 publications have no level-13 roots, while every omission has one or two.')
p('Different fields require different choices. A rule in only these three root counts cannot classify the full sample: omitted P-192/2198 and published P-239/2185 and P-384/2688 share (0,0,0). Field-dependent rules remain possible, but this source handles all these paths successfully and does not reject on these patterns.')
p('Historical test still required','Heading2')
p('Recover a dated pre-fix or standalone point counter, identify the actual relevant path, freeze its prediction without label-dependent changes, and check all 21 curves. No hypothetical reversal of a comparison is labeled recovered code. Inaccessible archive requests do not establish absence of older code.')
p('Portable replay','Heading2')
p('Extract evidence.tar.zst; run python3 -B evidence/verify.py. It verifies 489 sealed files and repeats independent Python arithmetic only. Native programs launched by replay: zero. The archive includes the raw errors and initial missing-table attempt; no failed invocation was silently repeated.')
p('Protocol SHA-256: b80560225b69b2cbb8370f01e26946164ef03b3d30055b31e50605a3566834ab. Seal and archive hashes: report.md and BUNDLE.json.')
p('Sources','Heading2')
for text in ['[1] github.com/passagemath/upstream-LiDIA, commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8, src/ec_order and ChangeLog.', '[2] Same repository, initial import 0171e66, NEWS: integration in 2.1pre2. Full source-history receipts included.', '[3] words.filippo.io/seeds-solved/ (16 October 2026), the historical selection question.', '[4] Local LMFDB av_fq manifest, public.av_fq_isog, extraction ended 2026-10-19T16:45:49.243703+00:00. Genus-1 coverage q<=1024; no match for these fields.']:
 p(text)
p('This report changes no official hypothesis status, conductor result or verified transfer map. The missing criterion remains open.')
def footer(c,d):c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#51606d'));c.drawString(38,22,'NIST/ANSI fixed-cohort audit | source use unestablished');c.drawRightString(A4[0]-38,22,str(d.page))
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'pages_expected':3,'rows':len(rows),'historical_criterion_identified':False}))
