# TASK-20260802-4bd310 — `failed_infrastructure`

The Executor for the batch's PRIMARY objective (NC-3/NC-6, the campaign's first
test of P0 rather than of cost) was terminated mid-run by an external API
session limit at ~2026-08-03T01:10Z, before any run directory was created.

**Under AGENTS.md rule 5 this is not mathematical evidence.** It says nothing
about Heuristic 1, about the random-integer model, about P0, or about the
attack. No statistic was computed to a verdict, and none may be reported.

## State left behind

`experiments/EXP-HEUR-d640d9/implementation/heuristic_tail.py` only —
uncommitted work in progress. **No `runs/` directory exists**, so there is no
partial receipt to quarantine and nothing that could be mistaken for a result.

## Successor

`TASK-20260803-4946a5`, re-running under the *same* contract frozen at
`dfe285d4`. The protocol is unchanged; this is a re-execution after an
infrastructure failure, not a redesign.

## Note on the standing instruction

The user directive of 2026-08-03 ("exhaustion is not allowed") makes explicit
what the inventor protocol already required: this failure does not close the
goal, does not become a negative result, and does not justify END-2. It is
re-dispatched. The directive binds effort, not outcome — it lowers no evidence
standard and makes no result more likely to be positive.
