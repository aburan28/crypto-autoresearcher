#set page(margin: (top: 0.55in, bottom: 0.55in, left: 0.65in, right: 0.65in))
#set text(size: 9.5pt)
#set heading(numbering: none)

#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-SSIQ-975f7e run report]
  #v(4pt)
  Crypto Autoresearcher · 2026-10-11
]

#block(fill: luma(242), inset: 8pt, radius: 3pt)[
  *Observation-only record.* This report describes the single validated
  execution and its recorded arithmetic. It does not promote, weaken, or
  review a hypothesis. The run used the fixed finite domain declared by the
  approved specification.
]

= Identity and execution

#table(
  columns: (1.3fr, 3.7fr),
  inset: 3pt,
  stroke: 0.3pt + luma(190),
  [*Experiment*], [#raw("EXP-SSIQ-975f7e")],
  [*Hypothesis*], [#raw("H-SSIQ-85f1f1")],
  [*Goal*], [#raw("GOAL-SSIQ-001")],
  [*Decision*], [#raw("DEC-20261010-d6e558")],
  [*Task*], [#raw("TASK-20261011-9b3693")],
  [*Run*], [#raw("RUN-SSIQ-be0b59")],
  [*Plan SHA-256*], [#raw("ee538b6482e02aedbbe0ce5dd9c52dcf140a1740caf7c3634266649488817909")],
  [*Receipt*], [#raw("output_validated; producer/checker return codes 0/0")],
)

The supervisor command was #raw("python3 tools/experiment_execution.py run --plan experiments/EXP-SSIQ-975f7e/trial-plan-v5.json --owner executor-ssiq-975f7e-v5 --epoch 1"). It ran in a network-disabled Linux container with Python 3.11.17, Linux 7.0.12-linuxkit-aarch64, the declared 128 MiB address-space ceiling, and a 60 second watchdog. The run receipt's execution checkout commit is #raw("ff9b34232ad7112973641564290d3e60f735cc35"); the thin checkout was assembled from the published branch after claim #raw("b08667305b").

The experiment source hashes recorded by the supervisor are #raw("run.py=1ec6e0c35ed451e7a142b5ef7c5baf0479579a5e75bc9f2e7846b2c6381a88f9") and #raw("check.py=b574781b55cb0b00515363d5290e7f3c3b32f26fdf89f2bb5675bee62b711e94"). The producer reported 0.000099709 wall-clock seconds for its arithmetic section; no CPU time or uncertainty estimate was recorded.

= Declared inputs and recorded values

The driver scanned every integer from 31 through 180 inclusive (150 candidate integers), retained factors from $2, 3, 5, 7$, and used $X=30$. The run recorded 41 eligible rows and #raw("match_count=0"). The raw artifact contains all 41 ordered rows at #raw("experiments/EXP-SSIQ-975f7e/runs/RUN-SSIQ-be0b59/raw-result.json"); the producer manifest and all supervisor logs are in the same run directory. The recorded qualifying-row list is empty. This is a measured value on the declared finite input, not an extrapolation.

#figure(
  image("prefix-plot.svg", width: 100%),
  caption: [Recorded ascending and descending prefix products for the 41 eligible rows in #raw("RUN-SSIQ-be0b59"). Points are the values stored in #raw("raw-result.json"); the plot adds no samples or recomputation. The editable graph source is #raw("plot_graph.py") and its vector rendering is #raw("prefix-plot.svg").],
)

= Controls and certificate state

The supervisor's independent checker returned 0. The six recorded controls were all true: all degrees were in range; all retained factors were allowed; all products reconstructed their degree; 11 was excluded; 30 was excluded from the scored domain; and the 32-prefix equality held. The run manifest leaves the certificate as #raw("kind: none, verified: false"); the checker receipt is the validation record for this execution, not a broader claim.

= Artifacts and limitations

The complete run directory is #raw("experiments/EXP-SSIQ-975f7e/runs/RUN-SSIQ-be0b59/"). Its supervisor receipt records the exact artifact SHA-256 map, authority, plan hash, start and finish timestamps, and checker return code. No seed was declared because the scan is deterministic. Earlier custody attempts are preserved separately under #raw("RUN-SSIQ-54cfe2") and #raw("RUN-SSIQ-f80485"); they were infrastructure failures and are not combined with this validated run.
