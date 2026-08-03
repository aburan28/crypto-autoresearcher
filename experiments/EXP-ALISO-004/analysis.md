# Analysis — Autolab isogeny: p1486_frobenius_midpoint_sweep_verify

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "aggregate_metrics": {
    "claimed_midpoint_success_rate": {
      "denominator": 8,
      "numerator": 8,
      "value": 1.0
    },
    "degree_metrics": {
      "doubled_degrees": [
        4,
        4,
        9,
        9,
        9,
        16,
        16,
        16
      ],
      "half_degrees": [
        2,
        3,
        4
      ],
      "published_deltas": [
        4,
        9,
        16
      ]
    },
    "family_success_rate": {
      "denominator": 3,
      "numerator": 3,
      "value": 1.0
    },
    "memory": {
      "peak_rss_bytes": 313573376
    },
    "rank": {
      "applicable": false,
      "reason": "no relation matrix is constructed"
    },
    "relation_probability": {
      "applicable": false,
      "reason": "this is an exhaustive isogeny-support verification, not relation collection"
    },
    "wall_time_sec": 5.5531735
  },
  "baselines_and_co
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
