"""Render only recorded observations. Run --figures, then --pdf with ReportLab."""
import argparse,csv,json,pathlib,textwrap
D=pathlib.Path(__file__).resolve().parent

def data():return json.loads((D/'AUDIT.json').read_text()),list(csv.DictReader((D/'cohort-features.csv').open()))
def figures():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 audit,rows=data();cols=['power/j/3','roots/3','roots/5','roots/13','valuation_delta/3','valuation_delta/5'];labels=['j is a cube\nBoolean','rational roots\nell=3','rational roots\nell=5','rational roots\nell=13','v3(Delta_pi)\nvaluation','v5(Delta_pi)\nvaluation'];a=np.array([[int(r[k]) for k in cols] for r in rows]);norm=a/np.maximum(1,a.max(axis=0))
 fig,ax=plt.subplots(figsize=(9,9.4));ax.imshow(norm,cmap='Blues',vmin=0,vmax=1,aspect='auto');ax.set_xticks(range(len(cols)),labels,fontsize=9);ax.xaxis.tick_top();ax.tick_params(length=0);yn=[]
 for r in rows:yn.append(('publication ' if r['label']=='published' else 'omission ')+r['name'].replace('skip-','')+' / '+r['ordinal'] if r['label']=='published' else 'omission '+r['name'].split('-')[1]+' / '+r['ordinal'])
 ax.set_yticks(range(21),yn,fontsize=8.5)
 for tick,r in zip(ax.get_yticklabels(),rows):tick.set_color('#174d76' if r['label']=='published' else '#a65015')
 for i in range(21):
  for j in range(len(cols)):ax.text(j,i,str(a[i,j]),ha='center',va='center',fontsize=10,color='white' if norm[i,j]>.58 else '#162538')
 for y in [7.5,12.5,13.5,15.5,16.5]:ax.axhline(y,color='white',linewidth=2)
 ax.set_title('Fixed-cohort arithmetic and source-root observations',fontsize=13,pad=41);fig.text(.02,.016,'NIST-TWO-RULE-01 v2; 21 exact curves. Printed values are exact; color is scaled within each column.\nBlue row labels:10 publications; orange:11 reconstructed omissions. No statistical uncertainty or historical attribution.',fontsize=8)
 fig.subplots_adjust(left=.40,right=.99,top=.88,bottom=.075);fig.savefig(D/'cohort-features.svg');fig.savefig(D/'cohort-features.png',dpi=180);plt.close(fig)
 diagram={'nodes':[{'label':'21 fixed curves','detail':'10 publications +11 omissions'},{'label':'1,913 Boolean predicates','detail':'574 numeric/source columns'},{'label':'495 observed signatures','detail':'retain complement/source aliases'},{'label':'122,265 unordered pairs','detail':'all 16 truth tables =1,956,240'},{'label':'0 robust or possible fits','detail':'122,265 retained collision witnesses'}],'boundary':'This finite two-atom library only; historical selector remains unresolved.'};(D/'workflow.diagram.json').write_text(json.dumps(diagram,indent=2)+'\n')
 fig,ax=plt.subplots(figsize=(10,3.8));ax.axis('off')
 for i,n in enumerate(diagram['nodes']):
  x=.1+.2*i;ax.text(x,.62,'\n'.join(textwrap.wrap(n['label'],22))+'\n\n'+'\n'.join(textwrap.wrap(n['detail'],23)),ha='center',va='center',fontsize=8,bbox={'boxstyle':'round,pad=.6','facecolor':'#eaf1f6','edgecolor':'#28506c'},transform=ax.transAxes)
  if i<4:ax.annotate('',xy=(x+.13,.62),xytext=(x+.075,.62),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#28506c'})
 ax.text(.5,.22,'Python integer arithmetic + bitset bins  /  independent PARI arithmetic + rowwise truth tables\nBoth implementations agree on every feature, fit and collision witness.',ha='center',fontsize=10,transform=ax.transAxes);ax.text(.5,.06,diagram['boundary'],ha='center',fontsize=10,transform=ax.transAxes);fig.tight_layout();fig.savefig(D/'workflow.svg');fig.savefig(D/'workflow.png',dpi=180);plt.close(fig)
 for f in D.glob('*.svg'):f.write_text('\n'.join(x.rstrip() for x in f.read_text().splitlines())+'\n')

def markdown():
 b=json.loads((D/'BUNDLE.json').read_text());t='''# Two-predicate audit of the fixed NIST/ANSI cohort — 2026-10-27

These are exact observations and scoped comparisons. The historical selector remains unresolved; this report changes no formal hypothesis or goal status.

**Measured/derived result:** 1,913 frozen Boolean predicates from 574 numeric/source columns give495 distinct complemented observation signatures on21 exact curve identities. Both implementations evaluated122,265 unordered signature pairs and all 16 truth tables per pair (1,956,240 distinct pair/function cases). There are **zero robust fits and zero possible fits**, including the explicit single-signature audit. Every pair has a publication/omission collision witness. No arbitrary pair of complex rules is excluded.

The ten publications and eleven reconstructed omissions cover all six timestamp streams. Omissions are not documented historical rejection events. Exact models and seeds are bound in [inputs.json](inputs.json), [rows.json](rows.json), [IDENTITY-BINDING.json](IDENTITY-BINDING.json) and [cohort-features.csv](cohort-features.csv). All 1,281 imported fibers also match the exact field and independently reconstructed j, not just a field-size alias. The actual rows-byte SHA is e8d6a874e3dc77970c88957f4bca075a0cc7a431dd8bcb25e5c5d7bcba6eeb0f.

## Fixed search scope

Read [LIBRARY.md](LIBRARY.md) and the frozen [v1 protocol](experiment.protocol.json), with the wrapper-only [v2 amendment](attempt-02/experiment.protocol.json). Features cover power residues of b,c,j,j−1728,E6 and discriminants; field residues and order shape; local CM-field characters and Frobenius-discriminant valuations through 293; all 61 rational-root table levels; source ECPP status and integer costs; twist observations; strict seed expansions; and four source-based sign-loss faults. No exact IDs, seed bytes, publication/base-point metadata or timing features enter the classifier. Global CM conductor values are not silently substituted for local valuations or actual endomorphism conductors.

All16 Boolean functions cover AND, OR, XOR, complements, constants and degenerate one-input rules. Aliases that coincide on these21 curves are not claimed universally equivalent. Unknowns stay unknown. A robust fit must work for every completion; a possible fit needs only a rowwise favorable completion, potentially without a jointly realizable mathematical completion. Both fit sets are empty.

The source imports and labels were already visible; this is exploratory fixed-cohort analysis. The library and code were frozen and pushed before fitting, not preregistered before discovery of the underlying observations. There is no p-value, held-out prediction, novelty or historical-use claim.

## Specific curve observations

The P-224 pattern survives: all three omissions have non-cubic j and one rational degree3 parameter root; the publication has cubic j and four roots. Its Frobenius-discriminant 3-adic valuation is3 rather than1. A second predicate from this library cannot extend that lead to an exact six-stream classifier. The two signs of b over P-224 are isomorphic models and are not counted twice.

All 21 j−1728 values are fourth powers; that supplies no exclusion. The P-256 publication and omission both have non-cubic j and identical local ramification/conductor behavior at3. The previous exact P-256 factorization gives f_pi=f_E=1 on both. The published P-224 curve is the f_pi=3 case. A factor3 of D_K is ramification, not conductor3. Local CM characters here are exact without determining a complete global D_K or the P384 endomorphism order.

For odd ell, Delta_pi=ell^v*u gives (D_K/ell)=0 when v is odd, otherwise (u/ell). This follows by removing the square conductor factor. With odd traces, Delta_pi and f_pi are odd, giving (D_K/2)=(Delta_pi/2). Python modular exponentiation and GP Kronecker arithmetic agree on every declared feature. No transfer map, subgroup transport or endomorphism efficiency follows from these characters.

![Full cohort feature observations](cohort-features.svg)

## Execution, controls and retained failures

Freeze commits:8a02d2e055251b8fd0c6c142c7433bd57993b912 (v1) and b9816392a140d245b9079de67b05c392e7d39da0 (v2). v2 protocol SHA2797d0041be4fc65913b2ecd809f148ff2a87fe64a318f4cc245744bc72bd60f. Exact command is `python3 run.py` in the extracted attempt 02 directory, following the repository checkpoint gate. Runtime is shared macOS arm64; GP binary SHA1b3464452036a97072a2514f5094bb49188e2ee3089a61514443494f4875ceb5. No timing comparison is made.

Across the two original attempts, four implementation evaluations were attempted: three succeeded and one stopped. In attempt 01 Python completed; GP returned 0 and 21 feature vectors, but the wrapper rejected its stack-size warning. Attempt 02 whitelisted only that exact warning, repeated identical inputs/library and completed both arms. The failed attempt, original code, stdout, stderr, process receipts, invalid export and corrected exports are retained. Pre-fit duplicate-import and protocol-schema corrections are recorded; none produced a classifier fit. The corrected export represents the failed terminal execution as outcome_class=completed per checker semantics, with status=failed preserved.

Both final arms pass the embedded XOR positive, indistinguishable-vector negative, unknown-value and A/A controls. XOR requires both predicates; the collision control has no fit; the unknown control has possible but no robust fits. One entire matrix is one protocol instance per arm, N=1, with internal complete enumeration. Both exports pass file verification. Final diagnostic wall times are 0.373s and 15.355s, user CPU 0.347s and 15.136s; these are process diagnostics on a shared desktop, not comparative performance evidence. The archive was independently extracted and both implementations rerun successfully after relocation; these are validation replays, not additional independent cohorts.

![Frozen search and scope](workflow.svg)

## Delivery and replay

The 70-file sealed archive is `evidence.tar.zst`, SHA ARCHIVE_SHA, ARCHIVE_BYTES bytes. [BUNDLE.json](BUNDLE.json) binds it. The source-feature matrix, all aliases, complete outputs and 122,265 little-endian collision witnesses are retained. Witness encoding is documented in LIBRARY.md. The parser/auditor agrees on every one. Original source packages, emails, papers and runtime binaries are excluded from redistribution, with source paths and hashes retained.

```sh
zstd -dc evidence.tar.zst | tar -xf -
cd evidence/attempt-02
python3 -B run.py
```

The producer uses embedded imports and performs no source download. Python3.14 and PARI/GP2.17.3 are the pinned original runtimes; GP path is `/opt/homebrew/bin/gp`. Run from a fresh extraction to preserve earlier results. Both frozen protocols, every raw process receipt and original first attempt remain inside the archive. Portable replay validation is recorded in PORTABLE-REPLAY.json.

Canonical artifact-store delivery returned HeadObject403; exact archive bytes are retained in Git under PR2602's verified large-file-ok exception. No object-store or CI success is implied. The existing immutable-record merge conflicts remain separate from these calculations.

## Sources and remaining question

Retrieved 2026-10-27: [Valsorda's fixed cohort and unresolved extra criterion](https://words.filippo.io/seeds-solved/); [Anthropic's RNG reconstruction and Solinas/Reiter correspondence](https://www.anthropic.com/research/ecdsa-curve-origins). Internal hashed receipts supply the all 61 modular-table roots, full-cohort ECPP observations, twist observations, seed variants and four later-source fault models. These imports are re-used observations, not new executions of the original 1997 caller. Complete global discriminants and actual endomorphism-ring results retain their earlier individual certification limits.

No linked canonical frontier graph changes: the existing CCR, y-matching and CM source reports retain their sealed scope. This round adds this exact finite-library diagram and observation figure only. The problem record stays open. The next discriminating evidence is a dated original caller/validation requirement or a separately frozen, source-motivated field-dependent mechanism tested on all 21 identities. A more complex classifier built solely from these labels would still need an independent historical prediction before it could explain what was used.
'''
 t=t.replace('ARCHIVE_SHA',b['sha256']).replace('ARCHIVE_BYTES',str(b['bytes']));(D/'report.md').write_text(t)

def pdf():
 from reportlab.pdfgen import canvas
 from reportlab.lib import colors
 from reportlab.lib.utils import ImageReader
 from reportlab import rl_config
 rl_config.useA85=0
 c=canvas.Canvas(str(D/'report.pdf'),pagesize=(595.28,841.89),invariant=1);W,H=595.28,841.89
 def footer(page):
  c.setStrokeColor(colors.HexColor('#d0dae2'));c.line(42,38,W-42,38);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#425568'));c.drawString(42,25,'NIST-TWO-RULE-01 v2 | fixed 21 cohort | 2026-10-27');c.drawRightString(W-42,25,str(page))
 def title(s):c.setFillColor(colors.HexColor('#143c58'));c.setFont('Helvetica-Bold',19);c.drawString(42,H-54,s)
 def para(s,y,size=10.5,width=91):
  c.setFont('Helvetica',size);c.setFillColor(colors.HexColor('#203243'))
  for line in textwrap.wrap(s,width=width):c.drawString(42,y,line);y-=size*1.40
  return y-11
 title('Two predicates: complete fixed-library audit');y=H-86
 y=para('Observation report. The historical selector remains unresolved. Exact computation on all 11 reconstructed omissions and 10 publications across six streams.',y)
 c.setFillColor(colors.HexColor('#e8f1f7'));c.roundRect(42,y-80,W-84,83,8,fill=1,stroke=0);c.setFillColor(colors.HexColor('#143c58'));c.setFont('Helvetica-Bold',22);c.drawString(56,y-28,'0 exact fits');c.setFont('Helvetica',11);c.drawString(56,y-51,'122,265 predicate pairs x16 functions =1,956,240 cases');c.drawString(56,y-69,'Both robust and favorable-unknown fit sets are empty.');y-=108
 y=para('The 1,913 Boolean atoms from 574 numeric/source columns reduce to 495 complemented observation signatures. Every original alias and every pair collision witness is retained. Single-signature rules also give zero fits.',y)
 y=para('The library covers j/coefficient/discriminant power residues, local CM splitting and conductor valuations, source rational-isogeny roots at 61 levels through 293, twist observations, source ECPP flags and costs, seed expansions and four sign-loss models.',y)
 y=para('The Python integer/bitset implementation and independent PARI arithmetic/rowwise truth-table implementation agree on every feature, fit and collision witness. Embedded positive XOR, negative collision, unknown-value and A/A controls all pass.',y)
 y=para('Attempt 01 retained one completed search and one verifier stop: its wrapper rejected a benign GP stack warning. Attempt 02 corrected only that exact warning check, then completed both arms. Original logs, frozen source and failed/corrected exports are retained.',y)
 y=para('Scope: this excludes Boolean functions of two atoms in the declared library only. It does not exclude arbitrary complicated rules, field-dependent paths, undocumented stopping logic or another historical implementation. Labels and source observations were already visible; no statistical or historical attribution claim.',y)
 c.drawImage(str(D/'workflow.png'),42,61,width=W-84,height=194,preserveAspectRatio=True,anchor='c');footer(1);c.showPage()
 title('Curve observations across all six streams');c.drawImage(str(D/'cohort-features.png'),26,112,width=543,height=634,preserveAspectRatio=True,anchor='c');y=104;y=para('P-224: j is non-cubic on all three omissions and cubic on the publication. No second library atom extends this pattern to an exact six-stream classifier.',y,size=10,width=96);footer(2);c.showPage()
 title('CM distinctions, custody and replay');y=H-88
 y=para('P-256: both the published and omitted curves have exact Frobenius conductor f_pi=1, forcing actual conductor f_E=1. The published P-224 curve has f_pi=3. Ramification of 3 in D_K is different from conductor divisibility.',y)
 y=para('Local CM-field characters are obtained exactly without full global factorization: for odd ell write Delta_pi=ell^v*u. Odd v gives ramification; even v gives the Legendre symbol of u. Odd traces give (D_K/2)=(Delta_pi/2). No full P384 endomorphism order or transfer advantage is inferred.',y)
 y=para('All 21 j-1728 values are fourth powers. P-256 publication and omission both have non-cubic j. Root/coefficient sign choices do not supply the missing class exclusion. These are observations, not historical acceptance requirements.',y)
 y=para('Custody: 70 sealed files. Archive SHA256 '+json.loads((D/'BUNDLE.json').read_text())['sha256']+'. Source imports are bound to exact UIDs, models and seeds; all 1,281 fibers match p and j. Original third-party source packages are not redistributed.',y,size=9.5,width=101)
 y=para('Frozen source commits: 8a02d2e055251b8fd0c6c142c7433bd57993b912 and b9816392a140d245b9079de67b05c392e7d39da0. Protocol v2 SHA256: 2797d0041be4fc65913b2ecd809f148ff2a87fe64a318f4cc245744bc72bd60f. Both exports pass full file verification.',y,size=9.5,width=101)
 y=para('Replay: extract evidence.tar.zst into a fresh directory, enter evidence/attempt-02, then run python3 -B run.py with Python3.14 and /opt/homebrew/bin/gp. A complete decompression/relocation replay passed. Replay counts are validation, not new independent cohort evidence.',y)
 y=para('Canonical artifact delivery returned HeadObject403; exact bytes are retained in Git under the existing PR2602 exception. PR merge conflicts remain unresolved. No object-store or CI success is asserted.',y)
 y=para('Primary sources retrieved 2026-10-27: words.filippo.io/seeds-solved/ and anthropic.com/research/ecdsa-curve-origins. Internal source bindings and limitations are in inputs.json and LIBRARY.md; full evidence and editable figures accompany report.md.',y)
 y=para('Next discriminating evidence: an authenticated dated caller or validation requirement, or a separately frozen field-dependent source mechanism covering every publication and omission. More elaborate label-fitted classifiers alone cannot establish historical use.',y)
 footer(3);c.save()

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--figures',action='store_true');a.add_argument('--pdf',action='store_true');x=a.parse_args()
 if x.figures:figures();markdown()
 if x.pdf:pdf()
