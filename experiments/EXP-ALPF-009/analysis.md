# Analysis — Autolab prime-field: round005_exp008_fixeddeg_fb

## Observation
SCOPED_NEGATIVE -- d_FB fixed, D_reg fixed, BUT descent blocked

Source excerpt / raw summary:

```
# EXP-008: Fixed-Degree Membership Factor Base -- Result

## Experiment
**Date:** Sat May 30 23:04:40 2026  
**Seed:** 42  
**Meter validated:** True  

## Hypothesis
A factor base whose membership is cut by a polynomial of FIXED low degree independent
of |FB| (trace-zero over F_{p^2}/F_p, norm-1, subfield) can stop D_reg from growing
with |FB|, potentially giving a genuine asymptotic lever over Pollard rho.

## Null Hypothesis
The FB-constraint degree still grows with |FB|, OR relations do not descend to the
F_p ECDLP (wrong subgroup), so no asymptotic gain exists.

## Meter Status
**METER_VALID = True**  
All EXP-008 first-fall results are TRUSTWORTHY.
  - POS-A fires: True (d_ff=4, D_reg=7)
  - NEG-1 quiet: True  
  - NEG-2 quiet: True  

## FB-Constraint Degree vs |FB| (Key Table)

| FB Type | Constraint | Degree d_FB | Grows with |FB|? |
|---------|-----------|-------------|----------------|
| trace-zero (Weil) | 2*u0_i + u1_i*Tr(w) = 0 | **1 (FIXED)** | NO |
| subfield | u1_i = 0 | **1 (FIXED)** | NO |
| norm-1 (Weil) | u0_i^2 + u0_i*u1_i*Tr(w) + u1_i^2*N(w) = 1 | **2 (FIXED)** | NO |
| x-interval baseline | prod(xi - xj) = 0 | **= |FB| (GROWS)** | YES |

**FINDING:** All three fixed-degree candidates have d_FB that is INDEPENDENT of |FB|.
This is the key lever sought since round 1.

## Subgroup Descent Gate (Critical Gate)

| FB Type | Frac in E(F_p) | Descends? |
|---------|---------------|----------|
| subfield (positive ctrl) | 1.000 | YES |
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
