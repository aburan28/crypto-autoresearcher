---
id: KN-FIND-023
type: internal_finding
title: Scoped finding from EV-REP-002
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-REP-002
- DEC-20260716-002
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy Edwards-admitting curves, m=3: d_reg=2 invariant Weierstrass vs twisted Edwards; model not a solving-degree lever at that scope.

## Provenance
- Evidence: `EV-REP-002` (strength: replicated)
- Decision: `DEC-20260716-002` (reject_scoped)
- Experiment: `EXP-REP-002`
- Hypothesis: `H-REP-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260716-002` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


