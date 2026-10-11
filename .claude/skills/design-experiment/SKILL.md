---
name: design-experiment
description: >-
  Convert a selected proposal (IDEA-*) into a specified hypothesis and a
  frozen, approved experiment contract ready for execution. Use after
  ideation, when the Coordinator selects ranked work. Runs under Coordinator
  authority.
---

# Design experiment

Budget estimates are advisory (`docs/research-budget-policy.md`); approval
capacity is not (`AGENTS.md`, "Approval is bounded by execution").

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
2. **Check approval capacity first.** Run
   `python3 tools/portfolio_kpis.py --capacity <GOAL-ID or area:AREA>`. It
   exits 1 when the goal already holds the cap (3) of approved contracts with
   no run. At the cap, the only contracts this turn may approve are ones that
   supersede or withdraw one of the listed ids (`supersedes_experiments` /
   `withdraws_experiments` on the approval decision). Otherwise **do not
   design**: the idea stays `proposed`, the reason goes in the session
   receipt (`--outcome refused_capacity`) and the goal's `next_action`, and
   the proposal record is not edited (`AGENTS.md`, "Approval is bounded by
   execution"). The validator refuses the approval decision anyway
   (`check_approval_capacity`), and a hypothesis plus contract that cannot be
   approved is the backlog this program is paying for. Say in the report
   which ids hold the capacity.
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
     criteria that name a metric the run produces and differ from each other,
     `designed_at`, a `decision_impact` block (`on_positive` / `on_negative`:
     what decision changes on each outcome; the two must differ), and
     required artifacts. No `outcome`, `result`, `conclusion` or `verdict`
     field exists before a run (`check_outcome_not_prewritten`);
   - refuse approval while any of those fields is null (status stays
     `review_required`).
4. Create the experiment directory:
   `experiments/<EXP-ID>/specification.yaml` (plus empty `amendments/` and
   `runs/`).
5. **Make it runnable, in this turn.** Implement or bind the launcher: a
   committed trial plan, an existing command-based runner named in the
   specification, or the code the contract needs. Then check
   `python3 tools/newest_experiments.py --experiment <EXP-ID> --json` and
   require `execution_state: ready`. If that cannot be reached this turn,
   leave the contract `review_required`, record the exact missing piece in
   the report, and stop here: an approved contract nobody can run is the
   backlog this program is paying for (`docs/track-record-review-20261006.md`).
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
   by exact path. Do not dispatch the Executor until its post-commit receipt
   verifies.
9. Push the branch and open or refresh a PR against `main` naming the new
   `H-*`/`EXP-*`/`TASK-*` records (see "Branch and PR hygiene"). A frozen
   contract that exists only in a local commit is not approved — it is
   unpublished.
10. End with a session receipt: `python3 tools/session_receipt.py --skill
    design-experiment --role coordinator --outcome <approved|review_required|
    refused_capacity> --created EXP-...,H-...,TASK-...` (see
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
