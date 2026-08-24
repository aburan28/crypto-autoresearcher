# EXP-INSTR-36c8cf — execution report, PHASE A under contract version 2

**Task** TASK-20260810-c98659 (re-execution of Phase A) · **Goal** GOAL-ENDO-001
· **Batch** BATCH-d7e255 · **claim_tier** toy
**Contract** `experiments/EXP-INSTR-36c8cf/specification.yaml` version 1, as
amended to **version 2** by `experiments/EXP-INSTR-36c8cf/amendments/v1.yaml`
(amendment ordinal 1, `approved_by: coordinator`, recorded by
DEC-20260810-56db2d).
**Run** `RUN-INSTR-36c8cf-phaseA-v2-57ca9a`, terminal state `completed_valid`.

**THIS FILE DOES NOT REPLACE `execution_report.md`.** That report is the record
of the version-1 run `RUN-INSTR-36c8cf-phaseA-2a5cd1`, it is committed, and
DEC-20260810-56db2d cites it. It is left byte-identical. This is deviation D1.

**NOTHING IN THIS REPORT IS AN INTERPRETATION.** No hypothesis status is
changed, no completion criterion is claimed met, no instrument is declared good
or bad, no heuristic is declared validated or refuted, and no curve-side
statement of any kind appears.

---

## 1. Outcome in one paragraph

Phase A produced **one run**, `RUN-INSTR-36c8cf-phaseA-v2-57ca9a`, terminal
state `completed_valid`. **SR1 is discharged on the two construction-free
quantities** that amendment change G1 narrows it to: the delta = 0 median p
measured 0.05975 against the published 0.0590, absolute difference 0.00075
against the adopted tolerance 0.010; and the published "as % of mean" column
reproduced at 4 of 4 rows. **No planting construction was run at all.** The SR3
v3 reference characterisation ran in full at p = 4001 against the named
reference run `EXP-ICINV-55c2d8 / RUN-ICINV-p4001-fixed`, at all thirteen frozen
density rows, at T = 400, at the frozen per-row central coverage 259/260, with
z = Phi^-1(519/520) computed inside the run, at all three declared seed rungs
(12 / 24 / 48). **The E3 stability rule was not met at any rung**: rung 2 versus
rung 1 fails at 12 of 13 rows (worst 39.3% at fb = 22) and rung 3 versus rung 2
fails at 8 of 13 rows (worst 23.5% at fb = 7), against the frozen 5% threshold.
**Falsification criterion F4 therefore fires and the work STOPS.** The interval
was **not** widened, the coverage was **not** changed, nothing was gated with
it, and no interval was accepted — so the C-SELF-CONSISTENCY verdict is recorded
as `not_evaluated` with its reason, and the p = 6007 family was not reached and
is recorded as `not_measured`. Whether F4 firing bears on HEUR-INSTR-2, on the
SR3 v3 gate design, or on anything else is not this report's to say.

---

## 2. Base commit checked against `origin/main`

```
$ git fetch origin main
HEAD        = cbbdd003d9169ec07a31f1c1f569fd08a77bcdca   (the snapshot commit given in the task)
origin/main = 44525b6f7aad8f69a9909d0721518e0934e7f10a
merge-base  = 44525b6f7aad8f69a9909d0721518e0934e7f10a
```

**Merge outcome: no merge required.** The merge-base *is* `origin/main`, so the
branch is 0 commits behind it. The executor does not merge `main` into a working
branch in any case (role prohibition); had the branch been behind, that would
have been reported to the Coordinator rather than merged.

Manifest `code.commit = cbbdd003…`, `code.dirty = false` (tracked files clean).
The four new harness modules were untracked at run time and are pinned by
content hash — 13 executed source files, `all_pinned: true`.

---

## 3. The run

| field | value |
|---|---|
| run id | `RUN-INSTR-36c8cf-phaseA-v2-57ca9a` |
| status | `completed_valid` |
| wall seconds | 128.234 |
| CPU seconds | 116.06 |
| peak RSS | 72,450,048 bytes (0.067 GB) |
| certificate | `kind: none` — pure measurement run; no discrete-log solve and no factor-base relation is claimed anywhere |
| environment | macOS-26.6-arm64, Python 3.13.1, sympy 1.14.0, pyyaml 6.0.3 |
| command | `PYTHONPATH=. timeout 14400 python3 -m harness.exp_instr_36c8cf.phase_a_v2 --run-suffix 36c8cf-phaseA-v2-57ca9a` |

**Budget consumed, against the frozen budget.** Wall clock 128.2 s of 14400 s
per run; CPU 116.1 s of 24 CPU-hours; memory 0.067 GB of 8 GB; runs used **2 of
20** across the whole task (`RUN-INSTR-36c8cf-phaseA-2a5cd1` and this one), plus
one aborted attempt that consumed **no run identifier** (D2). **No budget event
occurred**; `metrics.budget_events` is empty. Nothing was stopped by budget.

### Host load, actually observed

Ten observations by `os.getloadavg()` **inside the run**, recorded in
`load-observations.json` and in `raw.host.load_observations`. Only observed
values appear anywhere in this report (CORR-20260810-7cf0e9).

| point | 1 min | 5 min | 15 min | elapsed (s) |
|---|---|---|---|---|
| start | 42.00 | 28.71 | 21.59 | 0.1 |
| after SR1 | 40.26 | 28.79 | 21.70 | 10.6 |
| during p=4001 measurement, curve 116/138 | 30.09 | 27.92 | 21.86 | 70.9 |
| after p=4001 measurement | 28.50 | 27.68 | 21.88 | 81.5 |
| after p=4001 rungs 1, 2, 3 / family / end | 24.57 | 26.75 | 21.83 | 128.2 |

14 cores. The run was **single-threaded and sequential**: no thread pool, no
subprocess worker, no parallel map. No trial was lost and no measurement was
dropped; the run terminated on its own stopping rule, not on a timeout.

---

## 4. SR1 — C-NULLC-REPRODUCTION, as narrowed by amendment change G1

### 4.1 What was frozen before the run

Read from the amendment at run time, not transcribed: the discharging quantities
are **Q1** (the delta = 0 median p) and **Q2** (the "as % of mean" column); the
Q1 match rule is absolute difference at most **0.010**; the Q2 match rule is that
the measured percentage rounds to the published value at **one** decimal place.
The twelve contract seeds are unchanged (E4). Published values are parsed from
`…/BATCH-cb71b5/reviews/red-team/red_team_notes.md` section 5 at run time and
bound by sha256.

### 4.2 Q1 — the delta = 0 (construction-free) row

Twelve repetitions of `harness.exp_icinv.permutation_null`, called **unmodified**
on the committed p = 4001 per-class `rate_m3`, over the twelve contract seeds.

| quantity | value |
|---|---|
| measured median p | **0.05975** |
| published median p | 0.0590 |
| absolute difference | 0.00075 |
| tolerance (adopted by G1) | 0.010 |
| **passes** | **true** |

Per-seed p-values: 0.0605, 0.0645, 0.0630, 0.0555, 0.0685, 0.0525, 0.0625,
0.0575, 0.0540, 0.0620, 0.0540, 0.0590.

### 4.3 Q2 — the published "as % of mean" column

Pooled mean of `rate_m3` = **0.5272722457627118** over the four committed
classes (sizes {-30: 138, -18: 98, 18: 98, 30: 138}), whose per-class `rate_m3`
vectors from `RUN-ICINV-p4001-a` and `RUN-ICINV-p4001-b` **agree exactly**.

| delta | measured % of mean | rounded | published | matches |
|---|---|---|---|---|
| 0.002 | 0.37931069 | 0.4 | 0.4 | true |
| 0.005 | 0.94827673 | 0.9 | 0.9 | true |
| 0.010 | 1.89655346 | 1.9 | 1.9 | true |
| 0.020 | 3.79310691 | 3.8 | 3.8 | true |

4 of 4 rows match.

### 4.4 Recorded, and explicitly not a discharging quantity

Power at delta = 0: measured **0.00**, published 0.08. Amendment G1 records this
as **not a discharging quantity and not a failure** — 0.08 is one repetition in
twelve and the published seed set is recorded nowhere, so a one-repetition
difference is not attributable to anything and is not read in either direction.

### 4.5 What was deliberately not done

**No planting construction was executed.** `metrics.sr1_constructions_run = 0`.
Change G1 removes the delta > 0 rows from the gate, records them as
**permanently unreproducible** because the generating construction was never
recorded, and forbids selecting a canonical construction now that all seven
candidate profiles are visible in the version-1 run. None was selected and none
was re-run.

### 4.6 SR1 verdict

**SR1 is discharged on the construction-free quantities** (Q1 and Q2 both pass).
Under the contract's stopping rule, the characterisation then proceeded.

---

## 5. SR3 v3 reference characterisation

### 5.1 The reference runs, named explicitly

Identified from `harness/exp_icinv_fullgroup.py:BASELINE_RUNS_V2` — the committed
map that EXP-ICINV-4d33aa amendment v2 change A1 fixes — and read from their own
records with `raw-result.json` and `manifest.yaml` both hashed:

| prime | reference run | seed | T | class | curves | raw sha256 |
|---|---|---|---|---|---|---|
| 4001 | `EXP-ICINV-55c2d8 / RUN-ICINV-p4001-fixed` | 20260807 | 400 | trace 30, order 3972 | 138 | `251d58c7a4eb…` |
| 6007 | `EXP-ICINV-55c2d8 / RUN-ICINV-f09176` | 20260807 | 400 | trace 8 | 140 | `7fcc505bc42b…` |

The class-selection rule of the reference driver was **re-executed** and its
result checked against the reference run's own recorded trace, order and curve
count: agreement at p = 4001 (trace 30, order 3972, 138 curves). A disagreement
would have been fatal.

### 5.2 The frozen gate parameters, as read

| parameter | value | source |
|---|---|---|
| density rows | {4,5,6,7,8,9,10,11,12,13,15,18,22} | `EXP-ICINV-4d33aa/specification.yaml` (cited by G5/D1), cross-checked against the amendment |
| target count | 400 | same |
| rows gated | 13 | amendment G2 |
| family-wise target | 0.05 | amendment G2 |
| per-row two-sided alpha | 1/260 | amendment G2 (exact fraction) |
| per-row central coverage | 259/260 = 0.996153846… | amendment G2 (exact fraction) |
| interval quantiles | 1/520 and 519/520 | amendment G2 (exact fractions) |
| estimator | mean ± z·sd, sd = sample (n−1) | amendment G3 E1 |
| **z** | **2.8905115606917384** | **computed at run time** as `NormalDist().inv_cdf(519/520)`; the amendment's approximate 2.8905 is never read into the arithmetic |
| seed rungs | 12 / 24 / 48 | amendment G3 E2 |
| rung 2 adds | 20260821–20260832 | amendment G3 E2 |
| rung 3 adds | 20260833–20260856 | amendment G3 E2 |
| stability rule | half-width change < 5% relative at every row | amendment G3 E3 |

**Family scope, as declared:** one prime's thirteen rows is one family. p = 4001
and p = 6007 are two families, taken in ascending order, frozen before any
measurement. Nothing is pooled across primes.

### 5.3 Faithfulness of the measurement

| check | result |
|---|---|
| shared-sum-set path vs `run_saturation.measure_at_density` (unmodified), seed 20260807, 13 rows | **13/13 bit-exact** on the variance ratio |
| same, seed 20260810 (first contract seed), 13 rows | **13/13 bit-exact** |
| re-measurement at the reference run's own seed vs the reference run's **committed** per-row variance ratios | agrees to **≤ 1.56e-14 relative** (max over 13 rows); 1 row bit-identical, 12 rows differing at float ULP level — see deviation D5 |

### 5.4 The per-row sampling distribution and its interval, p = 4001

Rung 3 (48 seeds) shown; rungs 1 and 2 are in
`sr3v3-reference-sampling.json` and in `raw.sr3v3_families`. `min@seed` /
`max@seed` are the **tail check** the contract requires (extreme per-seed ratios
listed, so the endpoints can be seen rather than trusted).

| fb | mean density \|3V\|/#E | mean VR | sd | half-width | interval | min | max |
|---|---|---|---|---|---|---|---|
| 4 | 0.0239 | 1.7883 | 0.2643 | 0.7641 | [1.0242, 2.5523] | 1.3365 | 2.2682 |
| 5 | 0.0442 | 1.8876 | 0.2114 | 0.6110 | [1.2766, 2.4986] | 1.5133 | 2.3970 |
| 6 | 0.0735 | 2.1826 | 0.2651 | 0.7664 | [1.4162, 2.9489] | 1.5643 | 2.7108 |
| 7 | 0.1125 | 2.7166 | 0.3164 | 0.9145 | [1.8022, 3.6311] | 2.1575 | 3.5295 |
| 8 | 0.1628 | 2.4186 | 0.2423 | 0.7004 | [1.7181, 3.1190] | 1.9196 | 3.0276 |
| 9 | 0.2227 | 2.1702 | 0.1829 | 0.5286 | [1.6417, 2.6988] | 1.8529 | 2.5933 |
| 10 | 0.2901 | 2.4790 | 0.2198 | 0.6353 | [1.8437, 3.1143] | 1.9613 | 2.8881 |
| 11 | 0.3657 | 2.6301 | 0.2184 | 0.6313 | [1.9988, 3.2614] | 2.2212 | 3.3358 |
| 12 | 0.4441 | 2.4792 | 0.2095 | 0.6054 | [1.8738, 3.0846] | 1.8747 | 2.9554 |
| 13 | 0.5282 | 2.4889 | 0.2135 | 0.6170 | [1.8719, 3.1059] | 1.9706 | 2.8498 |
| 15 | 0.6813 | 2.9259 | 0.2940 | 0.8499 | [2.0760, 3.7758] | 2.3813 | 3.6261 |
| 18 | 0.8589 | 3.4336 | 0.3357 | 0.9702 | [2.4634, 4.4038] | 2.6903 | 4.2118 |
| 22 | 0.9725 | 3.1610 | 0.4675 | 1.3512 | [1.8098, 4.5123] | 2.3616 | 4.8231 |

Every row is also reported **stratified by r = #{x : x³+ax+b = 0}** in the run
record (class composition r = 1: 72 curves, r = 3: 66 curves). That
stratification gates nothing.

### 5.5 C-SEED-STABILITY — interval width against seed count

Relative change in half-width against the previous rung, threshold 5%:

| fb | rung 2 vs 1 | within 5%? | rung 3 vs 2 | within 5%? |
|---|---|---|---|---|
| 4 | 0.1908 | no | 0.0873 | no |
| 5 | 0.1428 | no | 0.0219 | yes |
| 6 | 0.1521 | no | 0.0436 | yes |
| 7 | 0.1330 | no | **0.2354** | no |
| 8 | 0.0003 | yes | 0.1210 | no |
| 9 | 0.1232 | no | 0.1046 | no |
| 10 | 0.0709 | no | 0.0352 | yes |
| 11 | 0.1035 | no | 0.1062 | no |
| 12 | 0.1705 | no | 0.0413 | yes |
| 13 | 0.1952 | no | 0.0242 | yes |
| 15 | 0.2696 | no | 0.0519 | no |
| 18 | 0.1680 | no | 0.0924 | no |
| 22 | **0.3932** | no | 0.0590 | no |

Rung 2: met at **1 of 13** rows. Rung 3: met at **5 of 13** rows.
**The rule requires every one of the thirteen rows. It is not met at any rung.**

### 5.6 F4 fires, and what was NOT done about it

Under amendment change G3 E3, verbatim: *the interval HAS NOT STABILISED,
HEUR-INSTR-2 is not validated at 48 seeds, falsification criterion F4 fires, the
work STOPS and the Coordinator is told. The interval is NOT widened and the
coverage is NOT changed.*

That is exactly what the run did. `metrics.sr3v3_families["4001"].F4_fired =
true`, `accepted_rung = null`, `interval_stabilised = false`. **No interval was
widened. No coverage was changed. Nothing was gated with any interval. No rung
was re-run with different seeds. No threshold was re-read after seeing the
result.**

### 5.7 C-SELF-CONSISTENCY

Recorded as **`not_evaluated`**, with its reason: E3 was not met, so **no
interval of this family is accepted**, and comparing the re-measurement against
a non-accepted interval would be gating with an interval the protocol does not
accept. The inputs a reviewer needs are all in the run record and nothing was
withheld: the faithful re-measurement at the reference run's own seed appears
per row in `sr3v3-self-consistency.json`
(`faithfulness_verification` and `reference_run_reproduction`), and every rung's
per-row interval appears in `sr3v3-reference-sampling.json`. No verdict is
computed from them here, because computing one now — after seeing F4 — would be
a post-hoc metric.

### 5.8 p = 6007

**`not_measured`.** Reason recorded verbatim in the artifacts: *"F4/E3: the
interval did not stabilise at p = 4001. The work stops; the interval is not
widened and the coverage is not changed."* The stop rule was frozen before the
run as a stop of the whole characterisation, not of one family.
**An unmeasured family is not a passed family.** It blocks the SR3 v3 gate of
EXP-ICINV-4d33aa at p = 6007.

### 5.9 The superseded band, stated plainly (contract success criterion 6)

Read from `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml` post_review_notes A5
**at run time** and bound by sha256 `5c1deda815e5…`: the superseded **[1.3, 3.6]**
band **was the outward-rounded hull of the committed rows it gated** — floor
slack **0.020397**, ceiling slack **0.011900**. That — **not** a failure of the
campaign's finding — is why literal band membership is being replaced.

**The cost of the chosen replacement, restated as the amendment requires it to
be restated wherever the gate is cited:** the family-wise construction makes the
gate **less sensitive to a small genuine baseline regression** than a 95%
per-row gate would be, and **if a future run passes this gate, that is not
evidence of no regression below its detection floor**. Separately, HEUR-INSTR-3
(the Gaussian tail rule at coverage 259/260) is a declared, unvalidated
approximation at precisely the coverage where such approximations are weakest;
the per-row extremes in section 5.4 are the tail check that lets it be seen
rather than trusted.

---

## 6. Cell coverage

| cell | status |
|---|---|
| SR1 / NULL-C / committed p=4001 four-class geometry / Q1 delta = 0 median p | **measured** |
| SR1 / NULL-C / same geometry / Q2 "as % of mean" column | **measured** |
| SR1 / NULL-C published delta > 0 rows | **permanently unreproducible** (G1; construction never recorded; no construction selected) |
| SR3 v3 / NULL-B variance ratio / `RUN-ICINV-p4001-fixed` geometry / all 13 rows at T=400 | **measured**; F4 fired, no interval accepted |
| SR3 v3 / p = 6007 family | **not_measured** — blocks the SR3 v3 gate of EXP-ICINV-4d33aa at p = 6007 |
| every Phase B (statistic, geometry, density row) cell | **not enumerable**, hence **not_measured** |

**Phase B blockers, as named by the amendment and unchanged by this run.**
**B1** — the T5 walk-kernel bias ladder is undeclared and the Velu-constructed
107-volcano does not exist yet; the T5 walk cell is `not_measured` and **BLOCKS
the T5 reachability conclusion of EXP-VOLC-9f5571**. **B2** — neither
EXP-JINV-bd141d nor EXP-VOLC-9f5571 declares a numeric density grid, so every
per-density-row Phase B cell is not even enumerable; **every arm verdict of
EXP-JINV-bd141d and EXP-VOLC-9f5571 remains BLOCKED under GOAL-ENDO-001
criterion C4**. Phase A was told to stop at the phase boundary if it found
itself needing real class geometry. It did not need any: no geometry-specific
control was attempted.

**An unmeasured control is not a passed control.** Stating that a cell blocks a
lane conclusion is the factual statement the contract requires; deciding what
follows for the lane is the Coordinator's.

---

## 7. Controls demanded by the dispatch

| control | where it stands |
|---|---|
| `targets_B`, never `targets_uniform` | **CONFLICT-1, OPEN — see section 8.** The reference characterisation used the reference run's own sampler, as the contract requires. No new arm was added. |
| stratify on r and report the strata wherever a target is drawn | **honoured**: every row is reported per r-stratum; class composition r=1: 72, r=3: 66 |
| sweep factor-base density across the thirteen rows, never the saturated row alone | **honoured**: all 13 rows at every rung |
| NULL-C disqualified for any within-class contrast | **honoured**: NULL-C is used in SR1 only, on the between-class contrast over the four committed p = 4001 classes, and nowhere else in this run |
| C-SEED-STABILITY | **measured and reported** (section 5.5) |
| C-SELF-CONSISTENCY | **`not_evaluated`** with reason (section 5.7) |
| C-PSEUDO-CRATER, C-ARBITRARY-HALVES, C-LABEL-PERMUTATION, C-NUISANCE-DIRECTION, C-DOWNWARD-SWEEP | **Phase B, not run** (SR2; B1; B2) |

---

## 8. CONFLICT-1 — recorded, not resolved by this run

The dispatching envelope carries the standing control *"targets_B, NEVER
targets_uniform"*. The frozen contract's `characterisation_procedure` requires
re-measuring **the reference run at its own frozen parameters**, and names the
**sampler** among them; the reference run's own sampler is
`exp_icinv.targets_uniform`, read from its own recorded command and code path.

**Action taken: the contract was followed.** Substituting `targets_B` would
characterise a *different estimand* — the sampling distribution of a different
arm — so it would not be a re-measurement of the reference run at all, and
C-SELF-CONSISTENCY ("a faithful re-measurement of the reference run at its own
parameters compared against its own interval") would be vacuous.

**What was deliberately not done:** no `targets_B` arm was added. Adding an arm
the frozen contract does not declare is a scope extension forbidden by SR5
without a versioned amendment filed before the data is generated, and the
executor does not write amendments.

**Scope of the conflict:** the SR3 v3 characterisation only. Phase A draws
targets nowhere else — SR1 under G1 draws no targets at all, it permutes
committed measured values.

The conflict was declared **before any measurement** (`conflict-1.json`,
`raw.conflict_1`, and the driver's frozen-parameter checkpoint). **Adjudication
belongs to the Coordinator.**

---

## 9. Protocol deviations

**D1 — report filename.** The handoff names `execution_report.md`. That file is
committed, describes the version-1 run, and is cited by DEC-20260810-56db2d;
overwriting it would destroy a record a decision rests on. This report is at
`execution_report_v2.md` in the same directory instead.

**D2 — one aborted attempt, disclosed in full.** Attempt 1 (suffix
`36c8cf-phaseA-v2-479dc9`) aborted with a `RuntimeError` **before any run
directory was created**; it consumed no run identifier and produced no interval.
Its defect was in the *faithfulness check*, not in the measurement: the check
required the row **mean rate** to match bit-exactly, but the reference driver
reports that mean as `statistics.mean(rates)` while the verdict object it
returns computes `sum(rates)/n`, and those differ in the last bits at fb = 7 and
fb = 18 **inside the reference driver itself**. The check was corrected to test
bit-exact equality of **the variance ratio** (the statistic being characterised)
and to report both mean values with their difference. **No measurement code
changed.** Attempt 1's checkpoints are retained at `staging-…-479dc9/`. Full
account in `implementation.md`.

**D3 — sum sets shared across seeds.** The reference driver recomputes the
seed-independent m = 3 sum set on every call; this run computes it once per
(curve, fb) and scores every seed against it, which the contract states is what
bounds the cost. Verified bit-exact against the unmodified reference driver at
13/13 rows at two seeds (section 5.3).

**D4 — the reference run's own seed measured in addition to the rung seeds.**
Seed 20260807 is not in any rung seed set, but C-SELF-CONSISTENCY requires a
re-measurement *at the reference run's own parameters*, of which its seed is one.
It is measured in addition; it enters no interval and no rung.

**D5 — non-bit-exact agreement with the committed reference rows.** Max relative
delta 1.56e-14 over the 13 rows (one row bit-identical). The committed run ran on
Linux x86_64 / Python 3.11.15; this run on macOS arm64 / Python 3.13.1. Nothing
in this run gates on bit-exactness against the committed record, and no
tolerance was invented for it: every per-row delta is reported as measured.

**D6 — CONFLICT-1** (section 8). **OPEN.**

**D7 — p = 6007 not reached.** Recorded as `not_measured` with its reason
(section 5.8), per the stop rule frozen before the run. Not a pass.

**D8 — inference policy fallback.** `requested_policy: executor-implementation`;
`AUTORESEARCH_POLICY` unset, so the adapter-resolved environment was not applied
and the session model answered. `fallback_used: true` with the reason is
recorded in `inference-provenance.json`, in `baseline-provenance.json` and in
`raw.inference_provenance`. Known and already recorded as defect **D4 of
DEC-20260810-d70ece**; not this task's to fix. The model that actually answered
is recorded as `claude-opus-5`; `model_verified: false` (no adapter probe
receipt). The manifest's own `inference` block is `harness/runner.py`'s static
deterministic-execution block, and `runner.py` is read-only to this task.

**D9 — staging directories.** Incremental checkpoints were written to
`staging-<suffix>/` under the execution directory for session survival. These
are extra paths beyond the handoff's deliverables list and are retained.

**D10 — three artifacts beyond the twenty required**: `conflict-1.json`,
`inference-provenance.json`, `load-observations.json`. Nothing required is
missing.

**No other deviation occurred.** No infrastructure failure, no timeout, no
crash, no OOM, no lost trial, no dropped measurement, no re-run after seeing a
result.

---

## 10. Provenance

**Source provenance (blocking A6 precondition).**

```
$ python3 tools/check_run_source_provenance.py --experiment EXP-INSTR-36c8cf --strict
2 pinned, 0 unpinned, 0 unreadable, of 2 run manifest(s) in scope
exit 0
```

13 executed source files pinned by sha256 in this run's manifest, `all_pinned:
true`, `code.dirty: false`.

**No transcribed reference values.** Every reference value — the published
NULL-C profile, the SR1 tolerance and rounding rule, the coverage and its exact
fractions, the seed rungs and their ranges, the stability threshold, the
thirteen density rows, T, the detection-bound table, the [1.3, 3.6] band and its
slacks, the reference runs' identities, seeds, parameters and per-row values, and
the budget — is read from its committed record at run time and bound by a
sha256 in `baseline-provenance.json`. **z is computed at run time** from the
frozen exact fraction 519/520; no reference value is written into source at any
precision.

**Certificate.** `kind: none`, explicitly. This is a pure measurement run: no
discrete-log solve and no factor-base relation is claimed anywhere.

**Reproduction and raw/summary agreement, checked after the run in a fresh
process.**

* The rung-3 interval at fb = 22 recomputes **bit-exactly** from the stored
  per-seed ratios: mean, sd, and both endpoints.
* The two extreme per-seed ratios of that row, which are the tail check's
  endpoints, reproduce **bit-exactly** from a fresh measurement: seed 20260840 →
  2.3616054016546686, seed 20260830 → 4.823059054262121.
* `manifest.result.metrics` agrees with `raw-result.json` on the SR1 Q1 median p
  and on the F4 flag; `sr3v3-reference-sampling.json` agrees with
  `raw.sr3v3_families` on the interval endpoints.

No additional run identifier was consumed by these checks.

---

## 11. Scope and honesty

`claim_tier` **toy**. Instruments only, on toy-scale objects: the committed
p = 4001 four-class geometry (~12 bits) and the p = 4001 trace-30 class of 138
curves. **No curve-side claim is made at any scale. No attack, no exponent, no
speedup. `sota_delta` zero on every axis.** `dominated_by` parallel Pollard rho
with distinguished points at 0.886·sqrt(N) group operations and O(1) memory
(KN-TECH-001, KN-TECH-006) and, on CM curves, its automorphism-discounted
variant (KN-TECH-018), under which any factor at or below sqrt(6) ≈ 2.449 is
baseline calibration and never an attack.

Every number here applies to exactly the geometry it was measured at and
transfers to no other. Redesigning the SR3 gate re-adjudicates nothing:
EXP-ICINV-4d33aa's two INVALID terminations were admissibility failures in the
gate and bear on neither H-ICINV-6c7920 nor EV-ENDO-10109d.

**Statuses this run does not move and does not comment on:** H-INSTR-444c7b
stays `specified`; H-ICINV-6c7920 stays `specified`, neither presumed true nor
false; H-ICINV-d5e351 stays `specified`; H-ENDO-001 stays `approved`; H-STR-002
stays `weakened`. No evidence record is written. No completion criterion is
claimed. GOAL-ENDO-001 criterion C4 is **not** discharged. No attestation and no
closure quorum. Nothing here is committed by the executor, and nothing is
durable until the Coordinator's snapshot archive is committed, pushed and
accepted by the post-commit verifier.

---

## 12. Artifact paths

Run record — `experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/`:
`manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`raw-result.json`, `nullc-reproduction.json`, `geometry-inputs.json`,
`detection-floors.json`, `false-positive-rates.json`,
`pseudo-crater-control.json`, `arbitrary-halves-control.json`,
`label-permutation-control.json`, `nuisance-direction.json`,
`nullc-matched-order-recharacterisation.json`, `sr3v3-reference-sampling.json`,
`sr3v3-interval-stability.json`, `sr3v3-self-consistency.json`,
`baseline-provenance.json`, `cell-coverage.json` (the twenty required), plus
`conflict-1.json`, `inference-provenance.json`, `load-observations.json`.

Harness — `harness/exp_instr_36c8cf/`: `refvalues_v2.py`, `sr1_g1.py`,
`sr3v3.py`, `phase_a_v2.py` (new); `refvalues.py`, `sr1.py`, `phase_a.py`
(untouched version-1 modules).

Execution —
`coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/`:
this report, `implementation.md`, `staging-36c8cf-phaseA-v2-479dc9/`,
`staging-36c8cf-phaseA-v2-57ca9a/`, and the untouched version-1
`execution_report.md`.

**Untouched and not superseded:**
`experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-2a5cd1/` remains
exactly as recorded, `completed_invalid` / `specification_error`.
