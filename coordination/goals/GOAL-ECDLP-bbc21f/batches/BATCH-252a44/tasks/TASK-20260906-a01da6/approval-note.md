# Approval note -- TASK-20260906-a01da6

## Branch taken

**Approve.** The v2 protocol amendment to `EXP-ECDLP-612fb1`
(`experiments/EXP-ECDLP-612fb1/specification.v2.yaml`, drafted and committed
at `c39430554`, PR #815) is approved as frozen, exactly as offered by the
recommended option below. No revision was requested; the curve re-run was not
skipped (the v2 contract itself does not re-run Stage 3 in any case, per
`field_provenance.changed` and the amendment record's `judgment_calls`, so
"skip the curve re-run" and "approve as frozen" are the same outcome on this
contract's own scope).

## Authorship

Inline Coordinator authorship under the declared fallback:

- `requested_policy`: `coordinator-orchestration-code`
- `resolved_model`: self-reported by the runtime as the model answering this
  session (Claude Sonnet 5, per this session's own system identification)
- `model_verified`: `false` (this authoring role has no mechanism to
  independently verify its own served model identity, exactly as
  `DEC-20260906-1f5b71` and `DEC-20260906-2b1387` disclose for themselves --
  "this coordinator role has no shell and computed no hash" / no independent
  verification path)
- Recorded as a **fallback**, not a degradation: the capability contract
  (tool use, reasoning effort high) is met; `fallback_allowed` is honoured per
  the task's inference block; nothing here was degraded.

This note, `experiments/EXP-ECDLP-612fb1/specification.v2.yaml`'s gate-field
edit, and `ledger/handoffs/TASK-20260906-5e78c7.yaml` are authored by this
task (`TASK-20260906-a01da6`), inline, per its handoff and task card. The
decision record `DEC-20260906-806501` that makes this approval official is
**not** authored here -- it is authored by the ledger-archive task
`TASK-20260906-773a2e`, which archives this task's artifacts alongside the
committed decision.

## Question, options, and answer (verbatim)

User confirmation, obtained 2026-09-06 via the interactive question tool of
the orchestrating session, after PR #815 (design commit `c39430554`) was
pushed.

**Question presented (verbatim):**

> Approve the v2 protocol amendment to EXP-ECDLP-612fb1 (batch-reselected
> fixed-size distinguished-point table)? The v1 batch measured the
> pre-registered T/2 claim as infeasible (S1 failed with CI-separation; F1's
> literal threshold also not reached -- a cell v1's contract didn't name).
> DEC-20260906-1f5b71 requires eight changes before any further run: (a) a
> ceiling-feasibility gate G3 from exact basins, run before interpreting any
> re-selected arm; (b) a non-vacuity guard + relative tolerance on S1; (c) a
> one-sided S2; (d) the headline reported as a full frontier tuple charging
> working storage, never a bare ratio; (e) a corrected batch-pool heuristic
> using the measured admitted-walk count; (f) a pool cap enforced per
> admission; (g) a permanent negative-fixture regression test; (h) a cheap
> a-scan run first to locate any feasible operating point. New run grid:
> T_sel in {0.65T, 0.75T}, N in {2^24, 2^30}, a=1/4, r=2, k=4, 5 seeds (~17
> runs). v1's own 0.51 prediction is retracted and replaced by the measured
> oracle floor (~0.55), flagged unverified. Approval authorizes execution: a
> committed Coordinator decision marks v2 approved and writes the executor
> handoff -- nothing runs on this answer alone.

**Options offered:**

1. "Approve as frozen (Recommended)"
2. "Approve, but skip the curve re-run"
3. "Revise before approving"
4. "Do not approve; stop here"

**Answer, verbatim:** "Approve as frozen (Recommended)"

## Diff scope, exact

Per the task card's `write_scope` and the handoff's `constraints`, exactly
four fields of `experiments/EXP-ECDLP-612fb1/specification.v2.yaml` were
changed, plus one field added:

| field | before | after |
| --- | --- | --- |
| `status` | `review_required` | `approved` |
| `approved_by` | `null` | `coordinator` |
| `frozen` | `false` | `true` |
| `execution_authorized` | `false` | `true` |
| `approval_note` | (pre-approval "NOT APPROVED" text) | replaced with the approval text, which preserves the full pre-approval note **verbatim** inside itself under a "PRE-APPROVAL NOTE, PRESERVED VERBATIM" heading |

**Why exactly these fields, and no others:** these are the same four gate
fields (plus the note) that v1's own approval (`DEC-20260906-2b1387`, applied
to `specification.yaml`) changed, and they are the only fields the frozen
design contract names as under Coordinator approval authority
(`invalidation_rules`: "Execution while status is not approved or
execution_authorized is false: no run under this contract is evidence").
Every other field of the v2 contract -- `field_provenance`, all eight
amendment items (a)-(h) in `discharges`/`controls`/`definitions`,
`instrument`, `inputs`, `controls`, `metrics`, `preregistered_prediction`,
`budget`, `stopping_rules`, `invalidation_rules`, `success_criterion`,
`falsification_criterion`, `required_artifacts`, `cost_model`,
`interpretation` -- is a substantive protocol term that was drafted and
committed at `c39430554` under the design task's own authority and reviewed
by the user in the question above; touching any of them here, after the
question was answered, would silently change a frozen protocol post-hoc,
which is forbidden (`AGENTS.md` / `CLAUDE.md`: "Never change success
criteria after observing outcomes without a versioned `protocol_amendment`
record" -- and no run has even occurred yet to justify any such change).
`version` stays `2`: approval does not mint a new contract version, only
authorizes execution of the one already drafted.

## What this note does not do

This note is not itself the official approval. The official approval is
`DEC-20260906-806501`, a committed `coordinator_decision` record, authored by
the ledger-archive task `TASK-20260906-773a2e` -- not by this task. This
note, the gate-field edit, and the executor handoff
(`ledger/handoffs/TASK-20260906-5e78c7.yaml`) are the artifacts that decision
cites as evidence of what was authorized and why; nothing here is durable
until that decision is committed and the post-commit verifier accepts it,
per `AGENTS.md` "Concurrency: many agents, many worktrees" (content-first
verification) and rule 7 (nothing is official until the dispatcher's
post-commit verifier accepts it).
