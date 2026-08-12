## Handoff: SGCP V8 exact-commit accounting review

### Claim or task

Audit exact commit `a1719f7d910d3cc454911a55ceb8b30d833a0b2d`
for accounting integrity and readiness for launch-plan design only.

### Status

`OBSERVATION`; decision `REVISE` before launch-plan design. Execution remains
unauthorized, `maximum_runs=0`, and the claim remains `HYPOTHESIS`,
`TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- Only exact committed scoped blobs were substantively reviewed.
- Logged tests were inspected but not rerun; all nine recorded hashes match.
- In-process counters are combinatorial only, not field/group operations, CPU,
  RSS, allocator/parser memory, disk, I/O, or bandwidth.
- An incomplete receipt is invalid and cannot support a mathematical outcome.

### Evidence so far

- Ledger state is correctly `review_required`, with `runs=[]` and zero budget.
- Source-sized admission precedes generic traversal, and report size fallbacks
  fail closed for ordinary bounded metadata.
- Completeness and actual-to-reservation dominance are validity checks for the
  counters currently covered.
- Aggregate phases carry expected, completed, and failed unit receipts.
- The V8 log records 54 focused passes and 197/198 repository passes, with the
  sole failure attributed to the preserved SGCP-EMBED-001 run directory.

Findings:

1. `BLOCKER`: `graph_cells` is a reservation-shaped potential count rather
   than exact executed dimensions. The verifier charges
   `candidate_count + C(candidate_count,2) + candidate_count^2`, while the
   conflict loop and pair-output matrix operate on eligible candidates. The
   frozen row has 31 candidates and 12 eligible vertices, so the corresponding
   executed dimensions are `31 + C(12,2) + 12^2 = 241`, not 1,457. The
   1,457 value remains below the 1,855 reservation and is therefore accepted
   despite being mislabeled exact actual work.
2. `HIGH`: graph and expansion work is charged only after reconstruction
   completes. A mid-function exception can therefore mark the receipt
   incomplete while omitting already executed graph/expansion work, contrary
   to the promised partial lower-bound diagnostic.
3. `LOW`: fail-closed producer diagnostics retain `version-7` wording.

### Failure modes

- A valid report can overstate graph actual work while satisfying dominance.
- A failed B6/B8 verification can hide completed graph or expansion work.
- Frozen B4 is the only standalone complete five-field oracle; B6/B8 secondary
  objective fields remain replay-confirmed.
- B6/B8 CPU, wall time, output size, RSS, object/cache bytes, parser allocation,
  disk/I/O, and memory bandwidth remain external-runner obligations.
- No attack-level rho, BSGS, relation, linear-algebra, or descent baseline is
  beaten because this experiment does not solve a DLP.

### Next concrete action

Produce one no-run repair that separates candidate evaluations,
eligible-conflict checks, and eligible pair-output cells; charges graph and
expansion work incrementally; and adds independent success recounts plus
mid-function graph/expansion exception controls. Then request fresh exact-
commit accounting review with `maximum_runs=0`.

### Artifact paths

- `git:a1719f7d910d3cc454911a55ceb8b30d833a0b2d`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v8.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v8.md`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`

