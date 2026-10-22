# Published runbook claims can lack local origin-tracking visibility

- **Status:** `resolved` for reviewed source `4489fb39918660d4298c2d548fee7eeed09ea99a`; PR #2446 CI/merge pending
- **Kind:** implementation gap in orchestration metadata; no mathematical obstruction
- **Affected work:** `EXP-ICPERF-e467a5`, stopped session `RBS-ICPERF-b7e41c`; original task `TASK-20261021-b8030c`, corrective task `TASK-20261021-751951` and fresh independent review `TASK-20261021-d0c5d4`
- **Next action owner:** Coordinator, final administrative publication and CI/review follow-through on PR #2446; no scientific launch
- **Last updated:** 2026-10-21

## Problem

A successful runbook task-claim push does not guarantee that the exact claim is visible in local origin-tracking refs when native supervisor admission checks it. Default fetch can refresh only main and leave the own branch absent.

## Evidence and uncertainty

- **Observed:** The retained old claim stdout says `published b661e2d428` and pushed, then native supervisor exit 2 reports claim not visible in origin tracking refs. Source commit `93b87120f68801ce4a70e678067b33d661623117`, narrow byte-preserving inputs and hashes are in [source-bindings.json](../coordination/tasks/TASK-20261021-f1df6d/inputs/source-bindings.json). No trial directory, execution receipt or measurement was produced by that stopped attempt.
- **Historical baseline source (2026-10-21 orientation):** At `b6dbfa28bbe0e48d328ca4da34269956166355fe`, `goal_lanes.py:568–586` pushes without fetching; `runbook.py:1340–1357` proceeds from claim publication to supervisor; `experiment_execution.py:316–319` requires exact claim containment in local origin-tracking refs. These three blobs are unchanged from the preserved stop.
- **Configuration captured at initial orientation (2026-10-21):** `remote.origin.fetch` was only `+refs/heads/main:refs/remotes/origin/main`; the own tracking branch was absent at that observation. This explains the failure mechanism. The exact historical fetchspec was not captured and remains unknown. Successful publication is evidence against calling the old claim simply unpublished.
- **Initially missing capability:** Explicit own-branch remote-to-tracking synchronization and containment at the runbook boundary for new and reused live claims, with local bare-Git controls.
- **Initial unresolved gates:** A new implementation and passing regression were not yet established at orientation. Those software gates are now met in the scoped resolution below; no scientific result, ready scientific launch or resolution of distinct pilot approval/output/archive-coverage problems is established. Old session is stopped but natively reopenable through append-only preflight; no reopen is authorized here.

## Software exit criteria

- [x] Exact own-branch remote fetch with explicit tracking destination and exact native claim containment protects both ownership paths before supervisor invocation.
- [x] Disposable local bare-origin main-only-fetchspec controls reproduce the gap, pass the repaired remote-proof path and fail closed for actual unpublished/tampered claims and push/fetch failures.
- [x] Source snapshot and focused test receipts are published, then a fresh independent software review accepts all predeclared joints without gate bypass or old-evidence edits.

This establishes only the scoped software custody correction. Scientific ready/ownership/resource/manifest checks, any later run and independent scientific interpretation remain required.

## Current next action and recheck

- **Action:** Coordinator completes the final nine-path administrative archive/publication, then CI/review/publication follow-through on [PR #2446](https://github.com/aburan28/crypto-autoresearcher/pull/2446). No scientific or cloud action follows from this software resolution.
- **Scope:** Source4489fb39918660d4298c2d548fee7eeed09ea99a plus fresh independent holds review. Exact selected-epoch fencing is not a global Git-feed lock; callers omitting expected_epoch deliberately retain legacy behavior.
- **Recheck:** A contradictory native ownership/publication-proof record, a change to these code paths, or a failed applicable final CI check reopens the relevant software obligation. Scientific admission and separate named obstructions retain their own gates.

## Resolution and history

2026-10-21: Named the current source gap and froze prospective task `TASK-20261021-b8030c` under `DEC-20261021-55cd89`. At that initial stage the record remained unresolved. It is distinct from [prime63 pilot self-attested approval](icperf-prime63-launcher-self-attested-approval.md) and [missing supervisor archive coverage](ready-plans-lack-supervisor-archive-coverage.md), neither of which this repair resolves.


2026-10-21 independent software review: source102d71b590 passed97 focused tests and26 synthetic controls, but [review36](../coordination/tasks/TASK-20261021-36e54c/review.md) and its immutable findings establish one blocking F1/P2. After fetching a divergent newer same-owner epoch2, cleanup of verified local epoch1 called unqualified native release, wrote/committed2.release.json and then failed its push; supervisor calls were0. This is durable incorrect ownership metadata, not scientific evidence or an admission bypass. [DEC195c49](../ledger/decisions/DEC-20261021-195c49.yaml) records scoped breaks and keeps this problem investigating.

Additional required exit conditions:

- [x] Native API/CLI expected-epoch fencing validates a positive integer and checks the single selected current epoch before payload/path/write_once, with no reselection or wrong-epoch mutation.
- [x] Both cleanup and ordinary runbook release always pass captured epoch; actual native divergent-remotes regression, normal-release advancement and owner/write-once/legacy controls pass without wrong release-file/commit/push mutations.
- [x] A fresh published corrective source snapshot and [independent review plan](../coordination/tasks/TASK-20261021-751951/protocol/review-plan.yaml) support a later scoped disposition. Prior passed tests, failed attempts and review evidence remain unchanged.

At the original breaks checkpoint, the prospective [corrective queue](../coordination/tasks/TASK-20261021-751951/protocol/dispatch_queue.json) was the next action. No new scientific trial, old-session resume or goal/hypothesis status change is authorized by this software review.


2026-10-21 scoped software resolution: corrective source `4489fb39918660d4298c2d548fee7eeed09ea99a` has an exact nine-path native-verified published snapshot. Fresh independent [review d0](../coordination/tasks/TASK-20261021-d0c5d4/review.md) and its [findings](../coordination/tasks/TASK-20261021-d0c5d4/findings.json) hold all three frozen software joints, with no finding. The independent focused suite passed141tests and19subtests;26 publication/log controls and28 supplemental native result objects passed. Four stale native release schedules refused before release/Git mutation. Two reviewer-driver mistakes remain retained; the original97-pass-plus-F1/breaks history is unchanged. [DEC-b416e2](../ledger/decisions/DEC-20261021-b416e2.yaml) accepts only this tested-source behavior.

The marked software exit criteria are supported by that source snapshot and fresh independent review. Final administrative archive/publication and applicable CI/merge on PR #2446 remain pending at this decision. This is not a scientific readiness/result, mathematical theorem, complete concurrency proof or end-to-end performance claim. The separate prime63 self-attested-approval and SCURVE/generated-artifact coverage/envelope obligations are unchanged. No old research session was reopened.
