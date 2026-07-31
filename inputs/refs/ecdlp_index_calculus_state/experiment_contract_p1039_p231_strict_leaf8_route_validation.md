# Experiment Contract: P1039 p231 strict leaf-8 route validation

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1038 narrow positive signal is tied to the strict P1029 leaf-8 route, not to the broad row pools. Freezing `p1029_leaf8_scout`, terms `[8,8,11,11]`, tail support `[9,12]`, same-public same-window q-diversity, exact local factor-vector equality, and the public guard `term_gap >= 3 OR tail_width >= 3` should produce fresh forward compressed target predictions with zero false toy-secret checks on windows beyond `12624_12631`.

## Null hypothesis
The strict route has no fresh q-diverse supply, has q-diverse supply but no exact factor-vector match, or produces any false compressed prediction. This would narrow the strict-route P1038 observation; it would not disprove index calculus or other representations.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- forward validation windows: `12632_12639` through `12752_12759`
- source rank floor: `0`
- modulus/order: `11779`
- primary row pool: `p1029_leaf8_scout`
- diagnostic row pools: `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- strict family: terms `[8,8,11,11]`, tail support `[9,12]`
- object models: exact tail, motif, exact terms plus tail support, and shifted gap-tail shape
- primary view: row-signature-compressed forms
- diagnostic view: raw reconstructed forms and widened row pools

## Metrics
- source windows available;
- primary and diagnostic row counts;
- strict family form count;
- q-diverse same-public same-window object group count;
- factor-matched prediction count;
- true/false toy-secret verification count;
- factor-matchless q-diverse group count;
- widened-pool diagnostic false count.

## Positive control
The scout-window primary compressed control must preserve the original clean leaf-8 signal: nonzero true predictions and zero false predictions under the strict family.

## Negative control
The forward validation windows must be disjoint from the P1038 windows. Widened pools are reported as red-team diagnostics and cannot be used to promote the primary strict-route claim.

## Success criterion
Primary success requires at least one forward compressed factor-matched prediction and zero forward compressed false predictions in `p1029_leaf8_scout`.

## Falsification criterion
Any primary forward compressed false prediction falsifies this strict route for the scanned slice. If there are no primary compressed predictions but q-diverse groups exist, the bottleneck is exact factor-vector compatibility. If there are no q-diverse groups, the bottleneck is strict-route relation supply.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1039_p231_strict_leaf8_route_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1039_p231_strict_leaf8_route_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1039_p231_strict_leaf8_route_validation_probe.json
```

## Results
Run timestamp: `2026-06-30T03:54:31Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1039_p231_strict_leaf8_route_validation_probe.json`.

Claim status: `NEGATIVE_RESULT_P1039_STRICT_ROUTE_FALSE_PREDICTION`.

Forward windows: `12632_12639`, `12640_12647`, `12648_12655`, `12656_12663`, `12664_12671`, `12672_12679`, `12680_12687`, `12688_12695`, `12696_12703`, `12704_12711`, `12712_12719`, `12720_12727`, `12728_12735`, `12736_12743`, `12744_12751`, `12752_12759`.

Primary scout control passed: `p1029_leaf8_scout` had `13` strict scout forms, `8` q-diverse groups, `140` predictions, `140` true, and `0` false across raw plus compressed views.

Primary compressed forward summary:

| Pool | Rows | Strict forms | q-diverse groups | Predictions | True | False |
|---|---:|---:|---:|---:|---:|---:|
| `p1029_leaf8_scout` | 4 | 2 | 4 | 4 | 0 | 4 |

Diagnostic forward summary:

| Pool | Rows | Compressed strict forms | Compressed predictions | Compressed false | Raw predictions | Raw false |
|---|---:|---:|---:|---:|---:|---:|
| `leaf8_all_selectors` | 336 | 9 | 4 | 4 | 128 | 128 |
| `contains_leaf8` | 483 | 9 | 4 | 4 | 288 | 288 |
| `all_target_rows` | 1056 | 6 | 0 | 0 | 288 | 288 |

Primary compressed false witness:

| Window | Public fingerprint | Terms | Tail | q-values | Predicted target | Source secret |
|---|---|---|---|---|---:|---:|
| `12704_12711` | `[9665,1060]` | `[8,8,11,11]` | `[9,12]` | `[8099,10611]` | 3712 | 7344 |

The same false witness appears under exact-tail, motif, terms-tail, and gap-tail-shape object models.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE: the strict `p1029_leaf8_scout` route does not generalize unchanged from P1038 to the fresh `12632_12639..12752_12759` holdout. The failure is not lack of relation supply or q-diversity; it is scalar instability under exact local factor-vector elimination.

Next concrete action: create P1040 as a public disambiguator scout over the clean P1038 positives and the P1039 false witness. The candidate features should remain public and local: source row-key/salt provenance, exact duplicate/compression multiplicity, q/rhs deltas, sign pattern of tail coefficients, public fingerprint residues, and whether raw and compressed views agree before promoting any stricter selector.

## Interpretation boundary
This is a strict-route relation-generation validation. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, or target descent. Pollard rho remains the one-target scalar-search baseline.
