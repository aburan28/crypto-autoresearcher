# Analysis — Autolab isogeny: p1486_degree_first_hecke_verify

## Observation
PASS / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY

Source excerpt / raw summary:

```
{
  "coordinate_bounds": [
    9,
    9,
    8
  ],
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
      "-1366"
    ],
    [
      "-1402",
      "-1366",
      "4172"
    ]
  ],
  "input_file_sha256": "24d4399e0ff08a0d0922c12960600d148b543ce3521fceed3cee1dc94a4b8d90",
  "mutations": [
    {
      "name": "first_degree",
      "rejected": true
    },
    {
      "name": "degree_form",
      "rejected": true
    },
    {
      "name": "recurrence",
      "rejected": true
    },
    {
      "name": "payload_hash",
      "rejected": true
    }
  ],
  "negative_gates": {
    "1024": {
      "count_order": true,
      "count_pred
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
