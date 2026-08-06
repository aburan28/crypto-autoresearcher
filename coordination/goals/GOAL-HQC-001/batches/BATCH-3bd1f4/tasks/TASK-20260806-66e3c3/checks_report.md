# Reliability checks report: conditional-vs-unconditional `mubar_{k-1}` and SE-scaling in-range

`TASK-20260806-66e3c3` (executor) · `BATCH-3bd1f4` · `GOAL-HQC-001` ·
`EXP-HQC-982268`. Authorized by `DEC-20260806-d9d395` `next_actions` item 1.
Pre-registration: `design.md` (written and frozen before `reliability_checks.py`
was run on any data). Raw output: `checks_results.json`. Full
command/provenance: `run_manifest.yaml`.

**Claim tier: TOY, hard ceiling.** PS-R3 only (`n_e=56, n=7187, N=7168,
dup=1, m=17`). **No new (T)-sampling was performed** — both checks compute
entirely from two already-committed JSON artifacts plus a sha256-pinned,
read-only import of `measure.py`'s `comb_matrix`/`log2_A_from_hists`. This
report separates observations from interpretation and makes **no
campaign-level recommendation** (proceed to a global-injection pilot, do
more validation first, or otherwise) — that call belongs to the Coordinator
and the two independent reviews of this batch.

---

## 0. What was done, in one paragraph

Two pre-registered checks were run, both against already-collected PS-R3
data. Check 1 measured the deviation between the real, measured
`mubar_{k-1}/mubar_k` ratio and the i.i.d.-blocks prediction `1/q_hat`
across a full range of `k` (not just the Red Team's single `k=17` number),
on **two independent datasets**: the T=1e7 real-sampler baseline
(`TASK-20260806-cde749`) and the T=10,000 pooled matched-pair true-arm
(`TASK-20260806-e120e8`, the same dataset the Red Team's 13.4% figure came
from). Check 2 independently reimplemented the required-T formula from
committed constants and swept `Delta_p` across six orders of magnitude
(`1e-6` to `1.0`, both signs), at `k=17` and across the full reported
`k=2..26` range, checking for the algebraic `1/Delta_p^2` scaling,
monotonicity, sign symmetry, and absence of blow-ups/discontinuities/sign
errors. All fail-closed self-integrity gates passed (Section 1 below); no
gate needed to abort on the authorized run (a deliberately-corrupted pin was
separately exercised in `--selftest-fail-closed` mode and correctly aborted
— see `run_manifest.yaml`).

---

## 1. Fail-closed self-integrity gates: all PASS

| gate | result |
|---|---|
| `measure.py` sha256 == pinned (`a4fd1ecb...5dc8`) | **PASS** |
| `measurement_results.json` sha256 == pinned (`6b2804e3...5801`) | **PASS** |
| `reanalysis_results.json` sha256 == pinned (`d67c80fe...5bd35`) | **PASS** |
| Dataset A `S_histogram` sum == `T_arm.trials_achieved` (1e7) | **PASS** |
| Dataset A `q_hat` recomputed from histogram == committed `q_hat_measured` (rtol 1e-12) | **PASS** |
| Dataset A pinned `log2_A_from_hists`' internal `q` == independently recomputed `q` | **PASS** |
| Dataset A recomputed `log2_A_17` == committed `MEASUREMENT.cells[k=17]` (atol 1e-9) | **PASS** |
| Dataset B `q_hat` from `mubar_1` (k=2 row) == `q_hat` parsed from provenance string (rtol 1e-9) | **PASS** |
| `z_sum` recomputed from `alpha=0.05, power=0.90` == committed `power_target.z_sum` (atol 1e-6) | **PASS** |
| Recomputed `k=17, Delta_p=0.0082` `total`/`required_T` == committed `load_bearing_k17` values (rtol 1e-9 / 1e-6) | **PASS** |
| All 8 committed `delta_p_sensitivity_k17` points reproduced (rtol 1e-6) | **PASS** |

Separately, `--selftest-fail-closed` mode deliberately corrupted the
`measure.py` sha256 pin and confirmed the gate aborts with `SystemExit`
before computing anything (`run_manifest.yaml` records this as a distinct
invocation, not counted against the one authorized run).

---

## 2. Check 1: conditional-vs-unconditional `mubar_{k-1}` deviation across k

### 2.1 Dataset A (T=1e7 real-sampler baseline, `q_hat=0.3198315732142857`)

`mu_k` computed for `k=1..35` (35 = the largest `k` for which the committed
`S_histogram` has nonzero support at `s=35`; no trial in the 1e7-trial
sample had all 36+ blocks fail simultaneously). `relative_deviation(k) =
(mubar_{k-1}/mubar_k) * q_hat - 1`:

| k | rel. deviation | eff. trials contributing to `mu_k` |
|---:|---:|---:|
| 2 | +0.42% | 10,000,000 |
| 5 | +1.71% | 9,999,974 |
| 10 | +4.00% | 9,961,702 |
| **17** | **+7.63%** | 6,614,923 |
| 20 | +10.28% | 3,109,645 |
| 26 | +27.81% | 119,319 |
| 30 | +70.36% | 3,207 |
| 35 | +659.92% | 5 |

Full table (all `k=2..35`) in `checks_results.json.check1_dataset_A.per_k`.

**The deviation is positive at every single `k` tested (2 through 35, no
exceptions), and increases monotonically with `k` throughout the entire
range** — smoothly through `k~2..20`, then increasingly steeply as the
histogram's support thins out (`k>=26`, where fewer than 120,000 of the 1e7
trials have `S>=k`, and by `k=35` only 5 trials do). The rapid blow-up at
`k>=30` coincides with `effective_trials_k` collapsing into the low
thousands-to-single-digits, i.e. that portion of the table is reported
faithfully but should be read as increasingly noise-dominated, not as
evidence the deviation is "truly" hundreds of percent at those orders.

### 2.2 Dataset B (T=10,000 pooled matched-pair true arm, `q_hat=0.3194053571428572`)

Same computation, `mubar_k_true`/`mubar_km1_true` read directly (no
recomputation) from `reanalysis_results.json`'s already-committed
`required_T_derivation.per_k` table, `k=2..26`:

| k | rel. deviation |
|---:|---:|
| 2 | +0.36% |
| 5 | +1.52% |
| 10 | +3.78% |
| **17** | **+13.39%** |
| 20 | +26.40% |
| 26 | +118.50% |

Full table in `checks_results.json.check1_dataset_B.per_k`. `k17_dataset_B
= 0.13388396046433848` reproduces the Red Team's reported 13.4% figure
exactly (same underlying committed table).

**Same qualitative pattern as Dataset A: positive at every `k=2..26`,
monotonically increasing throughout, with the steepest growth at the high-k
end of the range.**

### 2.3 Cross-dataset comparison, and the disagreement this reveals

At small `k` (2-10), the two independent datasets agree closely (e.g.
`k=2`: 0.42% vs. 0.36%; `k=10`: 4.00% vs. 3.78%). **At `k=17` — the
pre-specified, load-bearing order the 4.33e8/1.38e5 figures are built on —
the two datasets disagree by nearly a factor of 1.75: Dataset A (T=1e7)
gives +7.63%, Dataset B (T=10,000) gives +13.39%.** The gap widens further
at higher `k` (`k=20`: 10.28% vs. 26.40%; `k=26`: 27.81% vs. 118.50%).

`effective_trials_k` at `k=17` in Dataset A is 6,614,923; the analogous
count in Dataset B is bounded by its total sample size of 10,000 trials and
is necessarily far smaller (Dataset B does not retain this count, but its
total trial budget is ~660x smaller than Dataset A's `k=17` effective
count). The pattern — close agreement where both datasets have ample
effective sample size, growing disagreement as effective sample size
shrinks, and by far the largest disagreement occurring in the region where
Dataset B's much smaller total trial count leaves the fewest trials
contributing to the estimate — is consistent with (but this task does not
prove) Dataset B's 13.39% figure at `k=17` carrying a non-trivial sampling-noise
component on top of a real underlying deviation that Dataset A's ~660x
larger effective sample estimates at 7.63%. This task does **not** determine
which point estimate is closer to a hypothetical true population value,
does not compute formal confidence intervals on either deviation series (not
pre-registered), and reports both numbers as facts, not as a resolved
correction.

### 2.4 Reading against the pre-registered criteria (design.md Section 1.3)

Both criteria named in advance are met **simultaneously, in different
respects**, which is reported as a mixed result rather than rounded to one
conclusion:

- **Toward lower confidence:** the deviation does **not** stay bounded near
  its `k=17` value as `k` moves away from 17 — it grows sharply and
  monotonically for `k>17` in both datasets (in Dataset B, from 13.4% at
  `k=17` to 118.5% at `k=26`; in Dataset A, from 7.6% at `k=17` to 27.8% at
  `k=26`). Per the pre-registered reading, this is the signature that would
  argue for lower confidence in treating the `k=17` figure as a bounded,
  order-of-magnitude-stable correction — the approximation gets
  systematically worse, not better, moving to higher joint-failure orders.
- **Toward higher confidence in the deviation being a real, structural
  (not erratic/noise-driven) effect:** the deviation's **sign never flips**
  anywhere in either dataset (2 through 35 in Dataset A, 2 through 26 in
  Dataset B) and its growth with `k` is smooth and monotonic in both
  datasets independently, not jagged or sign-alternating. This is the
  opposite of what a purely noise-driven, erratic pattern would look like.
- **A new, disclosed fact not anticipated in the pre-registration's binary
  framing:** the two independent datasets' point estimates at the
  load-bearing order `k=17` itself disagree by a factor of ~1.75 (7.6% vs.
  13.4%), correlated with their very different effective sample sizes at
  that order. This bears directly on how much weight the specific "13.4%"
  number (as opposed to the qualitative existence and sign of the
  deviation) should carry in any downstream arithmetic.

No mechanistic interpretation of the deviation's sign (e.g., relative to
`EV-HQC-b71230`'s own headline anti-correlation finding) is offered here;
that reconciliation is left to the Coordinator and reviewers.

---

## 3. Check 2: SE-scaling / required-T formula in-range check

### 3.1 Reproduction of the already-audited point and table (fail-closed gates)

The independent reimplementation reproduces the committed `k=17,
Delta_p=0.0082` figures (`total=0.0015053436004862052`,
`required_T=432907900.434108`) to relative differences of `4.3e-16` and
`8.3e-16` respectively, and reproduces all 8 points of the committed
`delta_p_sensitivity_k17` table to `rtol<1e-6`. This confirms the
reimplementation used for the sweep below is the same formula already
reviewed, not a divergent one.

### 3.2 Wide sweep at k=17: `Delta_p in [1e-6, 1.0]`, both signs, 61 points

- **`T_req(k=17, Delta_p) * Delta_p^2` is constant across the entire six-order-of-magnitude
  sweep to a coefficient of variation of `2.47e-16`** — i.e. machine
  precision. The `1/Delta_p^2` scaling the Validator checked at one point
  (`Delta_p=0.0082`, 9 significant figures) holds, to the same precision,
  everywhere in this much wider swept range, not only at that one point.
- **Strictly monotonically decreasing** in `|Delta_p|` across all 61 points
  — no discontinuities, no local humps.
- **Sign-symmetric**: `T_req(+Delta_p) == T_req(-Delta_p)` to relative
  difference `<1e-9` at every swept point.
- **Finite and positive at every one of the 61 points**, including the
  extreme ends of the range (`Delta_p=1e-6`: `T_req` very large but finite
  and well-behaved; `Delta_p=1.0`, a deliberately non-physical magnitude
  included only to stress the arithmetic, not as a plausible input:
  `T_req` small, finite, positive, no overflow/underflow artifact).
- **No sign error**: the bracket term `mubar_16/mubar_17 - 1/q_hat` at
  `k=17` is `+0.4192` (positive), consistently reproducing the same sign as
  the algebraically-identical quantity Check 1 measures at `k=17` (Dataset
  B: `relative_deviation(17)=+0.1339`, and `bracket = relative_deviation /
  q_hat = 0.1339 / 0.3194 = 0.4192` — the two checks' numbers are
  cross-consistent by construction, as expected since they compute the same
  underlying ratio two different ways).

### 3.3 Bracket-term sign stability across the full k=2..26 range

The bracket term `mubar_{k-1}/mubar_k - 1/q_hat` (the same quantity Check 1
reports as `relative_deviation(k)/q_hat`) is **positive at every one of the
25 reported k values (`k=2..26`), with no sign change anywhere in the
range** (`distinct_signs_observed: ["positive"]`). At each of these 25 `k`
values, an independent wide `Delta_p` sweep (`1e-6` to `~0.32`, 21 points
each) reproduces the same monotonic, finite-and-positive,
`1/Delta_p^2`-scaling behavior found at `k=17`
(`all_k_monotonic=true`, `all_k_finite_positive=true`,
`max_cv_across_k=3.53e-16`).

### 3.4 What this does and does not establish

Per the pre-registered scope (design.md Section 2.3): this check confirms
the required-T **arithmetic/implementation** is well-behaved (no
discontinuity, sign error, or blow-up bug) across a `Delta_p` range roughly
120x wider on the low end and 20x wider on the high end than the previously
audited single point, and across the full `k=2..26` range rather than only
`k=17`. It does **not** by itself say anything new about whether the
formula's own i.i.d.-blocks *modeling* approximation is accurate — that is
what Check 1 (Section 2 above) addresses, and Check 1's finding is that the
approximation error is real, always the same sign, and grows (not shrinks)
moving away from `k=17` toward higher joint-failure orders.

---

## 4. Summary table (facts only, no rounding to a single verdict)

| quantity | value | source |
|---|---|---|
| Red Team's original single-number deviation at k=17 | 13.4% | `red_team_report.md`, Dataset B |
| This check's Dataset B (T=10,000) deviation at k=17, reproduced | 13.39% | matches, same table |
| This check's Dataset A (T=1e7, ~660x more effective trials at k=17) deviation at k=17 | 7.63% | independent, larger dataset |
| Deviation sign across k=2..35 (A) / k=2..26 (B) | always positive, 0 sign flips | both datasets |
| Deviation trend with k | monotonically increasing in both datasets, steepening past k~20 | both datasets |
| `T_req * Delta_p^2` coefficient of variation over `Delta_p in [1e-6,1]` at k=17 | 2.47e-16 (machine precision) | independent reimplementation |
| Bracket-term sign stability across k=2..26 | stable, always positive | independent reimplementation |
| Any discontinuity / sign error / blow-up found in the required-T formula over the swept range | none found | Check 2 |

---

## 5. What this task does not conclude

Per `agents/executor.md`: this is a report of two pre-registered reliability
checks' measured results, offered as facts. This task does **not** decide
whether the ~1.38e5 global-injection projection (or the 4.33e8 single-block
figure) is now more or less trustworthy overall, does **not** decide whether
the k-dependence pattern in Section 2 makes the global-injection projection
optimistic or pessimistic, and does **not** recommend proceeding to scope a
global-injection pilot, running further validation, or any other
campaign-level action. Those calls belong to the Coordinator and the two
independent reviewers dispatched against this task's artifacts. Claim tier
stays toy throughout; nothing here is a statement about HQC, assumption A17,
HQC's decoding-failure rate, or any standardized parameter set. This task
tested exactly one parameter set (PS-R3) and reused exactly two
already-committed datasets and one already-committed formula — nothing here
generalizes beyond that.

---

## 6. Budget and validity

- Core-seconds / wall-seconds: authorized run completed in **9.65 wall
  seconds** (well inside the 1,800-second budget; core-second usage is
  negligible pure-Python/NumPy arithmetic on already-loaded JSON, no
  cryptographic sampler invoked). Full accounting in `run_manifest.yaml`.
- Runs: **1 of 1 authorized** used for the reported results
  (`checks_results.json`); a separate `--selftest-fail-closed` invocation
  (which writes no results file and produces no reportable measurement) was
  also run, to demonstrate the fail-closed gate construction, and is
  recorded in `run_manifest.yaml` as a distinct, non-counted invocation.
- No randomness of any kind is used anywhere in `reliability_checks.py` —
  every number is either read directly from an already-committed JSON file
  or derived from one via deterministic arithmetic (including the
  sha256-pinned reuse of `measure.py`'s own estimator functions). There is
  no seed to record because there is no draw.
- `checks_results.json.validity.status = "valid_measurement"`: all
  pre-registered mechanically-sound criteria (design.md Section 3) were
  met — every fail-closed gate passed, no uncaught exception, both datasets
  yielded well over 10 usable `k` values with finite nonzero moments.
- `certificate.kind: none` — this is a pure measurement/reanalysis run; no
  discrete-log solve or factor-base relation is claimed.

---

## 7. Artifacts

- `design.md` — pre-registered, written before this run.
- `reliability_checks.py` — the checks script (sha256-pinned reuse of
  `measure.py`'s `comb_matrix`/`log2_A_from_hists`; fail-closed integrity
  gates; both checks; `--selftest-fail-closed` mode).
- `checks_results.json` — full raw output of the one authorized run.
- `run_manifest.yaml` — command, git commit/dirty-state, environment,
  timings, validity status, explicit no-new-sampling statement.
- `stdout.log` / `stderr.log` — captured output of the authorized run.
- This file.
