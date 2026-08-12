# Experiment Contract: P1045 p231 y-residue representation-change rank scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1043/P1044 factor-rank-one obstruction is specific to the standard global factor-index representation. A feature-preserving representation change may split the stable y-residue residual stream into more than one consistent factor direction while keeping zero compressed false predictions.

## Null hypothesis
Every tested representation either remains rank one, becomes inconsistent, or gains rank only by over-local labels that do not reuse factor labels across forms. This would keep the current route at scalar-stability evidence rather than a useful factor-base relation stream.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source windows: `12504_12511` through `13008_13015`
- source rank floor: `0`
- modulus/order: `11779`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- form family: y-filtered repeated two-tail witnesses that already pass P1044 compressed scalar-stability checks
- frozen public disambiguator: public fingerprint y-coordinate residue mod `11` in `{2,7}`
- required residual class: `5459`
- baseline factor signature: `[(8,11777),(11,11777)]`
- candidate label families: standard index, signed index, public x/y residues, Kummer/x-only residue labels, support-split labels, salt/row-key context labels
- rank-row source: persisted primary strict true witness groups from P1038/P1041/P1042
- broad guard source: P1044 all-pool compressed aggregate over the 64-window adjacent-family scan

## Metrics
- unique witness groups;
- unique forms;
- compressed true/false count;
- label count per representation;
- coefficient rank and augmented rank;
- rank gain over standard factor-index representation;
- label reuse statistics;
- consistency of residual `5459`;
- over-locality diagnostics.

## Positive control
The standard factor-index representation must reproduce P1043/P1044: zero false predictions, residual `5459`, coefficient rank `1`, augmented rank `1`.

## Negative control
Labels that include exact public fingerprint or exact per-form identity are not promotable. Exact salt/row-key labels are reported as diagnostics and must be treated as over-local unless they show meaningful reuse.

## Success criterion
Scout success requires at least one non-overlocal public representation with coefficient rank greater than `1`, augmented rank equal to coefficient rank, residual class `5459`, zero compressed false predictions, and reused labels across multiple forms.

## Falsification criterion
If every non-overlocal representation has rank `1` or augmented inconsistency, P1045 is negative for this representation-change catalog.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1045_p231_yresidue_representation_change_rank_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1045_p231_yresidue_representation_change_rank_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1045_p231_yresidue_representation_change_rank_scout_probe.json
```

## Interpretation boundary
This is a representation-labeling scout over toy p231 artifacts. A positive result is a candidate factor-coordinate system, not a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, target descent, or deployment-relevant break.

## Runtime scope note
The implementation computes rank on concrete persisted primary strict witness forms and uses the P1044 all-pool aggregate as the zero-false / unique-signature guard. It does not rematerialize all 64 windows during P1045, because P1044 already performed that expensive reconstruction.

## Results
Timestamp: `2026-06-30T04:50:18Z` in the probe artifact.

Claim: `P1045_REPRESENTATION_RANK_GAIN_CANDIDATE`

- P1044 broad guard: `22` compressed predictions, `22` true, `0` false, `1` unique compressed factor signature.
- Rank-row input: `5` primary strict witness groups, `10` unique forms, `5` unique publics, `0` residual conflicts.
- Standard factor-index control: coefficient rank `1`, augmented rank `1`.
- Public coordinate candidates:
  - `public_x_mod_11`: coefficient rank `4`, augmented rank `4`, `8` labels, `8` reused labels.
  - `public_y_mod_5`: coefficient rank `4`, augmented rank `4`, `8` labels, `8` reused labels.
  - `public_x_mod_5`, `public_x_mod_7`, and `public_y_mod_7`: coefficient rank `3`, augmented rank `3`.
  - Frozen `public_y_mod_11`: coefficient rank `2`, augmented rank `2`.
- Exact-public, exact-x, row-key, salt, and form-local labels remain diagnostics, not promoted factor-base representations.

## Interpretation
OBSERVATION / TOY-EVIDENCE / MODEL-BOUND: public coordinate-residue labels can split the previously rank-one y-residue residual stream into several consistent reusable directions under this toy p231 artifact set. This is a viable representation-change lead for an index-calculus route, not sparse linear algebra closure, target descent, or a faster-than-rho ECDLP algorithm.

## Next concrete action
Build P1046 as a red-team validation: freeze `public_x_mod_11` and `public_y_mod_5`, run leave-one-public and fresh-heldout tests, include shuffled-residue and exact-public controls, and require rank gain plus zero compressed false predictions before treating coordinate residues as factor-base structure.
