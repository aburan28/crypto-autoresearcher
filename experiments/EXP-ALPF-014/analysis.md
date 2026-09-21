# Analysis — Autolab prime-field: round007_exp013_posc_anchor

## Observation
{'n_cells_attempted': 10, 'n_cells_valid': 10, 'n_fire': '10', 'n_gate_pass': '10', 'n_gate_meaningful': '10', 'n_gb_below_Dreg': '10', 'n_not_unit_ideal': '10', 'self_validation_pass': True}

Source excerpt / raw summary:

```
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
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
