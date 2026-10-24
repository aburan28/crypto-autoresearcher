# Independent software review: breaks

Task `TASK-20261021-36e54c` reviewed published snapshot `102d71b590d4b45dd39361af17658e18d0582109` at review HEAD `ed8179fd61097a0677053733eec4f308170acd77` on `codex/coordinate-20261021`. The remote-proof repair passes its supplied tests, but its new proof-failure cleanup can release a different live epoch. This breaks the frozen ownership-cleanup joint and blocks acceptance of the complete software claim. No mathematical conclusion follows.

## Blocking finding: cleanup reselects an unverified epoch

**F1, P2, `tools/runbook.py:1356–1357` and `1384–1386`.** `_sync_claim()` verifies the local committed claim at epoch 1 before fetching. If that fetch reveals a newer claim, a failed containment check still enters `_release_claim()` because `claim_identity_verified` describes the pre-fetch claim. The release command supplies the task and owner, with no expected epoch. The unchanged native `goal_lanes.release_task()` discovers claims again and chooses the highest epoch (`tools/goal_lanes.py:414–439`). Thus the release need not concern the identity that this runbook verified.

The independent deterministic fixture used an actual local bare origin, a main-only default fetchspec, two disposable worktrees, and the **unchanged native claim publisher**, SHA-256 `e7fe3b37bf4841eb79f66e90b3e40631c572f13e2d27db103707f00617e0b50f`. Only the supervisor was synthetic; it recorded calls if invoked. No Git outcome was mocked. The fixture first pushed the approved synthetic base, then:

1. Local worktree: native `python3 tools/goal_lanes.py claim experiments/EXP-TEST-abcdef/queue.json TASK-20261016-abcdef --as mech-test --ttl-minutes 60 --publish --no-push --session local-unpublished-epoch1` returned 0. Its unpublished epoch-1 claim commit was `8afed50762d23b9bec2d38e7c14eb8054427345b`.
2. A peer clone of that bare origin published its own native epoch 1 using the same owner and `--session published-other-epoch1`, then native epoch 2 using `--force --session published-newer-epoch2`; both returned 0. The local worktree had not fetched these records. The forced claim was confined to the disposable fixture.
3. `Runner._live_claim_epoch()` in the local worktree returned 1. Running the synthetic runbook verified local epoch 1 and its committed bytes. `git fetch --no-tags origin refs/heads/fixture:refs/remotes/origin/fixture` returned 0 and fetched the divergent peer history. `git merge-base --is-ancestor 8afed50762d23b9bec2d38e7c14eb8054427345b refs/remotes/origin/fixture` returned 1.
4. Cleanup invoked native `python3 tools/goal_lanes.py release experiments/EXP-TEST-abcdef/queue.json TASK-20261016-abcdef --as mech-test --outcome failed --note 'runbook session RBS-TEST-abcdef' --publish`. It wrote and committed **epoch 2's** release before its push was refused as non-fast-forward; the command returned 2. There was no epoch-1 release. The session stopped, supervisor calls were 0, and journal verification returned `[]`.

The wrong release file contained this observed JSON:

```json
{
  "artifact_sha256": {},
  "epoch": 2,
  "note": "runbook session RBS-TEST-abcdef",
  "outcome": "failed",
  "owner": "mech-test",
  "released_at": "2026-10-21T15:27:16Z",
  "schema": "crypto.autoresearch.task_release.v1",
  "task_id": "TASK-20261016-abcdef",
  "was_expired": false
}
```

The raw fixture stdout, all actual command/status/stdout/stderr records, observed release content and proof data are embedded in `findings.json`, command label `independent-native-newer-epoch-cleanup`; transcript SHA-256 `5f55301374a3ab0c4e72a6fa4c77077b63006550575a848cf16d3174ebd1b902`. The fixture driver exited 0 because the reproduction completed; the checked ownership invariant **failed**. Its temporary repositories were then deleted.

This report attributes the new trigger to the proof-failure cleanup added at lines 1356–1357. Normal post-supervisor cleanup already used an owner-only native release before this patch; the underlying re-selection behavior and any equivalent race on that older path are pre-existing. No supervisor-admission bypass occurred in this counterexample. The impact established here is incorrect durable ownership metadata: a release for a live epoch whose identity this invocation did not verify. The push failure does not undo the locally written and committed release.

A sufficient correction must prevent a proof-failure cleanup from releasing any identity other than the exact verified task/owner/epoch. Leaving such failed proofs for explicit ownership reconciliation avoids the new mutation. If automatic cleanup remains required, the native release mutation needs an expected-epoch comparison at the write boundary, with serialization or equivalent protection against re-selection between comparison and write. A wrapper-only precheck leaves that race. Changing native publisher authority requires a prospective amendment; this reviewer changed no source.

The existing `FAKE_LANES` release stub (`tests/test_runbook.py:747–749`) only changes its state file; it does not implement native claim discovery or epoch selection. This explains why the supplied cleanup controls do not detect F1. A corrective regression should use native claim discovery/release against a disposable remote containing a newer same-owner epoch and assert that no release for that newer epoch is written or committed.

## Frozen joints and known-false objects

| Joint | Verdict | Evidence |
| --- | --- | --- |
| Remote proof, not local fabrication | holds within tested scope | `runbook.py:1413–1448` validates branch and exact committed claim identity, obtains the claim-path commit, fetches the remote own branch with the required explicit refspec and `--no-tags`, and checks containment. No source creates tracking proof from local HEAD. |
| Both ownership paths and failure accounting | **breaks** | The new and reused positive paths and all supplied failure cases pass, with exclusive logs preserved. F1 shows the new failure cleanup can release a newer epoch after a fetch. |
| Scope and provenance | holds | All seven snapshot paths independently match committed and archive-bound SHA-256 values. All six protected source/document hashes remain unchanged. All five preserved failure inputs match their frozen hashes and historical Git bytes. Producer raw logs and all twelve declared output-segment hashes match. |

I independently executed the final-source three positive controls and all 22 negative cases using the frozen test functions, actual subprocesses, `pytest.MonkeyPatch` for fixture environment settings and the trace fixture. The trace observes the real `run_process()` outcomes. It replaces no Git return code. Each ownership path had these outcomes:

| Known-false object | Actual new / reused outcome | Supervisor calls |
| --- | --- | --- |
| Unpublished claim | Required own-branch fetch 0; exact-claim ancestry 1; stopped | 0 / 0 |
| Wrong or tampered claim | Owner/task/epoch/branch identity mismatches refused; dirty committed-byte mismatch refused; stopped | 0 / 0 |
| Failed own-branch fetch | Actual fetch 128 with nonempty stderr despite stale tracking data; stopped | 0 / 0 |
| Absent remote branch | Actual fetch 128 with nonempty stderr; stopped | 0 / 0 |
| Failed claim push | Actual receive-hook push refusal; new claim command 1, no proof/supervisor continuation. Reused fixture had a real failed push, then fetch 0 and ancestry 1; stopped | 0 / 0 |

Detached cases also stopped with zero supervisor calls. The three positive cases completed with one synthetic supervisor invocation each: new, reused, and reused with an unrelated unpublished HEAD. The latter checked the claim commit rather than substituting HEAD. The independent exclusive-log control confirmed that an existing attempt raises `FileExistsError`, a distinct attempt creates new logs, and original bytes remain intact. Its supervisor calls were zero. These successful controls do not negate F1.

## Verification and custody

The prescribed independent invocation was:

```sh
PATH=/tmp/coordinate-test-venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_runbook.py -q -p no:cacheprovider
```

It returned **0: 97 passed in 52.95s**. The subprocess duration was 53.59751151099999 seconds. Raw stdout SHA-256 is `68e5bd0e6293f8acbd7e13d9b14bb34c08e6398afd3189c1876a0b55a378df4c`; stderr was empty. The actual interpreter was `/tmp/coordinate-test-venv/bin/python3`, CPython 3.12.14, pytest 9.1.1, PyYAML 6.0.3. Raw stdout, including native trailing spaces, is embedded without normalization in `findings.json`.

The additional direct synthetic controls completed with driver exit 0; their raw transcript is embedded under `independent-direct-synthetic-controls`, SHA-256 `f5a75008baab6532e7ee60c45af4110f6e3cb655a2a70e93052a99744b563768`. There are 25 recorded result objects (three positives, 22 negatives) plus the separate successful exclusive-log control. F1's native-publisher fixture is additional evidence, not an alteration of these results.

Reviewed source SHA-256 values:

| Path | SHA-256 |
| --- | --- |
| `tools/runbook.py` | `856577fd473bbb3b7a7d45b2d99c3cf148eb8fe16f14680988d1309e2559338c` |
| `tests/test_runbook.py` | `6228fa578d88498f9aaeb7b88fbabcb6d4a15abde2585378e967fd8781f3bd01` |
| `tools/goal_lanes.py` | `e7fe3b37bf4841eb79f66e90b3e40631c572f13e2d27db103707f00617e0b50f` |
| `tools/experiment_execution.py` | `1abf021e2a490bedb7c76908a4fd230e0aedddfcb71c6ddb32846efbd59c5fdd` |

The source snapshot's exact seven changed paths comprise these two source/test files, the producer's four receipt/README/log files and its snapshot control. They include no research session or scientific state changes. Independent byte checks verified both original source bindings at base `b6dbfa28bbe0e48d328ca4da34269956166355fe`, the six protected unchanged paths, seven snapshot artifacts, five preserved historical inputs and twelve producer output segments. Producer dependency failure, expected prepatch regression failures and test-authoring failures remain present; this review neither overwrites them nor reclassifies them as final-source failures. No raw producer log was edited.

Actual inference provenance: a fresh independent native Codex invocation, GPT-6 family from session developer metadata; requested policy `review-adversarial`, requested effort `xhigh`, runtime-native fallback authorized by frozen `DEC-20261021-55cd89`, no degradation. The static adapter's Opus 5.5 binding was unprobed and is not asserted served. No exact serving-model probe was performed. The Coordinator supplied the independent-session dispatch and published-snapshot provenance; this reviewer separately verified local Git content and hashes, without a real-origin fetch or network publication probe.

## Residual limits and disposition

This is a software-only review. All executions were the authorized disposable software fixtures, including the supplied toy conformance suite. No actual repository research runbook/session was started or reopened; no real supervisor/plan, research claim, workflow, cloud/provider/resource/credential action or model probe ran. The native supervisor's unchanged admission check was inspected at `experiment_execution.py:312–319`; actual scientific admission was not exercised. No scientific readiness, research improvement, mathematical result or hypothesis disposition is established.

The review did not enumerate every possible concurrency schedule or hostile Git configuration. The historical stopped attempt's exact fetchspec remains unknown; the current main-only fetchspec and synthetic reproduction establish the scoped mechanism only. No sibling review was read. Only this review and `findings.json` were written; no shared-repository commit or push was made. The Coordinator was notified immediately after F1 was reproduced. Acceptance requires a prospective corrective task, a new published source snapshot and fresh independent review of the corrected ownership behavior.
