# EXP-MONO-005b49 implementation notes

Executor: Claude Code, `executor` role, `executor-implementation` policy,
`medium` reasoning effort. Handoff: `ledger/handoffs/TASK-20260904-9abe5a.yaml`.
Source: `experiments/EXP-MONO-005b49/implementation/run_experiment.py`
(single self-contained script, standard library + scipy only, no CAS, no
network; scipy used exclusively for the diagnostic-only P5 Fisher-exact
figure, never for the pre-registered P3 test).

## Code reuse discipline (per the handoff's `reused_frozen_artifacts`)

- `experiments/EXP-MONO-64aaa4/implementation/run_experiment.py` is loaded
  **read-only, by file path** (`importlib.util.spec_from_file_location`),
  never copied or edited. Its `construct_ordinary`, `construct_cm_j0`,
  `construct_cm_j1728`, `is_prime`, `primes_in_range`, `build_factor_base`,
  `measure_curve`, `SIGN_CLASSES`, `NCLASSES`, and `fisher_exact_2x2` are
  called directly from the loaded module object. This is the exact pattern
  `EXP-MONO-cb905d`'s own `run_experiment_v2_part_a_corrected.py` used to
  reuse the same file.
- `experiments/EXP-MONO-cb905d/implementation/run_experiment_v2_part_a_corrected.py`
  is loaded the same way, for its `measure_group_uniform_v2` function (which
  itself calls `sample_group_uniform_v2_corrected`, the amendment v1
  construction). The deprecated `sample_group_uniform_v1_biased` defined in
  that same file is never imported or invoked here.
- Domain separation: this script sets the loaded EXP-MONO-64aaa4 module's
  `DOMAIN` global to `"EXP-MONO-005b49/v1"` (this contract's own declared
  `inputs.domain`) before any Stage-0/1 draw, so every seed stream here is
  disjoint from EXP-MONO-64aaa4's own runs and from EXP-MONO-cb905d's own
  runs (v1 and v2 domains). This is the identical mechanism
  EXP-MONO-cb905d's own v2 script used relative to v1's domain
  (`m64.DOMAIN = CB_DOMAIN_V2`).

## Stage 0: search procedure and outcome

Ascending-p scan over `primes_in_range(3001, 20000)` (EXP-MONO-64aaa4's own
`is_prime`/`primes_in_range` helpers, unmodified), fixed in that order
*before* any search was run, per the contract's `stage_order.stage_0`. This
order is baked into the code as written (a plain `for p in primes:` loop
with no reordering, sorting, or filtering by later results) and was not
altered after seeing any result.

`p=617` was confirmed explicitly (in code, via an assertion-style check that
raises if false) to not fall in `[3001,20000]`; the exclusion is a no-op in
this range as the contract itself anticipated, and the check is recorded in
`raw-result.json.excluded_prime_in_range_check`.

**Outcome: a match was found at the 66th admissible prime scanned, p=3541**
(N=3600, tau=4, ordinary curve A=577/B=1628, CM candidate j=0, A=0/B=2728).
This is the FIRST match under the fixed ascending scan order; the loop
`break`s immediately on finding it, so no later prime in the range was ever
constructed or compared — there is no possibility of a "better" later match
having been seen and discarded.

## Stage 1: measurement

Both curves (ordinary at p=3541, CM j=0 at p=3541) were measured fresh under
both arms, 20000 tuples each, using:

- **Transversal arm**: `m64.measure_curve(curve, fb_info, 20000, "random",
  ...)`. EXP-MONO-64aaa4's own `implementation.md` item 4 established that,
  for this m=4/3-drawn-point construction, the `"fixed"` and `"random"` sign
  conventions are provably (not just empirically) identical — flipping any
  one point's sign only permutes which of the 4 canonical sign-classes
  computes which sum, never changing the multiset of resulting
  x-coordinates. A single arm (`"random"`) therefore suffices as *the*
  transversal measurement for this contract; running `"fixed"` as well
  would only reproduce byte-identical counts, adding no information. This
  choice is disclosed here rather than silently assumed.
- **Group-uniform arm**: `mcb.measure_group_uniform_v2(m64, curve, 20000,
  ...)`, i.e. amendment v1's corrected 2p+1-slot rejection sampler,
  byte-identical code reuse, no reimplementation.

Both arms use fresh draws (there is no prior run for this cell to reuse
counts from, unlike EXP-MONO-cb905d's own reuse of RUN-1's transversal
counts for its p=617 cell).

Raw counts (pairs-colliding out of 20000 tuples, both curves, both arms):

| | transversal | group-uniform |
|---|---|---|
| ordinary (A=577,B=1628) | 98 | 233 |
| CM j=0 (A=0,B=2728) | 94 | 201 |

## Stage 2: the sole pre-registered test

Computed exactly as `significance_test_pre_registered_before_any_draw`
specifies, using only `math.log`, `math.sqrt`, and `math.erf` (standard
library; `Phi(x) = 0.5*(1+erf(x/sqrt(2)))`), with **no** scipy dependency
for this headline statistic:

```
P1 = (233/20000) / (98/20000)  = 2.377551...
P2 = (201/20000) / (94/20000)  = 2.138298...
log_ratio = log(P1/P2)          = 0.106061
var_logP1 = 1/233 + 1/98        = 0.014496
var_logP2 = 1/201 + 1/94        = 0.015613
se = sqrt(var_logP1+var_logP2)  = 0.173520
z = log_ratio / se              = 0.611230
two_sided_p = 2*(1-Phi(|z|))    = 0.541048
```

P4 (direction check): P1 (2.3776) > P2 (2.1383) — same direction as the
first cell's own P1 > P2 finding (P1=2.398 at p=617, per the contract's own
`claim_ceiling.exact_scope_a_run_could_support` text).

A diagnostic-only, explicitly labeled same-curve Fisher-exact test on the
group-uniform arm's per-tuple any-collision indicator is also reported
(`stage2.P5_diagnostic_only_KNOWN_DEFECTIVE_per_CORR_20260904_d0205d`),
labeled per the contract's own instruction as known-defective and
diagnostic-only, never as a competing headline: odds ratio 1.107, p=0.398,
not significant at 0.05.

No other test, substitution, or "improved" statistic was computed or
considered for the headline P3 figure.

## Deviations / anomalies log

- None. No timeout, crash, construction failure, or budget breach occurred.
  Total wall time ~8.2 seconds (well under the 3600s hard budget and the
  2700s Stage-0 soft deadline this script itself imposed to leave headroom
  for Stage 1/2). No hypothesis, experiment, or goal status changed by this
  script or this executor session.
- The Stage-0 soft deadline value (2700s) is this script's own choice
  (not specified numerically by the contract, which only fixes the overall
  3600s hard budget); it is disclosed here as an implementation-level
  timing choice, analogous to EXP-MONO-64aaa4's own 1800s soft deadline
  choice under its own 3600s hard budget. It did not bind in this run
  (Stage 0 finished in 0.32s).
