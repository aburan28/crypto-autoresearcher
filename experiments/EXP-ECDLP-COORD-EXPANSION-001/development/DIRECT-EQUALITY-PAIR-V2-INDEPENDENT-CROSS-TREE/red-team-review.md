# Independent Red-Team Review

## Handoff: Direct Equality Pair V2 Cross-Tree

### Claim or task

Audit enumeration completeness, affine/residual semantics, target provenance,
producer/verifier independence, operation accounting, and the evidence
envelope.

### Status

- fixed-fixture mathematical sweep: `OBSERVATION`, `TOY-EVIDENCE`,
  `MODEL-BOUND`;
- original verifier completeness: scoped `NEGATIVE RESULT`;
- strict successor verifier: valid;
- ECDLP significance: none established.

### Evidence so far

- An independent aggregate recount reproduced all 12 rows, 555,804 ordered
  tuples, 14 Catalan trees, 316 planted witnesses, 84 held-out witnesses, and
  36 infinity outputs.
- Every fixture and target is on curve; all three `p` and `q` values are prime,
  curves are nonsingular, and `qG=O`.
- Planted target regeneration and cross-cut target agreement passed.
- Every original manifest hash matched its file and source commit/tree.
- The strict successor verifier derives the exact row sequence, recomputes
  controls, tree digests, validity, operations, summary totals, target
  finiteness/on-curve status, and cross-cut agreement.
- It rejects mutations to a dropped row, duplicate row, summary total,
  control, operation count, tree digest, mutation counter, and cross-cut
  target.

### Failure modes

1. The original verifier accepted a truncated/tampered envelope because it
   replayed only rows supplied by the artifact and omitted summary, control,
   operation, mutation, and tree-digest enforcement.
2. The historical `run-manifest.json` is a custom development receipt and
   does not conform to `schemas/run-manifest.schema.json`.
3. V2 tests abstract affine semantics, not V1 RCB or coefficient factors.
4. Held-out target hash-to-curve derivation remains unregenerated.
5. The x-plus-one target mutation is generally off curve and is only a
   residual-change control.
6. The producer multiplication count is a group-law proxy, not complete
   executed-field or memory accounting.
7. Current fixtures use canonical affine coordinates. The affine law is not
   normalized for arbitrary noncanonical integer representatives.
8. One deterministic nonzero scale pair is sampled per tuple; arbitrary-scale
   invariance follows algebraically, not from exhaustive scale testing.

### Strongest valid correction

> On the frozen canonical toy fixtures, two separate affine implementations,
> an aggregate recount, and a strict envelope verifier agree that abstract
> point equality and simultaneous residual zero are invariant under the
> enumerated R orders, 14 parenthesizations, two regroupings, and sampled
> nonzero scales.

This statement does not certify V1 polynomial factors, compiler accounting,
relation rank, or descent.

### Next concrete action

Use the V3 independent coefficient audit to bridge the abstract semantics to
the frozen factor vectors. For future formal runs, emit a schema-conforming
runner manifest at launch time with timestamps, environment, dirty state, and
resource boundaries rather than retrofitting those fields.

### Artifact paths

- `development/DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE/raw-result.json`
- `development/DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE/verification.json`
- `development/DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE/strict-verification.json`
- `src/direct_equality_pair_cross_tree.py`
- `src/verify_direct_equality_pair_cross_tree.py`
- `src/verify_direct_equality_pair_cross_tree_strict.py`
