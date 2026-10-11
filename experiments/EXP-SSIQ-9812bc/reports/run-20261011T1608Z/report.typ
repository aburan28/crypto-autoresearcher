#set page(margin: (top: 0.55in, bottom: 0.55in, left: 0.65in, right: 0.65in))
#set text(size: 9.5pt)
#set heading(numbering: none)

#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-SSIQ-9812bc run report]
  #v(4pt)
  Crypto Autoresearcher · 2026-10-11
]

#block(fill: luma(242), inset: 8pt, radius: 3pt)[
  *Observation-only record.* This report describes the single validated
  execution and its recorded finite-domain arithmetic. It does not promote,
  weaken, or review a hypothesis.
]

= Identity and execution

#table(
  columns: (1.3fr, 3.7fr),
  inset: 3pt,
  stroke: 0.3pt + luma(190),
  [*Experiment*], [#raw("EXP-SSIQ-9812bc")],
  [*Hypothesis*], [#raw("H-SSIQ-c82b7d")],
  [*Goal*], [#raw("GOAL-SSIQ-001")],
  [*Decision*], [#raw("DEC-20261007-3e731d")],
  [*Task*], [#raw("TASK-20261011-30cb51")],
  [*Run*], [#raw("RUN-SSIQ-ee5cdb")],
  [*Plan SHA-256*], [#raw("6c291c3bcda53022a53384cd4d59ceafefbc3854127369285fe81a8133641bef")],
  [*Receipt*], [#raw("output_validated; producer/checker return codes 0/0")],
)

The supervisor command was #raw("python3 tools/experiment_execution.py run --plan experiments/EXP-SSIQ-9812bc/trial-plan-v2.json --owner executor-ssiq-9812bc --epoch 1"). It ran in a network-disabled Linux container with Python 3.11.17, Linux 7.0.12-linuxkit-aarch64, the declared 512 MiB address-space ceiling, and a 120 second watchdog. The execution checkout commit recorded in the receipt is #raw("5639a985566224fe9d1dc09f2034992bf1a4d4e8").

The source hashes recorded by the supervisor are #raw("run.py=f54566d695b757068b35b79176f520085a157d3e24d3c8d8e109e1d9b5608100") and #raw("check.py=d51391dc05be8278bf1da207b349f7756079afa102aa018c262a20f80fcf943f"). The producer and checker logs are empty; the supervisor recorded return code 0 for both.

= Declared inputs and recorded values

The driver evaluated the two frozen curves over #raw("F_361") using basis #raw("z^2 - 2"). It recorded #raw("m_a=37"), #raw("m_n=45"), and #raw("gap=-8"). The selected reading row is #raw("negative_gap"); #raw("checks_pass=true") and #raw("attack_claimed=false"). Both histograms contain 19 bins, and both recorded totals are #raw("n_a=n_n=399").

#figure(
  image("histogram-plot.svg", width: 100%),
  caption: [Recorded histogram counts for the two frozen curves in #raw("RUN-SSIQ-ee5cdb"). The bars are values stored in #raw("raw-result.json"); the plot adds no samples or recomputation. The editable graph source is #raw("plot_graph.py"), with vector renderings in #raw("histogram-plot.svg") and #raw("histogram-plot.pdf").],
)

= Controls and validation boundary

The run's recorded arithmetic checks passed, and the declared checker exited successfully. The checker imports the producer's #raw("build_report") and #raw("reading_row") functions, so it is a consistency check against altered output files rather than an independent mathematical re-derivation. The producer also writes a minimal #raw("manifest.yaml") with experiment/run/command/reading fields; it is not the repository's canonical run-manifest schema. These are limitations of the frozen implementation and are recorded here without changing the run output.

= Artifacts and interpretation boundary

The complete run directory is #raw("experiments/EXP-SSIQ-9812bc/runs/RUN-SSIQ-ee5cdb/"). Its execution receipt records the artifact SHA-256 map, authority, plan hash, timestamps, and checker return code. The result is an observation on the declared finite input and does not by itself change hypothesis status or establish a broader cost or security claim.
