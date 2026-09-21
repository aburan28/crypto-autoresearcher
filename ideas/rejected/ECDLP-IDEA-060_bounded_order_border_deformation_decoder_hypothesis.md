# ECDLP-IDEA-060 — Bounded-order border-deformation decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `merged_rejected_generic_tensor_backend`
- Evidence scale: `toy` symbolic degeneration only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a border-rank degeneration or valid limiting relation is not a break.

## Falsifiable hypothesis

The exact elliptic decomposition tensor has a public degeneration
`T(epsilon)=sum_{j=1}^R A_j(epsilon)` with `R=N^(r+o(1))`, `r<1/2`, whose desired
coefficient occurs at interpolation order `D=N^(d+o(1))` and satisfies `r+d<1/2`.
Exact bounded-order interpolation plus conditioned contractions recovers source points
with complete time and memory below rho/BSGS.

## Mechanism-new operation

The operation is a **bounded-order exact border degeneration with a source decoder**.
Approximate bilinear terms are evaluated at certified parameter values, interpolated
exactly to the elliptic tensor coefficient, and conditioned to recover indices. Border
rank alone, numerical approximation, generic tensor contraction, solver substitution,
or relation-only interpolation is a control.

## Assumptions

1. `E(F_p)` has prime subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. The factor base `F` is deterministic with `B=N^beta`.
3. The degeneration is public, target-independent, exact over a specified ring, and covers all charts.
4. Coefficient height, interpolation points, order, rank, and conditioned witness overhead are charged.
5. Source recovery needs no explicit `B^m` table or scalar advice.
6. Scaling claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_decomposition_tensor | exact_border_degeneration | bounded_interpolation_order | conditioned_contraction | source_witness_recovery`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — blocks representation changes without total-cost gain.
2. `ledger/EV-REP-001.yaml` — supplies exact representation controls.
3. `ledger/EV-REP-002.yaml` — supplies rank and scaling evidence.
4. `ledger/FINDING-PF-IC-001.md` — fixes the membership baseline.
5. `ledger/SYNTHESIS-20260716.md` — requires end-to-end source recovery and descent.

## Closest primary literature

- Bini, Capovani, Lotti, and Romani, [O(n^2.7799) complexity for n x n approximate matrix multiplication](https://doi.org/10.1016/0020-0190(79)90113-3), introduces approximate/border algorithms.
- Bini, [Relations between exact and approximate bilinear algorithms](https://doi.org/10.1137/0209053), gives exact interpolation overhead for approximate bilinear schemes.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the elliptic relation tensor.
- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), supplies exact addition-chart coverage.

No source gives the required low-order elliptic degeneration with source recovery.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,m,beta,F`, exact tensor encoding, coefficient ring, and parameter points.
2. Construct and symbolically verify the degeneration through order `D` on every chart.
3. Contract each rank-one term for known `R=[a]P` and interpolate the exact relation coefficient.
4. Condition contractions to recover sources and independently verify factor-base membership and sums.
5. Collect independent rows and solve factor-base logarithms.
6. Apply unchanged to `Q+[t]P`, recover sources, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho is `N^(1/2+o(1))` time with constant state; BSGS is
`N^(1/2+o(1))` time and memory. Let degeneration rank `N^r`, interpolation order
`N^d`, per-term contraction/conditioning `N^c`, build/storage `a,s`, reciprocal
densities `delta,delta_t`, and `B=N^beta`. Query exponent `q=r+d+c`, so
`lambda=max(a,beta+delta+q,2beta,delta_t+q)` and
`mu=max(s,beta,r+d)`. Precision, coefficient height, every interpolation point, and all
failed conditionings are charged.

## Likely fatal obstruction

Exactification may require interpolation order or coefficient height that cancels the
border-rank saving; conditioned source recovery can restore the exact balanced-rank
floor. Thus `r+d+c>=1/2` even if the formal border rank is small.

## Proof track

Exhibit the exact degeneration, prove bounded interpolation order and coefficient height,
complete chart and witness recovery, and derive full `lambda,mu<1/2`.

## Disproof track

Prove exactification or conditioning restores `N^(1/2-o(1))` rank/order, find an exact
coefficient mismatch, or show every frozen arm has `lambda>=1/2`.

## Positive and negative controls

- Positive control: a known approximate matrix product with exact bounded interpolation.
- Positive correctness control: exhaustive tiny-curve tensor entries and decompositions.
- Negative control: random tensors with matched dimensions and sparsity.
- Mechanism control: exact tensor rank and generic tensor-network contraction.
- Leakage control: forbid numerical rounding, target-dependent degeneration, post-hoc interpolation order, and tuple tables.

## Quantitative promotion and falsification gates

Reconsideration requires an explicit elliptic degeneration proving `r+d<1/2` and exact
source conditioning before any backend experiment. A later study would require zero coefficient/witness errors, 20 curves
per size, 1,000 relations and 100 descents, upper 95% `q<=0.20`,
`lambda<=0.45`, and `mu<=0.45`. Reject on a generic mismatch, required
`r+d+c>=1/2`, coefficient bit-size exponent at least `1/2`, or lower 95%
`lambda>=0.50`.

## Artifact plan

- Degeneration: `ideas/artifacts/ECDLP-IDEA-060/border_deformation.md`
- Exact checker: `ideas/artifacts/ECDLP-IDEA-060/check_interpolation.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-060/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-060/analysis.md`
- Retain exact decompositions, interpolation orders, coefficient heights, witnesses,
  failures, seeds, commands, environment, commit, timing, memory, stdout, and stderr.

## Interpretation boundary

This rejected claim is toy, heuristic, model-bound, and novelty-unverified. A low border
rank, exact coefficient, or valid relation cannot establish an ECDLP speedup without
source recovery and full rho/BSGS accounting.

## Exactly one next executable action

1. Compute the exact interpolation order of the smallest complete balanced elliptic relation tensor under the proposed one-parameter degeneration.
