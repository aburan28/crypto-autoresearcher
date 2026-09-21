# Analysis — Autolab prime-field: round019_PO009prime

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "start": {
    "p": 4099,
    "N": 4021,
    "D": -10155,
    "h": 20
  },
  "rows": [
    {
      "a": 4041,
      "b": 4067,
      "S4deg": 12,
      "S4_vanish_ok": 10,
      "S4_nonzero_ok": 10,
      "maxGBdeg": 3,
      "nsols": 7,
      "found": true,
      "d_ff": null,
      "D_reg": 7,
      "gate_meaningful": false,
      "tag": "E0"
    },
    {
      "a": 65,
      "b": 3474,
      "S4deg": 12,
      "S4_vanish_ok": 10,
      "S4_nonzero_ok": 10,
      "maxGBdeg": 3,
      "nsols": 7,
      "found": true,
      "d_ff": null,
      "D_reg": 7,
      "gate_meaningful": false,
      "tag": "l=3"
    },
    {
      "a": 2247,
      "b": 3036,
      "S4deg": 12,
      "S4_vanish_ok": 10,
      "S4_nonzero_ok": 10,
      "maxGBdeg": 3,
      "nsols": 7,
      "found": true,
      "d_ff": null,
      "D_reg": 7,
      "gate_meaningful": false,
      "tag": "l=5"
    },
    {
  
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
