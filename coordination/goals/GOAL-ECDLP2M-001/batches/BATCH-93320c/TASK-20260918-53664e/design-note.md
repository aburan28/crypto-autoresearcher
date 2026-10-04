# Design note — TASK-20260918-53664e

**Goal:** GOAL-ECDLP2M-001 · **Batch:** BATCH-93320c  
**Source proposal:** IDEA-20260916-3f7a1c (`status: proposed`, unchanged)  
**Outputs:** `H-QSP-cd0c90` · `EXP-QSP-70b731` v1 (`approved_by: null`)  
**Archive owner:** TASK-20260920-e51da0  

Designing is **not** approving. Execution is a separate `/run` after a separate Coordinator approval decision. This task ran with `maximum_runs: 0`; no census, spot check, or prototype was executed; `runs/` and `amendments/` contain only empty `.gitkeep`.

---

## What was carried forward from IDEA-20260916-3f7a1c

| Element | Disposition |
| --- | --- |
| Derivation (A) / H-based reduced count | Carried as the mathematical content of **I_indep** (high cells and cross-check arm) |
| Brute / direct gcd cross-check | Carried as **I_direct**; widened from `{11, 22}` to **Band L `n' = 3..14`** plus bridge **`n' = 22`** |
| Proves-too-much controls `(7,3)→8`, `(31,15)→32768`, `(12,6)→64` | Carried as C2–C4 |
| Null object + linearized + square/degenerate arms | Carried as C5–C7 |
| Toy fixtures `(11,6)`, `(13,7)`, `(7,3)` | Carried as Stage 1 calibration |
| Stage 0 hand re-derivation gate | Carried |
| Explicit root-list certificates + wrapper re-verification | Carried; certificate-bearing redefined to block the 732-vs-546 defect |
| `proof_search_map` structure | Filled on `H-QSP-cd0c90` |

## What was widened

- **Uncovered cells `n' = 3..14`** at `n = 131` (244 candidates each) — no committed run existed; now declared Stage 2 cells with **I_direct** (directly computable, `deg L ≤ 2^{14}`) and **I_indep** required to agree.
- **Independent-replication frame** for Band H `{33, 44, 66}`: freeze I_indep outputs, then COMPARE to sealed EXP-QSP-33b442 Stage 3 — closes EV-QSP-a6aa4b’s 98.4% single-instrument / missed-root exposure and DEC-20260917-793ae2 PD-6.

## What was dropped (and why)

| Dropped | Why |
| --- | --- |
| Full five-stage bound/beta campaign of EXP-QSP-33b442 (complete-splitting sweep, rational-lambda conjecture, table-row arithmetic) | Out of scope for a replication+uncovered-cell contract; would re-litigate H-QSP-5540d7 |
| Optional `n' = 33` half-gcd spot check | Impediment-prone (DEC-20260917-793ae2 NA-6 iii); left for a future amendment |
| IDEA-20260918-6c07e1 “no complete splitter in `n' = 3..14`” as a preregistered success/falsification branch | Unreviewed at design time (handoff C-8 / DEC-20260918-7e0865); census measures `N_K(L)` regardless |
| Any outside-harness / scratchpad Band-L numeric prior | Handoff motivation prohibition; honest prior is HEUR-1 (~2 roots/candidate; Poisson orbit mean `244/131 ≈ 1.86`) only |
| Editing IDEA-20260916-3f7a1c or EXP-QSP-33b442 | Immutable (handoff C-4) |

## KN-TECH-54c38e decision

**`may_use: false`.**

KN-TECH-54c38e is the composition-lemma instrument validated by TASK-20260917-5fa7d5, which already agreed with the producer on `n' = 33` aggregates. Using that note as an implementation cookbook would share lineage with the only prior “independent” check and would not close the single-instrument exposure. I_indep must be written from `H-QSP-cd0c90` / IDEA-20260916-3f7a1c statement+(A) only; `knowledge/techniques/KN-TECH-54c38e.md` is on `blind_from`. Band-L **I_direct** needs no composition lemma.

## Direct vs derivation cells (handoff C-7)

- **Directly computable:** `n' ∈ {3..14, 22}` — I_direct is primary; I_indep must agree.
- **Derivation-dependent (I_indep completeness; no I_direct in v1):** `n' ∈ {33, 44, 66}`.

## Approval / execution

`approved_by: null`. Hypothesis `status: proposed`. No run artifacts. Parent Coordinator may approve under standing authorization once protocol readiness is checked; that is a separate decision and a separate `/run`.
