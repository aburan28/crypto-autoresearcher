# Analysis — Autolab prime-field: round003_exp004_firstfall_reps

## Observation
failed

Source excerpt / raw summary:

```
# EXP-004: Validated First-Fall Instrument + Three-Representation Sweep

**Experiment:** round003-exp004  **Seed:** 42  **Date:** 2026-05-30 21:21  **Verdict:** FAILED

## Instrument Gate (STEP 0)

Gate criteria:
- (0a) Planted-syzygy system {xy-1, xz-1, yz-1} must show d_ff < D_reg_pred
- (0b) Semiregular random system must NOT show early fall
- LIMITATION: Sensitivity to strict early falls not independently validated (see log)

| Gate | Pass? | d_ff | D_reg_pred | early_fall |
|---|---|---|---|---|
| 0a: calibration (semiregular: d_ff=D_reg_pred) | PASS | 4 | 4 | False |
| 0b: specificity (no false positives) | PASS | 4 | 4 | False |
| **Overall gate** | **PASS** | | | |

## Per-Cell Results

| Cell | Rep | d_ff | D_reg_pred | fb_deg | early_fall? |
|---|---|---|---|---|---|
| structured_13b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_13b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_13b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_13b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_13b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_13b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_13b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_13b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_13b_FB5 | Kummer | 10 | 10 | 4 | no |
| structured_15b_FB3 | e-ring | 1 | 1 | 1 | no |
| structured_15b_FB3 | power-sum | 4 | 4 | 3 | no |
| structured_15b_FB3 | Kummer | 7 | 7 | 3 | no |
| structured_15b_FB4 | e-ring | 4 | 4 | 2 | no |
| structured_15b_FB4 | power-sum | 7 | 7 | 4 | no |
| structured_15b_FB4 | Kummer | 10 | 10 | 4 | no |
| structured_15b_FB5 | e-ring | 5 | 5 | 3 | no |
| structured_15b_FB5 | power-sum | 10 | 10 | 5 | no |
| structured_15b_FB5 | Kummer | 10 | 10 | 4 | no |
| structured_17b_FB3 | e-ring | 1 | 1 | 1 | no |
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
