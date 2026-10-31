"""PDF digest of report.md; sources and editable SVGs remain alongside it."""
from pathlib import Path
import re
from reportlab import rl_config
rl_config.useA85 = 0
rl_config.invariant = 1
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle

P = Path(__file__).resolve().parent
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyX', fontName='Helvetica', fontSize=9.4, leading=13.3, spaceAfter=9))
styles.add(ParagraphStyle(name='SmallX', fontName='Helvetica', fontSize=8, leading=11, spaceAfter=7))
styles.add(ParagraphStyle(name='TitleX', fontName='Helvetica-Bold', fontSize=19, leading=23, spaceAfter=14))
story = []


def text(s, style='BodyX'):
    s = re.sub(r'\b(all|the|and|of|a|A|by|at|over|on|with|covers|levels|level|original|Original|independent|includes|page|pages|is|pp|p|Broad|eco|ell|Type|type|ANTS|fixed|or)(?=\d)', r'\1 ', s)
    s = re.sub(r'(July|April|October)(?=\d)', r'\1 ', s)
    s = s.replace("Maurer\'s130", "Maurer\'s 130").replace('The1994', 'The 1994')
    s = re.sub(r',(?=\d)', ', ', s)
    s = s.replace('281, 859', '281,859')
    story.append(Paragraph(s, styles[style]))


def title(s):
    text(s, 'TitleX')


def picture(name, width, height):
    story.append(Image(str(P/name), width=width, height=height, kind='proportional'))
    story.append(Spacer(1, 10))


title('The 1994 implementation thesis')
text('Actual resource controls, a documented exceptional case, and the remaining caller gap')
text('27 October 2026 | T-5518 | implementation-sources-01', 'SmallX')
text('<b>Historical selector unresolved.</b> This is a primary-source review and crosswalk to completed evidence. There are zero new scientific trials. The goal remains the actual mechanism accounting for all eleven reconstructed omissions while retaining ten publications across six streams.')
text('<b>New source recovered:</b> Markus Maurer\'s130-page Saarland diploma thesis has a title-page date of29 July1994. The original gzip was recovered from an archived university FTP mirror; its PostScript header is dated17 October1994. A2006 capture date establishes preservation then, not the original1994 custody.')
picture('source-chain.png', 495, 183)
text('The thesis identifies the C/C++ program <b>eco</b>, source-file/function names, relation-file formats, configurable resource controls and command-line modes. It does not identify a NIST/ANSI invocation or a candidate-decision log.')
text('The exact public gzip is281,859 bytes, SHA256:<br/><font face="Courier" size="7.7">a0bfcc09e9d58bfefac531bf9a9037f42b317c36f7e5681f273b283cf6b1b3e3</font>', 'SmallX')
text('The author-hosted ANTS1994 counting paper and the27 April1995 Buchmann-Muller-Shoup report were also obtained and read. The former has a2001 PDF conversion date; no byte identity to the proceedings edition is claimed. Source bytes and renderings remain private under .work/.', 'SmallX')
story.append(PageBreak())

title('Every omission and publication covered')
text('The retained modular-coordinate audit covers21 curves,61 levels3..293,1185 rational modular parameters and2071 fibers. The new script checks every p,j and full p,b,n,UID binding before summarizing those existing observations.')
picture('fiber-coverage.png', 495, 382)
text('<b>Ma94 p93:</b> type2 neighbor reconstruction is unspecified when G_l(A(tau),Y) has repeated roots. In the retained later-table audit all299 type2 fibers, and all1772 type1 source/Fricke fibers, have coprime derivative gcds. The condition occurs on none of the21 curves. An existing level53 positive control over F1009 does trigger it.')
text('These are exact retained counts, without a statistical uncertainty model. They are not a fresh run of eco1994. Original1994 coefficient bytes and the1997 caller remain unauthenticated. Full fields, equations, orders, seeds, ordinals and UIDs are retained in cohort-crosswalk.csv.', 'SmallX')
story.append(PageBreak())

title('What the implementation actually controls')
entries = [
 ('pp65-66: baby-step memory', 'A configurable K_B,max shifts moduli to giant steps and rebalances them. It bounds a table, not the eigenvalue list at a particular prime. No fixed32 or2048 acceptance rule is supplied.'),
 ('p111: total combinations', 'MAXKOMB concerns the combined CRT candidate population. Its numerical value is not supplied. It is distinct from an eigenvalue-list length and from the minimum degree of a division-polynomial factor.'),
 ('pp117-118: caller modes', '-moduls supplies a prime list; -noadeg suppresses Atkin-degree work only with that list; -rsplit skips primes missing saved split data; -proof requests order proof. Actual invocation, defaults and files remain unknown.'),
 ('pp83-93: neighbor formulas', 'Given coefficients supply E4=-a/3 and E6=-b/2. The displayed interfaces request no cube root of j. Type1 DJ=0 has a square-root fallback; type2 repeated roots have the explicit gap checked on page2.'),
 ('pp94-100: eigenvalue matching', 'Signed positive-half candidates and a y-only heuristic are described. The previous independent411-kernel comparison has no wrong first-y match on any cohort kernel; it includes228 omission and183 publication kernels over22 represented levels.'),
 ('pp39-46: CM shortcuts', 'Norm-based special counters cover supersingular curves and base-field isogeny classes containing j=0/1728. The previous all21 comparison finds no cohort member on those routes, with generic-j positive controls.'),
]
for head, body in entries:
    text('<b>'+head+'</b><br/>'+body)
text('<b>Literal pseudocode caveat.</b> The image on printed p111 really initializes KOMB=1 and prints an AND guard requiring KOMB&gt;MAXKOMB. For every positive integer MAXKOMB this is initially false for every curve. A literal copy would visit no odd auxiliary prime. This is a documentary inconsistency, not an observed C-program defect. An OR repair would be a reconstruction choice.')
story.append(PageBreak())

title('Provenance and the next discriminating evidence')
text('<b>Primary passages read.</b> Ma94: title/date; pp22-28,39-46,59-61,65-67,83-100,110-114,117-126. Title and PDF pages67,94,96,112,119 were inspected visually. Printed page = PDF page minus one. The two short reports were read completely; their date and key algorithm pages were inspected.')
text('<b>Retained imports.</b> CROSSWALK.json pins the prior cohort, fiber audit and its bundle, complete y-match audit and bundle, and independent CM-route result and bundle. build_crosswalk.py --check reconstructs the complete CSV and metadata from those records. It neither invokes a point counter nor changes a frozen result.')
text('<b>Access limits.</b> The archived project page and report directory now establish both thesis filenames. Exact Le94 archive requests return an empty array; its contents remain unobtained. Broad100-row CDX outputs are bounded. Two wildcard queries returned general-domain rows and are unused as filename evidence. Failed CLI and catalog attempts remain in the retrieval receipts. No copy request or outgoing contact was sent.')
text('<b>What the evidence leaves open.</b> The P-224 cube/splitting pattern and the retrospective ell199 separator remain leads. This source supplies neither a cube-root-of-j prerequisite nor the two fitted caps. Original function bodies, coefficient tables, defaults, invocation, root order, error policy and candidate visitation remain unknown. No endomorphism, conductor, transfer or cryptographic weakness conclusion follows from these passages.')
text('<b>Next sources.</b> Recover the named C bodies, especially buildLlist, choose_relations, compute_klist, binsearch and verify_order; recover Le94 and authenticated coefficient data; obtain the original Reiter/NIST/ANSI caller or run log. Freeze any newly recovered rule before comparing every omission and publication without retuning. Reconstructed omissions remain distinct from documented rejection events.')
text('<b>Primary links</b><br/>Ma94 archive: web.archive.org/web/20060216012606id_/http://www.informatik.tu-darmstadt.de:80/ftp/pub/TI/reports/maurer.diplom.ps.gz<br/>ANTS author copy: shoup.net/papers/counting.pdf<br/>1995 report: publikationen.sulb.uni-saarland.de/handle/20.500.11880/25886<br/>Full Markdown report, exact receipts, editable SVGs and21-curve CSV accompany this digest.', 'SmallX')
text('Canonical parent diagrams were checked and their mathematical statements remain unchanged. No formal hypothesis status, isogeny edge or historical-selector attribution is added. The full goal remains active.', 'SmallX')


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#536477'))
    canvas.drawString(48, 28, 'T-5518 | implementation-sources-01 | source review; no new scientific trials')
    canvas.drawRightString(564, 28, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(str(P/'report.pdf'), pagesize=(612,792), rightMargin=48,
                        leftMargin=48, topMargin=42, bottomMargin=45,
                        title='The1994 point-counting implementation thesis', author='T-5518')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
