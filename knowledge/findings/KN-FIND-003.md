---
id: KN-FIND-003
type: internal_finding
title: mu_3 supplies infinity-norm-1 MW relations on the frozen j=0 free-x family; polarisation
  Gram rank is not Shioda rank
tags:
- lifting
- xedni
- function-field
- mu3
- mordell-weil
- coefficient-bound
- methodology
- toy-scale
confidence: reported
status: established
internal_refs:
- EV-XEDN-002
- DEC-20260724-009
- H-XEDN-002
- EXP-XEDN-003
proof_status: empirical_only
proof_refs:
- ledger/evidence/EV-XEDN-002.yaml
- experiments/EXP-XEDN-003/execution-report.yaml
- experiments/EXP-XEDN-003/analysis.md
- experiments/EXP-XEDN-003/specification.yaml
added: '2026-07-24'
superseded_by: null
schema_repair_note: 'Committed with `evidence:`/`decision:` keys, which the internal_finding
  schema does not define, so its references were never cross-checked and its proof level was
  never stated. Repaired 2026-08-02 under CORR-20260802-007: the same two records are carried
  in internal_refs alongside the hypothesis and experiment the evidence itself names, and
  proof_status is set to the conservative empirical_only. No claim, scope or strength in the
  body text is changed.'
---

# KN-FIND-003

On the frozen EXP-XEDN family `y²=x³+b(t)` with `a=0` (hence `j=0`) at primes
`p≡1 mod 3`, free-x integral sections of shape `deg x≤2`, `deg y≤3` accepted by
the frozen `is_square_poly` predicate organize into `μ₃` orbits satisfying
`S+wS+w²S=O`. Those relations have infinity-norm 1 and specialise to O on smooth
fibres. Across `p∈{7,13,19,31}` the shortest observed relation among free-x
sections therefore has `max_|coeff|=1` with no growth vs `log p`.

Separately, the polarisation height Gram built from
`⟨P,Q⟩=ĥ(P+Q)-ĥ(P)-ĥ(Q)` with `ĥ=(1/2)max(deg num x, deg den x)` can report
ranks above the Shioda–Tate bound `r≤8` even when the height-control
`deg(num x(nS))=2n²` holds. Treat that Gram as diagnostic only; do not equate
its rank with geometric Mordell–Weil rank without local corrections.

Scope: toy isotrivial family only; not a closure of candidate B2 or of
non-isotrivial / number-field xedni.
