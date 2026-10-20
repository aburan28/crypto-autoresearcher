#set page(paper: "us-letter", margin: 0.54in)
#set text(font: "New Computer Modern", size: 8.6pt)
#set par(leading: 0.43em)

= Prime63 solver panel: recorded execution

EXP-ICPERF-891f7f • H-ICPERF-05021b • GOAL-ICPERF-e6b6a4 \
RUN-ICPERF-7ed866 • 2026-10-18 00:04 UTC

This report describes the frozen trial's outputs. It makes no scientific-status decision or factor-base performance claim.

== Requested run and provenance

The approved panel requested one supervisor trial of 27 cells: six planted positive controls at m=2 and m=8, then 21 natural same-point cells covering three B=475 bases (coset, random, small-x) at m=2..8. Each cell had a 300-second wall cap, 8 GiB sampled process-tree RSS and scratch caps, one worker, and a 64-model guard. The four-hour panel cap was not reached. Each natural arity's public target was fixed and shared by the three arms. Inputs and any seeds were already frozen in the source bundles; no new selection was made during this run.

The macOS/Darwin trial launched from code commit `9ce4da79fbff15c7f3130010c442103d0213d6c0` with a dirty worktree reported by the panel receipt (the run directory was being produced). The plan SHA256 was `24a1443ef683ae64d47878c189fbcd45eabc83bc949c1a3229d4c2b6591f1978`. The bound Sage binary SHA256 was `b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1`. The exact command and source/input digests are in `command.txt`, `environment.json`, and `panel/receipt.json` beside the run record. The host name and CPU model were not recorded in those receipts.

#figure(image("peak-rss.svg", width: 88%), caption: [RUN-ICPERF-7ed866. Sampled peak process-tree RSS for the six planted controls, one attempt per cell. GiB is the recorded byte count divided by 2³⁰. Every plotted cell reached its 300-second wall cap without a response.])

== Observed terminal states

The runner attempted 7 of 27 cells. The six planted controls each ended `timeout_censored` without a solver response or certificate. Recorded wall seconds, in schedule order, were coset m2 300.288, coset m8 300.422, random m2 301.267, random m8 300.059, small-x m2 300.312, and small-x m8 300.084. These are individually recorded elapsed values, not solve times or successful relation costs. Their sampled peak RSS values are in the graph; no cell hit the 8 GiB cap. The natural coset m2 cell stopped after 2.268 wall seconds with `infrastructure_monitor_error:RuntimeError:rss_monitor_unavailable_for_live_child` and no response. The remaining 20 natural cells were recorded as unattempted with reason `failed_independent_control_or_execution`.

The raw producer wrote `attempted=7`, `unattempted=20` and a `manifest.yaml` marked `completed` for artifact production. The independent checker exited 1 with `ValueError: missing response without bounded censoring` on the monitor-error cell. The supervisor receipt therefore records `status=invalid_output`, `check_returncode=1`, `published=false`, and the selector records `needs_reconciliation`. One supervisor trial was requested; zero output-validated trials completed. The runner returned exit code 0 before the checker failed. No cell response, full-point certificate, verified relation, rank increment, or target solve was produced.

The panel receipt reports 1815.916 wall seconds from 00:04:43.473062 to 00:34:59.398786 UTC. CPU-user and CPU-system seconds for each attempted cell, sampled memory, scratch and free-space minima, and exact per-cell start/stop times are retained in `raw-result.json` and the sealed `panel/receipt.json`. The supervisor's own start and finish times were 00:04:28.791695 and 00:35:04.238420 UTC. Execution-receipt SHA256: `1dc03aed73728f57d2fda8b62a787b29de7fa7d994cc99341012a52798748826`.

== Measurement boundary

These six time caps are censored controls; they do not establish an unsatisfiable system or a failed factor base. The natural cell's stop is an instrument failure. Solver degree, natural relation yield, useful rank, linear algebra, target work, complete cold-start IC cost, matched rho and a Bernstein–Lange setup-excluded comparison remain unmeasured. The run files preserve the first attempt for a separately authorized, fresh-ID continuation.
