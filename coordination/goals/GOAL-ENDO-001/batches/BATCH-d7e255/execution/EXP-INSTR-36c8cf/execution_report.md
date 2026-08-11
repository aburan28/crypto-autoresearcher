# EXP-INSTR-36c8cf — execution report

**Task** TASK-20260810-c98659 · **Goal** GOAL-ENDO-001 · **Batch** BATCH-d7e255
· **Contract** `experiments/EXP-INSTR-36c8cf/specification.yaml` version 1,
sha256 `de3369049eaba01290f7a320d24a94e531e168891cc77b83b62962e9e6bde3f9`
· **Approving decision** DEC-20260810-a4bec4 · **claim_tier** toy

This report covers **PHASE A ONLY**. Phase B is not dispatched and was not run.
It will be appended to this same report when Phase B is dispatched as a
resumption of this task id, per the handoff's two-phase structure.

**NOTHING IN THIS REPORT IS AN INTERPRETATION.** No hypothesis status is
changed, no completion criterion is claimed met, no instrument is declared good
or bad, and no curve-side statement of any kind appears.

---

## 1. Outcome in one paragraph

Phase A produced **one run**, `RUN-INSTR-36c8cf-phaseA-2a5cd1`, terminal state
`completed_invalid`, classification **`specification_error`** (two of them). The
SR1 reproduction gate reproduced the construction-free `delta = 0` row of
NULL-C's published power profile and reproduced the published "as % of mean"
column exactly, but **no** declared planting construction reproduced the
`delta > 0` rows — and the construction and permutation seeds that generated
those rows are recorded in no committed record. The SR3 v3 reference
characterisation **was not run and no data for it was generated**, because the
frozen contract declares no numeric coverage for its "declared central
interval". Both are frozen pre-registered parameters that the executor may not
invent. Per the contract's own SR1 stopping rule, nothing downstream was
characterised.

---

## 2. Base commit checked against `origin/main`

```
$ git fetch origin main
HEAD          = 761e206c682a50555068f8aae009e011d4442215   (= the snapshot commit given in the task)
origin/main   = 44525b6f7aad8f69a9909d0721518e0934e7f10a
merge-base    = 44525b6f7aad8f69a9909d0721518e0934e7f10a
left/right    = 0 behind, 6 ahead
```

**Merge outcome: no merge required.** The branch is 0 commits behind
`origin/main`; the merge-base *is* `origin/main`. The executor does not merge
`main` into a working branch in any case (role prohibition); had the branch been
behind, this would have been reported to the Coordinator rather than merged.

Working tree at run time: `dirty: false` for tracked files. The four new harness
modules were untracked and are pinned by content hash (below).

---

## 3. The run

| field | value |
|---|---|
| run id | `RUN-INSTR-36c8cf-phaseA-2a5cd1` |
| status | `completed_invalid` |
| classification | `specification_error` |
| command | `PYTHONPATH=. python3 -m harness.exp_instr_36c8cf.phase_a --run-suffix 36c8cf-phaseA-2a5cd1` |
| wall clock | 220.232 s (budget 14400 s/run) |
| CPU | 214.502 s ≈ 0.0596 CPU-hours (budget 24 CPU-hours total) |
| peak RSS | 74 924 032 B ≈ 0.070 GB (budget 8 GB) |
| runs used | 1 of 20 |
| certificate | `kind: none`, `verified: true`, verifier `no-claim` — pure measurement run; no discrete-log solve and no factor-base relation is claimed anywhere |
| parallelism | none; single-threaded, sequential, launched with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` under `timeout 14400` |

**No budget figure was exhausted and no infrastructure event occurred.** No
trial was lost, no cell was dropped to host contention, and the run was not
truncated.

### Host load, actually observed

`os.getloadavg()` on a 14-core host, recorded inside the run and written to
`raw-result.json` → `raw.host`:

| point | 1 min | 5 min | 15 min |
|---|---|---|---|
| immediately before the run (`2026-08-10T17:32:47-0700`) | 14.84 | 14.67 | 18.17 |
| immediately after the run (`2026-08-10T17:36:27-0700`) | 17.42 | 15.64 | 17.76 |

Also observed from the shell (`uptime`), reported because CORR-20260810-7cf0e9
was issued in this batch for a load figure that appeared in no artifact:
`17:16 … 22.91 21.17 26.29` at task start, `17:32 … 14.84 14.67 18.17` at
launch, `17:36 … 16.43 15.49 17.68` at completion. Every figure in this section
was read from a program's output; none is estimated.

---

## 4. SR1 — C-NULLC-REPRODUCTION

### 4.1 What was frozen before the graded run

* **Statistic**: `harness.exp_icinv.permutation_null` (NULL-C), **unmodified**,
  at its default 2000 iterations. `harness/exp_icinv.py` was not edited.
* **Data**: per-class `rate_m3` at p = 4001, read at run time from the two
  committed runs `experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a` and
  `…/RUN-ICINV-p4001-b`. The two vectors were compared and **agree exactly**;
  class sizes `{-30: 138, -18: 98, 18: 98, 30: 138}`, 472 curves in 4 classes.
* **Deltas**: read at run time from `red_team_notes.md` §5 —
  `[0.0, 0.002, 0.005, 0.010, 0.020]`.
* **Seeds**: the twelve seeds declared in the contract's `replication.seeds`,
  12 repetitions per cell.
* **Constructions**: seven declared additive between-class mean-shift
  constructions, **all run, all reported, none selected after the fact**.
* **Tolerance**: |Δ median p| ≤ 0.010 and |Δ power| ≤ 1/12.
  **EXECUTOR-DECLARED, because the contract declares none** — flagged in §6 as
  part of the specification gap. All raw numbers are in
  `nullc-reproduction.json` so any other rule can be applied by a reviewer.

### 4.2 What reproduced

* **Construction-free `delta = 0` row: REPRODUCED.** measured median
  p = **0.0597** over the twelve declared seeds against the published 0.0590
  (read from the record at run time). Measured power at α = 0.05 was **0.00**
  against the published 0.08; 0.08 is one repetition in twelve, and the
  published seed set is not recorded, so this is one repetition of difference at
  the tolerance boundary. Per-seed p-values are in `nullc-reproduction.json`.
* **The published "as % of mean" column: REPRODUCED EXACTLY.** Pooled mean of
  `rate_m3` measured 0.527272, giving 0.38 / 0.95 / 1.90 / 3.79 % against the
  published 0.4 / 0.9 / 1.9 / 3.8 %. This binds the harness to the same data as
  the published table.

### 4.3 What did not reproduce

`d=` rows are median p over the twelve declared seeds, `pw=` is power at
α = 0.05. Published targets: `d=0.000 med=0.0590 pw=0.08`,
`d=0.002 med=0.0595 pw=0.08`, `d=0.005 med=0.0055 pw=1.00`,
`d=0.010 med=0.0000 pw=1.00`, `d=0.020 med=0.0000 pw=1.00`.

| construction | d=0.000 | d=0.002 | d=0.005 | d=0.010 | d=0.020 | rows matching |
|---|---|---|---|---|---|---|
| `ladder_unit` | 0.0597 / 0.00 | 0.0037 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 4/5 |
| `ladder_total` | 0.0597 / 0.00 | 0.0305 / 1.00 | 0.0080 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 4/5 |
| `ladder_centered` | 0.0597 / 0.00 | 0.0037 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 4/5 |
| `top_class_up` | 0.0597 / 0.00 | 0.0323 / 1.00 | 0.0072 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 4/5 |
| `bottom_class_up` | 0.0597 / 0.00 | 0.0860 / 0.00 | 0.1003 / 0.00 | 0.0522 / 0.25 | 0.0000 / 1.00 | 2/5 |
| `halves_aligned` | 0.0597 / 0.00 | 0.0240 / 1.00 | 0.0030 / 1.00 | 0.0000 / 1.00 | 0.0000 / 1.00 | 4/5 |
| `halves_antialigned` | 0.0597 / 0.00 | 0.1042 / 0.00 | 0.1467 / 0.00 | 0.0955 / 0.00 | 0.0000 / 1.00 | 2/5 |

**Constructions reproducing the full published profile: none.** Every
construction fails at exactly one row, `delta = 0.002`, and fails it in one of
two directions: the four gradient-aligned constructions already reach power 1.00
there (published: 0.08), and the two gradient-opposed constructions have not
reached power 1.00 even at `delta = 0.005` (published: 1.00).

**The measured fact behind that split, stated without interpretation.** The four
committed classes already carry an ordered class-mean gradient in the
unperturbed data — class means 0.52395, 0.52500, 0.52954, 0.53060 in ascending
trace order — so an additive between-class shift is constructive or destructive
depending on its sign relative to that gradient, and the published profile's
flat `delta = 0.002` row followed by a saturated `delta = 0.005` row lies
between the two families measured here.

### 4.4 SR1 verdict

**SR1 IS NOT DISCHARGED AS WRITTEN, AND THE REASON IS A SPECIFICATION GAP, NOT A
HARNESS DEFECT.** See §6, gap G1. Under the contract's own SR1 stopping rule
("STOP, run INVALID, return the defect, and characterise nothing"), nothing
downstream of SR1 was characterised.

**What this is NOT.** It is not evidence that the control harness exercises a
different statistic from the one the red team exercised: the committed
`permutation_null` is called unmodified on the committed data, and both
construction-free reproducible quantities (the `delta = 0` row and the
"% of mean" column) reproduce. It is not a finding about NULL-C, about
H-ICINV-6c7920, about EV-ENDO-10109d, or about any curve.

---

## 5. SR3 v3 reference characterisation — NOT RUN, NO DATA GENERATED

**No SR3 v3 data of any kind was generated.** This is deliberate and is not a
budget, host or schedule outcome.

The frozen contract requires the acceptance region to be "a declared central
interval" of the reference run's own empirical sampling distribution, but
**declares no numeric coverage for that interval**. A machine check inside the
run parsed `experiments/EXP-INSTR-36c8cf/specification.yaml` at run time for any
numeric coverage or nominal level attached to that interval and found
`numeric_interval_coverage_declared: false`, with the phrases
`declared central interval`, `interval coverage`, `DECLARED NOMINAL LEVEL` and
`declared level` all present **without a number**. The check is recorded in
`baseline-provenance.json` and `raw-result.json` so the STOP is auditable rather
than asserted. No numeric coverage is supplied by H-INSTR-444c7b,
DEC-20260810-a4bec4, DEC-20260809-de11f9, `EXP-ICINV-4d33aa/specification.yaml`
or its amendments v1/v2 either (all searched).

**Why the data was not generated first and the coverage declared afterwards.**
Emitting the per-density-row sampling distributions and then choosing the
coverage would fit the acceptance region to the data it gates — the exact defect
the v3 redesign exists to repair. The gate is therefore stopped **before** any
sampling data exists.

`sr3v3-reference-sampling.json`, `sr3v3-interval-stability.json` and
`sr3v3-self-consistency.json` are present in the run directory and each records
`status: not_measured`, `data_generated: false`, the reason, and what it blocks.

**SR4 (no widening) was not reached, and there is nothing to widen.** No
interval was constructed, none was widened, and no coverage was changed. The
self-consistency check was not run, so its verdict is `not_measured` — not a
pass and not a failure.

**What this blocks (factual statement required by the contract, not an
interpretation).** The redesigned SR3 gate of EXP-ICINV-4d33aa is not evaluable,
so it cannot gate a successor run of EXP-ICINV-4d33aa; and GOAL-ENDO-001
criterion C4 is not discharged for the SR3 v3 gate. Deciding what follows is the
Coordinator's.

### The superseded [1.3, 3.6] band (values read from the record at run time)

Read at run time from `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml`
(sha256 `5c1deda815e52330a3b15acc6aa1b3f8bea370c05c2108061f8a1ed7e50f0a42`),
key `post_review_notes.A5_new_standing_caution_on_the_band`: band low **1.3**,
band high **3.6**, **floor slack 0.020397**, **ceiling slack 0.011900**, and the
record's own statement that the band is the outward-rounded hull of the
committed rows it gates and that 1.3 is a hull edge, not an independent
threshold.

**Stated plainly, as the completion gate requires:** the superseded [1.3, 3.6]
band was the outward-rounded hull of the committed rows it gated, with under 2%
margin at the floor, and **this — not a failure of the campaign's finding — is
why literal band membership is being replaced.** The cost the chosen replacement
imposes, recorded and not minimised: the gate cannot be evaluated until the
reference run's per-density-row sampling variance has been characterised; that
characterisation does not exist today; producing it is additional work; and it
delays the successor run of EXP-ICINV-4d33aa and, through the C4 block,
EXP-JINV-bd141d and EXP-VOLC-9f5571, relative to the cheaper interior-rows
option. **This Phase A adds a further increment to that cost**: the
characterisation cannot even begin until a coverage is declared by amendment.

EXP-ICINV-4d33aa's two INVALID terminations were admissibility failures in the
gate and bear on neither H-ICINV-6c7920 nor EV-ENDO-10109d. Nothing in this run
re-adjudicates either record.

---

## 6. Specification errors returned (both are `specification_error`)

### G1 — the SR1 planting construction and permutation seed set

* **Missing field**: `EXP-INSTR-36c8cf` `controls[0]` (C-NULLC-REPRODUCTION) —
  the planting construction that produced the published `delta > 0` rows, and
  the twelve permutation seeds used for them. Also: no numeric tolerance for
  what "reproduce" means.
* **Where it is not**: `red_team_notes.md` §5 states the profile and not the
  construction; `red_team_report.yaml` objection O3 restates the profile and
  adds no construction; no script survives in the red-team review directory
  (it holds exactly two files, `red_team_notes.md` and `red_team_report.yaml`);
  the contract supplies neither.
* **Consequence**: SR1 as written is not reproducible from committed records.
* **Resolution**: a Coordinator `protocol_amendment` declaring the SR1 planting
  construction, the seed set, and the match tolerance, filed **before** the
  affected data is generated.

### G2 — the numeric coverage of the SR3 v3 central interval

* **Missing field**: `EXP-INSTR-36c8cf` `inputs.sr3_amendment_v3.change` and
  `inputs.sr3_amendment_v3.characterisation_procedure` — the numeric **coverage**
  of the "declared central interval".
* **Consequence**: the entire SR3 v3 reference characterisation is not
  executable under freeze discipline; no data was generated.
* **Resolution**: a Coordinator `protocol_amendment` declaring the coverage
  before the data is generated. Note also that the contract's `preregistered_
  prediction` (2) and its matched-null cells refer to a "declared nominal level"
  which is likewise numeric-free; Phase B will hit that gap for
  `false-positive-rates.json` unless the same amendment declares it, together
  with the density rows and the planted-size ladders (`SR3 DOWNWARD SWEEP`
  refers to "the declared maximum" and "the declared minimum", neither of which
  is a number in the contract).

The executor does not author amendments (handoff constraint) and did not.

---

## 7. Cell coverage

Full machine-readable table: `cell-coverage.json`. **An unmeasured control is
not a passed control.**

| cell | status | blocks |
|---|---|---|
| SR1 / NULL-C / committed p=4001 4-class geometry / `delta = 0` | **measured** (median p 0.0597, power 0.00, twelve declared seeds) | — |
| SR1 / NULL-C / same geometry / `delta > 0` rows | **not reproducible from committed records** (G1) | the SR1 gate cannot be discharged as written, so under the contract's own stopping rule nothing downstream of it is characterised |
| SR3 v3 / variance-ratio statistic / reference-run geometry / every density row | **not_measured**, no data generated (G2) | the redesigned SR3 gate of EXP-ICINV-4d33aa is not evaluable; no successor run may be dispatched; C4 not discharged for that gate |
| every Phase B (statistic, geometry, density row) cell | **not enumerable yet** | every arm verdict of EXP-JINV-bd141d and EXP-VOLC-9f5571 |

The Phase B cells are recorded as *not enumerable*, not merely unmeasured: they
cannot be listed until Stage 1 of EXP-JINV-bd141d and EXP-VOLC-9f5571 emits the
real class census, the real per-level vertex counts and the real Velu volcano.
Enumerating them from the design document would be reporting a control at an
assumed geometry, which is an invalidation rule of this contract.
`geometry-inputs.json`, `detection-floors.json`, `false-positive-rates.json`,
`pseudo-crater-control.json`, `arbitrary-halves-control.json`,
`label-permutation-control.json`, `nuisance-direction.json` and
`nullc-matched-order-recharacterisation.json` are each present recording
`status: not_measured`, phase B, and what they block.

---

## 8. Controls demanded by the dispatch, and where they stand

* **`targets_B`, not `targets_uniform`** — no target was sampled in Phase A at
  all. Phase A re-uses committed measured `rate_m3` values and draws no new
  target, so neither sampler was invoked. `targets_uniform` was not used
  anywhere. `harness/exp_icinv_fullgroup.py` was not executed in Phase A; when
  Phase B samples, `targets_B` is the sampler.
* **Stratify on r and report the strata** — not applicable to Phase A, which
  drew no target and computed no per-curve measurement; the committed rows carry
  no `r` field for this statistic. Binding for Phase B.
* **Sweep factor-base density** — Phase A ran no density sweep. The SR3 v3
  per-density-row sweep is the sweep, and it was not run (G2). No saturated row
  was run alone; no row was run at all.
* **NULL-C used only where the contract still admits it** — NULL-C was exercised
  in Phase A **only** for SR1, the reproduction gate, on the between-class
  4-class p = 4001 geometry it was originally characterised on. It was **not**
  used for any within-class contrast, in either direction, anywhere. Its
  admissibility for the between-class matched-order contrast is a Phase B cell
  and is `not_measured`.

---

## 9. Protocol deviations

1. **No `implementation.md` was written.** The role contract asks for an
   implementation note; `experiments/EXP-INSTR-36c8cf/implementation.md` is
   **outside this task's declared `write_scope`** (which covers
   `experiments/EXP-INSTR-36c8cf/runs/**`, not the experiment root). The
   implementation note is therefore this report, §4.1 and §10. Reported rather
   than resolved by writing out of scope.
2. **The manifest's `inference` block is the harness's static block.**
   `harness/runner.py` writes `requested_policy: executor-terra`,
   `resolved_model_id: none (deterministic harness execution)` for every run it
   writes, and it is read-only to this task. The agent-level inference
   provenance is in `inference-provenance.json` and in `raw-result.json` →
   `raw.inference_provenance` (see §10). Both are in the run directory.
3. **`origin/main` was fetched and compared but not merged**, because the branch
   is not behind it (§2) and because merging `main` is a Coordinator duty.
4. **Exploration preceded the freeze of the SR1 construction set**, and is
   disclosed here in full: before writing `harness/exp_instr_36c8cf/sr1.py` the
   executor ran the committed `permutation_null` in a scratch session on the
   same committed data over seeds `range(12)` (NOT the contract's declared
   seeds) at the same five deltas, under six candidate constructions, to find
   out whether any natural additive construction reproduces the published
   profile. It established that the `delta = 0` row reproduces, that the "% of
   mean" column pins the data source, and that no candidate reproduces the
   `delta = 0.002` row. The graded run then re-ran the full enumeration — seven
   constructions, the contract's twelve declared seeds — and reports every one.
   No construction was dropped after the fact and none was selected. This
   exploration touched no threshold that gates any downstream measurement: SR1's
   reference values are all read from the committed record, and the SR3 v3
   interval, the only fitted object in the contract, has no data at all.
5. **No amendment was authored**, per the handoff constraint. In particular
   `experiments/EXP-ICINV-4d33aa/amendments/v3.yaml` was not created, no
   successor run of EXP-ICINV-4d33aa was dispatched, and RQ-ICINV-475b5e is not
   treated as unpaused.

No infrastructure failure, no timeout, no OOM, no lost trial, no host-contention
event, and no budget exhaustion occurred in Phase A.

---

## 10. Provenance

### Source provenance (blocking A6 precondition)

```
$ python3 tools/check_run_source_provenance.py --experiment EXP-INSTR-36c8cf --strict
1 pinned, 0 unpinned, 0 unreadable, of 1 run manifest(s) in scope
  of the pinned, 0 also ran from a fully clean tree
exit=0            # PASSES
```

Nine executed source files are pinned by sha256 in the manifest; four are
untracked at run time (the new package `harness/exp_instr_36c8cf/__init__.py`,
`phase_a.py`, `refvalues.py`, `sr1.py`) and are pinned by content hash, which
stays valid after the Coordinator commits them. `code.commit`
`761e206c682a50555068f8aae009e011d4442215`, `code.dirty: false`.

### No transcribed reference values

Every reference value used by the run was read from its committed record **at
run time** and is bound by a `source_sha256` in `baseline-provenance.json`:

| value | record | sha256 |
|---|---|---|
| NULL-C published power profile (§5), repetitions per cell | `coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/reviews/red-team/red_team_notes.md` | `414d850b5b91…` |
| detection-bound table (§6), recorded for Phase B | same file | `414d850b5b91…` |
| [1.3, 3.6] band, floor slack, ceiling slack | `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml` | `5c1deda815e5…` |
| per-class `rate_m3` at p = 4001 | `experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-{a,b}/raw-result.json` | both, in `baseline-provenance.json`; the two agree exactly |
| the twelve declared seeds, and the coverage check | `experiments/EXP-INSTR-36c8cf/specification.yaml` | `de3369049eab…` |

**`sr3v3_reference_run_ids` is recorded as NOT NAMED BY THIS RUN**, with the
reason: naming them is part of the characterisation, which was not run. This run
performs no comparison against any reference run.

### Inference provenance (agent level)

```
requested_policy : executor-implementation
adapter resolves : executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)
actually answered: claude-opus-5
fallback_used    : true
fallback_reason  : AUTORESEARCH_POLICY is unset in this Claude Code harness, so the
                   adapter-resolved environment was not applied and the session model
                   answered instead of the policy's resolved model. Known and already
                   recorded as defect D4 of DEC-20260810-d70ece; the corrective is at
                   harness level and is not this task's to make. Recorded, never
                   silently substituted (AGENTS.md rule 11).
AUTORESEARCH_POLICY / AUTORESEARCH_BACKEND : unset / unset  (observed)
model_verified   : false (no adapter probe receipt)
```

---

## 11. Scope and honesty

`claim_tier: toy`. Instruments only, on toy-scale objects — the committed
p = 4001 class set (~12 bits). **No attack, no exponent, no speedup.
`sota_delta` zero on every axis.** `dominated_by`: parallel Pollard rho with
distinguished points at 0.886·√N group operations and O(1) memory (KN-TECH-001,
KN-TECH-006), and on CM curves its automorphism-discounted variant
(KN-TECH-018), under which any factor at or below √6 ≈ 2.449 is baseline
calibration and never an attack. **No curve-side conclusion of any kind appears
in this run or this report.** Any figure measured here applies to exactly the
geometry it was measured at and transfers to no other.

H-INSTR-444c7b stays `specified`. H-ICINV-6c7920 stays `specified`, neither
presumed true nor false. H-ENDO-001 stays `approved`. H-STR-002 stays `weakened`
with DEFER-BATCH009-001 OPEN. No completion criterion of GOAL-ENDO-001 is
claimed met; C4 is not discharged. No attestation and no closure quorum is
recorded. No evidence record is written by this task. Nothing here is durable
until the Coordinator's snapshot archive is committed, pushed, and accepted by
the post-commit verifier — and in particular the C4 block on TASK-20260810-9c2e47
and TASK-20260810-820328 is not lifted by anything in this report.

---

## 12. Artifact paths

```
harness/exp_instr_36c8cf/__init__.py
harness/exp_instr_36c8cf/refvalues.py
harness/exp_instr_36c8cf/sr1.py
harness/exp_instr_36c8cf/phase_a.py
experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-2a5cd1/
    manifest.yaml  command.txt  environment.json  stdout.log  stderr.log
    raw-result.json  nullc-reproduction.json  baseline-provenance.json
    geometry-inputs.json  detection-floors.json  false-positive-rates.json
    pseudo-crater-control.json  arbitrary-halves-control.json
    label-permutation-control.json  nuisance-direction.json
    nullc-matched-order-recharacterisation.json
    sr3v3-reference-sampling.json  sr3v3-interval-stability.json
    sr3v3-self-consistency.json  cell-coverage.json
    inference-provenance.json          [extra, not in required_artifacts]
coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report.md
```

All twenty artifacts named in `required_artifacts` are present. The executor
made no commit.
