# RUN-PEC-d7979c-a — INCOMPLETE, NOT A RESULT

**Status: `failed_infrastructure`. This directory is NOT a run receipt and must
never be cited as one.**

## What happened

The Executor for TASK-20260802-459b18 was terminated mid-run by an external API
session limit (`You've hit your session limit · resets 1:10am (UTC)`), on
2026-08-03 shortly before 01:13Z. The termination is an infrastructure event in
the harness that runs the agent. It is **not** a stopping rule firing, not a
budget (budgeting is retired repo-wide), and under **AGENTS.md rule 5 it is not
mathematical evidence about anything** — not about FC-4, not about L1, not about
the entry-weighted correction, and not about the attack.

## Why this directory is preserved rather than deleted

It contains real bytes produced by a real partial execution: `raw-result.json`
parses and carries the contract binding and preamble, and `stdout.log` holds
4657 bytes of genuine output. Deleting measured output because a crash
interrupted it would destroy evidence, so it is kept.

## Why it is NOT the run

The receipt bundle is incomplete: `manifest.yaml`, `execution_report.yaml`,
`stdout.txt` and `stderr.txt` were never written, and no statistic reached a
recorded verdict against its pre-registered threshold. A partial receipt cannot
be validated, and EXP-PEC-d7979c pre-states that **any truncation of
NC2d-PROPER yields `INCONCLUSIVE`** — so nothing here can become a retirement of
FC-4 by having stopped early.

## What supersedes it

The re-run is **`RUN-PEC-d7979c-b`**, dispatched as TASK-20260803-d164ba under
the *same* frozen contract at commit `dfe285d4`. The contract is unchanged: this
is a re-execution after an infrastructure failure, not a redesign, and nothing
in the protocol was adjusted in response to anything visible in this directory.

A new run id is used rather than overwriting `-a` because artifacts are
immutable and a crashed attempt is part of the record.
