---
id: KN-FIND-017
type: internal_finding
title: Scoped finding from EV-BKK-001
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-BKK-001
- DEC-20260718-005
- EXP-BKK-001
- H-BKK-001
- DEC-20260722-003
proof_status: empirical_only
proof_refs:
- research/THM_BKKMV1.md
- DEC-20260722-003
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy p≤1009, m∈{3,4,5}: target-sectioned Semaev systems are Newton box-saturated (MV=multigraded Bézout); no support-aware BKK solve-cost advantage in tested scope.

## Provenance
- Evidence: `EV-BKK-001` (strength: replicated)
- Decision: `DEC-20260718-005` (reject_scoped)
- Experiment: `EXP-BKK-001`
- Hypothesis: `H-BKK-001`
- Later theorem upgrade (not restated as this EV claim): `THM_BKKMV1` / `DEC-20260722-003` prove the m≤5 sectioned barrier; C1 all-m gap remains open.

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Empirical EV claim is not itself the theorem; theorem covers m≤5 proved fragment only.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-005` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- Cross-note: `DEC-20260722-003` / `THM_BKKMV1` later upgrade H-BKK-001's scoped rejection with a proved m≤5 barrier (N4).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- All-m box-saturation theorem (C1 open)


