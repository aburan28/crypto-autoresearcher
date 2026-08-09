# Execution report — EXP-ICINV-4d33aa, contract version 2

- **Handoff**: `TASK-20260809-caa93e` (coordinator → executor)
- **Goal / batch**: GOAL-ENDO-001 / BATCH-aa267f
- **Contract**: `experiments/EXP-ICINV-4d33aa/specification.yaml` (v1, approved
  2026-08-07) as amended by the approved, frozen
  `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml`
- **Branch**: `claude/ecdlp-endomorphism-analysis-4m2w3z`
- **Executed at**: 2026-08-09

**This report records what ran and what did not. It interprets nothing.** No
evidence record is written here, no hypothesis status is moved, and nothing is
characterised about `EV-ENDO-10109d`, `RQ-ICINV-475b5e` or `GOAL-ENDO-001`.
Those are Coordinator acts on a later ledger archive after independent review.

---

## 1. Emitted terminal state

```
terminal_state: INVALID
```

Emitted by the frozen decision rule from **inside** the run (SR6, no outcome
shopping), by `RUN-ICINV-99f722`, over the nine stage records, at the contract's
own `target_count_primary = 400` and first frozen seed `20260807`.

| field | value |
|---|---|
| `terminal_state` | `INVALID` |
| `aggregate_persistence` | `null` (undefined: one prime yielded a verdict) |
| `majority_counts` | `PERSISTS 1, COLLAPSES 0` (`majority_shape` `1-0`) |
| `stratification_verdict` | `NEGATIVE` (no prime positive) |
| `premise_failures` | none — the SR1 premise gate **passed** at all three primes |

Two invalidation rules fired, in the contract's own order:

1. **Arm A0 failed the baseline-reproduction control at p = 6007.**
2. **Fewer than two primes yield a persistence verdict** (p = 2003 and p = 6007
   have none).

Per prime:

| prime | persistence | detail |
|---|---|---|
| 2003 | **no verdict** | stage 3 **not run** — SR3 halted the experiment at p = 6007 (deviation D10) |
| 4001 | `F_p = 0.6923076923076923` → **PERSISTS** | 13 rows, 0 inconclusive, `S_prime_positive = False` |
| 6007 | **no verdict** | SR3 fired; no Arm B persistence statistic was computed for this prime |

`INVALID` means the measurement was not admissible. Per AGENTS.md rule 5 and the
contract's own `state_0`, it is **not** evidence in either direction: neither
`H-ICINV-6c7920` nor `EV-ENDO-10109d` is touched by it.

---

## 2. Change A1 — the re-measured p = 6007 baseline (blocking, ran first)

`experiments/EXP-ICINV-55c2d8/runs/RUN-ICINV-f09176/`, committed at `c23e41f1`
**before any version-2 Arm A0 or Arm B measurement existed**, so its numbers
could not be adjusted after Arm A0's were seen.

Command (recorded verbatim in `command.txt`):

```
python3 -m harness.run_saturation --p 6007 --targets 400 \
  --fb-sizes 4,5,6,7,8,9,10,11,12,13,15,18,22 --seed 20260807 --suffix f09176
```

Parameters as executed: `n_targets 400`, the thirteen frozen factor-base sizes
`{4,5,6,7,8,9,10,11,12,13,15,18,22}`, the committed sampler
`exp_icinv.targets_uniform` called unmodified through
`run_saturation.measure_at_density`, the `run_saturation.run` class-selection
idiom (primary class `t = 8`, `#E = 6000`, 140 curves — the class the committed
`RUN-ICINV-p6007-fixed` measured), seed `20260807`.

### Did the re-measured baseline itself fall inside [1.3, 3.6]? **No.**

**2 of its 13 rows fall below the frozen floor**, and both are at the lowest
densities:

| fb | density \|3V\|/#E | variance ratio | NULL-B verdict | in [1.3, 3.6] |
|---:|---:|---|---|---|
| 4 | 0.0159 | `1.2315292605941532` | invariant | **NO** |
| 5 | 0.0296 | `1.1125313273888915` | invariant | **NO** |
| 6 | 0.0495 | `1.4518421211510657` | over-dispersed | yes |
| 7 | 0.0763 | `1.3141804685063918` | over-dispersed | yes |
| 8 | 0.1111 | `1.5825402248780034` | over-dispersed | yes |
| 9 | 0.1526 | `1.5787641552269556` | over-dispersed | yes (operating row) |
| 10 | 0.2021 | `1.828574962171749` | over-dispersed | yes |
| 11 | 0.2589 | `1.701674989231687` | over-dispersed | yes |
| 12 | 0.3216 | `1.9200559971131461` | over-dispersed | yes |
| 13 | 0.3889 | `2.2629458456465694` | over-dispersed | yes |
| 15 | 0.5276 | `2.8764746761544338` | over-dispersed | yes |
| 18 | 0.7286 | `3.3201635060634387` | over-dispersed | yes |
| 22 | 0.9073 | `2.6387142875815535` | over-dispersed | yes |

`monotonic_decay = False`. Operating row `fb = 9`, VR `1.5787641552269556`.

Per amendment A1's `forbidden` clause this is **a finding about
`EV-ENDO-10109d`, reported as one**. No band, threshold or tolerance was moved
anywhere in this execution, and this Executor draws no conclusion from it. The
amendment's own standing caution A5 (1.3 is the outward-rounded hull edge of the
committed rows, not an independent threshold) is recorded in the run artifact
beside the finding.

The run is emitted by `harness/runner.py:write_run`, so `code.source.all_pinned`
is `true` and `all_clean` is `true`: all 6 executed source files pinned by
sha256, tree clean at commit `fb56dcf`.

---

## 3. What ran

Executed in the contract's declared stage order, **one prime per invocation**.

| # | run id | experiment | stage / prime | status | wall s | peak RSS MB |
|---:|---|---|---|---|---:|---:|
| 1 | `RUN-ICINV-f09176` | EXP-ICINV-55c2d8 | A1 baseline, p=6007 | `completed` | 32.1 | 77.6 |
| 2 | `RUN-ICINV-65bc20` | EXP-ICINV-4d33aa | stage 1, p=2003 | `completed_valid` | 3.5 | 100.5 |
| 3 | `RUN-ICINV-fda7fe` | EXP-ICINV-4d33aa | stage 1, p=4001 | `completed_valid` | 6.7 | 112.8 |
| 4 | `RUN-ICINV-d1cbec` | EXP-ICINV-4d33aa | stage 1, p=6007 | `completed_valid` | 12.2 | 125.4 |
| 5 | `RUN-ICINV-84bd66` | EXP-ICINV-4d33aa | stage 2, p=2003 | `completed_valid` | 15.2 | 179.4 |
| 6 | `RUN-ICINV-910053` | EXP-ICINV-4d33aa | stage 2, p=4001 | `completed_valid` | 22.6 | 238.3 |
| 7 | `RUN-ICINV-9f38cf` | EXP-ICINV-4d33aa | stage 2, p=6007 | `completed_valid` | 40.5 | 349.1 |
| 8 | `RUN-ICINV-40622f-failed` | EXP-ICINV-4d33aa | stage 3, p=4001 (attempt 1) | `failed_infrastructure` | 47.7 | 352.7 |
| 9 | `RUN-ICINV-40622f` | EXP-ICINV-4d33aa | stage 3, p=4001 | `completed_valid` | 47.8 | 352.7 |
| 10 | `RUN-ICINV-c670c2` | EXP-ICINV-4d33aa | stage 3, p=6007 | `completed_invalid` | 58.7 | 379.6 |
| 11 | `RUN-ICINV-99f722` | EXP-ICINV-4d33aa | decision | `completed_invalid` | 0.1 | 94.0 |

Every run id carries a random 6-hex token minted without scanning committed
state and confirmed free with `python3 tools/allocate_id.py --check` before use.
`RUN-ICINV-40622f-failed` is the driver's own derived suffix on a minted token.

### What did NOT run, and why

- **Stage 3 at p = 2003 (`RUN-ICINV-bb3f51`, id minted, never used).** SR3:
  *"If the baseline-reproduction control fails, STOP and return the defect."*
  The gate failed at p = 6007 and the experiment stopped there. This corrects
  version 1's deviation D7, where p = 2003 had already executed before the gate
  result could be read. It is recorded in the decision artifact as
  `stage3_not_run` — **a missing measurement, not a COLLAPSES, not a PERSISTS,
  and not evidence in any direction.**
- **Secondary-class runs.** Not triggered: both r strata exceed the
  `stratum_floor_for_verdict` of 20 on the primary class at every prime
  (p=2003 52/52, p=4001 72/66, p=6007 70/70).
- **The p = 10007 stretch prime.** Optional under the contract; not run.

### Budget

11 runs of a maximum of 30 (amendment change A3). Total wall 287.1 s
(0.0797 h); total CPU 296.0 s (0.0822 CPU-hours of 12); largest single-run wall
58.7 s of a 14400 s/run cap; largest peak RSS 379.6 MB of a 4 GB cap. Each
invocation ran under `ulimit -v 4194304` and `timeout 14400`. **No budget limit
was approached and none was breached.**

---

## 4. Stage 1 — exact coverage certificate (SR1). PASSED at all three primes.

`premise_gate.premise_failed = false`, **0 violations**, at p = 2003, 4001 and
6007. Certified by enumeration, not inferred:

- Arm A coverage exactly `1.0` on **every** r = 1 member and exactly `0.5` on
  **every** r = 3 member; zero within-stratum variance at all three primes.
- Arm B coverage exactly `1.0` on every curve (252, 210, 158 certificates).
- Arm C coverage exactly `0.5` on every curve it was applied to.
- **No curve anywhere with n1 > 2** (coverage tail).
- `class_census` returns `agrees: true` for every ordinary class used, at every
  prime; 0 census failures over 178 / 252 / 310 ordinary classes.
- Committed-sampler replication verified on every curve: **0 failures**.
- Independent `lift_x` cross-check of the enumerated point set agreed on every
  sampled curve.
- r × n1-parity cross-tabulation: every r = 3 curve has n1 even, every r = 1
  curve has n1 odd, at all three primes.

### Class selection (amendment change A2), recorded as (p, t, member count)

The rule used is the `harness/run_saturation.py:run` idiom, reproduced verbatim.
The contract's prose tie-break is **withdrawn and is not evaluated anywhere** in
this execution.

| prime | primary class | tied on size with | NULL-R class | odd-order substitution |
|---|---|---|---|---|
| 2003 | t = 36, #E = 1968, 104 members | t = −36 | t = 6, #E = 1998, 54 members | no |
| 4001 | t = 30, #E = 3972, 138 members | t = −30 | t = 72, #E = 3930, 72 members | no |
| 6007 | t = 8, #E = 6000, 140 members | t = −8 | t = 22, #E = 5986, 112 members | no |

The p = 4001 and p = 6007 primaries are the classes the committed
`EV-ENDO-10109d` runs measured.

---

## 5. Stage 2 — null first (SR2). Written to disk before any primary Arm B verdict.

Stage 3 refuses to start without these records and binds their digest in its own
`dependencies` block.

**Planted signal (Arm C, prediction P4).** An index-2 restriction imposed on a
declared half of the NULL-R class (the first ⌊n/2⌋ members in ascending (a, b)
order). The instrument **detected it as over-dispersed at 13 of 13 density
rows at every one of the three primes** — mixture VR range roughly 1.75 to 5.64
(p=2003), 1.97 to 3.60 (p=4001), 1.76 to 3.73 (p=6007).

**Matched null (Arm B on the NULL-R class, r constant, coverage certified 1.0).**

| prime | rows | verdict `invariant` | verdict `over-dispersed` |
|---|---:|---:|---:|
| 2003 | 13 | 4 | **9** |
| 4001 | 13 | 4 | **9** |
| 6007 | 13 | 9 | **4** |

These are the numbers the contract's prediction P5 and falsification condition
F-iii are stated against. **This Executor reports them and does not evaluate
F-iii**; that judgement belongs to the Reviewer and Coordinator.

The variance-decomposition identity is **not defined** on the NULL-R class (a
single r stratum by construction) and is reported as `null` with that reason,
never as a pass.

---

## 6. Stage 3 — the SR3 baseline gate

### p = 4001 (`RUN-ICINV-40622f`): gate **PASSED**

| sub-check | result |
|---|---|
| every row in [1.3, 3.6] | **True** (rows outside: none) |
| `monotonic_decay` is False | **True** |
| operating row within ±0.25 | **True** — fb = 8, measured `1.9182028291085371`, reference `1.9182028291085371`, delta `0.0` |

Reference `RUN-ICINV-p4001-fixed`, read at run time, `raw-result.json` sha256
`251d58c7a4eb65524df5b874684946cc75b0672bdf6d493b4b35e72c53db10b3`,
`manifest.yaml` sha256
`0e155c10636eadc12539fbaf2ccfa66fcb1a7f4e9b0a50adabbfbcafea82a0b7`.
`parameter_mismatch_with_reference_run`: false on both target count and grid.
Row-by-row (reported, not gating): **13 of 13 rows reproduced exactly, max
|delta| = 0.0**. The reference is itself inside the band at every row.

### p = 6007 (`RUN-ICINV-c670c2`): gate **FAILED**, on one sub-check only

| sub-check | result |
|---|---|
| every row in [1.3, 3.6] | **False** — fb = 4 at `1.2315292605941532`, fb = 5 at `1.1125313273888915`, both NULL-B verdict `invariant` |
| `monotonic_decay` is False | **True** (passes) |
| operating row within ±0.25 | **True** — fb = 9, measured `1.5787641552269556`, reference `1.5787641552269556`, delta `0.0` |

Reference `RUN-ICINV-f09176` (the change-A1 re-measurement), read at run time,
`raw-result.json` sha256
`7fcc505bc42b1904bd7f677d5f3bd6c7874ca4a6b70fa2c0ebac367ddc3b3bfd`,
`manifest.yaml` sha256
`9c8e5b5ea02a377c7f053579fad0dba10f352dbfc201b8b99bcb11f719f00782`.
`parameter_mismatch_with_reference_run`: **false on both target count and grid**
— the comparison A1 was filed to make possible.

**The reproduction itself is perfect: 13 of 13 rows reproduced exactly,
max |delta| = 0.0, at every one of the thirteen frozen densities.** The gate
fails because the frozen acceptance band does not contain the two lowest-density
rows — and `reference_self_check.reference_itself_inside_band_at_every_row` is
**false at exactly those same two rows (fb 4 and 5)**.

Also reported and **not** gating (deviation D8): against the contract's prose
constant 1.591 the operating row would also pass, delta
`-0.012235844773044402`.

Under SR3 the driver halted: `cell-aggregates.json` was **not** written, no
persistence or stratification statistic exists for p = 6007, and the run is
`completed_invalid`. Every per-curve hit count for every arm is retained in
`per-curve-measurements.json` — nothing was discarded. All five tail checks were
written in full, which version 1 skipped on a gate failure.

### p = 4001 sweep, seed 20260807, T = 400 (the only prime with a persistence verdict)

| fb | density | VR A0 | VR A1 | VR B | Arm B verdict | row persists | S1 | S2 | S3 | VR(r=1) | VR(r=3) | VR_within |
|---:|---:|---:|---:|---:|---|---|---|---|---|---:|---:|---:|
| 4 | 0.0239 | 2.103 | 2.103 | 1.124 | invariant | no | F | F | F | 1.085 | 1.155 | 1.120 |
| 5 | 0.0442 | 1.907 | 1.907 | 1.156 | invariant | no | F | F | F | 1.347 | 0.956 | 1.156 |
| 6 | 0.0735 | 2.047 | 2.047 | 1.338 | over-dispersed | **yes** | F | F | F | 1.285 | 1.417 | 1.348 |
| 7 | 0.1125 | 2.394 | 2.394 | 1.434 | over-dispersed | **yes** | F | F | F | 1.591 | 1.284 | 1.444 |
| 8 | 0.1628 | 1.918 | 1.918 | 1.225 | invariant | no | F | F | F | 1.124 | 1.309 | 1.213 |
| 9 | 0.2227 | 2.005 | 2.005 | 1.100 | invariant | no | F | F | F | 1.072 | 1.096 | 1.084 |
| 10 | 0.2901 | 2.358 | 2.358 | 1.403 | over-dispersed | **yes** | F | F | F | 1.306 | 1.506 | 1.402 |
| 11 | 0.3657 | 2.248 | 2.248 | 1.760 | over-dispersed | **yes** | F | F | F | 1.648 | 1.910 | 1.773 |
| 12 | 0.4441 | 2.477 | 2.477 | 1.746 | over-dispersed | **yes** | F | F | F | 1.681 | 1.819 | 1.747 |
| 13 | 0.5282 | 2.298 | 2.298 | 1.930 | over-dispersed | **yes** | F | F | F | 1.928 | 1.961 | 1.944 |
| 15 | 0.6813 | 3.209 | 3.209 | 2.407 | over-dispersed | **yes** | F | F | F | 3.066 | 1.632 | 2.374 |
| 18 | 0.8589 | 3.588 | 3.588 | 3.077 | over-dispersed | **yes** | F | F | F | 3.308 | 2.820 | 3.070 |
| 22 | 0.9725 | 3.332 | 3.332 | 3.241 | over-dispersed | **yes** | F | F | F | 4.155 | 2.329 | 3.248 |

`F_p = 9/13 = 0.6923076923076923` → **PERSISTS**; 0 inconclusive rows; 13 of 13
rows stratum-`verdict_eligible`; `S_row_fraction = 0.0` → `S_prime_positive =
False`.

**Arm deltas at p = 4001.** A0 → A1 is **exactly 0.000e+00 at every one of the
thirteen rows** (at T = 400, seed 20260807, on this class the committed
sampler returned 400 of 400 requested targets on every curve, so the
requested-count denominator equals the actual-count denominator and the
denominator defect contributes nothing). A1 → B ranges from −0.0906 (fb = 22) to
−0.9790 (fb = 4). Whatever separates the arms here is the coverage change, not
the denominator; the Coordinator's mechanism accounting is recorded per row in
`cell-aggregates.json`.

---

## 7. Controls and tail checks

- **Variance-decomposition identity**: holds at **every** cell where it is
  defined. p = 4001: 351/351 cells, max relative error `5.39e-15`; p = 6007:
  351/351, max `4.91e-15` — both far inside the frozen 1e-9 tolerance.
- **Sum-set sharing** (an invalidation rule if violated): exactly one
  enumeration per (curve, fb_size) in every sweep — 1794/1794 (p=4001 primary),
  1820/1820 (p=6007 primary), 702/702, 936/936, 1456/1456 (NULL-R). The
  committed `exp_icinv.decomposition_rate_m3/_m2` were additionally called on
  the first 3 curves of each class and reproduced the shared set's hit counts
  exactly.
- **Dropped or short cells**: none, anywhere.
- **Extreme-curve check**: reported at every (arm, prime, density) with (a, b),
  r, (n1, n2), coverage fraction and |3V|.
- **Degenerate-rate check**: p = 4001 primary 0 rows; p = 6007 primary 4 rows;
  NULL-R 104 (p=2003), 11 (p=4001), 10 (p=6007). **Every degenerate rate sits at
  an extreme density** — rate 1.0 only where |3V|/#E ≥ 0.98, rate 0.0 only where
  |3V|/#E ≤ 0.16 and only on the index-2-restricted Arm C. None occurs against a
  non-extreme density.
- **Coverage tail**: min/max per arm per prime reported; no curve with n1 > 2
  anywhere.
- **Chi-square tail**: exact statistic and both Wilson–Hilferty bounds reported
  for all 351 cells per sweep; 55 (p=4001) and 78 (p=6007) flagged
  `near_band_edge` (within 10% of a bound) so no near-edge verdict reads as
  decisive.
- **T-scaling tail** at the operating row, p = 4001: Arm A0/A1 VR 1.2837 (T=100)
  → 1.9182 (T=400) → 6.0721 (T=1600), against a linear prediction of 4.4561,
  departure **+1.6161**; Arm B 0.9548 → 1.2249 → 2.2145 against 2.3055,
  departure −0.0911. At p = 6007, Arm A0/A1 1.3129 → 1.5788 → 3.3251 against
  2.6420, departure **+0.6831**; Arm B 0.9745 → 0.8723 → 1.5215 against 0.4636,
  departure +1.0578. Reported as the contract's tail check requires; the
  prediction-P7 / F-v judgement is not this Executor's.
- **NULL-C (`exp_icinv.permutation_null`)**: mechanically audited every run,
  **0 call sites** in `exp_icinv_fullgroup.py` and `run_fullgroup.py`, and not
  imported into either module namespace.
- **`harness/exp_icinv.py` byte-identical to HEAD**: verified `true` at the
  start of every single run; the file was not edited by this task
  (`git diff fb56dcf..HEAD -- harness/exp_icinv.py` is empty).

---

## 8. Change A6 — source-provenance verification (blocking)

Both forms were run and both results are reported (deviation D9).

**Form 1 — the handoff's exact command:**

```
$ python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-4d33aa --strict
10 pinned, 19 unpinned, 0 unreadable, of 29 run manifest(s) in scope
  of the pinned, 9 also ran from a fully clean tree
  ... 19 unpinned runs listed, all of them RUN-ICINV-fg-* ...
FAIL (--strict): a run that cannot bind its own code to a hash is not a reproduction package (GOAL-ENDO-001 N6)
exit=1
```

**This command exits 1, and it cannot do otherwise.** All 19 unpinned manifests
are the **version-1 run directories**, every one written before the N6 fix
landed and every one immutable under AGENTS.md rule 4. **Zero version-2 runs are
unpinned.** The tool's own documentation prescribes `--since-commit` for exactly
this situation.

**Form 2 — scoped to runs added after the version-1 base commit:**

```
$ python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-4d33aa \
    --since-commit fb56dcfcf49073ca0282feb555e17c52a6226d4b --strict
10 pinned, 0 unpinned, 0 unreadable, of 10 run manifest(s) in scope
  of the pinned, 9 also ran from a fully clean tree
exit=0
```

**Form 3 — the change-A1 baseline run under EXP-ICINV-55c2d8:**

```
$ python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-55c2d8 \
    --since-commit fb56dcfcf49073ca0282feb555e17c52a6226d4b --strict
1 pinned, 0 unpinned, 0 unreadable, of 1 run manifest(s) in scope
  of the pinned, 1 also ran from a fully clean tree
exit=0
```

**Every one of the 11 runs written by this task reports
`code.source.all_pinned: true`.** Ten of eleven also report `all_clean: true`.
The exception is `RUN-ICINV-65bc20` (stage 1, p = 2003), which ran before the
version-2 harness was committed and so records `all_clean: false` with
`modified: [harness/exp_icinv_fullgroup.py, harness/run_fullgroup.py]`. All
seven of its recorded sha256 values were checked against the blobs now at HEAD
and **all seven match** — which is the property `source_provenance()` exists to
give: a hash recorded while a file is uncommitted stays valid once it is
committed, and provably fails if the file is later edited.

`python3 tools/check_run_immutability.py` → `OK: no committed run artifacts were
modified or deleted`.

---

## 9. Change A4 — no reference value is transcribed

Every reference number in this execution is read from its record at run time and
bound by sha256. `baseline-provenance.json` is emitted by **every** version-2 run
and names, per prime: the run id read, its **declared parameters as read**, the
sha256 of `raw-result.json` **and** of `manifest.yaml`, the full row table, and
the operating row.

| prime | reference run | T as read | fb grid as read | matches frozen grid |
|---|---|---:|---|---|
| 2003 | none — the contract states no baseline control here | — | — | — |
| 4001 | `RUN-ICINV-p4001-fixed` | 400 | the thirteen frozen sizes | **yes** |
| 6007 | `RUN-ICINV-f09176` (change A1) | 400 | the thirteen frozen sizes | **yes** |

The superseded `RUN-ICINV-p6007-fixed` is read and hashed
(`0da2ef85e19fce67b3d2dbd342c840ca042be7dc79e0231127c16de0feb3b0a5`) and
recorded as `not_used_because` its declared parameters — n_targets **500** over
the eleven sizes `{5,6,7,8,9,10,11,12,14,17,21}`, *read from the record, not
asserted* — are not the frozen grid. **No number from it enters any comparison.**

Mechanical check: the only float literal with four or more decimals in either
harness module is the contract's own frozen `operating_density_target =
0.16666666`. The version-1 defect `CORR-20260807-a24675` (24 hard-coded
literals, 22 with invented digits) is not reintroduced.

---

## 10. Protocol deviations

All ten are recorded in `protocol_deviations` in **every** version-2 run
manifest. D1 and D2 are discharged by the approved amendment; D3–D6 are
unchanged from version 1; D8, D9 and D10 are new and were **all fixed in code
before any version-2 measurement was taken**.

| id | status | summary |
|---|---|---|
| D1 | **resolved by amendment A2** | primary-class rule stated once by reference to `run_saturation.run`; the prose tie-break is withdrawn and never evaluated. |
| D2 | **resolved by amendment A1** | the p = 6007 SR3 reference is the re-measurement at the frozen grid. |
| D3 | unchanged | SR3's "do not run Arm B" vs the cost-sharing invalidation rule cannot both be honoured literally. One shared sum-set pass scores every arm; the gate is evaluated and written before any Arm B statistic is read, aggregated into a verdict, or reported as an arm contrast. On failure the Arm B aggregates are dropped and raw per-curve counts are retained. |
| D4 | unchanged | The handoff asks the Executor to merge `origin/main`; `agents/executor.md` forbids the Executor from merging, pushing or opening PRs. **`origin/main` was fetched and compared; no merge was performed.** See §11. |
| D5 | unchanged | Per-stratum `own_null` (per-cell verdict and band) and `ratio_pooled_null` (the only null under which the identity holds) are both computed, labelled and reported. S3 uses the own-null ratios. |
| D6 | unchanged | The rule names no seed or T for F_p. The contract's own `target_count_primary = 400` and first frozen seed `20260807` are used, fixed in code; all nine seed × T combinations are reported regardless. |
| **D8** | **new** | The ±0.25 operating-row reference is the **record-read** value from the bound baseline run (A1 + A4), not the contract's prose constants. Both are computed and reported at every prime; the contract-stated comparison is `contract_stated_reference_reported_not_gating` and never gates. Fixed before any measurement. At p = 6007 both would have passed. |
| **D9** | **new** | The handoff's unscoped `--strict` provenance command cannot pass while 19 immutable version-1 runs are in its scope. Both the exact command and the tool's documented `--since-commit` scoping were run; both results are in §8 verbatim. |
| **D10** | **new** | Stage 3 runs one prime per invocation in the contract's order and honours SR3's stop. Stage 3 at p = 2003 was therefore **not run**. This corrects version 1's D7. |

### Defects and infrastructure events, recorded not hidden

- **`RUN-ICINV-40622f-failed`, `failed_infrastructure`.** The first stage-3
  invocation at p = 4001 completed its sweep and its baseline gate, then raised
  `KeyError: 'operating_row_target'` inside `_print_sweep`, a **stdout
  formatting helper** that still used the version-1 key name for the
  operating-row reference. Classification: **`implementation_error` in this
  Executor's driver, in reporting code only**. Per AGENTS.md rule 5 it is not
  negative mathematical evidence and not a verdict. No measurement survived the
  generic handler; nothing is quoted from that run. The defective attempt keeps
  its own immutable run id and stays in the ledger; the corrected attempt ran
  under the distinct, never-previously-written id `RUN-ICINV-40622f`. Nothing was
  overwritten and no run was re-keyed.
- **First `--stage decide` invocation: `PreconditionRefusal`, exit 4, no run
  record written.** It iterated prime-major, so at p = 2003 no stage-3 record had
  yet been loaded and the SR3 halt at p = 6007 was not visible to explain the
  absence. Fixed by reading every stage-3 record before asking why one is
  missing; the explanation is still read from the run records and never asserted.
  Because the refusal path deliberately writes no run record, no immutable id was
  burned and nothing required superseding.

### Unexpected observations, recorded

- The re-measured p = 6007 baseline is **outside the frozen [1.3, 3.6] band at
  its two lowest-density rows** (§2). This was not predicted by the amendment,
  which raised it only as a possibility, and it is the direct cause of the SR3
  failure at that prime.
- At p = 4001 the **A0 → A1 delta is exactly zero at all thirteen rows**: at
  T = 400 the committed sampler lost no draws on any curve of that class, so the
  denominator defect contributes nothing there.
- The **NULL-R matched null is over-dispersed at 9 of 13 rows at p = 2003 and
  p = 4001** under Arm B, where r is constant and coverage is certified complete.
- The **T-scaling tail departs upward from the linear prediction** on Arm A at
  both primes (+1.6161 at p = 4001, +0.6831 at p = 6007).

These are observations. Their bearing on predictions P5, P7 and falsification
conditions F-iii and F-v is for the Reviewer and Coordinator.

---

## 11. Branch and base-commit state

- `git fetch origin main` performed at the start of the session.
- Base checked: `origin/main` at `3ff7a0fffe1f0a08cf2156e9324d281c33cbccba`;
  merge-base with this branch `d2806f6f12d77d5db01c1ed36bc690c5854d33f9`;
  divergence at that point 3 commits on main / 3 on the branch.
- **Merge outcome: no merge performed by this Executor** (deviation D4). The
  three main-only commits touch only
  `coordination/goals/GOAL-ECDLP-001/...`, `ledger/decisions/DEC-20260808-b671fd.yaml`,
  `ledger/evidence/EV-ECDLP-cbc6d2.yaml` and
  `ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-f7de45.yaml` — a different
  goal's ledger records. Nothing this experiment reads or writes is affected.
  Bringing `main` into the branch, and pushing, are Coordinator acts.
- Every run manifest carries its own `git_context` block with HEAD, branch,
  `origin/main`, merge-base and behind/ahead counts as of that run.
- Work is committed on `claude/ecdlp-endomorphism-analysis-4m2w3z`.
  **Not pushed. No PR opened or updated.**

### Reproduction checks (completion gate: "the result reproduces from the recorded command and revision")

Both were run **after** the last commit, write nothing, and consume no run
budget.

1. **The frozen decision rule re-executed read-only** in a fresh process over the
   nine committed stage records, and its output compared against the emitted
   `decision-rule-evaluation.json` of `RUN-ICINV-99f722` (excluding the two keys
   the driver adds outside the rule, `null_first_evidence` and
   `source_run_resolution`): **byte-equal, 16448 == 16448 characters of
   canonical JSON**, `terminal_state INVALID` both times.
2. **The change-A1 baseline re-run from its recorded command** with `--no-write`
   at the same revision: all thirteen variance ratios reproduce the committed
   `RUN-ICINV-f09176` values, `monotonic decay: False`, operating row fb = 9 at
   1.579. Exact match at the four decimals the driver prints.

### Repository checks run after the last commit

| check | result |
|---|---|
| `python3 tools/validate_ledger.py` | `OK: validated 5312 records, no new violations` (exit 0) |
| `python3 tools/check_run_immutability.py` | `OK: no committed run artifacts were modified or deleted` |
| `python3 tools/check_merge_hygiene.py --base origin/main` | `PASS: no conflict markers, no unparseable records, no identifier collisions`, scoped to the 135 files this branch adds or modifies (exit 0) |

**Recorded rather than passed over:** the *unscoped* `check_merge_hygiene.py`
sweep reports 6 unparseable records —
`experiments/EXP-P13-NC2b/specification.yaml`,
`experiments/EXP-P13-NC2d/specification.yaml`,
`ledger/decisions/DEC-20260805-364e9e.yaml`,
`ledger/decisions/DEC-20260805-48b52e.yaml`,
`ledger/decisions/DEC-20260805-661790.yaml`,
`ledger/evidence/EV-HAWK-af783e.yaml`. **All six already exist on
`origin/main`, are untouched by this branch, and are byte-identical to their
`origin/main` versions** (verified per file). They belong to other campaigns and
are the scheduled `main-health.yml` sweep's business, not this task's; they are
noted here so the next reader does not attribute them to this work.

---

## 12. Artifact paths

Change A1 baseline (EXP-ICINV-55c2d8):

- `experiments/EXP-ICINV-55c2d8/runs/RUN-ICINV-f09176/`

Version-2 runs (EXP-ICINV-4d33aa), each with `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`,
`coverage-certificates.json`, `per-curve-measurements.json`,
`decision-rule-evaluation.json`, `baseline-reproduction.json`,
`baseline-provenance.json`, `tail-checks.json` (and `cell-aggregates.json` on
sweeps that were not halted by SR3):

- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-65bc20/` — stage 1, p = 2003
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-fda7fe/` — stage 1, p = 4001
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-d1cbec/` — stage 1, p = 6007
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-84bd66/` — stage 2, p = 2003
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-910053/` — stage 2, p = 4001
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-9f38cf/` — stage 2, p = 6007
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-40622f-failed/` — preserved failure
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-40622f/` — stage 3, p = 4001
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-c670c2/` — stage 3, p = 6007
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-99f722/` — decision run

Instrument:

- `harness/exp_icinv_fullgroup.py` (extended; additive)
- `harness/run_fullgroup.py` (extended; additive)
- `harness/exp_icinv.py` — **not modified**, verified byte-identical to HEAD at
  the start of every run

This report:

- `coordination/goals/GOAL-ENDO-001/batches/BATCH-aa267f/execution/EXP-ICINV-4d33aa-v2/execution_report.md`

---

## 13. Scope and honesty statement

Toy scale throughout, p ≤ 6007 (the 10007 stretch was not run).
`claim_tier: toy`, `sota_delta` zero. Complete isogeny-class enumeration is
O(p²) and every sum set is enumerated point by point: this is a measurement
instrument, not an algorithm at any scale. **No run of this contract can support
or reject an ECDLP cost claim, and none is offered.** Any evidence record
arising from this execution is pre-capped at `preliminary` by the amendment's own
`confirmatory_status: exploratory_only`, unconditionally and regardless of
outcome. Lawful defensive cryptanalysis on public toy constructions only; no
live key, wallet or deployed system was touched.
