# Classical ECDLP projection and public-decoder follow-up

**Current research objective:** obtain a correct working algorithm, compare it with an explicit baseline, and improve that baseline. Novelty is assessed separately and is not a prerequisite for recognizing progress. The [interpretation clarification](../../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/interpretation-clarification.md) explains the earlier wording and the existing cube-root online baseline with preprocessing. This batch did not measure runtime against that baseline.

The fresh follow-up is complete: [report](../../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/HEADER.md), [PDF](../../experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/report.pdf), and [sealed raw records](../../experiments/EXP-ECDLP-7c0b1e/runs/RUN-ECDLP-0b7dd5/parts-manifest.json). It follows the [ten-track pilot](../classical_ecdlp_pilot/README.md). Both use classical computation outside index calculus.

One admitted batch ran five jobs with three concurrent measurement workers on 24 fresh toy curves at 8/10/12 subgroup bits and 192 public targets. All 3,624 output rows passed the frozen integrity checks. The command envelope took 121.795798 seconds; the supervisor including its checker took 124.715335 seconds. These are host observations, not algorithm comparisons.

| Module | Workload | Observed result and limit |
| --- | --- | --- |
| `src/projection_scale.cpp` | Exact pair/unary entropies, 99 unrestricted and 99 sign-matched null arrays per applicable feature | Pair gaps persist with much smaller magnitudes on fresh curves; unary gaps have mixed signs. Six fifth-power features are inapplicable. |
| `src/decoder.cpp` | Public unlabelled training; four offset views; paired model/exact-prefix modes; beams 1/8; constant/hash controls | 69 verified case witnesses concern 44 targets across 12–16 configurations. At beam 8, exact-prefix x-mod-7 recovers 13/192, hash 12/192, constant 7/192. No established advantage. |
| `src/basis_audit.cpp` | Expanded exact rational grammar, pin constraints, characteristic-two polynomial certificate | 496 invertible rational matrices, 16 AND-only survivors, zero joint AND-and-pin survivors. The characteristic-two obstruction concerns a fixed isolated AND gate under invertible local gauges. |

The decoder measurement path does not construct a labelled subgroup orbit or receive planted scalars or hidden intermediate traces. It learns approximate transition kernels from public unlabelled subgroup samples. Its multiview beam score is a heuristic, not an exact scalar posterior. Every returned candidate is checked with separately coded Jacobian arithmetic and replayed by the output checker. Constant-control recoveries receive the same per-instance verification. See [interface](INTERFACE.md), [model and prior art](theory/prior-art-and-model.md), and [post-run character/interface bounds](theory/character-kernel-bound.md). Source-enforced input separation is not OS-isolated blindness.

Setup, heldout calibration, views, inference, failed candidates and verification costs are retained separately. A positive toy witness is not a speedup, asymptotic exponent, novelty result or independent scientific review. No full-cost comparison with strong Pollard rho was made, so an algorithmic advantage is not claimed. The larger original discovery and blinded solver cohorts remain uncompleted.

The source-bound supervisor plan is complete and preserves its existing run:

```sh
python3 tools/experiment_execution.py status \
  --plan experiments/EXP-ECDLP-7c0b1e/trial-plan.json
```

The [operations record](protocol/admission/OPERATIONS.md) describes prospective admission and custody. The exact raw records were published first, then the isolated snapshot receipt `3e6ca92887e07e4d9a1710eddd8c450e70fc86fa` was checked with the unchanged Git repository verifier for 349 bound paths. Both task claims are released as completed. A new cohort or changed decoder needs fresh IDs, source freeze, prospective admission and a published live claim; do not overwrite this run.

The [open construction problem](../../problems/direct-ecdlp-cancellation-construction.md) remains. No original lead or hypothesis has been promoted, rejected or declared exhausted by these observations.
