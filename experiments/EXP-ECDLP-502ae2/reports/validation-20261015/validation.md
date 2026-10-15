# Validation: EXP-ECDLP-502ae2 / RUN-ECDLP-502ae2-01

- Validation id: `VAL-20261015-280100` (structured record: `validation_report.yaml` in this directory)
- Validator: independent Validator subagent, 2026-10-15. Not the producer, and nothing in this directory was copied from the producer's reports.
- Snapshot validated: commit `1d008fd8e6` on `claude/p256-ecdlp-factor-base-wq59m1`. It was exported with `git archive 1d008fd8e6 experiments/EXP-ECDLP-502ae2 experiments/EXP-ECDLP-f49f75` into `/tmp/claude-0/validator2/snap/`, and all checks ran against that export. The live working tree was being edited by another session during validation: `analyze.py` had an uncommitted plot-only diff and `reports/run-20261015T1634Z/` was untracked or staged. None of that working-tree-only material was validated.
- Raw run artifacts, the ledger and research status were not modified, and nothing was committed.

**Terminal verdict: `passed`.** The RUN-ECDLP-502ae2-01 receipt is admissible evidence. The frozen falsification criterion is met by both of its clauses, and the success criterion is not met. Several concerns are listed below. None changes the verdict or the direction of the result, but one (C4c) changes the size of the reported A/B ratio. A passed validation does not by itself change the status of H-ECDLP-60de36; that decision belongs to the review-evidence gate and the Coordinator.

## Summary table

| # | Check | Result |
|---|---|---|
| 1 | Protocol frozen before data; spec unchanged | **PASS** (minor concern: the criteria script was committed 36 s after the start) |
| 2 | Positive control, and soundness of `eval_gb_at` | **PASS** (32/32 planted-ok results, 40/40 planted results with a completed GB; evaluator sound; at most 1 constant term per input polynomial in all 78 systems) |
| 3 | Frozen criteria re-derived independently | **PASS**. Falsification criterion **met** (clause 1: A ≥ B in 2/2 jointly completed cells; clause 2: A retired at L=5, B and C at L=7). Success criterion not met. |
| 4a | Same msolve flags across arms | **PASS** |
| 4b | A encodes the same fibre as B | **PASS** (quotient_dim A = B on 8/8 paired instances; = Singular vdim on 34/34) |
| 4c | Is A's slowdown an artefact of the `-P 1` genericity handling? | **CONCERN (magnitude only)**. The `-P 1` retries scale with variable count and inflate A/B about 5x, but A is slower on GB time alone (8.0x, 30.5x, >79x) and was retired at L=5 in the GB step itself. |
| 4d | "status ok" vs the stopping rule | **PASS** (0/90 status inconsistencies; stopping rule applied correctly) |
| 4e | L=6 B/C cells (only the 2 random targets completed) | **CONCERN (interpretation)**. Those two "ok" results are no-solution certificates (`[1]` basis). Under a planted-only reading, B and C complete only up to L=5. The verdict is unchanged because A completes only up to L=4. |
| 5 | Reproducibility re-run (L=3 inst 0–5, L=4 inst 0, 3, 4; arms A, B) | **PASS** (0 mismatches in deterministic fields over 18 arm-results; timings within 0.7–1.9x at L=3 and 0.98–1.15x on the L=4 planted runs) |
| + | Artifact presence and hashes | **PASS** (7/7 manifest sha256 match) |
| + | Resource records | **CONCERN**: no memory measurement in the run records |
| + | Required report artifacts (run report and PDF) | **Not in snapshot `1d008fd8e6`**: committed later as `14dbf74292` (run records unchanged); contents not validated |

## Check 1: protocol frozen before data, spec unchanged

Evidence (from `git log`, `started_at` and `environment.json`):

| Event | Time (UTC) | Commit |
|---|---|---|
| spec + launcher + trial plan frozen | 2026-10-15T16:33:59Z | `43f93787df` |
| `started_at` | 2026-10-15T16:34:16Z | (17 s after the freeze) |
| `analyze.py` (criteria operationalisation) | 2026-10-15T16:34:52Z | `f91c152c79` |
| `finished_at` | 2026-10-15T18:26:25Z | elapsed 6729 s; stdout reports `elapsed_s: 6728.9` |
| run records committed | 2026-10-15T18:26:57Z | `1d008fd8e6` |

- `environment.json` records `git_head = 43f93787df…` and `git_dirty: false`, and `manifest.json` records `launcher_commit` as the same commit.
- `git diff 43f93787df 1d008fd8e6` is empty on `specification.yaml`, `msolve_grid.py`, `trial-plan.json` and the imported `experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py`. That module was last changed in `7b09a17417` (07:01Z, f49f75 AMD-02), before the freeze.
- The working-tree `specification.yaml` has sha256 `4f4804bf…ef2698`, identical to the blob at `43f93787df`. `amendments/` is empty.
- **Minor concern.** The operational definitions of "jointly completed" (A and B each have ≥1 ok) and "retired" (every instance timed out) appear only in `analyze.py`. That file was committed 36 s after `started_at`, and the L=3 cell finishes in about 3 s, so L=3 rows may already have existed. The spec text alone is enough to decide this outcome, and Check 3 shows the verdict is the same under every reasonable reading.

## Check 2: positive control and `eval_gb_at` soundness

Run records (`outputs/recompute.out.json` → `positive_control`):
- Planted results with status `ok`: **32/32** have `planted_in_variety: true` (A 8, B 12, C 12).
- Planted results whose GB step completed, including the 8 L=6 B/C planted results whose solve timed out: **40/40** are true. Every one of them also has `quotient_dim > 0`, so the basis is a proper, non-empty, zero-dimensional basis.
- Random targets carry no planted check, by design (there is no planted point). Arm E reports ≥1 decomposition on every planted target.

Evaluator tests (`scripts/test_eval.py` → `outputs/test_eval.out`), using `eval_gb_at` imported from the committed launcher:
- **Root and non-root.** On a system over F_101 with the known root (2,7,54), the evaluator returns True on the root and False on 4 non-roots. On a Singular-style system (implicit coefficient 1, negative coefficients) it accepts **exactly 4 of the 101² grid points**, which are its 4 true F_p roots, so there are no false accepts. With A-arm variable names (`w101`) it accepts the roots and rejects them once perturbed.
- **Inconsistent system.** For a basis of `[1]` it returns False.
- **Vacuity.**
  - A synthetic empty basis `[]:` returns True, so a vacuous pass is possible in principle. It does not occur in this run: every planted GB has `quotient_dim > 0` (msolve prints no quotient dimension for `[1]`), and the bases kept in the re-run have 3–45 elements.
  - The evaluator raises an error, rather than passing, when the `[` is missing (ValueError) or a variable is unknown (NameError).
  - **Partial parse.** The number of polynomials the producer's slice-and-split finds equals msolve's `#length of basis` header in 18/18 kept files. The `#` header lines contain no brackets, and the body runs from `[` to the final `]:`.
- **Independent evaluator** (`scripts/solparse.py`, a term parser with no `eval`): on the 12 planted re-run bases it agrees with `eval_gb_at` 12/12, and it rejects the planted point with x1+1 12/12.

msolve constant-term quirk:
- Confirmed: `x1+3+4` and `3+x1+4` both parse as `x1+4`, so msolve 0.6.5 keeps only the last constant.
- `lin_terms` merges constants. Over **all 30 instances and 78 input systems**, every input polynomial has at most 1 constant term (`outputs/check_inputs.out.json`, `max_const_terms: 1`). This includes both target types and every Singular-expanded S_4 string (122–125 terms, with negative coefficients).

Input-level control, independent of msolve: the planted point (x, plus the chain w's for A) is a zero of every input polynomial in every planted system, and the perturbed point is not. p, b, chain_c, fb_size, nvars and npolys recompute exactly for all 78 systems.

Cross-instrument: msolve `quotient_dim` equals Singular `vdim` (EXP-ECDLP-f49f75 RUN-02, same seeds, p, b and chain_c) on **34/34** paired (L, inst, arm) results at L=3..5. msolve and Singular therefore built the same ideal.

Solve-step control (validator-added; not part of the frozen protocol): in the re-run, the `-P 1` parametrization recovers the planted point in 12/12 planted A/B results, and returns `[-1]` (no solution) on 6/6 random-target results.

**Instrument note (limitation, not a failure).** msolve 0.6.5's `-P 1` picks a random separating linear form on each run. Over these tiny fields (p = 599 at L=3) it sometimes outputs a parametrization after logging "Elimination polynomial is not squarefree", which drops colliding solutions:
- L=3 inst 0, arm A: eliminating-polynomial degree 21 against a quotient dimension of 22 in the re-run, then 22 in the diagnostic run.
- Same instance, arm B: 22 in the re-run, then 19 in the diagnostic run (`diag/L3i0*.Pv2.log`).

So solve status `ok` means msolve finished, not that every solution was listed. The effect is random per run, hits both arms, and does not affect the timing comparison.

## Check 3: frozen criteria re-derived

Independent script: `scripts/recompute.py` → `outputs/recompute.out.json`.

| L | A median solve (s) | B median solve (s) | A/B solve | A median gb (s) | B median gb (s) | A/B gb |
|---|---|---|---|---|---|---|
| 3 | 1.403 | 0.0848 | 16.5 | 0.205 | 0.0257 | 8.0 |
| 4 | 291.25 | 1.941 | 150.1 | 10.49 | 0.343 | 30.5 |
| 5 | 6/6 timed out in the gb step (≥600.16 s) | 35.22 | — | ≥600.16 | 7.59 | >79 |

- **Jointly completed L** (A and B each have ≥1 ok): {3, 4}. A's median is at or above B's in **2/2 = 100%** of them, so falsification clause 1 is **met**.
- **Retirement** (every instance timed out): A at **L=5**, B at **L=7**, C at **L=7**. The largest L with ≥1 ok result is A 4, B 6, C 6. Since 5 ≤ 7, falsification clause 2 is **met**.
- **Falsification criterion: MET**, by each clause independently. **Success criterion: NOT met** (A is faster in 0/2 cells, and A's largest completed L, 4, is below B's and C's, 6).
- **Robustness to how "completed" is read.** If "completed" means ≥1 planted ok, or all 6 ok, B and C reach L=5 and A reaches L=4. Clause 2 still holds and the success clause still fails.
- The pre-registered prediction (A is slower than B in every jointly completed cell and is retired at a smaller L than B and C) matches the outcome.
- Replaying the producer's committed `analyze.py` on the snapshot (`producer-analyze-replay/criteria.json`) gives the same values: joint {3, 4}, A_faster 0, ratios 16.5 and 150.1, retirement A 5, B 7, C 7.

## Check 4: instrument fairness

**4a. Flags: PASS.** `build_system` is the only per-arm difference. The msolve argv is identical for every arm: `-f IN -o OUT -g 2 -v 2 -t 1` for the GB step, then `-f IN -o OUT -P 1 -t 1` for the solve. The 600 s timeout applies to each step. Within an instance the arms run one after another in the same worker of a 4-process pool, so all arms see the same contention.

**4b. Same fibre: PASS.**
- quotient_dim(A) = quotient_dim(B) on all 8 paired planted instances where both finished (L=3: 22, 3, 34, 6; L=4: 6, 6, 6, 6).
- On the random targets at L=3 and L=4, both A and B have an empty variety: no quotient dimension is recorded, and the re-run bases are `[1]` for both arms.
- Algebraic reason: each chain equation `v(u−x0) − u(u−x0) − t` is linear in the next variable with coefficient `u−x0`. That coefficient is a unit on the variety, because `t ≠ 0`. Hence k[x,w]/I_A ≅ k[x]/I_B.
- `build_chain` asserts that all 2^L elements of V map to c. `check_inputs.py` confirms that B's dense polynomial has degree 2^L and vanishes on V. Arm A has 3L variables and 1+3L polynomials, as specified.

**4c. `-P 1` genericity handling: CONCERN about magnitude; the direction is unaffected.**
- msolve's default `-c 2` handles a non-generic staircase in two stages. Planted solution sets are non-generic, because the S3 permutation symmetry of a decomposition means no single coordinate separates the solutions. msolve first retries other variable orders and then adds linear forms, and each retry is a full F4 run.
- Diagnostic on L=4 inst 0 (`diag/L4i0*.Pv2.log`, `diag/L4i0*.timing.json`):
  - **A:** 322 s in total (peak RSS 252 MB). 11 variable-order changes give 12 F4 runs of 10.5–11.7 s each, followed by 3 linear-form F4 runs of about 63 s each.
  - **B:** 2.1 s in total (peak RSS 20 MB) over 5 F4 runs (2 order changes and 2 linear forms).
- The number of retries grows with the number of variables (3L for A, against 3 for B). This explains why A's planted solve/gb ratio is about 28x while B's is about 5.5x. On random targets, where the variety is empty and no genericity step runs, A's solve time roughly equals its GB time (10.8 s against 10.4 s).
- The frozen primary metric's A/B ratio (150x at L=4) is therefore inflated roughly 5x by an instrument policy that scales with variable count.
- **On GB time alone A is still slower in every cell:** 8.0x at L=3, 30.5x at L=4, and at L=5 A's GB step timed out in 6/6 instances against a 7.6 s median for B (>79x).
- A's retirement at L=5 happened entirely in the GB step, where `-P 1` never ran. On a GB-only reading, A completes up to L=4 and B and C up to L=6, so the falsification does not depend on `-P 1`.

**4d. Status vs stopping rule: PASS.**
- The status of all 90 A/B/C results was recomputed from `gb_status` and `solve_status` with 0 inconsistencies. A result is `ok` iff both steps returned rc 0, and `timeout` if either step timed out. There were no crashes and no degenerate targets.
- The stopping rule was applied correctly:
  - A was retired after L=5 (6/6 timeouts) and has no L=6 or L=7 rows.
  - B and C continued after L=6 (4/6 timeouts) and were retired at L=7 (6/6), which is the last planned L.
- Because each step has its own 600 s limit, a timed-out instance can use up to about 1200 s. Even so, no `ok` result exceeds 600 s for GB plus solve (the maximum is 438 s, at L=6). The metric "completed within 600 s" therefore holds for every `ok` result.

**4e. L=6 B/C cells: CONCERN about interpretation.**
- Only inst 4 and 5 completed. Both have empty varieties: E finds 0 decompositions, msolve prints no quotient dimension, and the basis is therefore `[1]`. Their `ok` certifies that the system is inconsistent; it is not a solve.
- All 4 planted instances finished the GB step (256–270 s) and then timed out in `-P 1` at 600 s. That fits the genericity retries in 4c: about 5 F4 runs at roughly 260 s each.
- "B and C reach L=6" therefore rests on no-solution instances. Reading planted instances only, B and C reach L=5. A reaches L=4 under either reading, so the verdict is unchanged. The producer's working-tree graph annotation states the same thing, but that annotation was not validated.

## Check 5: reproducibility

Driver: `scripts/rerun.py`. It calls the committed `msolve_grid.run_instance` unmodified (launcher sha256 `a44d2ed6…`), with two changes only: tempfiles go to a kept directory, and they are not deleted. The sample was L=3 inst 0–5 and L=4 inst 0, 3 (planted) and 4 (random), arms A and B, 4 workers, on the same machine class (4 vCPU, kernel 6.18.44, msolve 0.6.5-1build2, Singular 4.3.2, Python 3.13.16), from 2026-10-15T18:34:09Z to 18:39:45Z. Outputs are in `rerun/`, and `scripts/postcheck.py` produced `outputs/postcheck.out.json`.

- **Deterministic fields.** 0 mismatches over 18 arm-results on fb_size, nvars, npolys, gb_status, solve_status, status, f4_max_deg, quotient_dim and planted_in_variety. seed, p, b and chain_c are identical.
- **Timings, as re-run/original ratios.**
  - L=3: GB 0.70–1.88, solve 0.995–1.35. These runs are sub-second and noisy.
  - L=4 A planted: GB 1.06 and 1.11, solve 1.07 and 1.10 (314 s and 318 s against 293 s and 290 s).
  - L=4 B planted: solve 1.13 and 0.99.
  - L=4 random: 0.99–1.49.
- A > B is reproduced on every instance, for both GB and solve.

## Other checks

- **Artifacts.** All 7 files named in `manifest.json` are present, and their sha256 hashes match. `stderr.log` is empty, `stdout.log` ends with `exit=0`, and `command.txt` matches the trial-plan command.
- **Resource records (CONCERN).** The run records contain wall times but no peak-memory measurement, so the spec's 12 GB budget cannot be checked from the receipt (AGENTS.md "Artifact policy" requires resource measurements). The validator's own measurements of `-P 1` at L=4 are 252 MB for A and 20 MB for B. This is not load-bearing for the verdict.
- **Required report artifacts.** `reports/` (run report, graph, PDF) is not in snapshot `1d008fd8e6`. During validation the producer committed it as `14dbf74292` (`reports/run-20261015T1634Z/{report.typ,report.pdf,msolve-cost-vs-L.{png,svg},summary.json,plot_source_analyze.py}` plus the plot-only `analyze.py` diff). `git diff 1d008fd8e6 14dbf74292` is empty on `runs/`, the spec, the launcher and the trial plan, so the validated records are unchanged. The report's contents were **not** validated here: it is outside the task's snapshot and is a sibling report.
- **Secondary metric (msolve/Singular ratio).** `analyze.py` divides Singular's internal `rtimer` time (std + fglm, in ms) by msolve's process wall time, which includes process spawn, parsing and the genericity retries. The two quantities differ in what they measure, so treat the ratio as indicative only. It is not part of either frozen criterion.
- **Null-object control (inventor-protocol §3).**
  - Arm C (a random 2^L-set, dense) is the null object, and its medians track B's: 0.085 s vs 0.126 s at L=3, 1.94 vs 1.37 at L=4, 35.2 vs 49.1 at L=5, and 214.5 vs 229.4 at L=6 (random targets only). The dense encoding shows no effect from the set's structure.
  - The A/B effect grows with L (GB ratio 8.0 → 30.5 → >79) rather than staying flat, so it does not show the "should decay but doesn't" artefact pattern.
- **Validation ladder (§6).** Not applicable: no speedup is claimed. The result is a measured, negative A/B ratio at the scales where it was run, not an extrapolation.
- **Heuristic-validation and cost-model checks.** Not applicable: there is no heuristic CDF and no cost table.

## Scope of the negative evidence (for the decision record)

The negative evidence covers only this configuration:
- m = 3, L = 3..7 (p of 10–22 bits), 6 instances per cell (4 planted, 2 random), seed `EXP-ECDLP-f49f75/v1`;
- msolve 0.6.5, single thread, DRL with variable order x1..x3 then w(i)(j);
- `-g 2` reduced basis and `-P 1` with the default `-c 2` genericity handling;
- 600 s per step.

It does not cover:
- other variable orders, or block/elimination orders for arm A (for example `-e`, eliminating the w's);
- `-c 0` or `-c 1`, or a solve that skips the genericity retries;
- other F4 implementations (Magma, FGb), multi-threading, or larger p at fixed L;
- m ≠ 3, or other chain encodings.

## Files in this directory

- `validation.md`: this report. `validation_report.yaml`: the structured record. `SHA256SUMS`: digests of every file below.
- `scripts/`: the exact scripts that ran. They contain absolute scratch paths (`/tmp/claude-0/validator2/...`) for the snapshot export and the helper import.
  - `recompute.py`, `check_inputs.py`, `postcheck.py`, `rerun.py`, `solparse.py`, `test_eval.py`, `probe_sol.py`, `timed_msolve.py`.
- `outputs/`
  - `recompute.out.json`, `check_inputs.out.json`, `postcheck.out.json`, `test_eval.out`;
  - `evaltest/`: the toy msolve inputs and outputs.
- `rerun/`
  - `rerun-raw.jsonl`, `rerun-environment.json`, `rerun.stdout`, `rerun.stderr`;
  - `files/`: the kept msolve `.ms`, `.gb` and `.sol` files for every re-run arm-result.
- `diag/`: the `-P 1 -v 2` logs, `.sol` outputs and timing/peak-RSS JSON for L=3 inst 0 and L=4 inst 0 (arms A and B). `L4i0.files` maps file names to arms.
- `producer-analyze-replay/`: output of the producer's committed `analyze.py` replayed on the snapshot.

Commands, run from `/tmp/claude-0/validator2`:

```
python3 -I work/recompute.py snap/.../RUN-ECDLP-502ae2-01/raw-result.jsonl snap/experiments/EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-02/raw-result.jsonl
python3 -I work/check_inputs.py snap/experiments/EXP-ECDLP-502ae2/msolve_grid.py snap/.../RUN-ECDLP-502ae2-01/raw-result.jsonl
python3 -I work/rerun.py snap/experiments/EXP-ECDLP-502ae2/msolve_grid.py /tmp/claude-0/validator2/rerun
python3 -I work/postcheck.py snap/experiments/EXP-ECDLP-502ae2/msolve_grid.py snap/.../RUN-ECDLP-502ae2-01/raw-result.jsonl rerun
python3 -I work/timed_msolve.py LOG -- -f rerun/files/L4-inst0/<A|B>.ms -o OUT.sol -P 1 -t 1 -v 2
python3 -I snap/experiments/EXP-ECDLP-502ae2/analyze.py producer_analyze_out snap/.../RUN-ECDLP-502ae2-01 snap/experiments/EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-02
```
