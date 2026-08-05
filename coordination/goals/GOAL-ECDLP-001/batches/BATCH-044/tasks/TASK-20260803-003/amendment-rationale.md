# Amendment rationale — TASK-20260803-003

**Amendment ID:** `PA-IT-001-v3-rc44-repair-4`  
**Experiment:** `EXP-IT-001` / `H-IT-001` / `GOAL-ECDLP-001`  
**Batch:** `BATCH-044`  
**Closes:** `RT-20260802-314` (DEC-20260802-233)  
**Supersedes:** `PA-IT-001-v3-rc43-repair-3`  
**Does not edit:** `specification.v3.yaml`, prior overlays, or any run artifacts.

## RT-314 closures

| Blocker | Repair | Freeze |
|---------|--------|--------|
| B1 | R4-FIX-B1 | `c_smart=8` ⇒ at pinned bits=20, `C_special_smart/matched_rho≈0.176<0.7` on the constant alone, with headroom `C_path+C_pullback≤floor(0.45·matched_rho)`. |
| B2 | R4-FIX-B2 | `anomalous_plant_bits=20`; restated `matched_rho=ceil(0.886·√N*)`; explicit supersession of spec v3 quadratic `20·(log2 N)²`. |
| B3 | R4-FIX-B3 | Density abscissa restored to `{20,24,28}` (Bonferroni×3); supersedes prior `{16,18,20,22,24}` overlays. |

RC-43 command binding, nonspecial/reversal certificates, null-recompute manifest path, comparator wording, null packaging gate, and quantitative Pareto axes are preserved.

## Inventor-protocol fields

- **`dominated_by`:** Pollard rho at exponent ½.
- **`sota_delta`:** three axes `not_applicable` with explicit non-solver scope (design-only task).

## Scope / non-claims

Toy tier only. No implementation, run, or H-IT-001 transition. Reserved run IDs unused here.
