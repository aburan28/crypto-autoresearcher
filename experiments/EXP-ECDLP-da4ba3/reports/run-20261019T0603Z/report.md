# Recorded geometry census

Observations only. This report records the completed run; it makes no scientific verdict, speedup or security claim.

Experiment EXP-ECDLP-da4ba3; hypothesis H-ECDLP-9e7a19; goal GOAL-ECDLP-001. The sole requested trial, RUN-ECDLP-dad803, completed and its independent checker passed, with zero failed checks. No trial failed or timed out. [Immutable run records](../../runs/RUN-ECDLP-dad803/) were published at commit 49c499a9 before this report.

The exact command was `python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-da4ba3/trial-plan.json --owner executor-prym-geometry --epoch 1`. Producer revision e2442834348a7ff60ee50c4618268555d0d5f2fc had no tracked changes. Parameters were the eight primes 11,13,17,19,23,31,43,59; eight first eligible primary pairs and eight next eligible companion pairs per prime; field degrees 1 and 2; forward and reverse enumeration; seed 0. The input is a new deterministic catalogue, unrelated to the unsourced historical “32 covers.” F43 (0,1) is previously seen calibration.

Measured exact counts: 64 primary and 64 companion covers, 24 synthetic screen controls. The checker independently recounted every cover in both field degrees and checked both enumeration arms, the elliptic trace recurrence, genus-2 reciprocal polynomial and rational gcd. All synthetic shared/coprime/malformed classifications agreed. Forward/reverse A/A comparisons agreed. Raw per-cell field counts, candidate rejections and operation vectors remain in `raw-result.json` and `events.jsonl`; independent costs remain in `verification.json`.

The graph plots recorded numbers of covers with nonzero rational Frobenius gcd, in covers per eight-cell panel. The primary counts sum to 3/64 and companion counts to 4/64 (derived by addition of the plotted integers). These are exact finite-census observations; no sampling intervals were recorded. In particular, factor overlap does not supply an explicit map or an ECDLP algorithm.

![Recorded overlap counts, RUN-ECDLP-dad803](graph.svg)

Measured producer wall time: 2.040924355 s; CPU: 2.059629574 s; peak RSS: 53,055,488 bytes. Independent checker wall: 0.500340244 s; CPU: 0.499568460 s; peak RSS: 50,208,768 bytes. Environment: Linux x86_64, Python 3.12.14; full host, dependencies and resource guard details are in the manifest and environment record. Process-group RSS was sampled every 0.05 s, so shorter peaks can be missed. Operation units are not summed into a scalar work metric.

Fp and Fp2 provide only two genus-3 traces. The complete genus-3 Frobenius polynomial was inferred from the geometry, not independently certified. Jacobian maps, subgroup transport, relation generation and recovery were not measured. Missing measurements remain missing. No canonical evidence graph changes follow from this execution-only report.

The one-page PDF was opened and visually inspected before publication. Its graph and editable recorded-data source accompany this file.
