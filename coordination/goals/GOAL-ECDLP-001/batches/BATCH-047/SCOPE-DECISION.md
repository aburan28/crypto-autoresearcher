# BATCH-047 scope decision

BATCH-047 re-executes the EXP-IT-001 isogeny-transfer cost gate under frozen
PA-IT-001-v3-rc45-repair-5, closing the three control voids that rendered
BATCH-046 inconclusive (DEC-20260803-004 BF-1..BF-3).

## What this batch does

One bounded Executor run (RUN-IT-001-rc47) in smoke mode, immediately followed
by the reserved measure seeds if and only if all three smoke controls pass.
Independent Validator and Red Team review the complete run package.

Three specific repairs bind the Executor:

**BF-1 closure — CTRL-ANOMALOUS-TRACE1 at bits=20.**
The planted endpoint must satisfy #E(F_p) ≡ 0 (mod N) with trace t ≡ 1 (mod N)
in the Smart sense (anomalous: N = p). Embedding-degree-1 MOV endpoints are not
Smart anomalous and are contract-invalid as the anomalous positive control.
The Executor must produce `anomalous_trace1_certificate.json` with `verified: true`,
record `c_special_formula_id: C_special_smart`, and use
`C_special = ceil(c_smart * log2(p))` with `c_smart = 8` as the sole anomalous
pass threshold. Using 20*(log2 N)^2, ceil(2*sqrt(N*)), or any MOV formula as the
anomalous pass threshold is contract-invalid and triggers immediate abort.

**BF-2 / BF-3 closure — CTRL_NULL_IT_PLANT and CTRL-NULL-PACKAGING-GATE.**
The Executor must persist a non-empty null plant edge ledger (at least one row)
by running recompute_null_plant_from_ledger.py against the raw edge data; the
live CTRL-NULL-PACKAGING-GATE must run and actually reject a pre-registered
synthetic R_xfer < 0.7 claim.

**Provenance rebind.**
The manifest `batch_id`, `task_id`, and `execution_report` path must reference
BATCH-047 / TASK-20260803-027, not any prior batch.

## What this batch is NOT

Not an attack. Not a cryptanalytic result. Not a result above toy tier (20–28
bit prime-order subgroups). Not a hypothesis-status transition. H-IT-001 stays
`specified` regardless of outcome; only a completed-valid run with all controls
passing and a ratio comparison can move it. All four asymptotic-claim promotion
gates remain open. GOAL-ECDLP-001 completion is not claimable from this batch
under any outcome.

## Forward path

If smoke controls pass and measure seeds run: Validator + Red Team review the
full package; Coordinator decides evidence strength and whether to advance
H-IT-001 toward `supported` or `weakened` at toy tier.

If any smoke control fails: record as `inconclusive` (infrastructure / harness
void), carry the specific void forward as a named repair obligation, and open
a successor batch targeting only the remaining void.

## Pareto declaration

Non-solver control and measurement batch. `dominated_by` is not_applicable for
the control fixes; the measurement arm competes against matched Pollard rho
(0.886 sqrt(N)). All three SOTA deltas are not_applicable until a sub-rho
transfer ratio is demonstrated with certificates.
