#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(font: "Arial", size: 9.5pt)
#set par(justify: true, leading: 0.62em)

= Bounded k11 solver-to-certificate pilot

*Observation-only run record.* EXP-ICPERF-018b0c; H-ICPERF-195806; GOAL-ICPERF-e6b6a4. The two output-validated stage directories preserve censored and gated calls. Scientific interpretation is reserved for independent evidence review.

First trial start: 2026-10-17 14:37:33.881131 UTC. Source commit: `56be1ed09b6140fbd51aff2602b1006494a91159`. Raw source commit: `f5098b004f45d2ce85b38a1c6fa837d915576206`. Content-first raw snapshot marker: `72d96cc75e90db9fbe59b0b7fdb970f727beed1e`. Its receipt at `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-35c5a6/archives/TASK-20261017-da78be/snapshot-receipt.json` binds 26 raw files; the additive queue also binds that receipt.

== Frozen panel

One ordinary binary curve over GF(2^61), prime subgroup order 576460752557211763 (60 bits), eight summands, and two target-blind 316-column bases. The protocol requested two planted positives, then 64 calls for eight common natural subgroup targets times four channels times two bases. It used CryptoMiniSat 5.14.7, one thread, seed 20261017, a 300 s call wall cap, 8 GiB sampled-RSS cap, and 64 primary models per call. Python 3.12.8 ran on macOS 26.6 arm64. The run-time dirty-tree flag was not recorded. Exact commands and source hashes are in the two run directories.

== Observed calls and gate

#table(
  columns: (1.5fr, 0.8fr, 1fr, 1fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("cfd8df"),
  [Arm / stage], [Calls], [Process wall], [Outcome],
  [Weighted positive], [1], [300.015663 s], [wall censored],
  [Local-random positive], [1], [300.021396 s], [wall censored],
  [Natural panel], [0 of 64], [No solver process], [gated],
)

#image("diagram.svg", width: 100%)

The bars use the exact raw process-wall samples from `RUN-ICPERF-712e85/calls.tar.gz`: 300.0156629999983 s and 300.0213959590037 s. Each arm has n=1, with no recorded spread or uncertainty. Both reached the 300 s watchdog cap. The sampled process CPU user+system totals are derived as 271.031035392 s and 243.695254528 s. Sampled peak RSS values are 207,814,656 and 222,822,400 bytes. Neither call returned a solver model or a point certificate.

The positive driver took 601.2394865410024 s wall, including 0.7232824589955271 s bundle packaging and 12 raw call files. The gated natural driver took 0.0026677079949877225 s wall, including 0.0005297500028973445 s bundle packaging and zero raw call files. Its 64 scheduled solver calls were unattempted under the frozen positive-control gate. Both stage `independent_check.json` files validate their raw output and classification; they record zero natural calls and zero distinct projected rows. Full stage CPU and complete preparation-to-target cost were not recorded in this pilot.

The equal-column candidate and control had equal archived per-channel formula counts. The run measured no natural yield, useful rank, degree of regularity, linear algebra, unknown-target recovery, matched rho, or complete end-to-end S. Wall censoring gives neither solver exhaustion nor evidence that point relations are absent.

*Sources:* `RUN-ICPERF-712e85/raw-result.json`, `RUN-ICPERF-1c8bfe/raw-result.json`, their `execution-receipt.json` and `independent_check.json` files, the positive `calls.tar.gz` summaries, the frozen specification and trial plan, and the raw snapshot receipt named above. `plot-data.json` and `chart.py` reproduce the embedded SVG; the companion `report.md` gives the full path links and cost detail.
