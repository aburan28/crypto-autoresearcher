# Prime63 panel monitor and positive-control feasibility remain unresolved

- **Status:** `open`
- **Kind:** implementation gap; bounded empirical feasibility limit. No mathematical obstruction is claimed.
- **Affected work:** [EXP-ICPERF-891f7f](../experiments/EXP-ICPERF-891f7f/specification.yaml), [RUN-ICPERF-7ed866](../experiments/EXP-ICPERF-891f7f/runs/RUN-ICPERF-7ed866/execution-receipt.json), [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [full-width arity-grid problem](full-width-ic-arity-grid-unmeasured.md), [DEC-20261018-eb6e00](../ledger/decisions/DEC-20261018-eb6e00.yaml).
- **Next action owner:** Executor for a source-level monitor repair and bounded positive-control diagnostic design; Coordinator for a separately frozen, approvable successor before any scientific trial.
- **Last updated:** 2026-10-18

## Problem

The approved 63-bit prime-field B=475 coset, random, and small-x panel cannot provide a checked m=2..8 solver-to-certificate comparison because the first natural cell lost process-tree RSS monitoring and the checker rejected its no-response state, while all six planted positive controls reached their individual 300-second caps without a response. These are two distinct gaps: monitor reliability and bounded solver feasibility. Repairing the monitor alone would leave the six censored controls unexplained. The 21 natural cells were scheduled, but only the first was attempted; the other 20 have no solver measurement.

The requested conclusion remains a complete, verified end-to-end index-calculus comparison at subgroup order 2^50..2^63 across prime, Koblitz, and ordinary binary curves and m=2..8. This panel itself was a prime-field feasibility pilot and could not establish complete IC cost even if all 27 cells had returned certificates.

## Evidence and uncertainty

- **Observed:** [The sealed supervisor receipt](../experiments/EXP-ICPERF-891f7f/runs/RUN-ICPERF-7ed866/execution-receipt.json) reports `status=invalid_output`, `check_returncode=1`, `published=false` and plan SHA-256 `24a1443ef683ae64d47878c189fbcd45eabc83bc949c1a3229d4c2b6591f1978`; its own SHA-256 is `1dc03aed73728f57d2fda8b62a787b29de7fa7d994cc99341012a52798748826`. [Raw results](../experiments/EXP-ICPERF-891f7f/runs/RUN-ICPERF-7ed866/raw-result.json), SHA-256 `ad14331e985cb703cbc864927e77772619b1e783c158a9263c95995c1e0af07f`, record six planted `timeout_censored` cells (coset, random and small-x at m=2 and m=8), one `natural-coset-m2` `infrastructure_monitor_error:RuntimeError:rss_monitor_unavailable_for_live_child` after 2.268 seconds, and 20 unattempted natural cells. The [run report and graph](../experiments/EXP-ICPERF-891f7f/reports/run-20261018T0004Z/report.typ) and [PDF](../experiments/EXP-ICPERF-891f7f/reports/run-20261018T0004Z/report.pdf) preserve the execution boundary.
- **Observed implementation:** In the frozen [launcher](../research/icperf_prime63_inflight_admission_20261017/execute.py), `supervise` samples a `psutil` process tree and raises `rss_monitor_unavailable_for_live_child` when a process disappears or becomes a zombie while `child.poll()` still returns `None`; it then terminates that child. The frozen [checker](../research/icperf_prime63_inflight_admission_20261017/check.py) accepts absent responses only for enumerated bounded-censor states, so this monitor-error cell caused `ValueError: missing response without bounded censoring`. That failure is appropriately fail-closed, but the process-lifecycle cause has not been independently isolated.
- **Derived or proved:** The six planted controls' archived satisfying inputs prevent interpreting their timeouts as proof of unsatisfiability. The recorded 300-second limits establish only that no control certificate was returned within each bounded call. No degree of regularity, natural relation yield, useful rank, linear algebra, target cost, complete cold-start `S`, or matched rho value was measured in this run.
- **Suspected explanation:** A transient child-process exit or zombie race may explain the RSS monitor exception. The six timeouts may reflect expensive Gröbner work, stalled preparation, or process/supervisor behavior; the current artifacts do not distinguish those explanations.
- **Missing capability:** A race-safe, fail-closed process-tree monitor with checked resource-accounting semantics; phase-level observations and an independently checked certificate from a small, prospectively frozen positive-control diagnostic, or an explicit bounded censor result showing where work stopped.
- **What this evidence does not establish:** It does not rank the three bases, refute a decomposition, show a degree-of-regularity reduction, or supply any end-to-end speedup. The unattempted cells are missing observations, not zero yield.

## What would unblock it

- [x] An Executor implementation makes the RSS monitor race safe while retaining a fail-closed 8 GiB process-tree cap. Tests cover normal exit, abrupt exit, zombie/NoSuchProcess during sampling, a genuinely live unreadable child, and memory-cap termination. Every path must produce a stable terminal classification and preserve raw stdout, stderr, request, response when present, and exact hashes; an unmonitorable live process must not be silently counted as zero RSS.
- [ ] A separate Coordinator-approved, fresh-ID diagnostic with frozen source, inputs, controls, resource caps, checker, and archive demonstrates where at least one m=2 planted positive spends time and either returns an independently checked full-point certificate or records a justified bounded censor with phase trace. The diagnostic must preserve the six prior 300-second censored outcomes and include a monitor fault-injection control.

The first condition repairs instrument classification. The second distinguishes solver cost from preparation or monitor behavior. Meeting both would permit a rational next solver strategy and a later m=2..8 panel; it would still leave natural yield, rank, full IC costs, Koblitz and ordinary-binary rows, and matched rho open.

## Next discriminating step

- **Action or proof obligation:** Implement and test a race-safe monitor and phase telemetry, then prepare a small positive-control diagnostic packet for Coordinator preapproval. The implementation task makes no scientific run and does not revise the frozen EXP-ICPERF-891f7f bytes.
- **Inputs and controls:** Reuse the archived 63-bit curve, B=475 point sets, exact planted m=2 systems and witnesses, and sealed run for regression. Include normal/abrupt/zombie/live-unreadable process tests and a changed-witness checker rejection. Compare phase accounting across the three arms only under a later common frozen diagnostic; keep m=8 and direct S8/S9 formulation work separate.
- **Execution limits and stop condition:** Any later diagnostic must have fixed sample count, per-call wall/RSS/scratch caps and an exact stopping rule in a new approved protocol. The existing 27-cell plan and six 300-second outcomes are historical; do not retry within RUN-ICPERF-7ed866.
- **Outcomes and next actions:** A checked positive m=2 certificate supports extending an arity-specific solver protocol; a phase-traced bounded timeout redirects solver/formulation design; a monitor fault blocks interpretation until repaired; a contradictory accepted root triggers independent backend/encoding review. None of these alone selects a factor base or completes the end-to-end comparison.
- **Recheck trigger:** Source repair and its fault-injection tests are archived, followed by an approvable diagnostic packet.

## Resolution and history

- 2026-10-18: Opened from the sealed RUN-ICPERF-7ed866 and additive DEC-20261018-eb6e00. Preserve both the six censored positives and the natural-cell infrastructure fault; neither is rewritten as a base result. Unresolved.
- 2026-10-18: First unblock condition met. TASK-20261018-3b41b1 passed 10/10 synthetic monitor and phase cases with zero scientific trials. The content-at-commit snapshot TASK-20261018-a2cf7c (commit 1e1df4ea164cb010cdbcbc5c29ba00ac30fdc7b7) was verified by DEC-20261018-1e362f, and BATCH-4379b2 is closed. The second condition (an approved, archived m=2 diagnostic) remains open: a preapproval probe on preview bytes reports approvable false because the diagnostic launcher, request manifest and independent checker are unimplemented. Unresolved.
