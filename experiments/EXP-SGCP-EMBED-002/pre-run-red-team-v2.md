# EXP-SGCP-EMBED-002 independent red-team review v2

## Handoff: matched-density evidence boundary

### Claim or task

Determine whether version 2 correctly implements and independently verifies
the preregistered matched-density frontier semantics.

### Status

`REVISE`, `OPEN`, `TOY-EVIDENCE`, `MODEL-BOUND`, and
`NOVELTY-UNVERIFIED`. Canonical `maximum_runs` remains zero.

### Assumptions

- The review was read-only on the same dirty-worktree snapshot identified in
  `pre-run-accounting-review-v2.md`.
- No curve-family sweep or repository write was performed.
- Dynamic probes used only the frozen `p=19,a=2,b=9,q=23` fixture and abstract
  in-memory graphs.

### Evidence so far

The primary objective order is correctly implemented as retained support,
constrained-label count, public-edge count, retained maxima, and lexical
witness order. The formal-multiset and ordered-tuple energy definitions are
also mathematically consistent.

The following self-consistent mutations were nevertheless accepted:

| Mutation | V2 result |
|---|---|
| Fabricated curve seed, accepted draw, rejection list, and digest | `VALID` |
| Changed Mobius derivation nonce | `VALID` |
| Coordinate row assigned `null_replicate=999` | `VALID` |
| Fabricated operation-count decomposition | `VALID` |
| Corrupted serialized objective order | `VALID` |
| Added builder-visible scalar table | `VALID` |
| Empty V2 document with zero rows | `VALID` |
| Omitted frontier with a fabricated exact interval in the local checker | no local error |

### Failure modes

1. The document verifier does not enforce the canonical parameter matrix,
   controls, cross-row matching, medians, or family gates.
2. Local frontier-state checks cannot prove that no branch was omitted. The
   deterministic replay is close to the producer, while the alternate DFS
   currently must finish; unresolved intervals therefore lack an independent
   branch-complete certificate.
3. Curve draw transcripts and hash-derived Mobius parameters are not
   independently reconstructed. Cross-seed duplicate accepted curves are not
   rejected.
4. Row and document schemas are open, so appended scalar material is accepted
   after refreshing digests.
5. Cost receipts prove internal addition only, not independently reconstructed
   work or external wall/RSS limits.
6. Several required semantic mutations and inherited controls are documentary
   rather than V2 tests.
7. The verifier does not bind `objective_order`; the four-null median, ties,
   cap selection, and missing-cell rules are underspecified.
8. `source_recovery` checks tuple normalization rather than a public decoding
   algorithm. Final-edge exclusion is a construction invariant, not an
   empirical discovery.

### Next concrete action

Produce one version-3 frozen repair bundle with closed schemas, independent
curve/predicate derivation, an exact gate evaluator, and rejection tests for
every accepted mutation above before requesting another red-team decision.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
