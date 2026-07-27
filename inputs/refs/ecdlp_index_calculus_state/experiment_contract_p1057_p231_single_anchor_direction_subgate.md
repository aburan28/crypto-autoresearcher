# Experiment Contract: P1057 P231 Single-Anchor Direction Subgate

## Hypothesis
Inside the P1056 public cost reducer `case_count <= 2`, a calibration-only public direction-proxy subgate can isolate rank-dense source windows and reduce forward strict source charge per marginal rank gain below one rho budget per gained factor-rank dimension.

## Null hypothesis
Any calibration-selected direction subgate either fails to transfer forward, selects no usable source certificates, has zero forward rank gain, or does not improve charge per rank gain relative to the full P1056 subgate.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- seeds: inherited from P1054/P1056 selected source windows
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- baseline: P1056 public source-cost reducer `case_count <= 2`
- direction-proxy features: `max_ops`, `op_range`, `mean_ops`, `min_ops`, `salt_span`, `unique_salts`, `transfer_span`

## Metrics
- group operations: strict source charge = sum of `direct_ops_over_rho` over all source-family cases in selected windows
- field operations: not separately measured
- memory: selected windows, loaded certificate artifacts, unique target-eliminated rows
- relation probability: usable direct-source certificates per selected source case
- rank: base rank, base-plus-source rank, marginal rank gain, remaining free columns
- solver degree: not applicable
- wall-clock: script runtime

## Positive control
The P1056 baseline must reproduce forward rank gain `2` at strict charge `10.67153288` rho.

## Negative control
The P1052 gap split should remain empty or rank-neutral.

## Success criterion
The selected public direction subgate must:

- be chosen from calibration public features only;
- have calibration rank gain at least `2`;
- improve calibration charge per rank gain relative to the P1056 calibration baseline;
- on forward validation, produce positive rank gain and improve charge per rank gain relative to P1056 forward.

If forward charge per rank gain is below `1.0` but total strict source charge remains above `1.0`, the result is a positive rank-density signal, not a faster-than-rho algorithm.

## Falsification criterion
P1057 is negative if no calibration direction subgate improves calibration charge per gain, or if the selected rule fails to improve forward charge per gain while preserving forward rank gain.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1057_p231_single_anchor_direction_subgate.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1057_p231_single_anchor_direction_subgate.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1057_p231_single_anchor_direction_subgate_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `LOW-SUPPORT`: this audit permits a single calibration anchor if it has rank gain at least `2`; forward validation is mandatory.
- `HEURISTIC`: rank-density improvement is an index-calculus collector signal, not an asymptotic proof.
- `POLLARD-RHO-BOUNDARY`: total strict source charge and charge per rank gain are both reported. No deployed-curve break is claimed.
- `OPEN`: target descent, sparse linear algebra closure, and scaling remain open.

## Next concrete action
Run P1057. If positive, build P1058 to replicate the selected direction proxy on a disjoint chronological forward slice or to add batching over same-proxy windows; if negative, return to P1056 and test a different public source-family scheduler.

## Results
Command:

```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1057_p231_single_anchor_direction_subgate.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1057_p231_single_anchor_direction_subgate.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1057_p231_single_anchor_direction_subgate_probe.json
```

Claim: `POSITIVE_SIGNAL_P1057_DIRECTION_CPG_BELOW_RHO_NOT_TOTAL_RHO`.

P1057 kept the P1056 subgate `case_count <= 2` and selected this calibration-only public direction proxy:

```text
max_ops >= 0.83211679
```

Selection used calibration public source features only. Direct/shared verifier labels were not used by the subgate.

P1056 forward baseline:

- selected windows: `7`
- selected source cases: `14`
- strict source charge: `10.67153288` rho
- source rank gain over base: `2`
- charge per rank gain: `5.33576644`
- base plus source rank: `11/16`
- free columns after source rows: `[6,7,10,14,15]`

P1057 forward validation:

- selected windows: `1` (`18464_18471`)
- selected source cases: `2`
- strict source charge: `1.51824818` rho
- source rank gain over base: `2`
- charge per rank gain: `0.75912409`
- charge reduction factor versus P1056: `7.02884615`
- rank-gain retention versus P1056: `1.0`
- usable source certificates: `1`
- unique target-eliminated source rows: `6`
- source rows touching column `15`: `5`
- base plus source rank: `11/16`
- free columns after source rows: `[6,7,10,14,15]`

Calibration control:

- selected windows: `1` (`10336_10343`)
- strict source charge: `1.65693431` rho
- source rank gain over base: `2`
- charge per rank gain: `0.82846716`

P1052 gap control:

- selected windows: `0`
- source rank gain: `0`

## Interpretation
P1057 improves the P1056 source-cost profile: it preserves the same forward marginal rank gain `2` while reducing strict source charge from `10.67153288` to `1.51824818` rho. Charge per gained factor-rank dimension is now below one rho budget.

This is a low-support positive signal, not a completed faster-than-rho algorithm. The rule is anchored by one calibration window and one forward window, total strict charge is still above one rho, the rank does not advance beyond `11/16`, and target descent/sparse-linear-algebra closure remain open.

## Next concrete action after results
Build P1058 as a disjoint-forward replication and batching audit for `case_count <= 2 AND max_ops >= 0.83211679`. It should test later chronological windows, report whether the same proxy finds additional rank-gain windows, and compute the batch amortization factor needed to turn `1.51824818` rho strict charge into a total below-rho collector step.
