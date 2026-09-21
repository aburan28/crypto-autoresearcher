# Experiment Contract: P1056 P231 Public Source-Cost Reducer

## Hypothesis
A second-stage public subgate inside the P1054-selected source windows can preserve some P1055 target-eliminated factor-rank gain while reducing strict source charge per marginal rank gain.

## Null hypothesis
Any calibration-efficient public subgate either fails to transfer to forward windows, produces zero target-eliminated rank gain, or reduces charge only by discarding the rank signal.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- seeds: inherited from P1054/P1055 selected source windows
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- baseline: P1055 selected P1054 gate, forward charge `129.45985446` rho budgets for marginal rank gain `3`

## Metrics
- group operations: strict source charge = sum of `direct_ops_over_rho` over all source-family cases in selected windows
- field operations: not separately measured
- memory: selected windows, loaded certificate artifacts, unique target-eliminated rows
- relation probability: usable direct-source certificates per selected source case
- rank: base rank, base-plus-source rank, marginal rank gain, free columns after source rows
- solver degree: not applicable
- wall-clock: script runtime

## Positive control
The full P1054/P1055 gate must reproduce the known calibration and forward rank/charge baselines.

## Negative control
The P1052 gap split should remain empty or rank-neutral.

## Success criterion
The calibration-selected public subgate must:

- select at least `2` calibration windows;
- produce calibration marginal rank gain at least `2`;
- improve calibration charge per rank gain over the full P1054/P1055 calibration gate;
- on forward validation, produce positive rank gain and lower charge per rank gain than the full P1054/P1055 forward gate.

The result is still not a faster-than-rho algorithm unless total source charge for useful target descent is below the corresponding rho baseline.

## Falsification criterion
P1056 is negative if no public calibration subgate improves calibration charge per rank gain, or if the selected subgate has zero forward rank gain or no forward charge-per-gain improvement.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1056_p231_public_source_cost_reducer.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1056_p231_public_source_cost_reducer.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1056_p231_public_source_cost_reducer_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: factor rank is measured inside the current verifier target-eliminated factor namespace.
- `HEURISTIC`: charge-per-rank improvement is an index-calculus collector signal, not an asymptotic claim.
- `POLLARD-RHO-BOUNDARY`: the audit reports source charge explicitly and does not claim a deployed-curve break.
- `OPEN`: target descent, sparse linear algebra closure, and scaling to cryptographic prime fields remain open.

## Next concrete action
Run P1056 and record whether a calibration-selected public subgate reduces forward source charge per marginal rank gain. If positive but still above rho, build P1057 to combine the cost subgate with batching or rank-direction targeting for columns `[6,7,14,15]`.

## Results
Command:

```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1056_p231_public_source_cost_reducer.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1056_p231_public_source_cost_reducer.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1056_p231_public_source_cost_reducer_probe.json
```

Claim: `POSITIVE_SIGNAL_P1056_PUBLIC_COST_REDUCER_NOT_RHO_WIN`.

The calibration-only rule selector chose the public subgate:

```text
case_count <= 2
```

This rule was selected from calibration public source features only. Direct/shared verifier labels were not used by the subgate.

Full P1054/P1055 forward baseline:

- selected windows: `50`
- selected source cases: `174`
- strict source charge: `129.45985446` rho
- source rank gain over base: `3`
- charge per rank gain: `43.15328482` rho
- base plus source rank: `12/16`
- free columns after source rows: `[6,7,14,15]`

P1056 forward validation:

- selected windows: `7`
- selected source cases: `14`
- strict source charge: `10.67153288` rho
- source rank gain over base: `2`
- charge per rank gain: `5.33576644` rho
- charge reduction factor: `12.13132695`
- retained rank-gain fraction: `0.66666667`
- usable source certificates: `6`
- unique target-eliminated source rows: `13`
- base plus source rank: `11/16`
- free columns after source rows: `[6,7,10,14,15]`

Calibration control:

- selected windows: `2`
- strict source charge: `3.13138687` rho
- source rank gain over base: `2`
- charge per rank gain: `1.56569344` rho

P1052 gap control:

- selected windows: `0`
- source rank gain: `0`

## Interpretation
P1056 validates a public source-cost reducer for the P1054/P1055 branch. The rule `case_count <= 2` keeps a forward target-eliminated rank signal and cuts charge per rank gain by about `8.09x` relative to the full P1054/P1055 forward gate, while cutting total source charge by about `12.13x`.

This is still not a faster-than-rho ECDLP algorithm. Total source charge remains `10.67153288` rho for a partial rank signal, the rank gain drops from `3` to `2`, column `15` remains free, and target descent/sparse-linear-algebra closure remain open.

## Next concrete action after results
Build P1057 as a rank-direction-targeted batch collector: keep the P1056 `case_count <= 2` subgate, then add a public direction selector for the remaining free columns `[6,7,10,14,15]` or test whether batched source generation amortizes the `10.67153288` rho charge below a useful collector threshold.
