# EXP-SGCP-EMBED-002 independent red-team review v3

## Handoff: version-3 adversarial boundary

### Claim or task

Review frozen commit `2be45cd57bce4e23ad9996965999f906bb81dd4c` and
decide whether its V3 evidence boundary is ready for a separate hash-complete
canonical launch-plan design.

### Status

`NEGATIVE RESULT` for the claimed V3 closure; the underlying hypothesis remains
`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

**Final recommendation: REVISE before launch-plan design.**

`maximum_runs=0`, with zero canonical or new family rows, must remain unchanged.

### Assumptions

- Only committed blobs from `2be45cd` were reviewed; unrelated working-tree
  changes were ignored.
- No files were written and no curve-family or canonical work was run.
- Dynamic checks were limited to abstract fixtures, a scripted unit provenance
  case, and frozen `p=19`.
- Source hashes independently matched the six hashes in
  `development-test-log-v3.md`.

### Evidence so far

The following parts held under review:

- Exact canonical row order, curve consistency, node caps, and cross-seed
  uniqueness are enforced in `validate_canonical_rows` and
  `verify_v3_document_value`.
- Representative and source tables are independently reconstructed and
  compared exactly in `reconstruct_graph`, `retained_model`, and
  `verify_density_row`.
- Objective order is explicitly bound.
- A third exhaustive oracle matched the complete five-field objective in 1,200
  random monotone abstract fixtures and all four frozen p=19 caps. This is
  useful implementation evidence, not a proof for canonical parameters.
- Canonical row verification requires empty frontier, zero gap, exact primary
  and secondary flags, replay agreement, and a completed alternate primary DFS.
- Accounting is appropriately narrowed to reconstructible structural cells and
  nonadditive serialized sizes; peak memory and end-to-end operation claims are
  explicitly excluded.

### Failure modes

#### Exact implementation blockers

1. **Curve provenance does not record every applicable rejection reason.**

   The contract requires every draw and every applicable reason. Both producer
   and verifier short-circuit duplicate candidates to only
   `["duplicate_candidate"]`. The committed test explicitly blesses this
   incomplete transcript. Repeating `(p,a,b)=(19,0,0)` emits only
   `duplicate_candidate` although `singular` also applies. This is a
   producer/verifier shared bug.

2. **The schemas are key-closed but not type-closed.**

   `v3_row_schema_errors` checks key sets but does not enforce exact JSON types
   for most counts and receipts. Later checks use Python equality, where
   `False == 0`.

   On the frozen p=19 row, changing numeric `absolute_gap` from `0` to JSON
   `false`, then refreshing all byte receipts and the row digest, still returned
   `valid=true`. Thus a new self-consistent mutation survives the V3 verifier.

#### Overclaim corrections

- Complete rejection-reason and all-applicable-reason claims are not true.
- Closed schema currently means closed key set, not exact value types.
- The standalone family-gate helpers inspect only `primary_exact`,
  `full_objective_exact`, and `absolute_gap`. They do not themselves reject
  nonempty frontiers, wrong termination, or inconsistent bounds. Full document
  verification later catches these, so the canonical verifier is stronger than
  the gate helper.
- The independent DFS proves only primary support. Secondary exactness depends
  on a structurally similar replay; this is shared-model risk.
- The repository-wide suite is recorded as failed for a pre-existing
  immutable-run guard.

#### Required controls and next falsification tests

- Require exact rejection lists for duplicates of singular, wrong-bit,
  nonprime-order, trace-zero, anomalous, `j=0`, `j=1728`, and multi-reason
  candidates.
- Add strict recursive type checks, including mutations `0 -> false`,
  `0 -> -0.0`, integer to equal float, boolean to integer, malformed ratios,
  masks, counts, and node receipts.
- Add committed tests for extra, duplicate, reordered, wrong-cap,
  wrong-node-cap, inconsistent-curve, and cross-seed-duplicate canonical
  matrices.
- Mutate every exhausted-cell field independently, including frontier contents,
  termination, lower/upper equality, node cap, and secondary-exactness flag.
- Add a third exhaustive secondary-objective oracle to the committed abstract
  tests and frozen p=19 fixture.
- Ensure a future runner requires V3 schema, canonical scope, 168 rows, 672
  valid cells, and the expected claim boundary, not merely verifier exit status.
  Legacy empty noncanonical documents can still return valid through the
  legacy verifier branch.

Residual non-implementation risks remain: representative-compiler dependence,
only eight deterministic toy curves, four potentially duplicate null controls,
correlated B values, unknown 672-cell feasibility, and no relation collection,
rank, target descent, rho comparison, or preprocessing crossover.

### Next concrete action

Commit a no-run V4 repair that fixes complete duplicate provenance, enforces
exact JSON types, strengthens gate/exhaustion controls, and adds the mutation
matrix above; then request fresh independent review while preserving
`maximum_runs=0`.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v3.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v3.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
