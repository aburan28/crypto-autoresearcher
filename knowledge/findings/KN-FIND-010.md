---
id: KN-FIND-010
type: internal_finding
title: Joint deg-x≤3 / deg-b=10 non-isotrivial free-x still admit inf-norm-1 MW relations
  at p≤19; p=31 density-blocked
tags:
- lifting
- xedni
- function-field
- non-isotrivial
- mordell-weil
- coefficient-bound
- methodology
- toy-scale
confidence: reported
status: established
internal_refs:
- EV-XEDN-005
- DEC-20260730-001
- H-XEDN-005
- EXP-XEDN-006
proof_status: empirical_only
proof_refs:
- ledger/evidence/EV-XEDN-005.yaml
- experiments/EXP-XEDN-006/execution_report.md
- experiments/EXP-XEDN-006/specification.yaml
added: '2026-07-30'
superseded_by: null
schema_repair_note: 'Committed with `evidence:`/`decision:` keys, which the internal_finding
  schema does not define, so its references were never cross-checked and its proof level was
  never stated. Repaired 2026-08-02 under CORR-20260802-007: the same two records are carried
  in internal_refs alongside the hypothesis and experiment the evidence itself names, and
  proof_status is set to the conservative empirical_only. No claim, scope or strength in the
  body text is changed.'
---

# KN-FIND-010

On plant-discovered non-isotrivial surfaces `y²=x³+a(t)x+b(t)` with `a≠0`,
`deg a≤2`, `deg b=10`, and non-constant `j`, free-x sections `deg x≤3`,
`deg y≤5` admit group-law-verified Mordell–Weil relations with infinity-norm 1
at `p∈{7,13,19}` (EXP-XEDN-006 / EV-XEDN-005). Slope of max_|coeff| vs log p
is 0 on those measurable sizes. μ₃ orbits remain absent.

At `p=31`, the same plant-and-enumerate census found almost exclusively
single-slot surfaces: 48 analyzed, 2 eligible, 0 verified short relations
under budget. This is a free-x **relation-density** obstruction, not an
observed coefficient blow-up. The joint degree-shape transfer of the
coefficient-bound story therefore holds only for the measured sizes; it is
not established at p=31.

Scope: toy only; not B2 / crypto-scale.
