# EXP-ECDLP-e36df2 design note

Status: FINAL (all 24 main instances + 4 sensitivity-check instances
completed; pooled-summary.json written). This note documents
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

**Result:** across all 24 main instances (deep ladders up to ~3.3x10^5
per instance), the cross-prime screen fired at exactly two places, both
already known/engineered: curve 2's m=2 (x-degenerate on all 4 of its
primes, the pre-existing a26bde finding) and the positive-control curve's
m=2 (x-degenerate on 4/4 of its primes, by construction). No other m,
curve, or prime produced a 4-of-4 (or k-of-k) cross-prime coincidence
anywhere in the extended ladders -- consistent with H2's negligible
false-positive-rate estimate (`flagged_degenerate_census_by_curve` in
pooled-summary.json is empty for curves 0, 1, 3, 4).

## 4b. Pooled results (from pooled-summary.json)

| section | k (pooled agreements) | mu0 | rho_hat | 95% CI | one-sided p (H0: rate=mu0) |
|---|---|---|---|---|---|
| s_x | 487 | 479.28 | 1.016 | [0.928, 1.110] | 0.368 |
| s_y | 471 | 479.28 | 0.983 | [0.896, 1.076] | 0.653 |
| s_rand | 514 | 479.28 | 1.072 | [0.982, 1.169] | 0.060 |

Both `joint_verdict_ci_lower_bound_ge_3` and `joint_verdict_point_estimate_ge_3`
read `not_falsified_by_this_bar` for both s_x and s_y (see the protocol
ambiguity note in section 5). s_rand's CI contains 1 (control passes: the
chance-level null model is not broken). The positive control's screen
flagged m=2 on 4/4 primes (`m2_flag_rate: "4/4"`), and its own
post-exclusion, restricted rho_hat (s_x=0.863, s_y=0.950, s_rand=1.025, all
CIs containing 1) reads like an ordinary instance, not an anomaly --
confirming the screen excludes only the named degeneracy and reports the
rest honestly. The mu0_target=40 sensitivity check (curve idx 1, the
smallest-prime curve, fully re-run at double N_i) reproduces the same
qualitative verdict (s_x=1.004, s_y=0.891, s_rand=1.073, all CIs containing
1, none near 3) -- the verdict is unchanged under this tail check.

## 4c. Chi-square diagnostic: resolved, mechanical artifact -- not a finding

`chi_square_by_instance` shows statistics 19x-730x their degrees of freedom
for s_x/s_y (e.g. curve 0/p=12853: statistic=245518 vs dof=12852, a ratio
of ~19.1; curve 3/p=14821,n=415: ratio much larger). This is NOT evidence
against H1 or a computation bug. Both s_x(mS) and t(mS) depend on m only
through m mod n (s_x depends only on mS mod p, and [m]S mod p is a group
element of order n, hence periodic in m with exact period n; t(mS) is
defined via pmul(m mod n, ...) explicitly), so their difference -- and
therefore the digit d(s_x(mS)) itself -- is EXACTLY periodic in m with
period n, not p. Verified directly (not merely inferred): for
curve 3/p=14821/n=415, computing d(s_x(mS)) at m in {2,3,7,100} and at
m+415 for each gives bit-identical digits every time
(`4293/4293, 4081/4081, 3074/3074, 12576/12576`). Since N_i = ceil(20 p)
generally exceeds n by a large factor when the point's order n is much
smaller than p (n as low as 415 against p=14821 for this instance), the
chi-square test's assumed model (N_i INDEPENDENT draws over p categories)
is the wrong null: the true independent-sample count is bounded by the
number of full periods, ~N_i/n, and the observed statistic-to-dof ratio
tracks N_i/n closely (spot-checked: a fresh 835-value ladder on this same
instance, 2.01 periods of n=415, gives a chi-square/dof ratio of ~2.08,
matching N_i/n to within ~3%). This does NOT affect the pooled rho_hat
statistic in section 4b: that statistic's target quantity, m * d(s(S)) mod
p, does NOT share the short period n (d(s(S)) is a nonzero residue mod p
with gcd(n,p)=1, so m*d(s(S)) mod p cycles through p distinct values over
n periods of m, not n values), and s_rand -- a section with zero structure
by construction and no reason to inherit this periodicity argument at all
-- lands in the same rho_hat range as s_x/s_y, an independent confirmation
that the agreement statistic itself is unaffected by the periodicity that
inflates the (separate, secondary) chi-square diagnostic. The chi-square
column in pooled-summary.json is retained as raw diagnostic data but
should be read against dof x (N_i/n), not dof, for a period-n section.

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
