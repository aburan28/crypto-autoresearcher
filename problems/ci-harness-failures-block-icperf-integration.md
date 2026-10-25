# Harness CI failures block the prime63 integration PR

- **Status:** `open`
- **Kind:** repository CI implementation and dependency gaps; an unresolved set of test failures. No cryptanalytic obstruction is asserted.
- **Affected work:** [PR #2395](https://github.com/aburan28/crypto-autoresearcher/pull/2395), [GOAL-ICPERF-e6b6a4](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml), [prime63 diagnostic integration](../research/icperf_prime63_m2_diagnostic_integration_20261018/report.md), and the separate [merge-enforcement problem](pr-merge-checks-not-enforced.md).
- **Related delivery obstruction:** [GitHub Actions jobs remain queued without runner assignment](github-actions-jobs-queued-without-runners.md), so later current-head checks have not yet exercised the repaired source. The prior completed shard failures remain real and separate.
- **Next action owner:** PR author for check triage and fixes within the PR; maintainers of unrelated failing tests for their own source and fixtures.
- **Last updated:** 2026-10-18.

## Problem

PR #2395 cannot be merged under the repository's current-head all-applicable-check rule because four `harness-tests` shards failed on head `fa209de5a9bf0733d8d2c615b776eddc6214cf51`. The previously broken `changes` preflight had prevented those shards from running on `main`, so this is the first observed full gate for this PR; a passing comparison on the same source does not exist. The required `progress-fidelity` check and the `changes`, merge-hygiene, both runtime-regression, ledger, and static checks succeeded on that head. The later head `b8257585a1` corrects the audit-contract test regression caused by moving rules to a linked topic document; its current-head checks must be assessed separately. The failures block delivery of engineering source. They do not classify any solver call or factor-base result.

## Evidence and uncertainty

- **Observed:** [Shard 1](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39092850807/job/117573091194) reported seven `test_index_calculus_wide_tails.py` subprocess build failures, two pre-existing run-supersession registry assertion failures, and audit-contract and duplicate-instruction assertions. The two instruction assertions were fixed on head `b8257585a1`; local `python3 -m pytest tools/test_audit_curve_skill.py tools/test_instruction_uniqueness.py -q` passed 13 tests. The wide-tail subprocess logs were written to runner temporary paths and are not present in the PR artifacts, so their exact process exit cause is unknown from the Actions log.
- **Observed:** [Shard 2](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39092850807/job/117573091221) failed because `tests/test_p192_wcm_role2_interface.py` reads `experiments/EXP-SCURVE-1a8daf/runs/.gitkeep` and one archived verifier receipt omitted by sparse checkout. The sparse guard named those exact paths and recommends the full-checkout routing list.
- **Observed:** [Shard 3](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39092850807/job/117573091149) failed its sparse guard on `inputs/refs/experiments/ecdlp_prime_field`. Attribution in that log is `?`; the exact importing test remains to be identified. `tools/port_autolab_experiments.py` probes this path when resolving its source, but the log alone does not bind the caller.
- **Observed:** [Shard 4](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39092850807/job/117573091178) failed lattice tests because `fpylll` was unavailable, and separately failed campaign-autopilot, inference-policy, and newest-experiment assertions. The installed CI extras include `icperf-sat` after the first repair but do not include `fpylll`.
- **Observed, comparison limit:** [The previous `main` validation run](https://github.com/aburan28/crypto-autoresearcher/actions/runs/39089840512) failed at `Require a complete CI scope decision` before checkout and tests. It cannot establish whether the later failures already existed on a fully exercising `main` run.
- **Derived or proved:** None of these CI observations changes the accepted scientific scope of the nine-file integration or certifies a solver outcome.
- **Suspected explanation:** Several dependencies and sparse-routing entries appear absent from CI; the older registry and selector assertions may reflect source/test drift. Each requires a focused replay or fixture inspection before a code change.
- **Missing capability:** A successful current-head validation of every applicable shard without bypassing or weakening checks, plus retained failure output sufficient to diagnose the wide-tail subprocess.
- **What this evidence does not establish:** It does not prove the failing tests are irrelevant, that a full-checkout run would pass, or that a non-required GitHub context may be ignored under the repository's all-applicable-check rule.

## What would unblock it

- [ ] Run the changed audit-contract tests and instruction budget on the final head, preserving every moved rule and its links.
- [ ] Route tests that require archived paths to a full checkout or otherwise make the required fixture available, and show the sparse guard passes without disabling it.
- [ ] Install and pin the actual optional dependencies needed by the executed wide-tail and lattice tests, or repair the tests to use a valid declared backend; retain and inspect the wide-tail subprocess logs before assigning its cause.
- [ ] Resolve the run-supersession and campaign/inference/selector assertion failures through additive record corrections or justified source/test repairs, preserving immutable run records.
- [ ] Show all applicable checks successful or legitimately skipped on the exact final PR head, then confirm a two-parent merge commit under the expected-head guard.

Meeting these conditions would unblock this PR's delivery and verify its CI path. It would not measure prime63 solver feasibility, improve an index-calculus factor base, or complete the requested end-to-end comparison.

## Next discriminating step

- **Action or proof obligation:** On the current head, run the focused failing modules with the same CI dependencies and checkout shape; inspect the wide-tail `run-stderr.log` and the exact run-supersession fixtures. Make one scoped fix per demonstrated cause and rerun the complete PR gate on the new head.
- **Inputs and controls:** Preserve head `fa209de5a9`, its four job logs, the current code and `main` at `f279a4918cdc41885682b40de1b8e5150035242b`; compare full versus sparse checkout for the named path reads, and compare declared versus installed optional extras.
- **Execution limits and stop condition:** Keep the existing CI time and machine-protection limits; stop a fix that would rewrite frozen run artifacts or relax a check merely to obtain green.
- **Outcomes and next actions:** A focused passing control plus full current-head success permits merge; a still failing assertion requires its own cause and repair; missing runner-only logs keep that exact cause unknown; a new failure is recorded rather than hidden.
- **Recheck trigger:** Every new PR head and its terminal Actions results; any correction to the CI checkout, dependency set, or older registry tests.

A planned step is not a completed experiment. The scientific diagnostic still requires its own frozen approval and ready selector.

## Resolution and history

2026-10-18: Opened from PR #2395 head `fa209de5a9` Actions run `39092850807`. Head `b8257585a1` repairs the directly induced audit-contract assertion but does not establish a successful full gate. Unresolved.
