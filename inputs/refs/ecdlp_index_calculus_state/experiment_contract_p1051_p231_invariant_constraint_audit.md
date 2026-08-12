# Experiment Contract: P1051 p231 invariant-constraint audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND: the P1044/P1050 y-residue relation stream may contain a low-degree algebraic identity over public coordinates and public row coefficients that survives held-out rows and is absent from matched random controls. Such an identity would be an index-calculus precursor because it would constrain relation generation rather than merely increasing rowspace capacity.

## Null hypothesis
No overdetermined low-degree public identity validates on held-out rows, or every validating identity is reproduced by matched public-coordinate or row-coefficient null controls.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- modulus/order: `11779`
- train rows: P1045 persisted primary strict true witness forms from P1038/P1041/P1042
- validation source: full P1044-scope rematerialized compressed row pools, excluding train form identities
- start window: `12504_12511`
- rematerialization windows: `64`
- required factor signature: `[(8,11777),(11,11777)]`
- required residual class: `5459`
- baseline: Pollard rho remains the one-target scalar-search baseline; P1051 is not a complete solver or target-descent claim
- identity variables: public `x`, `y`, row `q_coeff`, row `rhs`, plus derived public features such as `y/x`, `y/(x+1)`, `x+1/x`, `x+y`, `x*y`, and `x^2-4y`
- promotable templates: affine public/source, quadratic public/source, bilinear public/source, rational public/source, trace/norm public/source, and small-residue public/source
- diagnostic-only controls: source-only identities and residual-constant sanity identities
- null controls: shuffled public coordinates, matched-random public coordinates, full-field random public coordinates, shuffled row `(q,rhs)`, and full-random row `(q,rhs)`

## Metrics
- train row count;
- validation row count;
- monomial count;
- train rank and train nullity;
- combined rank and combined nullity;
- overdetermined predicate;
- held-out-surviving nullity;
- matched-random public reproduction count;
- full-random public reproduction count;
- shuffled-public reproduction count;
- shuffled-row-source reproduction count;
- full-random-row-source reproduction count;
- exact artifact and source hashes.

## Positive control
The diagnostic `residual_constant_sanity` template must recover the trivial residual identity on train plus held-out rows. This uses scalar-derived residuals and is therefore excluded from promotion.

## Negative controls
Matched public-coordinate controls, shuffled public-coordinate controls, full-field public-coordinate controls, shuffled row `(q,rhs)` controls, and full-random row `(q,rhs)` controls must not reproduce a promotable identity profile. Any reproduction blocks promotion.

## Success criterion
Strict validation requires at least one promotable low-degree template with:
- train rows greater than monomial count;
- combined rows greater than monomial count;
- nonzero train nullity;
- nonzero combined nullity after adding held-out rows;
- zero broad compressed false predictions;
- no null control with a candidate-like identity of at least the observed combined nullity.

## Falsification criterion
P1051 is negative for this template catalog if no promotable overdetermined identity survives held-out validation, or if every surviving public identity is reproduced by at least one matched null family. This is a scoped negative for the tested low-degree templates over the P1044 y-residue stream, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1051_p231_invariant_constraint_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1051_p231_invariant_constraint_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1051_p231_invariant_constraint_audit_probe.json
```

## Interpretation boundary
This is a low-degree identity audit over a toy p231 artifact stream. A pass would be an index-calculus precursor only; it would still require relation collection, sparse linear algebra, individual-log/target descent, scaling tests, and a charged comparison to Pollard rho.

## Sub-agent handoff: Red-team interpretation

### Claim or task
Try to falsify any P1051 identity by reproducing it with matched random public coordinates or row-coefficient controls.

### Status
HYPOTHESIS

### Assumptions
- The train/validation split from P1047 is the correct immediate held-out surface.
- Public-coordinate identities must survive without using source secrets.
- Residual-derived identities are sanity checks only.

### Evidence so far
- P1050 showed nonlinear feature-channel rank lifts are reproduced by matched random two-feature controls.

### Failure modes
- Low row count can produce interpolation artifacts.
- Identities over `q,rhs` alone may reflect source generation, not EC public structure.
- Residual identities may use scalar-derived information and cannot be promoted.

### Next concrete action
Run the P1051 probe and require matched-null separation before promoting any identity.

### Artifact paths
- `tasks/ecdlp_index_calculus/low_term_total2_p1051_p231_invariant_constraint_audit.py`
- `ecdlp_index_calculus_state/low_term_total2_p1051_p231_invariant_constraint_audit_probe.json`

## Results
Timestamp: `2026-06-30T05:57:28Z` in the probe artifact.

Claim: `NEGATIVE_RESULT_P1051_NO_OVERDETERMINED_PUBLIC_IDENTITIES`

- Full P1044-scope rematerialization: `64/64` forward windows exist.
- Rematerialized compressed predictions: `7` total, `7` true, `0` false.
- Base-signature rows: `14` broad rows total, `4` broad-only validation rows after excluding P1045 strict train forms.
- Train rows: `10`.
- Tested templates: `8` total, `6` promotable and `2` diagnostic-only.
- Strict validation passes: `0`.
- Promotable candidate identities: `0/6`.
- Residual sanity control: passed, with identity `residual + 6320 = 0 mod 11779`, equivalent to residual `5459`.
- Source-only quadratic diagnostic: no train nullity.
- Affine public/source, rational public/source, trace/norm/discriminant public/source, and small-residue public/source templates all have train nullity `0`.
- Public-source bilinear has train nullity `1`, but held-out rows raise combined rank to full rank, so combined nullity is `0`.
- Public-quadratic/source-affine has train nullity `1`, but held-out rows raise combined rank to full rank, so combined nullity is `0`.

## Interpretation
NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND: P1051 moves from P1046-P1050 feature/rank-capacity tests to explicit low-degree invariant identities. The tested public-coordinate and row-coefficient templates do not produce an overdetermined identity that survives held-out validation. The useful obstruction is that the only train-nullity public templates are interpolation artifacts killed by the broad-only validation rows.

This does not close the index-calculus route. It narrows the next requirement: search for a representation that creates relation constraints through the actual source-generation mechanism, such as Semaev/slice quotient identities, target-descent-compatible factor variables, or a constructive source family that forces new factor-column motifs.

## Next concrete action
Build P1052 as a relation-generator constraint audit: connect the current y-residue row stream to source-generation mechanics by testing whether Semaev/slice quotient, selected-leaf polynomial coefficients, or known-column factor motifs predict the factor signature before scalar-derived verification. Require fresh held-out windows, source-charged accounting, and Pollard-rho comparison.
