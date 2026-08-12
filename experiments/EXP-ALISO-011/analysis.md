# Analysis — Autolab isogeny: p1486_parity_center_smoothness_verify

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_controls_pass": true,
  "baselines_and_controls": {
    "baseline": "producer exact population and registered sample summaries; producer code not imported or inspected",
    "negative_controls": [
      "squarefree B-smooth degree has sf(n)=n",
      "isogeny followed by its dual has noncyclic E[ell] kernel",
      "matched exact-uniform unconditioned sample is distinct",
      "product of distinct small odd primes exposes large center",
      "closed upper endpoint creates an exact +1 population error"
    ],
    "positive_controls": [
      "top-interval perfect B-smooth square has sf(n)=1",
      "planted a^2*7 instance is recovered exactly"
    ]
  },
  "claim_status": "INDEPENDENTLY-VERIFIED EXACT POPULATIONS AND TOY DISTRIBUTIONAL EVIDENCE / REGISTERED TREND FAILS / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM",
  "command_line": "python3 -B experiments/ecdlp_isogeny/p1486_pa
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
