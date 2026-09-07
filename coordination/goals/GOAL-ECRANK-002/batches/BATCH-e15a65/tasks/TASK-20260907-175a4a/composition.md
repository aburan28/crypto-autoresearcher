# Composition of BATCH-e15a65 — the two blinded reviews of EXP-ECRANK-73275e v1

- **Task**: TASK-20260907-175a4a (Coordinator, `coordinator-orchestration-code`, effort high)
- **Goal / question / batch**: GOAL-ECRANK-002 / RQ-ECRANK-27dcc5 / BATCH-e15a65
- **Frozen review plan**: `ledger/decisions/DEC-20260907-9953c0.yaml` (`REVIEW-PLAN-BATCH-e15a65`)
- **Second, earlier frozen prior**: `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/coordinator-prior-20260907T174252Z.md` (17:42:52Z, commit `10a0aacd7`)
- **Package composed over**: `experiments/EXP-ECRANK-73275e/` version 1, eight runs, snapshot commit `03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad`
- **Reports composed**:
  - `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-d47eb0/validation-report.md` (Validator, J1–J4)
  - `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-46731e/redteam-report.md` (Red Team, J5–J7 + proves-too-much)
- **Authority of this file**: a DRAFT composition. It changes no status, promotes nothing, writes no ledger path, and commits nothing. `H-ECRANK-36d8d7` stays `specified`; HEUR-1 is neither supported nor refuted; C1 stays OPEN with the `DEC-20260905-7adca0` candidate UNPROMOTED; IMP-2 is untouched. Nothing here is durable until the ledger archive `TASK-20260907-f5e45b` commits and the post-commit verifier accepts.

**Reading order note.** The four sections below are strictly separated. **Observation** contains only facts quoted from a named artifact. **Comparison** places the two reports and the two frozen priors beside each other and states where they differ. **Inference** contains every judgement I make, and its first item — §I.0 — is the validity determination, which is reached before any scientific interpretation and on which everything after it depends. **Limitation** states what this round could not see. No inference sentence appears in Observation.

---

# OBSERVATION

Every number in this section is quoted from the artifact named beside it. No judgement is offered here.

## O.1 The producer's own position

`experiments/EXP-ECRANK-73275e/execution-report.yaml` sets `interpretation: none` and its `report_scope_statement` declines to map the recorded facts to the frozen success criterion. The producer assigned no F1–F4 label and stated no claim.

## O.2 Receipt-level facts (Validator, J1/J2)

Quoted from `.../TASK-20260907-d47eb0/validation-report.md`:

- `git diff --stat 03c6e3181..HEAD -- experiments/EXP-ECRANK-73275e/` is **empty**; snapshot receipt `path_sha256` recomputed **60 matched, 0 mismatched, 0 missing**; `runs/` has **exactly one commit**; `experiments/EXP-ECRANK-73275e/amendments/` does not exist; post-design edits to `specification.yaml` touched **only** `status`, `approved_by`, `approval_note`.
- All eight `manifest.yaml` carry the nested `run:` mapping with **0 missing** `RUN_REQUIRED_TOP` fields; all five companions present in all eight; `command.txt` string-equal to `run.code.command` 8/8; `environment.json` byte-identical across all eight (sha256 `6c893fe431007f6e…`, CPython 3.12.3, Linux-6.12.94, `stdlib_only_pipeline: true`, `pari_in_pipeline: false`, `network: "none"`).
- `run.code.source_sha256` recomputed for the eight `source/*.py`: **8/8 match**. `code.commit` = `5b83fed02e40d5a2aea939220ff34e2ef4961f6b` in all eight. `code.dirty: true` in all eight resolves to exactly two **untracked** entries, `?? coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/claims/` and `?? experiments/EXP-ECRANK-73275e/runs/`.
- Seeds: R3 760806, R4 760806, R5 760810, R7 760812, R8 760808 — each a literal member of `replication.seeds`. **No derived seed exists anywhere in the package**; the predecessor's `Random(seed*1000 + index)` pattern does not recur. R6 records `seed: 760806`, which `replication.seeds_note` assigns to no run; R6's `coset_V` is `[0, 1, 28, 29, 64, 65, 92, 93]`, identical to R3's.
- Raw versus summary: **zero numeric disagreements** between `execution-report.yaml` and the named raw records, across all eight `counted_exact_ops`, all eight `ops_cap_respected`, all sixteen `wall_seconds_*`, all eight `peak_rss_bytes`, and every R1–R8 observation field.
- Op ledger, recomputed as the exact boolean `counted_ops < 1.0e8` with no band: R1 0, R2 0, R3 9 191 003, R4 9 191 003, R5 100 002 120, R6 37 416, R7 308 732, R8 6 751. **Recorded boolean equals recomputation in 8 of 8**; `false` for R5 alone. R5's stop is recorded as `exhaustion: {"kind": "counted_ops_cap", "ops": 100002120, "b_index": 666}`, `n_b_done: 667` of `n_b_declared: 10000`, and never as a result.
- R5 carries **1 checkpoint** (`ckpt-001-final.json`, a terminal checkpoint) against the **10** the 1e7-counted-op cadence of `stopping_rules` and `required_artifacts` implies. This is disclosed by no PD.
- `wall_seconds_monotonic` and `wall_seconds_timestamp_span` are identical in six runs and differ by 1e-6 in two: R4 `18.257394 / 18.257395`, R5 `75.686747 / 75.686748`.
- `resources.cpu_seconds` is `null` in all eight runs.
- R3 versus R4: `raw-result.json` key sets differ by exactly four keys (`iv2_counts_identical`, `iv2_instance_list_identical`, `iv2_ops_r3`, `iv2_ops_r4`); on the intersection **every key is equal**, `found` deep-equal over all 28 instances; `checkpoints/ckpt-001-final.json` sha256 `a6ae120aafd975d35689fad92bf833747a5b201cc5be52fd3162080b88cd4ecc` identical in both; `stdout.log` sha256 `68a499ffb459337bde19a483eb51acb4255dd7fd60cb7c36c8da8d297fe3612c` identical in both.
- `counts_per_H` recomputed independently from each run's own `found` list as the cumulative count of instances with `r_height <= H`: `{100: 15, 1000: 22, 10000: 28}` for **both** R3 and R4.
- The SR-11 IC-1 exclusion ledger is **absent** from every run record and from `execution-report.yaml`.

## O.3 Recorded control outcomes (Validator, J3 — quoted from raw records, not the report)

| Control | Recorded outcome (raw artifact) | Validator verdict | Frozen consequence |
|---|---|---|---|
| IV-1 | R7 `results["6"].per_b`: 8 entries, every one `{"built": false, "reason": "degenerate_deg_s_2"}`, `all_match: false`, `expected: 5`. `results["8"].per_b`: 8 entries all `built: true`, `aggregate_total` `[5, 6, 7, 7, 7, 7, 6, 7]`, `expected: 7`, mismatches at indices 0, 1, 6 | **NOT SATISFIED overall**; n = 6 branch **NOT EVALUATED**, n = 8 branch **NOT SATISFIED** | "IV-1 failure voids ALL runs of this experiment" |
| IV-2 | R3/R4 equal on every shared key; `found` deep-equal over 28; `ops` 9 191 003 both | **SATISFIED** on all three required objects | does not fire |
| IV-3 | R8 `plants` 9 entries all `{"built": false, "h0": null, "r": null, "reason": "degenerate_deg_s_2"}`; `recovered: []`; `cells {100:0,1000:0,10000:0}`; `decade_ratios: {}`; `log_log_slope: null`; the frozen windows `[0.699, 1.301]` and `[5, 20]` recorded and never applied | **NOT EVALUATED** | the frozen rules branch on IV-3 *failure* and carry **no branch for a control that never evaluated** |
| IV-4 | R6 `found: []`, `counts_per_H {"10000": 0}`, `feasible_tuples: 0`, `n_b_declared: 64`, `n_b_done: 64`; `null_proof_first: null`, no other proof or flag field | conjunct 1 **SATISFIED**, conjunct 2 **NOT EVALUATED in the run record** | "IV-4 failure voids every count" |
| IV-5 | R1 `b_tuple_mismatches: []`, `reconstruction_bit_identical_replay: true`, 1 row at `b_index 0` with 8 draws, `in_box_fraction 1.0`, `r1_planted_2d {H:20, N_a:8000, S_abs:1600, expected_meets:5.0, meets_observed:5, plant:[1,2]}`, `audit_source_commit_bound: a20a49b6adbcce51893c1221dbd69cdcd486ad9d` | **SATISFIED**, at the scope of one b-tuple and 8 draws | voids R2 only; does not fire |
| IV-6 | one attempt directory, `R1/attempt-1-precommit-smoke/` with `NOTE.txt`; no 13th-attempt refusal | **SATISFIED** on the ceiling; "every attempt preserved" **NOT EVALUABLE** | none |
| IV-7 | R3 ≡ R4; R2 `reconstruction_bit_identical_replay: true`; no replay for R1, R5, R6, R7, R8 | **SATISFIED for R3/R4 and R2; NOT EVALUATED elsewhere** | none stated |
| IV-8 | all 28 R3 certificates `n_classes: 3`, `verdict: "PASS"`, max 3, no 4-class instance; R5 `found: []`; R3 top-level keys carry **no** multi-class or untested field | **NOT SATISFIED** — branch 1 fails, branch 2 fails *in the run record* | "the certification claim is downgraded to single-class" — a downgrade, not a voiding |
| IV-9 | R2 `r2_plants` h0 = 7, 11, 13 distinct; R8 9 distinct b-tuples but 1 distinct pattern (all `[1,1,1,1,1,1]`) and all nine `h0` `null`, with `iv9_distinct_h0: true` | **SATISFIED for R2**; R8 (b, pattern) clause satisfied, h0 clause **NOT EVALUATED** and the recorded `true` vacuous | none |

## O.4 Blind re-derivation outcome (Validator, J4)

- Outcome recorded: **NOT DERIVABLE**. Seven definitional gaps G1–G7 (the family `g`; the ellipticity condition; the square pattern's enumeration; the height-H box; "certified rank above the trivial"; "twist class populated"; the distinct-minimal-model dedup key), plus an unfixed `random.Random(760806)` call order among the four consumers `replication.seeds_note` names.
- Committed blind prediction: first b-tuple `(0, 1, 4, −7, −1, −2)`, stream sha256 `b1e62603e99983565d65b38297be7c20eeddef3e6eb352bf89d5ff87c1fafeda` under conventions C1/C3/C5. The record's `found[0]` is `b_index: 579`, `instance.b = ["0","1","7","-14","16","-2"]`; blind-stream agreement **0/28**; the 4-set `{7, −14, 16, −2}` appears nowhere in the 10⁴-draw stream. A bounded search of **375 conventions** (3 pool orderings × 5 stdlib generators × 25 burn-in offsets) reproduces `b_index 579` under **none**.
- Four structural predicates committed blind and checked afterwards: P-a `20/10⁴ = 0.002` exactly and distinct `b_index` among the 28 = 20 = `feasible_tuples`; P-b the ≤ 2-rational-roots ceiling gives N₆ ≤ 40 and requires ≥ 8 tuples contributing two instances — the record shows **12 tuples × 1 and 8 tuples × 2**; P-c `15 ≤ 22 ≤ 28`; P-d measured decade ratios `22/15 = 1.467` and `28/22 = 1.273`, implied exponents 0.166 and 0.105, against the pre-registered exponent **+2** (×100 per decade).

## O.5 Control-mechanism facts (Red Team, J5 — four independent computations from committed bytes)

- **(T1)** `E.mestre_polys` (`source/ecrank_engine.py:394`) sets `g = polysqrt_trunc(p, k)`, so `deg s = deg(g² − p) ≤ k − 1 = n/2 − 1`; at n = 6 that is `deg s ≤ 2`. `E.build_instance` accepts only `deg ∈ {3, 4}` and otherwise returns `degenerate_deg_s_%d` (`ecrank_engine.py:806–808`).
- **(T2)** At `d = (1,…,1)` the interpolant `δ = lagrange_interp(xs, [1]*n)` is the constant polynomial 1, so `s = δ·g² mod p = (x+t)²` and the x⁵ coefficient vanishes identically; the n = 6 ellipticity quadratic has `(A, B, C) = (0, 0, 0)`. `NF.d1_quadratic_coeffs` (`source/null_family.py:20–47`) returns `(0,0,0)`; `construct._quad_rational_roots(0, 0, C)` returns `[]` (`construct.py:116–118`).
- **C-A** (independent code): `deg s = 2` on all 9 R8 b-tuples, `deg s = 2` on all 8 re-derived R7 n = 6 tuples, `deg s = 3` on all 8 re-derived R7 n = 8 tuples; sweep of 3000 random tuples per n gives n = 6 `{deg 2: 2999, deg 0: 1}` — **never 3 or 4** — and n = 8 `{deg 3: 2994, deg 2: 6}`.
- **C-D** (independent code): `(A, B, C) = (0, 0, 0)` on **all 64** R6 tuples, δ of degree 0. R6 never reaches `build_instance` and never reaches the certifier (`certifier=None` when `null_family=True`, `run_experiment.py:134–139`).
- **C-B** (independent code, from `found` in R3's raw record): **28/28 pass 10 checks each** — ellipticity, `s` reproduced exactly, `deg s ∈ {3,4}` (all 4), every `r_i ≠ 0`, `disc(s) ≠ 0` and equal to the recorded `disc_s`, the forcing identity `s(b_i) = d_i·r_i²`, the M2 identity `δ·g² ≡ s (mod ∏(x−b_i))`, `r_height` reproduced, base-class points `(b_i, r_i)` on `v² = (s/d1)(u)`, and exactly 2 rational base-class points. **28 distinct base-class j-invariants, 0 collisions.** `counts_per_H` recomputed from the recorded r-heights alone: `{100: 15, 1000: 22, 10000: 28}`.
- **C-C**: 20 feasible tuples produce **34** candidate rational roots (14 with 2 roots, 6 with `A = 0` and 1 root) → **28 kept, 5 rejected `r_height > 10⁴`, 1 rejected `r_zero`, 0 unexplained**; none of the 6 rejections appears in the record (`near_miss_total: 0`).
- **Stage coverage** (from committed source): the counted path is S1 `sample_b` → S2 `sample_dpat` → S3 `_n6_quad` → S4 `_quad_rational_roots` → S5 r-construction and height filter → S6 `build_instance` → S7 multi-class `certify_instance` → S8 counting. `construct._n6_quad` (`construct.py:98–111`) is executed by **no run in the package other than R3 and its bit-for-bit replay R4**, because `solve_n6` branches on `all(int(d) == 1 for d in dpat)` (`construct.py:74–75`) and every control uses `d = (1,…,1)`. R3's `coset_V` is `[0,1,28,29,64,65,92,93]` with observed member values `{±22, ±286, ±2310, ±30030}` — **1 is not a member** — while R7 selects `next(c for c in cosets if 1 in [...])` (`run_experiment.py:187–188`).
- All 8 R7 n = 8 certificates record `n_classes: 1`; all 28 R3 certificates record `n_classes: 3`.

## O.6 Cost, assumption and scope facts (Red Team, J6)

- `Bbox = min(int(H), 20)` (`construct.py:294–305`, `implementation.md` IC-732-3) makes the two declared n = 8 H levels the **identical** enumeration; 41² = 1681 integer points against ≈ 12 175² rationals of height ≤ 100 (≈ 1.1e−5 coverage) and ≈ 1.1e−9 at H = 1000. `grep -c "coeff_box_B\|scope_note"` returns **0** in R5's `raw-result.json`, `manifest.yaml`, `stdout.log`, and **0** across the whole `runs/` tree.
- R5 consumed 100 002 120 counted ops over 667 tuples = 149 928 ops/tuple; completing the declared 10 000-tuple sample needs ≈ **1.50e9 counted ops = 15.0× the frozen per-run cap**, at ≈ 1135 s wall against a 7200 s per-run budget.
- `counted_ops` wraps only the listed Fraction dunder operations plus `pow` and `isqrt` (`ecrank_engine.py:264–300`); it does not count Fraction construction and its gcd, comparisons, negation, `abs`, integer arithmetic or list work. R1 and R2 record `counted_exact_ops: 0` while consuming 0.324303 s and 0.313583 s of wall clock.
- `ops_cap_respected` is computed after the run as `counted_ops < 1.0e8` (`run_common.py:172`) while the stop rule breaks at `ops_count() >= OPS_CAP` (`construct.py:308, 370`), so any run the stop rule fires on necessarily records `false`.
- Σ per-run wall = 113.720816 s against 113.741739 s from R1 start to R8 finish. All eight runs executed in **one process** (`started_at` 2–3 ms after the previous `finished_at`); `peak_rss_bytes` is `resource.getrusage(RUSAGE_SELF).ru_maxrss`, and six runs record the byte-identical `30867456`.
- `execution-report.yaml`, `runs/` and `implementation.md` scanned for `HEUR-1 | supports | confirms | demonstrat | validates | proves | cryptograph | rank over | C1` return exactly one hit: `implementation.md:6`, "no HEUR-1 verdict".
- `specification.yaml metrics.secondary` names "the **3e-4/draw** draw-route upper bound of EV-ECRANK-8b35bb"; `EV-ECRANK-8b35bb obstruction.value` states "rule-of-three 95% upper bound **< 3e-4 instances per b-tuple at n=8 (3/10⁴)**", and its `observations` record "arm A (n=6, seed 760706) 1,000 seeded b-tuples … 0 constructed instances". The per-draw figure from the same record (0 of 80 000) is 3.75e−5; the same-n rule-of-three per-tuple bound is 3.0e−3; R3's measured per-tuple incidence is 28/10⁴ = 2.8e−3.
- `construct_arm` records only `{verdict, aggregate_total, n_classes, class_keys}` per instance (`construct.py:406–411`): **no a-invariants and no curve points are persisted in any R3 artifact.**

## O.7 Recorded R1/R2 audit numbers bearing on G1

From `execution-report.yaml` R2 `observations_quoted`, verified by the Validator against the raw record with zero disagreement: `inbox_fraction: 1.0`, `n_draws: 24`, `n_in_box: 24`; planted meets `{at 0, plant [7,8], meets_observed 3}`, `{at 1, plant [11,12], meets_observed 3}`, `{at 2, plant [13,14], meets_observed 4}`, each with `expected_meets: 5.0`, `S_abs: 1600`, `N_a: 8000`.

---

# COMPARISON

## C.1 Joint verdicts, each attributed to its single owner

| Joint | Owner | Verdict | One-line content |
|---|---|---|---|
| J1 run-record integrity, schema, seeds, raw/summary | TASK-20260907-d47eb0 (Validator) | **holds** | 60/60 content-verified, schema-complete 8/8, no derived seed, zero numeric disagreements; ten named defects, four of them absent `required_artifacts` |
| J2 reproducibility and op accounting | TASK-20260907-d47eb0 | **holds** | R3 ≡ R4 on instance list, counts and ops; `iv2_counts_identical: false` resolved as a defect in the **check**, not the run; `ops_cap_respected` exact 8/8; two defects (R5 cadence 1 of 10, SR-11 absent) |
| J3 IV-1…IV-9 against frozen text | TASK-20260907-d47eb0 | **breaks** | IV-1 not satisfied (n = 6 NOT EVALUATED, n = 8 not satisfied); IV-3 NOT EVALUATED; IV-4 conjunct 2 absent; IV-8 not satisfied; the frozen rules have no branch for a control that never evaluated |
| J4 blind re-derivation of N₆(H) | TASK-20260907-d47eb0 | **breaks** | N₆(H) not derivable from the frozen contract; 28 has no independent check behind it; **not** shown to be wrong |
| J5 do the controls discriminate | TASK-20260907-46731e (Red Team) | **breaks** | none of R6, R7(n = 6), R8 could have failed; the counted path and the control path are different code paths |
| J6 hidden assumptions, cost, scope | TASK-20260907-46731e | **breaks** on (a) and (c), holds with material caveats on (b) | 7 hidden assumptions; R5 measured a different quantity; the P4 comparison swaps n; the count is not H-driven |
| J7 cheapest falsification control | TASK-20260907-46731e | **holds** | ranked costed list; three items computed from committed bytes and run; the plan's own item (i) shown non-computable with a stated successor requirement |

Neither reviewer returned a whole-claim verdict; each states explicitly that four (respectively three) of seven joints are invisible to it by construction.

## C.2 The ten numbered prior expectations of `DEC-20260907-9953c0`, answered item by item

| # | Prior expectation | Outcome | Owner of the finding |
|---|---|---|---|
| 1 | J1 finds the set formally complete, plus one provenance defect (`cursor-grok-4.6`, `model_verified: false`, `fallback_used: true`, `git_dirty_at_runs: true`) | **Upheld on completeness; PARTLY OVERTURNED on the defect.** `fallback_used: true` is **contract-permitted** — `ledger/handoffs/TASK-20260907-2a3331.yaml` sets `fallback_allowed: true` with a recorded reason and `degraded_requirements: []`. `git_dirty_at_runs: true` resolves to two untracked **output** directories with all eight `source_sha256` verified. **Only `model_verified: false` survives as a live concern.** | Validator J1 |
| 2 | R4 ≡ R3; the producer's int-vs-str dict explanation for `iv2_counts_identical: false` is correct — "the place I most expect to be wrong" | **Upheld, and established independently rather than accepted.** `counts_per_H` recomputed from each `found` list; `found` deep-equal ⇒ no divergence is possible. The producer's *mechanism* lives in `blind_from` and remains **UNVERIFIED**. | Validator J2 |
| 3 | `ops_cap_respected` exact, false for R5 alone; R5's `found: 0` inert in both directions | **Upheld, 8/8**, with a defect the prior did not anticipate: **R5 carries 1 of its 10 required 1e7-cadence checkpoints, undisclosed by any PD.** | Validator J2 |
| 4 | IV-1 is where the round breaks; IV-1 as frozen is NOT satisfied | **Upheld on the bottom line; refined by both reviewers in different directions.** See §C.4. | Validator J3 + Red Team J5(a) |
| 5 | IV-3 and R8 did not discriminate | **Upheld and strengthened to NOT RUN and *could not have passed***: by (T2) the recovery call `solve_n6(E, b, [1]*6, 10⁴)` returns `[]` for every b even had the 9 plants built. | Red Team J5(c), Validator J3 |
| 6 | The R6 zero is weaker than it looks; `degenerate_deg_s_2` is a live alternative explanation | **Upheld on weakness, and CORRECTED on the mechanism.** R6 is *vacuous*, not merely weak: `(A,B,C) = (0,0,0)` on all 64 tuples and the solver returns before anything is built. The prior's proposed alternative is **wrong** — R6 never calls `build_instance`. The frozen infeasibility proof in `null_family.py` (`A·C_null > 0` and `B² − 4AC_null < 0`) is **false of the object that ran** (both quantities are 0). | Red Team J5(b) |
| 7 | PD-3 is material; R5 did not measure the contracted quantity | **Upheld and quantified**: `min(H,20) = 20` collapses both declared H levels into one enumeration; 1681 integer points against ≈1.1e−5 (H = 100) and ≈1.1e−9 (H = 1000) of the declared rational box; the true solution variety is generically non-integral so the expected yield is ≈ 0 whatever the op budget. | Red Team J6(a) |
| 8 | J4 reproduces 15 / 22 / 28 and 0.002 from the contract alone — "the one I would most like overturned" | **OVERTURNED.** No such reproduction is possible: gaps G1–G7 plus an unfixed RNG call order; 375 conventions fail to reproduce even the b-tuple at `b_index 579`. **It was not shown that 28 is wrong.** | Validator J4 |
| 9 | At least one cost-model gap; both `wall_seconds` forms identical to six decimals in **every** run | **Premise FACTUALLY CORRECTED by both reviewers independently** (R4 and R5 differ by 1e−6; six of eight agree). **Substance upheld and strengthened**: they are two clocks over one interval sampled one statement apart, so SR-10 is literally satisfied and purposively empty; the load-bearing missing quantity is `cpu_seconds`, `null` in all eight by design, beside a non-per-run RSS and a `counted_ops` that is a lower bound of unstated looseness. | Validator J2 + Red Team J6(b) |
| 10 | The prior is overturned as a whole if the R3 28 were produced by a code path the controls never traverse | **THE STATED OVERTURNING CONDITION HOLDS.** `construct._n6_quad`, which produces every counted instance, is executed by no run but R3 and its replay R4; the counted arm and the known-false control run over **disjoint cosets**. | Red Team J5(d), BLOCK-5 |

The earlier 17:42:52Z prior's items map onto the same findings: its IV-1 and IV-3 expectations are upheld, its symmetric-trap alternative (a) is resolved in §C.4, its alternative (b) (aggregate vs universal reading of the n = 8 totals) is resolved by the Validator (the contract defines no aggregation anywhere; the universal reading is the only one with operational content, and `mean([5,6,7,7,7,7,6,7]) = 6.5 ≠ 7` while `max = 7` would make the control unfailable), its "proves too much about the predecessor" requirement is discharged in §C.5, and its expected disposition (`inconclusive` with a repair successor) is the disposition §I.5 reaches — from the frozen rules, not from the prior.

## C.3 Where the two reports agree without having seen each other

Six agreements, each reached from a disjoint joint and a disjoint method:

1. **IV-3 never evaluated.** Validator from the raw record (`recovered: 0/0` is an empty denominator); Red Team from the source (`run_experiment.py:275–284` never iterates) plus (T2).
2. **The R6 zero is uninformative.** Validator: conjunct 2 not in the record. Red Team: the object was never instantiated.
3. **`counted_ops` is a lower bound and SR-11's exclusions are unrecorded.** Validator J2-D2 from the artifacts; Red Team J6(b) from the counter's source and from `DEC-20260906-7448cf`.
4. **The wall-clock prior's premise was factually wrong in the same two runs.**
5. **The producer's own language does not overreach.** Validator: the two awkward fields were quoted verbatim into the report with PD entries. Red Team: a keyword scan finds exactly one hit, "no HEUR-1 verdict".
6. **`counts_per_H = {15, 22, 28}` recomputes from the recorded r-heights.** Validator from each run's `found` list; Red Team independently in C-B.

And, decisively, **both independently identified the same gap in the contract**: `invalidation_rules` branch on control **failure** and carry **no branch for a control that never evaluated**. The Validator states it as a contract gap in J3; the Red Team reaches the same place from the other side (BLOCK-1 and BLOCK-4: the controls could not have failed).

## C.4 The one framing difference, and which reading the frozen text supports

**The difference.** On R7's n = 6 degeneration:

- The **Red Team** frames it as *the object behaving correctly*: by (T1), `deg s ≤ 2` at n = 6 while `build_instance` accepts only `deg ∈ {3,4}`, so `degenerate_deg_s_2` is the filter working on a genuinely degenerate object, and IV-1's n = 6 clause is **unsatisfiable as frozen** — the required value 5 is unreachable by any implementation, independently of this Executor.
- The **Validator** refutes *"degeneration is the control behaving correctly"* from the frozen text and classifies the branch **NOT EVALUATED, not failed**. It cites three frozen passages that pre-register a positive expectation: `specification.yaml` IV-1 "certified totals must equal n − 1 (**5** and 7)"; `H-ECRANK-36d8d7 structural_ingredients` "expected certified totals n − 1 at n = 6 and n = 8"; `H-ECRANK-36d8d7 proof_search_map.baseline_reproduction` "the d = 1 closed form **is reproduced in R7**".

**Which reading the frozen text supports: the Validator's.** The contract names 5 as the value R7 must produce at n = 6, in three places, and nowhere licenses "built nothing" as a pass. Reading a null build as a pass would be re-interpreting a frozen control after seeing its result, which the protocol forbids and which is the convenient reading rather than the textual one. So **as a matter of the contract, IV-1's n = 6 clause is not satisfied and cannot be recorded as satisfied.**

**But the two are not in conflict, and I record them as one composed finding rather than averaging them.** They answer different questions. The Validator answers *what does the contract say happened*; the Red Team answers *what could have happened under any implementation*. The Red Team's (T1) does not make the clause pass — it explains why the clause can **never** pass, which is a strictly stronger statement about the contract and a checkable one: `deg(g² − p) ≤ n/2 − 1 = 2` at n = 6 against an accepted `deg ∈ {3,4}`, corroborated on 9/9 R8 tuples, 8/8 re-derived R7 tuples and 2999/3000 random tuples with the remainder at degree 0 and **never** 3 or 4. The Red Team's own summary says both horns are true.

**The composed verdict, which is what the closing decision uses:** IV-1's n = 6 clause is **NOT EVALUATED and unsatisfiable as frozen**. That is a defect in the contract, not in the mathematics and not in the Executor's conduct. The distinction is operational, not cosmetic: "failed" would say the pipeline mis-certified and would point at a pipeline repair; "not evaluated and unsatisfiable" says the control clause must be replaced by amendment and the pipeline is simply **untested at n = 6 by this control**.

**They agree on the operative fact.** Both say the control **did not discriminate**. That is what carries the disposition; the framing difference does not.

**A separate, real difference in emphasis at n = 8, resolved the same way.** The Validator records IV-1's n = 8 branch as NOT SATISFIED (3 of 8 totals are 5, 6, 6 against 7) *and* adds the fact neither prior held: **every deviation is downward**, so the plan's `proves_too_much` failure signature (a) — a certified instance **above** n − 1 — is **not triggered**. The Red Team reaches the same place from the certifier's own docstring (`certify76.py:56–60`, "Claim: rank ≥ aggregate_total"): totals of 5 and 6 are a completeness shortfall in a **lower bound**, not an unsoundness. Composed: the frozen equality is not met, and the failure is in the certifier's conservative direction. Both halves travel together; neither alone is honest.

## C.5 The prior the Coordinator most wanted overturned — held together with the Red Team's success

Prior (8) is **overturned**: `N_6(H)` is **not derivable** from the frozen contract (seven definitional gaps plus unfixed RNG call order; 375 sampling conventions fail to reproduce even the b-tuple at `b_index 579`). The Validator states plainly that it did **not** show 28 is wrong — it showed **28 has no independent check behind it**.

The Red Team's C-B is a successful independent recomputation: 28/28 pass 10 checks each, 28 distinct base-class j-invariants, `counts_per_H` reproduced from the recorded r-heights.

**These verify different things, and the composition must say so explicitly rather than let one read as answering the other.**

- **C-B is a forward check on persisted objects.** Given the instances the run recorded — their `b`, `d_pattern`, `r`, `s` — do they satisfy the certifier's own stated criteria, and are they pairwise distinct? Yes, exactly and with independent code. **What this establishes:** the 28 recorded objects are structurally valid and pairwise non-isomorphic; the instance ledger is internally coherent; no counterexample exists among them.
- **J4 is a backward check on the procedure.** Can an independent party reproduce the **sample** — and therefore the **count** — from the frozen contract? No: the 10⁴ b-tuple stream is not reconstructible, and the predicates the metric counts under ("distinct-minimal-model", "twist class populated", "certified rank above the trivial") are not defined in the contract. **What this establishes:** `N_6(10⁴) = 28`, *as the primary metric of this experiment over the declared sample*, has no independent check.

So the honest joint statement is: **the objects are checkable and were checked; the count is not checkable and was not checked.** C-B does not repair J4, because reconstructing the sample is precisely what C-B did not attempt; J4 does not impugn C-B, because failing to reconstruct a sample says nothing about the objects the sample produced. A reader who takes C-B as independent confirmation of "28" has conflated an object-level verification with a procedure-level reproduction.

Two further Red Team facts sharpen the count's status without touching the objects: the primary metric's own two filters (minimal-model dedup, "certified rank above trivial") are **not implemented** in `construct_arm` (`construct.py:401–415`), though C-B shows both would have been no-ops on this output (28 distinct j-invariants, 28 `PASS`); and the count is **not H-driven** — decade ratios 1.47 and 1.27 against a frozen ×100 prediction, because 9 980 of 10 000 tuples produced no rational root at all and H enters only through 5 height rejections out of 34 roots.

## C.6 The proves-too-much control, as the plan defined it

Run by the Red Team against all three frozen objects.

- Clause **(a)** — the pipeline reports a certified instance **above** n − 1 on the all-ones family, or a nonzero solution set on the null family: **does NOT trigger.** n = 8 max is 7 = n − 1, 0 of 8 above; R6 `found: []` exactly. (The R3 `aggregate_total` values 2 and 6 are multi-class certificates over the degree-8 field on a **different** coset with 1 absent, and n − 1 is a closed form for the all-ones family only.)
- Clause **(b)** — the controls' zeros are produced by a rejection path the counted path never traverses: **TRIGGERS**, with the Red Team's own honest qualification: the `degenerate_deg_s_2` *test* at `ecrank_engine.py:806–808` **is** shared code and R3 passed it 28/28 with `deg_s: 4`; what no control traverses is stages S2, S3, S5, the multi-class S7 and S8, and the *condition* `deg s = 2` is unreachable from the counted path.
- Clause **(c)** — the planted family produced no plants: **TRIGGERS.**

Under the plan's own text, (b) or (c) means the round **fails as a review of the counted result, regardless of the value 28 and regardless of every other joint verdict**. Both halves of the Red Team's own gloss travel together: the 28 are independently re-verified **and** uncontrolled.

**Predecessor non-transfer, and its declared limit.** The Red Team argues the reading does not also invalidate `EXP-ECRANK-76a70d`: (T1) is n-specific (the predecessor's known-false control ran at n = 8 and n = 10, where objects build; `EV-ECRANK-8b35bb certificate_refs` lists `kf-n8-b00..b19` and `kf-n10-b00..b19` and **no `kf-n6-*`**), and (T2) is pattern-and-route-specific (`construct.solve_n6` did not exist there). It also records that its planted control recovered **1161/1161** with a log-log slope 0.905 inside the frozen window, which plainly discriminated. **The limit is declared:** `experiments/EXP-ECRANK-76a70d/` was outside the Red Team's enumerated read scope and was not opened, so the conditional — *if* the predecessor's controls were also built on an object its counted path cannot produce, the same objection applies there — is **untested**. See §L.4 and next action N5.

---

# INFERENCE

Everything below is my judgement as Coordinator. The first item is reached before any scientific reading.

## I.0 VALIDITY DETERMINATION — reached before any interpretation

Against the five checks `agents/coordinator.md` responsibility 6 requires:

| Check | Determination | Basis |
|---|---|---|
| Expected run count | **PASS** — 8 enumerated runs, all finalized, plus the one preserved R1 attempt directory IV-6 requires | Validator J1.2 |
| Schema-complete manifests | **PASS** — `RUN_REQUIRED_TOP` complete 8/8, five companions 8/8, environment byte-identical, executed code content-bound by `source_sha256` 8/8 | Validator J1.2 |
| Seed integrity | **PASS with one defect** — every seed a literal member of `replication.seeds`, **no derived seed anywhere**; R6 carries an undeclared seed (760806) the contract assigns to no run | Validator J1.3 |
| Raw/summary agreement | **PASS** — zero numeric disagreements; the two awkward fields were quoted verbatim rather than hidden | Validator J1.4 |
| **Control comparability** | **FAIL** | Red Team J5(d), BLOCK-5; Validator J3 |

**The determination: the package is RECEIPT-VALID and CONTROL-INVALID.**

Receipt-valid means the eight runs are admissible as *records*: they are complete, bound to content, deterministic where the contract asked for determinism, honestly op-accounted, and free of re-scoring. That is a real result and I record it as one — it is the standard the predecessor repair run `TASK-20260906-546d17` was needed to reach.

Control-invalid means the eight runs are **not admissible as evidence** for or against the mechanism they were run to test. The reason is not a shortfall in effort: every control object in the package sits on the all-ones stratum `d = (1,…,1)`, which by (T1) and (T2) the counted path cannot produce and cannot reach; the counted arm and the known-false control run over disjoint cosets; and `construct._n6_quad`, which produced every counted instance, is executed by no run but R3 and its own replay. A control that cannot fail whatever the counted path does is not a control (`docs/inventor-protocol.md`, "controls before belief"). Independently, the frozen `invalidation_rules` say "IV-1 failure voids ALL runs of this experiment", and IV-1 is not satisfied against its frozen text.

**Two consequences follow immediately, and both bind everything after this point.**

1. **Nothing in this package is evidence for or against HEUR-1, M-A, M-B, `H-ECRANK-36d8d7`, or C1, in either direction.** A control failure is an instrument failure and is never negative mathematical evidence (AGENTS.md core rule 3); the contract's own `F4_controls` says the same in its own words — "closes: **nothing** about the mathematics; the affected runs are VOID". The R5 counted-op exhaustion at `b_index 666` is inert in both directions for the same reason.
2. **The defect is in the frozen contract, not in the Executor's conduct.** The Executor implemented what was frozen, disclosed PD-1/2/3, quoted the two awkward fields verbatim, and interpreted nothing. Ownership of the repair therefore splits, and §I.6 splits it.

## I.1 What the frozen success criterion actually says, applied mechanically

- **G1 (M-A).** Its literal clauses are **met** by the recorded numbers: in-box fraction 1.000 across AT-0/1/2 (24 of 24 draws), and each planted point met at least once (3, 3, 4) over the pre-registered `N_a = 8000` with `expected_meets = 5.0`. `tail_checks` triggers `F1_audit` only on **zero** meets with expectation ≥ 5, which did not occur. **I record this rather than drop it (AGENTS.md rule 8) — and I do not read it as satisfied, because IV-1's frozen consequence voids all runs of this experiment, R1 and R2 included.** M-A therefore stays untested, but it stays untested for an instrument reason that a repaired successor should clear cheaply: R1/R2 are read-only audits of the predecessor's committed bytes at `a20a49b6a` and are structurally independent of the n = 6 all-ones degeneracy that voids the rest.
- **G2 (M-B at n = 6).** Requires `N_6(10^4) >= 1` certified instance **with the IV-8 multi-class clause satisfied (or the explicit untested statement)**. IV-8 is **NOT SATISFIED**: branch 1 fails (no 4-class instance; max `n_classes` = 3) and branch 2 fails *in the run record* — the untested statement exists only in `execution-report.yaml`, while IV-8 says "the **run record** carries". So **G2 is not met as frozen**, before IV-1's voiding is even applied.
- **G3 (N₈, secondary).** A number was reported, but by BLOCK-6 it is not the contracted quantity: `min(H,20) = 20` collapsed both declared H levels into one integer enumeration covering ≈1.1e−5 of the H = 100 rational box, and the enumeration's expected yield is ≈ 0 by geometry whatever the budget. **G3 is reported and inert.**
- **G4 (controls).** R1 passes, R4 passes (IV-2 satisfied on all three required objects), R6 is vacuous, R7 is not satisfied, R8 never ran. **G4 fails.**

## I.2 Three defects in the frozen contract, and one incoherence I add to the reviewers' two

The reviewers named two contract defects. I name a third, from composing them.

- **CD-1. `invalidation_rules` have no branch for a control that never evaluated.** They branch on IV-1…IV-5 *failure*. A control that produced no object is neither a pass nor a failure, and the contract is silent. Both reviewers reached this independently (§C.3). Consequence: IV-3's status and IV-4's second conjunct have no defined effect on any reading, so the contract cannot decide its own outcome.
- **CD-2. IV-1's n = 6 clause is unsatisfiable by construction.** It fixes a certified total of 5 on a family that at n = 6 is not an elliptic object at all (`deg s ≤ n/2 − 1 = 2` against an accepted `deg ∈ {3,4}`). A known-false control whose required value is unreachable is not a control; it is a clause that guarantees its own non-satisfaction. Corroborating evidence that this is a design defect and not an executor defect: `EV-ECRANK-8b35bb certificate_refs` shows the predecessor ran this control only at n = 8 and n = 10, so the n = 6 clause is **new in this contract** and was never exercised before.
- **CD-3 (added here). IV-8's fallback branch and its stated consequence are both mis-specified against the output that occurred.** The fallback demands "the single-class coverage count" and the consequence is "the certification claim is downgraded to single-class" — both written for a single-class world (the predecessor's `boundaries` record all 58 of its certificates as single-class). Here **28 of 28 certificates are 3-class**. So the required fallback statement has no coherent value to report, the producer duly wrote an incoherent one ("single-class coverage count: 28 instances, all 3-class"), and the frozen "downgrade to single-class" is not a downgrade of anything this run produced. The multi-class certification path is being exercised in this program **for the first time**, and it is exercised with **no control at any n** — the Red Team records the same gap for the predecessor.

## I.3 The composed reading of the counted result

Scoped to n ∈ {6, 8}; nested H ≤ 10⁴ at n = 6 and ≤ 10³ at n = 8; the seeded 10⁴ b-tuple sample per arm (R5 completed 667); b-tuples in affine normal form; support {−1, 2, 3, 5, 7, 11, 13}; exact stdlib `fractions.Fraction`; the 1.0e8 counted-op cap; **toy** claim tier:

> The 28 objects recorded by `RUN-ECRANK-73275e-R3` are, on independent recomputation from committed bytes, 28 structurally valid and pairwise non-isomorphic n = 6 prescribed-square instances, and `counts_per_H = {15, 22, 28}` reproduces from their recorded r-heights; but no control in this package constrains them, `N_6(H)` is not re-derivable from the frozen contract, and the run set is void as evidence under its own IV-1 rule. Nothing here is evidence for or against HEUR-1 or `H-ECRANK-36d8d7` in either direction.

Both halves are load-bearing and neither may be quoted alone. The first half is why this batch is not a wasted round: an independent agent, from committed bytes and its own code, found **no counterexample** in three attempts against the 28. The second half is why it cannot be promoted: existence of 28 valid objects is not the contract's metric, and the contract's metric has neither a definition an independent party can implement nor a control that could have failed.

## I.4 Why this is not `weaken`, `reject_scoped`, `support`, `replicate` or `expand`

- **`support` is unavailable** on the frozen text: G2 fails on IV-8 as frozen, G4 fails, and IV-1's voiding rule fires. It is also unavailable on the review architecture: the plan's own `failure_signature` clauses (b) and (c) both trigger, and the plan says that means the round fails **as a review of the counted result**.
- **`weaken` and `reject_scoped` are forbidden here**, and not merely unsupported. The only adverse-looking facts in the package — the zeros of R6, R7 and R8, and R5's `found: 0` — are all instrument facts: two of them are theorems about the control objects rather than measurements of the mechanism, and the third is a declared exhaustion. AGENTS.md core rule 3 and the contract's own `F4_controls` both forbid reading any of them as negative mathematical evidence. There is therefore **no adverse call to make**, and the `obstruction`/`resource_check` gate that would govern one is filled in the evidence draft as not-applicable-with-a-stated-reason rather than manufactured.
- **`replicate` would buy nothing.** A faithful re-run of this frozen contract is guaranteed by (T1) and (T2) to reproduce the identical vacuous controls, under any seed and any sample size. Replication is the right instrument for a surprising result; it is the wrong instrument for a contract defect.
- **`expand` would be make-work.** Enlarging the sample, the box or n on an uncontrolled counted path multiplies uncontrolled numbers. AGENTS.md "ECC comes first" removes the batch ceiling and explicitly not the duty to rank; a bigger run of the same design cannot be ranked ahead of repairing the design.

## I.5 The disposition

**`inconclusive`.**

It follows from the frozen text and from nothing else, by four steps:

1. `invalidation_rules`: **"IV-1 failure voids ALL runs of this experiment."** IV-1 is not satisfied against its frozen text — n = 8 records 3 of 8 totals at 5, 6, 6 against a required 7 under the only reading with operational content, and n = 6 produced no certified total at all.
2. `falsification_criterion` `F4_controls`: a control failure **"closes: nothing about the mathematics; the affected runs are VOID"**, per core rule 3.
3. `success_criterion`: G2 is not met as frozen (IV-8), G4 fails, G1's reading is void with the rest, G3 is inert.
4. Therefore the recorded observations **cannot discriminate** between the two explanations this batch existed to separate — that the prescribed-square construction genuinely exhibits certified n = 6 instances at a rate above the draw route, and that the recorded 28 are an artifact of an uncontrolled path. `agents/coordinator.md` escalation rule: *"Mark a result inconclusive when evidence cannot discriminate between competing explanations."*

`inconclusive` here is a determinate finding, not a shrug: this round established **why** the package cannot discriminate, to the level of two checkable theorems and a nine-row control table, and it converted a design question into a specified repair. That is the informative outcome the two frozen priors both predicted and neither could confirm.

**Evidence direction `neutral`, strength `inconclusive`, claim tier `toy`, `proof_status: derivation`.** The derivation basis is (T1)/(T2) plus the C-A/C-D confirmations, archived in the Red Team report before this decision relies on them, per `docs/claims-and-verification.md` "Refutation artifacts". It backs the statement *the controls could not have discriminated*; it backs no statement about the mechanism.

## I.6 Ownership of the repair — the defects, split by who can fix them

**Contract defects (owner: Coordinator design task, then Idea Generator where a new control object must be invented). These are why a re-run of this contract is refused.**

- CD-1 `invalidation_rules` carry no `never_evaluated` branch.
- CD-2 IV-1's n = 6 clause is unsatisfiable; the all-ones family is inert at n = 6 by (T1) and (T2).
- CD-3 IV-8's fallback and downgrade are written for single-class output against 28/28 three-class output; the multi-class certification path is uncontrolled at every n, here and in the predecessor.
- The primary metric `construct_count` is not implementable from the contract (G1–G7) and the RNG call order among its four declared consumers is unfixed.
- `metrics.secondary` mislabels `EV-ECRANK-8b35bb`'s `3e-4` as per **draw**; it is per **b-tuple at n = 8**. At fixed n = 6 and the same unit, R3's 2.8e−3 does not separate from the predecessor's own 95% upper bound of 3.0e−3.
- The 1.0e8 per-run cap and the declared 10⁴ n = 8 sample are mutually inconsistent by 15.0×, determinable at design time.

**Artifact defects (owner: Executor, in the successor run). These are concrete and are listed for the successor handoff, not as grounds to return this package — the runs are immutable and are never re-scored.**

- R5 carries 1 of its 10 required 1e7-cadence checkpoints, disclosed by no PD.
- The SR-11 IC-1 exclusion ledger is absent from every run record and from the report.
- IV-8's untested statement exists only in `execution-report.yaml`, not in the R3/R5 run records as IV-8 requires — and its text is incoherent.
- `tail_checks`' decade-ratio report against the +2 prediction is absent everywhere.
- The feasibility fraction is required per (n, H) and only one value is recorded; R5's `feasibility_fraction: 0.0` states no denominator (`n_b_done` 667, `n_b_declared` 10000).
- The R6 infeasibility proof is absent from the run record (PD-1), and the proof frozen in `null_family.py` is false of the object that ran.
- `implementation.md` IC-732-3 states the n = 8 box restriction is "Recorded in every R5 raw result"; it appears nowhere under `runs/`.
- The report's seed table omits R1, R2 and R6, against a completion gate requiring every seed; R6 runs on an undeclared seed.
- `cpu_seconds` is null in all eight and `peak_rss_bytes` is a process high-water mark reported per run (six runs share `30867456`).

**Provenance item (owner: Coordinator).** Of the four provenance concerns in prior (1), three are discharged; **`model_verified: false`** survives. No `adapter doctor --probe` receipt exists in the package, so no policy-requirement gap can be confirmed or refuted. This is a provenance gap, never a defect in the mathematics.

## I.7 What the next batch should buy, ranked

1. **A control the counted path can produce.** The Red Team's proposal is the right shape and I adopt it as the design constraint: every control object drawn from the **same coset and the same mixed-sign multi-class d-pattern distribution as the counted arm**, with the positive control built **by** the counted path — take a recorded R3 instance, perturb one `r_i` so ellipticity is provably violated (negative), re-inject an unperturbed one (positive).
2. **Persist a re-verifiable certificate.** `construct.py:406–411` records only `{verdict, aggregate_total, n_classes, class_keys}`; persisting `ainv_d` and the exhibited image points per class plus the Mazur witnesses is a small change that converts the strongest refutation artifact the plan asked for — J7 item (i), Weierstrass re-verification and Mazur non-torsion — from non-computable to computable from committed bytes.
3. **Specify the metric.** An additive `protocol_amendment` writing down the family, the ellipticity condition, the pattern enumeration, the height-H box, the dedup key, "certified rank above the trivial", "twist class populated", and the RNG call order. Without it no future round can re-derive the primary metric, and every "verification" of it reproduces whatever `source/` does.
4. **The cheapest experiment that makes P4 mean anything**: the predecessor n = 6 draw arm at 10⁴ b-tuples. At 10³ the bound is 3.0e−3 and 2.8e−3 does not separate; at 10⁴, if the arm still yields 0, the bound falls to 3.0e−4 and the separation becomes ≈9×.
5. **Check whether the predecessor has the same defect.** The Red Team's non-transfer argument is strong and its limit is declared — `EXP-ECRANK-76a70d/` was outside its read scope. `EV-ECRANK-8b35bb` is `strength: replicated`, `direction: weakens`, and its 1161/1161 plant recovery points the other way, but the question "do the predecessor's controls traverse its counted path" has not been asked of the predecessor's own bytes.

---

# LIMITATION

## L.1 Scope of everything above

n ∈ {6, 8}; nested H ≤ 10⁴ at n = 6 and ≤ 10³ at n = 8; the seeded 10⁴ b-tuple sample per arm, of which R5 completed 667; b-tuples in affine normal form `b_1 = 0`, `b_2 = 1`, `b_3..b_n` distinct integers in `[−20, 20] \ {0, 1}`; support {−1, 2, 3, 5, 7, 11, 13}; exact stdlib `fractions.Fraction` arithmetic with no descent, no PARI and no network; the 1.0e8 counted-exact-op cap per run; **toy** claim tier per `docs/claims-and-verification.md`. **Transfer assumptions: none are asserted.** Nothing here reaches larger n, cryptographic parameters, rank over ℚ in general, or C1. The construction's per-tuple cost structure is what would carry to larger n, and the contract itself records that transfer as a disclosed assumption rather than a claim.

## L.2 What this round is, stated at its true size

Two reviews, with three disclosed blindness deviations (`independence-check.md`), on a toy-scale run set whose primary positive control never evaluated and whose known-false control is unsatisfiable at n = 6 by construction. It is not a replication, not a breakthrough-tier review, and not a second independent execution of the mechanism. The strongest positive statement it supports is object-level (28 valid, pairwise non-isomorphic instances found by independent code), and even that rests on a single review computation whose script was not archived as a run record.

## L.3 What neither reviewer could see

- The Validator was blind from `source/` and `implementation.md` throughout: it could not verify the producer's `iv2` mechanism, could not verify that `null_family.py` contains the R6 infeasibility proof, could not verify PD-3, and could not answer the same-path question. All four were the Red Team's, and all four were answered.
- The Red Team did not open `ledger/hypotheses/H-ECRANK-36d8d7.yaml` (in scope, not needed for J5–J7), so its readings of IV-1 rest on `specification.yaml` alone. The Validator's three-passage textual refutation in §C.4 is what supplies the hypothesis-side text; that this came from one reviewer only is a coverage fact, not a defect.
- Determinism was exercised **only** on the R3/R4 pair and the R2 audit reconstruction. R1, R5, R6, R7 and R8 have no replay; IV-7 is NOT EVALUATED for them.
- IV-6's "every attempt preserved" is not evaluable from a record: absence of an `attempt-*` directory cannot distinguish one attempt from an unpreserved one.
- `model_verified: false` with no probe receipt: NOT EVALUATED.
- `near_miss_ledger` is empty in R3, R5 and R6 with `near_miss_total: 0` while 9 980 n = 6 tuples had no in-box solution; whether the contract requires enumeration or only existence is not pinned, and neither reviewer resolved it.

## L.4 Live open items this composition does not close

- Whether `EXP-ECRANK-76a70d`'s controls traverse its own counted path is **untested**; the Red Team's non-transfer argument is made from `EV-ECRANK-8b35bb` alone and its limit is declared. Until checked, `EV-ECRANK-8b35bb` is not disturbed by anything here, and I disturb nothing.
- The multi-class certification path that produced every counted `aggregate_total` in R3 is controlled by **nothing** in this package and, per `EV-ECRANK-8b35bb boundaries`, by nothing in the predecessor either.
- The `iv2_counts_identical` mechanism (int-keyed versus str-keyed dicts) is consistent with everything observable and remains **unverified**; a reported boolean whose value depends on dict key representation sits adjacent to IV-7's ban on dict-order dependence in any reported quantity, and the Validator flagged it without claiming IV-7 fails.
- The eight runs are immutable and are preserved with their anomalies (rule 8). Nothing here re-scores them, deletes them, or rewrites the execution report.

## L.5 Durability

This is a draft. It is not durable, and neither is the evidence record nor the closing decision drafted beside it, until the isolated ledger archive `TASK-20260907-f5e45b` merges `origin/main`, mints the closing decision id, commits exactly the declared paths, writes the write-once checkpoint shard, pushes, opens or refreshes the PR, and the post-commit verifier accepts. `H-ECRANK-36d8d7` remains `specified` until then, and after it unless that decision moves it.

## L.6 Infrastructure

No infrastructure event occurred in this composition task: no timeout, no crash, no `ENOSPC`. No command was run by this agent; the orchestrating session runs commands and reported the `tools/check_review_independence.py` result recorded in `independence-check.md`. No number in this file was computed by me — every quantity is quoted from the artifact named beside it.
