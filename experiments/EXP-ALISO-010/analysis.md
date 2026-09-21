# Analysis — Autolab isogeny: p1486_parity_center_smoothness_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_controls_pass": true,
  "claim_status": "HEURISTIC DISTRIBUTION EVIDENCE / TOY / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM",
  "elapsed_sec": 3.20544225,
  "families": [
    {
      "B": 13,
      "adversarial_squarefree_smooth_control": {
        "passes": true,
        "squarefree_kernel": 30030,
        "value": 30030
      },
      "all_samples_B_smooth": true,
      "all_samples_in_interval": true,
      "bits": 40,
      "center_exponent_log2_sf_over_bits": {
        "maximum": 0.3718529213611128,
        "mean": 0.15447637422992377,
        "median": 0.15323207542362416,
        "p90": 0.2603671308951804,
        "p95": 0.28536713089518034,
        "p99": 0.3468529213611128
      },
      "log_B_over_sqrt_logX_loglogX": 0.2672466665866815,
      "odd_valuation_prime_count": {
        "maximum": 6,
        "mean": 2.57568359375,
        "median": 3.0
      },
      "perfec
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
