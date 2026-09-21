# Experiment Contract: P1041 p231 y-residue strict-route validation

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The post-hoc P1040 public discriminator `public_y mod 11 in {2,7}` filters out scalar-unstable strict leaf-8 witnesses while preserving scalar-stable strict-route relation supply on fresh windows.

## Null hypothesis
The frozen y-residue selector has no fresh relation supply, has q-diverse supply but no exact factor-vector match, or produces any false compressed prediction. This would be a scoped negative for this public disambiguator, not for index calculus or the broader ECDLP objective.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- forward validation windows: `12760_12767` through `12880_12887`
- source rank floor: `0`
- modulus/order: `11779`
- primary route: `p1029_leaf8_scout`
- diagnostic row pools: `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- strict family: terms `[8,8,11,11]`, tail support `[9,12]`
- frozen public disambiguator: public fingerprint y-coordinate residue mod `11` in `{2,7}`
- primary view: row-signature-compressed forms
- diagnostic view: raw reconstructed forms and widened row pools

## Metrics
- source windows available;
- primary and diagnostic row counts;
- y-filtered strict form count;
- q-diverse same-public same-window object group count;
- factor-matched prediction count;
- true/false toy-secret verification count;
- widened-pool diagnostic false count.

## Positive control
The scout-window primary compressed control must preserve the original clean leaf-8 signal under the y-residue filter: nonzero true predictions and zero false predictions.

## Negative control
The forward validation windows must be disjoint from P1038 and P1039 validation windows. Widened pools are reported as red-team diagnostics and cannot promote the primary strict-route claim.

## Success criterion
Primary success requires at least one forward compressed factor-matched prediction and zero forward compressed false predictions in `p1029_leaf8_scout` after the y-residue filter.

## Falsification criterion
Any primary forward compressed false prediction falsifies this frozen y-residue selector for the scanned slice. If there are no primary compressed predictions but y-filtered q-diverse groups exist, the bottleneck is exact factor-vector compatibility. If there are no q-diverse groups, the bottleneck is filtered relation supply.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1041_p231_yresidue_strict_route_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1041_p231_yresidue_strict_route_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1041_p231_yresidue_strict_route_validation_probe.json
```

## Results
Run timestamp: `2026-06-30T04:06:52Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1041_p231_yresidue_strict_route_validation_probe.json`.

Claim status: `P1041_YRESIDUE_STRICT_ROUTE_FORWARD_SUPPLY_SIGNAL`.

Forward windows: `12760_12767`, `12768_12775`, `12776_12783`, `12784_12791`, `12792_12799`, `12800_12807`, `12808_12815`, `12816_12823`, `12824_12831`, `12832_12839`, `12840_12847`, `12848_12855`, `12856_12863`, `12864_12871`, `12872_12879`, `12880_12887`.

Primary scout control passed: `p1029_leaf8_scout` had `13` y-filtered strict scout forms, `8` q-diverse groups, `140` predictions, `140` true, and `0` false across raw plus compressed views.

Primary compressed forward summary:

| Pool | Rows | y-filtered strict forms | q-diverse groups | Predictions | True | False |
|---|---:|---:|---:|---:|---:|---:|
| `p1029_leaf8_scout` | 6 | 2 | 4 | 4 | 4 | 0 |

Diagnostic forward summary:

| Pool | Rows | Compressed y-filtered forms | Compressed predictions | Compressed false | Raw predictions | Raw false |
|---|---:|---:|---:|---:|---:|---:|
| `leaf8_all_selectors` | 340 | 2 | 0 | 0 | 0 | 0 |
| `contains_leaf8` | 487 | 2 | 0 | 0 | 0 | 0 |
| `all_target_rows` | 1166 | 3 | 0 | 0 | 0 | 0 |

Fresh primary compressed positive witness:

| Window | Public fingerprint | Terms | Tail | q-values | Predicted target | Source secret |
|---|---|---|---|---|---:|---:|
| `12776_12783` | `[1837,238]` | `[8,8,11,11]` | `[9,12]` | `[2362,9797]` | 8189 | 8189 |

The same witness appears under exact-tail, motif, terms-tail, and gap-tail-shape object models.

## Interpretation
OBSERVATION / FROZEN HOLDOUT POSITIVE / TOY-EVIDENCE: the P1040 public y-residue discriminator survived one fresh 16-window holdout on the strict P1029 route. It produced a new compressed q-diverse exact-factor-matched prediction with zero false primary or diagnostic checks.

This remains an index-calculus precursor. It shows a scalar-stability filter worth extending, not a complete faster-than-rho ECDLP algorithm. The next bottlenecks remain repeated holdout validation, relation volume, sparse linear algebra closure, and target descent.

Next concrete action: create P1042 as a second disjoint y-residue validation starting at `12888_12895`, and separately run a volume/rank audit that accumulates P1038 and P1041 true witnesses to test whether the filtered stream contributes independent relation rows rather than isolated scalar predictions.

## Interpretation boundary
This is a frozen public-disambiguator validation over toy p231 relation-generation artifacts. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, target descent, or a deployable selector. Pollard rho remains the one-target scalar-search baseline.
