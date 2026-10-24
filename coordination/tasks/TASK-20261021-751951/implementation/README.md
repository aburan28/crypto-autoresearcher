# Exact-epoch release correction

Corrective software task `TASK-20261021-751951`, authorized prospectively by `DEC-20261021-195c49`. The original source snapshot, its 97-test result, earlier failed attempts, and independent `breaks` review remain unchanged. This successor addresses the reported F1/P2 ownership defect; final acceptance belongs to a fresh independent review.

The native `release_task()` API now accepts optional `expected_epoch`. It rejects values other than an exact positive integer, excluding booleans, and compares the requested epoch with its single classified current claim before constructing the release payload, path or write. The payload and write-once path use that same checked epoch. Existing owner and exclusive-write checks remain. The CLI exposes `--expected-epoch`; callers omitting it retain their prior selection behavior, including existing `Namespace` callers without that attribute.

Runbook cleanup and normal terminal releases now require the operation's captured epoch and pass it to the actual native release CLI. The journal retains release argv, expected epoch, status, timeout and separate stdout/stderr paths. A refused cleanup leaves the original publication-proof failure intact; the cleanup refusal remains separately inspectable. Exact own-branch fetch/containment and native supervisor authorization are unchanged.

Before correction, the new regression executed the actual native publisher/release CLI against disposable local bare Git origin and two worktrees. Local unpublished epoch1 diverged from published same-owner epoch2. Fetch succeeded and epoch1 ancestry failed. The old cleanup wrote and committed epoch2's release, then its push failed. The regression failed the no-release assertion, with zero supervisor calls. Full command/output and wrong-release metadata are retained in the first command segment of the new logs.

Corrected native controls passed **20 tests and 17 subtests**. Eight runbook cases cover new/reused claims, proof-failure cleanup/normal terminal release, and matching/newer same-owner epochs. All four stale cases refused the actual native release without a release file, HEAD/index change or remote-head change. Stale proof-cleanup cases invoked no supervisor; terminal cases advanced the epoch only after a valid synthetic supervisor invocation. Matching cases published only the captured epoch's release. Actual native API/CLI controls also cover invalid types, mismatch, owner fencing, existing release, exclusive-write refusal, omitted-argument compatibility, and a newer claim appearing after selection without redirecting the checked write.

The original **26 publication/log controls** passed on the corrected source: three positives, 22 negative cases with zero supervisor invocations, and exclusive attempt-log preservation. Final focused validation returned **0: 141 tests and 19 subtests passed**:

```
PATH=/tmp/coordinate-test-venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_runbook.py tools/test_goal_lanes.py -q -p no:cacheprovider
```

All four test invocations, source hashes, statuses, raw stdout/stderr and output-segment hashes are recorded in [implementation-receipt.json](implementation-receipt.json), [tests.stdout.log](tests.stdout.log) and [tests.stderr.log](tests.stderr.log). The expected pre-correction failure is preserved without normalization or replacement. Raw pytest failure formatting can contain trailing whitespace; the four source files pass their scoped whitespace check. No broader test suite was run.

Actual inference provenance is native Codex, GPT-6 family from session developer metadata, under the frozen native-runtime fallback amendment; the static adapter model was not probed or claimed served. All executions used synthetic software fixtures and disposable local Git repositories. No actual scientific claim, supervisor/plan, old session, workflow, cloud action, credential access or model probe occurred. The writer made no shared-repository commit or push and edited no frozen old artifact or scientific status.

This fence binds the checked native selection to its write; it is not a global lock over claims arriving from other worktrees. Legacy callers omitting the optional epoch remain unfenced by design. Scientific readiness, later execution and mathematical conclusions are outside this correction. Parent-owned source publication and fresh independent review remain required. No canonical research graph changes.
