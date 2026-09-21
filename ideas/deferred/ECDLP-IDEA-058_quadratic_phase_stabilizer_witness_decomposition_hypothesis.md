# ECDLP-IDEA-058 — Quadratic-phase stabilizer witness decomposition

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `deferred_missing_curve_specific_phase_identity`
- Evidence scale: `toy` decomposition study only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a short phase expansion or correct relation is not a break.

## Falsifiable hypothesis

After a fixed exact encoding of complete elliptic addition, the factor-base
decomposition indicator has an exact expansion into `R=N^(r+o(1))` quadratic-phase
signatures with `r<1/2`. A common phase basis supports batched contraction and exact
conditional marginals, so actual source points can be recovered while complete relation,
linear-algebra, descent, verification, and memory exponents stay below `1/2`.

## Mechanism-new operation

The operation is a **curve-specific exact quadratic-phase decomposition with witness
marginals**. Addition-law terms are converted to affine symplectic constraints and a
signed sum of quadratic characters; conditioned contractions reveal source indices.
This is not generic stabilizer simulation, approximate cancellation, a sampled character
test, an ordinary tensor-rank claim, or a relation-only certificate.

## Assumptions

1. `E(F_p)` contains a prime-order subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. The factor base `F` is deterministic, target-independent, and has `B=N^beta`.
3. The phase encoding covers all addition charts, denominators, signs, and repeated points exactly.
4. Coefficients and cancellation are exact over a specified cyclotomic or finite-field ring.
5. Conditional contractions recover source points without enumerating `F^m`.
6. Any scaling inference is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`complete_elliptic_addition | exact_quadratic_phase_sum | affine_symplectic_constraints | conditioned_phase_marginals | factor_base_source_recovery`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — prevents a new encoding alone from counting as improvement.
2. `ledger/EV-REP-001.yaml` — supplies exact-representation controls.
3. `ledger/EV-REP-002.yaml` — supplies scaling and solve-cost evidence.
4. `ledger/FINDING-PF-IC-001.md` — fixes the measured membership baseline.
5. `ledger/SYNTHESIS-20260716.md` — requires the full factor-base-to-target path.

## Closest primary literature

- Bravyi, Smith, and Smolin, [Trading classical and quantum computational resources](https://arxiv.org/abs/1808.00128), develops stabilizer-rank simulation via short decompositions.
- Huang and Love, [Approximate stabilizer rank and improved weak simulation of Clifford-dominated circuits](https://arxiv.org/abs/1808.02406), shows the nearby rank/cancellation framework and its approximation boundary.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the exact relation predicate to be represented.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies complete addition charts.

No cited work gives an exact sub-rho quadratic-phase decomposition of generic elliptic
membership with source recovery; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, exact bit/field encoding, factor base, arity, and phase coefficient ring.
2. Compile complete addition and factor-base membership into exact algebraic constraints.
3. Decompose the resulting indicator into quadratic phases and verify equality exhaustively on tiny curves.
4. Contract the phase sum for known `R=[a]P` and condition variables to recover each source point.
5. Independently verify membership and `sum_i P_i=R`; retain all cancellations, misses, and ambiguities.
6. Collect enough independent rows and solve factor-base logarithms.
7. Repeat unchanged on `Q+[t]P`, recover a verified decomposition, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho has `N^(1/2+o(1))` time and constant state; BSGS has
`N^(1/2+o(1))` time and memory. Let phase rank `R=N^r`, build/storage exponents
`a,s`, per-phase contraction exponent `c`, conditioning overhead `N^h`, reciprocal
relation and descent densities `N^delta,N^delta_t`, and `B=N^beta`. Then
one source-resolving query costs `N^q` with `q=r+c+h`,
`T_rel=N^(beta+delta+q+o(1))`,
`T_LA=N^(2beta+o(1))`,
`T_desc=N^(delta_t+q+o(1))`,
`lambda=max(a,beta+delta+q,2beta,delta_t+q)`, and
`mu=max(s,beta,r)`. Approximate rank or uncharged cancellation precision cannot enter these bounds.

## Likely fatal obstruction

The exact phase rank may inherit the known balanced ordinary-rank floor, or the
cyclotomic precision needed to prevent cancellation errors may grow as `N^(1/2)`.
Conditioning can also multiply rank by `B`. Thus a compact count could coexist with
rho-scale witness recovery.

## Proof track

Exhibit the exact phase identity and coefficient ring, prove a subcritical rank bound,
complete chart coverage, exact conditional-marginal witness recovery, and end-to-end
`lambda,mu<1/2` including precision and verification.

## Disproof track

Prove an exact phase-rank or coefficient-height lower bound, show conditioned rank grows
to `N^(1/2-o(1))`, find reproducible cancellation errors, or establish
`lambda>=1/2` for all frozen arms.

## Positive and negative controls

- Positive control: a planted low-stabilizer-rank signature with exact known witnesses.
- Positive correctness control: exhaustive decomposition truth on tiny curves.
- Negative control: matched random sparse tensors and coefficient-shuffled addition laws.
- Rank control: ordinary flattening rank and generic tensor-network contraction on the same tensors.
- Leakage control: forbid approximate amplitudes, scalar advice, target-selected phases, tuple tables, and discarded zero contractions.

## Quantitative promotion and falsification gates

Use at least 20 curves per size from 9 through 22 bits and two independent encodings.
Promotion requires exact equality on exhaustive cells, zero false witnesses, at least
1,000 verified relations and 100 descents at the two largest sizes, upper 95%
`r<=0.20`, `q<=0.20`, `a<=0.45`, `lambda<=0.45`, and `mu<=0.45`, with
coefficient height fully charged and stable leave-largest-size-out fits. Falsify on an
exact symbolic mismatch, any independently reproduced false witness, lower 95%
`r>=0.50` or `q>=0.50`, or full-cost lower 95% `lambda>=0.50` in every arm.

## Artifact plan

- Decomposer: `ideas/artifacts/ECDLP-IDEA-058/phase_decomposer.sage`
- Exact verifier: `ideas/artifacts/ECDLP-IDEA-058/verify_phase_identity.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-058/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-058/analysis.md`
- Retain tensors, phases, coefficient heights, witnesses, misses, seeds, commands, environment, commit, timing, memory, stdout, and stderr.

## Interpretation boundary

The hypothesis is toy, heuristic, model-bound, and novelty-unverified. Correct phase
identities, low approximate rank, or relation validity do not establish an ECDLP speedup.

## Exactly one next executable action

1. Derive and machine-check a symbolic generic complete two-addition quadratic-phase identity with exact conditioned source marginals, without truncation or approximation.
