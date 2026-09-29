# Implementation notes: EXP-MONO-715694

Census-convergence power analysis (S_4 vs A_4, S_4 vs D_4), executed under
handoff `TASK-20260830-75c1c0` against the frozen contract at
`experiments/EXP-MONO-715694/specification.yaml`.

Source: `experiments/EXP-MONO-715694/implementation/run_experiment.py`
(pure Python 3 stdlib only: `sys`, `os`, `json`, `math`, `time`, `random`,
`itertools`, `collections.Counter`). No numpy/scipy/sympy/sage.

## Design overview

1. **Stage 0** (`stage0_exact_tables`): brute-force enumerate all 24
   permutations of `{0,1,2,3}` via `itertools.permutations`, cycle-decompose
   each by tracing point orbits (`cycle_type_of_perm`, a mechanical trace, no
   permutation-group library), and tabulate into the 5-way cycle-type space.
   Parity (for A_4 membership) is computed by counting inversions, also with
   no library. Hard-asserts the forced totals `[1,6,3,8,6]/24` (S_4) and
   `[1,0,3,8,0]/12` (A_4) before anything else runs; any mismatch raises
   `AssertionError` and the run would be `failed_infrastructure`.

2. **Stage 0b** (`stage0b_d4_law`): reads `N1_k1_exhaustive.jsonl` from BOTH
   `RUN-MONO-a20e48-1` and `RUN-MONO-a20e48-2`, excludes rows with
   `class is None` (ramified), cycle-decomposes every remaining row's `perm`
   field independently of its `class` label (per the handoff's explicit
   instruction not to trust the `class` field name), and tabulates. Hard
   gate: raises `AssertionError` if any 3-cycle is found, if the
   non-ramified row count is not exactly 44,310 in either run, or if the two
   runs' derived counts disagree. All three passed on both executed runs.

3. **Stage 1 (NULL controls)**: `null1_check` runs the identical Stage-2
   procedure with `sub_law = s4_law` (an independent second S_4 stream) at
   N in `{10,100,1000,10000,44310,100000}`. `null2_check` reports the
   calibrated false-positive rate at N in `{100,1000,10000,44310}`.

4. **Stage 2 (N_required search)**: `doubling_bisection_search` doubles N
   from 10 up to `search_ceiling_N=100000`, calibrating a threshold from
   20,000 S_4-generated trials and measuring power on 20,000
   subgroup-generated trials at each candidate N, then bisects between the
   last non-passing and first-passing N once `power >= 0.99` is first
   crossed.

5. **Stage 3 / Step 4a**: `bootstrap_power_curve_with_thresholds` resamples
   WITH REPLACEMENT directly from the real 44,310-point N1 pool (run 1) at
   every N in the Stage-2 S4-vs-D4 search grid, 1,000 replicates per N, using
   the SAME threshold calibrated in Stage 2 at that N, and reports the gap
   against the synthetic Monte Carlo power at the same N.

6. **Stage 3 / Step 4b**: classifies N3's real S=2,000 histogram (both runs)
   and N1's real 44,310-point histogram (both runs) under both pairwise
   tests, using the threshold calibrated at N=2000 (for N3) and N=44310 (for
   N1); since neither of those exact N values was already in the Stage-2
   search grid (the grid landed on N=10 only -- see below), both thresholds
   were RECALIBRATED exactly at N=2000 and N=44310 respectively, using the
   same seeded procedure, and this recalibration is recorded in
   `raw-result.json.step4b.threshold_source` (`"recalibrated": true`).

## Performance: exact multinomial sampling instead of per-draw categorical sampling

The frozen contract specifies "20,000 independent length-N i.i.d. samples"
for N up to 100,000. Drawing N categorical samples one at a time in a Python
loop (`sample_cycle_type_index` + accumulate into a 5-bin count vector) costs
O(N) per sample; at N=100,000 and 20,000 trials per side per candidate N,
this is >=4e9 elementary Python-level operations for a SINGLE candidate N,
which is infeasible within the 1800s wall-clock budget (a single such batch
alone was estimated at many minutes to hours in pure Python, and the search
grid visits multiple N values).

Because the N draws in each sample are i.i.d. from a fixed 5-category law,
the resulting count vector is EXACTLY `Multinomial(N, law)` in distribution
-- this is a standard fact, not an approximation. `multinomial_counts`
generates an exact multinomial draw via sequential conditional binomial
sampling (`n_1 ~ Binomial(N, p_1)`; given `n_1`, `n_2 ~ Binomial(N-n_1,
p_2/(1-p_1))`; etc.), using Python 3.12+ stdlib `random.Random.binomialvariate`
(part of the standard `random` module, not an external dependency). This
reduces the cost of drawing one length-N sample from O(N) to O(k)=O(5),
regardless of N, and produces the identical target distribution as the
literal per-draw procedure the contract describes. This is a performance
optimization only, disclosed here for auditability; both runs completed in
~2.3 seconds wall-clock, far under the 1800-second budget.

Step 4a's bootstrap resampling is implemented literally as specified
(`random.Random.choices` against the real, ordered pool of 44,310
cycle-type labels, with replacement) rather than via the multinomial
shortcut, because the frozen contract explicitly requires resampling
"directly from the real ... data points" as the test of whether the real
census has any correlation structure the i.i.d. simulation model misses.
`random.Random.choices` is used instead of a hand-written
`randrange`-per-element loop purely as a stdlib-internal performance detail
(same sampling distribution, C-optimized loop); this made bootstrapping the
full search grid (including N up to 100,000, larger than the population
itself, which is a legitimate with-replacement draw) complete in well under
a second.

## Direction-of-rejection: a disclosed judgment call on an internally ambiguous instruction

The handoff's task description contains two mutually inconsistent statements
about which tail of the LR statistic should be the rejection region:

- "Calibrate a rejection threshold ... so that the empirical false-positive
  rate (fraction of S_4-generated LR values below the threshold, **since a
  lower/more-negative LR favors 'it's the subgroup'**) is close to
  alpha=0.05."
- "if a cycle type has zero probability under P_sub ... and is observed even
  once in an S_4-generated sample, the log-likelihood-ratio is -infinity,
  which should be treated as **an immediate, maximally confident vote for
  'it's S_4'**."

These two statements contradict each other: the first says LOW/negative LR
means "it's the subgroup"; the second says a maximally-negative LR
(-infinity) means "it's S_4". Working through the actual arithmetic of
`LR = sum_i n_i * log(P_sub(i)/P_full(i))`:

- Under true S_4 data (`n_i` drawn from `P_full`),
  `E[LR] = -D_KL(P_full || P_sub)`. Because both tested subgroups (A_4, D_4)
  have strictly narrower cycle-type support than S_4, `D_KL(P_full||P_sub)`
  is `+infinity` in the exact sense used here (a category with `P_full>0,
  P_sub=0` gives an infinite penalty the moment it's observed) -- so real
  S_4 data drives `LR` to a large NEGATIVE value, exactly matching the
  second (NEG_INF_CAP) instruction's stated intent.
- Under true subgroup data (`n_i` drawn from `P_sub`, which never produces a
  forbidden category), `E[LR] = +D_KL(P_sub || P_full) >= 0`, a finite,
  non-negative quantity -- subgroup data drives `LR` toward positive values.

This is also the standard Neyman-Pearson convention: reject the null in
favor of the alternative when the likelihood ratio of alternative-over-null
is LARGE, not small. Given the direct contradiction in the handoff text, this
Executor followed the interpretation that is (a) internally consistent with
the handoff's own explicit, unambiguous NEG_INF_CAP worked example, and (b)
the only interpretation consistent with the stated LR formula's arithmetic.
Implemented rule: **`LR > threshold` classifies as "it's the subgroup"**;
threshold = the empirical `(1-alpha)` quantile (95th percentile, not 5th) of
the S_4-generated LR distribution. This is disclosed here in full rather
than silently resolved, per AGENTS.md's requirement to record protocol
deviations; it does not touch any frozen numeric parameter (alpha=0.05,
target_power=0.99, `monte_carlo_trials_per_candidate_N`=20000), only the
direction of comparison needed to make the stated formula computable at all.

## The -infinity / NEG_INF_CAP edge case

Implemented via `NEG_INF_CAP = -1e18` rather than Python's `float('-inf')`
literal, per the handoff's own suggestion ("cap at a very large negative
number"). Rationale: `-1e18` is many orders of magnitude more extreme than
any achievable finite sum of at most 100,000 real log-ratio terms (each
finite term has magnitude at most `ln(24) ~= 3.2`, since the smallest
nonzero probability in play is `1/24`), so a single occurrence still
dominates any sum exactly as `-inf` would, while avoiding `-inf` arithmetic
edge cases (`-inf + finite = -inf` is fine, but sorting, percentile
interpolation, and JSON serialization of `-inf` are all more fragile than a
large finite sentinel). `lr_statistic_from_counts` explicitly detects when
any category with a `NEG_INF_CAP` log-ratio has nonzero count and returns
`NEG_INF_CAP` for the whole sum (rather than a possibly-finite but enormous
negative number from adding a large negative count-weighted term to other
finite terms), so the "immediate, maximally confident" semantics are exact,
not approximate.

## What Stage 2 actually found, and why the doubling-bisection search terminates at its own floor

The frozen contract's search starts doubling from **N=10** (its own stated
floor, `battery.STAGE2-N-REQUIRED-SEARCH` and `test_boundary.parameters`).
Both tested pairs (S_4-vs-A_4 and S_4-vs-D_4) already reach
**power = 1.0 (with Monte Carlo SE = 0.0 across 20,000 trials) at N=10**, the
very first grid point tested, in both runs. This is because a proper
subgroup that categorically excludes one or more S_4 cycle types (A_4
excludes transposition and 4-cycle, total excluded mass 0.5; D_4 excludes
3-cycle only, excluded mass 0.333) makes the LR statistic hit `NEG_INF_CAP`
for essentially every S_4-generated sample as soon as N is large enough that
observing at least one excluded-category draw is near-certain -- and N=10
is already far past that point for both pairs (`P(no excluded category in 10
S_4 draws)` is `0.5^10 ~= 0.001` for A_4 and `0.667^10 ~= 0.017` for D_4).
Consequently `doubling_bisection_search` returns `n_required=10` for BOTH
pairs on its very first evaluation, with no doubling or bisection needed
(the search never observes a non-passing N to bisect against, since the
floor itself already passes).

**Reported as an observation, not resolved by extending the search below the
contract's own floor**: the frozen contract's `preregistered_prediction` and
`falsification_conditions` explicitly anticipate and name this outcome --
"`N_required(S_4 vs D_4)` is NOT strictly greater than `N_required(S_4 vs
A_4)`" is listed verbatim as a falsification condition, and this Executor's
measured result (`N_required` tied at the search floor, 10, for both pairs)
triggers it. This Executor did not extend the search below N=10 to attempt
to force the predicted ordering to appear, since the contract's search
range (`N=10` to `search_ceiling_N=100000`) is a frozen parameter; doing so
would be exactly the kind of post-hoc re-selection the contract's
`invalidation_rules` forbid. The one place the predicted ordering DOES show
up, reported honestly as a secondary, non-primary metric, is the
Chernoff-Stein asymptotic cross-reference computed alongside the Monte Carlo
result: `D_KL(A_4 || S_4)`-based estimate ~= 10.97, `D_KL(D_4 || S_4)`-based
estimate ~= 13.82 (both using `alpha=0.05, beta=1-0.99=0.01`) -- an
order-of-magnitude sanity check, not a substitute for the Monte Carlo
result, that is consistent with the predicted direction even though the
actual Monte Carlo search (constrained to start at N=10) cannot resolve it
at that granularity. The empirical false-positive rate at N=10 also differs
by pair in the predicted direction (A_4: 0.0007; D_4: 0.01675, both well
under alpha=0.05), suggesting A_4 remains "easier" to distinguish even
though both already achieve nominal power=1.0, power_se=0.0 at the floor.

## NULL-1 / NULL-2 degenerate-but-correct result

Both NULL controls report `false_positive_rate = 0.0` at every tested N (not
approximately `alpha=0.05`). This is the CORRECT, non-buggy answer for this
specific construction: NULL-1/NULL-2 set `sub_law = full_law` (the literal
same Python list, `s4_law`), so `log(P_sub(c)/P_full(c)) = log(1) = 0`
EXACTLY for every category -- the LR statistic is identically `0.0` for
every possible draw, regardless of N or which of the two "independent S_4
streams" generated the data (since the statistic is a function only of the
observed counts and the two IDENTICAL probability tables, not of which
stream the counts came from). The calibrated threshold is therefore also
exactly `0.0`, and with the implemented `LR > threshold` rejection rule, no
value can be strictly greater than the value that IS the threshold itself
(when, as here, the entire distribution is a point mass at that value), so
`false_positive_rate = 0.0` follows from the test statistic's own
degenerate-but-mathematically-correct behavior when the two hypotheses being
compared are literally identical. This trivially satisfies the contract's
NULL-1 success condition ("A materially nonzero apparent separation rate
above alpha=0.05 ... means the test construction is broken") -- 0.0 is not
above 0.05 -- but is reported here with its mechanism made explicit rather
than left as an unexplained zero.

## Threshold recalibration at N=2000 and N=44310 for Step 4b

Since the Stage-2 search grid for both pairs contains only N=10 (see above),
neither N=2000 (needed to classify N3's real S=2,000 sample under the
Stage-2-calibrated threshold) nor N=44310 (needed for the N1 sanity check)
was already present in the grid. Per the contract's explicit fallback
("using the SAME thresholds you calibrated in Stage 2 at N=2000, or
recalibrate exactly at N=2000 if 2000 isn't already one of your search grid
points -- document which"), both thresholds were recalibrated exactly at
N=2000 and N=44310 respectively, using the identical seeded calibration
procedure (`calibrate_and_measure_power`) as Stage 2, with a domain-tagged
seed distinct from the Stage-2 grid points. This is recorded per-run in
`raw-result.json.step4b.threshold_source` with `"recalibrated": true` for
all four thresholds used in Step 4b.

## Protocol deviations summary

1. Exact multinomial sampling (`random.Random.binomialvariate`, stdlib)
   substituted for literal per-draw categorical sampling, for performance;
   mathematically identical target distribution (see above).
2. `random.Random.choices` (stdlib) used for the Step 4a bootstrap draw
   instead of a manual per-element `randrange` loop; identical sampling
   distribution, faster C-level implementation.
3. Rejection-region direction (`LR > threshold` favors "it's the subgroup")
   resolved in favor of internal mathematical consistency with the
   handoff's own NEG_INF_CAP instruction, over a separate, contradictory
   prose aside in the same handoff (see full derivation above).
4. Threshold recalibration at N=2000 and N=44310 for Step 4b, since neither
   was already a Stage-2 grid point (contract-anticipated fallback, used and
   disclosed as instructed).
5. `N_required` for both pairs saturates at the contract's own search floor
   (N=10), so the contract's central ordering prediction
   (`N_required(D4) > N_required(A4)`) is NOT confirmed by the primary
   Monte Carlo metric at this search resolution -- reported as the record's
   own headline finding per the contract's `falsification_conditions`, not
   worked around by extending the search range.

No crash, timeout, or infrastructure failure occurred in either run. Both
runs completed in ~2.3 seconds wall-clock (well under the 1800-second
budget) and ~24MB peak RSS (well under the 2GB budget).
