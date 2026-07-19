---
name: review-evidence
description: >-
  Coordinator review of a completed experiment: validate run records, write
  the evidence record, assign evidence strength, and record the official
  decision (replicate/expand/refine/support/weaken/reject_scoped/
  inconclusive/pause). Use after /run-experiment completes.
---

# Review evidence

Run lifecycle steps 8–10 (`docs/task-lifecycle.md`): analysis, Coordinator
review, and synthesis.

## Steps

1. Read the experiment's `execution_report`, run manifests, and raw results
   from `experiments/<EXP-ID>/`.
2. Dispatch the **coordinator** subagent to:
   - re-verify validity before interpreting anything (run count, schema,
     seeds, raw/summary agreement, controls). Invalid or incomplete run
     sets go back to the Executor with concrete defects — stop there;
   - write `experiments/<EXP-ID>/analysis.md` strictly separated into
     Observation / Comparison / Inference / Limitation;
   - verify certificates: any run claiming a solve/relation must carry a
     `verified: true` certificate (`docs/claims-and-verification.md`); a
     failed or missing certificate on a claimed success invalidates that run
     rather than counting as evidence;
   - create the `evidence` record in `ledger/evidence/EV-<AREA>-<NNN>.yaml`
     with direction, strength (per the hierarchy in
     `docs/evidence-and-reproducibility.md`), `claim_tier` (never exceeding
     what the runs' parameters allow), `certificate_refs`, boundaries, and
     unresolved confounds;
   - record the `coordinator_decision` in `ledger/decisions/` choosing one
     transition: replicate | expand | refine | support | weaken |
     reject_scoped | inconclusive | pause, with rationale, evidence refs,
     limitations, and explicit next actions;
   - update the hypothesis record's status accordingly.
3. If the decision warrants promoting a durable finding into the knowledge
   corpus, add it via the `/curate-knowledge` conventions (type
   `internal_finding`, citing the EV/DEC IDs).
4. Report to the user: the decision, the evidence strength, the exact scoped
   claim the data justify (use the negative-result phrasing rules from
   `docs/evidence-and-reproducibility.md`), and the next actions.

## Rules

- Only the coordinator subagent changes hypothesis status.
- Claims must be scoped to the tested curves, bit sizes, solver, parameters,
  and budget. Toy-scale results never become crypto-scale claims.
- Surprising or high-impact results get `replicate`, not `support`, on first
  observation.
