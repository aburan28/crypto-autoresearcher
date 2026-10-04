# TASK CARD `TASK-20260830-fffafa` — Executor

**Goal** `GOAL-SSI-001` · **Batch** `BATCH-5917d5` · **Role** `executor` ·
**Policy** `executor-implementation` · **Archived by** `TASK-20260830-4b2fc8` ·
**Reviewed by** `TASK-20260830-92f16c`

## Objective

Verify the merged EXP-WESOVOW-001 charging-law source fix at its source,
reconcile the `fitted_opt` and `PAPER_PAIRS` anchors with one explicit
authority decision, and re-derive the P=512 crossover and its `w=2^80` sign
from the corrected run's own literals under the authoritative anchor. All
work is arithmetic on committed literals plus code reading, plus at most ONE
verification re-execution of the merged source.

This is not a new experiment, attack, certificate, or security conclusion,
and it does not lift the P=512 citation prohibition.

## Background (read these first)

- The charging-law defect (pre-fix law `T_full / sqrt(min(w, M))` vs the
  specification's `w=M` cap requirement, `specification.yaml:149`) was
  localized neutrally in BATCH-eb0a7e:
  `coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/`
  (`defect_localization.md`, `corrected_charging.py`, `recomputed_table.json`,
  `control_report.md`, `anchor_sensitivity.md`), accepted by
  DEC-20260824-384e78 / EV-SSI-12c22e.
- The source fix itself was committed at 7d188a7c3
  ("archive TASK-20260809-981821 ... RUN-WESOVOW-201692-001 corrected run
  snapshot") and reviewed in BATCH-dbfee9 (DEC-20260809-39eb45,
  EV-SSI-e8cc71, VAL-20260809-b30a85, TASK-20260809-e805f6). It is now on
  origin/main. The BATCH-eb0a7e branch did NOT contain 7d188a7c3, which is
  why its defect report cites the pre-fix file state — that provenance gap
  must be recorded, not silently resolved.
- DEC-20260824-384e78 directs: reconcile the anchors with an explicit
  authority decision; fresh independent review before any P=512 boundary is
  reconsidered.

## Deliverables — exactly six

```text
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/source_fix_verification.md
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/reexecuted_raw-result.json
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/reexecution_manifest.json
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/anchor_reconciliation.md
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/p512_rerivation.md
coordination/goals/GOAL-SSI-001/batches/BATCH-5917d5/tasks/TASK-20260830-fffafa/p512_rerivation.json
```

## Work items

1. **Source-fix verification.** Read the merged
   `experiments/EXP-WESOVOW-001/cost_model.py` (read-only). Verify the three
   load-bearing lines — serialized formula declaration, executable charging
   computation, crossover computation — against the law stated in
   EV-SSI-e8cc71: `T(w) = T_full * sqrt(M/min(w,M))`, i.e.
   `log2T(w) = log2T_full + 0.5*max(0, log2M-log2w) + c*sqrt(log2p)`,
   crossover `log2w_star = log2M + 2*(log2Tfull + c*sqrt(log2p) - log2TDG)`.
   Hand-check the cap requirement (at `w=M`, time equals `T_full` exactly)
   against the executable form. Report line numbers and verbatim quotes.
2. **Verification re-execution (the single authorized run).** Run the merged
   source with `WESOVOW_RAW_PATH` pointed at
   `reexecuted_raw-result.json` in your task directory; capture command,
   git commit + dirty state, environment/dependency versions, stdout,
   stderr, timestamps in `reexecution_manifest.json`. Diff
   `reexecuted_raw-result.json` against the committed
   `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json`
   and report the maximum absolute residual per top-level field. A residual
   beyond floating-point tolerance is an environmental deviation: record the
   exact versions and stop the reproducibility claim there — do not declare
   the source defective on that ground.
3. **Cross-check against BATCH-eb0a7e.** Confirm the corrected law used by
   `BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py` is the
   same law the merged source implements (state the comparison, do not edit
   either file). Spot-check that your re-executed per-field `optimal`
   values agree with the 240-row `recomputed_table.json` `fitted_opt` rows
   where the grids overlap.
4. **Anchor reconciliation.** State exactly ONE explicit authority decision:
   `fitted_opt` authoritative, `PAPER_PAIRS` authoritative, or both remain
   non-authoritative scenario anchors. Tie the reasoning to committed
   records (EV-SSI-e8cc71's reviewed crossovers taken from the corrected
   run's fitted values; DEC-20260809-39eb45's paper-pair 49.5 approximation
   note; PAPER_PAIRS provenance as a rounded paper Sec. 4.1 literal at
   `cost_model.py:60-65`; the 2026-08-24 closeout's anchor ambiguity). No
   anchor may be silently substituted anywhere in your artifacts. No
   assertion about the published state of the art, in either direction.
5. **P=512 re-derivation.** From the committed
   `RUN-WESOVOW-201692-001/raw-result.json` literals
   (`per_field[log2p=512].optimal.log2T`, `.log2M`) and the specification's
   grid/baseline (`log2T_DG = log2p/2`), re-derive the P=512 crossover
   `log2w_star` at `c=0` and the `log2w=80, c=0` sign under the authoritative
   anchor; machine-readable in `p512_rerivation.json` with the exact input
   literals quoted. State in-range/out-of-range against the tested
   `log2w ∈ {30..80}` grid.
6. **Provenance note.** Record, inside `source_fix_verification.md`, that
   `BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/defect_localization.md` cited the
   pre-merge source state (its branch lacked 7d188a7c3; its snapshot commit
   9d003a7d27f1 predates the fix's merge), and that the localization
   conclusion stands against that pre-fix state while the fix it describes is
   now merged. Note, do not edit, the predecessor artifact.

## Non-negotiable constraints

- No file under `experiments/EXP-WESOVOW-001/` or any `ledger/` path is
  edited, moved, or regenerated; write only inside your task directory.
- Write no ledger record, decision, or commit; no new run directory.
- `experiments_run: 1` (the verification re-execution only); no randomness
  (SEED=0); no network.
- Restate verbatim in every artifact: "The `P=512` crossover value and its
  `w=2^80` sign are **NOT citation-eligible**. This task does not lift that
  prohibition. Only a committed Coordinator decision on independently
  reviewed evidence can lift it." Name CORR-20260830-660318 as the intended
  filing vehicle for the versioned amendment, without pre-lifting the ban.
- Record requested policy `executor-implementation` alongside the model that
  actually answered; refuse rather than downgrade.

## Budget

wall_clock 4500 s · memory 4 GB · runs 1 (the verification re-execution)
