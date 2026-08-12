# Experiment Contract: P1028 p231 relation-class split audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1027 failure may come from pooling incompatible quotient relation classes. Splitting rows by canonical coefficient family, support size, support tuple, q-coefficient pattern, and salt signature may reveal a consistent factor-rank class with held-out public prediction.

## Null hypothesis
Every relation class with enough rows is either inconsistent, singleton/nonpredictive, or dependent without held-out public prediction. Then the current leaf-19 quotient family should be closed as context-local under this representation and the next positive search should move to a neighboring motif or representation.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- quotient source: P1026/P1027 scope with seed public `[9131,7063]` and fresh publics `[8914,3039]`, `[9299,3922]`
- training windows: P1022 positive calibration plus P1022 validation through `12432_12439`
- fresh windows: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the first coefficient as `q_right * left - q_left * right`
- modulus/order: `11779`
- class partitions:
  - exact canonical coefficient vector
  - factor support tuple
  - factor support size
  - coefficient family
  - exact q-coefficient pair
  - q-coefficient order pattern
  - salt-pair signature
  - row-key signature

## Metrics
- class size and distinct public count
- coefficient rank and augmented rank
- matrix consistency
- held-out public rowspace checks
- promoted class count
- diagnostic consistent class count

## Positive control
The audit must reproduce P1027's factor-only inconsistency over the full quotient pool: coefficient rank `2`, augmented rank `3`.

## Negative control
Classes that are exact singletons or have no held-out public test are not promotable.

## Success criterion
Primary success requires at least one class with:

- at least two distinct publics;
- matrix consistency;
- positive coefficient rank;
- at least one testable held-out public row; and
- every testable held-out public row passes rowspace prediction.

## Falsification criterion
If no class satisfies the success criterion, and any consistent classes are single-public or held-out-untestable diagnostics only, this is a scoped negative for the current leaf-19 quotient representation.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1028_p231_relation_class_split_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1028_p231_relation_class_split_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1028_p231_relation_class_split_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor. A promoted class would be a toy relation-class signal, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 19:07:18 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1028_p231_relation_class_split_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1028_p231_relation_class_split_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1028_p231_relation_class_split_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1028_p231_relation_class_split_audit_probe.json`
- claim: `NEGATIVE_RESULT_P1028_NO_CONSISTENT_RELATION_CLASS`
- controls: training selected `14`, fresh selected `3`, negative controls selected `0`, reconstruction errors `0`, seed quotient rank `2`.
- full factor-only pool: `10` relations, coefficient rank `2`, augmented rank `3`, inconsistent.
- class audit: `13` non-singleton classes tested; `0` promotable classes; `0` diagnostic consistent classes; `13` inconsistent classes.
- key failures: `unit_target_adjacent_tail` has `7` rows over `2` publics, rank/augmented `2/3`, held-out `0/5`; `zero_target_tail_1_1` has `3` rows over `3` publics, rank/augmented `1/2`, held-out `0/1`; support tuple `[0,1,2]` has `6` rows, rank/augmented `2/3`; support tuple `[1,2]` has `3` rows, rank/augmented `1/2`; salt-pair `[172,172]` has `6` rows, rank/augmented `2/3`.

## Interpretation
NEGATIVE RESULT under the P1028 class-split model: the leaf-19 quotient inconsistency is not caused by mixing incompatible relation classes. Every tested non-singleton class remains inconsistent, including canonical coefficient family, support tuple, support size, q-order pattern, row-key signature, and salt-pair signature.

This closes the current raw leaf-19 quotient pooling branch as a reusable factor-bank route under the tested representation. The clean scalar scheduler and local quotient signals remain useful as diagnostic structure, but they do not yet produce a globally consistent relation matrix.

## Next concrete action
Move to a neighboring motif/representation rather than adding more bookkeeping to leaf-19 quotient rows. Create P1029 as a motif-neighbor scout over fresh selected forms: compare leaf-19 against nearby leaf tuples or non-leaf-19 companion motifs, and require the first experiment to reproduce the clean scheduler precision while avoiding the rank/augmented inconsistency seen here.
