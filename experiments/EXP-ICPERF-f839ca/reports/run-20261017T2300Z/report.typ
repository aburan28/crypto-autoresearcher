#set page(paper: "us-letter", margin: 0.64in)
#set text(font: "New Computer Modern", size: 9.5pt)
#set par(leading: 0.56em)

= Prime63 panel launch: infrastructure observation

EXP-ICPERF-f839ca • H-ICPERF-05021b • GOAL-ICPERF-e6b6a4  \
RUN-ICPERF-3a849c • 2026-10-17 23:00 UTC

This report describes one frozen trial's output. It makes no scientific
status decision or factor-base performance claim.

== Requested boundary

One trial was requested on arm64 macOS from clean code commit
`130c1559cb6f73857fef1f2736d9826f2fa5c691`, plan SHA256
`6b6284d482527985821890a66fdac96aff87be5c466380aa75f5a9bc1df1a715`.
The launch used `tools/experiment_execution.py run` with owner
`executor-prime63-science` and epoch 1 through Conductor. The frozen panel
contains six planted positives and 21 natural cells across three B=475
prepared bases at m=2..8. Limits: 300 seconds, 8 GiB sampled RSS and 8 GiB
scratch per cell; one worker, 64-model guard and four-hour panel ceiling.

#figure(image("diagram.svg", width: 96%), caption: [Observed run boundary for
RUN-ICPERF-3a849c. Zero cells reached the solver.])

== Observed output

The supervisor wrote launch, command, environment, logs and execution receipt.
Its recorded status is `infrastructure_error`, driver return code 1, no
checker return code. The driver stopped at the `psutil` import in
`execute.create_panel` with `ModuleNotFoundError`. The import precedes cell
generation and Sage work. No raw-result, manifest, panel or cell response was
created. Requested trials: 1; completed: 0; infrastructure failures: 1;
timeouts: 0. All 27 cells were unattempted.

The receipt timestamps are 23:00:20.885149 and 23:00:24.190596 UTC. Their
difference is *3.305447 seconds, derived*. CPU time, process-tree RSS,
scratch, solver degree, certificates and relation counts are unmeasured.
Receipt SHA256: `80595df1532ca6de4efc260c1a520621bb7b2621d01fe5d75cae41d43d3ffb8d`.

There are fewer than two comparable solver values, so the visual is an
execution diagram. Useful rank, linear algebra, target work, matched rho,
Bernstein–Lange comparison and complete index-calculus cost remain unmeasured.
