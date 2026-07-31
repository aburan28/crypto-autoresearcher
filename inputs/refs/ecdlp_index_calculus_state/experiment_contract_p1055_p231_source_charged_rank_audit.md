# Experiment Contract: P1055 P231 Source-Charged Rank Audit

## Hypothesis
A public P1054 source-window gate over `mode_low_term_support_total5/top16/direct_source` does more than enrich accepted factor materialization: the selected source windows contribute target-eliminated factor-row rank over the existing order-`11779` bank after charging all selected source cases against Pollard rho.

## Null hypothesis
The P1054 gate only predicts aggregate materialization labels. Under source charging, the selected windows either produce no usable direct-source certificates, no new target-eliminated factor rows, or zero marginal rank gain beyond the current base factor bank.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`, factor-variable count inferred from scorer artifacts
- seeds: inherited from source row keys and transfer windows in the selected-leaf artifacts
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- baseline: existing base certificates from each factor-rank scorer artifact plus Pollard rho charge from `direct_ops_over_rho`

## Metrics
- group operations: strict source charge = sum of `direct_ops_over_rho` over all source-family cases in selected windows
- field operations: not separately measured in this audit
- memory: number of loaded certificate artifacts and unique target-eliminated rows
- relation probability: usable direct-source certificates per charged source case
- rank: base rank, source-only rank, base-plus-source rank, marginal rank gain, free columns after source rows
- solver degree: not applicable
- wall-clock: script runtime

## Positive control
Calibration windows selected by the P1054 rule should contain usable source certificates and nonzero target-eliminated rank gain if the rank extractor is wired correctly.

## Negative control
The P1052 gap split should remain empty or rank-neutral because P1054 selected zero gap windows.

## Success criterion
Forward-validation selected windows produce at least one usable direct-source certificate, at least one unique target-eliminated factor row, and positive marginal rank gain over the base bank. A separate stronger status is reserved for any case where strict source charge is below one rho budget.

## Falsification criterion
The hypothesis is narrowed or killed if forward selected windows have zero usable direct-source certificates, zero unique target-eliminated rows, or zero marginal rank gain after de-duplication and source charging.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1055_p231_source_charged_rank_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1055_p231_source_charged_rank_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1055_p231_source_charged_rank_audit_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: this is a p231/order-`11779` toy harness audit.
- `MODEL-BOUND`: factor rank is measured inside the current verifier target-eliminated factor namespace.
- `HEURISTIC`: positive rank gain is treated as an index-calculus precursor, not as an asymptotic claim.
- `POLLARD-RHO-BOUNDARY`: source charge is reported explicitly; positive rank gain alone is not a faster-than-rho algorithm.
- `OPEN`: target descent, sparse linear algebra closure, and public held-out collection at cryptographic scale remain unproved.

## Next concrete action
Run the P1055 audit, then promote the branch only if forward selected windows give source-charged rank gain. If rank gain is positive but rho charge is high, the next experiment is a P1056 public source-cost reducer or batch collector over the same selected family.

## Results
Command:

```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1055_p231_source_charged_rank_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1055_p231_source_charged_rank_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1055_p231_source_charged_rank_audit_probe.json
```

Claim: `POSITIVE_SIGNAL_P1055_SOURCE_CHARGED_RANK_GAIN_NOT_RHO_WIN`.

Forward validation selected `50` windows and `174` source-family cases under the P1054 rule `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`. Those cases had strict source charge `129.45985446` rho budgets, with `46` direct-verified below-rho cases and `46` usable direct-source certificates. The selected direct-source certificates produced `69` unique target-eliminated factor rows.

Rank result over order `11779`:

- base rank: `9/16`
- base free columns: `[4,6,7,10,11,14,15]`
- base plus selected source rank: `12/16`
- marginal source rank gain: `3`
- source-only rank: `6`
- source rows touching column `15`: `26`
- free columns after selected source rows: `[6,7,14,15]`
- strict charge per marginal rank gain: `43.15328482` rho budgets

Controls:

- calibration selected `10` windows, gave source rank gain `2`, strict charge `26.83941615`, and `10` usable source certificates.
- P1052 gap selected `0` windows, gave rank gain `0`.

## Interpretation
P1055 validates the P1054 gate as an index-calculus precursor: selected public source windows do produce real target-eliminated factor-row rank beyond the base bank. It does not validate a faster-than-rho algorithm. The source charge is too high, column `15` remains free after selected rows, and target descent/sparse-linear-algebra closure remain open.

## Next concrete action after results
Build P1056 as a public source-cost reducer or batch collector for the same selected family. The concrete target is to keep the P1054/P1055 rank-gain signal while reducing strict source charge per marginal rank gain, or to batch enough selected windows that source generation amortizes into a viable collector model.
