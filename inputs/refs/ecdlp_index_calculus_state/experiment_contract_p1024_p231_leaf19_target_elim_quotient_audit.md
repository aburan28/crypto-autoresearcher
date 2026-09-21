# Experiment Contract: P1024 p231 leaf19 target-eliminated quotient audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1023 same-public local rank gains contain target-eliminated factor-only relations. After eliminating the target/secret coefficient inside each public context, fresh validation forms should add factor-bank rank outside the P1022 positive-calibration span.

## Null hypothesis
The P1023 local gains are only scalar-certificate geometry. Target elimination either emits no nontrivial factor rows, emits inconsistent rows, or emits rows whose coefficient span is already covered by the positive-calibration quotient bank.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- positive calibration windows: `12184_12191`, `12192_12199`, `12216_12223`, `12272_12279`, `12304_12311`, `12336_12343`, `12352_12359`, `12360_12367`
- negative controls: `12224_12231`, `12264_12271`, `12320_12327`
- fresh validation windows: `12376_12383`, `12384_12391`, `12392_12399`, `12400_12407`, `12408_12415`, `12416_12423`, `12424_12431`, `12432_12439`
- focus public groups from P1023: `[9131,7063]` and `[5178,1815]`
- quotient method: for forms with the same public fingerprint, use `q_right * left - q_left * right` to eliminate the first coefficient, interpreted as the target/secret coefficient, then canonicalize the remaining factor coefficients modulo order `11779`
- baseline: Pollard rho remains the selection-cost baseline; this audit measures only factor-relation rank after quotienting

## Metrics
- group operations: inherited cumulative selected `source_ops_over_rho`
- field operations: inherited from source artifacts
- memory: selected rows, unique forms, emitted quotient rows, unique quotient rows
- relation probability: inherited from P1022 selected positives
- rank: calibration quotient rank, combined quotient rank, validation-over-calibration quotient rank gain, augmented-rank consistency
- solver degree: not applicable
- wall-clock: script runtime

## Positive control
The audit must reproduce the P1022/P1023 selection shape: positive calibration selects `10`, validation selects `4`, negative controls select `0`, and reconstruction has zero errors.

## Negative control
Rows selected from `12224_12231`, `12264_12271`, or `12320_12327` invalidate the quotient bank because those windows encode known false-positive mechanisms.

## Success criterion
Primary success requires:

- zero negative-control selections;
- zero reconstruction errors;
- one common form order;
- at least one nontrivial target-eliminated factor relation;
- matrix consistency after target elimination; and
- positive combined quotient rank gain over the positive-calibration quotient bank.

Secondary success requires same-public focus-group quotient rank gain even if global factor-bank rank remains open.

## Falsification criterion
The hypothesis is narrowed or rejected if target elimination emits no nontrivial factor rows, emits inconsistent rows, or fresh validation/mixed pairs add no quotient rank outside the calibration quotient span.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1024_p231_leaf19_target_elim_quotient_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor only. A positive result would mean the P1022/P1023 relation surface contributes target-eliminated toy factor rows. It is not full sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:40:48 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1024_p231_leaf19_target_elim_quotient_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit_probe.json`
- claim: `P1024_SAME_PUBLIC_QUOTIENT_RANK_GAIN_GLOBAL_INCONSISTENT_PLATEAU`
- controls: positive calibration selected `10`, validation selected `4`, negative controls selected `0`.
- reconstruction: `14` selected rows reconstructed with `0` errors; all forms have order `11779`.
- quotient rows: target elimination emits `48` factor relations in the pooled same-public quotient bank over `16` factor columns.
- global quotient bank: calibration quotient rank `2/16`; combined quotient rank `2/16`; validation-over-calibration rank gain `0`; pooled augmented rank `3` against coefficient rank `2`, so the pooled global quotient bank is inconsistent.
- focus public `[9131,7063]`: calibration has one unique form and no calibration quotient row; validation/mixed pairs emit `3` target-eliminated factor relations, rank `2/16`, augmented rank `2`, matrix consistent, rank gain `2`.
- focus public `[5178,1815]`: calibration rank `1/16`; combined rank `2/16`; rank gain `1`, but augmented rank `3` against rank `2`, so this focus group is inconsistent after adding validation/mixed pairs.

## Interpretation
OBSERVATION: target elimination turns the clean P1022/P1023 scalar surface into explicit factor-only rows. The strongest positive is local and context-scoped: public `[9131,7063]` has a consistent same-public quotient rank gain from validation/mixed pairs.

NEGATIVE RESULT under the primary P1024 criterion: when quotient rows are pooled across same-public contexts, validation adds no global rank beyond the calibration quotient span (`2/16` stays `2/16`), and the augmented system is inconsistent. This prevents promoting the current raw leaf-19 quotient bank to a reusable global factor-base matrix.

The result narrows the path: the index-calculus opportunity is now context-local quotient rank, not a global factor bank from this raw representation. The next move should preserve the consistent `[9131,7063]` quotient class and search for another independent, consistent same-public quotient class rather than pooling inconsistent contexts blindly.

## Next concrete action
Create P1025 as a consistency-filtered quotient scheduler: keep same-public quotient classes only when augmented rank equals coefficient rank, seed it with `[9131,7063]`, reject inconsistent groups such as `[5178,1815]`, and validate on fresh leaf-19 or neighboring motif windows for a second independent consistent quotient direction.
