# Experiment Contract: P1050 p231 nonlinear two-feature transform audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1049 failed because one-feature coefficient transforms are generic one-dimensional lifts. A nonlinear two-feature channel representation may create a higher-dimensional public-coordinate rowspace that carries broad-only validation rows and is not reproduced by matched random two-feature controls.

## Null hypothesis
Every tested two-feature public-coordinate transform either fails to carry validation rows in the train span, or its rank/rowspace profile is reproduced by shuffled feature pairs, matched random feature pairs, or full-field random feature pairs.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- train rows: P1045 persisted primary strict true witness forms from P1038/P1041/P1042
- validation source: full P1044-scope rematerialized compressed row pools, excluding train form identities
- start window: `12504_12511`
- rematerialization windows: `64`
- required factor signature: `[(8,11777),(11,11777)]`
- required residual class: `5459`
- baseline: constant-free differential rowspace
- public feature pairs: `(x,y)`, `(x,y/x)`, `(x,y/(x+1))`, `(x,x+1/x)`, `(y,x+1/x)`, `(x+y,x*y)`, `(x^2-4y,x+1/x)`, `(y/(x+1),x^2-4y)`, `(x mod 11,y mod 5)`
- channel modes: direct pair, cross pair, quadratic pair, full pair, antisymmetric pair
- controls per model: `64` shuffled-pair, matched-random-pair, and full-field-random-pair trials

## Metrics
- train row count, validation row count, unique public count;
- broad compressed true/false prediction counts;
- constant-free train rank;
- validation rank;
- combined rank;
- validation-in-train-span predicate;
- shuffled-pair candidate-like count;
- matched-random-pair candidate-like count;
- full-field-random-pair candidate-like count;
- exact artifact and source hashes.

## Positive control
The standard constant-free rowspace from P1049 must have rank `0`; P1050 only scores nonconstant feature channels.

## Negative controls
Shuffled observed feature pairs, matched random feature pairs drawn from observed marginal feature values, and full-field random feature pairs must not reproduce the same candidate rank/rowspace profile if the public-coordinate pair has algebraic content.

## Success criterion
Strict validation requires at least one public two-feature channel model with:
- train constant-free rank greater than `0`;
- at least one nonzero broad-only validation row;
- combined rank equal to train rank;
- zero broad compressed false predictions;
- no shuffled-pair control matching or exceeding the observed candidate rank;
- no matched-random-pair control matching or exceeding the observed candidate rank;
- no full-field-random-pair control matching or exceeding the observed candidate rank.

## Falsification criterion
P1050 is negative for this nonlinear two-feature catalog if every candidate profile is reproduced by any matched null family. This is a scoped negative for these public channel transforms over the P1044 y-residue stream, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1050_p231_nonlinear_two_feature_transform_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1050_p231_nonlinear_two_feature_transform_audit_probe.json
```

## Interpretation boundary
This is a null-model audit over toy p231 artifacts. A pass would be a candidate representation signal only; it would still require relation collection, sparse linear algebra, target descent, scaling, and Pollard-rho cost comparison.

## Results
Timestamp: `2026-06-30T05:43:46Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1050_TWO_FEATURES_MATCH_MATCHED_RANDOM_NULL`

- Full P1044-scope rematerialization: `64/64` forward windows exist.
- Rematerialized compressed predictions: `7` total, `7` true, `0` false.
- Base-signature rows: `14` broad rows total, `4` broad-only validation rows after excluding P1045 strict train forms.
- Tested nonlinear two-feature channel models: `45`.
- Public candidates before red-team: `45/45`.
- Strict validation passes: `0`.
- Matched-random-pair red team reproduces `45/45` public candidates.
- Full-field-random-pair red team reproduces `45/45` public candidates.
- Shuffled-pair red team reproduces `45/45` public candidates.
- Strongest public profile: `xmod11_ymod5__quadratic_pair`, with `4` channels, train rank `4`, validation rank `2`, combined rank `4`; matched random controls match or exceed its rank in `50/64` trials, full random controls in `64/64`, and shuffled controls in `64/64`.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1050 extends P1049 from one-dimensional feature lifts to nonlinear two-feature channel lifts. The public-coordinate channel profiles carry held-out rows, but matched random two-feature channels carry them too. This blocks promotion of the tested nonlinear channel catalog as factor-base structure.

This does not close the index-calculus route. It narrows the next requirement: move away from public-feature lifts and test representation constraints that impose algebraic identities, not just rowspace capacity.

## Next concrete action
Build P1051 as an invariant-constraint audit: instead of adding feature channels, test whether public coordinates satisfy low-degree polynomial identities among row coefficients and residuals that are absent from matched random rows. Success should require an overdetermined identity with held-out validation and random-row separation.
