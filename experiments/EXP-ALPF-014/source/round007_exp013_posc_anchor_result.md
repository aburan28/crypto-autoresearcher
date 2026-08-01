# EXP-013 — POS-C Gold-Standard Calibration Anchor under the Gated Meter

**Experiment**: EXP-013  **Round**: 007  **Timestamp**: 2026-05-31 00:33:32

## 1. Experiment Contract Summary

**Hypothesis**: The Weil-restricted Semaev S_3 system (POS-C) fires d_ff < D_reg
AND the gated meter confirms the firing syzygy genuinely involves the S_3 summation-
polynomial leading form, not just factor-base constraint rows. This should be stable
across p in {5,7,11,13,17} and multiple curves.

**Null hypothesis**: Either POS-C does not fire (d_ff >= D_reg), or the gate fails
(the firing syzygy is confined to non-summation rows), indicating the round-5 fire
was a coordinate artifact similar to the e-ring/power-sum spurious fires.

**Gated meter loaded**: True

## 2. Base-Meter Self-Validation

| Control | d_ff | D_reg | fires | expect_fires | ok |
|---|---|---|---|---|---|
| POSA | 4 | 7 | True | True | True |
| NEG1 | None | 4 | False | False | True |
| NEG2 | None | 7 | False | False | True |

**Self-validation PASS**: True

## 3. POS-C Sweep Results

**System**: 2-var Weil coefficient split of Semaev S_3 over F_{p^2}/F_p.
Ring: F_p[u0, u1]. sumpoly_indices=[0] (real part e0 = S_3 summation component).

| label | p | degs | lf_e0 | d_ff | D_reg | fires | gate_passes | gate_meaningful | max_gb_deg | vs_Dreg |
|---|---|---|---|---|---|---|---|---|---|---|
| p7-curve-A | 7 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p7-curve-B | 7 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p11-curve-A | 11 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p11-curve-B | 11 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p13-curve-A | 13 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p13-curve-B | 13 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p17-curve-A | 17 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p17-curve-B | 17 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p19-curve-A | 19 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |
| p19-curve-B | 19 | [4, 3] | `u0^2*u1^2` | 5 | 6 | True | True | True | 4 | below_Dreg |

**Aggregates**: cells=10  fires=10/10  gate_passes=10/10  gate_meaningful=10/10

**GB analysis**: max_gb_deg < D_reg in 10/10 cells. not_unit_ideal in 10/10 cells.

## 4. What the GB Step Degree Tells Us

The Froberg D_reg for a 2-variable system with degrees [4, 3] is **6**.
The early fall d_ff=5 < 6 predicts the Groebner basis should reach its max-degree
step BEFORE degree 6, i.e. max_gb_deg <= 5 in the degrevlex computation.
If max_gb_deg < D_reg in the majority of cells, this confirms the algebraic
prediction: the early fall genuinely reduces GB computation below the semiregular bound.

## 5. Ideal Consistency

A non-unit ideal with 0-dimensional variety means the POS-C system is algebraically
consistent (it defines a finite scheme over the algebraic closure). Solutions may
lie in F_{p^k} for k > 2; the variety being empty over F_p does NOT mean the
system is the unit ideal. The relevance for index calculus is at the POLYNOMIAL
SYSTEM LEVEL (degree complexity), not the solution count over a specific base field.

## 6. Honest Scope Statement

OBSERVATION (scoped): POS-C is an **F_{p^2} Weil-restriction** phenomenon.
The system lives in F_p[u0, u1] where u0, u1 are formal F_p coordinates for
x-coords of points in E(F_{p^2}). This is the FPPR/Gaudry/Diem/Joux regime for
**extension fields**, NOT a direct attack on F_p ECDLP.

**Calibration role of POS-C**: it proves the gated meter has a working PASS branch
on a genuine Semaev summation-polynomial system. The firing syzygy at d_ff=5
involves the S_3 real-part leading form (not just FB rows), confirming the gate's
discrimination ability. Without POS-C, the gate only has evidence from synthetic
planted-syzygy controls (EXP-012 synthetic-gate-POS), which are not Semaev-derived.

**What this does NOT establish**:
- No exploitable index-calculus structure for prime-field E/F_p ECDLP.
- No sub-rho algorithm or relation-generation speedup.
- No ECDLP relevance beyond the extension-field calibration role.

## 7. Verdict

**VERDICT**: SURVIVED

OBSERVATION: POS-C robustly fires AND passes the localization gate across all
swept (p, curve) cells. The gated meter's PASS branch is confirmed on a genuine
Semaev S_3 summation-polynomial system in the Weil-restriction setting. The GB
max step degree is at or below D_reg, consistent with the early fall prediction.

## 8. Next Steps

1. CONSERVATIVE: verify POS-C also works with larger factor bases (m=4,5) in the
   extension-field regime, confirming the gate on multi-decomposition systems.
2. REPRESENTATION-CHANGING: test whether a Weil restriction of a DIFFERENT summation
   polynomial (e.g. S_4 over F_{p^3}) also passes the gate, establishing the gate's
   sensitivity to the class of systems the literature calls exploitable.
3. HIGH-RISK: attempt to find ANY prime-field F_p system (m=3, factor base in F_p)
   where the gated meter fires gate_meaningful=True. If found, that is the first
   evidence of a prime-field exploitable structure; if not, the NEGATIVE RESULT
   is a sharper statement than before.

## 9. Artifacts

- `round007_exp013_posc_anchor.sage` (this experiment)
- `round007_exp013_posc_anchor.log`
- `round007_exp013_posc_anchor_result.json`
- `round007_exp013_posc_anchor_result.md` (this file)
- Loaded gate: `round007_exp012_localization_gate.sage`
- Loaded base meter: `round005_meter_validation.sage`
