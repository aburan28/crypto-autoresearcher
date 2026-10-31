"""Render recorded signed-action profiles and separately frozen policy checks."""
import argparse,csv,json,pathlib,textwrap,re
D=pathlib.Path(__file__).resolve().parent

def human(t):
 prefixes=['all','All','both','Both','at','At','through','below','before','from','degree','degrees','order','ranks','have','adds','yields','exact','Exact','are','cap','most','and','or','the','The','new','prior','generate','give','first','only','Only','published','Published','omitted','Omitted','Schoof','Morain','Dewaghe','Mueller','LiDIA','doi','reject','retains','rational','support','not','original','allocates','sign','primes','reached']
 for word in prefixes:t=re.sub(r'\b'+word+r'(?=\d)',word+' ',t)
 t=re.sub(r'\bprime(?=\d+\b)','prime ',t)
 t=re.sub(r',(?=[A-Za-z])',', ',t);t=re.sub(r'(?<=[A-Za-z]),(?=\d)',', ',t);t=re.sub(r':(?=[A-Za-z0-9])',': ',t);t=re.sub(r';(?=\S)','; ',t)
 for a,b in [('P224','P-224'),('P192','P-192'),('P256','P-256'),('P384','P-384'),('P521','P-521')]:t=t.replace(a,b)
 t=t.replace('.3,130,260','. 3,130,260').replace('.16 pairs','. 16 pairs').replace('.32/2048','. 32/2048').replace('andP-','and P-')
 return t

def read():return json.loads((D/'AUDIT.json').read_text()),list(csv.DictReader((D/'ell199.csv').open())),json.loads((D/'policy-check-01/RESULT.json').read_text())
def figures():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Rectangle
 audit,rows,policy=read();fig,axs=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[1.4,1]});ax=axs[0];ax.add_patch(Rectangle((-6,0),38,2048,facecolor='#edf7ef',edgecolor='none'));groups={}
 for r in rows:groups.setdefault((int(r['known_candidates_max']),int(r['min_factor_degree']),r['label']),[]).append(int(r['index']))
 for (x,y,label),ids in groups.items():
  color='#2166a0' if label=='published' else '#c45a24';ax.scatter([x],[y],s=45+18*(len(ids)-1),color=color,edgecolors='white',linewidth=.6,zorder=3);dy=55 if y<1950 else (-125 if y==1980 else 60);
  if x!=60:ax.annotate(','.join(map(str,ids)),(x,y),xytext=(x+2,y+dy),fontsize=8,color=color)
 ax.annotate('7 omitted Elkies cases\nIDs4,5,6,9,11,14,17',xy=(60,55),xytext=(44,500),fontsize=8,color='#c45a24',arrowprops={'arrowstyle':'->','color':'#c45a24'})
 ax.axvline(32,ls='--',color='#526b55');ax.axhline(2048,ls='--',color='#526b55');ax.text(33,2500,'candidate cap 32',fontsize=8,color='#526b55');ax.text(35,2080,'degree cap 2048',fontsize=8,color='#526b55');ax.set(xlim=(-6,72),ylim=(-80,2750),xlabel='Known-degree source candidate count at ell199',ylabel='Predicted minimum factor degree of psi199',title='Exact 21-curve separator at ell199');ax.grid(alpha=.15)
 ax=axs[1];xs=range(3);pub=[x['published_retained'] for x in policy['policy_arms']];omit=[x['omitted_retained'] for x in policy['policy_arms']];ax.bar([i-.17 for i in xs],pub,width=.32,label='publications retained',color='#2166a0');ax.bar([i+.17 for i in xs],omit,width=.32,label='omissions retained',color='#c45a24')
 for i in xs:
  ax.text(i-.17,pub[i]+.15,str(pub[i]),ha='center',fontsize=10);ax.text(i+.17,omit[i]+.15,str(omit[i]),ha='center',fontsize=10)
 ax.set_xticks(list(xs),['ell199\nknown degree','all ell<=199\nknown degree','ell199\nunknown degree'],fontsize=8);ax.set(ylim=(0,11.5),ylabel='Curves retained (count)',title='The literal resource-policy checks');ax.legend(fontsize=8,loc='upper right');ax.grid(axis='y',alpha=.15)
 fig.text(.02,.015,'NIST-SIGNED-FROBENIUS-01 + NIST-ELL199-POLICY-01. Exact fixed N=21; no sampling uncertainty.\nLeft labels are row indices in ell199.csv. Caps32/2048 are posthoc choices; factor degrees are derived, not full-cohort polynomial factorizations.',fontsize=8);fig.subplots_adjust(left=.07,right=.98,top=.9,bottom=.20,wspace=.35);fig.savefig(D/'separator-and-policies.svg');fig.savefig(D/'separator-and-policies.png',dpi=180);plt.close(fig)
 diagram={'nodes':['Certified p,n and explicit models','1281 signed Frobenius profiles: two independent methods','50,084,160 new pair/function cases:16 pairs,19 fits','Policy checks: exact at199; uniform and unknown-mode failures'],'scope':'Original caller, caps and199 requirement remain unestablished.'};(D/'workflow.diagram.json').write_text(json.dumps(diagram,indent=2)+'\n');fig,ax=plt.subplots(figsize=(10,2.8));ax.axis('off')
 for i,txt in enumerate(diagram['nodes']):
  x=.12+.25*i;ax.text(x,.65,'\n'.join(textwrap.wrap(human(txt),26)),fontsize=9,ha='center',va='center',bbox={'boxstyle':'round,pad=.7','facecolor':'#ecf2f6','edgecolor':'#315d7b'},transform=ax.transAxes)
  if i<3:ax.annotate('',xy=(x+.16,.65),xytext=(x+.10,.65),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#315d7b'})
 ax.text(.5,.13,diagram['scope'],ha='center',fontsize=10,transform=ax.transAxes);fig.tight_layout();fig.savefig(D/'workflow.svg');fig.savefig(D/'workflow.png',dpi=180);plt.close(fig)
 for p in D.glob('*.svg'):p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')

def markdown():
 b=json.loads((D/'BUNDLE.json').read_text());text='''# Signed Frobenius: an exact two-rule separator and its source limits

2026-10-27. Observation report; historical selector remains unresolved. This round adds exact evidence and changes no formal goal/hypothesis status.

**Observed:** a two-predicate separator at auxiliary prime199 retains all10 publications and excludes all11 reconstructed omissions across all six streams. It uses a source-derived eigenvalue candidate-list size and the minimum irreducible-factor degree predicted for the199-division polynomial. The caps32/2048 are posthoc representatives of a range, not recovered historical constants.

Let C199 be the maximum positive-half candidate-list length across the two stable eigenlines, assuming the projective splitting degree is known. C199=0 on the nonsplit branch because that source eigenvalue list is skipped. Let D199 be the smallest predicted irreducible factor degree of psi199. The observed classifier accepts exactly when **C199<=32 and D199<=2048**.

| Cohort subset at199 | Count | Candidate-list size | Minimum psi199 factor degree |
|---|---:|---|---|
| Published Elkies cases |4|at most20|below2048|
| Published Atkin cases |6|0, list skipped|at most1980|
| Omitted Elkies cases |7|60|below2048|
| Omitted Atkin cases |4|0, list skipped|2200 or2475|

Any candidate cap from20 through59 and degree cap from1980 through2199 gives the same fixed-cohort classification. The power-of-two pair32/2048 is therefore not uniquely identified. All exact models/seeds/UIDs are in prior-rows.json; [ell199.csv](ell199.csv) contains every199 observation and acceptance bit. Omissions are reconstructed positions, not documented original rejection events.

![Exact separator and policy checks](separator-and-policies.svg)

## Complete search and controls

Both independent arithmetic implementations agree on all1281 cells:21 curves x61 odd primes3 through293. The native method uses2x2 matrix orders and fixed-point divisor inversion. The independent GP method uses eigenvalue orders and separate split/nonsplit/scalar/Jordan cycle formulas. Exactly three cells need direct scalarity tests beyond trace/determinant: two239-bit cells at5 and publishedP224 at3. The native affine quotient and independent formal division-polynomial derivative maps agree. Differentiate before reduction.

The conjugacy counts are673 nonsplit,574 split,33 Jordan and1 scalar. The scalar cell is publishedP224 at3: Frobenius=-I, with full order2, order modulo global sign1, projective order1. Its quadratic twist consequently has full rational3-torsion. The three omittedP224 curves have non-scalar Jordan action at3. This gives a concrete torsion meaning of the earlier cube/splitting pattern on this cohort; no universal j-cube equivalence or historical requirement follows.

Controls distinguish +I,-I,Jordan and nonsplit actions. Native independently counts the small models and factors their division polynomials; GP independently counts the controls and computes the corresponding orders. Expected(full,x,projective) orders are(1,1,1),(2,1,1),(3,3,3),(48,24,8). A/A, singular and wrong-order controls pass. Local LMFDB classes1.7.b,1.7.ab,1.7.e,1.5.d are provenance for classes only, not exact models. Sourcepublic.av_fq_isog extraction ended2026-10-19T16:45:49.243703+00:00; explicit control equations, fields and counts are in arithmetic.py and LMFDB-controls.json. The indexes do not cover the cryptographic fields.

The new1313 columns generate6680 Boolean atoms. With the prior1913 atoms there are2551 distinct complemented observation signatures,2056 new to this round. The search evaluates only pairs involving a new-only signature:3,130,260 pairs and50,084,160 truth tables. Old-old pairs reuse the previous complete zero-fit census. Bitset and rowwise enumeration agree on all16 fitting signature pairs,19 complete truth tables and every collision witness. New single-signature fits:zero. All fits and every alias are retained unranked in [ALL-FITS.json](ALL-FITS.json); no other fit is silently discarded. There are3,130,244 nonfit pair witnesses and16 fit markers. Duplicate truth-table possibilities sometimes differ only on bins absent from this cohort.

All source observations and labels were already visible. The generation rules/code were frozen before new arithmetic and pair fitting; this is exploratory exact computation, not a p-value or held-out historical prediction. The source comparison counts are positive-half candidate-list metrics, not field-operation costs or wall time. Factor-degree multisets are derived from the independently checked linear action, not1281 newly factored division polynomials.

## Test of the resource-policy explanation

The separate follow-up was frozen after seeing the new exact-fit results. It fixes caps32/2048 and tests the domain/mode alternatives without retuning:

| Policy | Publications retained | Omissions retained |
|---|---:|---:|
| At199; splitting degree known |10|0|
| Every recorded prime through199; degree known |0|0|
| At199; splitting degree unknown |6|0|

The unknown-degree variant loses prime239v2,prime192v1,prime192v2 andprime256v1. The uniform variant loses every publication, starting at primes67 through83. All exact failing cells are in policy-check-01/RESULT.json. These failures test a particular resource-policy interpretation; they do not negate the199 observation.

The later full-counter replay reached199 or higher for onlyP384 andP521. All11 omission replays stopped below199; even publishedP224 stopped at197. Consequently an at199 callback cannot cause those omissions in that particular measured replay. The original1997 caller may have differed, but no artifact currently establishes a mandatory199 test.

Candidate count is not comparison rank. Omitted239/2863 and256/876 each have60 candidates but correct positive-half ranks3 or8 at199. A32-candidate-position timeout would admit either, rather than explaining its omission. The recovered source allocates100 slots at199, not32. A hypothetical older fixed32-entry buffer remains unestablished.

Minimum irreducible-factor degree is also not every intermediate polynomial degree. In the period account, a conjugate factor can have degree r*(ell-1)/2. Published239v1,239v3 andP521 have r199=40, producing degree3960 by that construction despite minimum irreducible degrees440,440,120. A hard2048 bound on all intermediate polynomials therefore fails those controls. Read [SOURCE-QUALIFICATION.md](SOURCE-QUALIFICATION.md) for the exact distinctions.

![Data and inference boundary](workflow.svg)

## Source and chronology

Primary retrieved sources:[Schoof1995](https://www.numdam.org/article/JTNB_1995__7_1_219_0.pdf), sections6-8, and[Morain1995](https://www.numdam.org/article/JTNB_1995__7_1_255_0.pdf), sections3.4-3.6 and bibliography. Morain cites Mueller October1994 and Dewaghe December1994 works in preparation. That establishes contemporary work, not identity with a later routine or use by the original NIST/Reiter caller. A1998 publication date alone cannot date when the underlying idea became available. Full Dewaghe1998 text remained inaccessible via AMS403; no algorithmic detail is inferred from its abstract. The Lercier/Morain author mirror timed out. Source code inspected is the explicitly later LiDIA23dac491 lineage; exact function-file hashes are in SOURCE.json. No retrieved source prescribes32,2048 or a mandatory199 gate.

## Execution, custody and replay

Main frozen code commit14879cb3754b2518ebfd50ff0d655cd6efe89310; protocol SHA7739aeed6fe205c3273d68e02156e98907897b63c8188689c1bf9e4f7eda1b8c. Policy freeze commit51e096610846 (full commit bound in its export); protocol SHAd7f20c7aada947521a45554110ac7814397023adc6c67a3187891361bfd339ab. Main execution: pinned python-flint0.9.0 interpreter invokes run.py; GP2.17.3 is /opt/homebrew/bin/gp. Shared macOS arm64, exact single-thread arithmetic; no timing claim. Two arithmetic producers, one classifier analysis and one shared policy process completed; exports represent two arithmetic whole-matrix instances plus three logical policy instances. The policy arms share a process and have no per-arm clock. Both exports pass file verification. No scientific producer/control failure occurred in this round; preliminary catalog SQL/read-path errors did not produce mathematical observations.

Archive:evidence.tar.zst, SHA ARCHIVE_SHA, ARCHIVE_BYTES bytes,54 sealed files. BUNDLE.json seals it and the payload manifest. It retains all native/GP outputs, predictions, candidate lists/ranks, source imports, every fit/witness, both protocols and both exports. Original third-party source packages, PDFs and runtime binaries are excluded. Canonical artifact upload returned HeadObject403; exact bytes remain in Git under PR2602's verified large-file-ok exception. No object-store or CI success is implied.

For fresh full replay, extract and run with the pinned flint Python:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/run.py
python3 -B evidence/policy-check-01/policy.py
```

The public verify_archive.py offers a shorter relocation validation: it hashes every sealed file, reruns both1281-cell arithmetic methods, recomputes all bitset pairs and policy results, and compares them with the original complete rowwise results/witnesses. It does not repeat the expensive rowwise pair enumeration. PORTABLE-REPLAY.json records its exact scope. These are same-input validation replays, not independent cohorts.

No canonical frontier graph or formal hypothesis status changes. Earlier sealed graphs retain their scope. This round adds the separator/policy figure and inference diagram and links the open selector problem. The next discriminating evidence is a dated original requirement/caller, or a source-backed mechanism explaining why199 is mandatory, which degree mode was used and what the two resource limits actually constrained. An exact retrospective classifier alone does not establish the criteria they used.
'''
 text=text.replace('ARCHIVE_SHA',b['sha256']).replace('ARCHIVE_BYTES',str(b['bytes']))
 for a,z in [('all10','all 10'),('all11','all 11'),('all16','all 16'),('all1281','all 1281'),('all21','all 21'),('Both1281','Both 1281'),('both1281','both 1281'),('new1313','new 1313'),('prior1913','prior 1913'),('generate6680','generate 6680'),('are2551','are 2551'),(',2056',', 2056'),('are673','are 673'),('newly1281','newly 1281'),('a1998','a 1998'),('A1998','A 1998'),('at199','at 199'),('At199','At 199'),('Atkin cases |','Atkin cases |'),('No1281','No 1281'),('No32','No 32'),('a32','a 32'),('A32','A 32'),('A2048','A 2048'),('hard2048','hard 2048'),('all61','all 61'),('and50,084','and 50,084'),('all3,130','all 3,130'),('No scientific','No scientific')]:text=text.replace(a,z)
 (D/'report.md').write_text(human(text))

def pdf():
 from reportlab.pdfgen import canvas
 from reportlab.lib import colors
 from reportlab import rl_config
 rl_config.useA85=0;c=canvas.Canvas(str(D/'report.pdf'),pagesize=(595.28,841.89),invariant=1);W,H=595.28,841.89;a,rows,policy=read()
 def foot(n):c.setStrokeColor(colors.HexColor('#cbd7df'));c.line(42,38,W-42,38);c.setFillColor(colors.HexColor('#415b6b'));c.setFont('Helvetica',8);c.drawString(42,25,'NIST-SIGNED-FROBENIUS-01 | exact 21 cohort | 2026-10-27');c.drawRightString(W-42,25,str(n))
 def title(t):t=human(t);c.setFillColor(colors.HexColor('#153f5a'));c.setFont('Helvetica-Bold',18);c.drawString(42,H-54,t)
 def para(t,y,size=10.5,width=91):
  t=human(t);c.setFont('Helvetica',size);c.setFillColor(colors.HexColor('#203849'))
  for line in textwrap.wrap(t,width=width):c.drawString(42,y,line);y-=size*1.4
  return y-10
 title('An exact separator, with source limits');y=H-88
 y=para('Observed: at auxiliary prime199, two predicates retain all10 publications and reject all11 omissions across six streams. Historical use remains unestablished.',y)
 c.setFillColor(colors.HexColor('#edf7ef'));c.roundRect(42,y-86,W-84,90,8,fill=1,stroke=0);c.setFillColor(colors.HexColor('#205d35'));c.setFont('Helvetica-Bold',15);c.drawString(55,y-23,'Known-degree candidate-list size <=32');c.drawString(55,y-48,'AND minimum psi199 factor degree <=2048');c.setFont('Helvetica',10);c.drawString(55,y-69,'Posthoc representative caps; the exact constants are not uniquely identified.');y-=112
 y=para('Seven omitted Elkies cases have60 candidates; the four omitted Atkin cases have predicted minimum factor degrees2200 or2475. Published Elkies cases have at most20 candidates; published Atkin cases have degree at most1980.',y)
 y=para('The prior library found no two-atom fit. The signed-action extension adds6680 predicates and now yields16 fitting signature pairs,19 truth tables. Both independent arithmetic and complete truth-table implementations agree. All fits are retained.',y)
 c.drawImage(str(D/'separator-and-policies.png'),28,190,width=W-56,height=250,preserveAspectRatio=True,anchor='c');y=167
 y=para('The same caps applied uniformly through199 reject every publication. Unknown splitting-degree mode at199 rejects four publications. The later counter replay stopped below199 for all eleven omissions. These are direct limits on a resource-policy explanation.',y,size=10.5,width=92)
 foot(1);c.showPage()
 title('Every curve at auxiliary prime199');y=H-88;y=para('P=published; O=omitted. S=split/Elkies; A=nonsplit/Atkin. R is projective order; F is full signed order; C is known-degree candidate count; D is minimum predicted division-polynomial factor degree.',y,size=9.5,width=102)
 widths=[20,198,25,48,65,60,70];heads=['ID','Curve / ordinal','Type','R','F','C','D'];xs=[42]
 for w in widths:xs.append(xs[-1]+w)
 c.setFillColor(colors.HexColor('#e8eff4'));c.rect(42,y-8,W-84,23,fill=1,stroke=0);c.setFont('Helvetica-Bold',9);c.setFillColor(colors.HexColor('#153f5a'))
 for xx,h in zip(xs,heads):c.drawString(xx+3,y,h)
 y-=27
 for r in rows:
  vals=[r['index'],('P ' if r['label']=='published' else 'O ')+r['name'], 'S' if r['kind']=='split' else 'A',r['projective_order'],r['full_order'],r['known_candidates_max'],r['min_factor_degree']];c.setFillColor(colors.HexColor('#2166a0' if r['label']=='published' else '#b45223'));c.setFont('Helvetica',8.8)
  for xx,v in zip(xs,vals):c.drawString(xx+3,y,str(v))
  y-=21
 y-=12;y=para('Exact field/model/order/seed identities and full UIDs are in prior-rows.json; all199 values are in ell199.csv. Nonsplit cases have C=0 because that source eigenvalue list is skipped. D is derived from the signed action, not newly factored here.',y,size=10,width=96)
 y=para('Every candidate cap20..59 paired with every degree cap1980..2199 gives the same observed split.32/2048 are convenient examples, not recovered constants. No omitted position is asserted to have been visited by the original program.',y,size=10,width=96)
 foot(2);c.showPage()
 title('The policy checks and source obstructions');y=H-87
 for arm in policy['policy_arms']:
  txt={'at199_known':'At199,known degree:10 publications retained;0 omissions retained.','all_le199_known':'Uniform through199,known degree:0 publications retained;0 omissions retained.','at199_unknown':'At199,unknown degree:6 publications retained;0 omissions retained.'}[arm['arm']];y=para(txt,y,size=11,width=87)
 y=para('Unknown-degree mode loses prime239v2,prime192v1,prime192v2 andprime256v1. The uniform caps fail every publication, first at auxiliary primes67 through83. The original degree mode and199 requirement are unestablished.',y)
 y=para('In the later native-counter observations, all11 omissions stopped before199. Only the P384/P521 controls reached199 or later; published P224 stopped at197. An at199 callback cannot explain those omission decisions in that replay. This does not establish original1997 visitation.',y)
 y=para('A list-length cap is different from a comparison timeout. Omitted239/2863 and256/876 have60 candidates but correct positive-half ranks3 or8. A32-position search limit would admit either. The recovered source allocates100 entries at199, not32.',y)
 y=para('The smallest irreducible factor is different from every intermediate polynomial. The period conjugate construction can have degree r*(ell-1)/2. Published239v1,239v3 andP521 have r199=40, giving degree3960, even though their minimum irreducible degrees are440,440,120. A hard2048 bound on all intermediate polynomials fails them.',y)
 y=para('No recovered source prescribes the numerical caps or a mandatory prime199 check. The exact classifier is retained as a specific lead. Actual selection criteria remain unidentified.',y)
 c.drawImage(str(D/'workflow.png'),32,70,width=W-64,height=155,preserveAspectRatio=True,anchor='c');foot(3);c.showPage()
 title('Validation, torsion meaning and provenance');y=H-87
 y=para('All1281 cells agree independently:673 nonsplit,574 split,33 non-scalar Jordan,1 scalar. Direct quotient coordinate maps settle the three ambiguous scalarity cells. Predicted division-polynomial factor degrees agree by separate matrix fixed-point and eigenvalue-cycle formulas.',y)
 y=para('P224 at3 is the scalar -I cell: full Frobenius order2, order modulo sign1, projective order1. Its quadratic twist therefore has full rational3-torsion. The three P224 omissions have Jordan action at3. This explains a concrete torsion aspect of the cube/splitting pattern, not why the original program selected it.',y)
 y=para('Controls +I,-I,Jordan,nonsplit give full/x/projective orders(1,1,1),(2,1,1),(3,3,3),(48,24,8). Native counts and division-polynomial factors, independent GP control counts, A/A and invalid-model/order controls pass. Local LMFDB class labels1.7.b,1.7.ab,1.7.e,1.5.d are class provenance only; models are independently counted.',y)
 y=para('The new1313 columns and6680 atoms give2056 new signatures.3,130,260 new pair classes and50,084,160 truth tables were exhaustively checked twice.16 pairs support19 fitting tables; no new single predicate fits. Prior old-old zero-fit pairs are reused. All aliases, fits and nonfit witnesses remain available; all labels were already visible.',y)
 y=para('Primary sources: Schoof1995,doi10.5802/jtnb.142; Morain1995,doi10.5802/jtnb.143. The latter cites Mueller/Dewaghe1994 work in preparation. This does not identify those manuscripts with a later routine or establish original caller use. Source code is later LiDIA23dac491, explicitly unproven as the1997 implementation.',y)
 y=para('Both formal exports pass file verification. Archive:54 sealed files, SHA256 '+json.loads((D/'BUNDLE.json').read_text())['sha256']+'. Original paper/package bytes are excluded. Canonical upload returned HeadObject403; exact bytes remain in Git under the existing PR2602 exception.',y,size=9.5,width=101)
 y=para('Relocation validation hashes all payloads and replays both1281-cell methods, all bitset pairs and the three policies. It compares with the original complete rowwise results/witnesses; rowwise enumeration is not repeated. Replays are same-data validation. See PORTABLE-REPLAY.json, PLAN.md, ALL-FITS.json and both protocols.',y,size=10,width=96)
 y=para('Next discriminating evidence: an authenticated requirement/caller or source-backed reason for the199 gate, degree mode and actual limits. The selector problem and goal remain open.',y,size=10,width=96)
 foot(4);c.save()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--figures',action='store_true');p.add_argument('--pdf',action='store_true');args=p.parse_args()
 if args.figures:figures();markdown()
 if args.pdf:pdf()
