# EXP-IT-001 implementation note (TASK-20260801-143 / RUN-IT-001-rerun)

Bound contract: `experiments/EXP-IT-001/specification.v3.yaml` (v3 / PA-IT-001-v3-rc45-repair-5) plus
repair overlay PA-IT-001-v3-rc45-repair-5 (FIX-1..FIX-7).

## What was implemented

- Density freeze for HEUR-ISO-1 (`rho_special`, `F_hit` tables, `d=3`) **before** path search
- Charged transfer gate with measured/modeled cost ledger labels; `R_xfer` = MIN over certificates
- CTRL-PLANTED-PATH-POS, matched rho/BSGS (modeled + calibration proxy), IDEA-011 null object
- CTRL-NULL-IT-PLANT packaging plant on designated bits=20 / seed=2026080347 cell
- Independent DL re-verify via `harness.toycurve.EllipticCurve.mul` when a solve is claimed
- FIX-1: Sage Integer -> int() casts via `_jsonable()` before every json.dump
- FIX-2: BFS runs on every cell (no rho==0 short-circuit); per-cell + total edge counters
- FIX-3: planted-path start requires a rational 2-isogeny; recovery requires H_min >= 1,
  non-empty path_edges, endpoint != start, verified certificate
- FIX-4: C_special calibrated to Smart/MOV ~O(log p) cost; modeled-vs-true disclosed
- FIX-5: null plant injection cell's honest cost C_path_honest > 0 required + disclosed
- FIX-6: per-attempt x inverse-success-probability term (or explicit deterministic-only)
- FIX-7: manifest declares all 12 paths + HEUR_ISO_1_report.freeze.json (13 total)

## Deviations / resource stops

See run manifest `protocol_deviations` and `anomalies`.

## Non-actions

- No git commit (TASK-20260801-144 archives)
- Did not execute specification.yaml / specification.v2.yaml
- Did not edit `approved_by` in v3
- Did not touch EXP-DS-001 / BATCH-026 / H-DS-001 / H-IC-001 / H-STR-002
- Did not modify runs/RUN-IT-001-bounded-toy/*
