# Cohort implementation status: three retained failed mock suites

2026-10-24 UTC. Engineering observations only. **Named orders executed: 0.**

## Question and fixed scope

Can the prepared ECPP compatibility library be wrapped by a supervisor-callable driver and a separate checker without changing the frozen eleven-omission/ten-publication cohort or its original configuration? TASK-20261024-4f1bf4 permits static and mocked tests only. The original legacy execution path has not been invoked on any cohort order.

The scoped goal GOAL-NISTSEED-ab8949, question RQ-NISTSEED-ac8851, administrative opening DEC-20261024-46d623, lane BATCH-08d006 and implementation claim are committed and pushed. This resolves the earlier missing administrative lane. It does not approve an experiment. The reserved EXP-NISTSEED-6886da has no scientific specification or trial plan.

## Observed implementation attempts

| Exact proposal | Static syntax | Unittest output | Concrete reported failures |
|---|---|---|---|
| v1 | Completed | 4 tests; 1 failure | Recursive-N and D regular expressions missed actual printed lines. |
| v2 | Completed | 5 tests; 1 failure, 1 error | The trace test used a captured default catalog path; recursive source collection duplicated legitimate archived UIDs. |
| v3 | Completed | 5 tests; 2 errors | Published controls are a dictionary, rather than the assumed list; the parser demanded a nonexistent D=1 catalog record. |

These are three versions of the same unfinished implementation, not independent scientific replications. Exact proposed source and test output are retained under the batch directory and hash-bound in source-bindings.json. The operator materialized each proposal verbatim, ran Python syntax compilation, then `python3 -m unittest experiments/EXP-NISTSEED-6886da/implementation/test_cohort_runner.py`. None of these tests ran the original execute_case, vm, runecpp or checkcertif path. The outer capture command ended with cat; separate native unittest return codes were not retained, so the table reports the preserved unittest output rather than inventing process receipts.

## Specific obstruction and next check

The current runner/checker is **not ready**. Besides the reported errors, static inspection of v3 finds no copied binding manifest, no private-cache redirection, no checker-side verification of all frozen hashes or complete prior-corpus mapping, and no complete mocked driver-to-checker fixture. Five passing helpers would not meet the full task gate; v3 does not even pass those helpers.

The next engineering check must create realistic supervisor launch/environment/command/stdio files, inject a fake at the entire legacy-library boundary, pass the produced admitted and censored outputs through the independent checker, and mutate identity, binding, status, trace, certificate and raw-artifact fields one at a time. It must exercise the actual driver/checker functions. Manually raising an expected exception does not test refusal behavior.

## Runtime calibration observation

The original exact OpenAI/Terra Executor session is verified at medium effort. A requested stronger calibration passed the public per-task resolver, but the native session probe refused before launching with reasoning_effort_policy_mismatch: that helper resolves its default effort before comparing the requested one. The conditional higher-effort amendment remains ineffective. Its refusal is retained; no check has been skipped, and no higher-effort task execution is asserted by this snapshot. The original route remains available.

## What this establishes and leaves open

This snapshot records implementation defects and a concrete readiness gate. It gives no measurement of the legacy program on the twenty-one orders and no common curve property, historical rejection criterion or security conclusion. The original generator/caller and actual candidate visitation remain unknown. Once the implementation is archived, a separate complete frozen measurement packet must pass actual preapproval, receive committed Coordinator approval, and report execution_state: ready before a separate run invocation.

The canonical admission graph changes to show the published administrative lane and the unfinished mock-tested implementation. No mathematical frontier, isogeny, endomorphism or weakness graph changes. Earlier runtime and follow-up reports remain their historical snapshots. The existing problem record and index record this exact obstruction and its exit conditions.
