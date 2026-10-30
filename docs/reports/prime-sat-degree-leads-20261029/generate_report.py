from pathlib import Path
import json, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
root=Path(__file__).resolve().parent
sections=[
('Prime-field elliptic curves: five solver leads',[
('p','Research and proposal report • 29 October 2026 UTC. No new mathematical experiments were run. The constructions below are proposed or algebraically derived; none establishes a smaller degree of regularity, a faster point-decomposition algorithm, or an ECDLP exponent improvement.'),
('p','Recommendation: first test shared divisor membership as a representation question, certified finite-field conflict learning as a proof-search question, and partial multigraded XL as a matrix-work question. Keep strong backdoors and chart-local saturation as secondary, stop-gated investigations.'),
('h','Scope and audit'),
('p','The target is a nonsingular short-Weierstrass curve E: y²=x³+ax+b over F_p, p>5, with a prime-order subgroup of size N. No particular deployed curve or target key is selected. A cofactor-one curve is the simplest first correctness fixture; otherwise subgroup membership must be checked. Small fixtures would diagnose mechanisms, not validate transfer to cryptographic sizes.'),
('p','The audit used 2,687 proposal and 2,136 hypothesis index rows at crypto-autoresearcher commit 708939176daa624e17c53e7ca4a9d0d478b10fb4, followed by a fetch/merge to 1896454c43bede18d19fb51362d748ed3246227e. That update changes seven lead records, including recent factor-base yield work. Related experiment references came from the existing source index and selected current Git objects. This is targeted deduplication, not an exhaustive proof of absence.'),
('p','Recorded prior work: prime-field digit encodings already cover carries and adaptive staircases; function-first H|L_V appears in IDEA-20260918-5a9a51; prime-field CDCL appears in IDEA-20260905-24d827; guarded subresultants appear in IDEA-20260906-69b3fc. Those ideas are not newly invented here.'),
('p','DEC-20261003-277d8b records a preliminary FULL inverse-degree result for the two-block digit residual at s=4,5,6 (EXP-ECDLP-3abd24). Its scope is a plain-Macaulay instrument, with disclosed dirty producer state and same-session review. It does not settle bounded polynomial calculus, CDCL, or intrinsic regularity. The PKM report in crypto records degree growth beyond an apparent plateau; a productive F4 degree is an observation, not an exact regularity theorem.'),
('p','The SATIC separator and guarded-PRS specifications cite run identities, but the inspected Git subtrees contain only their specifications. Reconcile those referenced artifacts before restarting their work. A separate function-first-linked experiment checks one F_17 chord; that is not a complete function-first solver test.'),
('diagram','lead-map.svg'),
]),
('1. Shared divisor coefficients and a Graeffe membership tower',[
('p','IDEA-20261029-3d0e71 • representation/composition • novelty unverified. The precise candidate is shared structured membership in divisor coefficients. Function-first decompositions, multiplicative-coset bases, symmetrization, and Graeffe root squaring are known ingredients.'),
('p','Let d=2^k divide p−1, choose nonzero t, set c=t^d, and define S={x in F_p: x^d=c}. For R=(r,s), use A=X³+a₂X²+a₁X+a₀, B=b₁X+b₀, and a monic quintic U₀. Impose:'),
('code','A(r) − s B(r) = 0\nA(X)² − B(X)² (X³+aX+b) = (X−r) U₀(X).'),
('p','On the chart gcd(B,U₀)=1 and U₀(r)≠0, every root ξ gives Pξ=(ξ,−A(ξ)/B(ξ)). The function A+By has pole order six at infinity. Its zero at −R and its five residual zeros give the divisor relation ΣPξ=R, counting multiplicity. Require squarefree U₀ for the distinct-coordinate comparison. This is a selected chart: repeated-coordinate, zero-denominator, and target-coordinate cases must be retained separately or their loss measured and charged.'),
('p','Instead of imposing five separate membership towers, write Uⱼ(X)=Eⱼ(X²)+X Oⱼ(X²), and apply the degree-five Graeffe transform:'),
('code','Uⱼ₊₁(T) = T Oⱼ(T)² − Eⱼ(T)²\nUₖ(T) = (T−c)⁵.'),
('p','The roots of Uⱼ₊₁ are the squares of the roots of Uⱼ. Thus every root of U₀ satisfies ξ^d=c. Because d divides p−1 and c=t^d, the membership polynomial splits over F_p. Each transform contributes five quadratic coefficient equations. This derivation is not an independently checked implementation or proof artifact.'),
('p','Why investigate it: the curve relation and membership now act on the same small collection of unordered coefficients. A shared quotient-ring circuit X^d≡c mod U provides a useful comparison. The tower does not make solving logarithmic: the possible root multisets remain combinatorial, and the familiar 5! permutation reduction is only a constant.'),
('p','First proposed test: exact tiny correspondence census with k=3,4 and at least five usable distinct x-coordinates; compare per-root PKM, symmetric S₆, shared quotient membership, and the Graeffe norm presentation on exactly the same chart. Use k=2 only as an empty-chart negative control: four membership roots cannot hold five distinct coordinates. Check every recovered sum and every missing/extra model before measuring work. Extend only after lower-arity calibration and the research question’s approval conditions are met.'),
('p','Stop if the apparent gain is only permutation removal, excluded branches, hidden high-degree elimination, or unsupported prime selection. A large 2-power divisor of p−1 is a real applicability condition; this proposal is not a generic-prime construction. Root-squaring is classical [S1], and the prime-field PKM construction is a required baseline [S2].'),
]),
('2. Certified finite-field learning inside a SAT-style search',[
('p','IDEA-20261029-8d82e6 • algorithm/composition • continuation of an existing research line. The unresolved step is whether polynomial-calculus or guarded finite-field explanations prune substantial regions before almost every coordinate block has been assigned.'),
('p','Use Boolean or explicitly finite-domain decisions for membership choices, while retaining multiplication in F_p. At a theory conflict produce an independently checkable identity or a guarded consequence. Under a fixed prefix an UNSAT certificate has the form 1=Σaᵢfᵢ, including the declared Boolean/domain constraints. Learn a clause over that prefix; a certificate valid only under guards must retain those guards.'),
('p','Native finite-field SMT already exists: cvc5 implements it [S3], and the Yices2 MCSat work uses zero decomposition to explain conflicts [S4]. Their published applications are not prime-field ECDLP attacks. The Yices2 paper also reports that its advantage weakens on large fields; blindly assigning arbitrary F_p values is an especially poor transfer strategy.'),
('p','The repository’s negative inverse-degree result is a useful starting point. Reuse the exact two-block residual fixtures where recoverable, reproduce their recorded plain-Macaulay behavior, then compare bounded polynomial-calculus closure and certificate-producing theory learning. Do not relabel ordinary full-degree XL as a new SAT method.'),
('p','Measure total failed and successful branch work, explanation construction and checking, learned-prefix coverage, complete SAT/UNSAT agreement, memory, and amortization over actual target counts. Compare bit-vector SAT, native finite-field SMT, the existing last-block root finder, and the strongest direct/MITM baseline under identical domains.'),
('p','Stop if conflicts become useful only after all but one block is fixed, if proving a conflict costs as much as the avoided enumeration, or if the advantage occurs only for witness-planted SAT instances. A few valid solutions do not establish completeness or inexpensive UNSAT decisions.'),
('h','A more speculative solver interface'),
('p','The divisor tower admits finite branching on root multiplicities when traversed backward. The first preimage of (T−c)⁵ has six multiplicity signatures between ±√c. Later layers can branch further. Certified norm-incompatibility lemmas could reject entire signature families. This is a possible extension of lead 1, not a sixth independent mechanism: without early pruning its leaves still enumerate the root multisets.'),
]),
('3. Partial multigraded Macaulay layers',[
('p','IDEA-20261029-e4edce • composition • a new application to test, using known ingredients. Aim to reduce actual matrix work without asserting that intrinsic regularity falls.'),
('p','The 2026 paper Smoothing the degree of regularity studies selected submatrices that can avoid building a whole final degree layer under stated rank assumptions [S5]. Multi-homogeneous XL gives a complementary framework for variable blocks and structured rank [S6]. Here the candidate is their combination on the exact prime-field membership/curve presentation.'),
('p','Keep the curve/divisor, membership-layer, and carry variables in explicit blocks. First determine whether a valid multi-homogenization exists; count its added variables and components at infinity. Compare full ungraded, partial ungraded, full multigraded, and partial multigraded arms. Each arm must reach a verified solution or refutation, rather than report a rank deficit alone.'),
('p','The assumptions established for random MQ or MinRank systems do not automatically hold for elliptic systems. The linked public MinRank implementation describes GF(16), so a prime-field backend requires work [S7]. This search inspected the two ePrint abstracts and the implementation README; full PDF retrieval was unavailable. Source-level reproduction is a prerequisite to implementation, not completed work.'),
('p','First proposed test: reproduce a source calibration case, then replay a tiny prime-field corpus whose full-layer outputs are certified. Record generated rows, columns, rank, field operations, selection/retry cost, solving degree, and peak memory. Stop if the selected submatrices grow to full size or the extra homogenization and recovery work absorbs the saving. Treat a bounded factor gain as such.'),
('h','4. Strong algebraic backdoors chosen without witnesses'),
('p','IDEA-20261029-2e292c • algorithm • speculative extension of guess-and-determine. Search for a small public set of carry/intermediate decisions such that every legal assignment leaves a residual tractable by a fixed bounded-degree or acyclic procedure. This is stronger than finding a few lucky assignments.'),
('p','Select variables from a frozen policy using the unsolved instance’s dependency structure. At tiny sizes, certify every residual branch. Compare equal-entropy random cuts, min-fill cuts, fixed coordinate blocks, and the proposed policy. Include a synthetic system with a known small strong backdoor as an instrument control.'),
('p','The price is C_select + Σα C_residual(α), not the degree of the easiest branch. Finding the backdoor is charged too. Stop if any legal assignment is unresolved, witness information enters selection, or the required decision entropy reproduces the existing enumeration exponent. Carries, ordinary guessing, and adaptive monomial bases are already in the ledger; only the strong low-entropy structure is the new question.'),
]),
('5. Complete chart-local saturation and the decision rule',[
('p','IDEA-20261029-ec08bc • algorithm/composition • conditional follow-up to guarded subresultants, not an untouched idea. First reconcile EXP-SDEG-8dfcf9 and its referenced artifacts.'),
('p','Denominator clearing can add components unrelated to genuine additions. For a chosen denominator or pivot h, split h=0 and h≠0. On the latter chart solve the localized system I:h^∞, with certificates hᵉg=Σaᵢfᵢ. Solve and charge the h=0 chart with complete doubling, infinity, and equal-coordinate cases.'),
('p','Compare plain substitution, inverse-variable equations, and localized closure on the identical partition. The question is whether removing those components reduces the expensive closure on valid inputs. A generic component that is still hard defeats the mechanism. Dense redundant summation-polynomial graphs were proposed previously [S8]; more equations by themselves establish nothing.'),
('p','First proposed test: exhaustive chart-union equality against group arithmetic, including deliberate exceptional fixtures, followed by independent certificate checks. Stop if valid relations disappear, exceptional charts dominate total cost, or the cost merely moves into saturation.'),
('h','What would make any lead matter?'),
('p','Let the usable point factor base have size B=N^β and let C=N^γ be complete per-attempt cost. Write ρ for the actual successful-target probability, not the average number of decompositions. A conventional sparse index-calculus cost model is:'),
('code','T ≈ preprocessing + (B/ρ) C + Õ(B²) + descent.'),
('p','Under a distribution heuristic, ρ is roughly min(1,B^m/(m!N)); witness conservation alone does not prove this coverage law or relation rank. At m=5 and β=1/5, constant ρ would require γ<3/10 to beat rho’s N^(1/2) time, with the matrix term N^(2/5). At m=4 and β=1/5, the corresponding threshold tightens to γ<1/10. These are conditional gates, not achieved exponents. Field-operation versus group-operation conversion and all preprocessing remain charged.'),
('p','Measure input degree, observed solving degree, matrix size, and certified refutation complexity separately. Exact regularity/first-fall/last-fall labels need their own certificates. A quadratic auxiliary-variable system may remain difficult, and a SAT solver can be useful without changing any algebraic invariant.'),
('p','Recommended sequence: (1) exact representation/solution-set checks for lead 1; (2) recover and extend the two-block certificate fixtures for lead 2; (3) source calibration for lead 3. Freeze a full experiment protocol before any trials. Stop the relevant lead on the stated failure, retaining exceptions and censored cells. No large campaign is justified by this memo alone.'),
]),
('Sources, local evidence, and limitations',[
('p','Primary external sources are cited for their stated techniques only. Applications and combinations in this report are proposals. Literature results were not independently reproduced here.'),
('p','[S1] Divasón et al., A Verified Implementation of the Berlekamp–Zassenhaus Factorization Algorithm (Graeffe transformation). https://link.springer.com/article/10.1007/s10817-019-09526-y'),
('p','[S2] Petit, Kosters, Messeng, Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields. https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf'),
('p','[S3] Ozdemir et al., Satisfiability Modulo Finite Fields. https://eprint.iacr.org/2023/091'),
('p','[S4] Hader et al., MCSat-based Finite Field Reasoning in the Yices2 SMT Solver. https://arxiv.org/html/2402.17927v1'),
('p','[S5] Jaques et al., Smoothing the degree of regularity for polynomial systems. https://eprint.iacr.org/2026/408'),
('p','[S6] Ning, Ran, Samardjiska, Multi-homogeneous XL. https://eprint.iacr.org/2025/2060'),
('p','[S7] Authors’ MinRankSolver repository. https://github.com/kcning/MinRankSolver'),
('p','[S8] Courtois, High Saturation Complete Graph Approach for EC Point Decomposition and ECDL Problem. https://eprint.iacr.org/2016/704'),
('h','Internal references inspected'),
('p','crypto: research/ic_next10_20261014/03-pkm-degree/README.md; research/ic_next10_20261014/05-multipoly-lattice/README.md; research/ecbench_sat_pdp_20261009/README.md; research/notes/index-calculus/RESEARCH_DEGREE_REDUCTION.md. These are prior recorded reports, not reruns or a fresh evidence audit.'),
('p','crypto-autoresearcher: RQ-PFDR-ae2fba; IDEA-20260918-5a9a51; IDEA-20260905-24d827; IDEA-20260930-ba8184; H-ECDLP-3091c2; DEC-20261003-277d8b; H-SATIC-b58495; EXP-SATIC-201dea; IDEA-20260906-69b3fc; H-SDEG-96e0d7; EXP-SDEG-8dfcf9; LEAD-ICP-digit-presentation-solving-degree; LEAD-ICP-algebraic-membership-factor-base; KR-IC-0d2021.'),
('p','Recent factor-base yield measurements recorded in the atlas do not answer the solver-cost question. Conversely, a new encoding does not evade conservation of witnesses. The earlier W10 lattice restrictions and later bounded extensions are not universal impossibility results for SAT or algebraic solving.'),
('p','All five ideas remain novelty-unverified and untested here. The two stop-gated secondary leads should not be represented as equally promising as the first three. Canonical evidence graphs and research decisions are unchanged. This report’s diagram shows proposed work only; it contains no invented performance data.'),
])]
(root/'report-content.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n')
md=[]
for title,blocks in sections:
 md+=['# '+title,'']
 for typ,txt in blocks:
  if typ=='h': md+=['## '+txt,'']
  elif typ=='code':md+=['```text',txt,'```','']
  elif typ=='diagram':md+=['![Proposed research paths](lead-map.svg)','']
  else:md+=[txt,'']
(root/'report.md').write_text('\n'.join(md))
fig,ax=plt.subplots(figsize=(10,3.1));ax.set_xlim(0,10);ax.set_ylim(0,3.1);ax.axis('off')
boxes=[(.1,1.75,3,1.05,'CHANGE REPRESENTATION','Shared divisor + Graeffe tower\nStrong backdoors / complete charts'),(3.5,1.75,3,1.05,'CHANGE PROOF SEARCH','Finite-domain SAT decisions\nCertified Fp explanations'),(6.9,1.75,3,1.05,'REDUCE MATRIX WORK','Partial degree layers\nValid multigrading')]
for x,y,w,h,t,b in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',facecolor='#e8f1f7',edgecolor='#335d7a'))
 ax.text(x+w/2,y+.78,t,ha='center',fontsize=10,weight='bold');ax.text(x+w/2,y+.34,b,ha='center',va='center',fontsize=9)
 ax.annotate('',xy=(5,.95),xytext=(x+w/2,y),arrowprops={'arrowstyle':'->','color':'#335d7a'})
ax.add_patch(FancyBboxPatch((1.2,.25),7.6,.75,boxstyle='round,pad=0.04',facecolor='#f2f1e7',edgecolor='#786d35'))
ax.text(5,.73,'SHARED GATE: identical verified relations + complete charged work',ha='center',fontsize=10,weight='bold')
ax.text(5,.43,'Membership • failed branches • exceptions • certificates • yield • rank • descent',ha='center',fontsize=9)
ax.text(5,3.01,'Proposed directions — no measured solver or exponent gains',ha='center',fontsize=11,color='#555555')
fig.savefig(root/'lead-map.svg',bbox_inches='tight');plt.close(fig)
typ=['#set page(paper: "a4", margin: (x: 19mm, y: 17mm), footer: context align(center)[#text(size: 8pt)[Prime-field solver leads • 2026-10-29 • #counter(page).display()]])', '#set text(font: "DejaVu Sans", size: 9.5pt)', '#set par(justify: true, leading: 0.62em)', '#set heading(numbering: none)', '#show raw: set text(size: 9pt)']
for idx,(title,blocks) in enumerate(sections):
 if idx:typ.append('#pagebreak()')
 typ.append('#heading(level: 1, '+json.dumps(title,ensure_ascii=False)+')')
 for kind,txt in blocks:
  if kind=='h':typ.append('#heading(level: 2, '+json.dumps(txt,ensure_ascii=False)+')')
  elif kind=='code':typ.append('#block(fill: rgb("f2f4f6"), inset: 9pt, radius: 3pt, width: 100%)[#raw('+json.dumps(txt,ensure_ascii=False)+', block: true)]')
  elif kind=='diagram':typ.append('#image("lead-map.svg", width: 100%)')
  else:typ.append('#text('+json.dumps(txt,ensure_ascii=False)+')\n\n')
(root/'report.typ').write_text('\n'.join(typ))
import typst
typst.compile(str(root/'report.typ'),output=str(root/'report.pdf'))
print(root)
