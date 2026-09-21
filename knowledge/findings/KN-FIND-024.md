---
id: KN-FIND-024
type: internal_finding
title: Scoped finding from EV-SIG-002
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-SIG-002
- DEC-20260718-017
- EXP-SIG-002
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy boolean Semaev t=3, n=12..21, D≤4: non-rewritable D4 residual exists, null residual=0, grows with n (counts later refined by EV-SIG-004).

## Provenance
- Evidence: `EV-SIG-002` (strength: replicated)
- Decision: `DEC-20260718-017` (supported_scoped)
- Experiment: `EXP-SIG-002`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Exact D4 counts superseded by EV-SIG-004 / KN-FIND-026.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-017` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Canonical exact D4 residual series (see KN-FIND-026)


