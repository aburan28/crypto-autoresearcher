# EXP-FROB-720a77 RESULTS — dim 5-6 Weil-census extension at n=131 over F_2

Run: **RUN-FROB-c87706** (2026-10-07, 126 s wall, completed_valid).
Contract: specification.yaml v1 (DEC-20260905-0f460b / DEC-20261005-0f460b).
All numbers below are this run's own outputs (`raw-result.json`).

## Verdict per the frozen stopping rules

**C1 PASS** — the instrument reproduces the prior exclusion exactly, by its own
Sturm tests on every candidate:

| dimension | candidates (exact DP count) | exact Sturm tests | hits | ambiguous (C2) | wall |
|---|---|---|---|---|---|
| 1 | 0 (no multiple of 131 in Weil range) | 0 | — | — | — |
| 2 | 0 (same) | 0 | — | — | — |
| 3 | 104 (all at target 131) | 104 | **0** | 0 | 0.4 s |
| 4 | 234,220 (8 multiples: 131..1048) | 234,220 | **0** | 0 | 124.3 s |

**FEASIBILITY GATE FIRES at dimensions 5 and 6 — impediment, never evidence:**

| dimension | candidates (exact DP count) | multiples of 131 in Weil range | gate |
|---|---|---|---|
| 5 | **2,200,952,677** | 51 | FIRES (> 50,000,000 exact tests) |
| 6 | **132,339,478,495,234** | 299 | FIRES |

Per-multiple candidate counts are in `raw-result.json` (`candidates_per_multiple`),
per the C3 empty-sweep-transparency rule (no multiple had an empty enumeration).

## What this run decides and what it does not

- **Decided**: the dimension 1-4 exclusion is reconfirmed by an independent
  implementation (zero hits at both recorded dimensions, zero boundary
  ambiguities), and the v1 method's exact cost is now measured at every
  dimension: the candidate count grows ~9,400x from dim 4 to dim 5 and
  ~60,000x again from dim 5 to dim 6.
- **Not decided**: H-FROB-ff99bf at dimensions 5 and 6 — the frozen
  feasibility gate stopped both as impediments. The exclusion is NOT extended,
  and NOT contradicted; the Couveignes-Lercier survival space at n=131 is
  unchanged by this run (dimensions 1-4 excluded, dim >= 5 open).
- **Successor (v2 amendment path)**: a pruned enumeration — cheap exact
  integer pre-filters before Sturm (e.g. Newton power-sum necessary
  conditions |p_k| <= g(2√2)^k, or derivative-interlacing screens) to cut the
  ~10^9-10^14 candidate boxes to a testable residue at dim 5, with the
  same C1/C2/C3 controls and the same 50M gate. The DP count itself (exact,
  no Sturm) is reusable as the enumeration oracle for any pruning scheme.

## Scope (frozen contract, unchanged)

q = 2, n = 131, dimensions 1-6, Honda-Tate bridge (recalled, classical).
No curve, group, point or key is constructed. ECC2K-130's rho baseline
(2^60.9, KN-LIT-096) is untouched. Observations only until the separate
review process supports any state transition.
