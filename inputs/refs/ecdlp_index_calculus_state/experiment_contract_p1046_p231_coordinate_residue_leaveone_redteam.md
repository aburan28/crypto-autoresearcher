# Experiment Contract: P1046 p231 coordinate-residue leave-one red-team

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1045 public coordinate-residue rank gain reflects reusable factor-base structure rather than a small-sample public-partition artifact. Frozen `public_x_mod_11` and `public_y_mod_5` should retain consistent rank behavior under leave-one-public and held-out-artifact tests, and the observed rank should not be matched by bucket shuffles that preserve only the residue multiplicities.

## Null hypothesis
The P1045 rank gain is explainable by public bucket partitioning over five toy publics. Held-out publics require unseen labels, artifact holdouts do not predict new rows without bucket leakage, or shuffled residue assignments match the observed rank and consistency.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- source windows: inherited from the P1044 broad guard, `12504_12511` through `13008_13015`
- rank-row source: persisted primary strict true witness groups from P1038/P1041/P1042
- broad false-positive guard: P1044 all-pool compressed aggregate
- frozen representation models: `public_x_mod_11`, `public_y_mod_5`
- secondary representation models: `public_x_mod_5`, `public_x_mod_7`, `public_y_mod_7`, `public_y_mod_11`
- baseline model: standard global factor index
- controls: exact-public labels and deterministic residue-bucket shuffles
- shuffle trials: `64`

## Metrics
- coefficient rank and augmented rank per frozen model;
- number of leave-one-public folds;
- number of held-out folds requiring unseen labels;
- combined train-plus-holdout rank and augmented-rank consistency;
- rowspace-closed folds;
- shuffled-rank histogram;
- shuffle count matching or exceeding observed rank;
- exact-public overlocal control rank;
- compressed true/false count from P1044.

## Positive control
The standard factor-index model must retain P1045's rank-one behavior, and exact-public labels must remain overlocal diagnostics rather than promotable structure.

## Negative control
Residue-bucket shuffles that preserve only the public bucket multiplicities should not reproduce the frozen model's rank and consistency if the coordinate residue has genuine structural content beyond partition size.

## Success criterion
Strict validation requires at least one frozen public coordinate model to satisfy all of:
- full-model coefficient rank greater than the standard rank;
- full-model augmented rank equal to coefficient rank;
- zero P1044 compressed false predictions;
- every leave-one-public fold uses labels already present in training;
- every leave-one-public combined train-plus-holdout system remains consistent;
- deterministic bucket shuffles do not match or exceed the observed rank under the same consistency criteria.

## Falsification criterion
P1046 is negative for promotion of P1045 if held-out publics mostly require unseen labels, if artifact holdouts fail the same label-reuse check, or if shuffled bucket assignments frequently match the observed rank and consistency. This does not rule out coordinate-residue index calculus; it only blocks treating P1045 as validated factor-base structure.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1046_p231_coordinate_residue_leaveone_redteam.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1046_p231_coordinate_residue_leaveone_redteam.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1046_p231_coordinate_residue_leaveone_redteam_probe.json
```

## Interpretation boundary
This is a red-team validation over toy p231 artifacts. A negative result is scoped to the P1045 rank-promotion claim and does not close the broader index-calculus route. A positive result would still be an index-calculus precursor, not sparse linear algebra closure, target descent, or a faster-than-rho ECDLP algorithm.

## Results
Timestamp: `2026-06-30T05:00:04Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1046_COORDINATE_RESIDUE_NOT_STRICTLY_VALIDATED`

- P1044 broad guard remains clean: `22` compressed predictions, `22` true, `0` false.
- P1045 rank-row input remains `10` unique forms over `5` unique publics.
- Standard factor-index control: coefficient rank `1`, augmented rank `1`.
- Exact-public and exact-x controls: coefficient rank `5`, augmented rank `5`, but marked overlocal and not promotable.
- Frozen `public_x_mod_11`: full coefficient rank `4`, augmented rank `4`; leave-one-public has `2/5` folds with no unseen labels and `3/5` folds requiring unseen labels; artifact holdout has `0/3` no-unseen folds; shuffled bucket controls match the observed rank in `64/64` trials.
- Frozen `public_y_mod_5`: full coefficient rank `4`, augmented rank `4`; leave-one-public has `2/5` no-unseen folds and `3/5` unseen-label folds; artifact holdout has `0/3` no-unseen folds; shuffled bucket controls match the observed rank in `64/64` trials.
- Secondary coordinate models have more leave-one-public reuse in some cases (`public_x_mod_7`, `public_y_mod_7`, and `public_y_mod_11` each have `4/5` no-unseen folds), but their shuffled controls also match observed rank in `64/64` trials.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1046 blocks promoting P1045 coordinate-residue labels as validated factor-base structure. The rank gains remain internally consistent, but the frozen top models are explained by bucket partitioning at this sample size because deterministic residue shuffles preserve the same rank behavior.

This does not rule out coordinate-residue or index-calculus approaches. It narrows the next requirement: find a representation whose factor labels are shared across held-out publics and whose rank/consistency profile separates from bucket-multiplicity shuffles.

## Next concrete action
Build P1047 as a fresh-row representation validation: materialize or import non-overlapping y-residue rank rows, then test rational-map, Kummer-coordinate, trace/norm, or composed public-coordinate labels under the same leave-one-public and shuffled-bucket controls. Success should require held-out label reuse and shuffle separation before any sparse-linear-algebra or below-rho claim.
