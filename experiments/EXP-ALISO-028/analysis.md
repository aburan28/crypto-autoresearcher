# Analysis — Autolab isogeny: iso_genus_filtered_crater_ancestor

## Observation
OBSERVATION / CURVE-LEVEL TOY-EVIDENCE / GENUS-FILTERED CANDIDATE REDUCTION

Source excerpt / raw summary:

```
{
  "arithmetic": {
    "class_number": 16,
    "crater_root_count": 16,
    "discriminant_factors": [
      3,
      5,
      11,
      23
    ],
    "expected_genus_size": 2,
    "floor_root_count": 48,
    "frobenius_identity_lhs": -15180,
    "genus_number": 8
  },
  "claim_boundary": {
    "deployed_scallop_break": false,
    "ecdlp_consequence": false,
    "end_to_end_kani_recovery": false,
    "general_theorem_proved_by_experiment": false
  },
  "crater_classes": [
    {
      "count": 2,
      "fingerprint": [
        -1,
        -1,
        -1
      ]
    },
    {
      "count": 2,
      "fingerprint": [
        -1,
        -1,
        1
      ]
    },
    {
      "count": 2,
      "fingerprint": [
        -1,
        1,
        -1
      ]
    },
    {
      "count": 2,
      "fingerprint": [
        -1,
        1,
        1
      ]
    },
    {
      "count": 2,
      "fingerpr
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
