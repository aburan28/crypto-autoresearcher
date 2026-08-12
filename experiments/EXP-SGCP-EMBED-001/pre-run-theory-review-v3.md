# Pre-run theory review: SGCP-EMBED-001 v3

Date: 2026-07-17

Execution state: no canonical certificate, relation collection, ECDLP run, or
performance run was launched.

## Handoff: v3 specification approval

### Claim or task

Verify that all four v2 specification blockers were repaired without inspecting
or executing source.

### Status

RESTRICTED THEOREM / GO FOR IMPLEMENTATION

The mathematical specification is approved for implementation. The hypothesis
remains HYPOTHESIS / MODEL-BOUND; no experiment or ECDLP claim is established,
and canonical execution still requires its separate approval boundary.

### Assumptions

- Review was restricted to the contract, registry, preflight records, and prior
  review artifacts.
- Builder and verifier must implement the normative definitions literally.
- Any hash drift, omitted subset comparison, altered tie-break, or
  first-error-only control handling invalidates the preflight.

### Evidence so far

- PASS: `I0`, `I(M)`, invalid vertices, conflicts, the independent-set iff
  lemma, and every-subset direct comparison are exact.
- PASS: raw/selected four-term sets, final supports, relative/absolute ratios,
  unordered edge count, and lexicographic comparator are exact.
- PASS: P0, P1, and P2 have distinct normative construction branches.
- PASS: all twelve controls have frozen fixtures, complete predicate vectors,
  counts/objectives, and exact or null counterexamples.
- PASS: the reviewer independently measured registry SHA-256
  `cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca`,
  matching every binding.

### Failure modes

- Source semantics drift from the approved contract.
- Builder and verifier share arithmetic, scalar material, or optimizer code.
- A canonical run is launched before source review, hash freeze, and execution
  approval.

### Next concrete action

Adapt the coordinate-only builder to the approved balanced universe, implement
an independently written scalar-table verifier, compare every five-bit subset,
and freeze reviewed source hashes before requesting canonical execution.

### Artifact paths

- `notes/sgcp_embed_001_contract_20260717.md`
- `experiments/EXP-SGCP-EMBED-001/control-registry-v2.json`
- `experiments/EXP-SGCP-EMBED-001/pre-run-theory-review-v2.md`
- `experiments/EXP-SGCP-EMBED-001/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-001/pre-run-theory-review-v3.md`
