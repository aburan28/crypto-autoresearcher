# Design: two cheap, no-new-sampling reliability checks on the "double dilution" formula
# (PRE-REGISTERED before `reliability_checks.py` is run or any result is computed)

`TASK-20260806-66e3c3` (executor) / `BATCH-3bd1f4` / `GOAL-HQC-001` /
`EXP-HQC-982268`. Authorized by `DEC-20260806-d9d395`'s `next_actions` item 1,
itself resting on `EV-HQC-036d4b` and the Red Team's independent review
`TASK-20260806-2cec38` of `TASK-20260806-e120e8`.

**This document is written and frozen before any check code is run.** The
data sources, the exact quantities each check computes, the fail-closed
self-integrity gates, and — critically — what result would indicate high vs.
low confidence in the ~1.38e5 global-injection `T_req` projection are fixed
here in advance. `checks_results.json` and `checks_report.md` are produced
afterward and must not cause this file to be edited retroactively.

Claim tier: **toy, hard ceiling**, identical scope boundary to every task in
this read chain (PS-R3 only, `n_e=56, n=7187, N=7168, dup=1, m=17`). Nothing
here is a statement about HQC, A17, any decoding-failure rate, or any
standardized parameter set.

---

## 0. What this task does and does not do

- **NO NEW (T)-SAMPLING.** No cryptographic sampler, no `decode_blocks`
  call, no `stage_a.py` shard is touched or regenerated. Both checks work
  entirely from numbers already committed to the repository:
  - `coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measurement_results.json`
    (the PS-R3 T=1e7 real-sampler baseline measurement, `EV-HQC-b71230`'s
    source data — `T_arm_diagnostics.S_histogram`, `q_hat_measured`, and the
    17 reported `MEASUREMENT.cells`).
  - `coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/reanalysis_results.json`
    (the T=10,000 pooled matched-pair true-arm re-decode, `EV-HQC-036d4b`'s
    source data — `primary_matched_pair_analysis.combined_10000` and
    `required_T_derivation.per_k`, which already store `mubar_k_true`,
    `mubar_km1_true`, `se_paired_at_T_ref_10000` for `k=2..26`).
  - `coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py`
    (`comb_matrix`, `log2_A_from_hists`), imported **read-only**,
    sha256-pinned against the hash already declared in that task's own
    committed snapshot receipt
    (`coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/archives/TASK-20260806-40c805/snapshot-receipt.json`).
    This is the only code reuse; no estimator arithmetic is reimplemented
    from scratch for computing `mu_k` from a histogram.
- Does **not** touch `stage_a.py`, `pilot_injection.py`, `measure.py`, or
  `experiments/EXP-HQC-982268/specification.yaml`.
- Does **not** run or scope a global-injection pilot. Does **not** make the
  campaign-level call (proceed / do more validation first). Reports
  observations only, per `agents/executor.md`.
- Does **not** adjudicate whether the dilution formula's algebra is correct
  — that is settled and out of scope here (`EV-HQC-036d4b`: two independent
  first-principles re-derivations already confirm the algebra). This task
  only asks how much the formula's *approximation* (the i.i.d.-blocks
  substitution) departs from what the campaign's own already-collected data
  shows, across a range, not at one point.

---

## 1. Check 1: conditional-vs-unconditional `mubar_{k-1}` deviation across k

### 1.1 What is measured

The dilution formula's model step (`design.md` of `TASK-20260806-e120e8`,
Section 3.2) substitutes the unconditional, full-population `mubar_{k-1}`
for the conditional, other-blocks-only moment the exact decomposition
actually requires. Applied to the **undefected baseline itself** (every
block including the perturbed one shares the same marginal rate `q`), this
substitution forces the i.i.d.-blocks moment relation `mubar_k = q *
mubar_{k-1}` for every `k`, i.e.

```
ratio(k)          = mubar_{k-1} / mubar_k
iid_prediction     = 1 / q_hat
relative_deviation(k) = ratio(k) / iid_prediction − 1 = ratio(k) * q_hat − 1
```

The Red Team's finding (`red_team_report.md` Section 1.3) is exactly
`relative_deviation(17) = 13.4%` computed from ONE dataset
(`TASK-20260806-e120e8`'s pooled T=10,000 true-arm data). This check computes
`relative_deviation(k)` at **every reachable `k`**, on **two independent,
already-committed datasets**, and reports the full pattern:

- **Dataset A** (`measurement_results.json`, T=1e7, PS-R3 real-sampler
  baseline, `q_hat_measured=0.3198315732142857`): `mu_k` for every `k` is
  computed from the committed `S_histogram` via the sha256-pinned
  `log2_A_from_hists`/`comb_matrix` (back out `mu_k = 2^(log2_A_k +
  k*log2(q))` from the pinned function's own return value — no
  reimplementation of the moment arithmetic). Reported for every `k` where
  `mu_k` and `mu_{k-1}` are both finite and nonzero given the histogram's
  support (`max(s) with H_s>0` bounds the largest usable `k`); the number of
  trials effectively contributing to each `mu_k` (`sum_{s>=k} H_s`) is
  reported alongside every point as a reliability indicator, since deviation
  point estimates at large `k` rest on shrinking support.
- **Dataset B** (`reanalysis_results.json`, T=10,000, pooled true-arm,
  `q_hat=0.31940535714285717`): `mubar_k_true`/`mubar_km1_true` are read
  **directly** from the already-committed `required_T_derivation.per_k`
  table for `k=2..26` — no recomputation, this is the exact table the Red
  Team's own 13.4% number came from, extended here to its full stored range.

### 1.2 Fail-closed self-integrity gates (fixed in advance)

All of the following are checked **before** any deviation number is
reported. A failure of any of them is `SystemExit` (`FAIL-CLOSED`, no
`checks_results.json` written):

1. `measure.py`'s sha256 equals the hash already declared in
   `TASK-20260806-40c805/snapshot-receipt.json`
   (`a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`).
2. `measurement_results.json`'s sha256 equals the hash already declared in
   the same receipt
   (`6b2804e36f35a453f524843af6ef40da03e0295aece7fc574e01923f0d575801`).
3. `reanalysis_results.json`'s sha256 equals the hash already declared in
   `TASK-20260806-7bbbc8/snapshot-receipt.json`
   (`d67c80fedd7e29e8c5dc1838a2003bb235241214103bf6cfbb1d68cde7e5bd35`).
4. `sum(S_histogram) == T_arm.trials_achieved == 10_000_000` (no silent
   truncation in the reused histogram).
5. Recomputing `q_hat` directly from `S_histogram`
   (`sum(s*H_s)/(T*n_e)`) reproduces the committed `q_hat_measured` field to
   `rtol=1e-12`.
6. Recomputing `log2_A_17` from `S_histogram` via the pinned
   `log2_A_from_hists` reproduces the committed
   `MEASUREMENT.cells[k=17].log2_A_k` value to `atol=1e-9`.

Criteria 1-3 guard against reading a different byte sequence than the one
this design was written against. Criteria 4-6 guard against a silent
transcription or arithmetic error in this task's own reuse of the pinned
estimator before any new number is trusted.

### 1.3 What result means what, stated in advance

This check cannot, by itself, prove which direction the true global-injection
`T_req` should move (this task does not conclude that; the direction depends
on how the excess-correlation structure interacts with a *global*
perturbation, which involves all 56 blocks' bracket terms simultaneously, an
extrapolation this task does not attempt). What is pre-registered is the
**diagnostic reading of the pattern**:

- **Higher confidence in treating ~13.4% (and hence ~1.38e5) as roughly
  representative** would look like: `relative_deviation(k)` staying in a
  similar order of magnitude (say, within a factor of ~2) across the
  reported range, without blowing up, changing sign erratically, or growing
  sharply and monotonically as `k` increases past 17 — i.e., k=16/17 is not
  a special outlier in an otherwise small-deviation regime.
- **Lower confidence** would look like: `relative_deviation(k)` growing
  substantially in magnitude at `k` values near or beyond the load-bearing
  order 17 relative to smaller `k`, or reversing sign across the range
  (which would mean the approximation error is not a stable, one-directional
  structural property but a `k`-dependent effect whose size at the specific
  order 17 is not representative of "how wrong the i.i.d. approximation is"
  in general).
- The **sign** of `relative_deviation(k)` (whether `mubar_{k-1}/mubar_k`
  exceeds or falls short of `1/q_hat`) is reported as a fact at every `k`,
  with **no mechanistic interpretation attached** (this task does not decide
  whether that corresponds to "positive" or "negative" block-failure
  correlation in the sense `EV-HQC-b71230`'s own headline anti-correlation
  finding discusses — that reconciliation, if needed, is for the Coordinator
  and reviewers).
- Agreement or disagreement **between Dataset A (T=1e7) and Dataset B
  (T=10,000)** at the `k` values they both cover is reported as a fact: close
  agreement would indicate the deviation is a stable population property, not
  a T=10,000 sampling artifact; disagreement would indicate the 13.4% number
  itself carries more sampling noise than its single-point presentation
  suggested.

---

## 2. Check 2: SE-scaling / required-T formula in-range check

### 2.1 What is measured

The Validator (`TASK-20260806-f743ae`) verified the reported `T_req ∝
1/Δp²` scaling to 9 significant figures **at one point**
(`Δp=0.0082`, `k=17`). This check independently reimplements the same
closed-form required-T formula from committed constants only —

```
Delta_log2_A(k, Δp) = (k/n_e) * (Δp/ln2) * [ mubar_{k-1,true}(k) / mubar_{k,true}(k) − 1/q_hat ]
T_req(k, Δp)         = T_ref * ( z_sum * SE_ref(k) / |Delta_log2_A(k, Δp)| )^2
```

using `n_e=56`, `q_hat=0.31940535714285717`, `T_ref=10000`,
`z_sum=3.241515551`, and the per-`k` `mubar_k_true`, `mubar_km1_true`,
`se_paired_at_T_ref_10000` already committed in
`reanalysis_results.json.required_T_derivation.per_k` — and sweeps `Δp`
across a **wide range**, not the single committed point estimate:

- The 8 already-committed sensitivity points (`Δp ∈
  {0.0002,0.0022,0.0026,0.005,0.0082,0.01,0.02,0.05}`, `k=17` only) are
  recomputed and checked against the committed `required_T` values
  (fail-closed cross-check, Section 2.2 item 4 below).
- A wider, log-spaced sweep, `Δp ∈ [1e-6, 1.0]` (both signs), at `k=17`, well
  beyond the committed table's `[0.0002, 0.05]` range, explicitly to stress
  the formula's behavior far outside the one validated point and the
  committed table — including deliberately non-physical magnitudes (`Δp`
  near 1 is not a plausible net marginal shift for this system; it is
  included only to check the formula/implementation, not to suggest it is a
  plausible input).
- The same sweep repeated at every `k=2..26` (the full range `per_k`
  covers), to check whether the bracket term's **sign** is stable across
  `k` (this reuses exactly the same quantity Check 1 measures, so the two
  checks are cross-referenced in the report, not treated as unrelated).

### 2.2 Fail-closed self-integrity gates (fixed in advance)

1. `reanalysis_results.json`'s sha256 matches the pinned hash (same gate as
   Check 1 item 3 — checked once, shared).
2. `z_sum` recomputed from `alpha=0.05`, `power=0.90` via the normal
   quantile identity `z_{1-alpha/2} + z_{1-beta}` matches the committed
   `power_target.z_sum` to `atol=1e-6`.
3. At `k=17`, `Δp=0.0082`: the recomputed `leading_term`, `q_shift_term`,
   and `total` match `required_T_derivation.load_bearing_k17.
   modeled_delta_log2_A_red_team_input` to `rtol=1e-9`.
4. All 8 committed `(Δp, required_T)` sensitivity pairs at `k=17`
   (`delta_p_sensitivity_k17`) are reproduced by this task's independent
   reimplementation to `rtol=1e-6`.

A failure of any of these is `SystemExit` (`FAIL-CLOSED`, no
`checks_results.json` written) — it would mean this task's reimplementation
of the formula is not, in fact, the same formula as the one already
reviewed, and no swept-range result computed from a mistranscribed formula
should be reported as informative.

### 2.3 What "behaves sensibly" means, fixed in advance

Over the full swept range (`Δp ∈ [1e-6, 1.0]`, both signs, `k=17`, and
`k=2..26` at fixed `|Δp|=0.0082`):

- `T_req(k, Δp) * Δp²` is checked for constancy (coefficient of variation
  across the sweep) — algebraically this product should be independent of
  `Δp` (holding `k` fixed) by construction of the formula, so this is a
  check on the **arithmetic/implementation**, not a claim that the physical
  model is more trustworthy at extreme `Δp`.
- `T_req` is checked to be strictly decreasing in `|Δp|` (no local
  non-monotonic humps or discontinuities) across the sweep.
- `T_req(k, +Δp) == T_req(k, −Δp)` (sign symmetry) is checked to floating
  precision.
- `T_req` is checked finite and positive at every swept point except in the
  immediate neighborhood of `Δp=0`, where it is expected to diverge
  smoothly (not `NaN`, not a discontinuous jump) — the check confirms the
  divergence is smooth (monotonic approach) rather than reporting infinity
  as a "failure."
- The bracket term's **sign** across `k=2..26` is reported: if it flips sign
  anywhere in this range, that is reported as a fact bearing on whether "the
  correction always points the same direction" is a safe assumption when
  reasoning about a global (all-`k`-order-relevant) injection.

**What this check does and does not indicate:** because `T_req ∝ 1/Δp²` is
an algebraic identity of the *stated* formula, a clean pass here confirms the
required-T *arithmetic/code path* is correct across a wide operating range
(not only the Validator's single audited point) — it does **not** by itself
say anything new about whether the formula's own i.i.d.-blocks approximation
is a good model of the real system (that is Check 1's question). A failure
here (discontinuity, sign error, non-monotonicity) would be a genuine
implementation-correctness finding independent of the modeling question.

---

## 3. Mechanically-sound criteria for this task (fixed in advance)

**Sound / results reportable** requires ALL of:

1. All fail-closed self-integrity gates (Sections 1.2 and 2.2) demonstrably
   pass (or, if run in a mode that deliberately corrupts an input to test the
   gate, that the gate demonstrably aborts — see `reliability_checks.py`'s
   `--selftest-fail-closed` mode, run separately from the authorized
   real-data run and reported in `run_manifest.yaml`, not counted against
   the one authorized run).
2. No uncaught exception on the authorized run.
3. Both datasets yield at least 10 usable `k` values each with finite,
   nonzero `mubar_{k-1}` and `mubar_k`.

A failure of 2-3 is reported as `invalid_measurement`, not silently retried.

---

## 4. What this task does not conclude

Per `agents/executor.md`: this task reports the per-`k` deviation pattern and
the swept required-T behavior as facts. Whether the campaign should now
proceed to scope the global-injection pilot at (or near) ~1.38e5, do further
validation first, or something else, is the Coordinator's and the two
independent reviewers' call on this batch's evidence, not this document's or
`checks_report.md`'s. This task does not resolve whether the approximation
error identified by the Red Team makes the ~1.38e5 projection optimistic or
pessimistic — it reports the k-dependence pattern that bears on that
question. Claim tier stays toy throughout.
