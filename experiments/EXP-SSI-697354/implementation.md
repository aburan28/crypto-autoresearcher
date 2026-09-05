# EXP-SSI-697354 — implementation note

Executor note for `RUN-SSI-697354-a`, written under handoff
`TASK-20260817-4d5e6f`. Observations only; no judgement on `H-SSI-7fe2bf`, no
security claim.

## What was built

`crossover.py` (stdlib-only primary path, Python 3.11.15) implements the frozen
contract end to end:

- **Step 0** writes `environment.json` with the interpreter, the
  `importlib.util.find_spec` result for numpy/sage/sagemath/g6k/fpylll/scipy/
  mpmath, and the explicit no-forbidden-import assertion. All seven were absent.
- **Step 1** re-reads T1 (`$.scaling_summary`, 8 rows) and compares to the frozen
  literals under exact float equality; re-parses T2 from lines 234–238 of the
  frozen paper text and compares both to the frozen columns and to the
  independent `PAPER_PAIRS` transcription at `cost_model.py` lines 60–66. Any
  mismatch raises `InputDrift` and the run stops. SHA-256 of every input,
  plus the freeze receipt binding `specification.yaml`, goes to
  `input_hashes.json` and `freeze_receipt.json`.
- **Step 2** fits L1–L4 from the re-read rows (nothing is hard-coded from the
  frozen coefficient list; the frozen values are used only as a comparison).
- **The RG gate runs before any curve is computed**, per the stopping rule. On
  failure the program writes the gate report and an `invalid` `raw-result.json`
  and exits 2. It did not fail.
- **One solver** (`solve_cell`) implements crossover_procedure steps 1–6 and is
  the *only* solver in the file. L1–L4, L5, N0 and N1 all go through it with
  `E(.)` swapped, which is what the null-arm clause requires.
- Controls, metrics, tail checks and the scope tables are computed from the
  solved grids and written to the twelve declared JSON artifacts.

`f3_escalation_check.py` is a **separate second pass** over the artifacts the
run had already emitted; it discharges the F3 escalation rule and the
vacuous-satisfaction disclosure. See deviation DEV-1 below.

## Deviations from the approved protocol

1. **DEV-1 — F3 audit ran outside the main program.** The escalation scan was
   not implemented inside `crossover.py`. Rather than re-execute the single
   authorized run, it was performed by `f3_escalation_check.py` over
   `p_star_table.json` and the committed T2 `L_mem` column, writing
   `f3_escalation_check.json`. No emitted number changed. Result: zero F3
   candidates; the bound is VACUOUSLY SATISFIED at every `log2 w <= 40`.
2. **DEV-2 — pre-flight and determinism executions.** Two smoke executions into
   a scratch directory outside the repository preceded the recorded run, and one
   followed it to verify the determinism guarantee. None wrote into
   `experiments/`; no artifact in this package came from them. The single
   authorized protocol run is `RUN-SSI-697354-a`, executed once, exit status 0.
3. **DEV-3 — A-invariant solve caching.** `Delta` does not depend on `A`, which
   cancels between `T_B` and `T_A`. Each cell is solved once per
   `(law, S, c, MC, log2 w, log2 k_DG)` and the outcome attached to all four
   declared `A` values, so every declared cell is emitted (4480 / 2240 / 1120)
   while 1120 / 560 / 280 distinct solves are performed. The invariance is
   *measured*, not assumed: 1360 comparisons, maximum spread 5.68e-14 bits
   (`reproduction_gate.json` → `A_cancellation_check`). `A` is retained inside
   `T_A` and `T_B`, where the absolute-cost gate needs it.
4. **DEV-4 — `stdout.txt`/`stderr.txt` are copies** of the `stdout.log` /
   `stderr.log` the recorded command wrote, because the contract's artifact list
   names `.txt` and `docs/evidence-and-reproducibility.md` names `.log`.

## Implementation choices a reviewer should attack

- **MONO-1 straddle handling.** The declared w grid is non-uniform, so a segment
  could in principle straddle the clamp at a committed `P` row. The code
  compares each measured slope against the clamp-implied slope for that segment
  (which reduces to +0.5 / 0 / −0.5 for non-straddling segments) at tolerance
  1e-6. On the declared grid no segment straddled a clamp at a committed row, so
  the straddle class is empty and every measured slope is exactly +0.5, 0.0 or
  −0.5.
- **MONO-2 kink location** is measured by bisecting a backward finite-difference
  slope of the assembled `Delta` (h = 1e-11, 200 iterations), not by reading the
  `min()` clamp. A missing clamp would produce no sign change in the predicate
  and the bisection would return the bracket endpoint, failing the 1e-9 check.
- **`ROOT_OUTSIDE_WINDOW` is structurally hard to reach** under the specified
  procedure: step 4 classifies a sign-change-free cell as `NO_CROSSOVER_IN_WINDOW`
  before step 6 could see a root beyond the window. The label is implemented as a
  guard on any root the bisection returns outside `[256, 768]`; it fired zero
  times. The window itself is a hard boundary — `_interp` raises on any `P`
  outside it.
- **`undefined_segments.json` is per-cell** (7840 entries), because the
  extrapolation stamp is universal and the contract says an empty list would
  itself be a defect. Summarising it would have hidden the 488
  `interpolated_between_committed_rows` cells and the 3640
  `INFEASIBLE_AT_MEMORY` cells.
- **The margin band at the matched point straddles zero**, so its fractional
  width is large. Both fractions are reported as computed and the F2 judgement is
  left to review.

## Things recorded, not resolved

- The committed `MC_P13` formula makes the assessed method **more** expensive as
  memory shrinks (measured `dT_A/d(log2 w) = -0.5` below the clamp). This is the
  opposite of what `H-SSI-7fe2bf` HEUR-XO-3 `supporting_results` asserts about
  `MC-P13`. Reported in `sensitivity.json` → `SANITY-1` and in the execution
  report; not resolved here.
- No declared sub-grid reproduces RG-5's committed `[6, 11]` interval
  endpoint-for-endpoint; the in-interval sub-grid spans `[6.431, 9.539]` over 16
  cells. RG-5's stated pass condition is nonetheless met.
- `numpy` is absent, so XCHK-2 is `NOT_RUN` with its `ImportError` text.
  Infrastructure signal; no reported number depends on it.
- The model that served this session (`claude-opus-5`) differs from the
  `executor-implementation` binding (`claude-sonnet-5`) with
  `fallback_allowed: false`. Recorded truthfully in the manifest's `inference`
  block with `fallback_used: true`; no model was in the run's computational loop.
- `ledger/goals/GOAL-SSI-001` still exists neither as a file nor as a sharded
  directory, as the contract's own provenance note observed. Outside this task's
  write scope; surfaced for the Coordinator.
