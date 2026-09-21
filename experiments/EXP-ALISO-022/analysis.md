# Analysis — Autolab isogeny: p1243_ordinary_transverse_field_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_pass": true,
  "artifact_hashes": {
    "contract_sha256": "778a4195551e1214d73134b0c422e2fad9f54ef2d9a3703a8dcda79aa7a966f0",
    "source_sha256": "157cc931e51336ca9b205215f5e8ecdb05472d91bab7ee674de64ca706b3024d"
  },
  "claim_status": "ORDINARY TOY-EVIDENCE / FIELD-ACCOUNTING CONTROL / NO KANI RECONSTRUCTION",
  "fixtures": [
    {
      "charged_compositum_degree": 3,
      "coefficients": [
        1,
        3
      ],
      "expected_degree": 3,
      "frobenius_discriminant": -24,
      "gates": {
        "natural_orientation_lost": true,
        "non_special_j": true,
        "ordinary": true,
        "quotient_torsion_degree_expected": true,
        "ramified_valuation_one": true,
        "repair_within_charged_field": true,
        "same_line_composite_backtracks": true,
        "source_torsion_degree_expected": true,
        "transverse_codomain_not_base_rational": t
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
