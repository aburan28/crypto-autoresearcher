# COORD-VERIFY-PREFREEZE-v11 — Coordinator independent re-derivation of the
# load-bearing number in RT-PREFREEZE-EXP-SSIQ-a85692-v11 (PF-11)

GOAL-SSIQ-001 BATCH-014. Companion to
`RT-PREFREEZE-EXP-SSIQ-a85692-v11.md` (task `TASK-20260807-43d16f`,
verdict `DO-NOT-FREEZE`).

**Why this note exists.** PF-11 is the finding that redirects the batch: it
asserts the drafted sweep's headline question is already answered by
archived data, before any compute. A finding that decides a batch's
direction is exactly the kind this lineage requires be checked rather than
taken on trust (goal record's standing BATCH-013 obligation: a finding
derived from first principles and confirmed with zero exceptions against raw
data, then reproduced on an independent re-execution, is qualitatively
stronger than a pattern observed once). This is that independent
re-execution. It is a Coordinator arithmetic check against the committed
artifact only — it is **not** a second adversarial review, it originates no
claim, and it does not upgrade the campaign's evidence tier.

## What was recomputed

Source artifact, read directly from the committed tree:
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`

Independent Python over `per_vertex_records`, no reviewer code reused, no
intermediate figure taken from the report:

| quantity | Coordinator recomputation | RT-PREFREEZE-v11 | agree? |
|---|---|---|---|
| `per_vertex_budget_seconds` | 15.0 | 15.0 | yes |
| `n_records` | 194 | 194 | yes |
| `n_timed_out` | 0 | 0 | yes |
| `n_resolved` | 194 | 194 | yes |
| min `wall_seconds` over `delta_E >= 5` | 1.392405 s | 1.392 s | yes |
| vertices with `wall_seconds < 1.2` | 2, both `delta_E = 2` | 2, both `delta_E = 2` | yes |
| natural completions at b=1.1 | 0 | 0 | yes |
| natural completions at b=1.2 | 2 (0 with `delta_E>=5`) | 2 | yes |
| natural completions at b=1.3 | 7 | 7 | yes |
| natural completions at b=1.4 | 45 (4 with `delta_E>=5`) | 45 (first `>=5` appearances) | yes |
| natural completions at b=1.45 | 115 (**36** with `delta_E>=5`) | 115 (**30** with `delta_E>=5`) | count differs |
| natural completions at b=1.7 | 194 | 194 | yes |
| total vertices with `delta_E >= 5` | **80** | **78** | count differs |

## Verdict on PF-11

**PF-11 is CONFIRMED on its load-bearing content.** The earliest natural
completion of any `delta_E >= 5` vertex is at 1.392405 s, which is above both
drafted sweep points (1.1 s and 1.2 s). The only two vertices completing
below 1.2 s both carry `delta_E = 2`. Therefore v11 as drafted could not
have observed a first `delta_E >= 5` natural completion at either sweep
point under any timing outcome, and its headline question was settled in
advance by data already in the tree. The DO-NOT-FREEZE verdict is
well-founded on this finding alone, independently of PF-12/13/14.

## Two count discrepancies, recorded rather than reconciled

Two subsidiary counts differ between the report and this recomputation:
the total `delta_E >= 5` population (80 here, 78 in the report) and the
`delta_E >= 5` subset completing under b=1.45 (36 here, 30 in the report).
Both are subsidiary: neither enters PF-11's argument, whose load-bearing
quantities (1.392405 s; 2 vertices under 1.2 s, both `delta_E = 2`) agree
exactly. The likely cause is a differing inclusion rule at the population
boundary (e.g. a `resolved`/`non_fp_rational` filter, or a strict-vs-inclusive
threshold), but **this note does not guess and does not reconcile them**:
per AGENTS.md rule 4 and rule 8 the discrepancy is recorded as an
observation for the round-2 reviewer to resolve, not silently harmonised in
either direction.

**Obligation carried to round 2:** the revised amendment's own pre-registered
prediction curve (PF-11's and PF-14's recommended fix) must state its exact
inclusion rule for the `delta_E >= 5` population and its threshold
convention, so that this ambiguity cannot propagate into a frozen
prediction. Whichever of 80/78 and 36/30 is correct under the stated rule,
the rule itself must be in the frozen text rather than inferred by a reader.

## Scope

This note establishes nothing about the supersingular isogeny problem, the
`p^{1/3+o(1)}` exponent budget, lever L4, or any `delta_E` mechanism. It
establishes only that one arithmetic finding about an already-committed run
artifact reproduces independently, and that two subsidiary counts do not.
No hypothesis status changes and no experiment is approved or frozen by it.

```yaml
provenance:
  role: coordinator
  task: TASK-20260807-43d16f (companion check; the task itself is the Red Team review)
  batch: BATCH-014
  goal: GOAL-SSIQ-001
  artifact_read: experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json
  method: independent Python recomputation over per_vertex_records
  independence_cap: >-
    NOT an independent adversarial review. Same session and same model family
    as the Coordinator that opened this batch. It checks arithmetic against a
    committed artifact and nothing else; it does not corroborate the report's
    judgement, only one of its numbers.
  recorded_at: '2026-08-07'
```
