# Analysis — Autolab prime-field: round006_exp010_validated_resweep

## Observation
POSITIVE (SURVIVED) -- at least one PRIME-FIELD m=3 representation genuinely early-falls (d_ff < D_reg) under the validated meter. This is the campaign's FIRST prime-field algebra-track positive. See firing cells below; escalate per EXP-011.

Source excerpt / raw summary:

```
# EXP-010 Result: validated-meter re-sweep of m=3 Semaev representations

SEED=42  timestamp=2026-05-30 23:43:48

Meter imported via `load()` from `round005_meter_validation.sage` (validated nontrivial-syzygy / Bardet-Faugere-Salvy first-fall meter on homogeneous leading forms).

## 1. Meter self-validation (MANDATORY, reported first)

| control | d_ff | D_reg_pred | fires | required | OK |
|---|---|---|---|---|---|
| POS-A (3 cubics, shared quadratic leading factor) | 4 | 7 | True | fire @ d_ff=4<D_reg=7 | True |
| NEG-1 (3 generic quadrics, regular CI) | 4 | 4 | False | quiet | True |
| NEG-2 (3 generic cubics, regular) | 7 | 7 | False | quiet | True |

**METER_SELF_VALIDATED = True**

## 2. Per-representation per-cell results (d_ff / D_reg_pred / fires)

Leading-form degree profile is the homogeneous top-form degrees actually fed to the meter.

| curve | bits | |FB| | rep | leading-form degs | d_ff | D_reg_pred | fires |
|---|---|---|---|---|---|---|---|
| structured | 13 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 13 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 13 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 13 | 4 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 13 | 4 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 13 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 13 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 13 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| structured | 13 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 13 | 5 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 15 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 15 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 15 | 4 | (D) pullback x=t^2 | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 4 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 15 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 15 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
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
