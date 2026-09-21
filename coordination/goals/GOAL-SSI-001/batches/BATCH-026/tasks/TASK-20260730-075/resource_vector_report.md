# Resource-vector ledger report — TASK-20260730-075 / BATCH-026

## What was ledgered

A checkable **symbolic** Q/S/P/C(+H) resource-vector ledger against frozen
FC0-EXT-PKG-SSI-001 / BATCH-022 scaffolding and BATCH-023
`peak_liveset_partial`, using BATCH-018 `joint_qspc_ledger` only as a field
template and STOPPING negative control (FAIL; τ not invented).

| Field | Meaning (short) | Status | Joint finiteness | Numeric width |
|-------|-----------------|--------|------------------|---------------|
| Q | Oracle/query charges through a stopping law | `symbolic_only` | false | not_invented |
| S | Non-oracle sieve / T-gate charges | `symbolic_only` | false | not_invented |
| P | Postprocessing charges | `not_instantiated` | false | not_invented |
| C | Classical recovery / reconstruction | `not_instantiated` | false | not_invented |
| H (optional) | Terminal tail + verification | `not_instantiated` | false | not_invented |

Cross-links retained:

- **peak_liveset_partial** (BATCH-023): peak = max over stage symbolic object
  counts (5), not sum; no widths; no peak-byte bound.
- **f_union_ledger_partial** (BATCH-025): symbolic \(U = \bigcup F_* \subseteq F\);
  no probabilities; QM-ERROR retained at this status.

Write-scope harness: `python3 -m resource_vector_harness.run_harness`
(from this task directory). Checks field statuses, joint-finiteness flags,
and absence of forbidden clearance claims.

## What remains open

- **QM-STOPPING:** open. No source-compatible Verify-relative τ; no jointly
  finite \(E[\sum Q/\sum S/\sum P/\sum C(+H)]\). BATCH-018 FAIL retained.
- **Numeric widths / peak-byte bound:** unresolved; not invented here.
- **Joint expectations under a stopping law:** not established.
- **QUERY_MEMORY:** unreconciled (`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`).
- **QM-ERROR:** retained `f_union_ledger_partial` (no probability composition).
- **CollimationSieve@6f9188e4:** host gap retained; no APIs invented.
- **BATCH-020 `no_admissible_pin`** and **ttm-v2** finite ideal-choice panel
  retained; not equated with BATCH-014.

## Claim boundary

**Supported:** zero-compute symbolic resource-vector field ledger
(`resource_vector_partial`) advancing QM-MEMORY-MAP from
`peak_liveset_partial` without clearance.

**Excluded:** QUERY_MEMORY / MEMORY-MAP / STOPPING / ERROR clearance;
PIN_COMPLETE; invented τ or joint finiteness; numeric widths; peak-byte
bounds; probabilities; security bits; breakthrough or goal completion;
CollimationSieve API invention; BATCH-014 equivalence; curve/isogeny/quantum
circuit computation.
