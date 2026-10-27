# Independent native-guard review

TASK-20261026-5bedd5 · joint `guard-enforcement-coverage-and-retention` · verdict **breaks**

The qualification claim does not hold over all five required classes. The retained evidence supports stopped-child placement, exact 8 GiB readback, escaped-session tree cleanup, the repaired full 1800-second watchdog/serial test, and both Q5 negative cases in the recorded private Docker runtime. It does not support actual exact-8-GiB OOM enforcement: original Q4 and followup Q4 both stopped at their prospective headroom gates, no allocator or Q4 worker launched, and no OOM-event delta, kernel victim, peak-at-enforcement, parent-survival, or post-OOM cleanup receipt exists. This is a coverage failure for the qualification claim, not evidence that the supervisor's memory cap fails.

Full guard qualification therefore remains false. This review grants no scientific approval, performance claim, global-host readiness, hostile-worker isolation, experiment readiness, or status transition. Scientific calls were 0 and all 24 original scientific cases remain unrun.

## Independent findings

### Source, binary, runtime, and custody binding holds

- Programme input is `fb316cb16e51ffb28f84af8f42f4bbe2bb166d80`. Original owner C1 is `204735c3f6f3144911df58a6ece7699c0e74d4ad`; successor source, preparation, and final trees are respectively `6b3ed020228586f60ab4ae56edf68fed2a853ef5`, `608f7198db59fc431123de2c4d928e4e3466d6da`, and `76a3e4eb67e818354da7575dad4b834467a97e5c`. The ancestry is continuous from production pin `86ddd19f67e08160c22a0d8ba9a32a92321d18ad` through C1 and the successor trees.
- All 12 protected `experiments/joint-smallroot-native/src/` files are byte-identical between the production pin and final owner tree. In particular, `supervisor.hpp` is SHA256 `2b7d98fbba725c56c920b468b217c0b1bb7786802828d1e1a2304544bf3085d8`. `guard_worker.cpp`, the runtime shell/JSON, and the Makefile are unchanged from C1 to the final tree.
- The C1-to-successor helper diff is confined to Q3: the dedicated competitor `wait4` and its receipt move before generic orphan cleanup. The predicates, 1800-second production timer, worker modes, Q1/Q2/Q4/Q5 branches, production source, runtime envelope, and cleanup implementation are unchanged. The repaired helper is SHA256 `9ca4ea5bde491c2470117d7713b7cbe8e001cbc8ebd964f974f84a0f481832c4`; the original helper and worker are `2738ade011be6b544d403d58ebe8f2245bbd973e4ce3269aa7f45e5807491c15` and `f06e008bb405bbbf11a3f85fafb10fb95e6c781e321ed1e11ffb787721f2afdb`. The retention-regression and cache-preparation binaries are `4f2ae7ac09d815a670204556421e25b52f34b25bd2dfa3edcea252f581980630` and `5615bb5614bce490f39d8e715c77e1ecdae0defd2dad6a67b977acbe3ee31144`. All five retained files still match their sealed byte counts and hashes.
- The image binding is `debian:trixie-slim@sha256:62bd423aeee912639ca8ee681c2b762cb3e25137e0a92b20be455898a9f034ad`, observed image ID `sha256:133aec7ab1411181567fef7fc3f4512123e1f9660090b49851de4b698b4ff772`. Each class record binds private cgroup namespace, network none, read-only rootfs, 16 GiB container memory, 16 GiB memory-plus-swap request, 2 CPUs, pids 64, read-only build/library binds, and only the task record bind writable. Q5-readonly is nonprivileged as required.
- I independently matched the original expected path set to the exact 691 paths changed from the production pin to C1, with zero set delta. All 46 top-level raw entries, 626 subtree members, seven subtree-index hashes, ten C1 source members, the custody manifest, and the root index matched retained hashes; the seven subtree indexes do not declare their own byte counts, so only their hashes are bound there. I also matched the successor's 681 current members plus seven shards, root index, and final manifest to the exact 690 paths changed from its worktree base to the final owner commit, with zero set delta. All 681 member hashes/bytes and all seven shard hashes/bytes matched.
- Historical phase semantics are sound: the source-stage manifest's 86 members match the `6b3ed...` tree, and the preparation manifest's three direct members plus its two index files match `608f71...`. Their daily-log bytes differ from the final appended log by design and resolve at their own commit trees; the final index binds the 11,223-byte appended log at `76a3e4...` with SHA256 `6cb20c4817959772b3f3038c591580bb4387d171dfe6827a95a5b74644879564`.
- The pre-action publication gates hold in their actual order. The successor admission was published at programme commit `de712891...` at `00:06:38Z`, and the frozen source stage at owner commit `6b3ed020...` at `00:51:18Z`. Cache-preparation admission `446773e2...` at `00:53:31Z` preceded its `00:56:36Z` container start and the `00:57:45Z` post-advice probe. Q3 admission `57f3427d...` at `00:55:58Z` preceded its `01:02:53Z` dispatch seal and `01:03:08.619938647Z` container start. The Q4 refusal was published at `3d369f1f...` at `01:00:56Z`; no Q4 allocator subsequently ran. The preparation-stage archive commit `608f7198...` at `01:10:40Z` did occur after Q3 started, as the final manifest explicitly records. That commit preserves already-completed preparation records; it is not the source/admission publication gate asserted before either action, and I do not relabel it as prelaunch publication.
- Programme snapshots preserve those bindings. Original snapshot TASK-20261026-a3ab76 has five of five declared hashes matching; successor snapshot TASK-20261026-b7eff7 also has five of five matching and is unchanged from snapshot commit `c90b8b1a12bc6323ece604a965bb96bad823c166`.

### Original rows remain original

The original five programme rows are byte-equivalent as structured data to the owner C1 table and to the `original_five_rows` copied into the successor results. They were not rescored by the followups.

| Row | Independent reading of retained raw evidence |
| --- | --- |
| Q1 placement and ordinary completion | **Passed in the recorded fixture.** Source stops the child before `exec`, places the stopped PID in the new cgroup, reads membership, then resumes it. The worker's first snapshot records PID 7 at `/delegated/joint-smallroot-1`, `memory.max=8589934592`, raw child `memory.swap.max=max`, and parent `memory.swap.max=0`; it exits 0. Production wall is 100,511,873 ns, independent elapsed 100,945,099 ns, primary is absent, and the group is removed. The worker snapshot supplies the exact membership evidence that the supervisor's substring readback alone would not.
| Q2 escaped-session tree cleanup | **Passed in the recorded fixture.** Primary PID 7 remains in session 1; child PID 8 and grandchild PID 9 each set `sid=pid` and share `/delegated/joint-smallroot-1` with the primary. Stable start-time comparisons observe the descendants as zombies, not live processes; the primary is absent and the cgroup is removed. Normal worker exit is 0 and the case is uncensored.
| Q3 watchdog and serial exclusion | **Failed as originally recorded.** The production timer genuinely reaches 1,800,071,055,817 ns; independent elapsed is 1,800,071,693,757 ns, wait status is SIGKILL 9, serial rejection is retained, the escaped tree is no longer live, the group is removed, and the lock is released. Generic cleanup reaped the competitor first, however, so dedicated `wait4` returned `-1/ECHILD(10)` with status and usage unavailable. That retention failure remains a failed original row.
| Q4 exact 8 GiB OOM | **Infrastructure not started.** The original raw minimum is `min(17,834,926,080 host, 17,165,516,800 container, 12,439,695,360 visible outer)=12,439,695,360` bytes, 445,206,528 below the required 12,884,901,888. The prospective worker is excluded from this minimum. No worker, mmap, touch loop, event delta, or victim exists.
| Q5 failure retention and read-only negative | **Passed in the recorded fixture.** Missing exec yields wait status 32,512 (exit 127), an available worker CPU receipt, and group removal. The ordinary nonprivileged negative has `access(W_OK)=-1` and actual mkdir `errno=30`/EROFS; container exit 0 means the negative predicate passed. Partial and unavailable inner records remain explicit.

### Followups remain separate

- The pure software retention regression was invoked once by the producer and retained both outcomes: old order observes the child with `waitid(WNOWAIT)`, generic `waitpid` reaps exit 23, then dedicated `wait4` returns ECHILD; corrected order retains exact PID/exit 23 and actual usage before generic cleanup. The current zero-run handoff and explicit instruction prohibited reviewer execution, so I reviewed its source and raw receipt but did not independently replay it. This is an unperformed reviewer replay, not a second producer attempt or a pass claim by this session.
- Q3-followup-1 used the repaired helper and unchanged C1 worker. It ran once. The container ran from `2026-10-27T01:03:08.619938647Z` to `01:33:08.853118452Z`; production wall is 1,800,064,885,794 ns and independent elapsed is 1,800,065,709,473 ns. The external 1,950-second fail-safe did not fire. Dedicated competitor `wait4` returns PID 7, errno 0, reaped true, exit 0, user 1,018 us/system 0 us. The exact serial exception is `sequential supervisor lock unavailable`; source ordering makes that exception occur before any competing cgroup or fork, and no competing worker `primary.ready` exists. Escaped descendants transition R/Z with `populated=1` to Z/Z with `populated=0`; the group is removed, lock reacquisition succeeds, container removal succeeds, and exact container absence is recorded.
- The one additional cache-advice preparation starts from 398 sealed candidates, excludes 23 duplicate-inode aliases including the original 80 set by path/device/inode, and advises 375 unique files (631,361,269 bytes) once. All 375 raw rows carry `fadvise_rc=0` and `stable_after=1`; the preparation container and records show one invocation and clean removal. Advice is not evidence of reclaimed memory.
- Q4-followup-1 remains **infrastructure not started**. Raw post-advice values give visible outer headroom 9,452,244,992 bytes before the probe and 9,264,652,288 after it; the latter is the conservative minimum and is 3,620,249,600 below the requirement. Host samples are all about 17.8 GB and are not limiting. The empty child readback is exactly 8,589,934,592 bytes with current 0, empty `cgroup.procs`, raw child swap max, container swap 0, and `populated=0`; it was removed. The 8 GiB group is intentionally excluded from the enclosing-headroom calculation. Worker launches and allocator launches are both 0.

### Cross-version transfer is narrow but supported

Q1, Q2, and Q5 remain observations of the original C1 helper, while Q3-followup-1 is an observation of the repaired helper. The only helper change is inside Q3 after the production supervisor returns and before the shared cleanup call. It cannot change the Q1/Q2/Q5 execution branches, and the protected supervisor, worker, runtime, libraries, image, resource envelope, and class predicates are unchanged. Those original observations therefore transfer as evidence about the same protected supervisor in this exact fixture context. This does not turn the original Q3 failure into a pass, imply that all five classes reran under the repaired helper, or supply the missing Q4 enforcement observation.

## Why the joint breaks

The plan requires genuine enforcement, not a `memory.max` readback. Neither Q4 row contains `pre-touch.events`, an `oom_kill` delta, the bounded 8 GiB+64 MiB touch attempt, a kernel-selected victim, a contemporaneous peak, parent survival, or cleanup after OOM. The source contains predicates that would check those observations if a worker ran, but unreachable test code and an empty-cgroup readback do not qualify enforcement. Required-test omission therefore breaks `guard-enforcement-coverage-and-retention`, while the underlying OOM behavior remains unknown.

The production supervisor also checks only host `/proc/meminfo` before launch. The stricter enclosing-headroom rule is supplied by the qualification driver before its Q4 call. This review supports that frozen fixture-side admission design; it does not establish that the production supervisor independently refuses every low-headroom enclosing cgroup.

## Retention and remaining boundaries

- Native guard custody is complete for the declared owner sets and keeps the original failed Q3, both infrastructure-not-started Q4 rows, raw unknown CPU scopes, and all followup rows separate. No surviving owned descendant or container appears in the receipts.
- Effective swap 0 is observed through the container parent's raw `memory.swap.max=0`; worker and delegated raw values may be `max`. Hidden ancestors remain unobserved. Conclusions are limited to the recorded privileged/private-cgroup, trusted-root-worker environment; the ordinary Q5 negative is the separate nonprivileged case.
- Full process-tree CPU remains unknown. No global-host, arbitrary-hostile-worker, or general deployment conclusion follows.
- Ancillary Rust validation is not a clean suite pass: exit 101, 4,888 passed, 6 failed, 121 ignored; six same-binary replays are 4 failed/2 passed. The 18-file canonical package contains the excerpt and replays. The complete 431,104-byte raw log is present locally with SHA256 `b37a4217610b6d40aa72004ef36b170bac669545f389b6bc218f7f6c2cd38636`, but configured-credential upload failed, so canonical full-log custody is incomplete.
- Root's cached `git diff --check` remains exit 2 with eight blank-at-EOF diagnostics in two immutable CPU-info logs and six Rust replay logs. Their bytes are preserved; this review makes no format-pass claim.
- `agents/reviewer.md`, named by the task routing, is absent from the published programme checkout. I applied the present shared review-plan/attestation provisions in `agents/validator.md`, `agents/red-team.md`, the handoff, the template, and the independence checker. No sibling review was read.
- The frozen/offline instruction forbade new source calls. I therefore did not retrieve external documentation in this session; the load-bearing review uses repository source, manifests, commit trees, and raw receipts. The producer's cited wait documentation was not accepted as a substitute for those observations.
- One read-only metadata command encountered an exec-server transport disconnect and was repeated after the environment recovered. A later local Git metadata lookup used the wrong checkout for mixed programme/owner commit IDs, causing a partial-clone promisor fetch attempt that the network sandbox blocked; no object was retrieved, and the same commit metadata was then read from the correct local checkouts with lazy fetch disabled. No guard, regression, stress case, allocator, science, source edit, or case retry occurred.

Actual review provenance is the published task binding `openai/gpt-5.6-sol`, `review-adversarial`, reasoning `xhigh`, verified model true, independent session `native-independent-guard-5bedd5`, with no fallback or degraded requirement. Root may release this review claim as completed for reporting only after archiving these three declared outputs. That consent conveys no full guard qualification, scientific readiness, merge, or official state change.

```yaml
review_attestation:
  task_id: TASK-20261026-5bedd5
  joints_owned:
    - guard-enforcement-coverage-and-retention
  sources_read:
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/review-plan.json
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/qualification-plan.json
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/tasks/TASK-20261026-6374dd/
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/archives/TASK-20261026-a3ab76/snapshot-receipt.json
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/amendments/DEC-20261026-b83007/reviewer-directive.json
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/amendments/DEC-20261026-b85397/reviewer-directive.json
    - coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/successors/DEC-20261026-7a93a8/
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/src/
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/tests/guard_qualification.cpp
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/tests/guard_worker.cpp
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/spec/guard-qualification-runtime.sh
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/spec/guard-qualification-runtime.json
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/spec/checks/TASK-20261026-6374dd/
    - /workspace/crypto-native-smallroot/experiments/joint-smallroot-native/spec/checks/TASK-20261026-1525ac/
    - git:crypto-native-smallroot@6b3ed020228586f60ab4ae56edf68fed2a853ef5:docs/session-logs/2026-10-27.md
    - git:crypto-native-smallroot@608f7198db59fc431123de2c4d928e4e3466d6da:docs/session-logs/2026-10-27.md
    - git:crypto-native-smallroot@76a3e4eb67e818354da7575dad4b834467a97e5c:docs/session-logs/2026-10-27.md
    - /workspace/smallroot-session/native-guard-final-stage-publication.json
    - /workspace/smallroot-session/native-guard-final-cached-diff-check.log
    - /workspace/smallroot-session/native-owner-current-cargo-attempt9-60e694.log
  read_sibling_reports: false
  blind_from_respected: null
  verdicts:
    guard-enforcement-coverage-and-retention: breaks
```
