# CTRL-B protocol repair — TASK-20260725-701

## Purpose
Revise the TASK-20260725-689 CTRL-B freeze to discharge RT-20260725-691
(REVISE / DEC-20260725-023 / EV-DREG-006): closed quarantine machine-checks,
split authorization wording, and support/deletion-set hash admission beside
`ncols==174035`. Mathematical CTRL-B definition is unchanged.

## Inference
- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001

Fallback is infrastructure/policy, not mathematical evidence.

## Authorization (CTRL-AUTH-SPLIT)
Review-only repair. **No rank measurement** in BATCH-004.

| Gate | Unlocks |
|---|---|
| Protocol-review PASS | Schedule a later executor task only (`after_protocol_review_pass_allows_execution_only`) |
| CTRL-B execution admitted (receipt + all admission metrics) | Cite measured `deficit_genuine` as the D6 structural number |

Protocol PASS is not a d_reg result, not a pin of `deficit_genuine`, and not an
H-DREG-001 status change.

## RT objections closed

### CTRL-Q-MACHINE (OBJ-691-1)
Q1–Q4 are closed booleans under checker `CTRL-B-Q-MACHINE-v1` on named fields:
- **Q1** — forbid `structural_metric_id ∈ {deficit_vs_sr_pred, raw_deficit}` with
  value 17947; allowlisted quarantine-field mentions of 17947 only.
- **Q2** — `raw_headline_status == quarantined_confounded` on any D6-citing EV/DEC.
- **Q3** — before admission: only
  `genuine_support_independent_deficit_lower_bound >= 1931` or the pinned D5
  series tuples/run IDs from DEC-GOAL-DREG-001-B002 may be structural; not 17947
  and not pre-admission `deficit_genuine`.
- **Q4** — after admission: `structural_d6_number` equals measured
  `deficit_genuine` from the admitted receipt (`metric_id == deficit_genuine`);
  N/A before admission.

### CTRL-AUTH-SPLIT (OBJ-691-2)
Replaced overloaded `after_pass_*` with
`after_protocol_review_pass_allows_execution_only` vs
`after_ctrl_b_execution_admitted_allows_deficit_genuine_citation`.

### CTRL-SUPPORT-HASH (OBJ-691-3)
Pinned CTRL-A system hashes from
`support_confound_probe.json` and require, alongside `restricted_ncols==174035`:
- `deleted_ncols==16016`
- `deleted_set_equals_null_minus_sem`
- `deleted_degree_histogram == {6: 16016}`
- `restricted_support_hash` / `deleted_set_hash` equal digests from
  `sha256_sorted_monomial_canonical_v1` on the hash-matched rebuild

This blocks the ncols-only mutation (delete any other 16016 columns).

### Scope guard (OBJ-691-4)
Preserved under `always_not_claimed`.

## Why CTRL-B (unchanged math)
BATCH-002: null rank = sr_pred = 156520; sem rank = 138573; raw deficit 17947
vs sr_pred confounded by 16016 deg-6 support-gap columns. Genuine deficit ∈
[1931, 17947]. CTRL-B ranks null on sem's exact support to pin the exact value.

## Pending measurement
Honest degree-axis observable remains the pinned D5 series
(1322 / 1862 / 1999 at n=12/15/18). Raw 17947 stays quarantined.

## Supersedes
- Protocol card TASK-20260725-689 (RT-691 REVISE)
- Failed_infrastructure card TASK-20260725-621 (non-mathematical)
