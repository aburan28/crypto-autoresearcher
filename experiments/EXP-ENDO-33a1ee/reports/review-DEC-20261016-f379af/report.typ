#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#set par(justify: false)
#show heading: set text(size: 11pt)

= Decision report: DEC-20261016-f379af (EXP-ENDO-33a1ee)

*Decision: support H-ENDO-c9f324, scoped.* Evidence `EV-ENDO-118b3a`: direction supports, strength preliminary, claim tier measured-single-host. Read with correction `CORR-20261016-37897c` (provenance string only). No ECDLP, rho or exponent claim changes; wall time is not a measured bound.

== Identity
- Experiment `EXP-ENDO-33a1ee`, run `RUN-ENDO-bc1b14`, hypothesis `H-ENDO-c9f324`, idea `IDEA-20261016-15a6fc`, question `RQ-ENDO-476761`, goal `GOAL-ENDO-001`.
- Approval `DEC-20261016-cc8e56`; executor `TASK-20261016-1aa07a`; snapshot `TASK-20261016-8a9451` at `6033c3f08`; independent validation `TASK-20261016-35d324` (passed); ledger archive `TASK-20261016-5c0f78`.
- Analysis: `experiments/EXP-ENDO-33a1ee/analysis.md`. Earlier run report: `reports/run-20261016T1955Z/report.pdf`.

== Scoped claim
On other/BADA55-VPR-224, on one shared KVM host (Intel Xeon 2.80 GHz, 4 vCPU, no pinning), in `harness/endosweep/isobench/bench.c` (4-limb CIOS, S = M) compiled with cc 13.3.0 -O2 -march=native, one-shot variable-base k·P routed through the 5·5-isogenous neighbour's a = −3 model takes 0.9693 (95 % CI 0.9647 to 0.9767) of the time of k·P on E with E's generic-a doubling: a 3.07 % saving. The persistent form takes 0.9324 (0.9220 to 0.9423). 64 paired inputs, 41 repetitions. Nothing transfers to other curves, hosts, compilers or implementations.

== Graph
#figure(image("decision.svg", width: 100%), caption: [RUN-ENDO-bc1b14, recorded timings only. Filled dot and bar: recorded median paired ratio and 95 % percentile-bootstrap CI (4,000 resamples). Faint dots: 41 per-repetition ratios. Hollow dot: median without the repetitions flagged by the validator's contention rule (any arm above 1.10 times its median). Tick: modelled ratio from RUN-ENDO-d7cb69. Dashed: ratio 1 (success requires the target A2/A0 upper bound below it). Grey: the frozen A/A margin from 0.95 to 1.05.])

== Observation
- Gates: correctness true on both curves (512 of 512 outputs recomputed by the validator); target A/A 0.9989 [0.9923, 1.0101]; control A/A 1.0002 [0.9864, 1.0060]; control A1/A0 upper bound 0.9316.
- Target: A1/A0 0.9324 [0.9220, 0.9423]; A2/A0 0.9693 [0.9647, 0.9767]. Medians A0 224,139 ns, A1 212,508 ns, A2 220,662 ns.
- Control: A1/A0 0.9197 [0.9073, 0.9316]; A2/A0 0.9262 [0.9089, 0.9352].
- Contention bursts of 1.2–1.9 times hit 17 of 41 (target) and 19 of 41 (control) repetitions, evenly across arms and slots, with no drift. Without them: target A2/A0 0.9681 [0.9638, 0.9710], A3/A0 0.9987 [0.9944, 1.0062] (validator B4).

== Comparison
- Gate resolution: all gates pass, so the target inference is released.
- Success criterion (target A2/A0 upper bound below 1): *met*, 0.9767. Falsification and inconclusive branches do not apply. No gate outcome or interval side changes without the flagged repetitions.
- Prediction: persistent saving 6.76 % within (0, 15.205 %); one-shot 3.07 % within (0, 11.441 %); one-shot below persistent. *Holds*, and the control shows the same ordering (8.03 % and 7.38 %).
- Measured against modelled: the target keeps 44 % of the persistent and 27 % of the one-shot modelled saving; the control keeps 53 % and 51 %.
- Against the index-calculus baseline and the matched rho: not applicable (known-scalar wall-clock).

== Inference
On this curve, host, compiler and implementation the one-shot model-change route is measurably faster than k·P on E. The frozen on\_positive branch applies: the hypothesis is supported in exactly that scope. Strength stays preliminary: one curve, one host, an untuned generic A0, and no replication.

== Limitation
- Single shared host; contention visible though symmetric. Generic CIOS and an untuned A0. Variable-time code; one inversion per arm.
- One curve; BADA55-VPR-224 is a published demonstration curve, not a deployed standard (recalled pointer, not relied on).
- The prediction and the A/A margin were written with the smoke values in view (disclosed). Correctness was checked on repetition 0.
- Faster known-scalar multiplication does not establish faster unknown-scalar recovery.

== Next actions (ranked, recommended, not approved)
+ Fix isoglv's one-shot pricing and re-run the combined screen (DEC-20261016-4f3a1a).
+ Timed bench of the combined route on other/Tom-384 against GLV on E.
+ ecbench independent-runner replication of this experiment with pinning and isolation, as a new frozen contract. It is the frozen next step but hardens only a narrow claim on a demonstration curve; if it holds, a KN-FIND is promoted at its review.

== Canonical graphs
Checked and left unchanged: `research/endosweep_curves_20261006/` (modelled tables, no timing) and `knowledge/frontiers/ecdlp/` (no ECDLP claim moves). No canonical graph changes.

== Files
`plot.py` draws `decision.svg` from `runs/RUN-ENDO-bc1b14/{target,control}/{timings,summary}.json` only, plus the modelled gains frozen in the specification.
