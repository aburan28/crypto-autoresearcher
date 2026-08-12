---
id: KN-FIND-020
type: internal_finding
title: Scoped finding from EV-EQJ-001
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-EQJ-001
- DEC-20260718-006
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy p≤2^12, m=4 fibers: isotypic blocking yields no LA cost gain (full-rank survivors; 4× all-blocks cost); only orbit storage matching FHJRV symmetrization.

## Provenance
- Evidence: `EV-EQJ-001` (strength: replicated)
- Decision: `DEC-20260718-006` (reject_scoped)
- Experiment: `EXP-EQJ-001`
- Hypothesis: `H-EQJ-001`

## Limits
Toy-scale only (DEC-20260718-006: p≤2^12, m=4, 3 seeds). Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-006` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: `p≤2^12` is in the scoped claim sentence (DEC-20260718-006 limitations).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


