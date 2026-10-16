---
name: audit-runs
description: Independently audit finished runbook sessions, on a schedule or on request. Verify the journal chain and every digest, replay trials sampled from a nonce the executor could not predict, recompute metrics and certificates, and screen Lean statements. The Sonnet sweep validator does the reading, and anything flagged escalates to Opus. Use for audit-runs, checking the math on Haiku or mechanical-tier runs, or before an evidence review cites a runbook session. Never runs trials or changes research state.
---

# Audit runs

The independent half of runbook execution (`docs/runbook-execution.md`). The
mechanical tier ran a session; this skill checks it without trusting it. It
runs no trial, writes no run record and changes no research state.

## When

- On a schedule while runbook sessions are being produced: `/loop 6h
  /audit-runs` in a standing session, or a scheduled task that starts a fresh
  session with `/audit-runs`.
- Before a `/review-evidence` that cites a runbook session.
- When asked to check the math on Haiku (mechanical-tier) runs.

Never in the session that produced the run: independence is the point. Fetch
`origin/main` first so the sessions other branches published are on disk.

## Steps

1. **What is owed.** `python3 tools/runbook.py pending-audits --json` lists
   finished sessions with no audit of their current journal tip, oldest first.
   Take at most the number the user names, default 5. An empty list ends the
   skill with receipt outcome `no_change`.
2. **Deterministic audit, per session.**
   `python3 tools/runbook.py audit <session_dir> --auditor "<role>/<model id>"`
   writes `<experiment>/audits/<AUD-id>/audit.json` and prints the verdict. It
   re-verifies the hash chain and every digest, re-runs every unit's checker,
   recomputes the summary, re-checks Lean receipts, and replays a sample of
   units chosen from a fresh nonce. Pass `--samples N` above the runbook's
   default when the session will feed an evidence review; `detection_power`
   states what the sample size can and cannot detect. Never pass `--nonce`:
   randomness drawn after publication is what the executor could not predict.
3. **The reading half.** Dispatch the `validator-sweep` subagent (Sonnet 5.5,
   policy `audit-sweep`) with the session and audit directories. Dispatch
   `validator` (Opus, `review-adversarial`) instead when the arguments say
   `tier=opus`, when step 2 printed `flagged`, or when the session will be
   cited by an evidence review. The subagent performs the five checks in
   `.claude/agents/validator-sweep.md` (specification fidelity, one blind
   re-derivation, certificate mathematics, Lean statement fidelity, what is not
   covered) and writes `audit-review.yaml` beside `audit.json`.
4. **Report.** Per session: the deterministic verdict and findings, units
   replayed and the miss probabilities, the reader's verdict and `escalate`,
   and `not_covered`. For a flagged or broken session, name the exact finding
   and stop there. The Coordinator decides what follows: a rerun under a new
   session id, an implementation fix, or an invalidation record. Repair
   nothing.
5. **Publish.** Commit only the new `<experiment>/audits/<AUD-id>/`
   directories on this session's branch, push, and open or refresh a PR. An
   audit is a record about a session, never an edit to one.
6. **Receipt.** `python3 tools/session_receipt.py --skill audit-runs --role
   validator --outcome <reviewed|no_change|impeded> --created <AUD ids>`.

## What a clean audit says, and what it does not

`clean` means that:

- the journal chain and every recorded digest hold;
- every unit's checker passes again and the summary recomputes;
- the sampled units reproduced their declared fields;
- Lean receipts, where present, still satisfy their obligations;
- a reader found the runbook faithful to its specification.

It does not mean:

- that the hypothesis is supported;
- that the unsampled units are honest (the audit states the probability that
  fabrication at a given rate escaped the sample);
- that the computation was proved. Replay bounds fabrication; a receipt checked
  by a pinned zkVM verifier in an `execution_proof` step is what proves a
  computation, and the milestones of `docs/execution-proof-chain.md` remain
  open.

An audit never satisfies a `review-adversarial` or `review-breakthrough`
routing rule, and never enters the ledger as a `validation_report`.

## Rules

- A replay writes only under its audit directory. It is a verification, never
  a trial and never a run record.
- Audit directories are write-once. A second audit of the same session is a
  new `AUD-*` directory, and both stay.
- A Lean receipt's `semantic_review` stays `pending` in the formal lane after
  this screen. The screen is recorded, not substituted for that review.
- A missing verifier, absent Lean or a replay-exempt step is `not_covered`. It
  is never a failure of the hypothesis, and never a pass.
