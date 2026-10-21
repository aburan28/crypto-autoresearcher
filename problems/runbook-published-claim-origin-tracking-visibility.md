# Published runbook claims can lack local origin-tracking visibility

- **Status:** `investigating`
- **Kind:** implementation gap in orchestration metadata; no mathematical obstruction
- **Affected work:** `EXP-ICPERF-e467a5`, stopped session `RBS-ICPERF-b7e41c`; [prospective software task](../ledger/handoffs/TASK-20261021-b8030c.yaml)
- **Next action owner:** Executor `TASK-20261021-b8030c`, after published prospective authority and exclusive software ownership
- **Last updated:** 2026-10-21

## Problem

A successful runbook task-claim push does not guarantee that the exact claim is visible in local origin-tracking refs when native supervisor admission checks it. Default fetch can refresh only main and leave the own branch absent.

## Evidence and uncertainty

- **Observed:** The retained old claim stdout says `published b661e2d428` and pushed, then native supervisor exit 2 reports claim not visible in origin tracking refs. Source commit `93b87120f68801ce4a70e678067b33d661623117`, narrow byte-preserving inputs and hashes are in [source-bindings.json](../coordination/tasks/TASK-20261021-f1df6d/inputs/source-bindings.json). No trial directory, execution receipt or measurement was produced by that stopped attempt.
- **Current source:** At `b6dbfa28bbe0e48d328ca4da34269956166355fe`, `goal_lanes.py:568–586` pushes without fetching; `runbook.py:1340–1357` proceeds from claim publication to supervisor; `experiment_execution.py:316–319` requires exact claim containment in local origin-tracking refs. These three blobs are unchanged from the preserved stop.
- **Current configuration:** `remote.origin.fetch` is only `+refs/heads/main:refs/remotes/origin/main`; the own tracking branch is absent. This explains the failure mechanism. The exact historical fetchspec was not captured and remains unknown. Successful publication is evidence against calling the old claim simply unpublished.
- **Missing capability:** Explicit own-branch remote-to-tracking synchronization and containment at the runbook boundary for new and reused live claims, with local bare-Git controls.
- **Not established:** A new implementation, passing regression, scientific result, ready scientific launch or resolution of distinct pilot approval/output/archive-coverage problems. Old session is stopped but natively reopenable through append-only preflight; no reopen is authorized here.

## What would unblock it

- [ ] Exact own-branch remote fetch with explicit tracking destination and exact native claim containment protects both ownership paths before supervisor invocation.
- [ ] Disposable local bare-origin main-only-fetchspec controls reproduce the gap, pass the repaired remote-proof path and fail closed for actual unpublished/tampered claims and push/fetch failures.
- [ ] Source snapshot and focused test receipts are published, then a fresh independent software review accepts all predeclared joints without gate bypass or old-evidence edits.

This establishes only the scoped software custody correction. Scientific ready/ownership/resource/manifest checks, any later run and independent scientific interpretation remain required.

## Next discriminating step

- **Action:** [zero-science implementation queue](../coordination/tasks/TASK-20261021-f1df6d/dispatch_queue.json), then isolated source snapshot and [independent review](../coordination/tasks/TASK-20261021-f1df6d/review-plan.yaml).
- **Inputs and controls:** Exact current source hashes and preserved failure logs; actual local Git push/fetch/containment, failed push/fetch and unpublished/tampered claim controls.
- **Limits:** One software worker; 2 GiB software envelope; zero scientific runs, cloud actions or credential/model probes; only the two scoped code/test files plus own receipts/logs.
- **Outcomes:** Passing controls plus independent review permits a scoped resolved update; failing controls keep this problem open with exact software refusal. No outcome closes a mathematical direction or launches a scientific trial.
- **Recheck:** After the published source snapshot and independent report, or a new contradictory native admission record.

## Resolution and history

2026-10-21: Named the current source gap and froze prospective task `TASK-20261021-b8030c` under `DEC-20261021-55cd89`. This record is unresolved. It is distinct from [prime63 pilot self-attested approval](icperf-prime63-launcher-self-attested-approval.md) and [missing supervisor archive coverage](ready-plans-lack-supervisor-archive-coverage.md), neither of which this repair resolves.


2026-10-21 independent software review: source102d71b590 passed97 focused tests and26 synthetic controls, but [review36](../coordination/tasks/TASK-20261021-36e54c/review.md) and its immutable findings establish one blocking F1/P2. After fetching a divergent newer same-owner epoch2, cleanup of verified local epoch1 called unqualified native release, wrote/committed2.release.json and then failed its push; supervisor calls were0. This is durable incorrect ownership metadata, not scientific evidence or an admission bypass. [DEC195c49](../ledger/decisions/DEC-20261021-195c49.yaml) records scoped breaks and keeps this problem investigating.

Additional required exit conditions:

- [ ] Native API/CLI expected-epoch fencing validates a positive integer and checks the single selected current epoch before payload/path/write_once, with no reselection or wrong-epoch mutation.
- [ ] Both cleanup and ordinary runbook release always pass captured epoch; actual native divergent-remotes regression, normal-release advancement and owner/write-once/legacy controls pass without wrong release-file/commit/push mutations.
- [ ] A fresh published corrective source snapshot and [independent review plan](../coordination/tasks/TASK-20261021-751951/protocol/review-plan.yaml) support a later scoped disposition. Prior passed tests, failed attempts and review evidence remain unchanged.

The prospective [corrective queue](../coordination/tasks/TASK-20261021-751951/protocol/dispatch_queue.json) is the next action. No new scientific trial, old-session resume or goal/hypothesis status change is authorized by this software review.
