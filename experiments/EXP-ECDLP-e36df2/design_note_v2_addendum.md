# Design note addendum: v2 new-curve extension (curve idx=6)

Authoring task: `TASK-20260921-9b17e4`. Protocol amendment:
`experiments/EXP-ECDLP-e36df2/amendments/v1_to_v2_new_curve_extension.yaml`
(`PA-ECDLP-e36df2-v1-to-v2`, status `approved`, `approved_by: coordinator`).
Evidence target: `H-ECDLP-c48f2a` only.

This addendum documents the v2 addition. It does not edit, and should be
read alongside without altering, `design_note.md` (the frozen v1 artifact
underlying `EV-ECDLP-5b61eb` / `DEC-20260912-2a626b` / `H-ECDLP-09125b`,
which this task does not touch).

## Curve selection

New, non-engineered curve, selected by the identical seeded search already
frozen for this experiment family (`_candidate_curves` /
`_find_primes_for_curve`, `experiments/EXP-ECDLP-a26bde/driver/curves.py`),
under seed `20260921` (new, distinct from `20260905` and `20260911`), one
candidate requested, `curve_idx=6`.

Selection script (new file, not a modification of any existing driver
file): `experiments/EXP-ECDLP-e36df2/driver/new_curve_c6_selection.py`. It
imports `_candidate_curves` via `frozen_ref.a26bde_curves` and
`find_primes_for_curve` via `frozen_ref.find_primes_for_curve` (the same
frozen re-export `driver/positive_control.py` already used for the
engineered positive control), so the search code itself is byte-identical
to what produced the original five curves and their primes.

Avoid-set actually used in the search: the required 6 existing curves'
`(A,B,x0,y0)` keys, plus (defensively, not required by the handoff)
the `a26bde` anomalous-pair curve, for 7 keys total:

| idx | A | B | x0 | y0 | source |
|---|---|---|---|---|---|
| 0 | 3 | -315 | 7 | 7 | EXP-ECDLP-a26bde/frozen_curves_and_primes.json |
| 1 | 9 | -801 | 9 | 3 | " |
| 2 | 9 | 26 | 1 | 6 | " |
| 3 | 2 | -54 | 5 | 9 | " |
| 4 | 9 | -134 | 5 | 6 | " |
| 5 (positive control, engineered) | 5 | 10 | 1 | 4 | frozen_positive_control_curve.json |
| (defensive extra, anomalous pair) | 9 | -397 | 7 | 3 | EXP-ECDLP-a26bde/frozen_curves_and_primes.json |

The search returned exactly one candidate on its first pass (no rejections
against the avoid-set were needed in practice; the candidate curve did not
collide with any of the 7 avoided keys). This candidate curve was **not**
engineered, hand-picked, or checked for any small-rational-torsion-like
coincidence — it is the ordinary output of the same random-search family
used for the original five curves, run once under the new seed.

Resulting curve: **A=1, B=-689, x0=9, y0=7** (curve_idx=6, seed=20260921,
`engineered: false`). Frozen, before any per-instance compute, to
`experiments/EXP-ECDLP-e36df2/frozen_new_curve_c6_seed20260921.json`.

## Prime selection

`find_primes_for_curve(A=1, B=-689, x0=9, y0=7, seed=20260921, curve_idx=6,
count=4)`, same criteria as every other curve in this experiment family:
`p` in `[2**10, 2**14)`, good ordinary reduction (`p` does not divide the
discriminant, trace not `0 mod p`), `#E(F_p) != p` (non-anomalous), and
`gcd(n, p) = 1` for `n` = order of the reduced point (asserted, not merely
assumed, exactly as `curves.py`'s own docstring specifies).

Primes found (all satisfied on the first pass through the seeded prime walk,
no exhaustion): **p = 2437, 2441, 2447, 2459** — all in the required bit
range (`2437.bit_length() == 12`). Full per-prime detail (order, trace, n)
is in `frozen_new_curve_c6_seed20260921.json`.

Compared with the original curves (whose primes ran up to ~2^14, giving
`N_i` up to ~3.3e5), this curve's primes landed near the low end of
`[2**10, 2**14)`, giving `N_i = ceil(20*p)` between 48,740 and 49,180 — a
genuinely smaller, cheaper instance set than most of the original six
curves. This is exactly what an unengineered seeded search over the fixed
bit range can produce and is not itself a deviation; no primes were
rejected or re-drawn to change this.

## Execution

Ran through the existing v1 compute path (`instance_runner.run_curve`,
`sections.py`, `fastseries.py`, `frozen_ref.py`) entirely unmodified, at
`mu0_target=20`, via a new top-level script
`experiments/EXP-ECDLP-e36df2/driver/orchestrate_new_curve_c6.py` (not a
modification of `orchestrate.py`, which hardcodes `SEED=20260905` for the
six v1 curves and could not be reused as-is for a curve under a different
seed; the new script calls the same functions the same way, only the
top-level seed/curve differ, as the amendment requires).

Produced `RUN-ECDLP-e36df2-029` through `-032`, one per prime, each with a
schema-complete `manifest.yaml` (command, commit `6b0d0ed25e92f466513eef000fa465521b9275f8`,
dirty: false, environment, inference block), `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json` — the
same required-artifact shape as runs 001–028. All 4 runs reached
`status: completed_valid` (certificate `kind: none`, as this is a pure
measurement run with no discrete-log or relation claim). Total wall-clock
for the 4-instance compute: 577.3s (well within the amendment's ~4460s
estimate); no infrastructure failure, timeout, or precision-margin
exhaustion occurred at any point.

Cross-prime `+-1`-degeneracy screen: **no `m` was flagged** on either the
`x` or `y` coordinate for this curve (`flagged_x_degenerate_m` and
`flagged_y_degenerate_m` are empty for all 4 instances) — unlike the
engineered positive control, which by construction flags `m=2` on all 4 of
its primes. This is expected for an unengineered curve and is reported as
an observation, not an interpretation.

## Pooled statistic (this curve only)

`experiments/EXP-ECDLP-e36df2/driver/pooled_summary_new_curve_c6.py`
(new file, reuses `poisson_stats.rho_hat_with_ci` / `poisson_sf`
unmodified — the same exact-Poisson CI and one-sided-p-value code as
`pooled_summary.py`) pools **only** `RUN-ECDLP-e36df2-029..032` and writes
`experiments/EXP-ECDLP-e36df2/pooled-summary-new-curve-c6.json`. It never
reads, edits, or re-derives totals into `pooled-summary.json`.

Result (95% exact-Poisson CI, one-sided p-value against `mu0`, `alpha=0.01`):

| section | k | mu0 | rho_hat | CI (95%) | one-sided p |
|---|---|---|---|---|---|
| s_x | 72 | 79.719 | 0.9032 | [0.7067, 1.1374] | 0.8207 |
| s_y | 65 | 79.719 | 0.8154 | [0.6293, 1.0392] | 0.9594 |
| s_rand | 66 | 79.719 | 0.8279 | [0.6403, 1.0533] | 0.9479 |

Neither joint-verdict reading (`ci_lower_bound_ge_3` or
`point_estimate_ge_3`) is triggered for `s_x` or `s_y`:
`not_falsified_by_this_bar` for both. `s_rand`'s 95% CI contains 1
(`s_rand_ci_contains_1: true`).

Per-instance chi-square statistics are large relative to their degrees of
freedom (e.g. curve 6 / p=2441: statistic ≈ 308,039 at dof=2440), the same
pattern already present throughout the original 24-instance pool (e.g.
curve 0 / p=12893: statistic ≈ 1,023,518 at dof=12892, in `pooled-summary.json`).
This is reported as consistent with the pre-existing pattern, not a new
anomaly specific to this curve; no interpretation of what it means for
either hypothesis is offered here.

**This pooled statistic is evidence for `H-ECDLP-c48f2a` alone.** Per
`PA-ECDLP-e36df2-v1-to-v2`'s `confirmatory_status: exploratory_only`, a
single, unreplicated 4-instance run set may never itself drive a
`reject_scoped`-strength verdict; any eventual reading calls for `weaken`
plus replication at most. This does not reopen, reweight, or extend
`H-ECDLP-09125b`'s own closed, pre-registered 24+4-instance statistic
(`EV-ECDLP-5b61eb`, `DEC-20260912-2a626b`), which remains untouched.

## Protocol deviations / notes for the record

1. **New top-level orchestration script, not a reuse of `orchestrate.py`
   verbatim.** `orchestrate.py` hardcodes `SEED=20260905` (the v1 seed) at
   module scope and loads the fixed six-curve list; it cannot be invoked
   for a seventh curve under a different seed without either editing it
   (prohibited — it is a frozen v1 artifact underlying the closed decision)
   or wrapping it. `orchestrate_new_curve_c6.py` is a new script that calls
   the identical underlying functions (`instance_runner.run_curve`,
   `harness.runner.run_wrapped`) the same way, parameterized for this one
   new curve/seed. This is the same relationship `positive_control.py` has
   to `curves.py`'s search functions, applied one level up (orchestration
   rather than curve-freezing).
2. **Avoid-set superset.** The handoff specifies an avoid-set of exactly the
   6 existing curves' keys; the search was actually run against those 6
   plus the `a26bde` anomalous-pair curve (7 keys), defensively. This is
   strictly more conservative than required and did not change the outcome
   (the candidate returned did not collide with any of the 7, so it would
   equally have been accepted against the required 6-key set alone).
3. **Extra bookkeeping file.** A non-required file,
   `experiments/EXP-ECDLP-e36df2/orchestrate_manifest_summary_new_curve_c6.json`,
   was written alongside the 4 required run directories, mirroring
   `orchestrate_manifest_summary.json`'s existing pattern for the v1 runs.
   It duplicates information already in the run manifests and is not one of
   the handoff's listed deliverables; it is additive documentation only and
   touches no existing file.
4. No curve-search or prime-search exhaustion occurred; no run hit
   infrastructure failure, timeout, or precision-margin exhaustion. There is
   nothing to report under the handoff's stopping-rule / infrastructure-
   defect clause.

## Files touched (all new; nothing existing modified)

- `experiments/EXP-ECDLP-e36df2/driver/new_curve_c6_selection.py` (new)
- `experiments/EXP-ECDLP-e36df2/driver/orchestrate_new_curve_c6.py` (new)
- `experiments/EXP-ECDLP-e36df2/driver/pooled_summary_new_curve_c6.py` (new)
- `experiments/EXP-ECDLP-e36df2/frozen_new_curve_c6_seed20260921.json` (new)
- `experiments/EXP-ECDLP-e36df2/runs/RUN-ECDLP-e36df2-029/` .. `-032/` (new)
- `experiments/EXP-ECDLP-e36df2/orchestrate_manifest_summary_new_curve_c6.json` (new, non-required bookkeeping)
- `experiments/EXP-ECDLP-e36df2/pooled-summary-new-curve-c6.json` (new)
- `experiments/EXP-ECDLP-e36df2/design_note_v2_addendum.md` (this file, new)

Not touched: `specification.yaml`, `design_note.md`, `pooled-summary.json`,
`stage0_regression_transcript.json`, `frozen_positive_control_curve.json`,
and `runs/RUN-ECDLP-e36df2-001` through `-028`.
