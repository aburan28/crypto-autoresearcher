"""Render the dated-source audit; the stronger certificate experiment remains pending."""
from pathlib import Path
from reportlab import rl_config
rl_config.useA85=0;rl_config.invariant=1
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.graphics.shapes import Drawing,Rect,String
from reportlab.graphics import renderSVG
P=Path(__file__).resolve().parent
md="""# Dated class-number advice: source audit

28 October2026 UTC, T-5518. No new scientific trials.

The dated200 bound is already settled conditionally by the retained full21 comparison: ten publications and eleven omissions pass. The stronger10^7 bound has NOT been evaluated. This source audit must not be presented as the completed stronger test.

Baier2002 section2.3.5 reports the German requirement h(O_K)>=200. ETSI TS102176-1 V1.2.1 July2005 clause6.1.2.3 and AnnexD.3 require the same200 lower bound on the maximal CM order. RFC5639 March2010 section2.1 item3 requires h(O_K)>10^7. These are dated later documents, not evidence of1997 NIST use. The2005 Brainpool PDF retrieval timed out; its actual contents were not read here.

The earlier class-number study compares all21 frozen identities against an external list claimed complete for h(K)<=2000. There are zero matches. Conditional on that completeness theorem, all21 have h(K)>2000 and therefore meet the documented200 bound. The new SOURCE-AUDIT.json binds that exact prior analysis digest and every UID. The2026 theorem is an external dependency, not independently proved by this session. No conclusion for10^7 follows from h(K)>2000.

For an actual CM order O_f, the class map to the maximal order is surjective, so h(O_K) divides h(O_f). Thus a certified lower bound for the maximal order also lower-bounds the actual CM-order class number. A large Frobenius-order class number does not imply a large maximal-order class number. A conductor of3 is not by itself evidence for small class number.

The prospective stronger test is fixed in PLAN.md: take the first24 split rational primes and check4*product(primes)<abs(D_K). CERTIFICATE-LEMMA.md proves that this would give h(K)>=2^24=16777216>10^7. Missing certified fundamental discriminants stay UNKNOWN; failure of the sufficient inequality is NOT_CERTIFIED, not an upper bound. Controls, an independent arithmetic verifier, the formal frozen protocol and complete21-row accounting remain required before execution.

Source links: https://d-nb.info/964515040/34 ; https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf ; https://www.rfc-editor.org/rfc/rfc5639.html ; https://arxiv.org/abs/2610.21511 .

Prior analysis: ../nist_seed_commonality_20261023/class_number_screen/report.md . Earlier graph content remains unchanged; source-boundary.svg records this audit's conditional completed result and pending stronger test. The historical selector remains unresolved and the full goal stays active.
"""
(P/'report.md').write_text(md)
d=Drawing(500,105)
for x,w,t,b,c in [(0,240,'Documented h(K) >= 200','10 published / 11 omitted PASS*','#e8f3ee'),(260,240,'Documented h(K) > 10^7','NOT EXECUTED: certificate planned','#fff3dd')]:
 d.add(Rect(x,25,w,65,fillColor=HexColor(c),strokeColor=HexColor('#43566a')))
 d.add(String(x+w/2,66,t,textAnchor='middle',fontName='Helvetica-Bold',fontSize=10))
 d.add(String(x+w/2,44,b,textAnchor='middle',fontName='Helvetica',fontSize=9))
d.add(String(250,6,'*Conditional on the external h <= 2000 list completeness theorem',textAnchor='middle',fontSize=8))
renderSVG.drawToFile(d,str(P/'source-boundary.svg'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.5,leading=12.7,spaceAfter=9))
story=[Paragraph('Dated class-number bounds',styles['Title']),Paragraph('28 October 2026 UTC | T-5518 | source audit; no new scientific trials',styles['BodyX']),d,Spacer(1,12)]
for t in [
 '<b>Completed comparison:</b> the dated lower bound200 passes all ten publications and eleven omissions, conditional on the existing external list completeness theorem. <b>The stronger10^7 condition has not been evaluated.</b>',
 '<b>Source dates.</b> Baier2002 section2.3.5 reports h(O_K)&gt;=200. ETSI TS102176-1 V1.2.1 (July2005), clause6.1.2.3 and AnnexD.3, uses200. RFC5639 (March2010), section2.1 item3, requires h(O_K)&gt;10^7. All concern the maximal CM order. No1997 NIST adoption is established.',
 '<b>Evidence limit.</b> The earlier full21 study found no field on an external list claiming completeness for h(K)&lt;=2000. The new crosswalk binds that analysis and each UID. Conditional on the theorem, h(K)&gt;2000 implies the documented200 condition. It does not establish h(K)&gt;10^7. This session did not independently prove the external classification.',
 '<b>Order distinction.</b> The class number of the maximal order divides that of any order in the field. A certified maximal-order lower bound therefore also applies to the actual CM order. A Frobenius-order lower bound alone cannot be transferred in the reverse direction. Conductor3 alone does not imply small class number.',
 '<b>Prospective certificate.</b> For24 distinct split primes with4*product&lt;|D_K|, the subset-ideal argument in CERTIFICATE-LEMMA.md proves h(K)&gt;=2^24&gt;10^7. PLAN.md fixes ascending-prime selection and UNKNOWN/NOT_CERTIFIED outcomes. Implementation, independent arithmetic checks and formal protocol freezing remain required before new cohort evaluation.',
 '<b>Primary sources.</b> d-nb.info/964515040/34; ETSI TS102176-1 V1.2.1 July2005; rfc-editor.org/rfc/rfc5639.html; arxiv.org/abs/2610.21511. Exact source URLs and prior-input digest are in SOURCE-AUDIT.json. Full report.md and editable figure generator accompany this digest. Historical selector unresolved; goal active.'
]:story.append(Paragraph(t,styles['BodyX']))
SimpleDocTemplate(str(P/'report.pdf'),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40).build(story)
print('Dated-source report, editable SVG and PDF rendered.')
