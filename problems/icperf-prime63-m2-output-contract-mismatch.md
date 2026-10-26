# Prime63 m=2 diagnostic launcher and supervisor disagree on required outputs

- **Status:** `open`
- **Kind:** implementation gap in the trial output contract; not a mathematical obstruction.
- **Affected work:** [EXP-ICPERF-515ae3](../experiments/EXP-ICPERF-515ae3/specification.yaml), [RUN-ICPERF-eb0d88](../experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/execution-receipt.json), [run report](../experiments/EXP-ICPERF-515ae3/reports/run-20261019T2113Z/report.md), [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), and the separate [solver-feasibility problem](icperf-prime63-monitor-and-positive-controls.md).
- **Next action owner:** Coordinator for a prospective, fresh-ID correction contract; Executor for its implementation; independent checker for acceptance.
- **Last updated:** 2026-10-19

## Problem

The attempted 63-bit prime-field, B=475, m=2 three-arm diagnostic cannot satisfy its frozen supervisor output check because its [trial plan](../experiments/EXP-ICPERF-515ae3/trial-plan.json) requires top-level `manifest.yaml` and `raw-result.json`, while the bound [launcher](../research/icperf_prime63_m2_diagnostic_integration_20261018/execute.py) writes `diagnostic/receipt.json` and `diagnostic/raw.tar.gz` without those two top-level files. The independent checker can report `integrity_pass` for its own raw diagnostic, yet the standard supervisor correctly records `invalid_output` and `needs_reconciliation`. This mismatch prevents a validated trial record. It does not explain or erase the three separately recorded 600-second solver censors.

The exact run used prime `p = 9223372021248595841`, subgroup order `r = 9223372018953067627`, one 475-point factor base per arm (coset, random, small-x), and separately planted targets. It was a bounded certificate diagnostic, not a complete ECDLP pipeline.

## Evidence and uncertainty

- **Observed:** The immutable [execution receipt](../experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/execution-receipt.json) has `returncode: 0`, `check_returncode: 0`, `status: invalid_output`, and `detail: missing/empty required artifact: manifest.yaml`. The run directory also lacks `raw-result.json`. [Checker output](../experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/check.stdout.log) reports `integrity_pass`, `positive_censored: 3`, and `positive_verified: 0`; [raw diagnostic receipt](../experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/diagnostic/receipt.json) records three `timeout_censored` positive calls and a correctly injected monitor-null fault. The frozen plan SHA-256 is `08f32f02a191dfd16f5342540716a327da73f5091528bac07cf5ee77cdb7cbc9`; the launcher SHA-256 is `4cba7cfb3238b656db29510cbc2ba315e665c81aee491c28960187d0c34cd92c`. Run commit `1f857554d6` and report commit `fc07c3dd27` are published in PR #2429.
- **Observed custody mismatch:** The [write-once executor release](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/claims/TASK-20261019-904fbf.1.release.json) records `outcome: failed`, `was_expired: false` and hashes only the existing execution receipt. Yet `python3 tools/research_dispatch.py coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/dispatch_queue.json --ready-only` still offers `TASK-20261019-904fbf` as ready because the [original queue](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/dispatch_queue.json) remains `queued`. Its snapshot task `TASK-20261019-2c3c6a` declares the absent `manifest.yaml` and `raw-result.json`, so that task cannot truthfully complete against the preserved run. This is an administrative duplicate-dispatch hazard, not a new scientific observation.
- **Derived or proved:** The plan's required-artifact list and the launcher's actual output paths disagree on these exact frozen bytes. The supervisor's `invalid_output` classification follows its declared output check; the checker success proves only the checker's narrower raw-integrity predicates.
- **Suspected explanation:** The launcher and checker were integrated against the diagnostic subdirectory but the prospective plan retained the standard top-level artifact names. This is a code-path explanation to verify in a no-science engineering fixture, not a claim about solver behavior.
- **Missing capability:** A future plan/launcher/checker trio with one consistent, hash-bound required-output schema and a standard-supervisor terminal fixture that validates both successful and censored outputs.
- **What this evidence does not establish:** It does not establish an unsatisfiable polynomial system, an inferior factor base, a certificate, natural relation yield, useful rank, complete IC time, or a matched-rho gap. The current run and its missing outputs remain immutable.

## What would unblock it

- [ ] Publish an additive, Coordinator-authorized queue disposition that makes the original executor terminal `failed` for selection without editing its frozen queue or relaunching it. Use a fresh custody task and archive scope that hash every existing run artifact and the failed release, explicitly inventory both absent paths, and retain the supervisor/checker scope difference. Independently review that scoped custody before a ledger decision; never complete the original full-output snapshot task against missing bytes.
- [ ] Freeze a fresh-ID successor with exact source and input hashes, an approved plan, and a documented mapping from each required top-level artifact to the bytes the launcher writes, including censored and successful cell outcomes. `experiment_preapproval.py --packet` must report `approvable: true` for those prospective bytes before approval.
- [ ] Under the standard supervisor, a no-science fixture exercises a censored cell and a canned positive response, and each terminal run produces every declared required artifact with hashes and an independent checker result. Negative controls reject a missing, empty, changed, or unlisted artifact without silently adding a replacement file to the historical run.
- [ ] After a separate Coordinator approval and fresh claim, the successor selector reports `ready` before a scientific launch; an actual successor trial can then be recorded as `output_validated` if its declared outputs are present. A censored solver result must stay censored even when its artifact contract passes.

These conditions repair the output contract for prospective trials. They do not produce a full-point certificate, settle the 600-second solver bottleneck, or demonstrate end-to-end speedup.

## Next discriminating step

- **Action or proof obligation:** Implement and archive a fresh-ID engineering fixture and output-contract correction, then have an independent checker compare the frozen plan's required paths with the files actually emitted in both terminal classes.
- **Inputs and controls:** Use the exact archived three request hashes and receipt as regression inputs; inject one missing required file, one changed digest, one censored response, and one canned positive response. Keep the current run untouched.
- **Execution limits and stop condition:** The first step is bounded engineering only: no Sage solver call or repeated scientific trial. A later scientific execution needs its own approved fixed wall, memory, sample and stopping rules.
- **Outcomes and next actions:** If both terminal fixtures validate and all negative controls reject, the Coordinator can complete a prospective runnable protocol. A false acceptance or missing artifact requires another correction. A fixture crash is an infrastructure result. A future solver censor still redirects solver/formulation work and cannot rank bases.
- **Recheck trigger:** A committed successor source/plan/checker bundle with a passing standard-supervisor fixture and a matching preapproval packet.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it. The administrative queue correction is a prerequisite to safe dispatch; it does not validate this attempt or approve a successor.

## Resolution and history

- 2026-10-19: Opened from published RUN-ICPERF-eb0d88. The checker and supervisor results are preserved together; the frozen run is not repaired in place. Unresolved.
- 2026-10-19: Added the failed-release versus ready-selector mismatch and the missing-file snapshot obstruction from the published batch records. No queue, run, research status, or scientific evidence was changed by this problem update.
