---
name: design-experiment
description: >-
  Convert a selected proposal (IDEA-*) into a specified hypothesis and a
  frozen, approved experiment contract ready for execution. Use after
  ideation, when the Coordinator selects ranked work. Runs under Coordinator
  authority.
---

# Design experiment

Budget estimates and the approved-unrun backlog are advisory
(`docs/research-budget-policy.md`; `AGENTS.md`, "Approval is bounded by execution").

Run lifecycle steps 3–5 (`docs/task-lifecycle.md`): hypothesis
specification, experiment design, approval, and handoff.

## Steps

1. Read the selected proposal from `ledger/proposals/` — locate it through the
   generated index (`python3 tools/build_ledger_index.py` writes
   `ledger/.index/proposals.jsonl`; grep that, not the corpus). If the user did
   not name one, the Coordinator ranks open proposals and selects the next
   justified candidate under AGENTS.md standing user authorization. Do not ask
   for per-idea selection or approval. Before designing, merge `origin/main`
   into the working branch (merge, never rebase) so the hypothesis and contract
   are drafted against current ledger state — see "Branch and PR hygiene" below.
2. Inspect `python3 tools/portfolio_kpis.py --goal-backlog <GOAL-ID or area:AREA>`
   to rank ready execution work. The command reports backlog and always exits
   successfully; it does not limit design or approval.
3. Dispatch the **coordinator** subagent to:
   - mint ids with `python3 tools/allocate_id.py --next hypothesis --area <AREA>`
     and `--next experiment --area <AREA>` (confirm each with `--check`; never
     pick "the next free number");
   - convert the idea into a `hypothesis` record (template in
     `templates/research-records.md`) with explicit test boundary and
     distinguishable outcomes, saved to `ledger/hypotheses/<H-ID>.yaml`;
   - draft the `experiment` contract with inputs, controls, independent
     variables, primary/secondary metrics, seeds and replication plan,
     budget, stopping and invalidation rules, success and falsification
     criteria, and required artifacts;
   - write the blocks of `docs/confound-control.md`: a `variable_ledger`
     with an A/A comparison, `prediction_provenance`, and, when a claim
     crosses a map, `transfer_obligations` with the `transfer` skill's
     assessment;
   - refuse approval while required scientific-contract fields, including
     those blocks, are incomplete (status stays `review_required`). Advisory
     research estimates and unlimited campaign budgets may be null under the
     current budget policy; that alone does not prevent approval.
4. Create the experiment directory:
   `experiments/<EXP-ID>/specification.yaml` (plus empty `amendments/` and
   `runs/`).
5. **Make it prospectively runnable, in this turn.** Implement or bind the
   launcher, trial plan, executor handoff and dispatch queue. Before approval,
   provide preview copies of the exact proposed final bytes in a packet for
   `python3 tools/experiment_preapproval.py --packet <PACKET.json>`. Require
   `approvable: true`; the probe checks hashes, archive coverage, execution
   route and lawful lane without authorizing a run. If it refuses, leave the
   contract `review_required` and record its exact blockers. Do not interpret
   the ordinary execution selector's exclusion of an unapproved experiment
   as a readiness result.
5a. **Runbook, so the mechanical tier can run it.** Dispatch
   `experiment-director` in `compile` mode (`docs/model-tiers.md`): it writes
   `experiments/<EXP-ID>/runbook.yaml` (`docs/runbook-execution.md`) and a
   task card under `task-cards/`, and returns both lint outputs. Require
   `LINT OK`; resolve any value it reports missing in the specification. The
   approval decision carries `runbook_sha256`, the executor task's
   `write_scope` includes `experiments/<EXP-ID>/runbook-sessions/` and
   `reports/`, and the handoff names `inference.policy: executor-mechanical`;
   once approved, `tools/task_card.py lint` must print `CARD OK`. If it cannot
   lint clean this turn, commit no runbook: the task stays
   `executor-implementation`.
6. Under the standing user authorization in `AGENTS.md`, the Coordinator
   records approval of the complete, runnable, frozen contract with
   `approved_by: coordinator` and a committed approval decision. Do not ask
   for user confirmation. Cite the standing authorization as the user approval
   basis; the Coordinator still checks protocol completeness and declared
   resource limits before authorizing dispatch. Freeze scientific tests, not
   arbitrary CPU allowances. Report the concrete approved scope as a progress
   update, not as a permission question.
7. On approval, write the `handoff` record to `ledger/handoffs/` targeting
   the executor, with the completion gate filled in. Omit budget fields that
   are null; a block of `null`s is not a budget.
8. The Coordinator runs an isolated snapshot archive task that commits the
   selected proposal, hypothesis, frozen specification, launcher, and handoff
   by exact path. After its receipt verifies, require `python3
   tools/newest_experiments.py --experiment <EXP-ID> --json` to report
   `execution_state: ready` before dispatch. A mismatch stops dispatch and
   requires an additive correction. The preapproval probe never replaces the
   ordinary selector, dispatcher or live-claim checks.
9. Push the branch and open or refresh a PR against `main` naming the new
   `H-*`/`EXP-*`/`TASK-*` records (see "Branch and PR hygiene"). A frozen
   contract that exists only in a local commit is not approved — it is
   unpublished.
10. End with a session receipt: `python3 tools/session_receipt.py --skill
    design-experiment --role coordinator --outcome <approved|review_required>
    --created EXP-...,H-...,TASK-...` (see
    `docs/session-receipts.md`).

## Branch and PR hygiene

Designing an experiment creates shared records (hypothesis, specification,
handoff), so every run of this skill also pulls in `main` and surfaces the
work as a PR:

- **Before designing:** `git fetch origin && git merge origin/main` — merge,
  never rebase. If the merge conflicts, stop and report; never resolve a
  conflict by editing a record. Re-run `tools/validate_ledger.py` after the
  merge.
- **After the snapshot archive:** `git push -u origin <branch>`, then open or
  refresh a PR against `main` with the runtime's PR tool, titled
  `experiment: <EXP-ID>` and naming the `H-*`/`EXP-*`/`TASK-*` ids in the
  body. Use `gh pr create` only where `gh auth status` succeeds; a Cursor
  cloud session uses its PR tool, and a session with neither reports the
  pushed branch and stops.

## Experiment class patterns

Two experiment classes carry the highest evidentiary risk and get first-class
design treatment. The canonical exemplar for both is the target-result profile
in `docs/target-result-profile.md` (Wesolowski's p^{1/3+o(1)} supersingular
isogeny result): a conditional theorem whose heuristic is validated
experimentally at cryptographic scale, paired with a concrete-cost table under
explicitly flagged optimistic assumptions.

### Heuristic-validation experiment

Use when a hypothesis conditions a theorem or algorithm on an explicitly
stated heuristic — e.g. "the degree of the smallest isogeny E → E^{(p)} is
B-smooth with probability u^{-u(1+o(1))}, matching a uniformly random integer
of its size". The contract must include:

- **The heuristic, stated exactly.** Numbered and formally stated, with its
  quantifiers, the distribution it concerns, and the rigorous results it
  interpolates between (e.g. a proven bound on the quantity combined with a
  classical distribution theorem such as Canfield–Erdős–Pomerance).
- **A pre-registered prediction and its source.** The frozen contract names
  the theoretical prediction under test (e.g. Ψ(X,B) = X·u^{-u(1+o(1))}, or
  the Dickman–de Bruijn CDF ρ(u)) and cites the publication it comes from.
  The prediction is written before any run and is never adjusted afterward.
- **Scale access.** State how the design reaches relevant scale — for example
  an exact correspondence (Deuring: maximal orders ↔ supersingular curves)
  that permits sampling at larger parameters. If a smaller scale is used, the
  test boundary and any transfer assumptions must be stated explicitly.
- **Sample-size justification.** Derive the sample count from the smallest
  predicted probability the experiment must resolve. If the predicted tail
  probability is q, plan enough samples that the expected tail count is
  meaningfully larger than 1, and state that multiple.
- **Comparison metric and tail checks.** Predefine how the empirical and
  predicted distributions are compared (e.g. empirical CDF of the largest
  prime factor vs. ρ(u)), including explicit checks on extreme samples (e.g.
  the smoothest observed sample vs. its predicted probability).
- **Controls.** At minimum: a synthetic control drawing the same statistic
  for genuinely uniform integers of matched size (validates the sampler and
  the metric); independence of instances and seeds; and a second parameter
  set at a different scale so the comparison is not scale-specific.

### Cost-model measurement experiment

Use when the deliverable is a concrete-cost table rather than a binary test
of a prediction. The contract must include:

- **Measured vs. modeled separation.** Every reported number is labeled
  measured (instrumented run with manifest) or modeled (cost formula, with
  the formula and its source named). The two never mix in one column.
- **Optimistic-assumption disclosure.** Each optimistic simplification (e.g.
  "one field operation per table entry", tightness of a lower-bound success
  probability) is listed explicitly with the direction of its bias. Tables
  produced under such assumptions are labeled bounds, not predictions.
- **Memory accounting.** Peak memory is a first-class metric alongside time:
  the dominant data structure is sized analytically (e.g. a table of
  M = Ψ(X,B)·X entries) and measured `peak_rss_bytes` is reconciled against
  it. Where a time–memory tradeoff exists (e.g. van Oorschot–Wiener), state
  it with its interpolation range.
- **Hidden-overhead honesty.** If the headline complexity hides a
  superpolynomial factor inside an o(1) term, the contract says so and the
  deliverable reports it.
- **Standardized parameter sets.** Concrete costs are reported at fixed,
  named parameter sets (e.g. NIST-I/III/V security levels), with affected-
  vs-safe scope stated for any claimed cryptanalytic impact.

## Rules

- After approval the protocol is frozen. Any later change requires a
  versioned `protocol_amendment` in `experiments/<EXP-ID>/amendments/`.
- For heuristic-validation and cost-model experiments, the pre-registered
  prediction or cost model is part of the frozen contract. Adjusting it
  after any run creates a new record through the amendment path — it is
  never an edit of the frozen prediction, and runs already executed are
  never silently re-scored against the new one.
- The success criterion must be decidable from the predefined metrics —
  reject contracts where no possible outcome would count as negative.
- Only one-factor, factorial or absolute comparisons and out-of-sample
  predictions carry success or falsification criteria; an A/A comparison
  sets their noise floor; confounded and in-sample ones are reported, never
  decisive.
