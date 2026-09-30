# TASK-20260926-e13b6b (S5) generator report: target-dependent and implicit factor bases on ECC2K-130

Lane: idea-generator, policy research-deep, round 2, seam S5 of
`BRIEF-ROUND2.md` section 3. Written 2026-09-26; the lane was interrupted by
an API rate limit after the first record and resumed on the coordinator's
instruction (the first record was re-checked and re-written with three
apostrophe-in-single-quote scalars converted to block scalars; no other
change). No run, no solver, no status change; proposals only. No web search;
every external reference is `recalled`; every record is
`novelty_status: unverified` with a `prior_art` block.

## Records written (3 of 5 ids used)

| id | class | question | claim in one line | (representation, Sigma) | target m and budget | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-bbf2ed | representation | RQ-CERTBIN-836ce2 | The partial trace spectrum V_E = {x : Tr(x^e) = 0, e in E}, 98 cyclotomic classes of 2-weight <= 3, is a Frobenius-stable implicit base at n = 131 (K-degree > 2^130, ANF degree <= 3, O(n) membership); priced by closure cost on RC-1 against subspace, random quadrics, ball and random set. | R1 abscissa; Sigma = {sigma, negation} plus translation by base elements inside the decomposition; Class I partial action; description is Class III | m = 4, |E| = 98, |F| ~ 2^33; budget 2^30.6 orbit-reduced or 2^5.73 no-orbit (both cited) | unverified | impl medium, compute low (minutes per arm) |
| IDEA-20260926-bc1cab | control | RQ-QSP-f9bbdb | K-coefficient census at n = 131: QSP lambda (d <= 7, n' = 33) bounded by d^4 with no 131-orbit peak; the linearized successor sub-shape x^{2^33} + c x^{2^32} + e(x) sits where the bound is vacuous and is decided exactly per candidate by a 131 x 131 rank; predicted null with the sampling ceiling stated. | R1; Sigma = twisted sigma^{n'} chain / {sigma^a, link}; census of the description, Class I for the relation vector | not applicable (certificate); a positive successor member inherits a17f43's m = 4 at n' = 33 with the NO-orbit budget 2^5.73 | unverified | impl low, compute low (rank arms minutes to hours; non-linearized arm needs a C helper beyond tens of candidates) |
| IDEA-20260926-beb5b6 | control | RQ-BINSTD-b6f698 | Target-dependent bases are instance-dependent (unknowns shared only through the instance), so the class collapses to known-log pools, the Gamma-orbit of Q and relabelings; the collected 2^33 DPs hold ~2^-1.6 zero-sum 4-subsets and 2^29 5-subsets, findable only by m-SUM at >= 2^66; toy zero-sum census against relabelled and non-walk pools. | R1 walk points with (a, b); Sigma = the walk step, sigma, negation; branching for the pool, Class I for the zero-sum vector | m = 3..5 on the pool; cost >= 2^66 against rho's remaining 2^60.5; zero relations, zero linear algebra | unverified | impl low, compute low (under one CPU-hour) |

Unused ids, returned by name: **IDEA-20260926-c5125a**, **IDEA-20260926-c5cdb5**.
The seam's remaining candidates reduced to closures (below) or to arms of the
three records; spending an id on a record whose predicted outcome and
mechanism are already carried by the closures would have been a fatigue
report dressed as a proposal.

## Which to test first, and why

**IDEA-20260926-bbf2ed, Cell A**, first. It is the only record here whose
positive branch adds an object the corpus does not have (a second
Frobenius-stable factor base at n = 131, with constraint degree 3 rather
than the ball's 7), it runs on the installed CERTBIN instruments in minutes
with four matched controls in the same falsification bands as
IDEA-20260926-b6cc43 (so the two invariant-family members are directly
comparable), and it carries an exact size identity (the Walsh/Arf recount
of claim (D)) that makes the instrument self-checking at zero extra cost.
Its negative branch is a measured cardinality of the penalty, which is the
closure standard. The cheapest valid discriminator is the four-arm closure
comparison at n = 17, m = 2 with E = all 8 quadratic classes, whose
size-matching to RC-1 is arithmetic (n - l = (n - 1)/2 = number of Gold
forms at every odd n with l = (n + 1)/2).

Second: bc1cab Stages 0-3 (the rank arms), because they cost hours, exercise
an existing instrument on its declared unvalidated path, and their positive
branch is the outcome KN-FIND-617d78 itself names as the most valuable.
Third: beb5b6, a controlled null that closes the seam's two
target-dependent candidates with numbers.

## Inventor-protocol section 5 block

**Objects considered.**
1. The partial trace spectrum Phi_E and its fibres (bbf2ed) -- the
   trace-form end of the rotation-invariant (necklace-class) family whose
   symmetric-function end is b6cc43's Hamming ball.
2. K-coefficient (twisted) quasi-subfield root sets and the K-coefficient
   linearized successor sub-shape at a = 32 (bc1cab).
3. Known-log pools (walk points, distinguished points) as target-dependent
   factor bases with an m-SUM relation mechanism (beb5b6), and the
   instance-dependence lemma that makes them, with b48c9d's Gamma-orbit and
   the relabelings, the whole target-dependent class for index calculus.
4. Considered and closed without a record (below): run-length classes,
   cyclotomic-coset / linear-complexity objects at n = 131, smoothness and
   multiplicative-subgroup bases, image bases f(W), target-shifted subspaces,
   the Krylov (conjugate-span) base, the minimal-polynomial-weight ball.

**Depth of verified structure.** Zero-compute derivations only, stated at
derivation tier and marked for re-derivation: the ANF-degree and
Frobenius-invariance of Tr(x^e); the count of 65 quadratic and 2795 cubic
classes at n = 131 and the consequence that a 2^33 trace-spectrum base needs
cubic forms; the radical-{0, 1} argument and the exact Walsh/Arf size
formula for quadratic E; the kernel bounds 8 / 4 / 1 for linearized
K-coefficient lambda at (131, 33) and the exact two-root fixture for
monomial twists (2^33 = 68 mod 263); the vacuity of the correspondence bound
for the linearized successor sub-shape at a = 32; the zero-sum arithmetic
of the DP pool (2^-64.0, 2^-32.6, 2^-1.6, 2^29.1 at m = 2..5, B = 2^33);
the instance-dependence lemma. Nothing is measured; nothing re-derives a
published result through a new lens except the placement of the DP pool
under the generic bound.

**dominated_by (Pareto, checked against every frontier row).**
- bbf2ed: matched rho 2^60.8 (KR-RHO-18cc42) on every m = 4 row until a
  per-attempt solve under 2^30.6 is demonstrated; within the factor-base
  column, KN-FIND-47da4e's orbit union and b6cc43's ball are the siblings;
  KR-IC-1fcdbc is the standing negative. No row claimed until measured.
- bc1cab: n/a (no attack claimed); KR-IC-49c882 is the row a slice of which
  is measured; a positive successor member is priced by a17f43's audit with
  the no-orbit budget and stays dominated until that audit says otherwise.
- beb5b6: matched rho on time (>= 2^66 versus 2^60.5 remaining) and memory
  (2^66 two-list tables); KR-RHO-ea34b8 precomputation is for many targets
  and costs 2^86.3 to build for one; KR-RHO-7d93f6 places the tables on the
  wrong side of the T^2 S curve.

**sota_delta.** Zero on every ECDLP cost axis for all three. Contributions:
a second Frobenius-stable base at n = 131 with an exact quadratic size
formula (bbf2ed); two declared QSP gaps turned into measurable cells and the
sampling-ceiling statement (bc1cab); the target-dependent class collapsed to
three sub-classes with the collected pool's zero-sum arithmetic (beb5b6).

**Enumerated closures, each with its mechanism (section 4 standard).**
- C1 (walk-carried bases, "relation collection and rho as one process").
  A walk point is a known-log point; the only relation among known-log
  points is a zero-sum m-subset; expected count C(B, m)/l is 2^-1.6 at
  (2^33, 4) and 2^29.1 at (2^33, 5); finding one is m-SUM over an
  unstructured pool at B^{ceil(m/2)} >= 2^66 (two-list), a k-tree cannot
  beat it because sum-compatible filters carry 2 bits on the order-4l group
  (Theorem C via IDEA-20260926-136bd3), and the only non-generic route is an
  algebraic m-SUM over a set with no description beyond "in B_34 and
  visited", whose floor is b6cc43's random-set arm. Walk-into-a-fixed-base
  hits occur at |F|/N = 2^-98 per step: the product law at arity 1.
  Recorded in beb5b6 with a toy census as its one falsifier.
- C2 (short tau-adic distance from R). {f(tau) R : wt(f) <= w} is
  b48c9d's Gamma-orbit quotient; w = 1 is 178821's conjugate base; nothing
  new. Placed under the instance-dependence lemma in beb5b6.
- C3 (target-shifted and endomorphism-pulled bases). x_R + V and x_R V are
  cosets or subspaces; F_V - R decomposes R' iff R' + mR decomposes over F_V;
  phi^{-1}(F_V) is F_V with logs rescaled by the scalar phi acts as on the
  prime-order subgroup. Lossless relabelings; fail the lossy-projection test
  as new objects. The Krylov base span{x_R^{2^j} : j < l} is a
  target-dependent SUBSPACE (bounded-degree class) whose only special
  property is a77711's equivariance V_{sigma R} = sigma(V_R), which is not a
  per-instance symmetry; relations for R and sigma R live over different
  bases and do not combine without the orbit union of KN-FIND-47da4e.
- C4 (cyclotomic-coset and linear-complexity objects at n = 131). With
  ord_131(2) = 130 the 2-cyclotomic cosets mod 131 are {0} and {1..130}, so
  every DFT-support-defined object collapses: Frobenius-stable subspaces
  have dimensions {0, 1, 130, 131} (IDEA-20260918-9abf42) and, by the
  Blahut linear-complexity / DFT-weight identity (recalled), every
  non-constant period-131 binary sequence has linear complexity >= 130. A
  "low linear complexity" or "few cyclotomic cosets" base is empty at
  n = 131. The usable reading of "cyclotomic-coset weight" is the 2-weight
  of an exponent class mod 2^131 - 1, which is bbf2ed.
- C5 (run-length classes). The number of runs of a cyclic string is
  HW(x + x^2) in a normal basis, so a run-count ball is the Artin-Schreier
  pullback of an even-weight Hamming ball: an F_2-linear change of
  coordinates of b6cc43's object (a change of coordinates, not a new
  object, by the lossy-projection test); a longest-run bound alone is far
  too large (no two adjacent ones gives a Lucas-number count, about 2^90.9
  at n = 131) and needs a second constraint to reach index-calculus size.
- C6 (smoothness and multiplicative bases). k-smooth x(t) in the polynomial
  basis has O(n^2) membership and size 2^131 rho(u) (about 2^33 at k = 6 by
  the polynomial Dickman heuristic, recalled), but the property is
  multiplicative and the relation mechanism is additive: no parameterisation
  the descent can use, so relations are membership hits only (arity 1,
  product law 2^131) or enumeration. Multiplicative subgroups of K^* have
  index 263 or order 263 (2^131 - 1 = 263 p), neither in the
  index-calculus band, and their cosets are permuted by Frobenius in orbits
  of 131 with union K^*.
- C7 (image bases f(W)). With f from the 2-torsion translation (x -> 1/x)
  or squaring, f(W) is the known symmetrised object (KR-IC-955fd6,
  IDEA-20260922-29b1c5); with generic f the descended degree grows by
  deg f and nothing is gained; and for f with F_2 coefficients on a
  non-stable W the image is not stable either.
- C8 (twisted QSP by luckier lambda). Closed by KN-FIND-617d78 (A) as a
  derivation; bc1cab does not reopen it, it exercises it and hunts the
  refutation, and separates the one cell where the bound is vacuous.

**Open directions for the next session.**
1. The minimal-polynomial-weight ball {x : wt(minpoly(x)) <= w}: the
   "most implicit" Frobenius-stable set (the Hamming ball in orbit-
   canonical coordinates; about 2^36.6 elements at w = 9), with the
   identity e_k(x) = sum over weight-k classes of Tr(x^e) linking it to
   bbf2ed's family; no decomposition handle is visible and the honest
   prior is dominated, so it is guidance, not a record.
2. The structured search that bc1cab hands forward: monic M of 2-degree
   33 - w and a subspace polynomial P_W of 2-degree w with M o P_W sparse
   (a gap from 2-degree 3 to 31), which is where a K-coefficient successor
   member would have to live; the rank-metric / cyclic-subspace-code
   literature named in KN-LIT-4fe9d2 section 4.5 is the retrieval target.
3. The Arf-sign census that would make quadratic-constrained base sizes at
   n = 131 exact for |E| up to about 25, and its relation to the weight
   distribution of the cyclic code with Gold zeros (Kasami-type results,
   recalled).
4. A single three-arm CERTBIN contract deciding the Frobenius-stable
   factor-base choice at n = 131 once: orbit union (KN-FIND-47da4e), ball
   (b6cc43), trace spectrum (bbf2ed), at matched size, with the random-set
   floor.
5. XOR-aware / cardinality-aware SAT arms for all of the above once an
   engine is installed (`missing: WDSat / CaDiCaL` throughout).
6. A mechanism that shares unknowns across targets by a shared implicit
   structure in target-dependent descriptions, which the instance-dependence
   lemma of beb5b6 does not cover; none was found this session.

## Records read this session

In full: the lane card; BRIEF.md; BRIEF-ROUND2.md; the rendered frontier map
(48 rows); docs/object-frame-ideation.md; agents/idea-generator.md;
docs/inventor-protocol.md; IDEA-20260922-845a77; KN-OPEN-020; KN-TECH-54c38e;
IDEA-20260916-a17f43; IDEA-20260926-b6cc43, -b48c9d, -178821, -cafcf1;
KN-FIND-617d78; KN-FIND-aa2efc; analysis/binstd-idea-review-20260926/README.md;
analysis/frobenius-orbit-ecc2k130/README.md; experiments/EXP-CERTBIN-e94b27/
impl/README.md. Partially (grep or first lines): titles and claims of every
other IDEA-20260926-*; IDEA-20260916-5c9d6e lines 60-90 and 262-280;
qspcore.py docstring; RQ-CERTBIN-836ce2 and RQ-QSP-f9bbdb (first 120-140
lines); templates/research-records.md prior-art and provenance sections;
KN-FIND-47da4e title and tags. Corpus greps: target-dependent, implicit,
tau-adic, necklace, run-length, cyclotomic coset, twisted, quasi-subfield,
walk, precomputation, Gold, trace form, Walsh, Arf, known-log pool, DP pool,
zero-sum, 4SUM, k-SUM, instance-dependent, minimal polynomial weight, linear
complexity, Artin-Schreier.
