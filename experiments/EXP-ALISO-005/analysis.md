# Analysis — Autolab isogeny: p1486_frobenius_midpoint_verify

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "claim_status": "INDEPENDENTLY-REPLAYED TOY EVIDENCE / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM",
  "elapsed_sec": 0.225543042,
  "general_p_one_third_improvement": false,
  "mutation_rejection_count": 4,
  "mutation_rejections": {
    "count": true,
    "cyclicity": true,
    "midpoint": true,
    "overclaim_gate": true
  },
  "payload_sha256": "8d552a1b9ca5b9b641d36d5caf007bc70453ec18adbebd7d125a164cfdf0984c",
  "producer_payload_recomputed": true,
  "producer_payload_sha256": "5f15fe51351a8c5d3e6b8cd9f7aa2961d4af2e66643b519b8ec474b39ec25e3e",
  "producer_result_sha256": "6649e961d3c6abcdd48174b61c11d7f4ebb9b862c56a86de0042a77ea6299c77",
  "producer_source_sha256": "f97db9e7f4b064e4fc65f4f0df8cf9ccddf7ff5ca58015efc3335ebc42fb2277",
  "schema": "p1486-frobenius-midpoint-verifier-v1",
  "scientific_replay": {
    "backtracking_two_torsion_kernel_size": 4,
    "degree_four_subgroup_c
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
