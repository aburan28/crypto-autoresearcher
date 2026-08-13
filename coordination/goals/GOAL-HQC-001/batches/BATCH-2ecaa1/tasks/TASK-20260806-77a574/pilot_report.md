# Pilot report: real-sampler defect injection (V3 class, decode_blocks injection point)

`TASK-20260806-77a574` (executor) · `BATCH-2ecaa1` · `GOAL-HQC-001` ·
`EXP-HQC-982268`. Authorized by `DEC-20260806-1ac8fa`. Pre-registration:
`design.md` (written and frozen before `pilot_injection.py` was run on any
real data). Raw output: `pilot_results.json`. Full command/provenance:
`run_manifest.yaml`.

**Claim tier: TOY, hard ceiling.** This is a PILOT at PS-R3
(`n_e=56, n=7187, omega=45, omega_r=omega_e=51, N=7168, dup=1, m=17`),
ONE defect class (V3: last-block-window-read-early), ONE injection point
(`decode_blocks`'s block window, last block only), 5,000 defect-injected
trials paired with 5,000 undefected control trials. This is **not** the full
`T_req = 3.09e5` run and states nothing about HQC, assumption A17, HQC's
decoding-failure rate, or any standardized parameter set. Per
`agents/executor.md`, this report separates observations from
interpretation and offers no conclusion about A17 or OPEN-6 — the campaign's
next go/no-go call belongs to the Coordinator and the two independent
reviews of this batch.

---

## 1. What was tested, precisely

- Parameter set: **PS-R3 only** (order-matched to HQC-3's shape, `dup=1`,
  not HQC-3's true deployed duplication multiplicity).
- Defect class: **V3 (last-block-window-read-early)**, chosen and justified
  in `design.md` §2 (the Red Team's own explicit recommendation, and the
  only defect/injection-point pairing that is a direct translation of a
  prior control arm's defect name onto the real sampler's code). V1 was
  **not** tested in this pilot.
- Injection point: **`decode_blocks`'s block window, last block only**
  (index `n_e - 1`), shifted left by exactly one bit position. `decode_blocks`
  itself — fold, size-128 WHT, argmax, tie rule — was called **unmodified**
  on the perturbed bit array; the only new code is the bit-array
  preprocessing wrapper (`pilot_injection.py`'s `make_defected_decode_blocks`)
  and this pilot's own driver/reporting logic (`design.md` §3,
  `pilot_results.json.injection`).
- Trial counts: **5,000 defect-injected trials** (within the pre-registered
  2,000-10,000 range) **paired with 5,000 undefected control trials** at
  the same T, same parameter set, disjoint PRNG shards (`5000`/`6000`,
  confirmed disjoint from every prior committed `T`-arm shard usage at PS-R3
  found in this task's read scope: Stage-A's `0-3`/`900`, the cost-model
  benchmark's `999`, `measure.py`'s `1000-1007`).
- Estimator: `log2_Ahat_k` for `k = 2..26` (the intersection of both arms'
  independently-computed reachable range, via `stage_a.py`'s own
  `evaluable_k`, `T_STAB_THRESHOLD=30`, reused unmodified), including the
  load-bearing order `k = m = 17`, with leave-one-batch-out jackknife SE
  computed via `measure.py`'s own `comb_matrix`/`log2_A_from_hists`, reused
  by direct call, sha256-pinned.
- One authorized run (`runs_used: 1` of `1` authorized). A prior, uncharged
  shakedown of the identical script and identical PRNG shards was run in
  session scratch space first (not committed, not part of this deliverable
  set) to catch implementation bugs before the authorized run; its output
  is bit-identical to the authorized run's `log2_Ahat_k` values (confirmed
  directly), which is itself expected given identical shard/seed derivation
  and is recorded as a determinism check, not a second measurement.

---

## 2. Mechanical soundness: **SOUND**, against every pre-registered criterion in design.md §5

| pre-registered criterion (design.md §5) | outcome |
|---|---|
| No uncaught exception/crash | PASS — clean exit 0, `stderr.log` empty |
| Injection invariant holds on every defected trial | PASS — never violated during the authorized run (the invariant is checked on every internal batch call and would raise `SystemExit` immediately on any violation; none occurred) |
| D2 (exact generation weight) clean on both arms | PASS — 0 violations, defected and undefected |
| D3 (support cap) clean on both arms | PASS — 0 violations; `w(etilde)` max observed 2,740 (defected) / 2,732 (undefected), both under the cap of 4,641 |
| `decode_blocks` called unmodified (identity-checked) | PASS — `pilot_results.json.injection.wrapper_calls_unmodified_function = true`, confirmed by `id()` equality between the wrapper's inner call target and the sha256-pinned `stage_a.decode_blocks` |
| Estimator returns finite values at `k = m = 17` on both arms | PASS — `-1.086` (defected), `-0.879` (undefected), neither NaN |
| Both deliberate-mismatch dry runs abort and neither writes output | PASS — see §3 |
| Throughput is a real, reportable number | PASS — see §4 |

`pilot_results.json.validity.status = "valid_measurement"`. No criterion in
design.md §5's "needs structural redesign" list fired.

---

## 3. Fail-closed demonstration (both required checks)

Two independent fail-closed checks were exercised as deliberate-mismatch
dry runs, both executed automatically inside the authorized run itself
(before any real trial data was generated), and both aborted correctly:

1. **sha256 pin mismatch** (`load_module()`, same function used for the
   real, successful load of `stage_a.py`): called with a deliberately wrong
   expected hash (`0`×64). Result: `SystemExit`, message names both the
   wrong expected hash and the correct actual hash
   (`06a0a618...717681405`), **no file was written**. This differs from the
   V1-V3 convention of editing-then-reverting the pinned constant in the
   committed script — it calls the identical `load_module()` function with a
   wrong argument instead, so the committed pinned constants are never
   touched, not even transiently. Documented as a protocol note, not a
   deviation, in `run_manifest.yaml`.
2. **Injection invariant mismatch**: a wrapper was deliberately constructed
   to APPLY a 2-bit-position shift while its invariant check still asserts
   the pre-registered 1-bit-position semantics — i.e. a genuine mismatch
   between what was built and what was checked, run on a small synthetic
   array (no real pipeline draws consumed). Result: `SystemExit`, message
   names "injection invariant violated." Both dry runs are visible in
   `pilot_results.json.fail_closed_selftests` with `verdict: PASS`.

The run's own `main()` refuses to proceed (`FAILED_IMPLEMENTATION`,
`SystemExit`) if either selftest does not pass — this was exercised live,
not merely asserted after the fact.

---

## 4. Measured signal or clean null: report, not interpretation

**The properly isolating comparison is the DIFFERENCE between the paired
arms, not either arm's deviation from the theoretical A17-implied `log2 A_k
= 0` in isolation** — and both are reported below because the isolated
per-arm numbers, read alone, would be misleading.

**Individually, both arms deviate from 0 at k = m = 17:**

| arm | `log2_Ahat_17` | jackknife SE | `z` vs. 0 |
|---|---:|---:|---:|
| defected | -1.0857 | 0.2825 | -3.843 |
| undefected control | -0.8788 | 0.3421 | -2.569 |

Read in isolation, the defected arm's `z = -3.84` at `k=17` could look like
"a signal." **It is not attributable to the injection by itself**: the
UNDEFECTED control arm, run at the same T with the same parameter set and
the real, unmodified `decode_blocks`, ALSO deviates from 0 with `z = -2.57`
— consistent with what prior PS-R3 measurements in this campaign already
found (e.g. the -244.1-to-32.4-SD range cited in `EV-HQC-bfb257`'s
provenance chain): the undefected estimator itself is not 0 at finite T on
this parameter set, for reasons this pilot does not investigate and does
not need to, precisely because the design (design.md §1, §6) built a paired
undefected control for exactly this reason.

**The isolating comparison — defected minus undefected, at the
pre-registered load-bearing order:**

`log2_Ahat_17(defected) − log2_Ahat_17(undefected) = −0.2069`,
combined jackknife SE = `0.4437`, **z = −0.466**.

This is a **clean null** at `k = m = 17`, exactly the primary outcome
`design.md` §4 pre-registered as most likely given the injection's
narrowness (one block out of 56) and the resulting `k/n_e` dilution in the
joint moment.

**Across the full reported range (`k = 2..26`):** the difference's `|z|`
never exceeds `0.700` at any reported `k` (maximum at `k = 24`,
`z = −0.700`; monotonically small at low `k`, e.g. `z = −0.186` at `k=2`).
No `k` in the reported range shows a difference distinguishable from noise
at this trial count. This is a **clean null across every reported cell**,
not merely at the pre-specified order — reported as such, magnitude and
direction included (every difference in the table is negative in sign,
i.e. the defected arm's point estimate is consistently slightly lower than
the undefected arm's at every `k`, though never outside ~0.7 combined SE),
without concluding what this pattern means at this scale or whether it
would persist, grow, or vanish at a larger T. Full per-`k` table:
`pilot_results.json.MEASUREMENT.defected_minus_undefected`.

---

## 5. Throughput: measured, defect-injected, compared to both cost-model figures

| quantity | value |
|---|---:|
| Defected arm, measured | **2,097.6 trials/core-second** (5,000 trials / 2.3837 core-s) |
| Undefected control arm, measured | **2,105.6 trials/core-second** (5,000 trials / 2.3747 core-s) |
| Cost model optimistic band (`EV-HQC-bfb257`) | 2,168-2,227 t/cs |
| Cost model pessimistic figure (`EV-HQC-bfb257`) | 788 t/cs |
| Defected ÷ optimistic-band-low (2,168) | 0.968 |
| Defected ÷ pessimistic (788) | 2.662 |
| Undefected (this pilot) ÷ optimistic-band-low | 0.971 |
| Undefected (this pilot) ÷ pessimistic | 2.672 |

**Both measured figures sit close to, and just below, the optimistic band's
low end (2,168 t/cs)** — about 3.2% below it — and are roughly **2.66-2.67x
the pessimistic figure**, closer to the optimistic band by a wide margin.
This is the first measurement in this campaign of the defect-injected
pipeline's throughput; it directly corroborates the optimistic band as the
more accurate planning figure for a defect-injected run specifically
(`EV-HQC-bfb257`'s `unresolved_confounds` item: "whether injecting the
defect changes the per-instance cost... is unmeasured" — this pilot
supplies that missing corroboration).

**The defect itself changed measured throughput negligibly**: defected
(2,097.6 t/cs) vs. undefected (2,105.6 t/cs) differ by about 0.4%, run in
the same process with the same warm-up discipline (both code paths were
warmed with a throwaway 300-trial call before either timed measurement,
per the order-reversal/warm-up discipline the Validator established in
`TASK-20260806-069687` for exactly this kind of comparison). This magnitude
of difference is well within ordinary run-to-run timing noise at this scale
and is not read as evidence the injected conditional branch has any
measurable cost — only that a one-line-scale conditional added to a
per-batch decode call did not visibly move throughput at this trial count.

Both figures are **measured** (this task's own `_t_shard`-based benchmark,
`pilot_results.json.throughput`), not modeled; the cost-model figures they
are compared against are cited, not re-derived, from `EV-HQC-bfb257`.

---

## 6. Budget

- Core-seconds: **5.339 of 400 authorized** (1.3%).
- Wall-seconds: **5.232 of 2,700 authorized** (0.2%).
- Runs: **1 of 1 authorized**, used.
- No overrun of any kind on any budget dimension.

---

## 7. What this pilot does not say

Per `agents/executor.md` and this task's own constraints: no conclusion is
drawn about A17, HQC's decoding-failure rate, or any standardized parameter
set. The classification "mechanically sound" above is this executor's own
factual assessment against the criteria pre-registered in `design.md` §5,
offered as a factual input; whether the campaign proceeds to the full
`T_req = 3.09e5` run or something else is the Coordinator's and the two
independent reviewers' call, per `DEC-20260806-1ac8fa`'s stopping rule. This
pilot tested exactly one defect class, one injection point, one parameter
set, and one small trial count; nothing here generalizes to V1's global
shift, to the other three injection points, to PS-A/PS-R1/PS-R5, or to any
standardized HQC parameter set.

---

## 8. Artifacts

- `design.md` — pre-registered, written before this run.
- `pilot_injection.py` — the pilot script (thin injection wrapper + driver;
  reuses `stage_a.py`/`measure.py` sha256-pinned, read-only).
- `pilot_results.json` — full raw output of the one authorized run.
- `run_manifest.yaml` — command, git commit/dirty-state, environment, seeds,
  timings, validity status, fail-closed check verification detail.
- `stdout.log` / `stderr.log` — captured output of the authorized run.
- This file.
