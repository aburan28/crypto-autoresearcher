#set page(width: 8.5in, height: 11in, margin: 0.8in)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")

#align(center)[#text(18pt, weight: "bold")[EXP-PFDR-2d36f9 break-even growth ladder]]
#align(center)[Run report --- 2026-10-31]

#v(0.5em)
#table(
  columns: (1.4in, 3.0in),
  [Experiment], [EXP-PFDR-2d36f9],
  [Hypothesis], [H-PFDR-ed7ccf],
  [Goal], [GOAL-PFDR-fd09e0],
  [Run IDs], [RUN-PFDR-f86a2a, b507a1, 601709, b126f3, 97fa6c, 8cb633, 73276d],
  [Code commit], [41020cfad0 (clean)],
  [Reading], [#text(weight: "bold")[O-INVALID]],
)

== What ran

Seven planned trials, all with `output_validated` execution receipts: selftest, the descriptive
reanalysis of EXP-PFDR-ca5e01, pilot, census-main (14,571 jobs), analyze-main, census-rep
(no ALIVE lines, so it records an empty result and stops), and analyze-final. The selftest
passed 126 kernel-vs-brute checks, 9 near-2^32 key checks, 6 `plant_internal` checks and 12
order certifications including 8 at 32 bits. Census-main recorded 0 failed-infrastructure jobs.

== Recorded structured-line values

The five-rung slope `delta_hat` and the frozen class are recorded below. Three of the six
lines are invalid because the pilot's mean null count at bits 16 did not reach the frozen
2500-coincidence target; no class is assigned to them.

#figure(
  image("graph.svg", width: 100%),
  caption: [Recorded kappa per rung for the six structured lines (RUN-PFDR-b126f3, RUN-PFDR-73276d). Points are the measured mean kappa at each rung; lines connect recorded values only. Classes are the frozen analysis labels.],
)

#table(
  columns: (0.6in, 0.5in, 0.9in, 1.0in, 3.3in),
  table.header([theta], [d], [class], [delta_hat], [reason]),
  [0.3], [1], [invalid], [-0.012502], [b16-t0.30-d1 M 2333.0 < 2500],
  [0.3], [2], [invalid], [0.004153], [b16-t0.30-d2 M 2333.0 < 2500],
  [0.3], [3], [invalid], [-0.000893], [b16-t0.30-d3 M 2333.0 < 2500],
  [0.35], [1], [SUB-BE], [-0.009795], [valid],
  [0.35], [2], [SUB-BE], [-0.004440], [valid],
  [0.35], [3], [SUB-BE], [0.005368], [valid],
)

== Recorded controls

#table(
  columns: (0.6in, 0.6in, 1.0in, 1.4in),
  table.header([control], [pass], [entries], [design and slope ok]),
  [C3], [False], [8], [4],
  [C4], [False], [2], [0],
  [C5], [False], [6], [0],
  [C6], [False], [0], [0],
)

Calibration recorded n = 30, mean = -0.149520, sd = 0.659750, pass = False.
The analysis therefore records `O-INVALID`: fewer than five of six structured lines are valid
and the blocking calibration/controls do not pass. This report describes the recorded run; it
does not decide support, weakening, or the fate of H-PFDR-ed7ccf.

== Missing and derived values

The raw census job file is stored in the artifact store as `main-jobs.jsonl.gz` with a
`.artifacts.json` manifest; the report graphs only values recorded in `analysis.json`.
`delta_hat` is the frozen ordinary-least-squares slope of log2 kappa on the rung mean log2 N;
the bootstrap interval is recorded in `analysis.json`, and is not recomputed here.
