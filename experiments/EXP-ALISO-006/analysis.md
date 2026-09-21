# Analysis — Autolab isogeny: p1486_hecke_degree_pair_support_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "algorithmic_breakthrough": false,
  "all_gates_pass": true,
  "claim_status": "TOY-EVIDENCE / EXACT SUPPORT ENUMERATION / MODEL-BOUND / SUPPORT-PRIMITIVE NOT IMPLEMENTED",
  "elapsed_sec": 0.937747292,
  "families": [
    {
      "conjugate_j": [
        130,
        166
      ],
      "count_mismatches": [
        [
          4,
          4
        ],
        [
          6,
          6
        ]
      ],
      "exact_unweighted_count_equality_claimed": false,
      "gates": {
        "all_half_degree_path_counts_match_psi": true,
        "all_support_bits_match": true,
        "nontrivial_gcd_correction_present": true,
        "positive_and_negative_pairs_present": true,
        "sharp_square_pair_positive": true
      },
      "h_values": {
        "1": 0,
        "12": 1,
        "16": 0,
        "18": 1,
        "2": 0,
        "24": 3,
        "3": 0,
        "36": 0,
        "
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
