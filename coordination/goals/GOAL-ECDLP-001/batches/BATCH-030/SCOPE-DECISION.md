# BATCH-030 scope decision — gated repair/rerun of EXP-IT-001 v3 (RC-30)

**Selected:** The gated repair/rerun of EXP-IT-001 v3 under
SG-ECDLP-002 / H-IT-001 mandated as the exact next action of
DEC-20260731-036, encoded as `PA-IT-001-v3-rc30-repair-1-to-7.yaml`
(FIX-1..FIX-7) with Executor `RUN-IT-001-rerun*` and independent
Validator + Red Team before any official disposition.

## Batch-id ruling

BATCH-028 is CLOSED at ledger `4be3195f8` (DEC-20260731-036). BATCH-029
(CTRL-RT025-SPARSE-P-SUCCESS residual) is parked ledger-closed (DEC-040) and
is **not touched**. Under BUDGET-AMEND-20260730-001 the campaign budget is
maximum_batches = 50, so BATCH-030 is the next free batch id and fits the
budget. This batch supersedes nothing in BATCH-028/029 and rewrites no
ledger record.

## Claim ceiling

**Toy.** This batch can only ever produce a bounded toy measurement of the
EXP-IT-001 v3 charged transfer gate with working controls. NOT claimable
under any outcome: crypto-scale ECDLP behavior, asymptotic support for
HEUR-ISO-1 or any complexity claim, H-DS-001 support / S1_met, STR reopen,
lane death of any direction, GOAL-ECDLP-001 completion, promotion of any
KN-FIND. All four asymptotic-claim promotion gates remain **OPEN**. H-IT-001
stays `specified` until an admissible measurement exists; the scientific
question stays `inconclusive` until then.

## Forbid list (batch-wide)

- sub-rho / transfer-gate reading while the planted-path positive control is
  not recovered (FIX-3 gate).
- Reading any BATCH-028 R_xfer=0.0 / rho_special / rate_iso_1 value as
  evidence (censorship placeholders, not measurements).
- Editing (at this open or by any producer before the ledger archive):
  BATCH-028 queue/records, BATCH-029 records, `ledger/evidence/EV-IT-001.yaml`,
  `ledger/decisions/DEC-20260731-036.yaml`, `ledger/hypotheses/H-IT-001.yaml`,
  `ledger/goals/GOAL-ECDLP-001.yaml` (follow-up ledger commits only),
  H-DS-001, H-IC-001, H-STR-002, `tools/`, `experiments/EXP-IT-001/specification*.yaml`
  (immutable), existing implementation files, and existing run artifacts
  (incl. `runs/RUN-IT-001-bounded-toy/*`).
- Writing EV-IT-002 or DEC-20260801-002 at batch open (reserved for
  TASK-20260801-147).
- Executing specification v1 or v2; editing the v3 blob's `approved_by`.
- Fabricating commands, hashes, timings, exit codes, or run results.
- Claiming the C_special / transfer accounting is calibrated without the
  FIX-4 / FIX-6 disclosure in `transfer_gate_report.json`.

## The single next action

Execute the gated repair/rerun chain, in order, with a snapshot before every
independent review and a ledger archive after it:

1. TASK-20260801-142 snapshots the batch open (DEC-20260801-001 +
   QUEUE-AMEND + SCOPE-DECISION + PA-IT-001-v3-rc30-repair-1-to-7 +
   TASK-141 card).
2. TASK-20260801-143 (Executor) validates the frozen contract + repair
   overlay, implements the seven fixes, and runs the bounded rerun
   (`RUN-IT-001-rerun*`, deterministic seeds, toy 20/24/28-bit).
3. TASK-20260801-144 snapshots the full run package: ALL manifest-declared
   paths PLUS `HEUR_ISO_1_report.freeze.json` (13/13, command.txt,
   environment.json, stdout.log, stderr.log included).
4. TASK-20260801-145 (Validator, INDEPENDENT) verifies run integrity,
   controls, artifacts, and snapshot completeness against the seven fixes.
5. TASK-20260801-146 (Red Team, INDEPENDENT) challenges the interpretation
   and cost model and names the cheapest falsification control.
6. TASK-20260801-147 (ledger archive, runs alone) writes EV-IT-002 /
   DEC-20260801-002 (reserved) and any H-IT-001 status_history entry
   (status unchanged), then the GOAL-ECDLP-001 bind follows as a separate
   Coordinator commit (BATCH-028 pattern).

## Does not claim

SG-ECDLP-001 / SG-ECDLP-002 lane death; H-DS-001 support; S1_met; any
support or promotion; any asymptotic result; STR; a repaired instrument is
a precondition for future H-IT-001 evidence, never evidence itself.
