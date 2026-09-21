# Analysis — Autolab isogeny: p1243_transverse_auxiliary_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_gates_pass": true,
  "artifact_hashes": {
    "contract_sha256": "7abb99ad2a49f9e11b2d3335d1f3462f653ba9f3cad27745542e550a50b1cbac",
    "source_sha256": "00e157eda26fca4d328c11feb71f81c97a94e7996db3ff15bd165d610ef7ad16"
  },
  "asymptotic_field_bound_verified": false,
  "claim_status": "TOY GEOMETRIC EVIDENCE / FULL RATIONAL TORSION / NO KANI RECONSTRUCTION",
  "families": [
    {
      "cumulative_auxiliary_degree": 3,
      "curve_cardinality": 144,
      "expected_cardinality": 144,
      "final_known_line_order": 3,
      "gates": {
        "all_same_line_composites_backtrack": true,
        "all_same_line_mutations_fail": true,
        "all_transverse_composites_cyclic_locally": true,
        "all_transverse_pairings_full": true,
        "all_transverse_steps_preserve": true,
        "basis_orders": true,
        "basis_pairing_full_order": true,
        "final_known_line_
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
