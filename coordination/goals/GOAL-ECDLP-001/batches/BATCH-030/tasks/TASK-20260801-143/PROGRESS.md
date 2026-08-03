# TASK-20260801-143 — BATCH-030 gated repair/rerun of EXP-IT-001 v3 (Executor)

**Role:** executor (`executor-implementation`; resolved `opencode/deepseek-v4-flash-free`, fallback disclosed)
**State:** run complete — post-run verification done, execution report written
**Gate:** RC-30 admission (FIX-1..FIX-7) per `PA-IT-001-v3-rc30-repair-1-to-7.yaml`
**Bound contract:** `experiments/EXP-IT-001/specification.v3.yaml` ONLY (immutable; not edited)

## Step trail

- **STEP-0 — Admission.** Verified the frozen v3 contract (approval
  `8f02ab4b`, amend freeze `d65c5e21`) and the repair overlay
  `PA-IT-001-v3-rc30-repair-1-to-7.yaml`. Confirmed write scope
  (`implementation/*`, `runs/RUN-IT-001-rerun/*`, `results/*`,
  `BATCH-030/tasks/TASK-20260801-143/*`) and the OBSERVATIONS-ONLY contract:
  no hypothesis-status change, no commits (TASK-144 archives).
- **STEP-1 — FIX-1 (Sage Integer casts).** Every Sage Integer leaf cast to
  Python `int` before `json.dump` (`heur_report['version']` and all other
  leaves in all eight declared JSON artifacts). `stderr.log` has no
  TypeError / no json.dump traceback; rerun exited 0; every declared
  artifact parses with `json.load`; `version` serializes as a JSON number.
- **STEP-2 — FIX-2 (working BFS) + root cause.** Found and fixed the root
  cause of the zero-edge BFS: the MOV-window search called `m.factor_list()`,
  which does not exist in Sage (it is `m.factor()`); the `except Exception`
  swallowed the AttributeError, so `has_mov_factor` was always False and the
  window search never ran in any prior run. Fixed to `m.factor()` (~line 900
  of `run_bounded_toy.py`). Rerun explores nonzero edges:
  `total_heur_edges_expanded=42` (13 cells > 0), `total_gate_edges_expanded=15428`
  (21 cells > 0). Total censorship is recorded with the contract-conformant
  reason `heur_stop_reason=censored_consistent_with_density_freeze_rho_zero`
  per cell — consistent with the frozen density measurement
  `rho_special_by_bits = {20: 0.0, 24: 0.0, 28: 0.0}` (exhaustive for
  bits=20/24, sample for bits=28), not a non-running instrument.
- **STEP-3 — FIX-3 (planted-path positive control).** Math constraint handled:
  anomalous curves (#E=p odd) can never have a rational 2-isogeny, so the
  planted control must be an MOV-special with even order. Probe confirmed the
  cheap MOV-1 control: p=2097653, j=1416, N*=524413, order 2097652 (even),
  embedding degree 1, 3 rational 2-isogenies, found in ~28s. Rerun:
  `planted_path_recovered=true`, `plant_field_source=bits_window_mov_search`,
  n_hops_planted=2, H_min=1, path_edges=[1416→480976] (non-empty),
  endpoint 480976 != search start 1416, `certificate_pass=true`
  (wrapper-reverified; toy pullback = direct solve at toy scale),
  R_xfer=0.1107 < 0.7.
- **STEP-4 — FIX-4 (C_special calibration).** `C_special` recalibrated in
  `it001_pure.py`: anomalous `ceil(log2(N))` and MOV family
  `C_special_MOV(p,k) = max(1, ceil(C_SPECIAL_MOV_CALIB_CONST * k * log2(p)))`
  (Miller-loop model, ~22 ops at toy), replacing the generic BSGS
  `ceil(0.886*sqrt(p**k))` (~1284 ops at toy) that inverted the control.
  `c_special_calibration` disclosure in `transfer_gate_report.json` records
  calibrated formula, prior modeled value, source (Smart 1999 / Araki-Satoh /
  MOV), and 10x sensitivity note (planted control still PASSES at 10x).
- **STEP-5 — FIX-5 (null plant in nonzero-cost cell).** The null plant is
  injected into a cell with honest (unplanted) cost
  `C_path_honest=729 > 0` (bits=20, seed=2026073101, index=0, j=1074805).
  `plant_detected=true` with predicate inputs recorded
  (`C_path_honest=729`, `C_path_reported=182`, `C_path_recomputed=729`).
- **STEP-6 — FIX-6 (per-attempt x 1/p_success OR deterministic-only).**
  `expected_cost_bookkeeping` in `transfer_gate_report.json` declares
  `overall_mode=deterministic_only` with the stated consequence: with
  rho_special=0 the transfer gate finds no special vertex, expected transfer
  cost is unbounded under probabilistic failure, so **no** expected-cost
  comparison to matched rho is claimed. `p_success` defined and sourced
  (frozen `F_hit(hops_max; rho, d=3)`), per-row `per_attempt_cost` recorded.
- **STEP-7 — FIX-7 (complete durable snapshot set).** `manifest.json`
  `artifact_paths` lists all 13 paths: the 12 original (manifest.json,
  raw-result.json, command.txt, environment.json, stdout.log, stderr.log,
  summary.json, HEUR_ISO_1_report.json, transfer_gate_report.json,
  concrete_cost_table.json, null_it_isogeny_transfer_report.json,
  execution_report.yaml) PLUS
  `experiments/EXP-IT-001/results/HEUR_ISO_1_report.freeze.json`.
  `HEUR_ISO_1_report.freeze.json` is valid JSON carrying
  `frozen_before_path_search=true` and the density freeze fields
  (rho_special_by_bits, universe hashes/cardinalities, F_hit tables) written
  BEFORE path search; `rate_iso_1_pass` is null in the freeze by design
  (KS/TAIL/RATE filled after sampling — the post-search
  `HEUR_ISO_1_report.json` carries the filled `rate_iso_1_pass=false`).
- **STEP-8 — Probes and cleanup.** Temporary probes
  (`_window_probe.py`, `_plant_smoke.py`, `_plant_probe.py`) created, run,
  and deleted. `py_compile` clean before launch. No stale artifacts left in
  `implementation/`.
- **STEP-9 — Full rerun and completion.** Launched
  `sage -python experiments/EXP-IT-001/implementation/run_bounded_toy.py`
  (Sage 10.9, `RUN_ID=RUN-IT-001-rerun`). Completed:
  `validity=completed_valid`, n_unplanted=21 (target 20), wall=1627.5s
  (budget 7200s), exit 0, stderr empty, `anomalies=[]`,
  `protocol_deviations=[]`. All artifacts verified post-run; execution report
  written to `execution_report.yaml`.

## Verdict (Executor — observations only)

All seven admission conditions FIX-1..FIX-7 are PASS per the amendment's
acceptance criteria. The rerun is a completed-valid bounded toy measurement
with working controls. **No** support/reject/heuristic-validation conclusion
is drawn by the Executor; `summary.json` records `observations_only=true` and
`no_support_reject_conclusion=true`. Note for Coordinator/Validator/Red Team:
`rate_iso_1_pass=false` (fraction R_xfer>=1.0 = 0.0 < 0.90) and all cells
censored under rho_special=0 — per spec.v3 line 635 S1 does not hold at toy;
F1 (>=2 unplanted R<0.7 with certs) not triggered (0 unplanted certs).
Claim ceiling stays **toy**; H-IT-001 stays `specified`.

## Handoff

- Snapshot task TASK-20260801-144 archives all 13 manifest-declared paths
  (13/13).
- Validator TASK-20260801-145 and Red Team TASK-20260801-146 review
  independently.
- Ledger TASK-20260801-147 writes reserved EV-IT-002 / DEC-20260801-002.
