---
id: KN-FIND-021
type: internal_finding
title: Scoped finding from EV-FB-001
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-FB-001
- DEC-20260716-004
- H-FB-001
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy p~2^14, m=3, d≤12 (subgroup base excluded): tested FB structures leave d_reg, yield, and solve-cost scaling invariant vs random FB.

## Provenance
- Evidence: `EV-FB-001` (strength: replicated)
- Decision: `DEC-20260716-004` (reject_scoped)
- Experiment: `EXP-FB-001`
- Hypothesis: `H-FB-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Subgroup base excluded per EV-FB-001 / DEC-20260716-004.

## Key claims (verified here)
- The Coordinator decision `DEC-20260716-004` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: subgroup-base exclusion is in the scoped claim sentence (EV-FB-001 boundaries).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Subgroup-base factor-base structures (excluded)


