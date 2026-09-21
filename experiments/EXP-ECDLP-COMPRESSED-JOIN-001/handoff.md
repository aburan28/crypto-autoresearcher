## Handoff: coordinate-routed compressed join

### Claim or task

Test whether a public nonlinear coordinate feature compresses the exact `D2 + D2` witness relation enough to replace materialized `D4` keys and beat equal-advice fixed-base BSGS on the full `4+1` online query.

### Status

OBSERVATION, REVISE, scoped NEGATIVE RESULT

### Assumptions

- `UNTESTED`: coordinate-defined two-sum supports may exhibit feature-level addition locality absent from random labels.
- `MODEL-BOUND`: route payload bits and `S*T^2` are disclosed diagnostics, not universal lower-bound instantiations.
- `TOY-EVIDENCE`: exact support and hidden-scalar controls are feasible only on small generated groups.

### Evidence so far

- `EXP-ECDLP-FIXED-COMPILER-001` verifies the relation/rank/descent path but rejects explicit `D4` advice on one development seed.
- Dinur-Golovnev shows that subfunction structure can improve 3SUM-Indexing in the integer model.
- The ICALP 2026 unknown-universe result shows a useful heavy/light, random-partition, bounded-indegree pattern.
- A prime-order group has no nontrivial exact homomorphism into a smaller finite group, so integer modular routing needs a genuinely new coordinate analogue.
- The verifier replayed 216 rows and independently checked 8,952 returned witnesses.
- The original x-only signal disappears against eight symmetry-matched random x-fiber nulls.
- No router beats materialized D4 in both advice and query work or equal-advice fixed-base BSGS.

### Failure modes

- Route sparsity is explained entirely by empty buckets.
- Coordinate maps match random-label route entropy after bucket populations are charged.
- Exact candidate additions erase a smaller route table.
- Hidden scalar information leaks from the positive control into candidate routing.
- Equal-advice BSGS remains faster.

### Next concrete action

Specify `EXP-ECDLP-SOURCE-TAG-JOIN-001`, using compositional D2 provenance states and random tag permutations that preserve sign symmetry, occupancy, and witness multiplicity.

### Artifact paths

- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/contract.md`
- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/hypothesis.json`
- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/theory.md`
- `notes/compressed_join_literature_addendum_20260717.md`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development-result-v1.md`
- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/development-result-v1.md`
- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/development-red-team-v1.md`
- `experiments/EXP-ECDLP-COMPRESSED-JOIN-001/development/DEV-COMPRESSED-JOIN-001/verification.json`
