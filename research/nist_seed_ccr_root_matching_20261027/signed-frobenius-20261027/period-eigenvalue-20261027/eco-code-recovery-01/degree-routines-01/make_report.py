"""Render static source evidence and missing historical application; no trials."""
from pathlib import Path
from reportlab import rl_config
rl_config.invariant=1;rl_config.useA85=0
from reportlab.lib.colors import HexColor,white
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.graphics.shapes import Drawing,Rect,String,Line
from reportlab.graphics import renderSVG
P=Path(__file__).resolve().parent
d=Drawing(500,205)
boxes=[(0,132,154,58,'May 1997 package','Exact bytes recovered','#e8f3ee'),(173,132,154,58,'15 September 2001','Fix note; patch missing','#fff3dd'),(346,132,154,58,'Later 2.3.0 snapshot','Caller strips fixed roots','#e8f3ee'),(0,29,154,65,'Intended valid inputs','Conditional error bound','< 2^-174 per call'),(173,29,154,65,'Linear input edge','Empty factor-list path','Native effect untested'),(346,29,154,65,'Original NIST caller','UNKNOWN on all 21','No skip rule identified')]
for x,y,w,h,t,a,b in boxes:
 color=b if b.startswith('#') else ('#e8f3ee' if x==0 else '#fff3dd')
 d.add(Rect(x,y,w,h,fillColor=HexColor(color),strokeColor=HexColor('#526474')))
 d.add(String(x+w/2,y+h-17,t,textAnchor='middle',fontName='Helvetica-Bold',fontSize=8.4));d.add(String(x+w/2,y+h-34,a,textAnchor='middle',fontSize=8))
 if not b.startswith('#'):d.add(String(x+w/2,y+12,b,textAnchor='middle',fontSize=8))
d.add(Line(77,132,77,94,strokeColor=HexColor('#526474')));d.add(Line(77,114,250,114,strokeColor=HexColor('#526474')));d.add(Line(250,114,250,94,strokeColor=HexColor('#526474')))
d.add(Line(423,132,423,94,strokeColor=HexColor('#a97633'),strokeDashArray=[3,3]));d.add(String(250,5,'Verified source facts and derived conditions; historical invocation remains missing.',textAnchor='middle',fontSize=8))
renderSVG.drawToFile(d,str(P/'source-boundary.svg'))
md='''# May 1997 degree routines: exact source audit and application limits

28 October 2026 UTC, T-5518. Source-only observations and symbolic derivation; zero new native curve/control trials. The preceding class-group turn was progress. The full historical-selector goal remains active and unresolved.

The source comparison authenticates a dated splitting-degree bug report and identifies an unguarded linear-input path. It does not identify the original caller or explain any of the eleven reconstructed omissions. All 21 full identities and six streams are retained in cohort-crosswalk.csv; historical application remains UNDETERMINED for ten publications and eleven omissions.

## Exact source and chronology

The advertised LiDIA1.3 package captured17 May 1997 is2,343,749 bytes, SHA2560189dcbb3daab55cb39f213bf612d025b71aac6bd4ca7a5c09b687f47c98d387. Its README 1.3/header 1.2.0 discrepancy remains explicit. The exact factoring.c, compose.c, fac_vec.c, Fp_polynomial.h and poly_modulus.h were read without compiling them. The package's standalone ECO caller is absent; general polynomial utilities are present.

The pinned later snapshot at passagemath/upstream-LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8 supplies five further source files. Every fetched Git blob matches its Git object hash. SOURCE-MANIFEST.json binds all ten original files by exact bytes/digest/URL; third-party bodies stay private in ignored .work.

The later ChangeLog lines15530-15535 records a15September 2001 fix to compute_splitting_degree that had caused an eco_gfp error. It identifies no exact input, introduction date or patch. Public factoring.cc Git history contains a complete 2.3.0 import in 2013 and a separate 2019 root-wrapper fix. That history cannot reconstruct the2001 change. The2019 change passes a polynomial-modulus object to power_x during general root filtering; the 1997 find_roots function instead assumes split input and has no such filter call. This later defect must not be backdated to1997.

## What the degree routines actually require

The1997 deterministic and probabilistic routines require a polynomial whose irreducible factors share a degree. Four normalized arithmetic bodies match the later endpoint: base_case, compute_split, rec_compute_degree and prob_compute_degree. Normalization removes comments/diagnostics/spacing and maps the modulus-degree accessor/type spelling; this is a bounded textual check, not compiled equivalence. tandem_power_compose differs in the field-modulus initialization API. The later deterministic wrapper also accepts a supplied known multiple of the common degree.

The later SEA caller handles all-fixed and one-fixed-root cases separately. In the two-fixed-root Elkies branch it removes both linear factors and reduces the Frobenius image before degree computation; the remaining nontrivial cycles have equal length. Thus simply imagining that this caller feeds the mixed full polynomial into the equal-degree routine would contradict the source read. Later constructors default to DONT_COMPUTE_SP_DEGREE, with Atkin bound 50 when enabled. Those defaults do not establish original NIST use.

## Intended randomized behavior, conditional derivation

The old routine draws a polynomial, applies the trace map, then draws a separate projection in min_poly. For squarefree equal-degree input of degree n>=2, d>=2 and m=n/d factors, independent uniform field draws give independent uniform component trace values when p>n. Pair collisions have probability at most m(m-1)/(2p). The documented minimal-polynomial projection error adds floor(n/2)/p. For d=1 the routine returns1 directly because the Frobenius image is X.

Within the documented range of prime auxiliary ell<800, n=ell+1<=798 and m<=399. Thus the per-call exceptional-degree bound is at most 79,800/p, which is less than2^-174 for all cohort field sizes. PROBABILITY-BOUND.md gives the derivation. This is an intended-algorithm bound under uniform independence and correct valid-input arithmetic, not measured output or a probability assigned to the historical deterministic RNG. It covers neither biased/randomness-consumption defects, malformed inputs nor another implementation.

## An unguarded linear-input path

For f=X-a, the reduced Frobenius image is a constant, so the source's h.is_x guard does not return. Factoring the integer degree 1 creates an empty factor list. The deterministic routine nevertheless calls its recursive helper with bounds 0,-1. The splitter then obtains mid=-2 and the following product range accesses index -1. LINEAR-EDGE.md records this static invalid-index path.

No native crash, compiler behavior or historical visitation has been executed here. The later endpoint still lacks an explicit low-level degree-one guard, so this observation is not identification of the2001 fix. The later SEA caller avoids the relevant cases before degree computation. Whether any original NIST invocation reached this path remains unknown for every curve. No omission is marked rejected from it.

## Coverage, verification and next discriminator

Source metadata seals13 files; private byte verification checks ten sources, including five Git objects. Fresh-directory public metadata replay and every 21-identity p,-3,b,n,seed,ordinal,timestamp/UID binding pass. The source crosswalk deliberately records original caller, actual polynomial degree, invocation and error policy as UNKNOWN for all 21, with no new curve-property predicate sweep. Operational retrieval/decoding errors and bounded unsuccessful searches are retained separately. Raw commit 7ba50faa68 precedes this report. No native code, profiler, RNG stream or new point count ran.

The source-boundary.svg diagram distinguishes authenticated bytes, derived intended behavior, the potential linear edge and missing historical application. Earlier signed-action/SEA graphs were checked and left unchanged: there is no new verified historical or attack edge. No official research-state transition is made. The P-224 cube/splitting observation remains separate.

The next discriminating evidence is the pre-fix 2001 source or an authenticated older caller showing which degree routine and polynomial it used, including failure handling. Native confirmation of the linear path alone would establish only a low-level defect; original reachability must still be demonstrated. Any new cohort execution requires a prospective frozen protocol and all 21 accounting. No outgoing contacts, subagents or memory writes.

Primary source links:

* [May 1997 captured package](https://web.archive.org/web/19970517195215id_/http://www.informatik.th-darmstadt.de:80/TI/LiDIA/linktop/LiDIA.tgz).
* [Pinned later degree routines](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/finite_fields/Fp_polynomial/factoring.cc).
* [Pinned ChangeLog, lines15530-15535](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/ChangeLog#L15530).
* [Pinned later caller, lines221-418](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/ec_order/eco_gfp/eco_gfp/eco_prime.cc#L221).
* [2019 root-wrapper patch](https://github.com/passagemath/upstream-LiDIA/commit/8a0b29280e3504a16accd882b7807122a6219410).

Replay: python3 verify_sources.py (public metadata/input custody); python3 verify_sources.py --sources (also requires the pinned private source files). Neither command executes a point counter.
'''
(P/'report.md').write_text(md)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BX',fontName='Helvetica',fontSize=9.4,leading=12.5,spaceAfter=9));styles.add(ParagraphStyle(name='SX',fontName='Helvetica',fontSize=7.8,leading=10.2,spaceAfter=6))
def para(s,small=False):return Paragraph(s,styles['SX' if small else 'BX'])
story=[Paragraph('1997 degree routines: source evidence',styles['Title']),para('28 October 2026 UTC | T-5518 | source-only audit; zero new native trials'),para('<b>Finding and limit.</b> Exact source authenticates a later splitting-degree fix report and exposes an unguarded linear-input path. Neither identifies an original NIST call or explains any omission. All 21 historical applications remain undetermined.'),d,Spacer(1,10),para('<b>Dated defect report.</b> ChangeLog 15 September 2001 records an eco_gfp error fixed in compute_splitting_degree. Available Git history begins with a complete 2.3.0 import in 2013; it contains no exact 2001 patch. A separate 2019 power_x root-wrapper fix affects a filter absent from the 1997 split-root routine. Neither later defect is backdated.'),para('<b>Verified endpoints.</b> The advertised May 1997 package is pinned by its 2,343,749-byte digest; README 1.3/header 1.2.0 discrepancy retained. Five original members and five later Git blobs are byte-verified. Four normalized helper/probabilistic arithmetic bodies match; tandem composition changes modulus initialization API, and the later wrapper accepts a supplied degree multiple. Textual comparison is not native equivalence.'),para('<b>Caller contract matters.</b> Later SEA handles all-fixed/one-fixed cases separately, removes both linear factors in the Elkies two-fixed-root branch and then requests the common remaining degree. Its default is DONT_COMPUTE_SP_DEGREE; Atkin bound 50 applies when enabled. These are later source facts, not original NIST invocation evidence.'),para('Sources: exact archived package capture 19970517195215; passagemath/upstream-LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8, factoring.cc/eco_prime.cc/ChangeLog. Full URLs, original byte/Git hashes and read-line scopes are in SOURCE-MANIFEST.json, HISTORY.json and SOURCE-REVIEW.json.',True),PageBreak(),Paragraph('Derived bounds and missing application',styles['Heading1']),para('<b>Conditional intended error bound.</b> With squarefree equal-degree input, n&gt;=2, p&gt;n, correct arithmetic and independent uniform field draws, m=n/d trace components collide with probability at most m(m-1)/(2p). The separate min_poly projection adds floor(n/2)/p. For auxiliary primes ell&lt;800 and n=ell+1&lt;=798, the total is at most 79,800/p&lt;2^-174 for these field sizes. Degree-one factors with n&gt;=2 return directly when h=X. This is no measured frequency or historical RNG probability.'),para('<b>Static linear edge.</b> For f=X-a the reduced Frobenius image is constant; the low-level h.is_x guard misses it. Integer degree 1 has an empty factor list, but recursion is entered with 0,-1, the splitter yields mid=-2 and a subsequent product includes index -1. This is an unguarded source path. No native crash or historical reachability is asserted; the later SEA caller handles the relevant cases earlier.'),para('<b>Complete cohort accounting.</b> Full model/order/seed/ordinal/timestamp and exact UID are retained for every row in cohort-crosswalk.csv. The original degree-routine invocation and error policy are UNKNOWN on all 21. No failure is inferred from source absence.' )]
t=Table([['Group','Exact identities','Historical application'],['Published','10','UNDETERMINED'],['Reconstructed omissions','11','UNDETERMINED'],['All six streams','21','UNDETERMINED']],colWidths=[200,100,200]);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),9),('BACKGROUND',(0,0),(-1,0),HexColor('#e4eaf0')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f4f6f8')]),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.extend([t,Spacer(1,12),para('<b>Custody checks.</b> All 13 sealed metadata files, ten private source hashes including five Git objects, and every 21 identity binding pass. Relocated public metadata replay passes. These checks execute no native source or curve calculation. Raw commit 7ba50faa68 precedes report publication; unrelated files and frozen earlier records are preserved.'),para('<b>Next discriminator.</b> Recover the pre-fix 2001 body or authenticated older caller with exact polynomial inputs and failure policy. A native linear-input control alone would establish only a low-level defect; original reachability remains separate. Any new curve trial needs a separately frozen protocol and all 21 controls/accounting. Existing signed-action/SEA graphs are unchanged; P-224 lead and full historical goal remain open.'),para('Public replay: python3 verify_sources.py . Private bytes: append --sources. Complete symbolic derivation in PROBABILITY-BOUND.md; static path in LINEAR-EDGE.md. All source bodies stay ignored/private; metadata does not authenticate NIST use.',True)])
def footer(c,doc):c.setFont('Helvetica',7);c.drawString(48,24,'T-5518 | degree-routines-01 | source audit; historical selector unresolved');c.drawRightString(564,24,str(doc.page))
SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=34,bottomMargin=36).build(story,onFirstPage=footer,onLaterPages=footer)
print('Static source report, editable SVG and PDF rendered.')
