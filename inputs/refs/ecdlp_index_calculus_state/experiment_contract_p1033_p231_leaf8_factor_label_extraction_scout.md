# Experiment Contract: P1033 p231 leaf-8 factor-label extraction scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1032's leaf `[8]` local row-key/salt-pair diagnostic coherence may hide a more precise factor-label rule. Splitting factor labels per nonzero factor term, rather than per whole form, may either produce a public-shared pre-elimination factor merge or isolate row-local factor objects whose paired equations derive a target scalar.

## Null hypothesis
All public-shared factor-label rules remain augmented-inconsistent, and any local target prediction is either absent, false under toy-secret verification, or too tied to local target variables to guide index-calculus relation generation.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- primary scope: P1029 leaf `[8]`, row-signature compressed
- reference scope: P1022 leaf `[19]`, row-signature compressed
- source windows:
  - training: P1022 positive calibration plus validation through `12432_12439`
  - negative controls: `12224_12231`, `12264_12271`, `12320_12327`
  - fresh: `12440_12447` through `12496_12503`
- modulus/order: `11779`
- factor-label catalog:
  - global term;
  - term plus coefficient;
  - public/x-only term;
  - row-key term;
  - salt term;
  - support/tail/motif/exact-tail term;
  - row/salt plus support;
  - row/salt plus coefficient;
  - per-form term positive control.
- local target-prediction catalog:
  - row-vector object: same public, same row key, same nonzero factor vector;
  - salt-vector object: same public, same salt/terms/tail support;
  - exact-tail object: same public and exact tail expression;
  - motif object: same public and normalized motif key.

## Metrics
- matrix rank/augmented rank and consistency for each public-shared factor-label model
- factor-label count, compression, multi-form label count, max forms per factor label
- single-form relief set for one-rank augmented inconsistencies
- local target prediction count
- toy-secret verified true/false prediction counts
- same-window and same-split prediction subpolicies
- fresh-validation prediction subpolicy

## Positive control
The per-form term model must be consistent. It gives every nonzero factor entry its own label while keeping the target variable public-shared.

## Negative control
The global-term model should reproduce the public-shared obstruction. If it is consistent, the experiment must be treated as a control failure rather than a positive factor-label result.

## Success criterion
Primary factor-label success requires a non-control model with:

- target labels shared by public fingerprint;
- full matrix consistency;
- at least one factor label spanning multiple forms;
- fewer factor labels than the per-form control; and
- no failed control gate.

Local target-prediction success is weaker and must be labeled diagnostic/scout unless repeated on a frozen validation block. It requires:

- at least one local object with two forms that have identical factor labels and different target coefficients;
- the derived scalar verifies against the toy source secret;
- zero false predictions under the named subpolicy.

## Falsification criterion
If no primary factor-label model passes and no named target-prediction subpolicy yields a verified zero-false signal, this branch remains a scoped negative. If only a local target-prediction signal appears, the next action is a frozen validation experiment for that policy, not a claim of faster-than-rho ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1033_p231_leaf8_factor_label_extraction_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout_probe.json
```

## Interpretation boundary
This is an index-calculus precursor and target-prediction scout. Positive toy target prediction is not an asymptotic algorithm, not sparse linear algebra closure, not target descent, and not a deployed faster-than-rho solver. A positive result must be frozen and validated on disjoint windows before promotion.

## Results
- timestamp: 2026-06-30T03:02:08Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout.py --contract ecdlp_index_calculus_state/experiment_contract_p1033_p231_leaf8_factor_label_extraction_scout.md --out ecdlp_index_calculus_state/low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout_probe.json`
- claim: `P1033_LEAF8_ROW_LOCAL_TARGET_PREDICTION_SIGNAL`
- primary public-shared factor-label merge models: `0`.
- leaf `[19]` reference:
  - `17` selected rows, `3` fresh positives, `0` fresh false rows, `26` unique forms.
  - global term labels rank/augmented `11/12`; public term `20/21`; row/salt term `23/24`; row-support term `23/24`; all inconsistent.
  - per-form term control passes at `26/26`.
- leaf `[8]` primary scope:
  - `12` selected rows, `3` fresh positives, `1` fresh false row, `16` unique forms.
  - global term labels rank/augmented `8/9`; public term `12/13`; row/salt term `15/16`; row-support term `15/16`; all inconsistent.
  - per-form term control passes at `16/16`.
  - row/salt/row-support obstruction is localized: removing any one of four `[11476,7416]` forms from the same exact-tail cluster makes the corresponding matrix consistent.
- local target-prediction signal:
  - row-vector and salt-terms-tail objects: `all_pairs` has `1` true and `3` false predictions; `same_window_both_fresh` has `1/1` true, `0` false.
  - exact-tail and motif objects: `all_pairs` has `6` true and `7` false predictions; `same_window`, `both_fresh`, and `same_window_both_fresh` each have `6/6` true, `0` false.
  - all six exact-tail/motif zero-false predictions are the same public `[11476,7416]` in window `12440_12447`, with terms `[8,8,11,11]`, tail support `[9,12]`, and predicted target scalar `6678`.
  - the six verified pairs use four forms with row salts `166`, `166`, `171`, and `174`, q/rhs pairs `(6982,9973)`, `(831,6968)`, `(8650,5943)`, and `(1363,2406)`.

## Interpretation
OBSERVATION / TOY-EVIDENCE / SCOUT: P1033 does not find a promotable factor-base merge under public-shared target variables, but it does find a row-local target-prediction mechanism inside leaf `[8]`. The unrestricted local-object catalog is noisy, so the useful signal is specifically the same-window fresh exact-tail/motif object, not all row-local pairs.

This is a viable index-calculus-development path: exact-tail/motif local objects can eliminate the local factor contribution and derive a target scalar in the toy harness. The next question is whether this is a repeatable public relation-generation rule or a one-window coincidence.

## Next concrete action
Create P1034 as a frozen validation of the same-window fresh exact-tail/motif target-prediction policy on disjoint later windows. The policy should be frozen as: leaf `[8]`, same public, same window, exact-tail or motif object with terms `[8,8,11,11]` and tail support `[9,12]`, at least two forms with distinct q-coefficients; derive the scalar by eliminating the shared local factor vector and verify against the public key/toy secret.
