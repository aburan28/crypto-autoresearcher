#set page(margin: 1.7cm, numbering: "1")
#set text(size: 9.5pt)
#set heading(numbering: "1.")
#show raw: set text(size: 8pt)

= Superseding analysis of EXP-CMFB-cea1d2 (non-official, zero compute)

*Scope.* Recorded run RUN-CMFB-2010d3 (t8) is left untouched. This analysis re-reads the recorded raw results of the seven earlier runs through the frozen `implementation/analyze.py`, unmodified on disk, in two steps (`superseding_analysis.py`, result `superseding_result.json`, figure `fig_superseding.svg`/`.png` by `plot.py`). Evidence review: DEC-20261019-f33f3e, EV-CMFB-e3d1ec; reviews VAL-20261019-1b97f5 and RT-20261019-520123. This is a derived analysis, not an official run: no new trial, no new measurement, no ledger record changed.

== Step 1: the unchanged frozen analysis reproduces the recorded t8

Re-running `analyze.run_analysis` with the frozen constants on the recorded raw results reproduces `RUN-CMFB-2010d3/raw-result.json` leaf for leaf (0 differing values), excluding wall-clock `timings` and the driver's `peak_rss_bytes` process metric. So the harness is deterministic and the recorded t8 is the frozen analysis' output.

== Step 2: contract-text constants (defects D1 and D2)

Two in-process substitutions, nothing on disk changed: *D1* MDE = 3.61 x rms sd / sqrt(n) with no inflation factor (the specification text, lines 166-171 and 471-475; the code multiplies by sqrt(3) x 1.0025 = 1.736); *D2* I10 reference 1.4/sqrt(N) (the specification text; the code uses the superseded occupancy formula, about 0.49/sqrt(N)). All other fields of every table row (T, 95 percent interval, randomization p, Kolmogorov-Smirnov, lag-1, Sidak, member counts) are identical to the recorded values (checked field by field; the 53 changed leaves are MDE, powered flags, Holm p, I10 fields, the added C20 contrasts and slopes, and the official flags).

#figure(image("fig_superseding.svg", width: 100%), caption: [(a) minimum detectable effect, recorded (code) against superseding (contract text), with the 0.25 percent powered threshold. (b) I10 null-spread ratio, recorded against the draft reference and superseding against 1.4/sqrt(N); accepted band [0.75, 1.33]. (c) T with the recorded 95 percent interval, unchanged (hollow markers: C16, not powered; the C16 intervals extend beyond this zoom, see the table). Sources: RUN-CMFB-2010d3 raw-result.json, `superseding_result.json`.])

#text(size: 7.5pt)[
#table(columns: (auto, auto, auto, auto, auto, auto, auto, auto, auto), stroke: 0.3pt, align: center,
  [*Arm*], [*Cell*], [*n*], [*T (%)*], [*95 % interval (%)*], [*MDE (%) rec. / sup.*], [*powered rec. / sup.*], [*Holm p rec. / sup.*], [*I10 ratio rec. / sup.*],
  [FAM], [C16], [4], [-0.1742], [[-0.1742, -0.0340]], [1.332 / 0.767], [no / no], [none / none], [2.560 / 0.878],
  [FAM], [C20], [10], [-0.0296], [[-0.0741, +0.0482]], [0.243 / 0.140], [no / yes], [none / 1.0000], [2.568 / 0.896],
  [FAM], [C24], [13], [-0.0224], [[-0.0381, -0.0060]], [0.065 / 0.037], [yes / yes], [0.0936 / 0.1872], [2.679 / 0.940],
  [N-A], [C16], [8], [-0.0849], [[-0.4046, +0.2630]], [1.318 / 0.759], [no / no], [none / none], [2.393 / 0.815],
  [N-A], [C20], [16], [-0.0085], [[-0.0612, +0.0389]], [0.268 / 0.154], [no / yes], [none / 1.0000], [2.579 / 0.896],
  [N-A], [C24], [16], [-0.0004], [[-0.0237, +0.0267]], [0.063 / 0.037], [yes / yes], [0.9691 / 1.0000], [2.637 / 0.925],
  [N-B], [C16], [8], [-0.0094], [[-0.1862, +0.1661]], [1.537 / 0.885], [no / no], [none / none], [2.470 / 0.842],
  [N-B], [C20], [16], [+0.0102], [[-0.0384, +0.0570]], [0.245 / 0.141], [no / yes], [none / 1.0000], [2.719 / 0.945],
  [N-B], [C24], [16], [+0.0161], [[-0.0012, +0.0346]], [0.057 / 0.033], [yes / yes], [0.1589 / 0.3972], [2.767 / 0.971],
)]

Powered cells: recorded ['C24'], superseding ['C20', 'C24']. Holm family: 3 tests recorded, 6 superseding (C20 and C24). Rejections below delta: none under either. Contrasts at the added cell C20 and at C24 (99 percent intervals, in percent):

#text(size: 7.5pt)[
#table(columns: (auto, auto, auto, auto), stroke: 0.3pt, align: center,
  [*Contrast*], [*Estimate (%)*], [*99 % interval (%)*], [*Excludes 0*],
  [fam_natheta|C20], [-0.0642], [[-0.1291, +0.0440]], [no],
  [fam_natheta|C24], [-0.0001], [[-0.0358, +0.0425]], [no],
  [fam_na|C20], [-0.0211], [[-0.1079, +0.1057]], [no],
  [fam_na|C24], [-0.0220], [[-0.0640, +0.0150]], [no],
  [na_nb|C20], [-0.0187], [[-0.1109, +0.0730]], [no],
  [na_nb|C24], [-0.0165], [[-0.0559, +0.0268]], [no],
)]

== Result

- *Classification:* NULL_AT_RESOLUTION, identical to the recorded one. Growth assessable: False (two powered cells, three needed; slopes not assessable for any arm).
- *Powered set* is {C20, C24} under the contract text, as the validator (VAL M7) and the red team (RT-O2) computed independently.
- *Holm-adjusted p:* FAM C24 0.1872, N-B C24 0.3972, all other tests 1.0. Nothing is rejected; the smallest raw p (0.0312, FAM C24, a deficit) is not detected under the six-test family either.
- *I10:* 0 of 9 arm-cells flagged; ratios 0.815 to 0.971 against 1.4/sqrt(N), inside [0.75, 1.33]. The recorded flag in 9 of 9 cells was an artefact of the reference formula.
- At C20 every 95 percent interval is inside [-0.074, +0.057] percent and at C24 inside [-0.038, +0.035] percent, so the scoped statement of EV-CMFB-e3d1ec is unchanged: no coverage difference above 0.5 percent was observed for the small-x base against 200 matched random bases per member at the tested scope.

== What this does and does not settle

It removes defects D1 and D2 as obstacles: with the frozen text's constants the powered set, Holm family and I10 reading are the ones the contract promised, and the recorded classification is stable under both readings. It does not turn the single pass into a replication, does not test the CM structure (endomorphism chain, isogeny pullback, canonical lift, signed convention), does not give a growth reading, and makes no cost or ECDLP claim. No improvement over the random-base baseline was measured (the base equals it within 0.04 percent at C24). Earlier reports: `reports/run-20261019T0541Z/` (run report, recorded values) and `reports/review-DEC-20261019-f33f3e/` (decision report). The decision report's graph is not refreshed; it plots recorded values, which this analysis leaves unchanged.

== Next

The decision record's next action 2 (a scoped `support` decision once this analysis agrees) now has its input. It is a Coordinator decision (a new DEC- record), and the companion correction record for D1/D2 is a Coordinator ledger record; neither is written here. Open items unchanged: the eight run manifests lack `result.certificate` (validator errors), the independence check fails for the review round, and `validate` CI is red on `main`.
