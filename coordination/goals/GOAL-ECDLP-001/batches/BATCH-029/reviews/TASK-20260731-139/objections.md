# RT-20260731-139 — Objections (SPARSE-P-SUCCESS)

**Snapshot:** `9ac393ca` (TASK-137)  
**Control:** CTRL-RT025-SPARSE-P-SUCCESS @ `0d6a1a94`  
**Approval:** `e3b82f7b` / DEC-20260731-038  
**Prior:** EV-DS-009 / DEC-20260731-031 / RT-20260731-118 / RT-20260731-134 / RT-20260731-047  

## Verdict

`sparse_p_success_pass=true` on the declared 4-cell toy ladder is **protocol success for sparse-yield bookkeeping** (p̂ decay observed on one harder cell; total-expected-cost fields present; R_total_expected reported), **not** crypto-yield / S1_met / mechanism support / asymptotic win / lane death. R_total_expected ≡ R_per_attempt by construction when both arms share p̂ — the 1/p̂ penalty appears in absolute `total_expected_cost_*`, not in the ratio.

## Blocking (RT139-B1–B7)

| ID | Title |
|----|--------|
| RT139-B1 | Forbid stronger-than-toy readings from sparse_p_success_pass (keeps RT118-B1 / RT101-B1) |
| RT139-B2 | sparse_p_success_pass ≠ mechanism credit / S1_met / sparse-win narrative; RT047-B4 partial ladder-local discharge only |
| RT139-B3 | Unreplicated single-seed ladder forbids reject_scoped / lane death |
| RT139-B4 | One-cell p̂ decay (24/32 only) insufficient for sparse-yield or crypto-scale narrative |
| RT139-B5 | R_total_expected ≡ R_per_attempt — ratio cannot encode 1/p̂ penalty; wall-proxy / selection effects bind |
| RT139-B6 | No theater / EXP-IT / BATCH-027/028 launder |
| RT139-B7 | R_null≈88–125 persists; plant absent; backend charged-units proxy — not S1_met or structure credit |

## Major / info

- **RT139-M1:** Single seed 101 across all cells; no replication; ladder unreplicated exploratory_control.
- **RT139-M2:** Dirty-tree / assume-unchanged driver; bind EV to snapshot hashes not task prose.
- **RT139-M3:** Fixed n_usable=200 target inflates attempts on sparse cells (2958 vs 200) — p̂ is retrospective attempt fraction under selection, not fixed-budget yield.
- **RT139-M4:** R_per_attempt worsens on harder cells (0.027→0.076); split ratio does not improve under sparsity.
- **RT139-I1/I2:** Package forbid hygiene OK; inference fallback recorded.

## Observed (snapshot sparse_p_success_report)

| Cell | p̂ | decay? | R_per_attempt | R_total_expected | R_null | wall_naive (s) |
|------|-----|--------|---------------|------------------|--------|----------------|
| 20/64 ref | 1.000 | no | 0.0272 | 0.0272 | 103.2 | 7.0 |
| 24/64 | 0.704 | no | 0.0425 | 0.0425 | 125.4 | 101.3 |
| 20/32 | 0.631 | no | 0.1040 | 0.1040 | 116.0 | 15.3 |
| 24/32 | 0.0676 | **yes** | 0.0763 | 0.0763 | 88.6 | 250.2 |

Harder cell absolute total_expected_cost_split ≈ 1.80×10⁶ vs reference ≈ 1.38×10³ (~1300× yield penalty).

## TASK-140 recommendation

- **DISPOSITION:** `inconclusive` (preferred) or `expand` only for replication / multi-seed / crypto-correspondence scheduling  
- **NOT:** `support`  
- **H-DS-001:** keep `analyzed`  
- **Gates:** OPEN  
- **knowledge_promotion:** `not_warranted`  
- **Evidence / DEC:** EV-DS-010 + DEC-20260731-039  
