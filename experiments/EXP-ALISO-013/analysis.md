# Analysis — Autolab isogeny: p1486_quantum_cost_accounting_verify

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_pass": true,
  "artifact_hashes": {
    "contract_sha256": "d549384ef82c42e6bf17fee084696649fa60d7c9a1a4b07080a201cd52729b72",
    "source_sha256": "c7a7ee9217f5b5630e98fe904fae5312d75b1e6906b2b50e448eca22be0faba5"
  },
  "grid": {
    "denominator": 216,
    "gate_min": "1/3",
    "gate_minimizers": [
      "0/1"
    ],
    "query_min": "2/9",
    "query_minimizers": [
      "2/9"
    ]
  },
  "identity_checks": {
    "depth": true,
    "depth_times_width": true,
    "domain": true,
    "gates": true,
    "query": true,
    "query_optimal_r": true,
    "width": true
  },
  "membership_threshold": [
    {
      "alpha": "0/1",
      "minimizers": [
        "2/9"
      ],
      "observed_below_classical_one_third": true,
      "observed_below_quantum_one_quarter": true,
      "optimized_charged_exponent": "2/9",
      "pass": true,
      "predicted_below_classical_one_third": tru
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
