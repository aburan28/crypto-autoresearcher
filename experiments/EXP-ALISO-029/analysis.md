# Analysis — Autolab isogeny: iso_genus_filtered_crater_sweep

## Observation
OBSERVATION / MULTI-DISCRIMINANT CURVE-LEVEL TOY-EVIDENCE

Source excerpt / raw summary:

```
{
  "all_success": true,
  "claim_boundary": {
    "ecdlp_consequence": false,
    "end_to_end_isogeny_recovery": false,
    "formal_theorem_proved_by_sweep": false,
    "scallop_break": false
  },
  "fixture_count": 4,
  "rows": [
    {
      "class_counts": [
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
          "fingerprint": [
            1,
            -1,
            -1
          ]
        }
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
