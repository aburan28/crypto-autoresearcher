# H-STR-002 support was withdrawn on artifact, ablation and cost grounds

- **Status:** `open`
- **Kind:** evidence-integrity gap, scoped measured ablation, and missing cost evidence
- **Affected work:** H-STR-002 (`weakened`, DEC-20260727-009); EV-STR-002, EV-STR-003; EXP-STR-002, EXP-STR-003; KN-OPEN-006
- **Next action owner:** Coordinator
- **Last updated:** 2026-10-19

## Problem

DEC-20260727-009 withdrew `supported` using three distinct grounds: artifact defects, an independently reproduced comparison of the displacement metric, and missing evidence for a complete cost comparison. Its scoped measurement remains evidence about the tested collection convention. The decision does not reject the general phi-orbit mechanism; that separate limit must not erase the measured ablation.

## Evidence and uncertainty

- **Observed (DEC-20260727-009, R1):** EV-STR-002 carries `run_ids: []`; no run record for B = 55, 204 or 397 exists in any ref or object (247 refs, 47,983 objects searched); the committed `main()` raises IndexError at `harness/endomorphism_la.py:451` whenever B mod 3 != 0 (B = 55 and 397); `rand_alpha` 53, 200, 387 re-measure as 54, 201, 382 (3 of 3 differ); both records were rewritten in place after archival. The decision calls this "an evidence-integrity failure, not a mathematical one".
- **Observed (DEC-20260727-009, R2/R4):** under the same phi shift, collection rule and no-append convention, changing only the factor base gives alpha = (27, 52, 197, 386) for the phi-invariant arm and (27, 52, 199, 387) for the random-base arm, at B = (27, 55, 204, 397). The decision records this as an archived, independently reproduced contradiction of EV-STR-002's inference that the factor base alone induces constant displacement rank. This is a scoped comparison under the stated convention, not a refutation of the general mechanism.
- **Missing cost evidence (R3):** the recorded incidence rows lack target coefficients/right-hand sides, the measured rank deficiencies are (4, 6, 30, 67), and the headline instances have no archived complete baseline. The decision classifies this as an absence, not a refutation.
- **Derived and unresolved:** closing a row list under the shift makes it equivariant by construction. The separate instrument-confound premise remains `UNADJUDICATED`; the decision expressly does not use the withdrawn comparative probe as a ground for weakening. The general mechanism is not rejected.
- **Later work (checked 2026-10-18):** EXP-STR-004 was executed (DEC-20260730-014 `inconclusive`; EV-STR-004, 28/28 runs `completed_valid`, 654/654 certificates pass, `instrument_verdict: mixed`, direction `neutral`, "No H-STR-002 mechanism test"). It repaired the artifact gap for its own 14 cells but did not test the phi-orbit mechanism, so `weakened` still rests on the DEC-20260727-009 grounds.
- **What this evidence does not establish:** that the phi-invariant factor base does or does not give displacement rank O(1) in general. The recorded comparison covers four j=0 curves with B = (27, 55, 204, 397); the hypothesis remains `weakened`, not `rejected`.

## What would unblock it

- [ ] A frozen-contract experiment that tests the phi-invariant mechanism itself (EV-STR-004 tested only the displacement-rank instrument), with the truncation/closure artifact UC-2 controlled, factor-base and row-list sha256 per cell, criteria frozen first.
- [ ] Any batch authorization the campaign budget rules require.

## Next discriminating step

- **Action or proof obligation:** a mechanism-level successor to EXP-STR-004 designed from EV-STR-004's open confounds UC-1 and UC-2.
- **Outcomes and next actions:** a valid result moves H-STR-002 by a Coordinator decision; an instrument-only result changes nothing here.
- **Recheck trigger:** a Coordinator-approved successor contract.

## Resolution and history

2026-10-18: record opened from the owner's index-calculus integrity review. Unresolved. The H-STR-002 `weakened` status is left to the Coordinator.

2026-10-19: PR review corrected the summary to retain DEC-20260727-009 R2's measured ablation and R3's cost-evidence gap alongside R1's artifact defects. The decision and hypothesis remain unchanged; no new experiment was run.
