# Experiment Contract: P1042 p231 y-residue second-holdout validation

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The frozen P1040/P1041 public y-residue selector `public_y mod 11 in {2,7}` continues to filter scalar-unstable strict leaf-8 witnesses while preserving scalar-stable strict-route relation supply on a second disjoint fresh window block.

## Null hypothesis
The selector has no fresh relation supply, has q-diverse supply but no exact factor-vector match, or produces any false compressed prediction on the second holdout. This would narrow or falsify the y-residue route, not the broader index-calculus objective.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- forward validation windows: `12888_12895` through `13008_13015`
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
The forward validation windows must be disjoint from P1038, P1039, and P1041 validation windows. Widened pools are reported as red-team diagnostics and cannot promote the primary strict-route claim.

## Success criterion
Primary success requires at least one forward compressed factor-matched prediction and zero forward compressed false predictions in `p1029_leaf8_scout` after the y-residue filter.

## Falsification criterion
Any primary forward compressed false prediction falsifies this frozen y-residue selector for the scanned slice. If there are no primary compressed predictions but y-filtered q-diverse groups exist, the bottleneck is exact factor-vector compatibility. If there are no q-diverse groups, the bottleneck is filtered relation supply.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1042_p231_yresidue_second_holdout_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1042_p231_yresidue_second_holdout_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json
```

## Results
Run timestamp: `2026-06-30T04:12:49Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json`.

Claim status: `P1042_YRESIDUE_STRICT_ROUTE_FORWARD_SUPPLY_SIGNAL`.

Forward windows: `12888_12895`, `12896_12903`, `12904_12911`, `12912_12919`, `12920_12927`, `12928_12935`, `12936_12943`, `12944_12951`, `12952_12959`, `12960_12967`, `12968_12975`, `12976_12983`, `12984_12991`, `12992_12999`, `13000_13007`, `13008_13015`.

Primary compressed forward summary:

| Pool | Rows | y-filtered strict forms | q-diverse groups | Predictions | True | False |
|---|---:|---:|---:|---:|---:|---:|
| `p1029_leaf8_scout` | 10 | 4 | 8 | 8 | 8 | 0 |

Diagnostic forward summary:

| Pool | Rows | Compressed y-filtered forms | Compressed predictions | Compressed false | Raw predictions | Raw false |
|---|---:|---:|---:|---:|---:|---:|
| `leaf8_all_selectors` | 312 | 9 | 4 | 0 | 64 | 0 |
| `contains_leaf8` | 462 | 9 | 4 | 0 | 196 | 0 |
| `all_target_rows` | 1023 | 4 | 0 | 0 | 196 | 0 |

Fresh primary compressed positive witnesses:

| Window | Public fingerprint | Terms | Tail | q-values | Predicted target | Source secret |
|---|---|---|---|---|---:|---:|
| `12968_12975` | `[9166,10292]` | `[8,8,11,11]` | `[9,12]` | `[3698,4833]` | 1936 | 1936 |
| `13008_13015` | `[10378,8246]` | `[8,8,11,11]` | `[9,12]` | `[6530,10597]` | 11669 | 11669 |

Both witnesses appear under exact-tail, motif, terms-tail, and gap-tail-shape object models.

## Interpretation
OBSERVATION / SECOND FROZEN HOLDOUT POSITIVE / TOY-EVIDENCE: the frozen y-residue selector survived a second disjoint 16-window holdout and increased primary compressed true relation-supply volume without any primary or diagnostic false checks.

This still does not prove a complete faster-than-rho ECDLP algorithm. The next bottleneck is whether these true scalar-prediction pairs add independent relation rows or only repeat the same low-dimensional local-factor pattern.

Next concrete action: P1043 completed the volume/rank audit over the P1038, P1041, and P1042 y-residue true witnesses. Follow P1043's handoff: search adjacent repeated two-tail families for globally consistent residual classes with factor signatures independent of `[(8,-2),(11,-2)]`.

## Interpretation boundary
This is a second frozen public-disambiguator validation over toy p231 relation-generation artifacts. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, target descent, or a deployable selector. Pollard rho remains the one-target scalar-search baseline.
