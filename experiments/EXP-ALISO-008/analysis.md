# Analysis — Autolab isogeny: p1486_hecke_krylov_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "algorithmic_breakthrough": false,
  "candidate_admitted": false,
  "claim_status": "TOY-EVIDENCE / FULL-GRAPH ORACLE / MODEL-BOUND / ALGORITHM FALSE",
  "elapsed_sec": 7.2908495,
  "fixtures": [
    {
      "candidate_admitted": false,
      "control_reports": [
        {
          "adjacency": {
            "connection": [
              1,
              1000000,
              999987,
              50,
              85,
              999711,
              999835,
              724,
              86,
              999278,
              1000001,
              232,
              24
            ],
            "held_out_accuracy": 1.0,
            "held_out_correct": 16,
            "held_out_length": 16,
            "order": 12,
            "train_length": 72
          },
          "cyclic": {
            "connection": [
              1,
              1000000,
              8,
         
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
