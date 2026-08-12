# Analysis — Autolab prime-field: round018_T2_isogeny_gatedmeter

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "partA_topform_invariant": true,
  "partB_rows": [
    {
      "tag": "E0",
      "a": 7462,
      "b": 3472,
      "maxGBdeg": 3,
      "nsols": 4,
      "found": true,
      "FB": 4
    },
    {
      "tag": "l=3",
      "a": 2524,
      "b": 2823,
      "maxGBdeg": 3,
      "nsols": 4,
      "found": true,
      "FB": 4
    },
    {
      "tag": "l=5",
      "a": 4775,
      "b": 5740,
      "maxGBdeg": 3,
      "nsols": 4,
      "found": true,
      "FB": 4
    },
    {
      "tag": "CTRL(diff-order)",
      "a": 7519,
      "b": 6143,
      "maxGBdeg": 3,
      "nsols": 4,
      "found": true,
      "FB": 4
    }
  ],
  "partB_distinct_maxGBdeg": [
    3
  ],
  "partB_distinct_nsols": [
    4
  ],
  "partB_falsified": false
}
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
