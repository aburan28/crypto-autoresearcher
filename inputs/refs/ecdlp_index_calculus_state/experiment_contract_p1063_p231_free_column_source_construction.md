# Experiment Contract: P1063 P231 Free-Column Source Construction

## Hypothesis
The extra rank direction present in the broad P1054 source branch can be recovered by a public source-construction rule that targets remaining free columns after the P1059 anchor, without using salt/row-key threshold replay. A useful index-calculus route should be able to predict or construct relation rows that remove at least one of `[6,7,10,14,15]` at materially lower cost than the full broad P1054 collector.

## Null hypothesis
The extra P1054 rank direction is not exposed by the tested non-salt public row features. If it appears only when most broad P1054 rows are charged, then the current source family has a diffuse high-cost rank direction rather than a public low-cost construction rule.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- broad source gate: P1054 `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`
- anchor control: exact P1059 row-key prefix on forward window `18464_18471`
- public feature catalog: non-salt row/source-construction features `case_count`, `priority_count`, `transfer_span`, `min_ops`, `mean_ops`, `max_ops`, and `op_range`
- excluded features: salt values, salt spans, unique-salt counts, exact row keys, transfer labels as equality keys, and verifier labels

## Metrics
- group operations: marginal strict source charge from `direct_ops_over_rho`
- rank: marginal target-eliminated rank gain over the exact P1059 anchor
- free-column pressure: columns removed from `[6,7,10,14,15]`
- public transfer: calibration-selected non-salt row rule evaluated on forward windows
- oracle boundary: best forward-selected non-salt row rule, reported only as diagnostic
- broad baseline: full P1054 forward collector marginal charge and rank after the P1059 anchor

## Positive control
The exact P1059 anchor must reproduce the below-rho packet on `18464_18471`: charge `0.83211679` rho, rank gain `2`, free columns `[6,7,10,14,15]`.

## Negative control
P1062 found no rank-diverse family in the P1061 salt/priority catalog, including no forward single-family oracle candidate.

## Success criterion
P1063 is a strict positive only if a calibration-selected non-salt public row/source-construction rule adds forward rank over the P1059 anchor with marginal charge below one rho. A weaker positive is a calibration-selected rule that adds rank at lower marginal charge than the full broad P1054 collector.

## Falsification criterion
P1063 is negative for the tested feature catalog if no calibration-selected non-salt rule adds calibration rank over the anchor. It is an oracle-only diagnostic if a forward-selected non-salt rule adds rank but calibration cannot predict it.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1063_p231_free_column_source_construction.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1063_p231_free_column_source_construction.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1063_p231_free_column_source_construction_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `NO-SALT-REPLAY`: this audit intentionally excludes salt and exact row-key thresholds.
- `ORACLE-DIAGNOSTIC`: any forward-selected rule is not a public selector.
- `POLLARD-RHO-BOUNDARY`: a lower-cost rank direction is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: free-column pressure is not individual-log descent unless remaining dependencies are resolved.

## Next concrete action
Run P1063, then either promote a non-salt free-column predictor or record that the current broad-source extra rank is diffuse and move to an algebraic row-construction change.

## Results
- Status: `POSITIVE_SIGNAL_P1063_FORWARD_SOURCE_FEATURE_ORACLE_ONLY`.
- Exact P1059 anchor control: charge `0.83211679` rho, rank gain `2`, free columns `[6,7,10,14,15]`.
- Broad P1054 forward baseline: marginal rank gain `1`, marginal charge `128.62773767` rho, removed free column `[10]`.
- Calibration public non-salt selector: selected expression `None`; train positive count `0` across `3081` non-salt source-construction rules.
- Forward oracle non-salt selector: best expression `mean_ops >= 0.78345499`.
- Forward oracle effect: marginal rank gain `1`, marginal charge `2.35036497` rho, charge per marginal rank gain `2.35036497`, removed free column `[10]`, union free columns `[6,7,14,15]`.
- Forward oracle selected windows: `18016_18023` plus P1059 anchor `18464_18471`.
- Forward oracle selected cases: `4`, usable source certificates `2`, source support columns `[0,1,5,10,11,14,15]`.

## Interpretation
P1063 is a positive precursor, but not a public selector. It shows that the P1054 broad branch's extra rank direction is not purely diffuse: a simple non-salt source-construction feature can isolate the column-`10` rank direction at `2.35036497` rho marginal charge instead of the full broad-collector marginal charge `128.62773767` rho. The limitation is selection leakage: the rule was found using forward labels, while calibration exposes no rank-positive non-salt rule.

This is useful because it moves the next experiment away from salt/row-key replay and toward a measurable source-construction predictor. The next question is whether `mean_ops >= 0.78345499`, or a chronology-safe variant of it, predicts column-`10` removal on windows not used to choose the rule.

## Failure modes and boundaries
- `ORACLE-DIAGNOSTIC`: the selected rule used forward data and cannot be promoted as public.
- `NOT RHO WIN`: marginal charge `2.35036497` rho is lower than full P1054 but still above one rho.
- `MODEL-BOUND`: rank/free-column movement is measured only in the current order-`11779` target-eliminated factor namespace.
- `TARGET-DESCENT-BOUNDARY`: removing column `10` is rank pressure, not an individual-log descent.
- `NEXT POSITIVE QUESTION`: build P1064 as a chronological validation of the non-salt high-mean-ops source-construction rule, using earlier windows to freeze the rule and later windows to test column-`10` rank removal.
