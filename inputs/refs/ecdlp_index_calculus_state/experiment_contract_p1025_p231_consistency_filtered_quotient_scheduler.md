# Experiment Contract: P1025 p231 consistency-filtered quotient scheduler

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1024 clean same-public quotient class `[9131,7063]` can be used as a consistency-filtered seed. Applying the frozen P1022 leaf-19 scheduler to later fresh windows should either find a second independent quotient direction that remains matrix-consistent with the seed, or sharply rule out this fresh block for the current representation.

## Null hypothesis
Fresh windows after `12439` either select no usable rows, select only false-positive/noisy rows, emit no target-eliminated factor rows, emit inconsistent quotient rows, or emit rows whose coefficient span is already contained in the `[9131,7063]` seed quotient bank.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- seed/training windows: P1022 positive calibration plus P1022 fresh validation through `12432_12439`
- negative controls: `12224_12231`, `12264_12271`, `12320_12327`
- fresh validation windows: `12440_12447`, `12448_12455`, `12456_12463`, `12464_12471`, `12472_12479`, `12480_12487`, `12488_12495`, `12496_12503`
- seed quotient public: `[9131,7063]`
- quotient method: same-public form pairs eliminate the first coefficient as `q_right * left - q_left * right`, then canonicalize factor coefficients modulo order `11779`
- baseline: Pollard rho remains the scalar-search baseline; this audit measures quotient relation-bank rank and consistency only

## Metrics
- group operations: selected `source_ops_over_rho`
- field operations: inherited from source artifacts
- memory: selected rows, reconstructed forms, quotient rows, unique quotient rows
- relation probability: selected positives/false positives in the fresh block
- rank: seed quotient rank, candidate quotient rank, seed-plus-candidate rank gain, augmented-rank consistency
- solver degree: not applicable
- wall-clock: script runtime

## Positive control
The seed `[9131,7063]` quotient class must reproduce P1024: rank `2`, augmented rank `2`, matrix consistent.

## Negative control
The known false-positive calibration windows must select `0` rows under the frozen P1022 rule.

## Success criterion
Primary success requires a fresh or mixed training/fresh same-public quotient group with:

- at least one fresh selected row;
- zero reconstruction errors and one common order;
- internally consistent quotient rows;
- seed-plus-candidate augmented rank equal to coefficient rank; and
- positive rank gain over the `[9131,7063]` seed quotient bank.

## Falsification criterion
The current fresh block is narrowed or rejected if it has no selected rows, no reconstructed forms, no quotient rows involving fresh forms, inconsistent quotient rows, selected false-positive noise that prevents promotion, or no rank gain beyond the seed quotient bank.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1025_p231_consistency_filtered_quotient_scheduler.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler_probe.json
```

## Interpretation boundary
This is an index-calculus precursor. A positive result would be a second consistent toy quotient direction, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:47:20 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler.py --contract ecdlp_index_calculus_state/experiment_contract_p1025_p231_consistency_filtered_quotient_scheduler.md --out ecdlp_index_calculus_state/low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler_probe.json`
- claim: `P1025_LOCAL_CONSISTENT_FRESH_QUOTIENT_GLOBAL_RANK_PLATEAU`
- controls: training selected `14`, fresh selected `3`, negative controls selected `0`, reconstruction errors `0`.
- fresh precision: `3/3` fresh selected rows are label-positive, with selected cost `2.13138687x` rho. Fresh hits are `12480:12480` (`salt165+salt172`, `0.72992701x` rho), `12480:12483` (`salt166+salt172`, `0.70072993x` rho), and `12500` (`salt162+salt171`, `0.70072993x` rho).
- seed reproduction: public `[9131,7063]` reproduces the P1024 seed bank, with `3` target-eliminated factor relations, rank `2/16`, augmented rank `2`, and matrix consistency.
- fresh quotient candidates: `2` same-public candidates involve fresh forms; `1` is internally consistent, and `0` promote over the seed bank.
- candidate `[8914,3039]`: internally consistent fresh quotient row, rank `1/16`, but seed-plus-candidate rank remains `2/16` and augmented rank becomes `3`, so it is inconsistent with the seed bank and gives rank gain `0`.
- candidate `[9299,3922]`: emits `6` fresh quotient rows, rank `2/16`, but augmented rank `3`; it is internally inconsistent and gives seed-over-candidate rank gain `0`.

## Interpretation
OBSERVATION: the P1022/P1025 frozen public scheduler remains clean on the later `12440_12503` fresh block: three selected rows, all label-positive, zero selected false positives.

NEGATIVE RESULT under the P1025 promotion criterion: no fresh quotient group adds a second independent consistent quotient direction over the `[9131,7063]` seed. The fresh quotient rows remain in the same low-dimensional coefficient span, and pooling them with the seed produces RHS inconsistency.

The useful obstruction is now precise: the same quotient coefficient pattern `[0,1,1,...]` recurs with different RHS values across publics. This suggests the next model should test whether the leaf-19 quotient rows have a public-dependent affine RHS offset; if so, the current raw quotient representation is not yet a global factor-base namespace.

## Next concrete action
Create P1026 as an affine-RHS obstruction audit. For each same-public quotient group, cluster canonical coefficient vectors and measure whether RHS differences are explained by a public fingerprint, row-key signature, or salt-pair invariant. Success would be a public computable normalization that makes `[9131,7063]`, `[8914,3039]`, and `[9299,3922]` mutually consistent; failure would be a scoped negative for global quotient reuse without a new representation.
