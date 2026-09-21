# BATCH-d15fe0 input capsule

## Authoritative task boundary

This batch opens a bounded fresh-ideation search for `RQ-SSI-001` after the
verified close of `BATCH-042`. The prior FC0/QM lane remains host/source/
probability gated; its own decision bars another zero-compute tightening pass.
The batch searches a disjoint structural portfolio and does not authorize an
experiment, a hypothesis, a protocol, or an Executor.

## Inputs that define the current boundary

- `ledger/questions/RQ-SSI-001.yaml`
- `ledger/evidence/EV-SSI-042.yaml`
- `ledger/decisions/DEC-20260730-040.yaml`
- `knowledge/open-problems/KN-OPEN-013.md`
- `knowledge/open-problems/KN-OPEN-014.md`
- `knowledge/open-problems/KN-OPEN-015.md`
- `knowledge/literature/KN-LIT-074.md`
- `knowledge/literature/KN-LIT-078.md`
- `knowledge/literature/KN-LIT-079.md`
- `knowledge/literature/KN-LIT-069.md`
- `knowledge/literature/KN-LIT-071.md`
- `docs/inventor-protocol.md`
- `docs/target-result-profile.md`
- `templates/research-records.md`

The open-problem entries are reported context. `KN-LIT-074` is conditional on
GRH, and the `p^(1/4)` claims in `KN-LIT-078` / `KN-LIT-079` are reported
heuristic/expected baselines in their stated path-finding settings. Do not
convert any of them into a broader claim.

## Existing paths excluded from repetition

- `ledger/proposals/IDEA-20260725-001.yaml`
- `ledger/proposals/IDEA-20260725-002.yaml`
- `ledger/proposals/IDEA-20260725-003.yaml`
- `ledger/proposals/IDEA-20260729-001.yaml`
- `ledger/proposals/IDEA-20260801-007.yaml`
- `ledger/proposals/IDEA-20260803-82b2b7.yaml`
- `ledger/proposals/IDEA-20260803-48e258.yaml`

The FC0/CollimationSieve, stopping-trace collision, CSIDH collision-surface,
orientation residual, SQIsign transcript classification, path-rebaseline, and
P13 crossover routes are all excluded as described in `SCOPE-DECISION.md`.

## Required future proposal shape

The Idea Generator produces exactly three schema-complete idea records at the
three already allocated paths. They are proposals only. Every record must:

1. name a distinct structural object and a decision-changing mechanism;
2. use object-first generation, a lossy-projection test when applicable, and
   pre-registered null controls;
3. set novelty to `unverified` and document the non-duplication screen;
4. state `dominated_by` and a quantitative `sota_delta` without unchecked
   nulls;
5. give target time and memory exponents against the reported `p^(1/4)`
   classical/quantum baselines where that comparison is relevant, and otherwise
   state why no exponent comparison applies;
6. state named falsifiable heuristics, a concrete validation route, null
   controls, and an honest cost/budget; and
7. include a complete `proof_search_map` for any proof-oriented idea.

No proposal may present toy, conditional, or literature context as
crypto-scale validation. An unavailable source, untestable heuristic, or
unknown cost stays explicitly unknown.

## Validation baseline

`python3 tools/validate_ledger.py` currently reports 20 unrelated base errors.
Those failures are not repaired or absorbed here. This branch must add none;
the control-plane snapshot requires PR-scoped hygiene in addition to
JSON/YAML parsing and dispatch rendering.
