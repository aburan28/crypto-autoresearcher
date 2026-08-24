# PS-R3 joint-moment measurement at T = 1e7 under the admitted v3 rule

**Task** `TASK-20260806-cde749` (executor) · **Batch** `BATCH-0a65c0` (final batch
under the declared cap) · **Goal** `GOAL-HQC-001` · **Experiment**
`EXP-HQC-982268` · **Hypothesis** `H-HQC-18d1b4` (remains `proposed`)
**Produced** 2026-08-06.

---

## 0. Claim tier, authority, and boundary

**TOY, hard ceiling.** Nothing in this report is a statement about HQC, about
assumption A17 or A5, about any decoding-failure rate, or about any
standardized HQC parameter set. PS-R3 is **one reduced parameter set**,
order-matched to **HQC-3's shape** — not HQC-1's — with `n = 7187`, `n_e = 56`,
`n_2 = 128`, `dup = 1`. Every number below is scoped to that set, at
`T = 10,000,000`, with this solver and this budget.

**I am the Executor. I record observations.** I draw no conclusion, I change no
research status, and I do not interpret what fired. The interpretation is the
Coordinator's at the ledger archive, and the Validator's and Red Team's before
it. Where a reading is tempting, I have written down what the observation does
**not** establish instead.

---

## 1. The gate, verified before any compute

My card orders me to abort if either review refused. **Neither refused.** I read
both verdicts in full before running anything, and quote them here as ordered.

**Validator `TASK-20260806-f53255`** (`validation_report.yaml`, line 18):

> `OVERALL_VERDICT: ADMIT`

with, at `what_this_admission_does_and_does_not_authorize.does`:

> "It authorizes TASK-20260806-cde749 to run the PS-R3 joint-moment measurement
> at T = 1e7 under the v3 frozen table, using the constants byte-identical to
> those in amendment_v3.yaml, without re-tuning them."

**Red team `TASK-20260806-250b29`** (`red_team_report.md`, §9 and the headline
verdict at line 18):

> "**ADMIT**, subject to the four binding corrections in §9 (plus one recorded,
> non-binding)."

and, on the specific question of whether the defect it found touches this run
(§2.3):

> "**At PS-R3, dup = 1, so the specified expression and the correct one coincide
> and the funded measurement is unaffected.**"

Both ADMIT. The gate is open and I proceeded.

### Coordinator rulings observed

| ruling | what it binds | how this run complies |
|---|---|---|
| **RULE-1** | CTRL-IDXMAP and CTRL-POSHOM clause (b) are forward obligations, not blocking gates | Both reported **NOT RUN** (§6). No artifact synthesized; cited as passing by nobody |
| **RULE-2** | CTRL-IDXMAP's `L = n_2*dup` defect recorded, not repaired | Recorded in `controls_NOT_RUN`; not repaired, not exercised |
| **RULE-3** | k = 2 is an authorized reported cell | k = 2 reported under its frozen interval, in Table 1 |
| **RULE-4** | do not invoke `recalibrate.py` | Never imported, never executed. Constants loaded with `yaml.safe_load` in `"r"` mode |
| **RULE-5** | the battery is ~1.0% familywise, not 0.27% | Measured here as 1.026%; §5 states it and no reading in this report contradicts it |

Red team binding correction 2 also binds me directly — *"the (T) sampler is not
to be modified"*. `stage_a.py` was imported unmodified
(`sha256 06a0a618432c00fe…`) and its `_t_shard` was called as-is.

---

## 2. Provenance and integrity of the frozen input

All four artifacts frozen by `archives/TASK-20260806-ae094e/snapshot-receipt.json`
verify byte-for-byte after this run:

| artifact | sha256 | matches receipt |
|---|---|:--:|
| `amendment_v3.yaml` | `16e8b73a7790e271…` | yes |
| `fix_report.md` | `f53777130bbd2a9d…` | yes |
| `recalibrate.py` | `8a411b4acbfd441c…` | yes |
| `transcribed_size.json` | `379cd28aeec1f967…` | yes |

The amendment loaded is byte-identical to the artifact both reviewers verified.

**A defect in my own integrity check, reported rather than patched away.** The
in-run check looked for `path_sha256` at the *top level* of the receipt, but it
is nested under `archive`. The lookup returned `None`, so the in-run field reads
`match: false` with a `null` declared hash — and the abort branch was guarded by
`declared is not None`, so **the check was fail-open and could not have stopped
the run**. That is a defect in my harness, not in the artifact. The verification
was redone correctly afterwards (table above, and
`frozen_input_integrity_CORRECTED` in the results JSON); the in-run field is left
as it was recorded.

The **decision rule was used unmodified**: no re-tuning, no re-derivation, no
substitution. All 119 interval constants of this configuration parse as `float`
(the VF-1 guard, re-run here rather than taken on trust); zero parsed as `str`.

---

## 3. Blocking gates — all pass

### 3.1 INV-NULL run-time reproduction (MANDATORY AND BLOCKING)

The amendment requires that, *before any (T) datum is scored*, the run re-derive
the frozen constants from the recorded seed and assert **bit-identity** — an
equality test, not a tolerance test.

- Seed derivation reproduces the recorded `calibration_seed` exactly:
  `13271017274709966482`.
- 2,000,000 replicates, PCG64, fixed chunks of 100,000, in order.
- **17 of 17 cells bit-identical.** Verdict **PASS**.

This is a third independent reproduction of the v3 table (producer, validator,
and now this run), and mine was written from the estimator definition with the
matmul orientation matched to the generating procedure — bit-identity is
sensitive to summation order, and a transposed view would have broken it.

### 3.2 CTRL-ORACLE (ranked PRIMARY, mandatory, blocking)

Estimator arithmetic against the exact enumeration in the BATCH-003 oracle
package:

| quantity | required | measured |
|---|---:|---:|
| cells | ≥ 40 | **40** (zero slack) |
| max abs difference | < 1e-12 | **8.88e-16** |
| cells with abs(log2 A_k) > 1 bit | ≥ 5 | **12** |
| cells negative | ≥ 5 | **18** |

Verdict **PASS**.

*Reconciliation worth recording.* My naive sign test returned **21** negative
cells against the validator's recorded **18**. The difference is fully
explained: 11 cells belong to the independent-by-construction oracle
configurations (A1, A2, B3) whose exact value is 0, and three of those land at
−1e−16 in floating point. Excluding that exact-zero class gives **18**, which
reproduces the validator exactly. The >1-bit count (12) agreed already. Both
floors are met either way.

This gate establishes **estimator arithmetic only**. It says nothing about the
fixed-weight sampler, the ring product, the truncation, the folded-WHT decoder,
or the calibrated interval.

### 3.3 Hard invariants on the (T) arm

| detector | observable | result | verdict |
|---|---|---|:--|
| **D1** | `gamma_hat` | 0.78919 (alarm band is [0.95, 1.05]) | PASS — no drift alarm |
| **D2** | exact weights of x, y, r₁, r₂, e on **every** trial | 0 violations in 10,000,000 | PASS |
| **D3** | `w(ẽ) ≤ 2ωω_r + ω_e = 4641` | max observed 2808, 0 violations | PASS |
| **D4** | upper-tail quantiles vs BASE-TABLE10 | — | NOT APPLICABLE (PS-A table; PS-A not run) |
| **D5** | CTRL-REPLAY bit-identity via the independent dense-GF(2) path | 400 trials replayed, **0 mismatches** | PASS |

`gamma_hat = 0.789` sits where Stage-A measured it (0.7903) and well outside the
(M)-arm alarm band, which is the point of D1: a (T) arm that had silently become
an (M) arm would read ≈ 1.

**D5 shortfall, stated plainly.** The contract's CTRL-REPLAY target is 1e4
sampled trials per set. This run replayed **400** (50 per shard), matching
Stage-A's practice rather than the contract's number. The shortfall is reported,
not hidden.

---

## 4. The measurement

`T` achieved = `T` planned = **10,000,000**. No shard truncated, so the frozen
interval binds exactly as written; no `achieved_T_deviation` re-derivation was
needed or performed.

Measured `q̂ = 0.3198315732` against the frozen `q̂ = 0.3199462862` — a relative
shift of **−3.59e−4**, which is **0.44 ×** the 3 SE reference (8.17e−4) the
amendment certified the interval robust across. The measurement therefore sits
inside the q-robustness envelope that was frozen for it.

### Table 1 — log2 Â_k against the frozen admitted interval

| k | log2 Â_k | jackknife SE | frozen interval [c_lo, c_hi] | fired | (v − null_mean)/null_sd | T_stab(k) at measured q | margin | reach |
|---:|---:|---:|:--|:--:|---:|---:|---:|:--|
| 2 | −6.030632e−03 | 2.247e−05 | [−7.408048e−05, +7.398495e−05] | **FIRED** | −244.1 | 526 | 19018.4x | REACHED |
| 3 | −1.815742e−02 | 6.819e−05 | [−2.234508e−04, +2.233122e−04] | **FIRED** | −243.4 | 526 | 19018.4x | REACHED |
| 4 | −3.644591e−02 | 1.393e−04 | [−4.556072e−04, +4.552400e−04] | **FIRED** | −239.6 | 941 | 10629.4x | REACHED |
| 5 | −6.096011e−02 | 2.395e−04 | [−7.844606e−04, +7.823802e−04] | **FIRED** | −232.9 | 1,792 | 5580.2x | REACHED |
| 6 | −9.176163e−02 | 3.748e−04 | [−1.231713e−03, +1.228725e−03] | **FIRED** | −223.4 | 1,792 | 5580.2x | REACHED |
| 7 | −1.289092e−01 | 5.548e−04 | [−1.830465e−03, +1.825652e−03] | **FIRED** | −211.2 | 3,637 | 2749.3x | REACHED |
| 8 | −1.724587e−01 | 7.937e−04 | [−2.623452e−03, +2.621935e−03] | **FIRED** | −196.7 | 7,872 | 1270.3x | REACHED |
| 9 | −2.224632e−01 | 1.113e−03 | [−3.693998e−03, +3.698896e−03] | **FIRED** | −180.2 | 7,872 | 1270.3x | REACHED |
| 10 | −2.789740e−01 | 1.543e−03 | [−5.143000e−03, +5.169797e−03] | **FIRED** | −162.2 | 18,182 | 550.0x | REACHED |
| 11 | −3.420433e−01 | 2.131e−03 | [−7.148325e−03, +7.200597e−03] | **FIRED** | −143.1 | 18,182 | 550.0x | REACHED |
| 12 | −4.117313e−01 | 2.941e−03 | [−9.917687e−03, +1.005098e−02] | **FIRED** | −123.7 | 44,853 | 223.0x | REACHED |
| 13 | −4.881222e−01 | 4.065e−03 | [−1.385779e−02, +1.420509e−02] | **FIRED** | −104.6 | 118,270 | 84.6x | REACHED |
| 14 | −5.713551e−01 | 5.631e−03 | [−1.945282e−02, +2.043063e−02] | **FIRED** | −86.4 | 118,270 | 84.6x | REACHED |
| 15 | −6.616778e−01 | 7.811e−03 | [−2.748797e−02, +3.029903e−02] | **FIRED** | −69.8 | 333,667 | 30.0x | REACHED |
| 16 | −7.595306e−01 | 1.083e−02 | [−3.903554e−02, +4.652538e−02] | **FIRED** | −55.2 | 1,008,226 | 9.9x | REACHED |
| **17 (k = m, PRE-SPECIFIED)** | **−8.656666e−01** | 1.498e−02 | [−5.554716e−02, +7.510967e−02] | **FIRED** | **−42.7** | 1,008,226 | 9.9x | REACHED |
| 18 | −9.813074e−01 | 2.062e−02 | [−7.909013e−02, +1.260136e−01] | **FIRED** | −32.4 | 3,266,733 | 3.1x | REACHED |

**Every one of the 17 reported cells lies BELOW its frozen lower bound.** The
sign is negative at every order and the magnitude grows monotonically with k.
All 17 cells are REACHED at the measured q̂; the reachability arithmetic
reproduces the record exactly, with the 10.0× margin at k = m = 17 confirmed.

### Table 2 — per-cell calibration evidence

Every cell carries all three checks the amendment requires, and every one passes.

| k | bit-identical | out-of-sample size | 95% CI | in [0.002, 0.004] | undefined null frac |
|---:|:--:|---:|:--|:--:|---:|
| 2 | yes | 0.002730 | [0.002628, 0.002832] | yes | 0.0000 |
| 3 | yes | 0.002780 | [0.002677, 0.002883] | yes | 0.0000 |
| 4 | yes | 0.002780 | [0.002677, 0.002883] | yes | 0.0000 |
| 5 | yes | 0.002784 | [0.002681, 0.002887] | yes | 0.0000 |
| 6 | yes | 0.002782 | [0.002679, 0.002885] | yes | 0.0000 |
| 7 | yes | 0.002761 | [0.002658, 0.002864] | yes | 0.0000 |
| 8 | yes | 0.002766 | [0.002663, 0.002869] | yes | 0.0000 |
| 9 | yes | 0.002710 | [0.002608, 0.002812] | yes | 0.0000 |
| 10 | yes | 0.002654 | [0.002553, 0.002755] | yes | 0.0000 |
| 11 | yes | 0.002615 | [0.002515, 0.002715] | yes | 0.0000 |
| 12 | yes | 0.002648 | [0.002547, 0.002749] | yes | 0.0000 |
| 13 | yes | 0.002593 | [0.002493, 0.002693] | yes | 0.0000 |
| 14 | yes | 0.002567 | [0.002468, 0.002666] | yes | 0.0000 |
| 15 | yes | 0.002595 | [0.002495, 0.002695] | yes | 0.0000 |
| 16 | yes | 0.002668 | [0.002567, 0.002769] | yes | 0.0000 |
| 17 | yes | 0.002703 | [0.002601, 0.002805] | yes | 0.0000 |
| 18 | yes | 0.002782 | [0.002679, 0.002885] | yes | 0.0000 |

Zero cells outside the [0.002, 0.004] acceptance band, so the
`calibration_failed_clause` is triggered at no cell and no (T) result is
withheld under it. Zero undefined null replicates anywhere.

### Shape of the measured curve — a description, not a mechanism

log2 Â_k tracks `C(k,2) · log2 Â_2` closely at low order and drifts above it as
k rises:

| k | 2 | 3 | 4 | 5 | 6 | 7 | 17 | 18 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| observed / `C(k,2)·log2 Â_2` | 1.0000 | 1.0036 | 1.0072 | 1.0108 | 1.0144 | 1.0179 | 1.0555 | 1.0635 |

**This is a description of the curve and nothing more.** No mechanism is
claimed, no model is fitted, and this is not a statement about A17 or HQC. It is
recorded because it is a cheap, checkable regularity that a reviewer can
falsify.

---

## 5. RULE-5 — how this battery may and may not be read

This is binding on every downstream record and I state it before any control
discussion.

- **Measured familywise size of the 17-cell battery: 1.026 %** [1.0064, 1.0460],
  **3.80 ×** the 0.26998 % per-cell nominal, measured under the exact binomial
  null on 1,000,000 validation replicates with my own seed. This reproduces the
  validator's 1.017 % and the red team's 1.001 % at the same configuration.
- **A set of per-k firings from this 17-cell report is a familywise ~1.0 %
  observation, not a 0.27 % one.** A single fired cell out of 17 happens about
  1 run in 100 under the exact null, not 1 in 370. **No record may report a
  battery firing as if each cell were a 0.27 % test.**
- **Only the pre-specified cell k = m = 17 retains the 0.27 % size**, measured
  here at **0.002703**. That cell is flagged distinctly in Table 1. It fired at
  −42.7 null SD.
- This is a **size** caveat, not a power caveat.

I note without interpreting it that the multiplicity correction is what
distinguishes *one* cell firing from *seventeen*; how much weight that carries is
a reading question, and readings are not mine to make.

---

## 6. Every declared control, with its outcome

| control | rank | status | outcome |
|---|:--:|:--|:--|
| **NULL-M** | 1 | RUN, **severely under-powered** | 81,980 trials only. γ̂ = 1.00092, z = +0.19 vs 1 → **TC-5 passes**. See caveat below |
| **CTRL-ORACLE** | 2 | RUN | **PASS**, 40 cells, max diff 8.88e−16 (§3.2) |
| **CTRL-IDXMAP** | 3 | **NOT RUN** | Coordinator RULE-1 — forward obligation, not a gate. §6.1 |
| **CTRL-POSHOM (a)** | 4 | RUN | **DOES NOT FIRE**: X = 50.35, df = 55, X/df = 0.915, p = 0.653 |
| **CTRL-POSHOM (b)** | 4 | **NOT RUN** | Coordinator RULE-1. §6.1 |
| **NULL-P** | 5 | RUN | **0 of 17 cells fired** at T = 1e7 |
| **CTRL-DEC** | 6 | RUN (reduced scale) | WHT vs brute-force agree on **3000/3000** blocks across 5 densities |
| **CTRL-REPLAY** | 6 | RUN (reduced scale) | 400 replays, 0 mismatches (D5) |
| **CTRL-WBP** | 7 | **NOT RUN** | Contract runs it at PS-R1 only; this task is PS-R3 only |
| **CTRL-BS** | 8 | RUN (subsample) | max abs mean log2 Â_k = 9.76e−03; at k=2, −5.62e−05 (z = −2.31) |

### 6.1 The two controls that are NOT RUN, per RULE-1

**CTRL-IDXMAP — NOT RUN.** Declared "Blocking" by the amendment; ruled a
**forward obligation** by the Coordinator. Satisfying it requires the (T)
sampler to express truncation and block extraction as explicit index arrays and
*gather* through them. `stage_a.py` does neither — it truncates with
`epp & mask_N` and partitions with `reshape`, and contains no index array
anywhere. This task may neither modify that sampler nor write under
`experiments/`. **No `index_map.json` was synthesized. No index arrays were
constructed, so no SHA-256 of them exists, and the corresponding
`amended_manifest_requirements` field is filled with the reason rather than a
number. This control is cited as passing by NOBODY.**

Carried forward under RULE-2: the amendment's reference expression
`L = n_2*dup` is defective and would fire with certainty on a *correct* run at
PS-A. It is not repaired here and was not exercised; at PS-R3, `dup = 1`, where
the expression is degenerate.

**CTRL-POSHOM clause (b) — NOT RUN.** Same grounds. Its required artifact
`pair_counts_by_position.csv` lives outside this task's write scope, and the
amendment already records clause (b) as **UNEVALUATED, not passed**.

**The cost travels with the measurement.** This run scored 17 cells with **two
declared controls unevaluated**, and any reading of it must carry that.

### 6.2 Caveats on the controls that did run

**NULL-M is under-powered and must not be leaned on.** It was sized to the
residual budget and got 81,980 trials — against `T_stab(17) = 1.0e6`, so k = m
is not even reachable on that arm. Its low-order values (+2.0e−04 at k=2,
+5.2e−04 at k=3) are consistent with the finite-T ratio bias of the estimator,
and its high-order values (+0.22 at k=17) are what an unreachable cell looks
like, not a signal. **The frozen interval is calibrated at T = 1e7 and does not
apply to this arm, so no firing verdict is given for it.** Its one usable
result is the TC-5 check on γ̂, which passes. That NULL-M is thin is a **budget**
outcome and never a null result (AGENTS.md rule 5).

**CTRL-BS ran on a 200,000-trial subsample**, not the full arm, for budget. Its
forced value is exactly 0. At k = 2 it reads −5.62e−05 (z = −2.31) — nonzero,
and consistent with the finite-T ratio bias at the *subsample's* T, which is 50×
smaller than the arm's. It is ~107× smaller than the (T) value at the same k.
I record that it is not exactly zero rather than rounding it to zero.

**NULL-P drifts negative at high k** (−1.37e−02 at k = 18) and still does not
fire, because the frozen interval is calibrated on exactly that null and already
absorbs the estimator's finite-T bias. This is the cleanest available evidence
that the firing in Table 1 is not the estimator misbehaving at T = 1e7 under the
binomial law: **same estimator, same T, same interval, zero firings.**

---

## 7. What this measurement does NOT establish

Stated because the run is only as good as its boundary, and several of these are
carried unchanged from the admitted amendment and its two reviews.

1. **Nothing about HQC, A17, A5, any DFR, or any standardized parameter set.**
   PS-R3 is a reduced surrogate matched to HQC-3's shape. **No cell at true HQC
   parameters is certified under criterion (iv) at all** — PS-A was dropped from
   that criterion by v3, and nothing replaced it.
2. **`RT2-OBJ-1` is not closed.** The size of INV-NULL under the **composite**
   null is unknown. The interval is calibrated against a *specific* binomial
   law at the measured q̂; a firing is scoped to **that tested null**, not to
   "order k" as such. The run-time size guard is drawn from the same binomial
   law and cannot see this by construction.
3. **`OPEN-6` is not closed, and it is the largest hole.** **No arm tests the
   (T) joint law against an answer known in advance.** CTRL-ORACLE checks
   estimator arithmetic on enumerable toys; NULL-P and NULL-M check the pipeline
   on laws where A_k = 1 is a theorem. Nothing here verifies that the (T)
   sampler produces the object the contract intends, against an independently
   known joint answer.
4. **The blind class is inherited unchanged.** CTRL-POSHOM is measured
   **structurally blind** to V1 (off-by-one truncation) and V2 (interleaved
   partition), and blind to V3 as tested. Clause (a) not firing here therefore
   does **not** exclude a V1/V2-type index defect — those are invisible to it by
   theorem, not by weakness. The red team's `RT3-OBJ-2` further records that
   whether V2 changes the estimand is **unmeasured**, with the campaign's
   resolution an order of magnitude too coarse to settle it.
5. **Two declared controls were not evaluated** (§6.1).
6. **`A17`'s full content is not what was tested.** S is a symmetric functional
   of `(F_1,…,F_{n_e})`, so even at k_max = n_e this rule would test only the
   **symmetrised** content of A17 — the amendment's own struck-and-corrected
   sentence, retained here.
7. **One run, one seed family, one machine.** No replication at an independent
   seed was authorized or performed.

---

## 8. Budget, timings, deviations

**Within budget: 5170.3 of 5200 authorized core-seconds** (29.7 remaining);
1205 s wall of 2400 authorized; peak RSS 876 MB self / 1029 MB largest child,
against a 2 GB allowance.

| stage | core-s | wall-s |
|---|---:|---:|
| prior invocations (see below) | 481.29 | — |
| provenance | 0.40 | 0.23 |
| **INV-NULL bit-identity reproduction (blocking)** | 16.20 | 10.13 |
| out-of-sample size + familywise | 7.19 | 4.15 |
| CTRL-ORACLE | 0.003 | 0.003 |
| NULL-P | 1.30 | 1.30 |
| **(T) arm, 8 shards × 1,250,000 trials** | **4613.91** | 1174.12 |
| (T) analysis + jackknife | 0.12 | 0.12 |
| CTRL-BS | 1.99 | 1.73 |
| CTRL-DEC | 0.18 | 0.18 |
| NULL-M | 47.57 | 12.68 |
| **total** | **5170.31** | 1205 |

Measured (T) throughput: **2168 trials/core-second** at PS-R3, against Stage-A's
2061 and my pre-run benchmark's 2090.

**Prior invocations charged to this task**, on the amendment's own convention
(user + sys CPU per invocation, summed, aborted runs included):

| invocation | core-s |
|---|---:|
| throughput benchmark of `stage_a._t_shard`, 2 × 20,000 trials | 20.29 |
| null-replicate / estimator microbenchmark | 1.60 |
| `measure.py --smoke` full-path shakedown (produced **no** measurement) | 453.40 |
| auditing one-liners (yaml/json/seed checks) — **estimated** | 6.00 |

**Deviation, reported not absorbed.** The shakedown cost 453.4 core-seconds
because its smoke path failed to scale NULL-M down — it ran the full 1,000,000
trials. That is my error, and it consumed most of the margin the Coordinator
left on this budget. It forced NULL-M in the real run down to 81,980 trials
(§6.2) and CTRL-BS and CTRL-POSHOM clause (a) onto subsamples. Had the (T)
throughput come in at my pre-run estimate rather than 5 % better, the
measurement would not have fitted and I would have had to report exhaustion
instead. The run nonetheless completed at full `T = 1e7` inside the authorized
budget, so the frozen interval binds as written and no truncation deviation
arises.

**Read-scope note.** My card's `read_scope` lists the oracle package but not
`BATCH-6fddee/.../stage_a.py`. I was directed to reuse that committed instrument
rather than reimplement it, and did so — reading and importing it unmodified.
Both my predecessors disclosed the same excursion; the card that orders reuse of
an instrument should list it.

**Seeds.** (T) arm shards `1000–1007`, deliberately **disjoint** from Stage-A's
shards `0–3` and its smoke shard `900`, so these are fresh draws and not a reuse
of the diagnostics trials whose q̂ calibrated the frozen table.

**Validity: `valid_measurement`.** All blocking gates passed, T achieved equals
T planned, and the arm ran under the admitted rule. Full detail, including the
per-cell re-derived constants and the raw S-histogram, is in
`measurement_results.json`; the exact command, git state, environment, seeds and
timings are in `run_manifest.yaml`.

---

## 9. One-line summary for the ledger

At PS-R3, T = 10,000,000, under the admitted v3 frozen interval and with all
blocking gates passing, **log2 Â_k lies below its frozen lower bound at every
k = 2..18, including the pre-specified k = m = 17 cell (−0.8657, −42.7 null SD),
while NULL-P at the same T and the same interval fires at none of the 17 cells** —
observed with two declared controls (CTRL-IDXMAP, CTRL-POSHOM clause (b))
unevaluated, at familywise size 1.026 % for the battery and 0.27 % for the
pre-specified cell alone, and scoped entirely to this one reduced parameter set.

*Executor record. I hold no authority to change status and changed none.*
