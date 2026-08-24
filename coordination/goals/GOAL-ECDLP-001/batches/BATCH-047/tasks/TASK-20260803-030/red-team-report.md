# Red Team Report — RUN-IT-001-rc47 / BATCH-047

**Report ID:** RT-20260803-030  
**Verdict: FAIL**

See `verdict.yaml` for the full structured report with all findings and carryovers.

## Three Blocking Objections

**RT-047-B1**: The planted path positive control (CTRL-PLANTED-PATH-POS) starts
from a special curve (`start_det.embedding_degree=1, any_special=true`), directly
violating R5-FIX-PRESERVE-M1's requirement for `start_j_speciality: nonspecial`.
Required acceptance-criteria fields (`path_is_reverse_of_planted`,
`pullback_evaluated`, `relation_reverified`) are absent. Informal "FIX-3" cited
in run output does not appear in the frozen amendment.

The structural cause: trace/group-order is an isogeny-class invariant for
ordinary curves. Anomalous curves (trace=1, N=p) occupy their own separate
isogeny class and cannot be reached from generic non-anomalous curves via
ordinary 2-isogeny walks. This explains rho_special=0 at all tested bit sizes
and is consistent with the class-invariant property.

**RT-047-B2**: Run-id `RUN-IT-001-rc47` is not in the amendment's
`reserved_run_ids`; mode `smoke_then_measure` is not a frozen mode. The manifest
cites DEC-20260803-003 as `batch_open_decision` for BATCH-047, but
DEC-20260803-003 opens BATCH-046. No distinct BATCH-047 opening decision is cited.

**RT-047-B3**: `run_bounded_toy.py` was modified at runtime (dirty worktree).
Reproducibility from committed state cannot be confirmed.

## Narrowest Supported Statement

rho_special=0.0 for all three tested bit sizes (20, 24, 28-bit ordinary 2-isogeny
graphs). No transfer-gate measurement. No sub-rho claim. No H-IT-001 status change.
Toy tier only.

## Key Structural Observation

The class-invariant property (ordinary isogenies preserve trace of Frobenius)
implies that any anomalous curve (trace=1) is isolated from generic curves
(trace≠1) in the ordinary isogeny graph. If true at all scales, rho_special=0
is not a computational artifact but a mathematical fact. This deserves formal
analysis before further Executor work on the current H-IT-001 formulation.
