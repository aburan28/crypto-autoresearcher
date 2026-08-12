# Analysis — Autolab isogeny: p1486_degree_first_hecke_probe_result_v2

## Observation
TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY

Source excerpt / raw summary:

```
{
  "claim_gates": {
    "aov_delta_36_reproduced": true,
    "positive_multiplicativity_control": true,
    "positive_recurrence_control": true,
    "public_attack_input_available": false
  },
  "controls": {
    "divisor_sum_multiplicativity": {
      "defect": 0.0,
      "examples": [],
      "informative_defect": 0.0,
      "informative_mismatches": 0,
      "informative_pairs": 3507,
      "mismatches": 0,
      "pairs": 3507
    },
    "exponential_bm_order": 1
  },
  "degree_gram": [
    [
      "36",
      "35/2",
      "18"
    ],
    [
      "35/2",
      "36",
      "17"
    ],
    [
      "18",
      "17",
      "37"
    ]
  ],
  "degree_gram_determinant": "101051/4",
  "enumeration_radius": 13,
  "first_represented_count": 4,
  "first_represented_degree": 36,
  "gross_gram": [
    [
      "3959",
      "-1188",
      "-1402"
    ],
    [
      "-1188",
      "4032",
      "-
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
