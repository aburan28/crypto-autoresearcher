"""Plot the recorded source threshold and render the source-route report."""
import argparse,csv,json,pathlib,textwrap
P=pathlib.Path(__file__).resolve().parent

def figure():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 rows=json.loads((P/'RESULT.json').read_text())['rows'];groups={}
 for r in rows:groups.setdefault(int(r['p']).bit_length(),[]).append(r)
 bits=sorted(groups);xs=list(range(len(bits)));a=[groups[b][0]['literal_first_phase_stop_m0_1'] for b in bits];b=[groups[b][0]['literal_first_phase_stop_m0_2'] for b in bits]
 fig,ax=plt.subplots(figsize=(9.7,4));bars1=ax.bar([x-.18 for x in xs],a,width=.34,label='initial m=1',color='#285e81');bars2=ax.bar([x+.18 for x in xs],b,width=.34,label='initial m=2',color='#89a7bb')
 for bars in [bars1,bars2]:
  for r in bars:ax.text(r.get_x()+r.get_width()/2,r.get_height()+5,str(int(r.get_height())),ha='center',fontsize=9)
 ax.axhline(199,ls='--',color='#aa512d',lw=1);ax.text(-.47,202,'199: fitted rule prime',fontsize=9,color='#93431f');ax.set_xticks(xs,[str(k)+' bits\n'+str(len(groups[k]))+(' curve' if len(groups[k])==1 else ' curves') for k in bits],fontsize=9);ax.set(ylim=(0,225),ylabel='Last prime needed for m squared >= 16p',title='Literal first-phase threshold in Muller 1995 algorithm 10.5');ax.legend(loc='upper left',bbox_to_anchor=(.01,.83),fontsize=9);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
 fig.text(.02,.015,'NIST-MUELLER1995-ROUTES-01. Same 21 curves, six exact fields; two independent methods agree.\nThese are pseudocode thresholds, not measured practical stopping primes. Section 10.4 explicitly continues further.',fontsize=8);fig.subplots_adjust(left=.09,right=.98,bottom=.23,top=.88);fig.savefig(P/'first-phase.svg');fig.savefig(P/'first-phase.png',dpi=180);plt.close(fig);f=P/'first-phase.svg';f.write_text('\n'.join(x.rstrip() for x in f.read_text().splitlines())+'\n')

def pdf():
 from reportlab import rl_config
 rl_config.useA85=0
 from reportlab.pdfgen import canvas
 from reportlab.lib.colors import HexColor
 from reportlab.lib.utils import ImageReader
 c=canvas.Canvas(str(P/'report.pdf'),pagesize=(612,792),invariant=1);c.setTitle('Muller1995: source-defined CM routes and stopping limits');y=0
 def start(title,page):
  nonlocal y
  c.setFillColor(HexColor('#173e59'));c.setFont('Helvetica-Bold',17);c.drawString(42,749,title);c.setFillColor(HexColor('#222222'));c.setFont('Helvetica',8);c.drawString(42,731,'NIST-MUELLER1995-ROUTES-01 | T-5518 | 2026-10-27 | observation report');c.drawRightString(570,25,str(page));y=704
 def para(t,size=10):
  nonlocal y
  c.setFont('Helvetica',size)
  for line in textwrap.wrap(t,width=100 if size==10 else 115):c.drawString(42,y,line);y-=14
  y-=9
 def sub(t):
  nonlocal y
  c.setFont('Helvetica-Bold',11);c.drawString(42,y,t);y-=21
 start('Actual period source: special CM routes',1)
 para('Observation report and documentary comparison. The historical NIST/ANSI selector remains unresolved; no formal goal or hypothesis status changes. This round obtained and read the original 1995 Muller dissertation and checked its explicit special-route arithmetic on all 21 fixed curves.')
 sub('Recorded result: all 21 curves use the generic branch')
 para('Both independent methods agree: 0 of 10 publications and 0 of 11 reconstructed omissions are supersingular or in an ordinary base-field isogeny class containing j=0 or j=1728. This includes P-384 and requires no complete discriminant factorization.')
 para('For t=p+1-n and K=4p-t^2, the first method tests K=3v^2 or K=4v^2. The independent GP method solves norm forms and enumerates all unit-multiple traces. These detect CM fields Q(sqrt(-3)) and Q(i); a conductor equal to three is a different property.')
 sub('Positive controls test isogeny, not just the visible j')
 for t in ['F7: y^2=x^3+3x+1, order 12, j=2 -> ordinary j=0 isogeny class.','F5: y^2=x^3+4x+1, order 8, j=1 -> ordinary j=1728 isogeny class.','F7: y^2=x^3+x, order 8 -> supersingular route.','F5: y^2=x^3+x+1, order 9 -> ordinary, neither special class.']:para(t)
 para('Both methods independently count the four explicit small models. Generic positive j-values, negative case, singular/wrong-order guards and A/A repeats pass before cohort processing. Local LMFDB classes 1.7.e, 1.5.c, 1.7.a, 1.5.d supply class metadata only, not individual equations.',9)
 sub('Exact source identity')
 para('Volker Muller, Saarland dissertation, 1995; oral examination May 18, 1995. University DOI 10.22028/D291-25721. Source PDF: 1,850,913 bytes, 170 pages. Browser download succeeded after retained CLI/FTP failures. Source bytes, OCR and page images remain private and are excluded from Git/archive.',9)
 para('PDF SHA-256: d74d935009796e32237ffce2b4be1211c112f0e151fd407b074fffecdbeab8cc. Printed source pages 109-122, 132-161 were read for the interfaces, special cases, stopping and verification; load-bearing algorithm/policy pages were visually checked.',9)
 c.showPage();start('What the implementation description says',2)
 para('Section 7.4, printed pages 120-122, switches between division polynomials and rational functions according to candidate-list size and memory. It does not give a 32-candidate acceptance cutoff. Factoring the kernel and factor-assisted x-coordinate methods are listed as trial ideas not yet used in the reported implementation.')
 para('Algorithm 10.5 ascends auxiliary primes until the literal product threshold m>=4sqrt(p). Section 10.4 explicitly says the practical implementation continues further to reduce the remaining possibilities. It supplies no fixed final continuation threshold. Thus the chart below is not original visitation or an upper bound on practical visitation.')
 c.drawImage(ImageReader(str(P/'first-phase.png')),37,285,width=538,height=222)
 y=256;sub('Consequences for the ell-199 pattern')
 para('The special CM routes do not distinguish any of the eleven omissions. None of the literal first-phase variants requires 199; the largest threshold is 197. Practical continuation could still reach it. The source does not supply the fitted 32/2048 gate or identify original caller settings.')
 para('Algorithms 7.3/7.6 normalize from supplied a,b and derivatives; they do not ask for a cube root of j. Their formula inspection is separate from earlier executed coordinate audits. Algorithm 11.2 verifies an order using the curve, twist and partial factorizations; no new native execution of that verifier is claimed.',9)
 c.showPage();start('Verification, custody and next source target',3)
 sub('Frozen two-method evaluation')
 para('One complete 21-row evaluation per arm, N=1: Python integer square classes and prime sieve; independent PARI/GP norm-form solutions and nextprime. Labels, seeds and UIDs do not influence arithmetic. The exact p,a,b,n and UID remain bound to the original cohort bytes.')
 para('Planned 2; attempted 2; completed 2; failed 0; timed out 0; excluded 0; resumed 0. Both arms run on shared macOS arm64, one thread. Diagnostic wall seconds: Python 0.038837, GP 0.038662. Counted outputs are exact; wall_valid=false and no performance comparison follows.')
 para('Unified export file verification passes. Archive extraction and fresh-directory replay repeat both methods, with RESULT.json, the all-21 CSV and both raw output vectors byte-identical. This is same-data validation, not a new independent cohort. All original controls and failures remain retained.')
 para('Protocol SHA-256: e3f1c92cd312df6e21fe9eefde92438f184382ea93d44d75887748077ae13b52. Full freeze/raw commit identities and input hashes are in report.md. Archive: 21,642 bytes; 23 sealed files; SHA-256: 66afd594f61224ee61937a663d044f7c7fb9684a8dd6b086c539e8515cd91ca9.',9)
 para('Canonical artifact HeadObject returned 403; exact bytes remain in Git under verified large-file-ok. No third-party source bytes are republished. The local LMFDB extraction source is public.av_fq_isog, ended 2026-10-19T16:45:49.243703+00:00; all four selected index manifests are complete.',9)
 sub('Why source random points cannot change this CM result')
 para('The cohort orders n are certified primes. Every nonzero point has order n. Special-CM candidate orders lie in the Hasse interval, whose width is smaller than n here; a different candidate cannot annihilate a nonzero point. Conditional on certified inputs and valid point generation, the negative class result precludes accidental special-order acceptance. This is a group-theoretic deduction, not a point-generator replay.',9)
 sub('The next implementation-specific documents')
 para('Printed page 163 sends practical implementation details to Markus Maurer (1994), Eine Implementierung des Algorithmus von Atkin zur Berechnung der Punktanzahl elliptischer Kurven uber endlichen Primkorpern, and Frank Lehmann (1994), Implementierung von Algorithmen zur Berechnung modularer Polynome und deren Anwendung im Algorithmus von Atkin. Their contents have not yet been obtained.',9)
 para('Recover those implementation details or the actual NIST/Reiter caller before attributing the ell-199 pattern. This bounded source check does not cover all CM fields, general endomorphism criteria, transfers over extensions, or a different implementation. The historical selector remains open.',9)
 c.showPage();c.save()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['figure','pdf']);mode=a.parse_args().mode
 if mode=='figure':figure()
 else:pdf()
