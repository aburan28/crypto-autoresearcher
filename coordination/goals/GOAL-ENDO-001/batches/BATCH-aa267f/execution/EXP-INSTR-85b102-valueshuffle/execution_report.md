# Execution report — CTRL-VALUESHUFFLE (EXP-INSTR-85b102 amendment v2)

| field | value |
|---|---|
| contract | `experiments/EXP-INSTR-85b102/amendments/v2.yaml` (`status: approved`, `approved_by: coordinator`, `approved_at: 2026-08-07`) |
| experiment | `EXP-INSTR-85b102` |
| control | `CTRL-VALUESHUFFLE` (change B1), stopping rule `SR-B1` (B2), metrics (B3) |
| hypothesis / question | `H-INSTR-fffbfb` / `RQ-INSTR-f8faa0` |
| goal / batch | `GOAL-ENDO-001` / `BATCH-aa267f` |
| role | Executor |
| branch | `claude/ecdlp-endomorphism-analysis-4m2w3z` (not pushed; no PR opened; `main` not merged) |
| runs | `RUN-INSTR-85b102-valueshuffle-gate`, `RUN-INSTR-85b102-valueshuffle` |
| **terminal state, emitted from inside the code** | **`STRUCTURE_PRESENT` (`state_2_STRUCTURE_PRESENT`)** |
| claim tier | **TOY.** `sota_delta` zero on every axis. No ECDLP claim either way. |

**What this report is.** Observations and deviations. It contains no
interpretation of what the numbers mean for `NULL-C`, `H-INSTR-fffbfb`, or
`GOAL-ENDO-001`; no evidence record; no hypothesis-status change; and no
statement that a heuristic is validated or refuted. Those are Coordinator and
Reviewer acts on a later archive (AGENTS.md rule 1).

**What this control is not.** Not an ECDLP attack, discrete-logarithm
computation, relation collection, solver run, or cost/exponent/speedup claim.
`certificate.kind: none` on both runs, **explicitly**: nothing here claims a
solve or a factor-base relation, so there is nothing to certify
(`docs/claims-and-verification.md`). The reproduction gate, the per-replicate
geometry-invariance assertions and the closed-form applicability assertions are
internal consistency checks and are reported as such.

---

## 1. Repository state and base-commit check

- `git fetch origin main` → `origin/main` = `3f88aa1c31ce76ad4e5eafa59674102917d1ed48`.
- `git merge-base HEAD origin/main` = the same sha; `git rev-list --count HEAD..origin/main` = **0**.
- **Merge outcome: nothing to merge.** `origin/main` is an ancestor of the
  branch head. No rebase, no push, no PR, no merge of `main` — branch sync and
  PR creation are the Coordinator's duties.
- Execution commits on the branch: `2c928d99` (gate + module) and the archival
  commit carrying this report.

## 2. What was authorized and what was run

The amendment adds exactly one control to a frozen v1 contract and withdraws
nothing. No version-1 run is re-scored; all 13 v1 run directories are
untouched. Two runs were executed against `maximum_runs: 6`:

| run | stage | what it did |
|---|---|---|
| `RUN-INSTR-85b102-valueshuffle-gate` | `--stage gate` | SR-B1 only. **Committed at `2c928d99` before a single replicate existed.** |
| `RUN-INSTR-85b102-valueshuffle` | `--stage control` | Re-ran SR-B1 as a blocking precondition, then drew the 200-replicate null and emitted the terminal state. |

All new code is in one new module, `harness/ctrl_valueshuffle.py`. Nothing in
`harness/run_blocknull.py` or in the eleven functions frozen by v1 was
modified.

---

## 3. SR-B1 — the reproduction gate. **PASS.**

Blocking, ran first, before any replicate was drawn. The frozen observed value
is 50 of 144; the gate compares three independent re-derivations against it and
never the reverse.

| derivation | total | POOL_A | POOL_B | POOL_C | POOL_D | comparable | full |
|---|---|---|---|---|---|---|---|
| **D1** committed `variance_ratio_R_empirical` | **50** | 10 | 10 | 16 | 14 | 138 | 144 |
| **D2** committed `variance_ratio_R_closed_form` (exact, zero MC error) | **50** | 10 | 10 | 16 | 14 | 138 | 144 |
| **D3** recomputed end-to-end from `per_curve.csv` + `rung_table.json` | **50** | 10 | 10 | 16 | 14 | 138 | 144 |
| frozen in the amendment / RT-20260807-743198 item 3f | 50 | 10 | 10 | 16 | 14 | — | 144 |

D3 is the **identity replicate**: the same code path the 200 shuffled
replicates use, with no permutation applied. It is the derivation that
certifies the null is measured by the same instrument as the observed value; D1
and D2 alone would not.

Additional gate checks, all passing:

- The restated verdict rule (`run_blocknull.py:1552`) agrees with the committed
  `ratio_rises_monotonically_along_N_ladder` boolean in **144 of 144** cells
  (36/36 at every pool).
- **Degeneracy is a suffix of the N ladder at all four pools**, so the residue
  construction (non-degenerate rungs only) compares exactly the ladder-adjacent
  pairs and never manufactures a comparison between non-adjacent rungs.
  Non-degenerate N-ladder rungs: POOL_A `[R0, R2]`, POOL_B `[R0, R2, R3]`,
  POOL_C `[R0, R2, R3, R4]`, POOL_D `[R0, R2, R3]`.
- The m = 3 family reproduces at **8 of 8** for `sumset_m3` and **8 of 8** for
  `sumset_eff_m3`.

**Both denominators, as `denominator_note` requires.** The residue count is
**50/144** and **50/138**. The six-cell difference is `s3_support`
weighted and unweighted at POOL_A, POOL_B and POOL_D, whose R is undefined at
every rung. **Which denominator the decision rule used: neither, in the sense
that matters — the frozen statistic is a COUNT.** 50 reproduces under both
(those six cells cannot be in the residue under either), and the null is drawn
over the identical 144-cell frame with the identical six vacuous cells
(`cells_comparable == 138` in all 200 replicates, `cells_vacuous == 6` in all
200), so the denominator does not enter the p-value at all. The count 50 over
the 144-cell frame is what was compared.

Artifact: `reproduction-gate.json`, byte-identical in both runs
(sha256 `0b6d69f413857d607a81f1ea2f0880acf9249a814b0ba3e910235d24d5477542`).

---

## 4. The null object

Held fixed, bit for bit, and **asserted per replicate rather than assumed**
(sha256 of each quantity, recomputed after every shuffle, at every pool):
the (trace, N) pairs, the class sizes, the per-curve class labels, and the
per-curve block assignment at **all seven** rungs. Permuted: the per-curve
values of one functional, uniformly at random across the whole pool,
independently per functional per replicate. The value multiset is checked
preserved by sha256 of the sorted value vector.

- **200 of 200 replicates: every invariant held. Zero violations.**
- **Closed form retained `exact` applicability at every ladder rung in every
  replicate** (`classes_within_blocks` true throughout).
- **No permutation study.** `B` is not a parameter of this control; the whole
  ladder was recomputed from `closed_form_null_mean` alone. No curve
  re-enumerated, no functional re-measured, no Monte-Carlo draw taken.

Pools, read from committed artifacts only:

| pool | source run | p | n curves | K classes |
|---|---|---|---|---|
| POOL_A | `RUN-INSTR-85b102-poolA-c` | 4001 | 472 | 4 |
| POOL_B | `RUN-INSTR-85b102-poolB-b` | 4001 | 1152 | 12 |
| POOL_C | `RUN-INSTR-85b102-poolC` | 4001 | 424 | 12 |
| POOL_D | `RUN-INSTR-85b102-poolD` | 6007 | 1464 | 12 |

---

## 5. The null distribution of the type-A residue count (B3)

n = 200 replicates.

| statistic | value |
|---|---|
| min | **89** |
| 5th percentile | 99 |
| 25th percentile | 104 |
| **median** | **108** |
| 75th percentile | 112 |
| 95th percentile | 116 |
| max | **123** |
| mean | 107.635 |
| sd | 5.632 |

(quantiles are nearest-rank order statistics, no interpolation, so each is an
actually-observed replicate value)

Full histogram (count of the 200 replicates at each residue count):

```
 89:1   94:2   95:1   97:1   98:2   99:5  100:7  101:11 102:9  103:10
104:12 105:14 106:12 107:9  108:16 109:8  110:13 111:12 112:13 113:10
114:11 115:8  116:5  117:2  118:2  119:1  120:1  121:1  123:1
```

Per pool (a decomposition of the above; **not** part of the frozen decision
rule, reported as an observation):

| pool | observed | null min | null median | null max | replicates ≤ observed |
|---|---|---|---|---|---|
| POOL_A | 10 | 9 | 20 | 27 | 2 of 200 |
| POOL_B | 10 | 20 | 28 | 34 | 0 of 200 |
| POOL_C | 16 | 27 | 33 | 36 | 0 of 200 |
| POOL_D | 14 | 19 | 27 | 33 | 0 of 200 |

---

## 6. The frozen decision rule, applied exactly

Statistic, frozen in the approved amendment before any replicate existed:

> Two-sided empirical p-value of the observed type-A residue count in the
> shuffled null, computed as `(1 + #{replicates at least as extreme}) /
> (1 + n_replicates)`, extremeness measured as `|x - median(null)|`.

| quantity | value |
|---|---|
| observed residue count | **50** (50/144; 50/138) |
| median of null | 108 |
| observed extremeness `\|50 - 108\|` | 58 |
| replicates at least as extreme | **0 of 200** |
| **two-sided empirical p** | **1/201 = 0.004975124378109453** |
| resolution floor at 200 replicates | 0.004975124378109453 |

`p ≤ 0.05` → the frozen rule emits **`state_2_STRUCTURE_PRESENT`**. The state
was written by `harness/ctrl_valueshuffle.py::decide` into
`decision-rule-evaluation.json`; it was not chosen afterwards.

**Direction, recorded because it is an observation.** The observed 50 lies
**below the entire null support** (null min 89). The frozen rule is two-sided
on `|x − median|` and fires without regard to direction; the direction is
reported and not discarded.

**The p-value is exactly at the resolution floor.** Zero of 200 replicates were
at least as extreme, so 0.004975 is the smallest value this design can produce.
The reported p is that floor, not an estimate of the true tail probability;
nothing smaller is resolvable at 200 replicates. This is the mirror image of
the contract's declared asymmetry and is stated with the same care.

**The declared asymmetry, restated verbatim from the contract because it binds
the reading of this number.** `state_1` (CONTROLLED_NULL) would have been a
positive finding about the **instrument**; `state_2` (STRUCTURE_PRESENT) is
**not** a finding about mathematics. Neither outcome supports any
GOAL-ENDO-001 hypothesis. A `p > 0.05` result would have meant NO STRUCTURE
DETECTED at 200 replicates, never "no structure exists". The state that did
fire "REMAINS AN INSTRUMENT FINDING AT TOY SCALE and licenses no claim about
isogeny-class structure or ECDLP cost."

**Evidence-strength cap, from the contract.** Any evidence record arising from
this control is capped at `preliminary` and `claim_tier: toy` regardless of
outcome, and under AGENTS.md rule 12 the contradiction between a validated
execution report and an independent review already requires further independent
review before **any** evidence record is written from this line of work. This
report writes none.

---

## 7. The m = 3 family indicator (B3), reported separately

Residue indicator over the 8 cells (4 pools × 2 statistics) of each functional.
**This quantity does not enter the terminal state**, which the frozen rule keys
to the residue count alone. The frozen two-sided formula is applied for
consistency and the one-sided upper-tail count is reported beside it.

| functional | observed | null median | null max | null histogram (of 200) | two-sided p | one-sided upper p |
|---|---|---|---|---|---|---|
| `sumset_m3` | **8 of 8** | 6 | 8 | 3:6, 4:19, 5:33, 6:55, 7:60, 8:27 | 0.263682 | 0.139303 |
| `sumset_eff_m3` | **8 of 8** | 6 | 8 | 3:4, 4:11, 5:27, 6:60, 7:62, 8:36 | 0.258706 | 0.184080 |

Observation, without interpretation: under the shuffle, `sumset_m3` reaches
8 of 8 in 27 of 200 replicates and `sumset_eff_m3` in 36 of 200. At 200
replicates the observed 8-of-8 is not separated from the shuffled null by
either statistic.

Per-functional residue, observed against null, all 24 functionals. Observed
counts are this run's own D3 re-derivation
(`reproduction-gate.json -> observed_cells.by_functional`, summing to 50); null
means are over the 200 replicates (`valueshuffle-null.json ->
per_functional_null_mean_residue`). Cell counts differ by functional: 8 for
those present at both primes, 6 for `liftable_density` windows only at
p = 4001, 2 for those only at p = 6007.

| functional | observed | null mean | null range |
|---|---|---|---|
| `sumset_m3` | **8/8** | 6.12 | [3, 8] |
| `sumset_eff_m3` | **8/8** | 6.37 | [3, 8] |
| `decomp_efficiency_m2` | 6/8 | 6.11 | [1, 8] |
| `decomp_rate_m3` | 6/8 | 6.01 | [2, 8] |
| `decomp_efficiency_m3` | 5/8 | 6.14 | [3, 8] |
| `two_torsion_x` | 4/8 | 6.33 | [2, 8] |
| `decomp_rate_m2` | 2/8 | 6.08 | [3, 8] |
| `sumset_m2` | 2/8 | 6.30 | [3, 8] |
| `sumset_eff_m2` | 2/8 | 6.28 | [3, 8] |
| `s3_support` | 2/8 | 1.65 | [1, 2] |
| `order` | 0/8 | 6.34 | [2, 8] |
| `full_liftable` | 0/8 | 6.36 | [3, 8] |
| `liftable_density_W1000` | 2/6 | 4.62 | [2, 6] |
| `liftable_density_W2000` | 2/6 | 4.70 | [1, 6] |
| `liftable_density_W125` | 1/6 | 4.58 | [1, 6] |
| `liftable_density_W250` | 0/6 | 4.66 | [2, 6] |
| `liftable_density_W500` | 0/6 | 4.61 | [1, 6] |
| `liftable_density_W4001` | 0/6 | 4.78 | [2, 6] |
| `liftable_density_W187` | 0/2 | 1.55 | [0, 2] |
| `liftable_density_W375` | 0/2 | 1.65 | [0, 2] |
| `liftable_density_W750` | 0/2 | 1.56 | [0, 2] |
| `liftable_density_W1501` | 0/2 | 1.64 | [0, 2] |
| `liftable_density_W3003` | 0/2 | 1.57 | [0, 2] |
| `liftable_density_W6007` | 0/2 | 1.65 | [0, 2] |

These observed per-functional counts are the **residue** construction
(non-degenerate rungs only) and are therefore NOT the same numbers as the
full-ladder table in RT-20260807-743198 item 3a, which counts all reversals
including type B. They sum to 50.

The N-coupled functionals — `order` (= N), `full_liftable` (= (N−1+z)/2) and
`liftable_density` at the full-field window (`W4001` at p = 4001, `W6007` at
p = 6007) — are **0 of 8, 0 of 8, 0 of 6 and 0 of 2** observed, and have null
mean residue **6.34, 6.36, 4.78 and 1.65** under the shuffle. **This is what
the null object is built to do** — it destroys every value–N association — and
is recorded as a property of the control, not as a result.

---

## 8. Budget, measured

All numbers below are **measured**, from `resource.getrusage` and the wall
clock recorded in each manifest. None is modelled.

| quantity | gate run | control run | total | contract limit |
|---|---|---|---|---|
| wall seconds | 0.997 | 55.463 | 56.46 | 3600 per run |
| CPU seconds | 1.247 | 55.759 | 57.01 | 1 CPU-hour = 3600 s |
| peak RSS | 79.3 MB | 81.6 MB | — | 4 GB (`RLIMIT_AS` applied, verified in the manifest) |
| runs | 1 | 1 | **2** | 6 |

The null itself took **54.692 s for 200 replicates** = 0.273 s per replicate.
Total CPU 0.0158 CPU-hours against a 1 CPU-hour budget. The contract's
`budget_note` projected "about 1.6 CPU-minutes, under 10 CPU-minutes in total"
from RT-20260807-743198's measured 0.631 ms per closed-form call; the realized
cost is 0.95 CPU-minutes, inside that projection. No budget, timeout or memory
limit was approached, and no run was aborted.

---

## 9. Independent verification performed after the run

Read-only checks against the emitted artifacts. Each is restated so a reviewer
re-runs it rather than trusting it.

1. **The decision statistic recomputed from the raw per-replicate records.**
   Median of `[r["residue_count"] for r in valueshuffle-null.json["records"]]`,
   count of `|x − median| ≥ |50 − median|`, `(1+k)/(1+200)`. Result
   `0.004975124378109453`, agreeing with `decision-rule-evaluation.json` to
   double precision.
2. **Per-replicate bitmap consistency.** Every replicate's 144-character
   `cell_bitmap` has length 144 and a popcount equal to its `residue_count`;
   200/200.
3. **Per-pool sums.** `sum(by_pool.values()) == residue_count` in 200/200.
4. **End-to-end re-run of one replicate.** Replicate 137 recomputed from
   `derive_shuffle_seed(137, pool, functional)`: residue count 100 against the
   recorded 100, and the **144-cell bitmap identical**. Each functional's
   shuffled vector was checked to be a genuine permutation
   (`sort(shuffled) == sort(original)`).
5. **Forced value at degenerate rungs.** At a degenerate rung every block is a
   single class, so `E[T_pi | B] = T_obs` and `R = 1`. Measured
   `max |R − 1| = 4.440892e-16` over 258 degenerate rung-cells in the new code
   path — the v1 `R5_PERCLASS` invariant, re-checked here.
6. **Agreement with the committed v1 cells**, over all 4 × 180 = 720 ladder
   cells: `closed_form_null_mean` reproduces **bitwise** (max relative
   deviation `0.000e+00` at every pool); `T_obs` reproduces to a few ulp
   (max relative deviation 2.255e-16 / 2.756e-16 / 5.274e-16 / 3.439e-16 at
   POOL_A/B/C/D) against a verdict tolerance of 1e-12 on ratios of order 1.
7. **Source provenance (N6).** `python3 tools/check_run_source_provenance.py
   --experiment EXP-INSTR-85b102` → "2 pinned, 13 unpinned, 0 unreadable, of 15
   run manifest(s) in scope". The two pinned are this control's two runs; the
   13 unpinned predate the N6 fix and are unchanged by this work. The control
   run additionally records `all_clean: true` — the recorded commit `2c928d99`
   alone reproduces it.

---

## 10. Deviations from the approved protocol

Full detail in `implementation.md` in this directory. Summary:

| id | deviation / decision |
|---|---|
| D1 | The contract freezes three seeds and 200 replicates but no mapping between them. Resolved by a SHA-256 derivation consuming **all three** seeds per `(replicate, pool, functional)`, fixed before any replicate was drawn and restated exactly so any single shuffle reproduces. |
| D2 | Two runs rather than one: a standalone SR-B1 gate run committed before any replicate existed, plus the full control run that re-runs the gate as a blocking precondition. Within `maximum_runs: 6`. |
| D3 | The verdict rule is an inline expression at `run_blocknull.py:1552`, not a callable, so it is restated in the new module — and cross-checked against the committed booleans in 144/144 cells. The vacuous `all()` (OBJ-3) is reproduced **deliberately**, not repaired: the amendment says fixing it needs its own amendment. RC-2, RC-3 and RC-4 were not implemented. |
| D4 | Closed forms computed at all five N-ladder rungs though only the non-degenerate prefix is used, so the degenerate rungs serve as a forced-value check. |
| D5 | `T_obs` recomputed through the frozen scalar statistics rather than the v1 vectorized path; agreement measured, not assumed (section 9 item 6). |
| D6 | Both denominators reported; the statistic is a count, so the denominator does not enter the p-value. |
| D7 | No permutation study, no re-measurement, no frozen function modified; regenerated CTRL-FROZEN-DIFF reads ZERO BEHAVIOURAL CHANGE with all eleven frozen functions UNCHANGED. |
| D8 | Nothing else. No frozen number adjusted, no run repeated or discarded, no status moved, no evidence record written. |

**Unexpected observations** (U1–U4 in `implementation.md`): the observed value
lies below the entire null support; the p-value sits exactly at the resolution
floor; the m = 3 family's 8-of-8 is not separated from the null; and the
N-coupled functionals lose their coupling under the shuffle by construction.

**No infrastructure failure, timeout, crash or OOM occurred.** No run is
`failed_infrastructure`. No run is `invalid`.

---

## 11. Scope statement

Tier **TOY**. p ∈ {4001, 6007}, four pools of 424–1464 curves in 4–12 isogeny
classes. This is an **instrument characterisation** of the N-band blocking
ladder of `EXP-INSTR-85b102`. It computes no discrete logarithm, collects no
relation, runs no solver, and makes no cost, exponent or speedup claim.
`sota_delta` is **zero on every axis** (time, memory, data/queries);
`dominated_by` is not applicable because no method is claimed. Nothing here
bears on `EXP-ICINV-4d33aa`, `EV-ENDO-10109d`, `RQ-ICINV-475b5e`, `H-STR-002`,
`H-ENDO-001` or `KN-FIND-b7e091`. The emitted terminal state is a statement
about where one count falls in one shuffled null at these four toy pools, and
nothing wider.

---

## 12. Artifacts

Run package — `experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-valueshuffle/`:

- `manifest.yaml` (with `code.source` pins, N6; `all_pinned: true`, `all_clean: true`)
- `raw-result.json` (includes every per-replicate record and the full gate)
- `reproduction-gate.json`
- `valueshuffle-null.json`
- `decision-rule-evaluation.json`
- `frozen_function_diff.txt`, `frozen_function_diff.json`
- `command.txt`, `environment.json`, `stdout.log`, `stderr.log`

Gate run — `experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-valueshuffle-gate/`:
same package minus the null and decision artifacts.

Code: `harness/ctrl_valueshuffle.py` (new module; nothing else touched).

Reports: this file and `implementation.md`, in
`coordination/goals/GOAL-ENDO-001/batches/BATCH-aa267f/execution/EXP-INSTR-85b102-valueshuffle/`.

Exact commands:

```
python3 -m harness.ctrl_valueshuffle --stage gate    --replicates 200 \
    --suffix 85b102-valueshuffle-gate --max-seconds 3600
python3 -m harness.ctrl_valueshuffle --stage control --replicates 200 \
    --suffix 85b102-valueshuffle      --max-seconds 3600
```

---

## 13. Executor assessment

- `protocol_complete: true` — SR-B1 ran first and passed; the null ran at the
  frozen 200 replicates with zero invariance violations; the terminal state was
  emitted from inside the code by the frozen rule.
- `data_quality: good` — the deciding quantity is a closed form that reproduces
  bitwise against the committed v1 cells, and one replicate re-runs bit for bit.
- `requires_rerun: false`.

The one resolution limit worth the Reviewer's attention: **p sits exactly at
the 1/201 floor**, so the design distinguishes "at least this extreme" from
nothing smaller. The residue count and the m = 3 indicator are separate
quantities with separate nulls and only the first enters the terminal state.
