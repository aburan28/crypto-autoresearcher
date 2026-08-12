## Handoff: SGCP source repair v2 second red-team

### Claim or task

Determine whether source repair v2 was ready for freeze and canonical five-bit
preflight execution.

### Status

NEGATIVE RESULT, REVISE. Canonical execution remains unauthorized.

### Assumptions

- Review was read-only and preserved the dirty development worktree.
- Findings concern implementation readiness, not the SGCP hypothesis or ECDLP.
- No canonical command or output was executed.

### Evidence so far

- Focused `19/19` and repository `59/59` suites passed independently.
- Contract substitution, corrupted scalar ground truth, zeroed deterministic
  counters, unknown/scalar argv, protected/existing outputs, repaired semantic
  mutations, mask-order digests, and an omitted-subset claim were rejected.
- A separate scalar-index implementation, using neither source optimizer nor
  serializer, reproduced all five-bit optimizer results:

| B | candidates | valid | conflicts | subsets | objective `(support,D4,C*,edges)` | outcome digest |
|---:|---:|---:|---:|---:|---|---|
| 4 | 31 | 12 | 20 | 4096 | `(13,5,20,26)` | `8f95f52f...` |
| 6 | 68 | 8 | 4 | 256 | `(7,4,17,20)` | `c571d463...` |
| 8 | 124 | 14 | 53 | 16384 | `(7,4,14,21)` | `38f0c54a...` |

This is positive evidence for exhaustive optimizer correctness and contracted
lexicographic ordering, not cryptanalytic performance evidence.

### Failure modes

1. HIGH: the fixed-file CLIs cannot run through the repository approval runner.
   Locked children use `-I -S -B`, forbid subprocess descendants, create run
   stdout/stderr files before launch, require stdout JSON with exact
   `valid=true`, and link verifier input to predecessor `raw-result.json`.
   Current programs invoke Git, require a globally clean tree, print paths, and
   write fixed `preflight/` files.
2. MEDIUM: private v3a audit fields remain partial. Target association is lost
   in count-of-counts histograms, degree-two identity witnesses are omitted,
   private charged operations/final bytes are absent, and distinct candidates
   are mislabeled as raw parent-pair witness density.
3. MEDIUM: `scalar_table_material_emitted=false` is overbroad. The scanner
   checks names and shape, not covert encoding in unconstrained diagnostic
   integers; a scalar encoding in `wall_clock_ns` passed after receipt repair.
4. MEDIUM: the index differential shares verifier constructors and excludes
   retention/accounting. It is a representation differential, not a third
   independent optimizer. The external scalar-index recount is not checked in.

### Required repairs

- Add locked-run stdout JSON modes and predecessor linkage, with no child Git
  subprocesses, then test both roles through the actual runner protocol.
- Emit target-to-witness maps, all degree-two identity witnesses, private
  operation attribution, final charged bytes, and separate candidate and
  parent-pair densities.
- Check in an independently structured scalar-index P2 oracle covering counts,
  conflicts, outcomes, selection, objective, and retention.
- Scope scalar-material claims to mechanically checked structure/source names;
  add a covert diagnostic-channel regression.
- Bind timestamp and provenance through the external runner receipt.

### Next concrete action

Implement source repair v3, add runner-composition and expanded audit/oracle
tests, rerun all suites, and request another read-only review.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v1.md`
- `experiments/EXP-SGCP-EMBED-001/source-review-response-v2.md`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `src/crypto_autoresearcher/runner.py`
- `tests/test_sgcp_embed.py`
