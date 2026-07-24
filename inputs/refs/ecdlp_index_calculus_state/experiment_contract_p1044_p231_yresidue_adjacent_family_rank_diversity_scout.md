# Experiment Contract: P1044 p231 y-residue adjacent-family rank-diversity scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1040/P1041/P1042 y-residue scalar-stability filter can be extended from the strict `[8,8,11,11]` / tail `[9,12]` family to adjacent repeated two-tail families that produce true scalar predictions with factor signatures independent of `[(8,-2),(11,-2)]`.

## Null hypothesis
No adjacent y-filtered repeated two-tail family produces zero-false true scalar predictions with factor-rank gain beyond the known `[8,11]` direction. This would narrow the current route to a stable but rank-one scalar-prediction surface.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source windows: `12504_12511` through `13008_13015`
- source rank floor: `0`
- modulus/order: `11779`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- form family: repeated two-tail `[a,a,b,b]` with any two-tail support
- frozen public disambiguator: public fingerprint y-coordinate residue mod `11` in `{2,7}`
- local scalar rule: same-public same-window q-diverse exact factor-vector equality
- primary view: row-signature-compressed forms
- diagnostic view: raw reconstructed forms

## Metrics
- y-filtered repeated two-tail form count;
- q-diverse object group count;
- factor-matched prediction count;
- true/false toy-secret verification count;
- unique factor signatures;
- residual classes per factor signature;
- factor rank when adding each signature to the known base direction;
- zero-false independent-signature candidates.

## Positive control
The known strict family must be recovered as a zero-false factor-rank-one signal with factor signature `[(8,11777),(11,11777)]` and residual `5459`.

## Negative control
Candidate signatures are not allowed to use toy-secret labels for selection. Labels are used only for scoring. Any signature with a false prediction is not promotable.

## Success criterion
Scout success requires at least one non-base factor signature with nonzero true predictions, zero false predictions, consistent residuals, and factor-rank gain when combined with the known base signature.

## Falsification criterion
If every non-base signature has zero predictions, any false predictions, residual inconsistency, or no factor-rank gain, P1044 is negative for this adjacent-family catalog.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1044_p231_yresidue_adjacent_family_rank_diversity_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout_probe.json
```

## Results
Run timestamp: `2026-06-30T04:35:33Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout_probe.json`.

Claim status: `NEGATIVE_RESULT_P1044_NO_INDEPENDENT_YRESIDUE_SIGNATURE`.

Implementation note: the final run reconstructs compressed forms per window before recombining them. This avoids over-deduplicating later-window witnesses in a long accumulated scan.

Source windows: `12504_12511` through `13008_13015` (`64` windows).

Compressed summary:

| Metric | Value |
|---|---:|
| compressed predictions | 22 |
| compressed true | 22 |
| compressed false | 0 |
| unique compressed factor signatures | 1 |
| independent signatures | 0 |
| rank-diversity candidates | 0 |

Compressed pool summary:

| Pool | y-filtered forms | q-diverse groups | Predictions | True | False |
|---|---:|---:|---:|---:|---:|
| `p1029_leaf8_scout` | 40 | 20 | 5 | 5 | 0 |
| `leaf8_all_selectors` | 76 | 24 | 6 | 6 | 0 |
| `contains_leaf8` | 76 | 24 | 6 | 6 | 0 |
| `all_target_rows` | 68 | 20 | 5 | 5 | 0 |

The only compressed factor signature is the known base direction:

| Factor signature | True | False | Residual | Factor rank with base | Families | Pools |
|---|---:|---:|---|---:|---|---|
| `[(8,11777),(11,11777)]` | 22 | 0 | `5459` | 1 | terms `[8,8,11,11]`, tail `[9,12]` | all four pools |

Raw diagnostics are noisier: `31` raw predictions, `27` true, `4` false, and `5` unique raw factor signatures. These raw signatures are not promotable without a compressed zero-false counterpart.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE: within the scanned adjacent-family catalog, the y-residue filter did not expose any compressed factor signature independent of the known `[8,11]` direction. P1044 therefore does not solve the P1043 factor-rank bottleneck.

OBSERVATION: the corrected accumulated compressed scan strengthens the scalar-stability observation: across all four row pools and `64` windows, every compressed y-filtered prediction is true and all share residual `5459`.

Next concrete action: move from adjacent-family widening to a feature-preserving representation change. P1045 should keep the y-residue filter and residual `5459`, but search for a second factor direction by changing factor labeling or coordinates: support-split labels, signed/negated factor aliases, Kummer/x-only labels, or row-key/salt-context factor columns. Success requires factor rank greater than `1` with zero compressed false predictions.

## Interpretation boundary
This is a post-rank-obstruction scout over toy p231 artifacts. It can identify adjacent rank-diversity candidates, but any candidate must be frozen and validated on fresh windows before being promoted. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, target descent, or deployment relevance.
