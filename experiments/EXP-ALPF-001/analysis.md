# Analysis — Autolab prime-field: round001_exp1_firstfall

## Observation
d_ff(symmetric prime-field Semaev) stays bounded (flat) across >=3 sizes for fixed m, strictly below D_reg

Source excerpt / raw summary:

```
{
  "experiment": "round001-exp1-firstfall",
  "seed": 42,
  "timestamp": "2026-05-30",
  "hypothesis_H1": "d_ff(symmetric prime-field Semaev) stays bounded (flat) across >=3 sizes for fixed m, strictly below D_reg",
  "null_H0": "d_ff tracks D_reg up to m! constant (no exponent change)",
  "target_bits": [
    15,
    19,
    23,
    27
  ],
  "fb_sizes": [
    2,
    5,
    10
  ],
  "ms": [
    2
  ],
  "n_trials": 5,
  "structured_curves": [
    {
      "bits": 15,
      "p": 32783,
      "shape": "Solinas",
      "a": -3,
      "b": 12711,
      "n": 32911
    },
    {
      "bits": 19,
      "p": 524257,
      "shape": "Solinas",
      "a": -3,
      "b": 436528,
      "n": 524633
    },
    {
      "bits": 23,
      "p": 8388673,
      "shape": "Solinas",
      "a": -3,
      "b": 4464317,
      "n": 8391433
    },
    {
      "bits": 27,
      "p": 134215681,
      "shape": "Soli
... [truncated]
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
