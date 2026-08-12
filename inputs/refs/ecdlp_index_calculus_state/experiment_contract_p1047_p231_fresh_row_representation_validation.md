# Experiment Contract: P1047 p231 fresh-row representation validation

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: Although P1046 showed that simple coordinate residues are not validated factor-base structure, a richer public representation may transfer from the P1045 strict rows to fresh broad P1044 rows while separating from bucket-multiplicity shuffles.

## Null hypothesis
The broader compressed stream either provides too few strict-base residual rows under the bounded rematerialization budget, or every tested representation still depends on unseen held-out labels or has a shuffled-bucket control that reproduces the observed rank behavior.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- train rows: P1045 persisted primary strict true witness forms from P1038/P1041/P1042
- validation source: rematerialized P1044 compressed row pools, excluding train form identities
- start window: `12504_12511`
- bounded rematerialization windows: `64`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- required factor signature: `[(8,11777),(11,11777)]`
- required residual class: `5459`
- baseline: standard global factor-index labels
- frozen residue controls: `public_x_mod_11`, `public_y_mod_5`, `public_x_mod_7`, `public_y_mod_7`
- richer candidate families: coordinate-pair, rational-map, Kummer-inspired x-only, trace-like sum, norm-like product, and discriminant-like public buckets
- shuffle trials per model: `64`

## Metrics
- train row count, validation row count, unique public count;
- bounded broad compressed true/false prediction counts;
- coefficient and augmented rank on train rows;
- coefficient and augmented rank on train-plus-validation rows;
- validation rows whose labels are already present in training;
- shuffle count matching or exceeding observed combined rank;
- shuffle count satisfying the same held-out success predicate;
- exact artifact and source hashes.

## Positive control
The standard factor-index model must retain rank-one behavior on the strict train set. The P1046 frozen top models must not be promoted unless they satisfy held-out label reuse and shuffle separation on the fresh-row split.

## Negative control
For every public-bucket representation, deterministic shuffles of the public-to-bucket map must fail to reproduce the observed rank/consistency if the representation contains structure beyond bucket multiplicity.

## Success criterion
Strict validation requires at least one non-overlocal public representation with:
- train coefficient rank greater than standard train rank;
- train augmented rank equal to train coefficient rank;
- at least one broad-only validation row;
- every validation row using only labels observed in training;
- train-plus-validation augmented rank equal to coefficient rank;
- zero bounded compressed false predictions;
- no shuffled-bucket control matching or exceeding the observed combined rank under the same held-out predicate.

## Falsification criterion
P1047 is negative for the tested representation catalog if validation rows are absent or too sparse, if held-out rows require unseen labels, or if bucket shuffles reproduce the observed rank/consistency. This is a scoped negative for this representation catalog and bounded row block, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1047_p231_fresh_row_representation_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1047_p231_fresh_row_representation_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1047_p231_fresh_row_representation_validation_probe.json
```

## Interpretation boundary
This experiment tests whether a representation catalog can survive a fresh-row split after P1046. It does not test sparse linear algebra closure, target descent, cryptographic-size scaling, or a faster-than-rho end-to-end ECDLP algorithm.

## Results
Timestamp: `2026-06-30T05:15:46Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1047_HELDOUT_CANDIDATES_FAIL_SHUFFLE_SEPARATION`

- Full P1044-scope rematerialization: `64/64` forward windows exist.
- Rematerialized compressed predictions: `7` total, `7` true, `0` false.
- Base-signature rows: `14` broad rows total, `4` broad-only validation rows after excluding P1045 strict train forms.
- Public coverage: `7` unique broad publics, `2` unique validation publics.
- Standard factor-index control: train coefficient rank `1`, train augmented rank `1`.
- Tested representation catalog size: `12` models.
- Held-out candidate count before shuffle red-team: `1`.
- Strict validation passes: `0`.
- Only held-out candidate: `public_x_mod_11`, with train rank `4`, train augmented rank `4`, combined rank `4`, combined augmented rank `4`, and `4/4` validation rows using labels seen in training.
- Red-team failure for `public_x_mod_11`: `64/64` shuffled public-bucket controls matched or exceeded observed combined rank, `64/64` matched exactly, and `39/64` also satisfied the held-out success predicate.
- Other richer representation families, including coordinate-pair, rational-map, Kummer-inspired, trace-like, norm-like, and discriminant-like buckets, failed held-out label reuse or rank/consistency before shuffle separation.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1047 strengthens P1046. The simple `public_x_mod_11` representation is the only tested catalog member that transfers to the broad-only P1044 validation rows, but it still does not separate from bucket-multiplicity shuffles. This means the current evidence supports a reusable x-bucket partition signal, not validated factor-base structure.

This does not close the index-calculus route. It identifies the next missing property: a representation must impose algebraic structure on shared factor directions, not merely assign publics into reusable buckets.

## Next concrete action
Build P1048 as a coefficient-transform representation audit: keep global factor labels fixed and transform coefficients by public rational/Kummer/trace-like functions. This tests whether public coordinates can alter the relation row itself while preserving held-out label reuse, and it should include shuffled-feature controls before any rank-gain claim.
