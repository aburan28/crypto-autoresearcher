---
name: design-experiment
description: >-
  Convert a selected proposal (IDEA-*) into a specified hypothesis and a
  frozen, approved experiment contract ready for execution. Use after
  ideation, when the user picks an idea to pursue. Runs under Coordinator
  authority.
---

# Design experiment

Run lifecycle steps 3–5 (`docs/task-lifecycle.md`): hypothesis
specification, experiment design, approval, and handoff.

## Steps

1. Read the selected proposal from `ledger/proposals/`. If the user did not
   name one, list open proposals and ask which to pursue.
2. Dispatch the **coordinator** subagent to:
   - convert the idea into a `hypothesis` record (template in
     `templates/research-records.md`) with explicit test boundary and
     distinguishable outcomes, saved to `ledger/hypotheses/H-<AREA>-<NNN>.yaml`;
   - draft the `experiment` contract with inputs, controls, independent
     variables, primary/secondary metrics, seeds and replication plan,
     budget, stopping and invalidation rules, success and falsification
     criteria, and required artifacts;
   - refuse approval while any of those fields is null (status stays
     `review_required`).
3. Create the experiment directory:
   `experiments/EXP-<AREA>-<NNN>/specification.yaml` (plus empty
   `amendments/` and `runs/`).
4. Present the frozen contract to the user for confirmation before marking
   it `approved` with `approved_by: coordinator` — approval is the gate that
   authorizes execution and spends compute.
5. On approval, write the `handoff` record to `ledger/handoffs/` targeting
   the executor, with budget and completion gate filled in.

## Rules

- After approval the protocol is frozen. Any later change requires a
  versioned `protocol_amendment` in `experiments/<EXP-ID>/amendments/`.
- The success criterion must be decidable from the predefined metrics —
  reject contracts where no possible outcome would count as negative.
