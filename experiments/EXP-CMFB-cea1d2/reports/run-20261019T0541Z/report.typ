#set page(margin: 1.7cm, numbering: "1")
#set text(size: 9.5pt)
#set heading(numbering: "1.")
#show raw: set text(size: 8pt)

= Run report: EXP-CMFB-cea1d2

*Observations only.* This report describes what the eight frozen trials ran and what they recorded. It states no verdict, no support or weakening, and no significance; those belong to an independent evidence review. A recorded field that the frozen rule computed mechanically is quoted as recorded, not adopted. Numbers are marked _recorded_ (read from a run file) or _derived_ (arithmetic on recorded values, shown).

== Identity
#table(columns: (auto, 1fr), stroke: 0.4pt,
  [Experiment], [EXP-CMFB-cea1d2 (hypothesis H-CMFB-9b2eed, question RQ-CMFB-33610e, idea IDEA-20261015-cba035)],
  [Executor task / claim], [TASK-20261015-1c0251, claim executor-run-cmfb epoch 1 (commit cc2ece9a49)],
  [Frozen plan], [trial-plan.json sha256 d580d0503c2b7c9e4437d1f03eca2d6a93d86d7620e81ccb11c4a7a3b3ff50fe],
  [Code], [commit cc2ece9a497e805ec8ac76f38a5b28a3549ac08e, dirty = false (recorded in manifest)],
  [Host], [Linux x86_64, 4 CPUs, 16.9 GB RAM, Python 3.13.16, numpy 2.5.3 (recorded)],
  [Window], [2026-10-19 05:41:51Z to 05:57:50Z, wall about 16 min (recorded start and finish times)],
  [Instance list], [sha256 38cf55093614d8f8761e392d75e17ae5f0266e50b69b7abd58d6f01c3b2fa314 (identical in the pre-run inventory), 107 members total (recorded)],
)

== Trials
Requested 8, completed 8, failed 0, timed out 0. Every trial's checker returned success and the supervisor recorded `output_validated`. Run directories are under `experiments/EXP-CMFB-cea1d2/runs/`.
#table(columns: (auto, auto, auto, auto), stroke: 0.4pt,
  [*Trial*], [*Run ID*], [*Started (UTC)*], [*Duration*],
  [t1 inventory], [RUN-CMFB-2373be], [05:41:51], [2.7 s],
  [t2 gate: instrument], [RUN-CMFB-5905c0], [05:41:56], [24.4 s],
  [t3 gate: sensitivity], [RUN-CMFB-66b0fe], [05:42:23], [66.5 s],
  [t4 measure C16 + C20], [RUN-CMFB-3dc120], [05:43:33], [60.6 s],
  [t5 measure C24, FAM], [RUN-CMFB-42a578], [05:44:36], [241.9 s],
  [t6 measure C24, N-A], [RUN-CMFB-e13f0e], [05:48:40], [253.7 s],
  [t7 measure C24, N-B], [RUN-CMFB-c71d35], [05:52:57], [288.3 s],
  [t8 analysis], [RUN-CMFB-2010d3], [05:57:48], [2.2 s],
)
Durations are _derived_ from the recorded start and finish times. Peak memory of the analysis trial: 58.3 MB (recorded).

== Instances and cells
Recorded family-member counts: C16 = 4, C20 = 10, C24 = 13. Recorded arm sizes (FAM / N-A / N-B): C16 4 / 8 / 8, C20 10 / 16 / 16, C24 13 / 16 / 16. The pooling rule P1 was recorded as not applied. The pre-registered Bateman-Horn expectations were 3.11, 8.01 and 14.42; exact counts over expectation were 1.28, 1.25 and 0.90 (recorded).

The analysis recorded `powered` for C24 only; `mde_ok` was recorded false for C16 and C20, and `growth_assessable` = false (one powered cell). Recorded C20 arm MDEs were FAM 0.243 %, N-A 0.268 %, N-B 0.245 %, against the contract threshold 0.25 %.

== Gates and controls (recorded)
- Instrument gate t2 and sensitivity gate t3 passed; invalidation rules I1 to I9 all recorded true. The run is recorded `official` and `all_inputs_official`.
- qr_window positive control (f(x) residuosity): pooled scan-efficiency ratio R between 1.9941 and 2.0009 in all 9 pools, all inside the recorded band 1.98 to 2.02. Negative control (Legendre of x), R_wrong: 0.9970 to 1.0006 in all 9 pools. See the right panel of the figure.
- Planted-base sensitivity: detected 7 of 8 (C16), 8 of 8 (C20), 8 of 8 (C24). Pooled recorded ratio against the known value: C16 1.02667 vs 1.03035, C20 1.01091 vs 1.01247, C24 1.00525 vs 1.00521, all recorded within tolerance; pooled randomization p = 5.0e-5 in each cell.

== Measured coverage excess
T is the recorded mean over members of (coverage ratio against 200 matched random bases) minus 1, in percent. Intervals are the recorded 95 % moving-block-bootstrap intervals. Holm p is recorded only for powered cells. The last two columns show the recorded variance ratio and the same ratio rescaled (see below).
#figure(image("fig_run_summary.svg", width: 100%), caption: [Left: recorded T with 95 % intervals per arm and cell (n as labeled), grey band = the contract resolution ±0.5 %. Right: recorded scan-efficiency ratios per pool. Source: RUN-CMFB-2010d3 raw-result.json; script plot.py. Missing arm-cells: none.])
#text(size: 7.5pt)[
#table(columns: (auto, auto, auto, auto, auto, auto, auto, auto, auto, auto), stroke: 0.3pt, align: center,
  [*Arm*], [*Cell*], [*n*], [*T (%)*], [*95 % interval (%)*], [*Holm p*], [*rand. p*], [*MDE (%)*], [*meas/formula*], [*derived*],
  [FAM], [C16], [4], [-0.174], [[-0.174, -0.034]], [-], [0.411], [1.332], [2.56], [0.90],
  [FAM], [C20], [10], [-0.030], [[-0.074, +0.048]], [-], [0.441], [0.243], [2.57], [0.90],
  [FAM], [C24], [13], [-0.022], [[-0.038, -0.006]], [0.094], [0.031], [0.065], [2.68], [0.94],
  [N-A], [C16], [8], [-0.085], [[-0.405, +0.263]], [-], [0.686], [1.318], [2.39], [0.84],
  [N-A], [C20], [16], [-0.009], [[-0.061, +0.039]], [-], [0.843], [0.268], [2.58], [0.90],
  [N-A], [C24], [16], [-0.000], [[-0.024, +0.027]], [0.969], [0.969], [0.063], [2.64], [0.92],
  [N-B], [C16], [8], [-0.009], [[-0.186, +0.166]], [-], [0.969], [1.537], [2.47], [0.86],
  [N-B], [C20], [16], [+0.010], [[-0.038, +0.057]], [-], [0.795], [0.245], [2.72], [0.95],
  [N-B], [C24], [16], [+0.016], [[-0.001, +0.035]], [0.159], [0.079], [0.057], [2.77], [0.97],
)]
All nine recorded 95 % intervals lie inside ±0.5 %. Recorded Holm adjusted p-values for the three powered-cell tests: FAM 0.094, N-A 0.969, N-B 0.159; `holm_rejection_below_delta` is empty. Recorded contrasts in C24 (FAM minus N-A, FAM minus N-A near-family stratum, N-A minus N-B) have 99 % intervals that include zero. The lead tier is recorded null.

The analysis recorded the field `classification` = `NULL_AT_RESOLUTION`, computed mechanically from the frozen decision rule. It is quoted here as recorded; it is not a review decision, and the contract states it is reported at resolution 0.5 %, not as "no effect".

== Departures and defects observed
- *Variance check (I10) fires in all 9 arm-cells.* The recorded `sigma_flag_I10` is true everywhere, with recorded measured/formula ratios 2.39 to 2.77. The contract was revised before freezing to centre this check on 1.4/√N (band 0.75x to 1.33x), but `analyze.py` still computes the Poisson-occupancy formula (`count.sigma_rel_formula`), the source of the earlier 0.49/√N constant. _Derived_ (approximate): multiplying each recorded ratio by 0.49/1.4 = 0.35 gives 0.84 to 0.97, inside the contract band. I10 is a non-void flag; the run is not voided, but the flag text recorded in the tables reflects the code, not the contract.
- *Powered cells.* One cell (C24) was recorded powered; C20 failed the MDE condition because the N-A arm's MDE (0.268 %) exceeded 0.25 %. The contract stated before the run that no slope claim was possible.
- *FAM at C16.* The recorded interval for FAM C16 has T at its lower end (T = -0.174 %, interval [-0.174, -0.034] %, n = 4); recorded as is, no explanation computed here.
- The checker and the supervisor recorded no failed or retried trial. No data is missing.

== What this report does not do
It does not review the run, set any hypothesis status, or say whether the null reading is warranted. Reproduce the figure with `python3 plot.py` in this directory (reads RUN-CMFB-2010d3 only).
