# H-STR-002 was weakened for missing artifacts, not by a measurement that failed

- **Status:** `open`
- **Kind:** evidence-integrity gap (absent run records and non-reproducing headline numbers)
- **Affected work:** H-STR-002 (`weakened`, DEC-20260727-009); EV-STR-002, EV-STR-003; EXP-STR-002, EXP-STR-003; KN-OPEN-006
- **Next action owner:** Coordinator
- **Last updated:** 2026-10-18

## Problem

We cannot cite H-STR-002 as either supported or refuted by a phi-orbit factor-base experiment, because the evidentiary basis of the earlier `supported` verdict was absent from the repository and the `weakened` verdict records that failure of evidence, not a result about displacement rank.

## Evidence and uncertainty

- **Observed (DEC-20260727-009, R1):** EV-STR-002 carries `run_ids: []`; no run record for B = 55, 204 or 397 exists in any ref or object (247 refs, 47,983 objects searched); the committed `main()` raises IndexError at `harness/endomorphism_la.py:451` whenever B mod 3 != 0 (B = 55 and 397); `rand_alpha` 53, 200, 387 re-measure as 54, 201, 382 (3 of 3 differ); both records were rewritten in place after archival. The decision calls this "an evidence-integrity failure, not a mathematical one".
- **Derived or proved:** not established.
- **Later work (checked 2026-10-18):** EXP-STR-004 was executed (DEC-20260730-014 `inconclusive`; EV-STR-004, 28/28 runs `completed_valid`, 654/654 certificates pass, `instrument_verdict: mixed`, direction `neutral`, "No H-STR-002 mechanism test"). It repaired the artifact gap for its own 14 cells but did not test the phi-orbit mechanism, so `weakened` still rests on the DEC-20260727-009 grounds.
- **What this evidence does not establish:** that the phi-invariant factor base does or does not give displacement rank O(1). The `status_scope` limits `weakened` to four j=0 curves and the toy tier; the hypothesis is not `rejected`.

## What would unblock it

- [ ] A frozen-contract experiment that tests the phi-invariant mechanism itself (EV-STR-004 tested only the displacement-rank instrument), with the truncation/closure artifact UC-2 controlled, factor-base and row-list sha256 per cell, criteria frozen first.
- [ ] Any batch authorization the campaign budget rules require.

## Next discriminating step

- **Action or proof obligation:** a mechanism-level successor to EXP-STR-004 designed from EV-STR-004's open confounds UC-1 and UC-2.
- **Outcomes and next actions:** a valid result moves H-STR-002 by a Coordinator decision; an instrument-only result changes nothing here.
- **Recheck trigger:** a Coordinator-approved successor contract.

## Resolution and history

2026-10-18: record opened from the owner's index-calculus integrity review. Unresolved. The H-STR-002 `weakened` status is left to the Coordinator.
