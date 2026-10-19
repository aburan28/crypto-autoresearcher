#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#show heading: set text(size: 11pt)

= Run report: EXP-ENDO-33a1ee / RUN-ENDO-bc1b14

*Timed isogenous-model scalar multiplication.* This report records observations only. It gives no verdict: the evidence review decides that, and it also checks the gates.

== Identity
- *Records:* experiment `EXP-ENDO-33a1ee`, hypothesis `H-ENDO-c9f324`, approval `DEC-20261016-cc8e56`, goal `GOAL-ENDO-001`.
- *Tasks:* executor `TASK-20261016-1aa07a` (claimed, released `completed`); snapshot `TASK-20261016-8a9451`.
- *Run directory:* `experiments/EXP-ENDO-33a1ee/runs/RUN-ENDO-bc1b14/`.
- *Code:* design commit `f41fa9abb`; manifest `repository_dirty: false` (harness only).
- *Host:* one shared cloud container, x86_64, 4 CPUs, no core pinning or isolation. The compiler is `cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`, run as `--cflags=-O2 -march=native` (manifest `commands`).
  - The `cc` string in `summary.json` provenance omits `-march=native`. That is a recording defect in `isobench.py`, which slices the argument list too short; the compile used the frozen flags.
- *Timing of the run:* started 2026-10-16T19:55:02Z, wall time 15.3 s.
- *Concurrent load:* an independent-validation subagent (`TASK-20261016-1b5210`) was doing CPU work in the same container around this time. Its end time relative to this run was not recorded.

== What ran
- *Curves:*
  - Target: `other/BADA55-VPR-224`, with route [5, 5] (degree 25) to an a = −3-equivalent neighbour.
  - Positive control: the constructed 3-isogenous neighbour of NIST P-256, with route [3] back to P-256's a = −3 model.
- *Arms,* run on the same 64 (P, k) pairs per curve, interleaved, with the arm order rotated per repetition, for 41 repetitions:
  - A0: k P on E (generic-a doubling);
  - A1 persistent: k′ P′ on the a = −3 model;
  - A2 one-shot: forward route, k′ = k c mod n, k′ P′, then the dual route;
  - A3: A0 repeated (A/A control).
- *Measured value:* per-repetition mean ns per scalar multiplication. The ratios are derived as the median over repetitions of the paired per-repetition ratio, with a 95 % percentile-bootstrap interval (4,000 resamples).
- *Correctness:* every arm's affine output equals the Python reference on all 64 points (`correct: true` on both curves).
- *Run checks:* `check.py` reports "ok: both curves correct, 41 repetitions x 4 arms recorded". Coverage: `output_validated`.

== Graph
#figure(image("ratios.svg", width: 100%), caption: [RUN-ENDO-bc1b14, recorded timings only. Faint dots: per-repetition ratio to A0 (41 per row). Large dot and bar: median with 95 % bootstrap CI. Grey band: the frozen A/A margin [0.95, 1.05].])

== Recorded values (ns per scalar multiplication; medians over 41 repetitions)
#table(columns: 8, inset: 3pt, stroke: 0.4pt + luma(200), align: (left, right, right, right, right, left, left, left),
  [*curve*], [*A0*], [*A1*], [*A2*], [*A3*], [*A1/A0 [95 % CI]*], [*A2/A0 [95 % CI]*], [*A3/A0 [95 % CI]*],
  [BADA55-VPR-224], [224,139], [212,508], [220,662], [226,698], [0.932 [0.922, 0.942]], [0.969 [0.965, 0.977]], [0.999 [0.992, 1.010]],
  [control (P-256 neighbour)], [272,232], [250,264], [250,267], [267,944], [0.920 [0.907, 0.932]], [0.926 [0.909, 0.935]], [1.000 [0.986, 1.006]],
)
- *Derived savings* (1 − ratio):
  - target: persistent 6.8 % [5.8, 7.8], one-shot 3.1 % [2.3, 3.5];
  - control: persistent 8.0 % [6.8, 9.3], one-shot 7.4 % [6.5, 9.1].
- *Modelled values* from RUN-ENDO-d7cb69, for comparison:
  - target: persistent 15.20 %, one-shot 11.44 %;
  - control: persistent 15.28 %, one-shot 14.46 %.
- *Gate quantities* as recorded. The review checks them against the frozen thresholds; this report does not:
  - A/A CI: [0.992, 1.010] on the target and [0.986, 1.006] on the control;
  - control A1/A0 upper bound: 0.932;
  - correctness: true on both curves.

== Spread (recorded per-repetition ns, derived quantiles)
The per-repetition times are heavy-tailed. The interquartile range of A0 on the target is 220,795–259,340 ns, with a maximum of 403,654 ns, about 1.8 times the minimum. Single-repetition ratios range from about 0.55 to 1.85, consistent with episodes of contention on the shared host.

Taking the minimum of each arm instead of the median gives the same ordering: on the target, A1/A0 = 204,442 / 219,710 = 0.930 and A2/A0 = 212,834 / 219,710 = 0.969. This min-based figure is derived, not a frozen metric.

== Missing or out of scope
- A single host, with no isolation. An `ecbench-independent-runner` replication on an isolated runner would be stronger.
- `bench.c` uses generic CIOS arithmetic, not an optimised library.
- Correctness is checked on repetition 0's outputs.
- Peak memory is not recorded.
- Known-scalar multiplication only; no ECDLP claim.

== Files
`plot.py` draws `ratios.svg` from `runs/RUN-ENDO-bc1b14/{target,control}/{timings,summary}.json` only.
