# Independent corrective software review

All three assigned software joints **hold within the tested scope**. No new blocking finding was found. This review covers source snapshot `4489fb39918660d4298c2d548fee7eeed09ea99a`, parent `b0666bd646f017bea651a5487fade1ec574e6ad7`, at shared review HEAD `6e8294530de44e8a889f6084d1154709023e0e85`. It does not change the frozen original review's **breaks / F1 / P2** result or any official research status.

## Native epoch fence

`tools/goal_lanes.py:410` validates an optional expected epoch as an exact positive integer, excluding bool. `release_task()` loads/classifies once, captures the selected epoch, and rejects a mismatch before constructing a release payload/path or calling `write_once()`. The payload and path use that same captured epoch; owner and exclusive-write fencing remain. Both runbook paths pass their captured epoch through `--expected-epoch` (`tools/runbook.py:1357`, `1366`, `1386`). Static inspection found no re-selection between checking and writing.

The independent API/CLI probes exercised invalid types, stale epoch, matching epoch, foreign owner, an already-released claim, an occupied foreign release path, and omitted-argument compatibility. A separate scheduled control published an actual new native epoch after selection but before the original write: the release remained epoch1 and epoch2 stayed live. The focused suite also independently executed the native int-subclass and CLI owner controls.

This is an exact selected-epoch guarantee for the operation. Other worktrees can publish after the selection; this is not a global Git-feed lock. Legacy callers omitting the optional expected epoch remain unfenced by design.

## Independent native counterexample replay

An additional reviewer-written driver created disposable local bare origins and peers, copied exact native `goal_lanes.py` (SHA-256 `ca68df2f809c0b3c0be6acd3ebcb890f545f18b31bb6a1598b246d271807d8eb`), and invoked its actual CLI. Setup and the toy supervisor come from the supplied conformance fixture; schedules and invariant checks are independently written. No release or Git result was mocked.

| Captured claim | Release path | Matching epoch | Fetched same-owner newer epoch |
| --- | --- | --- | --- |
| New | Proof-failure cleanup | Release1, status0; proof still stops | Status2, no release; supervisor0 |
| Reused | Proof-failure cleanup | Release1, status0; proof still stops | Status2, no release; supervisor0 |
| New | Normal terminal | Release1, status0; completes | Status2, no release; synthetic supervisor1 |
| Reused | Normal terminal | Release1, status0; completes | Status2, no release; synthetic supervisor1 |

The stale cleanup fixture reproduces the original mechanism: local epoch1 and divergent published peer epoch2, actual own-branch fetch0, epoch1 ancestry1, then native `release --expected-epoch 1` refuses with `expected epoch 1, current epoch is 2`. Both release files are absent. Immediately across each stale release, local HEAD, index, tracked status, all local refs and bare-remote refs are identical. The original publication-proof failure and release refusal occupy separate logs/data fields. Every synthetic session journal verifies.

For the normal boundary, the supervisor first returns from a valid synthetic invocation. The peer then publishes divergent native epochs and the scheduler actually fetches into a fresh fixture tracking-feed ref so native discovery sees epoch2. The selected epoch1 terminal release refuses without mutation. This fresh ref is confined to the disposable fixture; source proof logic and shared Git configuration are unchanged.

All **28 supplemental result objects** passed, including eight runbook cases. Their exact driver, actual argv/status/stdout/stderr records, before/after states and log hashes are embedded in `findings.json`; raw result artifact SHA-256 is `82748e7b9d2dcd1e1830da3321eacd3f833090692ceaaaa68115fc589a3652e8`. Two earlier reviewer-driver failures are also retained: one incorrectly compared untracked log listings across expected log creation; one hit Git's real non-fast-forward tracking-fetch refusal. Neither is attributed to the candidate source. No failed attempt was overwritten or omitted from the report.

## Preserved proof and custody

The original **26 publication/log controls** were independently rerun with raw subprocess tracing: three positives, 22 negatives with zero supervisor invocations, and exclusive attempt-log preservation. The negatives cover unpublished claims, dirty/tampered identity, wrong branch/owner/task/epoch, fetch failure, absent remote branch, failed claim publication and detached HEAD on new/reused paths. The successful unrelated-unpublished-HEAD control proves that claim commit rather than HEAD is checked. These original controls use their supplied lane stub; the native tests above cover the actual release implementation.

The full focused command returned **0: 141 tests and 19 subtests passed**:

```sh
PATH=/tmp/coordinate-test-venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_runbook.py tools/test_goal_lanes.py -q -p no:cacheprovider
```

It took 65.025s; raw stdout SHA-256 is `894283e4ff241b1a3a6be3be3fd6fddb144669fea616200fcada6e27a6820a7f`, stderr empty. The traced26-control invocation returned0 in 8.144s; stdout SHA-256 is `f265e3f5e417f19378cbd514f19bcdb1161a37258988a4dd040684bdbb25efa4`. Full raw outputs and exact commands are embedded in `findings.json`. Actual interpreter: `/tmp/coordinate-test-venv/bin/python3`, CPython3.12.14; pytest9.1.1; PyYAML6.0.3; Linux6.18.55 x86_64.

Independent `GitRepositoryVerifier.verify_archive()` verifies the exact nine changed paths, expected parent, commit reachability, message IDs and hashes, with **no content-only degradation**. Current bytes and snapshot bytes match all nine archive bindings. Seven parent source/protected bindings, both original review hashes and all eight producer output-segment hashes match. The four source files pass the scoped whitespace check. Raw historical log whitespace is preserved. `tools/experiment_execution.py` remains SHA-256 `1abf021e2a490bedb7c76908a4fd230e0aedddfcb71c6ddb32846efbd59c5fdd`; its native live-owner/epoch and tracking-containment admission was inspected and unchanged.

| Reviewed source | SHA-256 |
| --- | --- |
| `tools/runbook.py` | `ce286aa92df78fa9db7d6f566fb88e848b1f33fba3bd9ced93ef6a6026625083` |
| `tests/test_runbook.py` | `b45b414dc3a68fdf339a75def49c868a78102e4a9ca1da75a95e9a31d866a68a` |
| `tools/goal_lanes.py` | `ca68df2f809c0b3c0be6acd3ebcb890f545f18b31bb6a1598b246d271807d8eb` |
| `tools/test_goal_lanes.py` | `4309bb7e021b6d7cc52f23ece931f33bd6a4e2ad1854a1669b46903d8cf4feec` |

Shared-source publication and pre-dispatch publication timing are Coordinator-provided provenance; local archive/content checks were independent. This reviewer made no real-origin network probe. The source-progress commit `6845beddf3bf6d9932fa7843c235ca348b4b8bc8` is administrative producer/source completion; it is not final acceptance evidence.

## Scope, provenance and attestation

Actual inference provenance is a fresh independent runtime-native Codex reviewer invocation, GPT-6 family from session developer metadata. Frozen policy is `review-adversarial`, requested effort `xhigh`; native fallback is authorized by `DEC-20261021-195c49`, with no degradation. Exact serving model and internal execution effort were not independently probed. No static adapter model is claimed served; `model_verified` is false.

Scientific runs are **0**. Only authorized disposable software fixtures and supplied toy conformance examples ran. No actual research plan/supervisor/trial, old research session reopen, cloud/provider/credential/model probe, workflow, research promotion or official status change occurred. The native scientific supervisor was inspected but never executed. No mathematical claim, scientific readiness or performance improvement is inferred; no canonical research graph changes.

The report does not enumerate all concurrency schedules, hostile Git configurations, or cross-machine feed collisions. It establishes the frozen software joints under the actual recorded controls. Only `review.md` and `findings.json` were written in the shared repository; scratch code/results are embedded from `/tmp`. No source, frozen history, shared Git commit/claim/release or root-owned administrative receipt was changed. The physical task card is `ledger/handoffs/TASK-20261021-d0c5d4.yaml`; the initial dispatch's nonexistent `protocol/handoffs/` hint was corrected by the Coordinator, and the embedded queue card matches.

`review_attestation` (full read provenance and per-joint verdicts are in `findings.json`):

```yaml
task_id: TASK-20261021-d0c5d4
joints_owned:
  - native atomic epoch fence
  - actual divergent-native release regression
  - preserved publication proof, scope and history
read_sibling_reports: false
verdict:
  native atomic epoch fence: holds
  actual divergent-native release regression: holds
  preserved publication proof, scope and history: holds
```

The native independence checker passed with `--no-addenda`: one report, every joint owned and attested, blindness respected and controls declared. Final source/report data checks passed. Both assigned outputs are frozen; all reviewer writes have stopped.
