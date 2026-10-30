# Protocol: is prime239v1's L(1, χ) ordinary?

Committed and pushed **before** any study curve's L-value or weighted
statistic is computed. Pilot measurements made before this commit used
synthetic discriminants only (class-number timing, below).

## Question

`papers/nist-seed-split-null/paper.md` §6 leaves open whether prime239v1's
low split count (S = 42 at B = 691, 0.06th percentile) reflects a small
L(1, χ_{D_K}) or only low early Euler factors. This study answers:

- **Q1 (primary).** Is log L(1, χ_{D_K}) for prime239v1 ordinary under the
  prime-order Frobenius null?
- **Q2.** Were its early Euler factors low? Percentile of the weighted
  statistic E(B) = −Σ_{3≤ℓ≤B} log(1 − χ_Δ(ℓ)/ℓ) at B = 691, and at
  B ∈ {101, 251, 397, 997, 2003, 5003} (descriptive).
- **Q3 (descriptive).** How log L splits into ℓ = 2, 3 ≤ ℓ ≤ 691, and ℓ > 691.

## Population

The same 61 curves as the held-out test of
`research/nist_seed_split_null_20261029/` (`heldout.py`, same three input
files): the 19 named curves and the 42 held-out unpublished draft-eligible
curves in the 192-, 224-, 239- and 256-bit fields. P-384 is excluded.

## Estimator

Exact class numbers are infeasible here. Pilot (synthetic prime |D|, PARI
2.17.2 `quadclassunit`, one thread): 0.86 s at 100 bits, 6.6 s at 120,
38 s at 140, more than 10 min at 192, extrapolating to roughly a day per
241-bit discriminant.

So L(1, χ_{D_K}) is estimated by the Euler product truncated at
x = 10⁸: log L̂ = −Σ_{ℓ≤x} log(1 − χ_{D_K}(ℓ)/ℓ), with χ_{D_K} the Kronecker
symbol. Here D_K comes from PARI `coredisc(Δ)` (complete factorization of
Δ = t² − 4p, checked against the conductor census for the named curves).
Under GRH the truncation error is of order log|D_K| / (√x log x), about
10⁻³. That is an expected scale, not a proved bound. The change from x = 10⁷
to 10⁸ is reported for every curve.

## Null

Frobenius mod ℓ is uniform in GL₂(F_ℓ) with determinant p, excluding
eigenvalue 1 (prime order), independently across ℓ. This is the law in
`analysis_lib.probs`, which gives P(χ = +1), P(χ = 0) and P(χ = −1) per
(p, ℓ). χ(2) = −1 is deterministic for odd prime order (Δ ≡ 5 mod 8) and
enters every arm identically.

- Null for log L: Monte Carlo over 3 ≤ ℓ ≤ 10⁵, 200,000 draws per field,
  seed 20261030. The ℓ > 10⁵ contribution has variance below 10⁻⁵ and is
  added from the observed curve.
- Null for E(B): the same draws, truncated at B.
- Position: mid-percentile, 100·(P(X < x) + P(X = x)/2), estimated from
  the draws.

## Decision rule (Q1)

prime239v1's L-value is **ordinary** if its log L mid-percentile lies in
[2.5, 97.5]. It is **low** if below 1, and **borderline** in between.
Its rank among the 61 curves is reported as descriptive.

## Controls

- **Positive (estimator).** Twenty random fundamental discriminants
  −D ≡ 1 (mod 4), five each at 80, 90, 100 and 110 bits (seed 20261030). For
  each, compare exact L = π h / √|D| (PARI `quadclassunit`; `qfbclassno` at
  80 bits) with L̂ at x = 10⁸. Pass if every |log L̂ − log L| ≤ 0.01.
- **Positive (χ).** For the 19 named curves, the count of +1 values of the
  vectorized χ_Δ over 3 ≤ ℓ ≤ 691 must equal the committed S in
  `research/nist_seed_split_null_20261029/runs/heldout.json`.
- **A/A (implementation).** For prime239v1 and two other curves, the vectorized
  χ must equal Python `pow`-based χ at every ℓ ≤ 10⁶.
- **A/A (Monte Carlo).** A second seed (20261031) gives prime239v1's
  percentiles. They must agree within 3 binomial standard errors.
- **Null calibration.** KS of the 42 held-out log-L percentiles against
  uniform, reported.

## Outputs

`runs/` holds `controls.json`, `lvalues.json` (per curve: D_K, f_π, log L̂
at 10⁶, 10⁷, 10⁸, E(B) at each cutoff, the percentiles) and `rows.jsonl`.
Also: a report, a figure and a PDF.

## Deviations

Any deviation goes in `DEVIATIONS.md` with its reason.
