# Experiment Contract: P1038 p231 guarded structural-family supply search

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1037 public guard `term_gap_ge_3 OR tail_width_ge_3` rejects the compressed P1036 false witness while preserving the clean scout signal. Applying this pre-registered guard to a forward slice of expanded-source windows may find same-public same-window q-diverse repeated two-tail groups with strict factor-matched target predictions and zero false toy-secret checks.

## Null hypothesis
The guarded structural family has no forward q-diverse supply, or has q-diverse supply but no exact local factor-vector match. This would be a guarded relation-supply negative, not a disproof of index calculus.

## Frozen guard
- repeated two-tail form shape `[a,a,b,b]` with two tail-support indices;
- `fresh_validation` only;
- same public fingerprint and same window;
- object models: exact tail, motif, exact terms plus tail support, and shifted gap-tail shape;
- public guard: `term_gap >= 3 OR tail_width >= 3`;
- strict target prediction requires exact local factor-vector equality.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- forward validation windows: `12504_12511` through `12624_12631`
- source rank floor: `0`
- modulus/order: `11779`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- primary view: row-signature-compressed forms
- diagnostic view: raw reconstructed forms

## Metrics
- available forward source windows;
- input row count per pool;
- reconstruction error count;
- guarded eligible form count;
- guarded same-public same-window object group count;
- q-diverse group count;
- factor-matched prediction count;
- true/false toy-secret verification count;
- factor-matchless q-diverse group count.

## Positive control
The scout-window compressed control must preserve the P1033/P1036 clean signal: nonzero true predictions and zero false predictions under the frozen guard.

## Negative control
The forward windows must not include the scout/control window. Raw duplicate-sensitive diagnostics are reported separately; the primary claim uses compressed forms.

## Success criterion
Primary success requires at least one forward compressed factor-matched prediction and zero forward compressed false predictions under the frozen guard.

## Falsification criterion
Any forward compressed false prediction falsifies this guarded structural-family rule for the scanned slice. If no forward compressed prediction exists but guarded q-diverse groups exist, the next bottleneck is local factor-vector compatibility. If no guarded q-diverse group exists, the next bottleneck is guarded relation supply.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1038_p231_guarded_structural_family_supply_search.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1038_p231_guarded_structural_family_supply_search.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json
```

## Results
Run timestamp: `2026-06-30T03:43:21Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json`.

Claim status: `NEGATIVE_RESULT_P1038_GUARDED_COMPRESSED_FALSE_PREDICTION`.

Forward windows: `12504_12511`, `12512_12519`, `12520_12527`, `12528_12535`, `12536_12543`, `12544_12551`, `12552_12559`, `12560_12567`, `12568_12575`, `12576_12583`, `12584_12591`, `12592_12599`, `12600_12607`, `12608_12615`, `12616_12623`, `12624_12631`.

Primary compressed forward summary by pool:

| Pool | Rows | Eligible forms | q-diverse groups | Predictions | True | False |
|---|---:|---:|---:|---:|---:|---:|
| `p1029_leaf8_scout` | 11 | 32 | 8 | 8 | 8 | 0 |
| `leaf8_all_selectors` | 372 | 64 | 8 | 16 | 0 | 16 |
| `contains_leaf8` | 543 | 64 | 8 | 16 | 0 | 16 |
| `all_target_rows` | 1243 | 44 | 4 | 4 | 0 | 4 |

Diagnostic raw forward summary:

| Pool | Raw predictions | Raw false |
|---|---:|---:|
| `p1029_leaf8_scout` | 52 | 0 |
| `leaf8_all_selectors` | 1152 | 1152 |
| `contains_leaf8` | 1808 | 1808 |
| `all_target_rows` | 2164 | 1824 |

The strict P1029 leaf-8 route produced two unique compressed forward toy-secret-verified relation predictions, repeated across four object models:

| Window | Public fingerprint | Terms | Tail | q-values | Predicted target | Source secret |
|---|---|---|---|---|---:|---:|
| `12520_12527` | `[5063,6547]` | `[8,8,11,11]` | `[9,12]` | `[7344,9170]` | 11550 | 11550 |
| `12552_12559` | `[4643,5694]` | `[8,8,11,11]` | `[9,12]` | `[646,4641]` | 440 | 440 |

The broader row pools falsify the general guarded rule. Representative compressed false witnesses include:

| Pool | Window | Public fingerprint | Terms | Tail | q-values | Predicted target | Source secret |
|---|---|---|---|---|---|---:|---:|
| `leaf8_all_selectors` / `contains_leaf8` | `12600_12607` | `[8882,1996]` | `[8,8,11,11]` | `[9,12]` | `[4461,7020,10796]` | 565 | 3771 |
| `leaf8_all_selectors` / `contains_leaf8` / `all_target_rows` | `12520_12527` | `[9276,1004]` | `[8,8,11,11]` | `[9,12]` | `[7344,9170]` | 11550 | 6714 |

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE: the broad frozen guard `term_gap >= 3 OR tail_width >= 3` is not sufficient once the row source is widened beyond the strict P1029 route.

OBSERVATION / INDEX-CALCULUS PRECURSOR: the strict `p1029_leaf8_scout` route produced forward q-diverse compressed supply with exact local factor-vector matches and zero false toy-secret checks in this slice. This is a narrow relation-generation signal, not a complete algorithm.

Next concrete action: create P1039 as a strict-route validation that freezes `p1029_leaf8_scout`, terms `[8,8,11,11]`, tail `[9,12]`, same-public same-window q-diversity, exact local factor-vector equality, and the P1037 public guard, then scans fresh windows beyond `12624_12631` while treating widened pools only as red-team diagnostics.

## Interpretation boundary
This is a guarded relation-generation supply experiment. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, or target descent. Pollard rho remains the one-target scalar-search baseline.
