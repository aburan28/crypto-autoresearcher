# Analysis — Autolab isogeny: p1486_quantum_aggregate_oracle_probe_result_v1

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_gates_pass": false,
  "claim_status": "TOY ORACLE-REDUCTION EVIDENCE / NOT A QUANTUM SIMULATION / NO GATE-COMPLEXITY CLAIM",
  "downstream_reduction_resolved": false,
  "elapsed_sec": 0.153905042,
  "families": [
    {
      "D_float": 4.725170528451599,
      "all_path_counts_match_psi": false,
      "dedekind_psi_counts": {
        "1": 1,
        "2": 3,
        "3": 4,
        "4": 6,
        "6": 12
      },
      "delta": 4,
      "delta_claw_count": 6,
      "diagonal_delta_claw_count": 2,
      "frobenius_claw_count": 39,
      "gates": {
        "delta_claw_present": true,
        "invalid_sentinels_disjoint": true,
        "known_square_midpoint_present": true,
        "padded_size_at_most_Y_squared_subpoly": true,
        "psi_counts": false
      },
      "half_degree_limit_Y": 6,
      "invalid_cross_collision_count": 0,
      "modular_specializations": 8,
      "p"
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
