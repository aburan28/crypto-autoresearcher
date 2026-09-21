# Experiment Contract: P1048 p231 coefficient-transform representation audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1046/P1047 failed because bucket labels split factor identities without changing the actual relation row. A public-coordinate coefficient transform may expose a nontrivial representation where global factor labels stay fixed, train rows gain consistent rank, and fresh broad-only validation rows remain consistent.

## Null hypothesis
All tested public-coordinate coefficient transforms either remain rank one, become augmented-inconsistent, fail on broad-only validation rows, or have shuffled-feature controls that reproduce the observed rank/consistency.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- train rows: P1045 persisted primary strict true witness forms from P1038/P1041/P1042
- validation source: full P1044-scope rematerialized compressed row pools, excluding train form identities
- start window: `12504_12511`
- rematerialization windows: `64`
- required factor signature: `[(8,11777),(11,11777)]`
- required residual class: `5459`
- labels: global factor index only; no public bucket label split
- coefficient feature families: x, y, x/y-style rational functions, Kummer-inspired x+1/x, trace-like x+y, norm-like x*y, and discriminant-like x^2-4y
- transform modes: factor-difference linear weights and one-sided feature weights
- shuffle trials per model: `64`

## Metrics
- train row count, validation row count, unique public count;
- broad compressed true/false prediction counts;
- standard factor-index coefficient and augmented rank;
- transformed train and combined coefficient rank;
- transformed train and combined augmented rank;
- validation consistency;
- shuffled-feature rank and success-like counts;
- exact artifact and source hashes.

## Positive control
The standard factor-index model must remain rank one and consistent on the strict train set.

## Negative control
Deterministic public-feature shuffles must fail to reproduce any observed consistent rank gain if the transform is using algebraic public-coordinate structure rather than only feature multiplicity.

## Success criterion
Strict validation requires at least one coefficient-transform model with:
- fixed global factor labels;
- train coefficient rank greater than standard train rank;
- train augmented rank equal to train coefficient rank;
- at least one broad-only validation row;
- train-plus-validation augmented rank equal to coefficient rank;
- zero broad compressed false predictions;
- no shuffled-feature control matching or exceeding the observed combined rank under the same success predicate.

## Falsification criterion
P1048 is negative for this transform catalog if all models are rank-one, augmented-inconsistent, validation-inconsistent, or reproduced by shuffled-feature controls. This is a scoped negative for coefficient transforms over the P1044 y-residue stream, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1048_p231_coefficient_transform_representation_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1048_p231_coefficient_transform_representation_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1048_p231_coefficient_transform_representation_audit_probe.json
```

## Interpretation boundary
This is a representation audit over toy p231 artifacts. A pass would be a candidate index-calculus representation signal only; it would still require relation collection, sparse linear algebra, target descent, and Pollard-rho cost comparison before any algorithmic speedup claim.

## Results
Timestamp: `2026-06-30T05:26:04Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1048_COEFFICIENT_TRANSFORMS_FAIL_SHUFFLE_SEPARATION`

- Full P1044-scope rematerialization: `64/64` forward windows exist.
- Rematerialized compressed predictions: `7` total, `7` true, `0` false.
- Base-signature rows: `14` broad rows total, `4` broad-only validation rows after excluding P1045 strict train forms.
- Standard factor-index control: train rank `1`, train augmented rank `1`, combined rank `1`, combined augmented rank `1`.
- Tested coefficient-transform catalog size: `50` models.
- Rank-gain models: `50/50`.
- Train-consistent rank-gain models: `50/50`.
- Held-out candidate models before shuffle red-team: `50/50`.
- Strict validation passes: `0/50`.
- Red-team outcome: for every tested model, `64/64` shuffled-feature controls matched or exceeded the observed rank, `64/64` matched the rank histogram, and `64/64` also satisfied the held-out success predicate.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1048 rules out the tested affine/one-sided coefficient transforms as validated representation structure. The universal pre-red-team success is itself diagnostic: these transforms create a constant/feature two-column lift where the constant residual lies in the lifted row span, and shuffled public features reproduce the same effect.

This does not close the index-calculus route. It narrows the next requirement: a coefficient transform must beat random or shuffled public features after removing trivial constant-column span effects.

## Next concrete action
Build P1049 as a constant-free/random-feature null audit: compare public coordinate transforms against deterministic random features, require success after removing any constant column or affine feature column, and only promote transforms that outperform random/shuffled controls on held-out broad rows.
