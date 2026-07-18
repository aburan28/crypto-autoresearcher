# ECDLP-IDEA-131 — Elliptic turnpike autocorrelation descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_homometric_source_ambiguity`
- Cohort: `20260717-g`
- Evidence scale: no run; any future turnpike preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an autocorrelation, reconstructed divisor up to symmetry,
  valid relation, full-rank toy system, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Represent an exact signed five-source tuple by a sparse source divisor on `E` and associate
to it the multiset-valued elliptic difference autocorrelation. Suppose this autocorrelation
can be computed from the public endpoint `R` without source enumeration and is rigid, after
frozen canonicalization, for generic factor-base divisors. A turnpike-style reconstruction
would output every exact source tuple in complete exponent `alpha<3/2`, generate
`B+sigma` rank-`B` relations, verify factor logs, and descend blind `Q+[t]P` below rho.

This record is rejected and merged with differential/symmetric-square/phase controls:
autocorrelation is translation/reflection invariant, homometric source divisors exist, and
the endpoint does not publicly reveal the unknown pairwise-difference multiset.

## Mechanism-new operation

The proposed operation is **derive a target's elliptic difference autocorrelation directly
from its endpoint, canonically reconstruct the sparse source divisor by a turnpike
algorithm, and verify each recovered factor-base tuple on the original curve**. The
operation must preserve signs, multiplicities, repeated points, infinity, and all
homometric branches.

Computing differences after a source tuple is known, replacing a pair table by a Fourier
magnitude table, choosing a post-hoc canonical representative, or using xADD/symmetric
square as another backend is a duplicate/control. Only a target-computable autocorrelation
with an exact source inverse could remove the recorded obstruction.

## Assumptions

1. `E(F_p)` contains public prime-order `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`,
   fixed arity five, and target-independent sign-canonical factor base
   `F={F_1,...,F_B}` with `B=L=N^ell`.
2. Each signed source tuple has a frozen divisor and elliptic-difference autocorrelation
   encoding order, signs, repetitions, and infinity exactly.
3. The complete autocorrelation or an equivalent query oracle is computed from `R` alone,
   without knowing sources, factor logs, or materializing a pair/five-source table.
4. A public canonical reconstruction enumerates all homometric divisors and returns exact
   factor-base indices rather than only a translate/reflection class.
5. Endpoint, sum, autocorrelation, and source conditions are biconditional and every output
   is independently verified by elliptic addition.
6. Autocorrelation construction, Fourier transforms, branching, output, misses, rank,
   linear algebra, blind descent, verification, and peak bit memory are fully charged.
7. All finite observations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`source_divisor | elliptic_difference_autocorrelation | homometric_turnpike_rigidity | canonical_multiset_reconstruction | exact_source_verification | blind_descent`

The target-computable autocorrelation and exact canonical source inverse are jointly
load-bearing. Pairwise differences computed from already known sources are only a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H660`, where exact symmetric-square
   degree-two divisor states retain generic pair-fiber cost rather than a source decoder.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`,
   where exact projective xADD does not
   compress the permutation-closed known-difference representation below the gate.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`,
   where exact divisor fibers and batched
   inversions improve constants but retain pair labels and output cost.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where
   tested rational-phase and character
   matrices have full pair-state rank and no complete nonlinear source bridge.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-002`, where target-coupled sparse
   divisor-difference relations work but raw list reconstruction remains BSGS-shaped.

## Closest primary literature

- Skiena, Smith, and Lemke,
  [Reconstructing sets from interpoint distances](https://doi.org/10.1145/98524.98598),
  study turnpike and beltway reconstruction, including multiple solutions and hard
  variants; they do not derive pairwise differences from an elliptic endpoint.
- Ranieri, Chebira, Lu, and Vetterli,
  [Phase Retrieval for Sparse Signals: Uniqueness Conditions](https://arxiv.org/abs/1308.3058),
  connect sparse phase retrieval to turnpike uniqueness and identify autocorrelation
  collisions as an obstruction; they do not give an ECDLP source oracle.

No checked primary source supplies a target-computable elliptic autocorrelation, eliminates
homometric ambiguity, or proves fully charged better-than-rho descent.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L`, signed source-divisor encoding, autocorrelation definition,
   canonical symmetries, reconstruction algorithm, ambiguity policy, exceptional cases,
   and independent elliptic verifier.
2. Build only target-independent factor-base support data and prove that no pair-incidence
   or hidden scalar table is embedded in the autocorrelation oracle.
3. For known public `R_j=[r_j]P`, compute the frozen endpoint autocorrelation, reconstruct
   every canonical source divisor, map each to exact signed factor points, and independently
   verify every five-point elliptic sum.
4. Preserve misses, homometric branches, translations, reflections, and duplicates;
   collect exactly `B+sigma` verified rows whose coefficient matrix has rank `B` modulo `N`.
5. Solve every factor-base logarithm and independently verify
   `[log_P(F_i)]P=F_i` for all `i`.
6. Freeze all autocorrelation/reconstruction state, choose fresh public masks `t`, and
   apply the identical oracle and source reconstruction to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every homometric scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Set `B=L=N^ell`. Let factor support,
autocorrelation oracle, canonicalization, and reconstruction setup cost `L^(s+o(1))`
time and `L^(s_m+o(1))` peak memory. Let one complete target autocorrelation, all
turnpike branches, entire source output, and verification cost `L^(alpha+o(1))` time and
`L^(m_q+o(1))` memory.

Unless a theorem proves a changed density, use `pi=min(1,L^5/N)`. In the sparse regime,

`T_rel=N*L^(alpha-4+o(1))`

and

`T_desc=N*L^(alpha-5+o(1))`.

Sparse linear algebra costs `L^(2+o(1))` time and at least `L^(1+o(1))` memory. Thus

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`

and

`mu=max(s_m*ell,m_q*ell,ell)`

For `ell=1/5`, strict time below rho requires `alpha<3/2`; promotion
`lambda,mu<=0.45` requires `alpha<=1.25` and `s,s_m,m_q<=2.25`. Every difference bin,
Fourier coefficient, homometric branch, emitted divisor/source, failed target, row, factor
log, and verifier operation is charged. An explicit `L^2` difference or pair table gives
setup or memory exponent `2` in `L` and fails the conservative gate.

## Likely fatal obstruction

Autocorrelation loses absolute position and orientation, and distinct homometric multisets
can have exactly the same difference data. The elliptic endpoint supplies only one sum;
it does not determine the `Theta(5^2)` source differences, so deriving the autocorrelation
from `R` can be as hard as reconstructing the sources. Canonical translation/reflection
choices do not remove genuine homometric collisions, while an explicit factor-base pair
difference dictionary has `L^2` work/memory and reproduces the known barrier.

## Proof track

Prove a target-computable autocorrelation identity, generic or uniform homometric rigidity
with complete branch enumeration, exact source reconstruction, and the full seven-step
rank, factor-log, blind-descent, output, and peak-memory bounds.

## Disproof track

Construct two factor-base source divisors with identical full autocorrelation and endpoint,
prove endpoint-to-autocorrelation computation needs source incidence, establish an
`Omega(L^2)` dictionary/output lower bound, or derive complete exponent at least `1/2`.

## Positive and negative controls

- Positive turnpike control: collision-free planted integer/finite-cyclic sets with exact
  distance multisets and complete reconstruction.
- Positive EC control: exhaustive tiny factor bases with blinded planted source divisors
  and independent endpoint verification.
- Negative controls: known homometric pairs, translations, reflections, repeated points,
  zero differences, and sources sharing the same endpoint.
- Mechanism controls: xADD, symmetric-square divisors, Fourier magnitude/phase retrieval,
  explicit pair tables, MITM, and post-hoc autocorrelation of known relations.
- Leakage control: permute factor-base scalar labels while preserving point/difference data;
  output must follow points only.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

This rejected lane cannot reopen without a theorem proving endpoint-to-autocorrelation and
autocorrelation-to-source biconditionals with symbolic `lambda,mu<=0.45`. A future toy
preflight must cover at least 20 ordinary curves per size across four increasing sizes,
exhaustive homometric/source truth through 18 bits, at least `1,000` verified relations and
`100` blind descents at each of the two largest sizes, exactly `B+sigma` retained rows of
rank `B`, zero source omissions/errors, and upper 95% bounds `lambda<=0.45` and
`mu<=0.45` including every ambiguity branch and difference datum. Falsify on one stable
equal-endpoint homometric collision without public disambiguation or a proved or lower-95%
complete bound `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Autocorrelation/source theorem gate: `ideas/artifacts/ECDLP-IDEA-131/autocorrelation_source_gate.md`
- Frozen divisor specification: `ideas/artifacts/ECDLP-IDEA-131/source_divisor.yaml`
- Prospective turnpike decoder: `ideas/artifacts/ECDLP-IDEA-131/reconstruct_sources.py`
- Independent homometry/source verifier: `ideas/artifacts/ECDLP-IDEA-131/verify_autocorrelation.sage`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-131/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-131/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. An
autocorrelation, phase-retrieval solution, reconstructed divisor up to symmetry, valid
relation, full-rank toy matrix, verified factor log, or recovered toy scalar is not a
better-than-rho result or a breakthrough. Without both public endpoint conversion and an
exact homometry-resolving source inverse, this remains a pair-state reformulation.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-131/autocorrelation_source_gate.md` proving either a target-computable homometry-resolving source inverse with symbolic `lambda,mu<=0.45` or an explicit equal-endpoint homometric/`Omega(L^2)` obstruction.
