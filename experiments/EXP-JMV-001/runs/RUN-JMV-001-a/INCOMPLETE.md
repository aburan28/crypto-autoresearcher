# INCOMPLETE RUN -- NOT A VALID RECORD, DO NOT CITE AS EVIDENCE

This directory's contents are the partial output of an Executor task
(TASK-20260906-e2719b, EXP-JMV-001) that was interrupted mid-run by an
account-wide HTTP 429 rate-limit ("session limit", reported reset 5:30pm
UTC 2026-09-07) on 2026-09-07 ~03:38 UTC. Per AGENTS.md rule 3, an
infrastructure failure is never negative (or positive) mathematical
evidence, and per AGENTS.md rule 5, missing data stays missing and is
reported as such -- this file is that report.

**Missing required artifact:** `manifest.yaml`. Without it there is no
`run.status`, no `dispatch_authorization` binding, no `code.commit`
pinning, and no `result.valid`/`certificate` block -- this directory
cannot be read as a terminal run record in its current state.

**What IS present** (produced before the interruption, not independently
verified by the Coordinator, not to be relied upon until re-verified by
whichever session completes or redoes this run): `raw.json`, `cpi_table.csv`,
`controls.json`, `figure1_transcription.md`, `transcription_fidelity.md`,
`analysis.md`, three certificate files under `certificates/`,
`run_conductor_audit.py`, `verify_certificates.py`, `resource_usage.json`,
`stdout.log`/`stderr.txt`/`time_and_stderr.txt`.

**Disposition:** a fresh Executor dispatch for TASK-20260906-e2719b (after
the rate limit clears) will either complete this run by adding the missing
manifest and verifying the above content, or discard and redo it, at that
Executor's discretion -- this directory does not bind that decision. This
marker is committed only so that the working tree is honestly reflected in
git history (no untracked partial state silently sitting outside version
control); it is not a Coordinator snapshot archive and confers no
evidentiary status on anything in this directory. Do not treat any file
here as a completed run until a manifest.yaml with `status: completed_valid`
(or another terminal status) exists and this INCOMPLETE.md has been
removed by whichever task finishes or supersedes this run.
