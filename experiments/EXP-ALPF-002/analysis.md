# Analysis — Autolab prime-field: round002_exp002_m3_firstfall

## Observation
failed

Source excerpt / raw summary:

```
# EXP-002 Result: m=3 Semaev First-Fall via Macaulay Rank Profile

**Seed:** 42  **Date:** 2026-05-30 20:14  **Verdict:** FAILED (NEGATIVE RESULT)

## Instrument Fix (Round 1 error corrected)

Round 1 used `min(GB-output-degree)` as d_ff proxy. This is a tautological lower bound
(pinned at input degree at m=2) and NOT the true first-fall degree.

Round 2 measures the true first-fall via Macaulay-matrix rank profile vs the semiregular
Hilbert-series prediction (Bardet-Faugere-Salvy-Yang definition):
- d_ff = smallest D where hf(D) < hf_pred(D) = max(c_D, 0).
- "early fall" = d_ff strictly less than D_reg_pred.
- Instrument verified via P1 (3 quadrics no-fall, 4 quadrics fall) and P2 (extension domain).

## Controls Outcome

| Control | Gate | Notes |
|---|---|---|
| P1 synthetic (3 vs 4 quadrics) | PASS | 3-quad d_ff=4=D_reg_pred (no fall), 4-quad d_ff=3 fall at D=3 |
| P2 extension-field (known fall) | PASS | fall_triggered=True at d_ff=6 > D_reg_pred=5 (overdetermined fall) |
| N1 random dense (noise floor) | PASS | 0/12 seeds showed early fall (d_ff < D_reg_pred) |

**P1 interpretation:** For 3 random quadrics in 3 vars, the graded HF tracks the semiregular
prediction exactly through D_reg_pred=4 (fall_triggered=False). For 4 quadrics (overdetermined),
hf drops below hf_pred=0 at D=3, triggering a fall. This confirms the instrument distinguishes
semiregular from overdetermined behavior. P2 shows the instrument detects falls in the known
extension-field regime.

## m=3 Results: Rank Profiles (representative cells)

### struct_13bit_FB4 (|FB|=4, degs=[4,2,2,2] in e-ring, D_reg_pred=4)
```
  D    ncols   rank  corank  semireg_cum   c_D   hf  hf_pred  status
  4       35     27       8            8    -1     0        0  pred_Dreg
  5       56     50       6            8    -3    -2        0  FALL! (but D=5 > D_reg_pred=4)
  6       84     80       4            8    -3    -2        0
  7      120    116       4            8    -1     0        0
```
RESULT: d_ff=5, D_reg_pred=4. fall_detected=False (5 > 4 = not early).
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
