# EXP-ECDLP-e36df2 design note

Status: DRAFT, being filled in as the run completes. This note documents
the s_y and s_rand constructions, the cross-prime screen's exact
definition, and the H2 empirical base-rate tabulation, per
specification.yaml `required_artifacts`.

## 1. s_x, s_y, s_rand constructions (code: `driver/sections.py`)

- **s_x** (`sections.s_x_section`): reuses
  `EXP-ECDLP-a26bde/driver/instrument.py`'s `teichmuller_section`
  UNMODIFIED, imported read-only via `driver/frozen_ref.py`. Teichmuller-lifts
  the x-coordinate to the unique (p-1)-th root of unity congruent to it mod
  p, then Hensel-lifts the matching-branch y from the curve equation.

- **s_y** (`sections.s_y_section`, NEW, independently coded): the mirror
  construction -- Teichmuller-lifts the y-coordinate
  (`frozen_ref.teichmuller_lift_scalar`, reused unmodified on a different
  input), then Hensel-Newton-lifts a root x of the cubic
  `x^3 + A x + (B - y_t^2) = 0` starting from the known mod-p root
  (`sections._hensel_lift_cubic_root`, new code, doubling precision each
  Newton step exactly like `frozen_ref.hensel_lift_sqrt`'s own iteration,
  applied to a different polynomial). Requires `f'(x0) = 3x0^2+A` to be a
  unit mod p (checked; failure raises `ValueError`, counted as a
  precision/degeneracy exclusion for that m, never silently substituted).

- **s_rand** (`sections.s_rand_section`, NEW): seeded pseudorandom-digit
  null object per `docs/inventor-protocol.md` section 3. `x' = x0 + p *
  PRNG(seed, curve_idx, p, m) mod p^(K-1)`, where PRNG is a SHA-256-based
  deterministic counter construction (`sections._prng_digit_mod`, stable
  across Python versions, unlike `random.Random`'s internal state layout);
  y is Hensel-lifted from x' with the branch fixed by the true y0 mod p.
  x' agrees with the true point only mod p; every higher digit is
  pseudorandom noise with no relationship to the true global lift, which is
  exactly the null-object property the control needs.

## 2. Cross-prime screen (code: `driver/instance_runner.py::run_curve`)

For a curve with primes p_1..p_k, at multiple m: `[m]S mod p_i^K` is
computed for EVERY prime of the curve (via `padic.pmul`, never exact
Fraction arithmetic in Stage 2). m is **x-degenerate** iff
`x([m]S) mod p_i in {1, p_i-1}` holds simultaneously for every p_i with
data at that m; **y-degenerate** is the symmetric condition on the
y-coordinate. Flagged m are excluded from that section's (s_x's or s_y's)
primary agreement statistic for every instance of that curve, and recorded
in the flagged-multiple census (`flagged_x_degenerate_m` /
`flagged_y_degenerate_m` in each run's raw-result.json, restricted to
`m <= that instance's own N_i+1`).

Design decision (recorded, not silently made): because a curve's 4 primes
are all drawn from a tight ~[2^10,2^14) range (typically within a few
hundred of each other, per `curves.py`'s seeded search), `N_i` differs only
slightly across a curve's primes. The screen is evaluated at every
`m in [2, max(N_i over the curve's primes)+1]`, i.e. every prime's
x(mS)/y(mS) mod p_i is computed even slightly beyond that prime's own
`N_i` where a curve-sibling prime's ladder runs longer, purely so the
screen has data from every prime at every candidate m. This is a small
extension (bounded by the primes' spread within the curve), not a
per-prime ladder change.

**On-curve verification and precision escalation:** every `[m]S mod p^K`
is checked against the curve equation at the achieved precision; on
failure the point is recomputed at escalating margins (40, 60, 75, matching
`instrument.split_point`'s own escalation pattern) before being accepted;
if all three margins fail, that m is `attempted_and_inconclusive`
(`n_precision_insufficient`), never a silently wrong digit or a negative
finding.

## 3. Performance optimization: `driver/fastseries.py` (NOT a change to the
frozen digit machinery)

`instrument.eval_series_mod` re-reduces the formal group's ~81 Fraction
coefficients (one modular inverse each) on every call -- fine at a26bde's
68-value ladder, prohibitive at this ladder's O(10^4-10^5) calls per
instance. `fastseries.reduce_series_once` precomputes the reduced
coefficient list ONCE per instance using the unmodified
`instrument.reduce_fraction_mod`; `fastseries.fast_eval_reduced` then
repeats `eval_series_mod`'s own Horner recurrence on that cached list.
`fastseries.self_check_equivalence` is run at the start of every instance
and asserts bit-identical output against the frozen `eval_series_mod` (both
at the instance's full precision and at derived lower moduli) before the
fast path is trusted; a failure would raise and halt that instance rather
than silently using a wrong value.

## 4. H2 empirical base-rate tabulation

H2 (heuristic_assumptions in H-ECDLP-09125b) predicts the per-prime base
rate of `x(mS) mod p_i in {1, p_i-1}` is close to 2/p_i. This experiment's
flagged-multiple census (section 2 above) IS this tabulation, extended to
the new deep ladder; the pre-existing a26bde raw data (m<=256, 20
instances) was separately used only as the Stage 0 regression baseline
and is not re-mined for a base-rate count here (specification.yaml assigns
that extension to the new ladder; the a26bde-data comparison was already
performed at hypothesis-authoring time, cited in H-ECDLP-09125b's own
`heuristic_assumptions.H2.validation_plan`).

_(Final base-rate numbers filled in below once pooled-summary.json is
available.)_

## 5. Protocol deviations recorded

- Stage 0's "for m=2..256" is interpreted as the a26bde ladder's actual
  committed set (`curves.M_LADDER`, 68 values including m=1, of which 67
  are m>=2), not every integer in [2,256]: the committed raw-result.json
  files only ever stored digits for that sparse set, so an exhaustive
  integer sweep would not be a comparison against committed data (most
  values were never computed by a26bde) and would not be "free" (exact
  Fraction height grows with m regardless of ladder membership). See
  `driver/stage0_regression.py`'s module docstring.
- The Stage 3 falsification bar is stated two ways in specification.yaml
  (point estimate >=3 in the procedure text; CI lower bound >=3 in
  success_criterion/falsification_criterion). Both are reported in
  pooled-summary.json without the executor resolving the discrepancy.
- The mu0_target=40 sensitivity check (tail_checks) is run on curve idx=1
  (the smallest-prime original curve) rather than "a subset of instances"
  drawn from across all curves, to keep the added compute proportionate to
  a secondary tail check; this is the cheapest full curve to re-run at
  double N_i and is a genuine full re-run (not reused/interpolated from the
  mu0_target=20 run).
