# Published-claim visibility implementation

Software task `TASK-20261021-b8030c`, under frozen authority `DEC-20261021-55cd89`. Implementation started from software ownership commit `d296c5af7efcf5cbd472b04955193fbde224c514`; Git publication and independent review belong to the parent Coordinator.

`Runner._supervise()` now shares one claim-proof path for newly published and reused live claims. It identifies the current branch, checks the exact native claim's task/owner/epoch/branch and committed bytes, obtains its commit with native claim-path Git history, then runs:

```
git fetch --no-tags origin refs/heads/<branch>:refs/remotes/origin/<branch>
git merge-base --is-ancestor <exact-claim-commit> refs/remotes/origin/<branch>
```

Every proof command retains actual argv, exit status, timeout status and exclusive per-attempt stdout/stderr, all bound into the existing journal. A failed proof prevents the supervisor call. Fetch/containment failures release only a claim whose local committed identity was verified, through the existing native release command. Malformed or foreign identities are left untouched. A failed claim publication retains the previous native behavior: return failure with its logs; do not launch or assume ownership can safely be released. Existing supervisor authorization remains unchanged.

The disposable local-bare-origin fixture uses a main-only default fetchspec. Before the patch, its successful real claim push left the own tracking ref absent; the synthetic supervisor mirrored the unchanged native containment refusal and returned 2. Both new and reused regression cases failed their success assertions against the original source, as expected. That actual output is retained.

Final validation: the prescribed focused suite passed **97 tests**. A separate final-source transcript passed **26 controls**: three positives (new, reused, and reused with an unrelated unpublished HEAD), 22 negative cases across both ownership paths, and exclusive attempt-log preservation. Each negative case records zero supervisor calls. Controls cover a truly unpublished claim with successful fetch but failed ancestry, uncommitted and committed identity tampering, wrong task/owner/epoch/branch, failed fetch with stale tracking proof, absent remote branch, real receive-hook push refusal with stale tracking data, and detached HEAD. Remote configuration changes occur only inside disposable fixtures. Source never fabricates a tracking ref from HEAD.

The exact command was:

```
PATH=/tmp/coordinate-test-venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_runbook.py -q -p no:cacheprovider
```

The initial interpreter lacked pytest; that failed invocation is preserved separately from the actual prepatch defect reproduction. The parent supplied the isolated test environment. The first postpatch suite exposed a test authoring error (`event` instead of the journal's `type` field), causing 22 test failures after 74 passes. Those outputs are preserved; the test helper was corrected before the final successful suite and control transcript. No failed output was replaced.

[implementation-receipt.json](implementation-receipt.json) records source hashes, runtime provenance, commands, outcomes and control summaries. [tests.stdout.log](tests.stdout.log) and [tests.stderr.log](tests.stderr.log) append each invocation with explicit command boundaries; nested fixture command records preserve actual Git stdout/stderr and statuses.

Actual inference provenance is native Codex, GPT-6 family from session developer metadata, with the frozen native-runtime fallback amendment. The static adapter binding was neither probed nor asserted served. No scientific run, real supervisor/plan execution, real research claim, old-session reopen, cloud action, credential access or model probe occurred. Mathematical and scientific statuses are unchanged. Native supervisor admission, resource and correctness checks remain necessary; synthetic software controls do not establish a scientific launch or result. No canonical research graph changes.
