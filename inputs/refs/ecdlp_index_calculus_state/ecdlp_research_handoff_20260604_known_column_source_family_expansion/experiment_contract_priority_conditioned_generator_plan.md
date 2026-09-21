# Experiment Contract: priority-conditioned generator plan

## Hypothesis
The current residual-class obstruction can be converted into concrete generator work items by joining support-to-form scheduling with q/pair option scouting.

## Null hypothesis
The joined artifacts only restate passive volume failures and do not identify exact transfers, row keys, q ratios, or partner-support gaps for the next generator.

## Parameters
- field/curve family: toy prime-field ECDLP target `22050.cf1@11731`
- sizes: direct-certificate frontier through `10535`
- seeds: inherited from public source artifacts
- factor base: order-`11779` low-term namespace
- relation shape: target-eliminated pairs from public direct relation-equation certificates
- baseline: Pollard-rho comparison remains the global benchmark; this experiment is a generator work-order planner, not a speedup claim

## Metrics
- q-pair lane count
- force-export lane count
- exported priority columns
- q-ratio diversity
- partner-support diversity
- charged residual promotion gate

## Positive control
Known exported-priority collapses at transfers `10478` and `10528` should appear as q/pair lane work items.

## Negative control
Support-loss groups with no exported priority columns should remain in the force-export lane and must not be promoted.

## Success criterion
Emit a durable JSON plan with exact transfer indices, row keys, q ratios, partner-support gaps, desired priority columns, and a nonzero-residual success gate.

## Falsification criterion
If no q-pair or force-export lane items are emitted, or if the plan promotes rows without a charged residual hit, this planner is invalid.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_priority_conditioned_generator_plan.py \
  --scheduler-artifacts ecdlp_index_calculus_state/low_term_total2_priority_conditioned_form_export_scheduler_10464_10535_col6_col15_probe.json \
  --pair-option-artifacts ecdlp_index_calculus_state/low_term_total2_priority_export_pair_option_scout_post10503_10504_10535_col6_col15_probe.json,ecdlp_index_calculus_state/low_term_total2_priority_export_pair_option_scout_current10535_exported_priority_10336_10535_col6_col15_probe.json \
  --target-columns 6,15 \
  --limit 16 \
  --out ecdlp_index_calculus_state/low_term_total2_priority_conditioned_generator_plan_10464_10535_col6_col15_probe.json
```

## Results
`low_term_total2_priority_conditioned_generator_plan_10464_10535_col6_col15_probe.json` reports `2` q-pair lane items, `38` concrete force-export lane items, and status `PRIORITY_CONDITIONED_Q_PAIR_GENERATOR_PLAN_READY`.

## Interpretation
TOY-EVIDENCE / MODEL-BOUND / HEURISTIC. The plan is a generator handoff, not target descent. Rows remain unpromotable until the charged residual scout reports nonzero target-column residual support.
