# Analysis — Autolab isogeny: p1486_hecke_support_cost_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "algorithmic_breakthrough": false,
  "analytic_asymptotic_exponents": {
    "classical_per_support_exponent": "1/6",
    "classical_total_exponent": "1/3",
    "gate_optimal_standard_gate_per_support_exponent": "1/6",
    "gate_optimal_standard_gate_total_exponent": "1/3",
    "outer_calls_exponent": "1/6",
    "query_optimal_standard_gate_per_support_exponent": "2/9",
    "query_optimal_standard_gate_total_exponent": "7/18",
    "tani_endpoint_query_per_support_exponent": "1/9",
    "tani_endpoint_query_total_exponent": "5/18"
  },
  "checks": {
    "analytic_classical_returns_frontier": true,
    "analytic_gate_optimal_gates_tie": true,
    "analytic_nested_query_beats_frontier": true,
    "analytic_query_optimal_gates_lose": true,
    "query_and_gate_models_separated": true,
    "source_support_probe_passed": true,
    "uncharged_query_as_gate_claim_rejected": true
  },
  "claim_s
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
