# Experiment Contract: P1059 P231 Rowkey Prefix Shared Source

## Hypothesis
A calibration-selected public source row-key prefix can turn the P1057 low-support anchor from a projection into a concrete below-rho rank packet: after the frozen P1057 window gate fires, charge only the first source case whose public row-key multiset matches the calibration-learned row-key multiset, and retain target-eliminated marginal rank gain.

## Null hypothesis
The P1057/P1058 batching signal depends on charging the whole selected source window, or on an oracle/post-verifier case choice. A public row-key prefix selected from calibration either fails to reproduce calibration rank, fails on the forward anchor, or remains above one rho.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- seeds: inherited from P1054/P1056/P1057/P1058 selected source windows
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- frozen public window rule chain: P1054 `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`, P1056 `case_count <= 2`, P1057 `max_ops >= 0.83211679`
- case-level policy family: calibration-selected public row-key multiset, with first transfer-index prefix inside each selected window
- anchor forward window: `18464_18471`

## Metrics
- group operations: strict source charge = sum of `direct_ops_over_rho` for case-level selected source cases
- field operations: not separately measured
- memory: loaded certificate artifacts, selected windows, selected transfers, unique target-eliminated rows
- relation probability: usable direct-source certificates per case-level selected source case
- rank: base rank, base-plus-source rank, marginal rank gain, remaining free columns
- controls: whole-window P1058 charge, first-transfer prefix, last-transfer prefix, and post-verifier verified-only diagnostic
- wall-clock: script runtime

## Positive control
Whole-window selection must reproduce P1058 on the anchor: charge `1.51824818` rho, rank gain `2`, and charge per rank gain `0.75912409`.

## Negative control
The last-transfer public prefix should expose transfer-order instability if calibration and forward anchors disagree on where the verified source case sits.

## Success criterion
P1059 is a concrete low-support positive if the calibration-selected public row-key prefix has calibration rank gain at least `2`, forward-anchor rank gain at least `2`, and forward-anchor strict source charge below one rho. It is not a complete index-calculus algorithm unless sparse linear algebra and target descent are implemented.

## Falsification criterion
P1059 is negative for concrete batching if the calibration-selected public row-key prefix does not exist, does not forward-validate on `18464_18471`, has zero marginal rank gain, or remains above one rho. A post-verifier-only success is diagnostic and must not be promoted as a public source schedule.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1059_p231_rowkey_prefix_shared_source.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1059_p231_rowkey_prefix_shared_source.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `FROZEN-WINDOW-RULE`: P1059 must not retrain P1054/P1056/P1057 on forward labels.
- `CALIBRATION-SELECTED`: row-key multiset selection may use calibration rank/charge only.
- `LOW-SUPPORT`: one calibration anchor and one forward anchor are expected.
- `POLLARD-RHO-BOUNDARY`: below-rho source charge for a rank packet is not a deployed-curve break, sparse-linear-algebra closure, or target descent.

## Next concrete action
Build P1060 as a disjoint-support validation or target-descent pressure test for the learned row-key prefix. Require either fresh/disjoint rank-packet replication or evidence that the below-rho rank packet contributes to an individual-log descent surface.

## Results
- Status: `POSITIVE_SIGNAL_P1059_ROWKEY_PREFIX_TOTAL_BELOW_RHO_LOW_SUPPORT`.
- Calibration-selected public row key: `22050.cf1@11731:uniform:256:salt173`, `22050.cf1@11731:uniform:256:salt175`.
- Calibration row-key prefix: selected transfer `10343`, strict charge `0.83211679` rho, marginal rank gain `2`, charge per rank gain `0.4160584`.
- Forward anchor row-key prefix: selected transfer `18465`, strict charge `0.83211679` rho, marginal rank gain `2`, charge per rank gain `0.4160584`.
- Whole-window P1058 positive control: forward anchor charge `1.51824818` rho, marginal rank gain `2`, charge per rank gain `0.75912409`.
- First-transfer control: fails calibration with rank gain `0`.
- Last-transfer control: succeeds on calibration but fails the forward anchor with rank gain `0`.
- Post-verifier verified-only diagnostic: matches the row-key prefix on the forward anchor, but remains diagnostic rather than a public selector.

## Interpretation
P1059 turns the P1058 two-way amortization projection into a concrete case-level source schedule for this low-support anchor: one calibration-selected public row-key prefix keeps the same target-eliminated rank gain while reducing total forward-anchor strict source charge below one rho. This is an index-calculus precursor rank-packet signal, not a complete ECDLP improvement, because disjoint replication, sparse linear algebra, and target descent are still open.

## Failure modes and boundaries
- `LOW-SUPPORT`: one calibration anchor and one forward anchor.
- `NO-DISJOINT-REPLICATION-YET`: P1058 found no later frozen P1057 windows.
- `MODEL-BOUND`: rank is still measured inside the current target-eliminated factor namespace.
- `POLLARD-RHO-BOUNDARY`: below-rho source charge for a rank packet is not a target recovery or deployed-curve break.
