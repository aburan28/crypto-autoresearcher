# Revision response: EXP-ECDLP-RECURSIVE-002 v2

The independent v1 pre-run audit returned `REVISE` at commit `96fcc1b`. No
canonical experiment was launched. This response maps every required control to
the versioned repair; a second independent audit must verify the final hashes.

| Audit item | Version 2 response | Verification gate |
|---|---|---|
| S0-1 command/provenance | Freeze exact run IDs, argv, seed, parameters, timeout, predecessor path, and clean-tree policy in the schema-validated execution plan. Externally pin generator, verifier, runner, schema, specification, and contract hashes in the second audit. | Runner adversarial tests plus audit hash table. |
| S0-2 budgets/run graph | Runner enforces maximum runs, caller timeout, child/post-run memory, cumulative CPU, predecessor `completed_valid`, and verifier input SHA linkage. | Synthetic excess-run, timeout, memory/CPU, argv, and linkage tests. |
| S1-1 positive control | Scalar-progression failure makes `valid=false`, suppresses all family promotion, and is independently reconstructed. | Synthetic nine-pass candidate rows with forced control failure must promote nothing. |
| S1-2 order dependence | Count successful partials `k` per target and use exact uniform-permutation first-hit expectation `(S+1)/(k+1)`, or `S` for `k=0`. Retain all four target-level shuffled vectors and gate sampled/exact and sampled/sample aggregate variation at 25 percent. | Exact reconstruction plus mutations of counts, fractions, vectors, and gate. |
| S1-3 offline accounting | Charge binary-pow multiplication proxies, coordinate RHS work, square/rational-map multiplications, and rational-map inversions. Gate group operations, charged multiplications, and charged inversions separately. Label lookup bytes as an assumption and the artifact as reconstructible rather than stored. | Per-family cost reconstruction and mutations. |
| S2-1 finite design | Retain favorable/tied/null counts and finite denominator for every percentile. Describe random and random-x as independently seeded samples of the same point-set null, and the three-family gate as exploratory without family-wise inference. | Rank/tie semantic tests and exact verifier replay. |
| S2-2 repeated fields | Replace seeds with 2473001, 2473004, and 2473012; require all nine field primes to be distinct. | Frozen schedule test and runtime invariant. |
| S2-3 semantic tests | Add brute-force support, percentile endpoint/tie, special/anomalous curve, global seed, exact first-hit, charged cost, mandatory control, family aggregation, budget, argv, dirty-tree, and predecessor-linkage tests. | Full repository suite before audit. |

## Preserved boundaries

- The two v1 predecessor runs remain immutable.
- Reduced v2 smokes are correctness/runtime checks, not hypothesis evidence.
- Rho remains an arithmetic scale and is excluded from promotion.
- Rank, relation independence, sparse linear algebra, factor-base logarithms,
  target descent, exponent fitting, and deployment relevance remain untested.

## Next action

Freeze the final v2 verifier and execution-plan hashes, run only the reduced
test suite, and request an independent pre-run `GO` or `REVISE`. Canonical
execution remains prohibited until `GO` is recorded and approval is committed.
