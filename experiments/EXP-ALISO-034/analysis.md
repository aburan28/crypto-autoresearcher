# Analysis — Autolab isogeny: p1486_frobenius_midpoint_probe_result_v1

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "admitted_degree_36_count": 2,
  "admitted_degree_36_records": [
    {
      "doubled": {
        "codomain_j": "33440*alpha + 42318",
        "cyclic_kernel": true,
        "degree": 36,
        "prime_torsion_kernel_sizes": {
          "2": 2,
          "3": 3
        },
        "target_j": "33440*alpha + 42318",
        "target_matches": true
      },
      "kernel_polynomial": "x^3 + (2788*alpha + 58609)*x^2 + (9129*alpha + 789)*x + 54157*alpha + 54085",
      "midpoint_in_Fp": true,
      "midpoint_j": "17069",
      "subgroup_index": 2
    },
    {
      "doubled": {
        "codomain_j": "33440*alpha + 42318",
        "cyclic_kernel": true,
        "degree": 36,
        "prime_torsion_kernel_sizes": {
          "2": 2,
          "3": 3
        },
        "target_j": "33440*alpha + 42318",
        "target_matches": true
      },
      "kernel_polynomial": "x^3 + (40826*alpha + 
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
