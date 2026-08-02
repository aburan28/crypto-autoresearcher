---
id: KN-FIND-018
type: internal_finding
title: Scoped finding from EV-BKKMV-001
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-BKKMV-001
- DEC-20260718-011
- EXP-BKKMV-001
- DEC-20260722-003
proof_status: empirical_only
proof_refs:
- research/THM_BKKMV1.md
- DEC-20260722-003
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy panel m=3,4,5: MV_m=(m−1)!·2^((m−1)(m−2)) exact with MV/Bézout_box=1; growth law certified on that range only, not m≥6.

## Provenance
- Evidence: `EV-BKKMV-001` (strength: replicated)
- Decision: `DEC-20260718-011` (supported_scoped)
- Experiment: `EXP-BKKMV-001`
- Hypothesis: `H-BKKMV-001`
- Later theorem upgrade (not restated as this EV claim): `THM_BKKMV1` / `DEC-20260722-003` prove the m≤5 sectioned barrier; C1 all-m gap remains open.

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Empirical EV claim is not itself the theorem; theorem covers m≤5 proved fragment only.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-011` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- Cross-note: `DEC-20260722-003` / `THM_BKKMV1` prove m≤5 sectioned box-saturation ⇒ MV law (N4); do not treat this draft as proving m≥6.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- All-m box-saturation theorem (C1 open)


