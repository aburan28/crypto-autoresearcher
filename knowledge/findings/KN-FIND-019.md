---
id: KN-FIND-019
type: internal_finding
title: Scoped finding from EV-BKKMV-002
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-BKKMV-002
- DEC-20260722-003
- EXP-BKKMV-002
proof_status: empirical_only
proof_refs:
- research/THM_BKKMV1.md
- DEC-20260722-003
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy m=6 extension: MV_6=125829120=5!·2^20 on 6/6 with MV/Bézout_box=1; hulls box-saturated at finite p (2/30 sections lost 30–60 hull-interior monomials; corners intact; MV unchanged); literal support saturation is char-0/generic-t; beyond m=6 unmeasured; all-m law remains C1 open.

## Provenance
- Evidence: `EV-BKKMV-002` (strength: replicated)
- Decision: `DEC-20260722-003` (supported)
- Experiment: `EXP-BKKMV-002`
- Hypothesis: `H-BKKMV-001`
- Theorem track: `research/THM_BKKMV1.md` (m≤5 proved; m=6 certified empirically; C1 open)

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Finite-p saturation is a hull statement per DEC-20260722-003 / EV-BKKMV-002; literal full-box support is not claimed at m=6.

## Key claims (verified here)
- The Coordinator decision `DEC-20260722-003` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N1 repair: wording is hull/MV (DEC-20260722-003 limitations; EV-BKKMV-002 observations), not unqualified literal box saturation.
- N4 cross-note: THM_BKKMV1 proves m≤5; m=6 is certificate; C1 remains open.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Literal support saturation of every m=6 section at finite p
- All-m box-saturation theorem (C1 open)


