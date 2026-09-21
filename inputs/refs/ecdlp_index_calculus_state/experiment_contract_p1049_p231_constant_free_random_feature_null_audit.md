# Experiment Contract: P1049 p231 constant-free random-feature null audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: After subtracting the standard rank-one relation, at least one public-coordinate coefficient transform has constant-free held-out structure that deterministic random features do not reproduce.

## Null hypothesis
Once the standard relation is removed, every public-coordinate transform is either constant-free rank zero, fails to carry broad-only validation rows in the train span, or behaves no better than shuffled/random public features.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- train rows: P1045 persisted primary strict true witness forms from P1038/P1041/P1042
- validation source: full P1044-scope rematerialized compressed row pools, excluding train form identities
- start window: `12504_12511`
- rematerialization windows: `64`
- required factor signature: `[(8,11777),(11,11777)]`
- required residual class: `5459`
- baseline subtraction: for each row, score `transformed_coefficients - standard_coefficients` with zero RHS
- coefficient feature catalog: same public features and transform modes as P1048
- controls: deterministic public-feature shuffles and deterministic random public features
- control trials per model: `64`

## Metrics
- train row count, validation row count, unique public count;
- broad compressed true/false prediction counts;
- constant-free train rank;
- constant-free validation rank;
- constant-free combined rank;
- validation rows in train span;
- shuffled-feature candidate-like count;
- random-feature candidate-like count;
- exact artifact and source hashes.

## Positive control
The standard factor-index relation must disappear under baseline subtraction: constant-free rank `0`.

## Negative control
Deterministic random public features must not satisfy the same constant-free held-out success predicate if the public-coordinate feature has algebraic content beyond generic feature variation.

## Success criterion
Strict validation requires at least one public-coordinate transform with:
- constant-free train rank greater than `0`;
- at least one nonzero broad-only validation row;
- combined constant-free rank equal to train constant-free rank;
- zero broad compressed false predictions;
- no shuffled-feature control matching or exceeding observed rank under the same predicate;
- no random-feature control matching or exceeding observed rank under the same predicate.

## Falsification criterion
P1049 is negative for this transform catalog if all public-coordinate constant-free candidates are reproduced by shuffled or random feature controls. This is a scoped negative for affine/one-sided coefficient transforms over the P1044 y-residue stream, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1049_p231_constant_free_random_feature_null_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1049_p231_constant_free_random_feature_null_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1049_p231_constant_free_random_feature_null_audit_probe.json
```

## Interpretation boundary
This is a null-model audit over toy p231 artifacts. A pass would be a candidate representation signal only; it would still require relation collection, sparse linear algebra, target descent, scaling, and Pollard-rho cost comparison.

## Results
Timestamp: `2026-06-30T05:34:45Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1049_PUBLIC_FEATURES_MATCH_RANDOM_NULL`

- Full P1044-scope rematerialization: `64/64` forward windows exist.
- Rematerialized compressed predictions: `7` total, `7` true, `0` false.
- Base-signature rows: `14` broad rows total, `4` broad-only validation rows after excluding P1045 strict train forms.
- Standard constant-free control: combined rank `0`, train nonzero rows `0`, validation nonzero rows `0`.
- Tested public-coordinate transforms: `50`.
- Constant-free public candidates: `47/50`.
- Strict validation passes: `0`.
- Random-feature red team: `47/47` public candidates are reproduced by deterministic random public features.
- Shuffle red team: `47/47` public candidates are reproduced by deterministic shuffled public features.
- Typical surviving model profile: train constant-free rank `1`, validation rank `1`, combined rank `1`, with random controls also rank `1` in `64/64` trials.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1049 removes the standard rank-one relation and shows that the surviving affine/one-sided transforms are generic rank-one feature lifts. They are not coordinate-specific structure, because deterministic random public features satisfy the same constant-free held-out predicate.

This does not close the index-calculus route. It narrows the next requirement: a representation must create structure beyond a one-dimensional feature lift, or it must beat a matched random-feature baseline on rank profile, rowspace carry, or invariant algebra.

## Next concrete action
Build P1050 as a nonlinear two-feature transform audit: use paired public features on the two factor columns, include cross terms such as `(x,y)`, `(x,y/x)`, `(x+1/x,y)`, and require a rank/rowspace profile that exceeds matched random two-feature controls on the same held-out broad rows.
