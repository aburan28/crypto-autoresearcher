# Design: LEAD-EXO-lattes-xline-dynamics, k-independence closure check

Draft, unfrozen. Mathematical research on toy parameters with planted scalars; no deployed key.

## Lead and question
Candidate C3 of the family-C report: Lattes-map dynamics on P^1(F_p) (forward orbits, iterated preimage trees of x(Q), postcritical and multiplier data) carries no ECDLP structure beyond the sqrt|Aut| constant. Question: at a matched curve, is the multiset of factor degrees of phi_d^(n)(X) - x(kP) independent of k, and does the forward x-orbit under a CM Lattes map have the length the eigenvalue predicts?

## What the lead already says
- LEAD-STR-torsion-module-leak (closed_obstructed, proof): curve-only statistics are k-independent; H-TORS-3bed8a covers the psi_5 analogue at p=13.
- LEAD-STR-small-cm-disc-nonunit-endo (theorem: orbit h = ord_N(lambda), n^h >= (sqrt N - 1)^2) and LEAD-STR-automorphism-quotient-rho (closed_known, sqrt|Aut|).
- ECDLP-IDEA-113 (rejected): a source-faithful quotient of the preimage tree has N^(1-o(1)) leaves.
- EV-ECDLP-0c0f51, EV-ECDLP-a8af77: neutral zero-run reviews of Lattes Cauchy-accumulator proposals (pole divisors, finite-quotient projector). They close different objects; they are not toy measurements of this statistic.
- LEAD-EXO-elliptic-net-eds: net oracle GGM-simulable (KN-FIND-002); same forward-iterate argument.
No row covers Lattes dynamics itself. The expected disposition is closed_obstructed.

## Correction to the report (checked by probe)
"Identical multiset for every k" is false in general. The roots are x(k'P + T), T in E[d^n]. The torsor is trivial only if kP lies in d^n E(F_p). That holds for all k exactly when ord(P) is coprime to d. If d divides ord(P), the multiset depends on the class of kP in E(F_p)/d^n E(F_p), a function of k mod d^n: the documented torsion-module leak. Probe (not a result): gp 2.15.4, p=1009, cyclic Z/1008 curve y^2=x^3+x+b with b chosen so the group is cyclic, d=3, n=1: k=1,2,4,5,... give degrees [3,3,3]; k=3,6,9,12 give [1,1,1,3,3]. So the prediction is restricted to prime ord(P)=l not dividing d, and the divisible case becomes the positive control.

## Hypotheses
- H0 (lead's disposition): for P of prime order l, l not dividing d, every cell has exactly one multiset, equal to the cycle type of Frobenius on E[d^n] (x-roots of the tree correspond bijectively to T in E[d^n] since 2k'P is not in E[d^n]). Expected null.
- H1: some cell has two k with different multisets.
- Orbit: x-period of x(Q) under phi_alpha equals least m with lambda^m = +-1 mod l (the x-line quotients only by sign: x(iQ) = -x(Q) differs). Expected exact match, plus the bound h >= log l / log N(alpha).

## Instances
- Tree arm: p in {1009, 2003}; 3 curves per prime, found by lexicographic scan of y^2=x^3+ax+b for a point P of prime order l > 16 with l not dividing 6. Matched curve means one curve, 50 k per cell. d in {2,3}, n=1..4 (d=3, n=4 on one curve per prime only; degree 6561). k_i = SHA-256(seed||cell||i) mod l, nonzero, distinct up to sign. Seeds 20261101..05 fixed in the protocol. Cells: 2 primes x 3 curves x 7 (d,n) = 42, plus 2 deep cells; 50 k each, set A (candidate) and set B (A/A).
- Positive control: curves with cyclic d-part of order >= d^2 and P generating it, d in {2,3}, n in {1,2}, p in {1009, 2003}, 2 curves each.
- CM arm: j=1728 with alpha=1+i (norm 2) and j=0 with alpha=sqrt(-3) (norm 3). p must be 1 mod 12, so p in {1009, 2017, 4093}; 2003 is 11 mod 12 and supersingular for these. Probed prime-order subgroups: (1009, j0, b=11, N=967), (2017, j1728, a=12, l=509), (4093, j0, b=2, N=3967), plus the scan's next hits. 20 random Q each.

## Arms and controls
Reference: Frobenius cycle type on E[d^n], derived by the checker from fixed-point counts |E[d^n](F_{p^j})| (PARI ellgroup), with no polynomial factored. Candidate: measured multisets. A/A: second k set, only the draw differs. Positive: pos-coset arm, same code path; it must split by k mod d^n up to sign, and the record writer also emits x(kP), which a constant-statistic test must reject. Orbit positive: the comparator fed lambda^m = 1 without the sign quotient must mismatch wherever -1 is in <lambda>. Negative: the positive-control multisets with class labels permuted (999 permutations, seed 20261104); the separation test must hold its false-positive rate at or below alpha/4. A null with no positive control passing is invalid_measurement, not a closure. Baseline: not applicable (no method being sped up).

## Counted metrics
Exact counts only: distinct multisets per cell (n_distinct), orbit mismatches, positive partition purity, negative false-positive rate. Field multiplications inside the factoriser are logged as counters. No clock is read, no rho comparison is made, no cost-against-rho claim.

## Decision rule
Supported (closure confirmed at toy scale) iff n_distinct = 1 in every candidate and A/A cell, multisets equal the reference, positive control separates in all cells, negative false-positive rate at or below alpha/4, orbit mismatches = 0. Disposition then: LEAD-EXO-lattes-xline-dynamics added as closed_obstructed, kind proof, with this measurement as its toy evidence.
Falsifier: any k-dependence at matched curve, i.e. one prime-order cell with two different multisets. Then the lead reopens, and the first action is a root-cause review (candidate causes: a repeated root from a critical-value target, an implementation fault, or a theorem error) before any claim. A control failure yields invalid_measurement and no closure.

## Inadmissible moves
Replacing or dropping a k, curve or cell after seeing a multiset; choosing curves where multisets agree; pooling d | ord(P) cells into the prime-order arm; inferring k-independence from one k-pair; presenting any of this as a cost or attack against rho; applying the CM prediction to non-CM curves.

## Cost estimate
Effort: about 1.5 days (Rust runner about 400 lines, Python orchestration and checker about 200). Compute: Rust distinct-degree factorisation by the Berlekamp Q-matrix, 43M entries at degree 6561, a few seconds per deep polynomial; 4,400 shallow polynomials under a second each. Estimated total about 40 minutes on one 4-core host (an estimate, to be measured). Checker: PARI factormod, about 20 s per deep polynomial (probe), so deep cells are checked on a nonce-sampled 10 of 50; all others in full.

## Implementation plan
Rust crate for the runner (field arithmetic mod p < 2^16, division polynomial recursion, ddf). Nothing to reuse in-repo: a grep found no division-polynomial or ddf code in a Rust crate; tools/isogeny_dreg_search.py and harness/endosweep/ (explicit.py, subgroup.py) are the nearest Python code for curve and subgroup scans and can seed the curve-selection logic and cross-check orders. The group law needed only for planting x(kP) and for building the CM lambda prediction. Python orchestrates and writes records.jsonl and the experiment.export/v1.

## Independent checker
PARI/GP script plus Python, sharing no code with the runner: replays recorded (p, a, b, P, k) rows, builds the target with ellxn, factors with factormod, recomputes the reference from ellgroup fixed-point counts, and recomputes lambda and the orbit period by integer arithmetic in Z[i] or Z[omega]. Tamper test: flip one degree in a recorded multiset, swap one k between two cells, and change one orbit period; the checker must flag all three.

## Open risks
- Biggest: the prime-order restriction changes the report's claim; the closure is for prime ord(P) coprime to d only, and says nothing for composite-order groups (known leak, trivial for prime N).
- Repeated roots when x(kP) is a critical value: excluded by a stated rule; at prime l this is rare.
- Cycle-type reference via ellgroup over high extension degrees may be slow; fallback is Frobenius matrix mod d^n from a basis found in a small extension.
- The p=2003 CM check cannot be run (p is 11 mod 12); 2017 and 4093 substitute.
- Phi_alpha for j=1728 needs i in F_p chosen consistent with the eigenvalue; the checker verifies by group law.
- The protocol is unfrozen; the preflight runtime is an estimate.
