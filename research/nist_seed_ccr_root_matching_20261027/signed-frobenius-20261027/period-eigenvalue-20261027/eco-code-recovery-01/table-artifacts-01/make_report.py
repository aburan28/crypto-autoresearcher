"""Render a two-page source-review digest with the editable evidence diagram."""
from pathlib import Path
import re
from reportlab import rl_config
rl_config.useA85=0;rl_config.invariant=1
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,Table,TableStyle
P=Path(__file__).resolve().parent
s=getSampleStyleSheet()
s.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.7,leading=13.6,spaceAfter=10))
s.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=8))
s.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=14))
story=[]


def text(t,style='BodyX'):
 t=re.sub(r"\b(May|Lehmann's|modulo|later|on|all|All|The|the|commit|verifies|inspected|capture|snapshot)(?=\d)",r'\1 ',t)
 t=t.replace('authenticated1997','authenticated 1997').replace('size0','size 0').replace('commitdda4','commit dda4').replace('Git blob01bec','Git blob 01bec').replace('ell199','ell 199').replace('/14','/ 14')
 story.append(Paragraph(t,s[style]))


text('Original tables and binary compatibility','TitleX')
text('28 October 2026 UTC | T-5518 | table-artifacts-01','SmallX')
text('<b>Historical selector unresolved.</b> This source-only round verifies a dated polynomial coefficient witness, reads the binary interfaces preserved in May1997 and checks an archived history lead. It runs no original point counter and no new scientific trial.')
text('<b>Dated coefficient identity.</b> Lehmann\'s1994 thesis, printed p78 / PDF p79, gives the complete ell=5 polynomial:')
text('<font face="Courier">G5(X,J) = (X^2+10X+5)^3 - J*X</font>')
text('All seven rows /14 coefficient entries match the later ASCII meq5 file exactly. The printed modulo101 table agrees with reduction of those integers. A separate convolution verifies the polynomial identity. The original source page was visually inspected, including the negative J coefficient.')
story.append(Image(str(P/'table-boundary.png'),width=500,height=182,kind='proportional'))
story.append(Spacer(1,11))
text('<b>Printed index inconsistency.</b> An intermediate boxed a_0,0=43 conflicts with the final a_0,0=24 modulo101. Its surrounding calculation concerns a_1,0=43; both final tables agree with the coefficient identity. This is not evidence of a native program defect.')
text('<b>All21 identities retained.</b> The crosswalk checks each p,b,n,seed,ordinal and full UID against the frozen prior rows and verifies the imported CSV against its original archive seal. Historical table bytes, backend/ABI, level visitation and error policy remain UNKNOWN for every curve. Therefore all ten publication and eleven omission predictions under the I/O explanation are UNDETERMINED.')
text('The ell=5 identity establishes one mathematical table witness. It authenticates neither the original binary bytes nor use by NIST. Existing P-224 cube/splitting and ell199 separator observations retain their earlier limits. No new conductor, endomorphism or transfer conclusion follows.','SmallX')
story.append(PageBreak())

text('What the actual I/O source requires','TitleX')
text('The preserved May1997 package has backend-specific binary interfaces. None of these source observations identifies an omission-specific consequence without original files and caller behavior.')
data=[
 ['Backend','Binary interface observed'],
 ['libI',Paragraph('Three native int fields, then length native unsigned-long digits. Endianness, widths and representation matter.',s['SmallX'])],
 ['FreeLIP',Paragraph('Native long words, including signed digit count and limb payload. The LiDIA wrapper discards the lower-level read-status return.',s['SmallX'])],
 ['GMP',Paragraph('mpz_out_raw / mpz_inp_raw. Its header records a binary/text API-body exchange on 9 January 1997; pre-change bodies are not recovered.',s['SmallX'])],
]
t=Table(data,colWidths=[75,425],hAlign='LEFT')
t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
 ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f0fa')),('TOPPADDING',(0,0),(-1,-1),8),
 ('BOTTOMPADDING',(0,0),(-1,-1),8),('FONTSIZE',(0,0),(-1,-1),9)]))
story.append(t);story.append(Spacer(1,12))
text('<b>Later reader boundary.</b> The later2.3.0 meq reader prefers ASCII, then binary/compressed forms; binary rows call its selected bigint backend. Its modulus-taking reader handles compressed inputs during polynomial construction. The canonical private copy matches Git blob01bec36819fde2ea247872e6add0ed578fe3bdbb. It is not authenticated1997 source.')
text('<b>Archive lead resolved.</b> The Software Heritage LiDIA-history snapshot returns an empty branch map and no next page. Earlier full-visit metadata does not mean historical code was preserved there. The GitHub repository advertises size0. This closes that specific lead, not all possible CVS/SVN archives.')
text('<b>Access limits.</b> The1999/2000 project-page captures describe the counter as outside the free distribution. One filtered CDX query is empty and three prefix queries time out; no absence proof follows. Original atobin/bintoa bodies, actual table files, binary build and caller remain missing.')
text('<b>Verification and custody.</b> Coefficient collation, all21 input bindings and the public seal pass. Fresh-directory metadata replay verifies16 sealed members and the coefficient identities without native execution or network. Raw commitdda4dd955f was pushed first. The16,808-byte archive excludes original code/package/HTML/PDF bodies. The initial archival file-count assertion stopped before committing, then the inspected22-file set was committed.')
text('<b>Next discriminating evidence.</b> Recover an actual standalone ECO distribution or original caller/table set. Freeze any precise recovered mechanism before an untuned comparison of all eleven omissions and ten publications. The overall goal stays active.','SmallX')
text('<b>Sources and replay</b><br/>Le94: author-homepage capture19970731071932, lehmann.diplom.ps, printed p78.<br/>May1997 package: capture19970517195215, TI/LiDIA/linktop/LiDIA.tgz.<br/>Later reader: passagemath/upstream-LiDIA, commit23dac491f4cd96eb7de648a5cf90eb9ec77653c8.<br/>SWH snapshot:1a8893e6a86f444e8be8e7bda6cb34fb1735a00e.<br/>Exact URLs, source-member hashes, line references and complete reading limits are in report.md and adjacent JSON records. Public replay: python3 -B verify_bundle.py.','SmallX')


def footer(c,d):
 c.saveState();c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#536477'))
 c.drawString(48,27,'T-5518 | table-artifacts-01 | source collation; historical selector unresolved')
 c.drawRightString(564,27,str(d.page));c.restoreState()


SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,
 topMargin=42,bottomMargin=45,title='Original table witness and binary compatibility',author='T-5518').build(story,onFirstPage=footer,onLaterPages=footer)
print('PDF source-review digest rendered.')
