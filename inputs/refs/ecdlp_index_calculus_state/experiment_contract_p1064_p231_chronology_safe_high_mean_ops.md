# Experiment Contract: P1064 P231 Chronology-Safe High-Mean-Ops Validation

## Hypothesis
The P1063 high-mean-ops source-construction signal can be converted from a forward oracle into a chronology-safe predictor for the remaining free column `10`. The exact P1063 rule should transfer to later windows, or an anchor-derived relaxed high-mean band should remove column `10` at materially lower cost than the broad P1054 collector.

## Null hypothesis
The exact P1063 rule only describes the discovery window `18016_18023`, and relaxed high-mean bands either select no later useful rows or require broad above-rho spend comparable to the full P1054 collector.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- broad source gate: P1054 `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`
- anchor control: exact P1059 row-key prefix on forward window `18464_18471`
- discovery rule: P1063 forward-oracle expression `mean_ops >= 0.78345499`
- discovery window: `18016_18023`
- validation windows: P1054 forward windows with start greater than `18023`; the exact P1059 anchor is used as the base packet, while selector-selected non-anchor cases in the same window are still charged
- relaxed rule: `mean_ops >= <P1059 anchor mean_ops>`, excluding salt and exact row-key thresholds

## Metrics
- group operations: marginal strict source charge from `direct_ops_over_rho`
- rank: marginal target-eliminated rank gain over the exact P1059 anchor
- free-column pressure: whether column `10` is removed from `[6,7,10,14,15]`
- exact transfer: P1063 exact threshold on validation windows
- relaxed transfer: anchor-derived high-mean threshold on validation windows
- broad validation baseline: all P1054 validation rows after the discovery cutoff

## Positive control
The exact P1059 anchor must reproduce the below-rho packet on `18464_18471`: charge `0.83211679` rho, rank gain `2`, free columns `[6,7,10,14,15]`.

## Negative control
The exact P1063 threshold should be reported separately; if it selects only the anchor and no post-discovery rows, that is a precision/coverage failure for the oracle threshold.

## Success criterion
P1064 is a strict positive only if the exact P1063 threshold removes column `10` on post-discovery validation rows with marginal charge below one rho. It is a weak positive if the anchor-derived relaxed threshold removes column `10` at lower charge than the broad post-discovery P1054 baseline.

## Falsification criterion
P1064 is negative if neither the exact nor relaxed high-mean rule removes column `10`, or if the relaxed rule costs at least as much as the broad validation baseline.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1064_p231_chronology_safe_high_mean_ops.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1064_p231_chronology_safe_high_mean_ops.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1064_p231_chronology_safe_high_mean_ops_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `NO-SALT-REPLAY`: this audit excludes salt and exact row-key thresholds for new selection.
- `DISCOVERY-DERIVED`: the exact P1063 threshold came from a prior forward oracle and is not a fresh public discovery.
- `ANCHOR-DERIVED`: the relaxed threshold uses the already-known P1059 anchor's public mean-ops value.
- `POLLARD-RHO-BOUNDARY`: cost-reduced column removal is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: removing column `10` is rank pressure, not individual-log descent.

## Results
- timestamp: `2026-06-30T07:47:51Z`
- claim: `POSITIVE_SIGNAL_P1064_RELAXED_HIGH_MEAN_COLUMN10_COST_REDUCED_NOT_RHO`
- record counts: `50` forward windows, `17` validation windows after cutoff `18023`, `1` anchor window.
- positive control: the exact P1059 anchor reproduced charge `0.83211679` rho, rank gain `2`, and free columns `[6,7,10,14,15]`.
- exact transfer: `mean_ops >= 0.78345499` selected only the anchor window `18464_18471`; marginal charge `0.0`, marginal rank gain `0`, removed free columns `[]`.
- relaxed transfer: `mean_ops >= 0.75912409` selected windows `[18464_18471,18768_18775,20456_20463]`, `10` cases, strict source charge `7.62773725` rho, marginal charge over the anchor `6.79562046` rho, marginal rank gain `1`, removed free column `[10]`, and left free columns `[6,7,14,15]`.
- broad validation baseline: all `17` validation windows selected `56` cases, strict source charge `41.5474454` rho, marginal charge over the anchor `40.71532861` rho, marginal rank gain `1`, and removed free column `[10]`.
- interpretation: the exact P1063 oracle threshold does not transfer as a public holdout predictor. The anchor-mean relaxation is chronology-safe and cost-reduces column-`10` rank pressure by about `5.9914x` versus the broad validation collector, but it remains above one rho and does not implement target descent or sparse linear-algebra closure.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1064_p231_chronology_safe_high_mean_ops_probe.json`

## Next concrete action
Build P1065 as a cost-compression/descent integration step for the relaxed high-mean column-`10` predictor: isolate which selected later row or certificate carries the new direction, test early-stop ordering within selected cases, and measure whether shared-source or target-descent accounting can reduce the marginal `6.79562046` rho cost.
