## Handoff: EXP-SGCP-EMBED-002 V7 independent accounting review

### Claim or task

Independently audit exact commit
`fe093d3d80bba38e729fd8c98f78bed569e5087d` for cost integrity and readiness
for launch-plan design only.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Decision: `REVISE` for launch-plan design only. Execution remains `NO-GO`.

### Assumptions

- Only exact committed blobs were used for substantive review.
- No family row, canonical matrix, runner, launch plan, or experiment run was
  created by the reviewer.
- Structural cells, CPU, field operations, RSS, disk, I/O, allocator work,
  and memory bandwidth are distinct resources.
- Resource exhaustion or verifier failure remains `INCONCLUSIVE`.

### Evidence so far

- The V7 development-log hashes match commit `fe093d3`.
- Ledger state is V7 `review_required`, with `runs=[]`.
- Declared combinatorial budget formulas recompute consistently.
- No relevant ECDLP baseline is beaten or end-to-end comparable.

### Findings

1. `BLOCKER`: density-primary point enumeration is missing from successful
   actual-work accounting. `independent_density_primary_optimum` calls
   `curve.points()` once per cap without charging
   `primary_curve_point_enumerations`; the charge exists only in an older
   sibling routine. Reservation provides a per-cap ceiling, but a valid report
   records zero actual calls while claiming completeness.
2. `HIGH`: reservation dominance is observed by one test but is not a verifier
   validity invariant. The source computes reservation ceilings and actual
   receipts separately, but does not invalidate a report when an actual
   source-owned count exceeds its reserved bound.
3. `HIGH`: pre-semantic B-derived admission is incomplete. Mobius-map lists,
   rejection-reason lists, root-polynomial coefficients, nested formal lists,
   nested byte receipts, and `family_gate` can remain bounded only by the
   global JSON ceiling or be rejected after semantic work. The four-item
   `nested_per_cap_json_bytes` association is not preflighted exactly.
4. `MEDIUM`: exceptions preserve prior caps but can lose work completed inside
   the failing cap. Replay and primary exception receipts report zero nodes
   and cache entries even after partial internal progress. Existing injected
   failures occur before the measured work begins.
5. `MEDIUM`: public direct-call semantics are not evidence-equivalent. Early
   direct-row returns have incomplete receipt envelopes, outer exceptions can
   discard cap reports, and value-level document verification omits complete
   reservation and actual-work receipts. Only path-based `verify_document`
   currently exposes the intended evidence boundary.
6. `MEDIUM`: structural reservations omit dominant implementation costs. Graph
   degeneracy reconstruction can be cubic in candidate count, and parser,
   sorting, hashing, serialization, Python-object, allocator, CPU, RSS, disk,
   I/O, and bandwidth costs remain external. The reservation is not evidence
   that a proposed four-GiB role is feasible.

### Accounting recomputation

Canonical ceilings are 480 prime candidates; 800,000 registered curve draws;
2,400,000 registered curve hashes; 1,600,000 provenance point-enumeration
calls; 232,704 predicate hashes; 168 semantic point enumerations; 672 primary
point enumerations; 473,928 expansion cells; 10,597,832 graph cells;
1,344,000,000 optimizer/replay nodes per corresponding role; between
1,344,000,000 and 3,360,000,000 primary nodes; between 5,430,000,000 and
9,465,000,000 aggregate cache-entry units; between 2,716,000,000 and
4,733,000,000 retained-model calls; and between approximately
1.351e14 and 2.342e14 retained-model cells. These are source ceilings, not
runtime predictions or peak-memory bounds.

### Failure modes

- A completed receipt can undercount point enumeration.
- Actual work can exceed reservation without invalidating the report.
- Nested transcript and gate amplification can precede expensive semantics.
- Interrupted work can be omitted rather than represented as an observed
  lower bound.
- Direct helpers can be mistaken for the complete path-based attestation API.
- B6/B8 feasibility, artifact size, field-operation cost, rank, and descent
  remain unmeasured.

### Next concrete action

Create a no-run V8 accounting repair that charges density-primary work,
enforces actual-to-reservation dominance as verifier validity, bounds every
nested transcript and `family_gate` before semantics, and adds exact-count and
mid-function exception tests. Do not create a generated density row or matrix.

### Artifact paths

- `fe093d3:experiments/EXP-SGCP-EMBED-002/contract.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/specification.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v7.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/development-test-log-v7.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `fe093d3:tests/test_sgcp_embed_family.py`

