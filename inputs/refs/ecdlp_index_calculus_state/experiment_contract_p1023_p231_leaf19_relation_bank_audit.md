# Experiment Contract: P1023 p231 leaf19 relation-bank audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1022 rank-aware leaf-19 scheduler is not only producing isolated scalar certificates. Its selected reconstructed forms contribute reusable relation-bank rows, visible as coefficient-rank growth from positive calibration to fresh validation without violating context-safe public grouping.

## Null hypothesis
The P1022 selected forms reconstruct, but validation contributes no new relation-bank rank beyond calibration, or any apparent rank gain only appears after mixing unrelated public contexts.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- positive calibration windows: `12184_12191`, `12192_12199`, `12216_12223`, `12272_12279`, `12304_12311`, `12336_12343`, `12352_12359`, `12360_12367`
- negative control windows: `12224_12231`, `12264_12271`, `12320_12327`
- fresh validation windows: `12376_12383`, `12384_12391`, `12392_12399`, `12400_12407`, `12408_12415`, `12416_12423`, `12424_12431`, `12432_12439`
- baseline: Pollard rho charged as `1.0` ops-over-rho for selection cost; relation-bank utility is measured separately by rank
- frozen order: P1020 `salt_gap_asc_ops`

## Metrics
- group operations: cumulative selected `source_ops_over_rho`
- field operations: inherited from source artifacts
- memory: selected rows, reconstructed forms, unique form rows, coefficient columns
- relation probability: inherited selected positives from P1022 controls
- rank: raw coefficient rank, augmented rank consistency, validation rank gain over calibration, same-public rank gain
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The audit must reproduce the P1022 selected-row shape: positive calibration selects `10` rows, fresh validation selects `4` rows, and the negative controls select `0` rows.

## Negative control
Any selected row in `12224_12231`, `12264_12271`, or `12320_12327` invalidates the audit because the relation bank would include the false-positive-only P1021 failure mode.

## Success criterion
Primary success requires:

- zero negative-control selections;
- zero reconstruction errors;
- one common order for all reconstructed forms;
- fresh validation contributes positive coefficient-rank gain over the calibration bank; and
- at least one same-public group spanning calibration and validation gains rank after validation forms are added.

A weaker positive is allowed if validation adds raw global rank but no same-public cross-split rank gain; that is a relation-bank signal with context glue still open.

## Falsification criterion
The hypothesis is narrowed or rejected if reconstruction fails, orders disagree, negative controls select rows, validation adds no novel form rows, validation adds no coefficient rank, or rank gain only exists in an invalid public-context merge.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1023_p231_leaf19_relation_bank_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1023_p231_leaf19_relation_bank_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1023_p231_leaf19_relation_bank_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor only. A positive result means the P1022 public selector feeds reusable toy relation-bank rows under the stated model. It is not sparse linear algebra closure, target descent, cryptographic-size evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:32:55 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1023_p231_leaf19_relation_bank_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1023_p231_leaf19_relation_bank_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1023_p231_leaf19_relation_bank_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1023_p231_leaf19_relation_bank_audit_probe.json`
- claim: `P1023_CONTEXT_LOCAL_RANK_GAIN_GLOBAL_BANK_PLATEAU`
- controls: positive calibration selected `10`, fresh validation selected `4`, negative controls selected `0`.
- reconstruction: `14` selected rows reconstructed with `0` reconstruction errors; forms have one order, `11779`.
- relation rows: `30` reconstructed forms, `28` unique form rows, `9` validation-unique form rows.
- raw rank: calibration coefficient rank `3/17`; validation coefficient rank `3/17`; global coefficient rank `3/17`; validation-over-calibration global rank gain `0`.
- augmented consistency: calibration/global augmented rank is `4` while coefficient rank is `3`, so the raw mixed-context augmented system is not a directly consistent factor-base matrix.
- same-public local gain: public `[9131,7063]` grows from rank `1` to `3`; public `[5178,1815]` grows from rank `2` to `3`.

## Interpretation
OBSERVATION: P1022 validation forms are not mere duplicates: they add `9` novel form rows and create local same-public rank growth in two contexts.

NEGATIVE RESULT under the primary P1023 criterion: the global coefficient span was already rank `3` after calibration, so fresh validation adds no global relation-bank rank. This points to a low-dimensional leaf-19 motif plateau rather than a growing full factor-base matrix.

The useful next question is not whether the scalar closures are real; P1022 already validated that. The next question is whether quotienting or target-eliminating the same-public forms exposes independent factor rows hidden behind the rank-3 motif.

## Next concrete action
Create P1024 as a target-eliminated/quotient relation-bank audit over the P1023 same-public groups, especially `[9131,7063]` and `[5178,1815]`. Success should require canonical target-eliminated rows with positive rank outside the current 3-dimensional motif span, or else a scoped negative result proving this leaf-19 family is a scalar-certificate surface without reusable factor-rank growth under this representation.
