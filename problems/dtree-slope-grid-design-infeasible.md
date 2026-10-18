# EXP-DTREE-001 slope grid was design-infeasible at the frozen seed

- **Status:** `open`
- **Kind:** implementation gap (instance generator) with an unrelated confound
- **Affected work:** H-DTREE-001 (`inconclusive`, DEC-20260809-91d4c7); EV-DTREE-b47c19, EV-DTREE-2e8f6a; EXP-DTREE-001; [KN-OPEN-5b3a08](../knowledge/open-problems/KN-OPEN-5b3a08.md)
- **Next action owner:** Coordinator (amendment or successor experiment)
- **Last updated:** 2026-10-18

## Problem

We cannot cite EXP-DTREE-001 for or against HEUR-001 at the C1 exact-enumeration slope fit, because the frozen grid yielded fewer than 6 non-saturated cells and the protocol's own stop rule recorded `design_infeasible` before the slope could be measured.

## Evidence and uncertainty

- **Observed:** 0 qualifying cells among 18 tested (curve, B') values, recomputed by hand from RUN-DTREE-001/raw.json in DEC-20260809-91d4c7. Root cause named there: `generate_instance` only requires a largest prime factor of at least 5, so the 8/10/12-bit curves have tiny subgroups. The decision classifies this as "infrastructure/design signal, not evidence against (or for) HEUR-001" (AGENTS.md rule 5).
- **Suspected explanation:** the C2 main-curve pattern may be driven by cofactor size and whole-curve factor-base sampling (KN-OPEN-5b3a08 Q2); EXP-DTREE-001 could not separate this.
- **Later work (checked 2026-10-18):** DEC-20260813-173d38 approved EXP-SEMAEV-a097b5 as implementation-only for the shared `s4_expr` repair (KN-OPEN-5b3a08); it ran no trial. No amendment or successor re-attempting the slope grid was found among decisions citing EXP-DTREE-001 or H-DTREE-001.
- **What this evidence does not establish:** any slope, and nothing for or against depth-2 descent.

## What would unblock it

- [ ] A versioned protocol amendment (empty `experiments/EXP-DTREE-001/amendments/`) changing only the tiny-curve seed policy to reach subgroup order n >= 80, or a successor experiment inheriting the C2 results unchanged.
- [ ] A matched `scope="target_subgroup"` versus `full_curve` factor-base arm, now that the option exists in `harness/semaev.py`.

## Next discriminating step

- **Action or proof obligation:** the C1/C2 actions in DEC-20260809-91d4c7 `next_actions`, plus the matched factor-base control above.
- **Outcomes and next actions:** per the decision; a repeat design stop is recorded here.
- **Recheck trigger:** Coordinator approval of the amendment or successor.

## Resolution and history

2026-10-18: record opened from the owner's index-calculus integrity review. Unresolved.
