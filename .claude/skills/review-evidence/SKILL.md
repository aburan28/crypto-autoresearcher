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
   - before any adverse call (`weaken`, `reject_scoped`), seek the strongest
     checkable refutation artifact the result admits — counterexample
     certificate, then derivation note, then empirical-only — per the
     "Refutation artifacts" section of `docs/claims-and-verification.md`.
     Archive the artifact with the analysis (it rides the snapshot/ledger
     commit) and set `proof_status`/`proof_refs` accordingly. Not every
     result can be proved: `empirical_only` is legitimate but must be
     declared, and an unreplicated empirical-only refutation takes `weaken`
     + replication, not `reject_scoped`;
   - create the `evidence` record in `ledger/evidence/EV-<AREA>-<NNN>.yaml`
     with direction, strength (per the hierarchy in
     `docs/evidence-and-reproducibility.md`), `claim_tier` (never exceeding
     what the runs' parameters allow), `certificate_refs`,
     `proof_status`/`proof_refs`, boundaries, and unresolved confounds;
   - record the `coordinator_decision` in `ledger/decisions/` choosing one
     transition: replicate | expand | refine | support | weaken |
     reject_scoped | inconclusive | pause, with rationale, evidence refs,
     limitations, and explicit next actions;
   - update the hypothesis record's status accordingly.
3. Run the knowledge-promotion gate. Every review answers the promotion
   question explicitly in the decision record's `knowledge_promotion` field
   (schema in `templates/research-records.md`):
   - Promotion is REQUIRED when the decision is `support` or `reject_scoped`
     and the evidence strength is `replicated` or `strong`: create a
     `knowledge/findings/KN-FIND-NNN.md` entry via the `/curate-knowledge`
     conventions, citing the EV-/DEC-/EXP- IDs. A proven scoped negative
     (`reject_scoped`) is a durable boundary and is promoted like a positive.
   - Promotion is CONSIDERED when an `inconclusive` or `pause` decision
     exposes a precisely statable unknown (→ `KN-OPEN`), or when an
     instrument/method has now been validated across experiments (→
     `KN-TECH`).
   - If nothing is promoted, record why in `knowledge_promotion.
     not_warranted` — one concrete line, not "n/a".
4. The Coordinator runs an isolated ledger archive task after every required
   review. It commits the review reports, analysis, evidence record, decision
   record, and any hypothesis or knowledge update by exact path. The official
   transition is blocked until the dispatcher verifies that commit's parent,
   diff, record IDs, and file hashes.
5. Report to the user: the decision, the evidence strength, the exact scoped
   claim the data justify (use the negative-result phrasing rules from
   `docs/evidence-and-reproducibility.md`), and the next actions.

## Rules

- Only the coordinator subagent changes hypothesis status.
- Claims must be scoped to the tested curves, bit sizes, solver, parameters,
  and budget. Toy-scale results never become crypto-scale claims.
- Surprising or high-impact results get `replicate`, not `support`, on first
  observation. Symmetrically, rejecting a theory deserves the same
  skepticism as confirming one: `reject_scoped` requires a checkable
  refutation artifact (counterexample certificate or derivation note) or
  replicated empirical evidence — never a single unreplicated
  empirical-only run.
- A working-tree-only evidence or decision record is incomplete, even when its
  content appears valid.
- A decision record with an unfilled `knowledge_promotion` field is
  incomplete: proven results that never reach `knowledge/findings/` are lost
  to future ideation and novelty checks.
