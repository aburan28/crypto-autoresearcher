---
id: KN-FIND-011
type: internal_finding
title: Full-enum densification recovers inf-norm-1 free-x MW relations at p=31 on joint deg-x≤3
  / deg-b=10 family
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
- EV-XEDN-006
- DEC-20260730-002
- H-XEDN-005
- EXP-XEDN-006
- EXP-XEDN-007
proof_status: empirical_only
proof_refs:
- ledger/evidence/EV-XEDN-006.yaml
- experiments/EXP-XEDN-006/execution_report.md
- experiments/EXP-XEDN-006/specification.yaml
- experiments/EXP-XEDN-007/execution_report.md
- experiments/EXP-XEDN-007/specification.yaml
added: '2026-07-30'
superseded_by: null
schema_repair_note: 'Committed with `evidence:`/`decision:` keys, which the internal_finding
  schema does not define, so its references were never cross-checked and its proof level was
  never stated. Repaired 2026-08-02 under CORR-20260802-007: the same two records are carried
  in internal_refs alongside the hypothesis and experiment the evidence itself names, and
  proof_status is set to the conservative empirical_only. No claim, scope or strength in the
  body text is changed.'
---

# KN-FIND-011

Under full free-x enumeration (`deg x≤3`) on plant-discovered non-isotrivial
surfaces with `deg a≤2`, `deg b=10` at `p=31`, EXP-XEDN-007 recovered two
group-law-verified Mordell–Weil relations with infinity-norm 1 (120 surfaces
analyzed; 14 eligible). This overturns the EXP-XEDN-006 sampling-regime
density block at p=31 without observing coefficient growth.

Together with EXP-XEDN-006 at `p∈{7,13,19}`, the joint degree-shape window
shows `max_|coeff|=1` on all tested sizes, with sparse but nonempty
relations at p=31.

Scope: toy only; not B2 / crypto-scale.
