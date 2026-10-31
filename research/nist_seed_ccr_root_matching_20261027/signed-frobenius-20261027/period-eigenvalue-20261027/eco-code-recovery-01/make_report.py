"""Create the PDF digest; the full report.md and editable figures accompany it."""
import json
import re
from pathlib import Path
from reportlab import rl_config
rl_config.useA85 = 0
rl_config.invariant = 1
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle

P = Path(__file__).resolve().parent
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.6,leading=13.4,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=7))
styles.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=13))
story=[]


def text(s,style='BodyX'):
    s = re.sub(r'\b(from|through|and|type|level|parameter|all|May|February|says|in|compressed|commit|has|of|pages|pp)(?=\d)',r'\1 ',s)
    s = s.replace('LiDIA1.3','LiDIA 1.3')
    story.append(Paragraph(s,styles[style]))


def picture(n,w,h):
    story.append(Image(str(P/n),width=w,height=h,kind='proportional'))
    story.append(Spacer(1,9))


text('Recovered modular-polynomial source','TitleX')
text('Lehmann 1994 and the May 1997 LiDIA package | T-5518 | 27 October 2026 PDT','SmallX')
text('<b>The historical selector remains unresolved.</b> This round obtains actual primary sources and compares their documented conditions with retained evidence for eleven reconstructed omissions and ten publications across six streams. There are zero new scientific trials and no execution of an original NIST/ANSI caller.')
text('<b>Source recovered.</b> Frank J. Lehmann\'s 125-page diploma thesis has a title-page date of 29 July 1994. An uncompressed PostScript link on his university homepage has a July 1997 archive capture; its PS creation header is dated October 1994. The exact original is 850,162 bytes. Its reading scope and digests are in SOURCE-REVIEW.json.')
picture('source-boundary.png',500,168)
text('<b>The j-cube distinction.</b> The Weber identity <font face="Courier">j=(w+16)^3/w</font>, with w=f2^24, occurs in formal q-series construction of integer coefficient tables. The curve interface substitutes J=j(E), reduces modulo p and inspects splitting. It specifies no cube root of the input j(E). Type2 Hecke-index restrictions concern the auxiliary prime and chosen index, not a curve conductor.')
text('<b>A concrete table provenance lead.</b> The thesis reports equivalent polynomials for every prime ell&lt;800. It describes CRT reconstruction with a heuristic stop after two unchanged iterations, ASCII out... files and libI binary conversion through atobin/bintoa. These are source-based dependencies to recover. They do not demonstrate a bad table or curve rejection.')
text('Le94 printed pp23-24,57-62,66,85-86,92,119-122. PDF pages1,25,67,93,120,122 were inspected visually. A July 1997 capture establishes preserved bytes, not NIST use. Full source URL, title, dates and hashes accompany this digest.','SmallX')
story.append(PageBreak())

text('All six streams and every fixed curve','TitleX')
text('The crosswalk checks exact p,b,n,j,seed,ordinal and full curve-UID bindings for all 21 entries before summarizing previously completed observations. All have p&gt;3 and ordinary generic j; none lies on the tested special CM routes containing j=0 or j=1728.')
picture('retained-coverage.png',500,210)
data=[['Stream','Published','Omitted','Type2 fibers','Triggers']]
names={863711343:'239-bit ANSI',863966734:'192-bit ANSI',871002724:'P-521',871696354:'P-256',872952608:'P-384',891607927:'P-224'}
record=json.loads((P/'CROSSWALK.json').read_text())
for r in record['streams']:
    data.append([names[r['stream']],r['published'],r['omitted'],r['type2_fibers'],r['repeated_fibers']])
data.append(['Total',10,11,299,0])
t=Table(data,colWidths=[128,85,85,105,92],hAlign='LEFT')
t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
                       ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f0fa')),
                       ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#728299')),
                       ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                       ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold')]))
story.append(t);story.append(Spacer(1,20))
text('<b>Retained scope.</b> 61 levels from3 through293, 1,281 cells, 1,185 rational parameters and 2,071 fibers: 1,772 type1 source/Fricke and299 type2. None has a nonconstant derivative gcd. The existing level53 control over F1009 at parameter98 does exercise a repeated type2 fiber.')
text('<b>Limitation.</b> These are exact retained counts using later LiDIA coefficient tables and rational parameter roots. They do not certify all extension-field fibers, every statement in the thesis or the original table bytes. No statistical uncertainty model or original-program acceptance rate is inferred.','SmallX')
story.append(PageBreak())

text('Software evidence and the remaining gap','TitleX')
text('<b>Actual preserved package.</b> The advertised LiDIA1.3 bundle captured in May1997 contains 1,461 members and1,285 regular files, all statically cataloged and hashed. The README says1.3; version.h says1.2.0. That discrepancy is retained explicitly. No package code was executed.')
text('The named Ma94 point-counter routines are absent under the declared whole-token scan. Generic polynomial degree and root routines, plus ECM factorization code, are present. Positive scanner controls find Fp_polynomial in70 files and power_mod in21; no claim of an absence of all elliptic arithmetic is made.')
text('<b>Release context.</b> The 5 February1997 announcement lists point counting as work in progress. The 2 February2000 announcement explicitly excludes its LiDIA-based SEA package from the free distribution. This explains why a general tarball need not supply the counter; it identifies no NIST software or missing mathematical criterion.')
text('<b>Checks and custody.</b> The exact private-package scan, all21 crosswalk and public seal check pass. A fresh-directory extraction verifies all36 sealed metadata files and the separate compressed1,285-file hash catalog. Python syntax and JSON parsing pass. All source bodies and source-page images remain private. Raw commit6501d989d0 was pushed before this report.')
text('<b>Still needed.</b> Recover authenticated out... coefficient tables, examine_l/lmod_equ/lcompute_ark/lcompute_ars and atobin/bintoa bodies; identify the original eco invocation, defaults, error policy and candidate-decision log. Freeze any actual new mechanism before testing all eleven omissions and ten publications without retuning.')
text('The P-224 cube/splitting observation and retrospective ell199 two-cap separator remain leads. This source adds neither a cube-root-of-j acceptance requirement nor the fitted caps. The reported ell&lt;800 coverage is evidence against an inherent precomputation ceiling of199, while actual generator deployment remains unknown. General j/endomorphism/transfer conditions stay open.')
text('<b>Publication state.</b> The fresh comparison with main still has11 merge conflicts and five immutable A/A identifier collisions. Those records remain unchanged. This report supplies no claim of merge readiness, original source execution or a solved historical selector.','SmallX')
text('<b>Primary sources and replay</b><br/>Le94: web.archive.org/web/19970731071932id_/http://www.cs.uni-sb.de:80/users/mdenny/Bewohner/lehmann/lehmann.diplom.ps<br/>Package: web.archive.org/web/19970517195215id_/http://www.informatik.th-darmstadt.de:80/TI/LiDIA/linktop/LiDIA.tgz<br/>Announcements: math.albany.edu/g/Math/Comp/cas/LiDIA-feb97 and LiDIA-feb2000<br/>Public seal: python3 -B verify_bundle.py<br/>Prior-input crosswalk: python3 -B source_crosswalk.py --check','SmallX')
text('The full report.md, exact source receipts, complete identity CSV, editable visual scripts and SVGs accompany this digest. No formal hypothesis status or canonical isogeny edge changes. The full goal remains active.','SmallX')


def footer(c,d):
    c.saveState();c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#536477'))
    c.drawString(48,27,'T-5518 | eco-code-recovery-01 | source review; zero new scientific trials')
    c.drawRightString(564,27,str(d.page));c.restoreState()


doc=SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,
                      topMargin=42,bottomMargin=45,title='Recovered 1994 modular-polynomial source',author='T-5518')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('PDF digest rendered.')
