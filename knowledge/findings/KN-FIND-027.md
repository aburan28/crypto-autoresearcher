---
id: KN-FIND-027
type: internal_finding
title: Scoped finding from EV-SIG-005
tags:
- ecdlp
- prime-field
- toy
- internal-finding
confidence: reported
internal_refs:
- EV-SIG-005
- DEC-20260720-001
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
---
## Scoped claim
Toy boolean Semaev t=3, n≤24: D4 law (2n/3+1) holds through n=24; D5-born residual non-monotone through n=18; D=6 null baseline invalid at tested n=9 (C5 fail) — cascade claims admissible only for D≤5.

## Provenance
- Evidence: `EV-SIG-005` (strength: replicated)
- Decision: `DEC-20260720-001` (supported_scoped)
- Experiment: `EXP-SIG-005`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only (n≤24; cascade valid D≤5). Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Does not assert null invalidity for untested D>6 sizes.

## Key claims (verified here)
- The Coordinator decision `DEC-20260720-001` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: toy / boolean-Semaev / n≤24 prefix is in the scoped claim sentence.
- N3 repair: cause is D=6 null C5 failure at n=9; cascade admissible only for D≤5 — not blanket “D≥6 null baseline invalid”.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Null-baseline invalidity for all D≥6 / untested sizes
- D6 birth-law residual magnitudes (measurement retracted as invalid)
