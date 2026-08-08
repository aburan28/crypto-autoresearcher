# Execution report — EXP-INSTR-85b102

| field | value |
|---|---|
| experiment | `EXP-INSTR-85b102` (approved, frozen, execution_authorized, evidence_eligible, 2026-08-07) |
| hypothesis | `H-INSTR-fffbfb` |
| question | `RQ-INSTR-f8faa0` |
| goal / batch | `GOAL-ENDO-001` / `BATCH-aa267f` |
| handoff | `TASK-20260807-681e17` |
| role | Executor |
| branch | `claude/ecdlp-endomorphism-analysis-4m2w3z` |
| stage reached | **S6 (emission). All of S0 → S6 executed.** |
| claim tier | **TOY.** `sota_delta` zero on every axis. |

**What this report is.** Observations and deviations. It contains no
interpretation of what the numbers mean for the research question, no evidence
record, no hypothesis-status change, and no statement that NULL-C is replaced or
retained. Those are Coordinator acts on a later ledger archive after independent
review (AGENTS.md rule 1; contract `authorization_note`).

**What this contract is not.** Not an ECDLP attack, discrete-logarithm
computation, relation collection, solver run, cost/exponent/speedup claim, or
adjudication of `RQ-ICINV-475b5e`. `certificate.kind: none` on every run,
explicitly: nothing here claims a solve or a factor-base relation, so there is
nothing to certify. The forced-value checks (liftable-count identity, `order`
returning exactly 0, `R5_PERCLASS` returning exactly 1.0, closed-form versus
Monte-Carlo null mean, Hurwitz–Kronecker census) are internal consistency
checks and are reported as such.

---

## 1. Repository state and base-commit check

Performed before any run manifest was written, per the handoff constraint.

- `git fetch origin main` → `origin/main` = `2d0c26c71f4a729ce70bf9764fd604aba3a6eacf`.
- `git merge-base HEAD origin/main` = the same sha; `git rev-list --count HEAD..origin/main` = **0**.
- **Merge outcome: nothing to merge.** `origin/main` is an ancestor of the branch
  head at the time of execution (`02487c1918fca88051b5ff3bf3248e648d9857a8`). No
  rebase was performed; no branch was pushed; no PR was opened or updated.

## 2. Deliverable: the new module

`harness/run_blocknull.py` (new file, ~3000 lines) with every function the
contract's `required_new_functions` block names:

| required | implemented as |
|---|---|
| `blocking(pool, rung)` → block map + realized geometry | `blocking()` → `(assignment, realized)` with `n_blocks`, `delta_max_N`, `blocks_with_ge_2_classes`, `blocks_with_ge_3_classes`, `degenerate`, band width, block composition by trace |
| `statistic_weighted(values, labels)` | `statistic_weighted()` = `SS_within/(n-K)` |
| `statistic_unweighted(values, labels)` | `statistic_unweighted()` = mean over labels with `n_c ≥ 2` of the `(n_c-1)`-denominator sample variance |
| `blocked_permutation_null(...)`, numpy-vectorized | `blocked_permutation_null()` returning the required 7-tuple, over `blocked_permutation_null_both()` which computes both statistics in one pass |
| `closed_form_null_mean(...)` | `closed_form_null_mean()`, returning `None` (not-applicable) when a class straddles blocks |
| `sumset_m2(E, fb)`, `sumset_m3(E, fb)` | exact enumeration, no targets, no sampling |

The permutation study is numpy-vectorized as the contract requires: measured
throughput ≈ 28 000 within-block permutations/second at n ≈ 1150. The whole
study — 4 pools × 7 rungs × 18 functional columns × 10 000 permutations, plus
4 pools × 7 rungs × (1 + 6) × 200 replicates × 1000 permutations, plus
CTRL-NSURR — ran in **0.97 CPU-hours against a 6 CPU-hour budget**. **No
replicate count was reduced. Every control cell ran at the declared 200
replicates**, and the declared minimum of 100 was never approached.

### CTRL-FROZEN-DIFF — zero behavioural change

`frozen_function_diff.txt` (in every run directory) records three independent
receipts, verdict **ZERO BEHAVIOURAL CHANGE**:

1. `git diff` against the binding base (`HEAD` = `02487c19`, the commit the
   contract was approved at and the four committed runs were produced at) is
   **empty** for all four frozen files: `harness/exp_icinv.py`,
   `harness/isogeny_class.py`, `harness/run_icinv.py`, `harness/toycurve.py`.
2. Per-function source SHA-256 taken live with `inspect.getsource` equals the
   SHA-256 of the same function extracted from the committed blob, for
   **11 of 11** named frozen functions: `_targets`, `targets_uniform`,
   `permutation_null`, `binomial_null_verdict`, `exact_null_verdict`,
   `decomposition_rate_m2`, `decomposition_rate_m3`, `liftable_density`,
   `factor_base_fixed_size`, `factor_base_window`, `two_torsion_x_count`.
3. A declared behavioural probe (p=101, a=2, b=3, seed 12345) evaluates each
   function and records its output verbatim, so a reviewer re-runs and compares
   numbers rather than trusting a hash.

Informational second row: those files already differed from `origin/main`
**before this contract existed** — branch commit `c9c27221` (BATCH-523510)
carries the campaign's own sampler correction, which this contract cites
(`CORR-20260807-9f83be`) rather than introduces. That is context, not the claim.

**Concurrency cross-check.** Each run's diff used `HEAD` at the moment it ran,
and `HEAD` moved during execution because a concurrent agent committed to this
same branch (`a3cbcd22`, an `EXP-ICINV-4d33aa` execution report and
implementation note; `7cc34bea`, two `CORR-*` ledger records). Neither touched
any harness file. Re-verified after all runs completed, **against the approval
commit `02487c1918fca88051b5ff3bf3248e648d9857a8` specifically**:
`git diff 02487c19 HEAD` is **empty** for all four frozen files and **11/11**
frozen functions hash identical — verdict **ZERO BEHAVIOURAL CHANGE**. The
receipt therefore holds against the commit the contract was approved at, not
merely against whatever `HEAD` happened to be per run.

---

## 3. Run inventory

**Thirteen** run directories under `experiments/EXP-INSTR-85b102/runs/`, against
a declared `maximum_runs: 16` — 3 runs of headroom left. Run records are
immutable: **no directory was overwritten, deleted or re-keyed.** Every corrected
run is a new run id and the defective one is preserved.

| run id | stage | status | valid | wall (s) | cpu (s) | peak RSS | commit | note |
|---|---|---|---|---|---|---|---|---|
| `RUN-INSTR-85b102-gates` | S0/S1/S2 | completed | true | 67.1 | 64.2 | 91 MB | `02487c19` | superseded (defective `frozen_function_diff` artifact) |
| `RUN-INSTR-85b102-gates-b` | S0/S1/S2 | completed | true | 58.2 | 58.7 | 91 MB | `02487c19` | **operative gate record** |
| `RUN-INSTR-85b102-poolA` | S3/S4/S5 | completed | true | 225.0 | 225.5 | 185 MB | `f6697e97` | superseded (two defective diagnostics) |
| `RUN-INSTR-85b102-poolA-b` | S3/S4/S5 | completed | true | 181.4 | 182.2 | 196 MB | `7d7fefc4` | superseded (shape-invariance defect) |
| `RUN-INSTR-85b102-poolA-c` | S3/S4/S5 | completed | true | 183.4 | 184.1 | 178 MB | `9c37e4f7` | **operative POOL_A record** |
| `RUN-INSTR-85b102-poolB` | S3/S4/S5 | completed | **false** | 764.3 | 762.0 | 205 MB | `9591caac` | **STOPPED by the R5_PERCLASS forced-value rule — `implementation_error`, not a negative observation** |
| `RUN-INSTR-85b102-poolB-b` | S3/S4/S5 | completed | true | 698.5 | 698.9 | 197 MB | `9c37e4f7` | **operative POOL_B record** |
| `RUN-INSTR-85b102-poolC` | S3/S4/S5 | completed | true | 208.3 | 209.0 | 187 MB | `e4b36a65` | **operative POOL_C record** |
| `RUN-INSTR-85b102-poolD` | S3/S4/S5 | completed | true | 1118.6 | 1112.2 | 210 MB | `7cc34bea` | **operative POOL_D record** |
| `RUN-INSTR-85b102-scorecard` | S6 | completed | true | 0.8 | 1.7 | 84 MB | `0bcae001` | superseded (P4 not decomposed) |
| `RUN-INSTR-85b102-scorecard-b` | S6 | completed | true | 0.8 | 1.5 | 84 MB | `0bcae001`, **dirty** | superseded (no SC5 collapse audit) |
| `RUN-INSTR-85b102-scorecard-c` | S6 | completed | true | 0.8 | 1.5 | 84 MB | `0bcae001`, **dirty** | superseded (ran from a dirty tree — see D17) |
| `RUN-INSTR-85b102-scorecard-d` | S6 | completed | true | 0.8 | 1.5 | 84 MB | `56d2a915`, clean | **operative emission record** |

**Dirty-tree state.** `code.dirty` is recorded in every manifest. It is **false
for every operative record** — `-gates-b`, `-poolA-c`, `-poolB-b`, `-poolC`,
`-poolD`, `-scorecard-d` — and true only for superseded or invalid runs
(`-poolA`, `-poolA-b`, `-poolB`, `-scorecard-b`, `-scorecard-c`), which were made
while the repair being tested was still uncommitted.

**Budget.** Longest single run 1118.6 s against the declared 5400 s per-run wall
limit. Total 3508.1 s wall / 3503.0 s CPU = **0.97 of the declared 6 CPU-hours**.
Peak RSS 210 MB against the declared 4 GB, which was additionally applied as a
hard `RLIMIT_AS` cap in every run. **No budget or resource limit was reached and
no `resource_exhaustion` occurred.**

Every run directory carries the full required artifact set: `results.json`,
`pool_table.json`, `rung_table.json`, `per_curve.csv`, `controls.json`,
`committed_fixture_table.json`, `prediction_scorecard.json`,
`frozen_function_diff.txt`, plus `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`.

---

## 4. S0 — pool freeze, before any functional was measured

`class_census` (Hurwitz–Kronecker) at both primes:

| prime | curves enumerated | traces | census failures |
|---|---|---|---|
| 4001 | 8004 | 253 | **0** |
| 6007 | 12018 | 311 | **0** |

The stopping rule "any `class_census` failure" did **not** fire. The pools were
frozen and written to `RUN-INSTR-85b102-gates-b/pool_freeze.json`, and every
later stage **read the traces back from that committed artifact** rather than
re-deriving them, so the quantifier order in the contract (pool frozen before
any functional is measured) is enforced mechanically and not merely by ordering.

| pool | prime | rule | realized traces | n | K | class sizes | Δ_pool | 4√p | Δ_pool/4√p | Δ_pool/(p+1) | dropped |
|---|---|---|---|---|---|---|---|---|---|---|---|
| POOL_A | 4001 | `pick_classes(4001, 3)` | 30, −30, 18, −18 | 472 | 4 | 138/138/98/98 | 60 | 253.01 | 0.2371 | 0.014993 | none |
| POOL_B | 4001 | `pick_classes(4001, 11)` | 30, −30, 18, −18, 78, −78, 90, 66, 54, 2, −2, −54 | 1152 | 12 | 138,138,98,98,88,88,84×6 | 168 | 253.01 | 0.6640 | 0.041979 | none |
| POOL_C | 4001 | 12 uniform draws from the 174 ordinary traces with size ≥ 20, arm label `POOLC` | 72, 26, 94, 9, −69, −23, −26, −32, −94, −31, 98, 25 | 424 | 12 | 72,48,32,31,25,25,48,24,32,21,38,28 | 192 | 253.01 | 0.7589 | 0.047976 | none |
| POOL_D | 6007 | `pick_classes(6007, 11)` | 8, −8, 40, −40, 32, −32, 48, −48, 22, −22, 68, −68 | 1464 | 12 | 140,140,132,132,126,126,114,114,112,112,108,108 | 136 | 310.02 | 0.4387 | 0.022636 | none |

POOL_A realized exactly the expectation stated in the contract (traces
{30,−30,18,−18}, sizes 138/138/98/98, N 3972/4032/3984/4020, Δ_pool = 60).
POOL_B, POOL_C and POOL_D were not predicted and are recorded here first.
**No class fell below the size floor of 20 at any pool, so the
`dropped_class_rule` recorded zero drops** — the rule ran and found nothing,
which is different from not running.

Realized band widths: POOL_A (30, 8, 2), POOL_B (84, 21, 6), POOL_C (96, 24, 6),
POOL_D (68, 17, 5). Full rung tables with block composition by trace are in each
run's `rung_table.json`.

### Committed fixture resolution

**11 of 11 fixtures RESOLVED, 0 UNREACHABLE.** The stopping rule "more than half
UNREACHABLE" did not fire. `committed_fixture_table.json` gives each fixture, its
primary path, RESOLVED/UNREACHABLE, the value read and the signed difference; all
signed differences are 0.

Two fixtures are stored in the committed artifacts as p-values rather than raw
counts (`permutation_null.liftable_density`, `window_decay` W=4001). The raw count
is recovered exactly as `p_value × B`, because `permutation_null` returns
`worse / iterations`; this is recorded in the fixture table rather than assumed.

---

## 5. S1 — the zero-compute arithmetic gate

Run **before any compute**, from the committed per-class `(N, n, mean z, Var z)`
of `RUN-ICINV-p4001-a` alone.

| quantity | re-derived | committed | signed difference | tolerance | gate |
|---|---|---|---|---|---|
| `mean_c Var(z_c)/4` (count units) | `0.24938572928901642` | `0.24938572928898783` | `+2.859e-14` | 1e-9 | **PASS** |
| closed-form free-permutation null mean (rate units) | `1.035750008010729e-05` | `1.0357263552475702e-05` | `+2.365e-10`, relative `+2.284e-05` | 1e-3 relative | **PASS** |

Intermediates recorded: pooled n = 472, grand mean N = 4002 exactly,
SS_N = 311904, S²_N = 662.2165605095541, SS_z = 468.6101762…,
S²_z = 0.9949260…, **Cov(N,z) = 0 exactly** (the pool is two symmetric twist
pairs), S²_Y = 165.8028716… count², committed ratio 664.79.

**The S1 gate PASSED, so the run continued.** The withdrawal branch (F1) was not
taken and the diagnosis under test was not withdrawn — which is an observation,
not an endorsement of it.

## 6. S2 — committed-fixture reproduction

Executed on the frozen POOL-A slice at seed 20260807 through the **unmodified**
committed code path. Realized dict insertion order recorded: **`[30, -30, 18, -18]`**
(that is `[target] + controls` as `run_icinv.main` builds it), with curves in
`isogeny_classes(p)` order, i.e. `enumerate_curves(p)` order by j-invariant then
twist. Reproduction depends on this order because `permutation_null` derives its
group sizes from `groups.values()`.

All seven sampler-free fixtures reproduced **BITWISE on raw counts, not merely on
rounded p-values**:

| fixture | committed | reproduced | match |
|---|---|---|---|
| `permutation_null.liftable_density` raw count | r = 1 of B = 2000 (p = 0.0005) | r = 1 of 2000, p bitwise `0.0005` | ✅ |
| `window_decay` W=4001 raw count | r = 0 of B = 1000 (p = 0.0) | r = 0 of 1000, p bitwise `0.0` | ✅ |
| `window_decay` W=4001 observed | `1.557881769803647e-08` | bitwise identical | ✅ |
| `window_decay` W=4001 null_mean | `1.0357263552475702e-05` | bitwise identical | ✅ |
| `full_field_liftable_within_class_count_variance` | `0.24938572928898783` | bitwise identical | ✅ |
| Var(z) at traces ±30 (n=138) | `1.0053951126626468` | bitwise identical at both | ✅ |
| Var(z) at traces ±18 (n=98) | `0.9896907216494846` | bitwise identical at both | ✅ |

Sampler-dependent fixtures, checked against `RUN-ICINV-p4001-degenfix` only (the
only valid target for today's code) and **not** a stopping rule: all four
reproduced on raw counts —
`decomp_efficiency_m2` r = 1563/2000, `decomp_efficiency_m3` r = 196/2000,
`decomp_rate_m2_RAW` r = 565/2000, `decomp_rate_m3_RAW` r = 214/2000, matching
the committed 0.7815 / 0.098 / 0.2825 / 0.107 exactly.

**The S2 gate PASSED.** No instrument instability was observed and the F2 branch
was not taken.

---

## 7. S3 — measurement

18 functional columns per curve (the contract's 13 declared keys, with
`liftable_density_W` expanding to its six declared windows — see deviation D5).
`per_curve.csv` in each pool run carries one row per curve with `p, a, b, j,
trace, N, aut_order`, factor-base sizes, hit counts, every functional, and the
per-curve identity flag.

| pool | curves | measurement wall | liftable-count identity holds | CTRL-TWIST |
|---|---|---|---|---|
| POOL_A | 472 | 47.9 s | **472/472** | 2 pooled pairs, all agree, 0 unpaired |
| POOL_B | 1152 | 69.9 s | **1152/1152** | 5 pooled pairs, all agree, unpaired {90, 66} |
| POOL_C | 424 | 41.4 s | **424/424** | 2 pooled pairs, all agree, 8 unpaired |
| POOL_D | 1464 | 172.9 s | **1464/1464** | **6 pooled pairs, all agree, 0 unpaired** |

**CTRL-TWIST**: every pooled `{t,−t}` pair at every pool has equal class sizes
and an identical **sorted** `two_torsion_x` multiset. At POOL_A the realized
composition is 66 curves with z=3 and 72 with z=1 in each of traces 30 and −30,
and 42 with z=3 and 56 with z=1 in each of 18 and −18 — exactly the composition
the contract derived from committed means, sizes and "distinct values: 2". At
p = 6007 all six pairs agree (out-of-sample). The F6 branch was not taken.

---

## 8. S4 / S5 — per-rung operating characteristics

**This is the deliverable the handoff asks for.** Realized size on both control
objects, power, nuisance budget and δ\*, per rung per pool. Exact two-sided 99 %
Binomial(200, 0.05) acceptance interval, computed by the Executor with exact
binomial probabilities: **[3, 19]** (the contract's normal-approximation guide
said "roughly 3 to 18"). Level 0.05, decision on `p_lower`, primary statistic
weighted, control B = 1000, primary B = 10 000, 200 replicates per cell.

### POOL_A — p = 4001, 4 classes, 472 curves

| rung | Δ_max(N) | blocks | nuisance budget | CTRL-NULLOBJ size (rej) | CTRL-SIZE0 size (rej) | calibrated | power@0.8 | δ\* |
|---|---|---|---|---|---|---|---|---|
| R0_FREE | 60 | 1 | 662.16 | 0.090 (18) | 0.040 (8) | ✅ | 1.000 | 0.2 |
| R1_TWIST | 60 | 2 | 663.82 | 0.065 (13) | 0.040 (8) | ✅ | 1.000 | 0.2 |
| R2_NBAND_w2 | 12 | 3 | 17.558 | 0.060 (12) | 0.065 (13) | ✅ | 1.000 | 0.2 |
| R3_NBAND_w3 | 0 | 4 | 0 | 0.060 (12) | 0.000 (0) — forced | degenerate | — | — |
| R4_NBAND_w4 | 0 | 4 | 0 | 0.060 (12) | 0.000 (0) — forced | degenerate | — | — |
| R5_PERCLASS | 0 | 4 | 0 | 0.040 (8) | 0.000 (0) — forced | degenerate | — | — |
| R6_TWIST_AND_NBAND_w2 | 0 | 4 | 0 | 0.050 (10) | 0.000 (0) — forced | degenerate | — | — |

### POOL_B — p = 4001, 12 classes, 1152 curves

| rung | Δ_max(N) | blocks | nuisance budget | CTRL-NULLOBJ size (rej) | CTRL-SIZE0 size (rej) | calibrated | power@0.8 | δ\* |
|---|---|---|---|---|---|---|---|---|
| R0_FREE | 168 | 1 | 2406.80 | 0.075 (15) | 0.050 (10) | ✅ | 1.000 | 0.2 |
| R1_TWIST | 156 | 7 | 1634.06 | 0.045 (9) | 0.025 (5) | ✅ | 1.000 | 0.2 |
| R2_NBAND_w2 | 72 | 3 | 483.09 | 0.045 (9) | 0.040 (8) | ✅ | 1.000 | 0.2 |
| **R3_NBAND_w3** | **12** | 8 | **18.463** | 0.045 (9) | 0.055 (11) | ✅ | **1.000** | **0.2** |
| R4_NBAND_w4 | 0 | 12 | 0 | 0.075 (15) | 0.000 (0) — forced | degenerate | — | — |
| R5_PERCLASS | 0 | 12 | 0 | 0.080 (16) | 0.000 (0) — forced | degenerate | — | — |
| R6_TWIST_AND_NBAND_w2 | 4 | 11 | 0.586 | 0.045 (9) | 0.040 (8) | ✅ | 1.000 | 0.4 |

### POOL_C — p = 4001, 12 randomly drawn traces, 424 curves (selection control)

| rung | Δ_max(N) | blocks | nuisance budget | CTRL-NULLOBJ size (rej) | CTRL-SIZE0 size (rej) | calibrated | power@0.8 | δ\* |
|---|---|---|---|---|---|---|---|---|
| R0_FREE | 192 | 1 | 3489.11 | 0.050 (10) | 0.065 (13) | ✅ | 1.000 | 0.4 |
| R1_TWIST | 188 | 10 | 1506.46 | 0.020 (4) | 0.075 (15) | ✅ | 1.000 | 0.4 |
| R2_NBAND_w2 | 89 | 3 | 729.47 | 0.055 (11) | 0.055 (11) | ✅ | 1.000 | 0.4 |
| R3_NBAND_w3 | 17 | 6 | 18.421 | 0.060 (12) | 0.030 (6) | ✅ | 1.000 | 0.4 |
| **R4_NBAND_w4** | **4** | 8 | **1.0878** | 0.075 (15) | 0.040 (8) | ✅ | **1.000** | **0.4** |
| R5_PERCLASS | 0 | 12 | 0 | 0.015 (3) | 0.000 (0) — forced | degenerate | — | — |
| R6_TWIST_AND_NBAND_w2 | 0 | 12 | 0 | 0.060 (12) | 0.000 (0) — forced | degenerate | — | — |

### POOL_D — p = 6007, 12 classes, 1464 curves (mandatory second prime)

| rung | Δ_max(N) | blocks | nuisance budget | CTRL-NULLOBJ size (rej) | CTRL-SIZE0 size (rej) | calibrated | power@0.8 | δ\* |
|---|---|---|---|---|---|---|---|---|
| R0_FREE | 136 | 1 | 1593.16 | 0.070 (14) | 0.030 (6) | ✅ | 1.000 | 0.2 |
| R1_TWIST | 136 | 6 | 1598.31 | 0.050 (10) | 0.015 (3) | ✅ | 1.000 | 0.2 |
| R2_NBAND_w2 | 60 | 3 | 265.20 | 0.050 (10) | 0.040 (8) | ✅ | 1.000 | 0.1 |
| **R3_NBAND_w3** | **10** | 8 | **13.503** | 0.035 (7) | 0.045 (9) | ✅ | **1.000** | **0.2** |
| R4_NBAND_w4 | 0 | 12 | 0 | 0.065 (13) | 0.000 (0) — forced | degenerate | — | — |
| R5_PERCLASS | 0 | 12 | 0 | 0.060 (12) | 0.000 (0) — forced | degenerate | — | — |
| R6_TWIST_AND_NBAND_w2 | 0 | 12 | 0 | 0.050 (10) | 0.000 (0) — forced | degenerate | — | — |

**Size calibration.** CTRL-NULLOBJ landed inside [3, 19] at **28 of 28**
(pool, rung) cells. CTRL-SIZE0 landed inside [3, 19] at **every non-degenerate
rung of every pool** (16 of 16) and returned **exactly 0 rejections at every
degenerate rung** (12 of 12). **No rung was excluded for uncalibrated size on a
non-degenerate rung.** The zero at degenerate rungs is forced by construction —
there the within-block label permutation is the identity, so `p_lower` is exactly
1.0 in every replicate — and it is reported as forced rather than as a
calibration failure; those rungs report no test either way under the contract's
own `degeneracy_rule`. This is flagged in `controls.json` as
`forced_by_degeneracy: true` and is stated here so a reviewer sees the literal
"outside the interval" fact and its cause together.

**Power.** Power at 0.8 within-class standard deviations is **1.000 (200/200
replicates) at every non-degenerate rung of every pool**, so the power cost of
blocking relative to R0_FREE is **0.000 at 0.8 sd everywhere**. δ\* (the smallest
grid effect with power ≥ 0.80) is 0.2 at POOL_A and POOL_B, 0.4 at POOL_C
(424 curves), 0.2 at POOL_D and 0.1 at POOL_D R2. The two deciding rungs for SC3
and P8 — POOL_B R3_NBAND_w3 and POOL_D R3_NBAND_w3 — both carry
`two_class_block: true` (no block holds three or more classes), so the planted
±1 offsets there were unavoidably monotone in N; the flag is recorded beside the
number as the contract requires, and the realized within-block correlation
between the offset u and N is **−0.189 at POOL_B R3** and **+0.442 at POOL_D R3**.

**Nuisance budget along the N ladder** (functional `order`, weighted statistic;
Δ_max non-increasing at every pool):

| pool | R0_FREE | R2 | R3 | R4 | R5 | SC5 clause satisfied at every step |
|---|---|---|---|---|---|---|
| POOL_A | 662.16 | 17.558 | 0 | 0 (collapsed) | 0 (collapsed) | ✅ |
| POOL_B | 2406.80 | 483.09 | 18.463 | 0 | 0 (collapsed) | ✅ |
| POOL_C | 3489.11 | 729.47 | 18.421 | 1.0878 | 0 | ✅ |
| POOL_D | 1593.16 | 265.20 | 13.503 | 0 | 0 (collapsed) | ✅ |

**Contamination gap** (the contract's headline pairing, `(p_lower, R, Δ_max)` at
R0_FREE beside the finest non-degenerate rung) is emitted for every functional
and pool in each run's `results.json` under `contamination_gap`, on both
statistics. Excess-over-surrogate curves (CTRL-NSURR, 50 replicates per
functional per rung, slope EXACT for `order` (1) and `full_liftable` (1/2) and
ESTIMATED with its standard error otherwise) are in each run's `controls.json`.

---

## 9. Tail checks

| tail check | POOL_A | POOL_B | POOL_C | POOL_D |
|---|---|---|---|---|
| `R5_PERCLASS` returns `p_lower` **exactly** 1.0, every functional | PASS | PASS | PASS | PASS |
| `order` returns `T_obs` exactly 0.0 at every rung | PASS | PASS | PASS | PASS |
| liftable-count identity per curve | PASS 472/472 | PASS 1152/1152 | PASS 424/424 | PASS 1464/1464 |
| no p-value exactly 0.0 or 1.0 outside a degenerate rung | **FAIL (literal)** | **FAIL (literal)** | **FAIL (literal)** | **FAIL (literal)** |
| smallest `p_lower` ≥ 1/(1+B) | PASS | PASS | PASS | PASS |
| closed form within 3 MC standard errors, `order` and `full_liftable` | **FAIL (literal)** | PASS | **FAIL (literal)** | **FAIL (literal)** |
| CTRL-NULLOBJ most extreme replicate consistent with 200 Uniform(0,1) draws | PASS | PASS | PASS | PASS |
| `T_obs` shape-invariance self-check (added after the POOL_B defect) | PASS | PASS | PASS | PASS |
| Δ_max non-increasing along R0→R2→R3→R4→R5 | PASS | PASS | PASS | PASS |

Both literal FAILs are reported in **both readings** in `results.json`, with the
Executor choosing neither:

- **"no p-value exactly 0.0 or 1.0".** **No p-value of exactly 0.0 occurs
  anywhere** — the frozen estimator makes it impossible and none was observed,
  which is the check's own stated rationale. The exactly-1.0 cells are tail
  p-values where `T_obs` lies at or outside that end of the realized null
  support, so the opposite tail sits at the resolution floor; each is listed with
  its `T_obs`, `null_min`, `null_max` and both tails. The
  `implementation_defect_indicator` is **PASS at all four pools**, with **zero
  unexplained cells**.
- **"closed form within 3 MC standard errors".** Every offending cell is at a
  **degenerate rung where the realized null is a bitwise point mass**: all B
  draws are identical, so numpy's pairwise summation of B identical doubles
  returns a mean one ulp off and the "Monte-Carlo standard error" is
  one-ulp-over-√B. Dividing a one-ulp difference by that yields ≈ 100 "standard
  errors" from an agreement whose **relative residual is 1.1e-16**. The
  `genuine_disagreement_indicator` — cells with a genuinely non-degenerate null —
  is **PASS at all four pools**, with **zero** offenders. Full per-cell tables
  (closed form, empirical, absolute and relative residual, MC SE) are in
  `results.json`.

---

## 10. Prediction scorecard P1–P8

From `RUN-INSTR-85b102-scorecard-d/prediction_scorecard.json` (byte-identical to `-scorecard-c`). Deciding numbers
abbreviated; the full record carries all of them.

| id | score | sample | deciding number |
|---|---|---|---|
| **P1** | **MET** | IN-SAMPLE | `T_obs` = `0.24938572928901642` vs committed `0.24938572928898783`, difference `2.859e-14` ≤ 1e-9; closed-form free null mean `165.80287163985756` count² = `1.035750008010729e-05` rate vs committed `1.0357263552475702e-05`, relative residual `2.284e-05` ≤ 1e-3. Frozen prediction 165.8028717 reproduced. |
| **P2** | **MET** | IN-SAMPLE | `E[T_π \| twist]` = `153.8650775` vs frozen `153.8651` (difference `−2.2e-05`); 1/ratio `616.976` vs frozen `617.0`; free 1/ratio `664.845` vs frozen `664.8`; `p_lower` = `9.999e-05` = the resolution floor exactly. |
| **P3** | **MET** | IN-SAMPLE | Finest non-degenerate rung R2_NBAND_w2, Δ_max 12 (= frozen 12), `p_lower` at the floor, **zero non-degenerate rungs clear 0.05** for `full_liftable`. Realized band width **30**, not the frozen illustration's 24 — see deviation D4. Realized `E[T_π]` = 4.566 and 1/ratio 18.31 against the frozen 9.0279 and 36.2, which are values for a partition the declared rule does not produce. |
| **P4** | **NOT MET** (literal) | IN-SAMPLE at POOL_A, OUT-OF-SAMPLE elsewhere | Two sub-clauses, scored separately. **p-hat sub-clause MET at zero tolerance: `p_lower` bitwise 1.0 in 144/144 cells (4 pools × 18 functionals × 2 statistics).** Ratio sub-clause NOT MET bitwise: max \|R − 1\| = **2.2e-16** against the empirical null mean (88 cells) and against the closed form (fewer cells). The cause is the denominator — at a degenerate rung all B draws are bitwise identical and their pairwise-summed mean is not bitwise that value. The contract's stopping rule and tail check are on `p_lower` and both passed at every pool. |
| **P5** | **MET** | IN-SAMPLE at POOL_A, **OUT-OF-SAMPLE at p = 6007** | Sorted `two_torsion_x` multisets identical across every pooled twist pair at all four pools; POOL_A composition exactly 66×z=3 / 72×z=1 at ±30 and 42×z=3 / 56×z=1 at ±18; all six pairs agree at p = 6007. |
| **P6** | **MET** | IN-SAMPLE | R6_TWIST_AND_NBAND_w2 at POOL_A is **degenerate**: 4 blocks for 4 classes, 0 blocks with ≥ 2 classes, `p_lower` = 1.0, w2 = 30 against min 2\|t\| = 36. |
| **P7** | **MET** | OUT-OF-SAMPLE | At both twelve-class pools the exact sum-set is more significant than the sampled rate under the FREE permutation: POOL_B m=2 `p_lower` 9.999e-05 (r=0) vs 1.9998e-04 (r=1), m=3 0.1111 (r=1110) vs 0.3665 (r=3664); POOL_D m=2 3.9996e-04 (r=3) vs 6.1994e-03 (r=61), m=3 0.0992 (r=991) vs 0.7560 (r=7560). **Recorded contrary observation: at POOL_C the direction reverses at both m** (m=2 4.9995e-04 vs 9.999e-05; m=3 0.6829 vs 6.0994e-03). POOL_A also satisfies it at both m. |
| **P8** | **MET** | OUT-OF-SAMPLE | Power at 0.8 within-class sd = **1.000 (200/200)** at the finest non-degenerate rung of both twelve-class pools: POOL_B R3_NBAND_w3 (Δ_max 12, nuisance 18.463, δ\* 0.2, `two_class_block: true`, corr(u,N) = −0.189) and POOL_D R3_NBAND_w3 (Δ_max 10, nuisance 13.503, δ\* 0.2, `two_class_block: true`, corr(u,N) = +0.442). Size calibrated at both. |

### SC8 — the clause that can return a negative

Reported as numbers only. **The Executor does not decide adoption.**

| pool | finest non-degenerate rung | nuisance R0_FREE | nuisance finest | reduction | ≥ 10× | power@0.8 | ≥ 0.90 | both met | size calibrated |
|---|---|---|---|---|---|---|---|---|---|
| POOL_A | R2_NBAND_w2 | 662.16 | 17.558 | **37.7×** | yes | 1.000 | yes | yes | yes |
| POOL_B | R3_NBAND_w3 | 2406.80 | 18.463 | **130.4×** | yes | 1.000 | yes | yes | yes |
| POOL_C | R4_NBAND_w4 | 3489.11 | 1.0878 | **3207.5×** | yes | 1.000 | yes | yes | yes |
| POOL_D | R3_NBAND_w3 | 1593.16 | 13.503 | **118.0×** | yes | 1.000 | yes | yes | yes |

`satisfied_at_both_primes: true` on the two twelve-class pools.

**Reading note on SC8's quantifier, recorded rather than resolved.** SC8 is
written "for at least one primary functional other than `order` and
`full_liftable`, the nuisance budget is reduced … AND the power … remains …".
Neither quantity depends on the functional: the nuisance budget is by definition
`E[T_π | rung]` for `order`, and the power study is on synthetic planted data.
The table above therefore evaluates SC8 per pool, which is the only coherent
reading available to the Executor. **This is flagged for the Coordinator rather
than resolved here.**

---

## 11. The pre-registered contradiction of IDEA-20260807-34754f

The contract's `divergence_from_parent_proposal` block derived, from committed
numbers and **before any run**, that twist blocking moves the observed/null
variance ratio by only ≈ 7 % and leaves the p-value at the resolution floor,
contradicting the parent proposal's own prediction 1 (which expected the
stratified p-value on full-field liftable density to rise above 0.05, honest
prior 0.75). **Measured outcome, on `full_liftable`, unweighted statistic:**

| pool | nuisance FREE | nuisance TWIST | nuisance change | 1/R FREE | 1/R TWIST | ratio movement | `p_lower` at TWIST |
|---|---|---|---|---|---|---|---|
| POOL_A (p=4001) | 662.16 | 663.82 | **+0.25 %** | 664.845 | 616.976 | **7.20 %** | **9.999e-05 = the floor** |
| POOL_B (p=4001) | 2406.80 | 1634.06 | −32.10 % | 2478.57 | 1763.75 | 28.84 % | **9.999e-05 = the floor** |
| POOL_C (p=4001) | 3489.11 | 1506.46 | −56.82 % | 8481.98 | 3940.13 | 53.55 % | **9.999e-05 = the floor** |
| POOL_D (p=6007) | 1593.16 | 1598.31 | **+0.32 %** | 1997.42 | 2119.37 | **−6.11 %** | **9.999e-05 = the floor** |

The measured outcome **matches the pre-registered contradiction**: at POOL_A the
ratio moves 7.20 % against the derived ≈ 7 %, and the p-value stays at the
resolution floor at **every one of the four pools and both primes**. At POOL_D
the ratio moves the *other* way (the twist-blocked ratio is smaller than the free
one) and the nuisance budget *rises* by 0.32 %, both consistent with the
contract's stated mechanism that `{t,−t}` is the pair with the **largest** N gap.
POOL_B and POOL_C move further only because they pool traces whose negations are
absent (2 of 12 at POOL_B, 8 of 12 at POOL_C), so R1_TWIST there is partly a
singleton partition rather than a twist-pair partition — recorded so the larger
movement is not misread as twist blocking working.

**No interpretation of what this implies for the parent proposal is offered
here.**

## 12. Unexpected observations, recorded not discarded

1. **`two_torsion_x` at p = 6007 survives the finest non-degenerate blocking.**
   At POOL_D, `p_lower` = 9.999e-05 (the floor) at **both** R0_FREE and
   R3_NBAND_w3, with R rising only 0.8408 → 0.8974, and CTRL-NSURR excess
   E = R_f/R_surr = **0.9114** (below 1, i.e. residual between-class structure
   beyond a matched pure-N surrogate). At POOL_B the same functional is
   unremarkable (`p_lower` = 0.1316 free). This does **not** trigger F7, which
   requires R < 1/4 at the finest non-degenerate rung while the surrogate's R
   exceeds 1/2 at **both** primes — here R = 0.897 and R_surr = 1.0001. It is
   recorded as an observation with the pool, prime, rung and functional named.
2. **`full_liftable` and `liftable_density` at W = p sit at the resolution floor
   at every rung at every pool**, with R rising from 4e-04 to ≈ 0.05 — the
   behaviour the contract pre-registered as arithmetically forced (N is injective
   in the trace). Reported as a reproduction of the pre-registration.
3. **Non-monotone ratio verdicts along the N ladder** occur in 17/36 cells at
   POOL_A, 18/36 at POOL_B, 23/36 at POOL_C and 16/36 at POOL_D (functional ×
   statistic). Per the contract's `what_non_decay_means` and SC5's own note, a
   non-monotone ratio is a **reportable outcome, not a clause failure**; every
   verdict with its full R sequence is in `results.json` under `monotonicity`.
   Most non-monotone cells are functionals whose R is already within ~0.5 % of 1
   at the free rung, where the ordering is Monte-Carlo noise; that is stated as a
   description of the numbers, not as an explanation.
4. **R1_TWIST's nuisance budget exceeds R0_FREE's** at POOL_A (663.82 vs 662.16)
   and POOL_D (1598.31 vs 1593.16). Blocking on the twist pair makes the residual
   within-block variance of N *larger* than no blocking at all. Consistent with
   the contract's derivation; recorded as measured.
5. **CTRL-NSURR excess E ≈ 1 for almost every functional at every rung** (POOL_B
   and POOL_D tables in §8's linked `controls.json`), with `full_liftable`'s
   E = 0.9936 at POOL_B R3 and 1.0003 at POOL_D R3 against an EXACT slope of 1/2.
   Recorded without interpretation.
6. **P7 reverses direction at POOL_C** (see the P7 row). Recorded.

---

## 13. Protocol deviations and defects

Every item below is a deviation, defect or judgement call. **None is omitted.**

| id | class | what | disposition |
|---|---|---|---|
| **D1** | `implementation_error` | `RUN-INSTR-85b102-gates` emitted a defective `frozen_function_diff` artifact: per-function hashes compared `inspect.getsource` output (trailing newline retained) against `ast.get_source_segment` output (trailing newline absent), reporting 11/11 frozen functions CHANGED on a normalization artifact; and the file-level rows compared against `origin/main` instead of the commit the contract was approved at. | Repaired; superseded by `RUN-INSTR-85b102-gates-b`. The defective run is preserved. S0/S1/S2 numbers were unaffected and reproduced identically. |
| **D2** | `infrastructure_error` | The first attempt at the corrected gates run was killed by SIGPIPE when its stdout was piped into `head -30`. **No run directory and no artifact were produced**, so nothing was overwritten. | Re-run with output redirected to a file. Recorded because it happened. |
| **D3** | `implementation_error` | `RUN-INSTR-85b102-poolA` and `-poolA-b` carried two defective **diagnostic** computations: `residual_in_mc_standard_errors` was computed at degenerate rungs where the null is a bitwise point mass (dividing one ulp by one-ulp-over-√B), and the exactly-1.0 p-value categoriser recognised only `T_obs == 0.0` as a forced boundary. | Repaired; both preserved and superseded. **All 252 cells reproduced BITWISE between `-poolA` and `-poolA-b`**, which is also the contract's `determinism_requirement` check. |
| **D4** | recorded pre-registration/realization mismatch — **no retune** | P3's frozen arithmetic uses band width **24** at POOL_A; the contract's declared rule `w2 = max(2, ceil(Δ_pool/2))` realizes **30**. The realized R2 blocks are {30,18},{−18},{−30} rather than {30,18},{−18,−30}. Δ_max = 12 is unchanged; `E[T_π]` and 1/ratio are not (4.566 and 18.31 against the frozen 9.0279 and 36.2). | **The declared rule was followed and no width was retuned.** Both the rule's realization and the frozen illustration's numbers are recorded side by side in `prediction_scorecard.json` under `P3.realization_note`. The substantive sub-claim (ratio far below 1, p-hat at the floor, no non-degenerate rung clears 0.05) is scored on the realized partition. |
| **D5** | scope clarification | The contract declares **13** functional keys and its budget note counts 13; `liftable_density_W` is one key with six declared windows, so **18 functional columns** were measured and reported per curve. `window W` is an explicit `independent_variable` in the contract. | All 18 reported; no functional omitted or added beyond the declared window family. |
| **D6** | **STOPPING RULE FIRED — `implementation_error`, not a negative observation** | At POOL_B, `R5_PERCLASS` returned `p_lower` = 1/(1+B) instead of exactly 1.0 for `sumset_m3`, `sumset_eff_m3` and `decomp_rate_m2` on the unweighted statistic. Root cause, entirely in the new module: `_Layout.statistics` ended with `SS[:, ge2].sum(axis=1)`; `np.add.reduceat` returns an array whose contiguity depends on the row count, numpy selects a pairwise or strided reduction accordingly, and the sum over 12 classes was therefore taken in a **different order** for the one-row observed array than for the 2083-row null chunk. POOL_A (K = 4) never exposed it. | **The run stopped and `RUN-INSTR-85b102-poolB` is recorded `valid: false` with `invalid_reason`.** Repaired by explicit column-by-column accumulation, plus a new per-cell self-check `observed_shape_invariance` (recomputes `T_obs` at 1 row and 8 rows and requires bitwise agreement) and a new tail check reporting it. **No frozen harness function and no measured functional is involved.** All four pools were re-run under new run ids after the repair; all now pass. |
| **D7** | `implementation_error` (reporting) | `_collapsed_onto_predecessor` in the pool runs compared block-**id-keyed** composition dicts, so `R5_PERCLASS` was reported as not collapsed onto `R4_NBAND_w4` at POOL_A, POOL_B and POOL_D although both realize the identical all-singleton partition, differing only in whether ids run by N band or by trace. | Repaired in the module and **audited from the committed block compositions** in `RUN-INSTR-85b102-scorecard-d` (`sc5_collapse_audit`), which reports both readings and **supersedes the field inside the pool run records**. No measured number changes. With the corrected flag, **SC5's nuisance clause is satisfied at every ladder step at all four pools.** |
| **D8** | `implementation_error` (reporting) | `RUN-INSTR-85b102-scorecard` scored P4 as one combined clause, hiding that the p-hat clause is met at zero tolerance while only the ratio clause misses by ≤ 2 ulp. | Superseded by `-scorecard-b`, `-scorecard-c` and finally `-scorecard-d`. All four read the same four pool run records; no measured number changed. |
| **D9** | under-determined field resolved by the Executor, declared | The contract does not name which functional CTRL-NULLOBJ runs on, and its cost accounting gives 200 replicates **per rung**, not per functional. **`full_liftable` was used**, declared in `controls.json` as `nullobj_functional`. | Recorded. One functional per (pool, rung), 200 replicates, as the cost accounting implies. |
| **D10** | under-determined field resolved by the Executor, declared | The seed rule's `(L, P, Rg, F, d, r)` tuple is undefined for arms with no rung/functional. Declared choices: POOL_C draw uses `L=POOLC, P=POOL_C, Rg=NONE, F=NONE, d=0, r=0`; CTRL-POWER uses `L=CTRLPOWER` for the data draw and `L=CTRLPOWERPERM` for the permutation draw with the same `(P, Rg, F=synthetic, d, r)`; CTRL-NULLOBJ uses `L=NULLOBJ` with `F=labels` for the synthetic labelling and `F=full_liftable` for the permutations; CTRL-NSURR uses `L=NSURR`. | All recorded in the module and reproducible from the tuple alone. |
| **D11** | declared implementation choice | `targets_uniform` needs a sampler seed but the contract's `seeds` block says the measurement arms "need none". **The committed reproduction seed 20260807 was used at every pool**, which is the contract's own `test_boundary.parameters.reproduction_seed` and is what makes the POOL_A head-to-head against the committed NULL-C rows meaningful. | Recorded in every run's `parameters`. |
| **D12** | declared implementation choice | CTRL-NULLOBJ, CTRL-SIZE0 and CTRL-POWER use **B = 1000** (the contract's `power_study_B`), since all three are level-0.05 decisions. Only the S4 ladder uses B = 10 000. CTRL-NSURR uses the **closed-form** null mean rather than a Monte-Carlo one, which is exact under the coarsening invariant (the surrogate's classes lie inside blocks by construction) and is labelled `null_mean_source: closed_form` in `controls.json`. | Recorded. Every comparison keeps B and the estimator constant within itself, per the contract's `invalidation_rules`. |
| **D13** | declared numerical convention | Every statistic sorts each class's values ascending before summing, so it is a function of the class value multiset alone and is bit-for-bit reproducible under re-ordering. `T_obs` is computed by pushing the identity permutation through the **same** vectorized path as the null draws. This is what makes `R5_PERCLASS` return exactly 1.0 without any tolerance or short-circuit in the p-value counter. The definitional (unsorted-order) `statistic_weighted`/`statistic_unweighted` are also exported and used by CTRL-NSURR and the closed form. | Documented in the module header. |
| **D14** | artifact-scope note | The pool freeze at S0 records trace, N, size, aut-order histogram, census observed vs Hurwitz-predicted, agreement flag and kept/dropped. **`Var(z)` and the sorted-z hash are filled at S3**, in each pool's own `pool_table.json`, because measuring them at S0 would violate the freeze order the stage exists to enforce. | Both artifacts carry an explicit note saying so. |
| **D15** | measurement cache | A pure measurement cache keyed by `(p, a, b, fb sizes, target count, sampler seed)` lives **outside the repository** (`$TMPDIR/blocknull-cache`). It changes no number; deleting it only costs recomputation. POOL_A's re-runs show a 0.0 s measurement stage for this reason. | Recorded so the timing table is not misread. |
| **D16** | required-artifact gap, disclosed | The contract requires "the exact commands, git commit, dirty-tree state, **Python version and numpy version**". `environment.json` is written by the committed `harness/runner.py::environment()`, which records `python_version`, `sympy` and `pyyaml` but **not numpy**. That function was not modified: it is not on the frozen list, but four committed runs' manifests were produced by it and changing its output shape mid-contract is exactly the class of silent change this campaign has twice been bitten by. | **The numpy version is therefore recorded here: `numpy 2.4.6`**, alongside `python 3.11.15`, `sympy 1.14.0`, `pyyaml 6.0.1` from `environment.json`. The gap is disclosed rather than patched into already-committed run directories, which are immutable. Adding numpy to `runner.environment()` is left as a proposal for the Coordinator. |
| **D17** | reproducibility gap, repaired | `RUN-INSTR-85b102-scorecard-c` was executed with a **dirty tracked tree**: `code.dirty: true` at commit `0bcae001`, while the module edit it exercised was not committed until `56d2a915`. The commit its manifest records therefore does not contain the code it ran. | Re-run from a clean tree at `56d2a915` as `RUN-INSTR-85b102-scorecard-d`, whose `prediction_scorecard.json` is **byte-identical** to `-scorecard-c`'s. `-scorecard-c` is preserved and superseded. The same applies to the already-superseded `-poolA`, `-poolA-b`, `-poolB` and `-scorecard-b`; **no operative record has `dirty: true`.** |

**Not deviations, recorded for completeness:** no replicate count was reduced; no
budget limit was reached; no run was omitted; no arm was re-run "until favourable"
— every re-run is a repair of a named defect, every attempt is in the ledger
above, and the repaired runs reproduce the earlier numbers bitwise wherever the
defect did not touch them.

---

## 14. Completion gate

| gate item | status |
|---|---|
| `harness/run_blocknull.py` exists with all required new functions; `frozen_function_diff.txt` shows ZERO behavioural change to every frozen function | **met** — 11/11 functions unchanged, all four frozen files byte-identical to the approval commit |
| S0 completed, pool frozen with provenance BEFORE any functional measured; `class_census` agrees at both primes | **met** — 0 census failures at 4001 and 6007; later stages read the traces back from the committed freeze artifact |
| S1's arithmetic gate reported with both re-derived values and signed differences | **met** — `+2.859e-14` (tol 1e-9) and relative `+2.284e-05` (tol 1e-3), both PASS |
| Every sampler-free S2 fixture reproduced exactly on raw counts, with the realized dict insertion order recorded | **met** — 7/7 bitwise; insertion order `[30, -30, 18, -18]` recorded |
| Every (pool, functional, rung) cell reports both statistics' `T_obs`, empirical and closed-form null means with residual in MC SE, both tails' raw counts and p-values, R, Δ_max, nuisance budget, degeneracy flag | **met** — 252 cells per pool in `results.json`, keyed `(pool, functional, rung, statistic, B)` |
| `R5_PERCLASS` returns exactly 1.0 and `order` returns zero within-class variance | **met at all four operative pool runs.** It did **not** hold at `RUN-INSTR-85b102-poolB`, which is why that run is recorded invalid and the defect repaired (D6) |
| CTRL-NULLOBJ, CTRL-SIZE0, CTRL-POWER, CTRL-NSURR reported at every rung and pool with realized size against its exact binomial interval; no uncalibrated rung contributes a result | **met** — 28/28 CTRL-NULLOBJ cells inside [3,19]; CTRL-SIZE0 inside at all 16 non-degenerate cells and forced to 0 at all 12 degenerate ones, flagged as forced |
| `prediction_scorecard.json` scores P1–P8 with the deciding number and an IN-SAMPLE / OUT-OF-SAMPLE flag | **met** |
| Any replicate-count reduction reported AS a reduction; any budget or infrastructure failure recorded as `failed_infrastructure` rather than as a result | **met vacuously** — no reduction occurred (200/200 everywhere), no budget failure occurred; the one infrastructure event (D2) produced no artifacts and is recorded |
| all planned runs terminal; missing runs explained; required artifacts present; raw data and summaries agree; result reproduces from the recorded command and revision | **met** — 11 terminal runs, none missing; artifact set complete in every run directory; the POOL_A repeat reproduced all 252 cells bitwise from the recorded command and revision |

---

## 15. Artifact paths

```
harness/run_blocknull.py
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-gates/            (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-gates-b/          (operative: S0, S1, S2)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolA/            (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolA-b/          (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolA-c/          (operative: POOL_A)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolB/            (INVALID, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolB-b/          (operative: POOL_B)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolC/            (operative: POOL_C)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-poolD/            (operative: POOL_D)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-scorecard/        (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-scorecard-b/      (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-scorecard-c/      (superseded, preserved)
experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-scorecard-d/      (operative: S6 emission)
coordination/goals/GOAL-ENDO-001/batches/BATCH-aa267f/execution/EXP-INSTR-85b102/execution_report.md
```

Reproduction: each run's `command.txt` carries its exact command;
`manifest.yaml` carries the commit, dirty-tree state, environment, seeds,
timings and resources. Environment: **Python 3.11.15, sympy 1.14.0, pyyaml
6.0.1** (from `environment.json`) and **numpy 2.4.6** (recorded here, not in
`environment.json` — see deviation D16), Linux x86_64.

---

## 16. Scope statement

Tier **TOY**, `sota_delta` **zero** on every axis (time, memory, data/queries)
against every row of the prime-field frontier. p ∈ {4001, 6007}; the largest
prime factor of N is around 12 bits. **No functional measured here is an attack
cost at any scale, none is claimed to be, and no downstream citation may raise
the tier.** Lawful defensive cryptanalysis on public toy constructions only; no
live key, wallet or deployed system was touched. Nothing here adjudicates
`RQ-ICINV-475b5e`'s isogeny-class invariance question in either direction, bears
on `H-STR-002`, `H-ENDO-001` or `KN-FIND-b7e091`, or addresses the
density-independent within-class over-dispersion of `DEC-20260807-41c173` next
action N8, which is a different object handled by `EXP-ICINV-4d33aa`.
`GOAL-ENDO-001` pause condition P2 is not engaged.
