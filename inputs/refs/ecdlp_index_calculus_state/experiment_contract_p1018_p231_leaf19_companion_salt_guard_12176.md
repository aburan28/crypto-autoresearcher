# Experiment Contract: P1018 p231 leaf19 companion salt guard

## Hypothesis
HYPOTHESIS: the scalar-closing companion row in the top-k4 line is the public cost-hybrid leaf-19 sibling with bounded row-key salts, and the frozen guard transfers to later unseen windows.

## Null hypothesis
The leaf-19/salt-bounded sibling is a post-hoc artifact: on later windows it either selects no rows, selects false positives, or fails to produce context-safe scalar-valid groups below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- diagnostic controls: `12104_12111`, `12168_12175`
- validation windows: `12176_12183`, `12184_12191`, `12192_12199`, `12200_12207`, `12208_12215`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- precision companion rule: exact anchor row-key set, `leaf_selector == mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, unique leaf tuple `[19]`, and `max(salt_values) <= 168`
- baseline: Pollard rho charged as `1.0` ops-over-rho
- frozen order: `salt_gap_asc_ops`

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The precision companion rule must reproduce below-rho context-safe scalar hits on `12104_12111` and `12168_12175`.

## Negative control
The unbounded leaf-19 companion rule is reported on the same validation windows to show whether the salt bound reduces noise.

## Success criterion
Validation success requires at least one later unseen validation window to have a selected public-key-verified below-rho row and a context-safe scalar-valid group charged below `1.0` rho under the frozen order.

## Falsification criterion
The hypothesis is narrowed or rejected if validation windows select no rows, no public-key-verified below-rho rows, no context-safe scalar-valid groups, or first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1018_p231_leaf19_companion_salt_guard_12176.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1018_p231_leaf19_companion_salt_guard_12176.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1018_p231_leaf19_companion_salt_guard_12176_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for precision companion-row scheduling. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results

Command completed with:

```text
claim=NEGATIVE_RESULT_P1018_VALIDATION_SELECTS_NO_ROWS control_pass=True selected=0 positives=0 precision=None groups=0 success=none false_positive_windows=none out=ecdlp_index_calculus_state/low_term_total2_p1018_p231_leaf19_companion_salt_guard_12176_probe.json
```

Key measurements:

- guarded controls passed:
  - `12104_12111`: selected `1`, positive `1`, scalar-valid groups `3`, first hit `0.70072993` rho.
  - `12168_12175`: selected `1`, positive `1`, scalar-valid groups `3`, first hit `0.73722628` rho.
- guarded validation `12176_12215`: selected `0`; the `max_salt <= 168` guard was too restrictive.
- unbounded leaf-19 companion control on the same validation batch selected `4`, positives `2`, precision `0.5`, scalar-valid groups `6`, with below-rho success windows `12184_12191` and `12192_12199`.
- unbounded false-positive windows: `12176_12183` and `12200_12207`.

## Interpretation

Status: `NEGATIVE RESULT` for the salt-bounded guard, with a positive unbounded sibling-family signal.

The useful family is not the low max-salt subset. The broader public rule, exact anchor row-key set plus cost-hybrid leaf-19 top-k4, produced two below-rho context-safe hits on later validation windows. The next concrete action is to freeze that unbounded leaf-19 companion rule and validate it on a fresh later batch, with false-positive rate reported rather than hidden.
