## Handoff: SGCP source-review repair v2

### Claim or task

Repair every blocking implementation finding in `source-red-team-v1.md`
without changing the approved version-3a mathematical hypothesis.

### Status

HYPOTHESIS, implementation repair in development. Canonical execution remains
unauthorized pending a second source red-team GO and hash freeze.

### Assumptions

- The mathematical contract remains version 3a and hash-pinned.
- Builder operation counts are deterministic fixture diagnostics; wall time and
  Python-object deep size are explicitly self-reported diagnostics.
- The semantic oracle and builder-compatible serializer may share mathematical
  definitions but must compare independent internal objects before exact JSON
  comparison.

### Evidence so far

| v1 finding | v2 repair |
|---|---|
| Caller-selected contract passed | Builder and verifier pin the exact mathematical contract path/hash and the separate experiment contract path/hash. Literature and control paths remain pinned. |
| Scalar results did not gate validity | The scalar-table digest is pinned and every applicable P0/P2 scalar result is an aggregate validity gate; rejected P1 remains not applicable. |
| Outputs could overwrite protected files | Builder and verifier accept only their exact preflight filenames, reject existing targets, and use no-replace atomic linking. Canonical CLI launch checks cwd, branch, and Git state. |
| Forged argv/metrics passed | Argv grammar is exact, unknown tokens fail, implementation/resources have a separate receipt digest, and deterministic builder operation counts are frozen and exact-compared. Memory and wall diagnostics are labeled self-reported. |
| Serializer clone was the only oracle | A second semantic path compares source tuples, formal families, evaluations, collisions, index-based star edges, constrained indices, density, all model predicates, scalar compatibility, and optimizer objective before JSON acceptance. |
| Contract metrics/schema were incomplete | Rows now expose contract source tuples, polynomial coefficients, row-level raw witnesses, public/source byte counts, raw-witness density, source-tag multiplicity/loss, and minimized-counterexample digest. The verifier reports its own operations, wall time, and process high-water memory diagnostic. |
| Outcome digest used mask order | Both programs sort outcome rows by lexicographic subset-universe indices and bind the ordering label before hashing. |

Development probes now reject the exact v1 false passes: `README.md` contract
substitution, corrupted scalar ground truth, protected output paths, zeroed
operation counters with a recomputed receipt, and scalar material appended to
argv with a recomputed receipt.

### Failure modes

- The second reviewer may find a remaining semantic/serialization common-mode
  error.
- The exact launch-state policy may not compose with the repository approval
  runner and must not be weakened without a versioned review.
- Self-reported wall time and object-graph memory are diagnostics, not
  independently attested resource measurements.
- This remains a five-bit implementation preflight with no ECDLP evidence.

### Next concrete action

Run the expanded focused and repository-wide suites, preserve exact logs and
source hashes, then request a fresh read-only red-team review of the repaired
sources and adversarial probes.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v1.md`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `tests/test_sgcp_embed.py`
