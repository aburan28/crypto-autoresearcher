#set page(paper: "a4", margin: (x: 15mm, y: 13mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt, fill: rgb("172b3a"))
#set par(justify: false, leading: 0.54em, spacing: 0.65em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 16pt)
#show heading.where(level: 2): set text(size: 11pt)
= Two structural continuations
#text(size: 8pt)[Prime-field decomposition · 2026-10-30 · GOAL-PFDR-fd09e0 · RQ-PFDR-ae2fba]

*Proposals published; scientific acceptance is false and novelty is unverified.* Generator TASK-20261030-12cc63 produced two ideas; snapshot TASK-20261030-9216da owns this report. No new experiment, solver invocation, implementation or independently reviewed theorem was produced. The factor-base/decomposition lens is explicitly authorized for these continuations; no escape from object-class barriers is claimed.

#figure(image("diagram.svg", width: 100%), caption: none)

The upper panels reproduce recorded counts from EXP-PSEARCH-3ea9fe / RUN-PSEARCH-c61489 / DEC-20261030-0c834c: 48 ordinary rows per strategy, excluding its A/A repeat. The 12 inputs were F17: $y^2=x^3+2x+2$ and F97: $y^2=x^3+x+4$, digit widths 2,3 and the first three target x representatives. No population uncertainty estimate is available. Recorded coefficient arithmetic was unchanged. Dashed paths are proposed, not measured gains.

== 1. Cold active-support search: first priority
*IDEA-20261030-b6f05e.* Let A contain every variable in every cleaned residual generator, including generators above the row-degree cap. Retain original labels, generator order, exact pivots, FIFO and caps; multiply queued rows only by variables in A. Inactive bits remain free in the original model domain.

Standard absent-variable specialization preserves identities and degree. A stronger *unreviewed source-specific simulation* groups rows and all multiplier entries by their inactive-variable mask. Exact pivots prevent cross-block reduction; nonempty blocks cannot yield 1. The empty-block FIFO subsequence is proposed to match active-only search, preserving every baseline-successful certificate within no more attempted insertions under the same cap.

This does not prove selected-echelon completeness. UNKNOWN outcomes, ranks and future SAT trajectories can differ. Full support leaves no removable blocks and adds extraction overhead. Parent-row specialization/re-elimination and event-driven prefix bookkeeping are *separate optional factors*; mixed-mask warm starts fall outside the cold proof premises.

*Next discrimination, not a launch:* independent source/proof audit, then separately admitted exact-certificate and cap controls. A lost valid baseline-successful cold certificate falsifies the simulation. Cost needs a new frozen whole-search comparison retaining all four encodings, projected completeness, signed witnesses, fallback, the charged complementary-point baseline and A/A. Count support extraction, failed rows, proof copies/checks, callbacks, memory and I/O. A smaller monomial universe is not a matrix-size, runtime or degree result.

#pagebreak()
== 2. Complete signed charts and interval membership
*IDEA-20261030-a62c58.* For nonsingular $E/F_p: y^2=f(x)=x^3+a x+b$, prime p greater than 3, let k of five summands be affine. The correctness domain includes two-torsion; attack interpretation retains prime-order/subgroup conditions. No new curve was tested.

Use $h=A+B y$ of exact pole order d=k+1 for finite R=(r,sR), with h(−R)=0; use d=k for R=O. Normalize its highest-pole term. For c=1 at even d and −1 at odd d, encode c(A²−fB²)=(X−r)U for finite targets, or U=c(A²−fB²) for R=O. U is monic of degree k. Include the all-identity case and absent pole-one chart explicitly. Recover h’s *signed* zero divisor, remove exactly one −R when finite, then pad identities. Repeats, target overlap, common A/B roots, opposite pairs and tangencies must survive. Rational descent, local-order completeness and characteristic-five factorization remain proof obligations.

For interval I=t+\[0,2^s\) modulo p, with interval length smaller than p, work in Q=Fp\[X\]/U. Introduce idempotents e_j, put n=X−t−Σ2^j e_j, and require e_j²=e_j, n^k=0 and \[f(f^((p−1)/2)−1)\]^k=0 in Q. Root evaluation and standard local-ring/CRT facts motivate interval and rational-ordinate support, including multiplicities. Replacing n^k=0 by n=0 wrongly excludes repeated roots. Signed recovery uses bounded-degree factorization and local orders; every attempt and square root remains charged.

*Raw highest-part obstruction — derived, unreviewed.* For Q=F5\[z\]/z², X=1+z, e=a+bz, coefficients of e²−e and (X−e)² have a unique affine solution (a,b)=(1,0), but their highest parts generate (a²,ab). Therefore b^D survives at every positive degree; the first degree containing the entire graded component is not finite. This is not Castelnuovo–Mumford regularity, a solving-degree bound or a SAT-time lower bound. Variable-U reduction couples coefficients: idempotent syntax is not joint quadraticity. Quadratic gate lifting changes both presentation and cost.

The optional Hasse/averaging argument proposes expected at most seven *charged full interval scans* to find at least 2^s/8 rational x coordinates for a whole prime-order curve with p at least 17. It is unreviewed and implies no relation yield, rank or scalar recovery. First audit the complete correspondence and exceptional controls; a later signed census and matched five-point encoding comparison need separate admission. Permutation constants or compact circuit size alone establish no solver advantage.

== Filing and evidence boundaries
Root accepted schema completeness and actual lexical-match positioning after *three returns* at 16:44:43 UTC. Corrections repaired flow-YAML claims, schema-invalid nearest-reference IDs and missing explicit discussion of actual matches; predecessor comparisons remain in notes. Claim/mechanism strings were preserved during match reconciliation. The receipt’s earlier revalidation-pending field remains historical; subsequent root acceptance is bound separately. This is filing, not scientific review.

Generator-reported primary reads: Stacks 00J4, Lemmas 10.53.2/6; 07BH, Lemma 10.18.3; Sutherland Lecture 23, Theorem 23.3 pp.1–2; Lecture 7, Hasse Theorem 7.3 pp.1–2. These support standard foundations, not complete proposal correctness. PC-restriction prior art was a primary search excerpt with direct access denied; incremental-SAT prior art was abstract-only. Links and precise source scopes are in report.md and the hashed proposal notes; no new primary retrieval is claimed by this synthesis.

Requested research-deep/Sonnet high used an admitted native Codex fallback. Serving model, provider, effective effort and capacities are unverified; no Sonnet/Opus execution or independent review is claimed. Source publication b01b60dd80b3b7f31044b6604dd5c9228ebbf9e0; completed release 7a31b80b6b5359bcafdc3141bbe1d5193983b392. Exact input hashes, filing/native amendment receipts and actual read-only graph checks are in report-inputs.json.

Both lead records, relevant frontier rows and the historical PSEARCH graph remain unchanged: no scientific result or historical observation changes. Full-ledger validation was unavailable under sparse checkout. No H/EXP/EV/KN/DEC/goal transition or trial approval occurs. *General ECDLP speedup, scalar recovery, complete-cost advantage and a new regularity reduction remain unestablished.* Root retains current-PDF rendering, every-page inspection and the exact twenty-path archive; these remain pending at composition.
