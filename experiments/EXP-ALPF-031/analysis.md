# Analysis — Autolab prime-field: round019b_ering_sweep

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "start": {
    "p": 4099,
    "N": 4021,
    "D": -10155
  },
  "rows": [
    {
      "tag": "E0",
      "a": 4041,
      "b": 4067,
      "d_ff": 3,
      "D_reg": 6,
      "fires": true,
      "summation_support": 0,
      "gate_meaningful": false
    },
    {
      "tag": "l=3",
      "a": 65,
      "b": 3474,
      "d_ff": 3,
      "D_reg": 6,
      "fires": true,
      "summation_support": 0,
      "gate_meaningful": false
    },
    {
      "tag": "l=5",
      "a": 2247,
      "b": 3036,
      "d_ff": 3,
      "D_reg": 6,
      "fires": true,
      "summation_support": 0,
      "gate_meaningful": false
    },
    {
      "tag": "l=7",
      "a": 1156,
      "b": 3882,
      "d_ff": 3,
      "D_reg": 6,
      "fires": true,
      "summation_support": 0,
      "gate_meaningful": false
    },
    {
      "tag": "l=7",
      "a": 1355,
      "b": 2774,
      "d_ff": 3,
      "D_reg
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
