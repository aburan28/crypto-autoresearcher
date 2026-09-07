# Harness CI and productive inference

The objective is evidence-producing work per token, not token consumption as
a success metric. These controls do not change ECC priority, campaign budgets,
task authority, write scopes, model-policy requirements or review independence.

## CI gates

`validate.yml` runs focused runtime and CI-gate regressions independently of
the ledger job on Python 3.11 and 3.13. Both jobs install the actual runtime
dependencies; an explicit import check prevents missing dependencies from
turning the focused runtime suite into a skipped green check. Tests use local
fixtures and scripted model responses, not inference credentials or paid calls.

The PR ledger gate compares the head against the event's pinned base commit.
`tools/ci_ledger_gate.py` requires both validator exit codes and complete normal
reports before comparing error identities. Crashes, missing logs, unexpected
exit codes, mismatched error counts and unsupported output formats fail closed.
An inherited schema error remains inherited; a crashed base is not an exemption.
The absolute main-branch ledger gate is unchanged.

Every added or modified PR dispatch queue must render, including proposal and
remediation queues outside goal batches. Historical unrelated queues remain the
responsibility of the main-health census rather than a repeated warning-only PR
sweep. Existing archive and dispatcher checks are not relaxed.

Superseded PR checks are cancelled, dependencies are cached, duplicate checks
are removed, and jobs have timeouts. Raw ledger logs, process statuses, changed
queue diagnostics and JUnit reports are uploaded even after failure. Runtime
regressions do not wait for the ledger job, so a ledger defect cannot prevent
that independent feedback.

## Repeated tool errors

The `api_direct` loop stops before a fourth model request after three consecutive
identical tool rounds in which every result is an explicit tool error or scope
refusal. Equality includes tool names, arguments, full results and error status,
but excludes call IDs and parallel result ordering. A changed argument, changed
result, new user input or successful result breaks the streak.

The stop reason is `repeated_tool_failure`, never `completed`. The receipt carries
the consecutive-round count, a fingerprint, tool names and the operational
classification. The full transcript and journal remain available; per-response
usage metadata and tool statuses are also retained when supplied by the runtime.
Absent usage is recorded as absent, not inferred to be zero.

This detector deliberately does not judge successful repeated reads, successful
polling, timeouts, command exit codes, scientific merit or hypothesis progress.
Those outcomes can be legitimate parts of approved experiments. It does not kill
an external job, restart a task, increase a budget, relax permissions or change a
campaign's status. A Coordinator must resolve the recorded prerequisite before
authorizing a retry. Native Codex/Claude sessions are not covered by this runtime
guard, and alternating error cycles are outside its narrow detection boundary.

## Focused local checks

After installing the optional runtime/test dependencies, the same fast checks
used by CI can be requested locally:

```sh
python3 -m pytest -q tests/test_agent_runtime.py tests/test_agent_progress.py tests/test_ci_ledger_gate.py
```

The tests cover complete/invalid validator reports, inherited versus new error
identities, repeated denials, corrected calls, parallel tool ordering, incomplete
rounds and controls that must not trigger the stall detector. Passing them is
software evidence only, not a scientific result or proof of campaign exhaustion.
