# Research budgets and machine protection

The user's 2026-09-06 instruction makes routine research budgets advisory for
this researcher, across all areas. Continue justified work within the authorized
research scope without repeated CPU-time, stage-budget or batch-budget approvals.
This supersedes older budget-exhaustion instructions. ECC campaign totals remain
unlimited; non-ECC estimates are also not automatic spending gates.

Time, CPU and run-count estimates may be null. Finite estimates remain useful
for ranking, scheduling and measured-versus-predicted cost comparisons, but do
not stop launches. Stage estimates are optional and need not sum exactly.
Memory and concurrency limits still protect the machine. Explicit caller or
locked-plan process timeouts remain watchdogs; an agent handoff can use
`runtime_limits: {wall_clock_seconds: 3600, reason: "checkpoint this worker"}`.
A watchdog stops a worker, not the campaign. Preserve its checkpoint and continue
autonomously when justified; an outage or timeout is never mathematical evidence.
The agent's step boundary and external API/tool limits remain operational limits.

## Exceptional restriction after months without progress

The minimum is **90 days**. A Coordinator may activate a scoped research cap
only after a committed assessment cites evidence of no meaningful progress
throughout that interval. New measurements, reproducible negative results,
resolved proof obligations and discriminating controls can all be progress;
paperwork counts and elapsed time alone cannot establish stagnation. Missing
telemetry, inactivity or infrastructure downtime is not a finding of stagnation.
No timer automatically retires a campaign or changes a hypothesis status.

The shared policy validates `budget.enforcement: stagnation` only with:

```yaml
stagnation_review:
  assessed_by: coordinator
  decision_id: DEC-YYYYMMDD-abcdef
  assessed_at: YYYY-MM-DD
  last_progress_at: YYYY-MM-DD
  no_progress: true
  infrastructure_only: false
  evidence_refs: [path/to/committed/assessment-evidence.md]
  scope: exact task or lane being restricted
  rationale: evidence of sustained stagnation and alternatives considered
  next_action: concrete successor or test that would clear the restriction
```

The cited decision must be committed, carry `decision: approve`,
`decided_by: coordinator`, the identical `stagnation_review` block, the
current target in `target_ids`, and exact numeric limits in `approved_budget`
(the budget mapping excluding `enforcement` and `stagnation_review`).
Evidence paths must also exist in that committed tree; inline self-grants and
uncommitted files cannot enable enforcement.

The assessment must be at least 90 days after the last documented progress and
no more than seven days old at enforcement. A stale or malformed restriction
must be reassessed, never silently renewed. A Coordinator must reassess when
new progress arrives. This is a review gate, not an automated scientific verdict.
`orchestration/research_budget.py` is the single source of the thresholds.

## What stays frozen

Approval, exact write scope, scientific controls, fixed sample counts, seeds,
locked trial lists, zero-run tasks and immutable receipts still bind. An advisory
run-count estimate does not authorize extra confirmatory samples or fishing for
a favorable result. Scientific changes require an additive amendment; ordinary
continuation does not require another user budget approval. Never relabel an old
run under the new runtime policy, rewrite archived budgets, or claim a watchdog
was enforced if it was not. New runs record the runtime policy they used.

Old bespoke experiment scripts may enforce their own frozen stopping rules.
Before continuing such a script, the Coordinator makes the minimal additive
amendment separating its scientific stopping criteria from obsolete spending
caps. The shared harness cannot safely rewrite arbitrary historical programs.
