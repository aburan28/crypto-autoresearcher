## Handoff: SGCP V5 exact-commit theory audit

### Claim or task

Review only commit `606daf8fee72979403915d23011f987f01007b74` for
EXP-SGCP-EMBED-002 V5 mathematical consistency, verifier totality, independent
oracle scope, gate semantics, and readiness for a separate hash-complete
canonical launch-plan design.

### Status

`NEGATIVE RESULT` for V5 protocol readiness and `RESTRICTED THEOREM` for the
fixed finite graph/ideal construction. The underlying research claim remains
`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Recommendation: `REVISE`. Launch-plan design and execution remain `NO-GO`, and
`maximum_runs=0` remains in force.

### Assumptions

- The review used only committed blobs at the exact requested commit.
- Exactness is limited to the fixed factor base, representative compiler,
  downward ideals, conflict graph, source model, ordering, and objective.
- A result is interpretable only from a complete, schema-valid,
  verifier-valid canonical matrix.
- Exhaustive subset checks address the finite graph object, not a general
  ECDLP, relation-generation, rank, descent, or preprocessing claim.

### Evidence so far

- All nine V5 development-log SHA-256 values match the committed blobs.
- The producer, verifier, protocol, hypothesis, specification, contract,
  revision response, and self-review agree on the underlying finite
  mathematical object. V5 changes receipt and outcome semantics without
  changing that object.
- For fixed downward ideals, pairwise conflict-graph independence is
  equivalent to injectivity on the union of the selected ideals.
- An exhaustive check of all 4,096 frozen B4 subsets found zero graph or
  monotonicity failures.
- The standalone B4 oracle independently implements EC addition, factor-base
  construction, representative compilation, ideals, graph construction,
  retained-model cost, final support, and all registered cap winners.
- The hand-derived gate arithmetic correctly distinguishes exact ratio and
  stratum thresholds, and the explicit negative outcomes are semantically
  consistent.
- V5 rejects legacy V1-V4 schemas and distinguishes invalid input from an
  inconclusive verifier exception.
- No family row, canonical matrix, runner, launch plan, or execution
  authorization exists at the reviewed commit.

### Failure modes

- The admitted curve `bits` value is not bounded to the registered protocol
  before prime enumeration. A digest-consistent current-schema input can
  request work far beyond the claimed verifier envelope.
- The generic B ceiling admits degree-eight expansion at B=64. That includes
  `C(71,8)=10,639,125,640` multisets before later semantic checks, so bounded
  JSON does not imply bounded verification work.
- A frozen or canonical envelope already known to be invalid can still enter
  row verification instead of failing before graph reconstruction and replay.
- The duplicate-null median fixture `[8,10,10,12]` is nondiscriminating: both
  the intended median and a deduplicated median equal 10. A discriminating
  fixture such as `[8,8,10,12]` yields 9 under the registered rule and 10 after
  erroneous deduplication.
- The standalone B4 oracle compares aggregate graph counts and optimizer
  outcomes, but it does not compare the complete candidate, edge,
  constrained-label, and source transcript.
- Exact closure of each canonical B8 cell can remain computationally
  infeasible even after input totality is repaired.

### Next concrete action

Implement a no-run V6 route that rejects nonregistered scope, curve, B, seed,
grid, row association, and resource values before reconstruction; bind every
pre-primary and replay phase to trusted limits; add the discriminating median
fixture; and compare the complete frozen B4 transcript with an independently
derived oracle.

### Artifact paths

- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/contract.md`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/specification.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v5.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:tests/test_sgcp_embed_family.py`

Final recommendation: **REVISE. Launch-plan design and execution remain
NO-GO.**
