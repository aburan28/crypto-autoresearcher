"""Render recorded exact capacity counts; no new classifier evaluations."""
import argparse,csv,json,pathlib
P=pathlib.Path(__file__).resolve().parent

def figures():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 x=json.loads((P/'RESULT.json').read_text())['enumerator'];rows=list(csv.DictReader((P/'raw/level-coverage.csv').open()))
 fig,axs=plt.subplots(1,2,figsize=(10.7,4.5),gridspec_kw={'width_ratios':[1.25,1]})
 ax=axs[0];v=[x['full_robust_covered']/4480*100,x['full_possible_covered']/4480*100,x['endpoint_full_robust']/126*100];bars=ax.bar(range(3),v,color=['#235a82','#78a1bf','#596b86'],width=.62)
 for b,txt in zip(bars,['3,864 / 4,480','3,873 / 4,480','110 / 126']):ax.text(b.get_x()+b.get_width()/2,b.get_height()+1.5,txt,ha='center',fontsize=9)
 ax.set_xticks(range(3),['All labels\nrobust','All labels\npossible','Endpoints fixed\nrobust = possible'],fontsize=9);ax.set(ylim=(0,105),ylabel='Representable assignments (%)',title='Broad two-feature family');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
 ax=axs[1];ells=[int(r['ell']) for r in rows];counts=[int(r['covered_labelings']) for r in rows];ax.scatter(ells,counts,color=['#bf562b' if c else '#8b9ba4' for c in counts],s=[55 if c else 13 for c in counts]);ax.annotate('ell = 199\nonly observed labeling',xy=(199,1),xytext=(135,.65),arrowprops={'arrowstyle':'->','color':'#bf562b'},color='#93431f',fontsize=10);ax.set(xlim=(0,303),ylim=(-.08,1.2),yticks=[0,1],xlabel='Auxiliary prime ell (61 primes)',ylabel='Representable labels out of 4,480',title='Same-prime candidate + degree caps');ax.grid(alpha=.15)
 fig.text(.015,.015,'NIST-CLASSIFIER-CAPACITY-01. Fixed reused observations on 21 curves; complete reference populations.\nExact counts, no sampling uncertainty. Descriptive capacity only: labels and prior fits were visible when choosing the families.',fontsize=8)
 fig.subplots_adjust(left=.07,right=.98,top=.89,bottom=.24,wspace=.34);fig.savefig(P/'capacity.svg');fig.savefig(P/'capacity.png',dpi=180);plt.close(fig)
 f=P/'capacity.svg';f.write_text('\n'.join(l.rstrip() for l in f.read_text().splitlines())+'\n')

def pdf():
 from reportlab import rl_config
 rl_config.useA85=0
 from reportlab.pdfgen import canvas
 from reportlab.lib.colors import HexColor
 from reportlab.lib.utils import ImageReader
 import textwrap
 c=canvas.Canvas(str(P/'report.pdf'),pagesize=(612,792),invariant=1);c.setTitle('NIST selector: exact capacity calibration and period source recovery')
 y=0
 def start(title,page):
  nonlocal y
  c.setFillColor(HexColor('#173e59'));c.setFont('Helvetica-Bold',17);c.drawString(42,749,title);c.setFillColor(HexColor('#222222'));c.setFont('Helvetica',8);c.drawString(42,731,'NIST-CLASSIFIER-CAPACITY-01 | T-5518 | 2026-10-27 | observation report');c.setFont('Helvetica',8);c.drawRightString(570,25,str(page));y=704
 def para(t,size=10):
  nonlocal y
  c.setFont('Helvetica',size)
  for line in textwrap.wrap(t,width=100 if size==10 else 115):c.drawString(42,y,line);y-=14
  y-=9
 def sub(t):
  nonlocal y
  c.setFont('Helvetica-Bold',11);c.drawString(42,y,t);y-=21
 start('An exact fit with a selective narrow family',1)
 para('This report presents recorded observations and a source review. It changes no formal goal or hypothesis status. The actual historical curve selector remains unresolved.')
 para('The earlier ell-199 rule accepts all 10 published curves and excludes all 11 reconstructed omissions across six streams: known-degree positive-half eigenvalue candidate count <= 32 AND minimum predicted psi-199 factor degree <= 2048. The two numbers are posthoc representatives, not recovered constants.')
 sub('New exact capacity result')
 for t in ['Full family, robust: 3,864 / 4,480 alternative labelings represented (86.25%).','Full family, possible unknown completions: 3,873 / 4,480 represented.','With all stream endpoints fixed: robust = possible = 110 / 126 represented.','Narrow same-prime cap family: 1 / 4,480 and 1 / 126 represented.','That one labeling is the observed publication assignment, and only ell=199 fits.']:para(t)
 c.drawImage(ImageReader(str(P/'capacity.png')),35,111,width=542,height=228);c.setFont('Helvetica',8);c.drawString(42,92,'Counts are exhaustive within frozen families. The reference populations are not a model of historical choices.')
 c.showPage();start('What was checked, and what it establishes',2)
 sub('Fixed populations and model families')
 para('Every label assignment keeps the publication count in each exact field: choose(8,3) * choose(5,3) * choose(2,1) * choose(4,1) = 4,480. P-384 and P-521 singleton publications stay fixed. Preserving each final stream endpoint leaves 126 labels and fixes all P-224/P-256 decisions; only earlier 192/239-bit positions vary.')
 para('The full family uses 2,551 frozen complemented observation signatures, all 3,252,525 unordered pairs and all 16 truth functions: 52,040,400 cases. The narrow family enumerates 1,777 observed-value cap pairs across 61 primes, 3 through 293. No new feature, curve or point count was added.')
 sub('Verification and controls')
 para('Enumeration constructs truth-table output masks and explicit cap grids. The second algorithm enumerates all 2^21 masks to check population completeness, verifies positive witnesses rowwise, proves missing fits by pair compatibility, and checks each cap fit using the smallest rectangle containing positives. Both modes share one native binary, input parser and embedded fixtures; this is not an independent review or new cohort.')
 para('All 4,480 witness/absence rows and all 61 per-prime cap bits passed. The verifier made 2,003,555,400 pair checks for the 616 robust-noncovered labels. Original-label 16 pairs / 19 truth functions were independently recounted. Four-bin, XOR, identical-row collision, unknown and A/A fixtures passed before cohort processing.')
 sub('Complete execution and custody')
 r=[json.loads((P/'raw'/(a+'-receipt.json')).read_text()) for a in ['enumerate','verify']]
 para('Planned 2; attempted 2; completed 2; failed 0; timed out 0; excluded 0; resumed 0. Diagnostic wall seconds: enumeration %.3f, verification %.3f. Shared macOS arm64, one thread, Apple clang 17 -O3; clocks are not comparative endpoints.'%(r[0]['wall_seconds_diagnostic'],r[1]['wall_seconds_diagnostic']))
 para('Protocol frozen and pushed at 6b0655a18f54b823cf9c7157ef777db765034d1e before coverage. Raw records committed separately at ec6fd4be59 (full identity in report.md). Archive extraction, rebuild and both complete-mode replays passed, with all six result files byte-identical. Export validation passed.')
 para('Archive: 91,413 bytes; 31 sealed files. SHA-256: fd066dd45628fb85847be9078ae132fcfca1613df2569b953c4cac893f8d1392',9)
 para('Canonical object-store HeadObject returned 403; Git retains exact bytes under the verified large-file-ok PR exception. No remote-store or hosted-CI success is asserted.',9)
 c.showPage();start('Period source recovery and remaining gap',3)
 sub('A real pre-1997 account of resultant sign tests')
 para('Dewaghe, Calcul du nombre de points sur une courbe elliptique dans un corps fini, Lille thesis defended December 12, 1996, contains the later article topic in chapter 2. The resultant formulas were read and visually checked on printed pages 31, 32 and 38. The exact 1998 journal text has not been compared for revisions.')
 para('Theorem 5 handles Elkies ell=3 mod 4 with the odd-degree kernel factor. Corollary 3 handles an odd order modulo sign for ell=1 mod 4. Proposition 28 requires odd projective order e in its Atkin resultant shortcut. These are mathematical hypotheses, not criteria for accepting curves.')
 para('At ell=199, published P-224 has e=20 while omitted P-224 positions 1485 and 5736 have e=25. Requiring that Atkin shortcut therefore fails published/omitted controls. The conjugate kernel factor has degree e*(ell-1)/2: published 239-bit curves with e=40 construct degree 3960, despite smallest irreducible degree 440. A literal cap on that intermediate is different from the observed cap.')
 sub('Source identity and gaps')
 para('Couveignes-Dewaghe-Morain author PDF, first article page dated April 12, 1996, cites the December 1995 / January 1996 Dewaghe preprints and Muller 1994 / 1995 work. The date and bibliography were visually checked. Full source URLs, hashes and page references appear in SOURCE-REVIEW.md.',9)
 para('Muller original 1995 dissertation located: Saarland DOI 10.22028/D291-25721. Its catalog is readable, but direct PDF retrieval failed and the cached extraction is font-encoded. Its algorithms have not been read. No outgoing copy request was sent.',9)
 sub('Interpretation boundary and next discriminating check')
 para('The narrow family uniquely represents the observed labeling among these reference assignments; the broad family represents many alternatives. Neither fraction is a p-value, chance estimate or historical-choice probability. Families were chosen after earlier labels/fits were visible; endpoint conditioning fixes P-224/P-256. No held-out historical decisions were tested.')
 para('Retain ell=199 as a specific lead. Recover a dated caller or implementation that justifies the prime, splitting-degree mode and both resource quantities/bounds; then test its actual visitation and stopping sequence on all 21 identities. Inspected source material supplies no such caller or constants. The goal remains open.')
 c.showPage();c.save()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['figures','pdf']);mode=a.parse_args().mode
 if mode=='figures':figures()
 else:pdf()
