# Direct five-source TT red-team v2

## Handoff: frozen preflight v2 red-team

### Claim or task

Verify `preflight-v2.md` at SHA256
`b90c09448b740d198b52afbf9743735e0fca12dc51a0011352610fb2fdf49ce1`
and `object-dimension-ledger-v2.md` at SHA256
`92435885c64f912627e7a212712561f907aa84485c0f326d818e245d4b9fe9fa`.

### Status

`GO`, narrowly for the paper preflight and fail-closed specification.

This does not authorize implementation or experiments. The candidate remains
`HYPOTHESIS`, `NOVELTY-UNVERIFIED`, and `REVIEW_REQUIRED` pending the complete
review bundle.

### Assumptions

- Arithmetic stays inside the registered odd-order subgroup.
- Dense-TT conclusions apply only to standard materialized cores.
- Fixed-online, compressed, and complete-ECDLP claims remain distinct.
- Any implementation preserves the bound formula, mode ordering, and byte
  accounting.

### Evidence so far

- Exact RCB Algorithm 1, coordinates, `b3=3*b`, the four-call addition tree,
  and the odd-subgroup condition close the exceptional-case oracle.
- Actual raw ranks replace v1's overbroad necessary conditions, and dense
  allocation is not called an information lower bound.
- Raw allocations, logarithmically many normalizations, canonical bytes,
  Frobenius traffic, final direct-sum normalization, and locator work are
  charged.
- `epsilon`, canonical relation rows, `eta_r`, duplicate/permutation handling,
  and required target classes are conjunctive gates.
- Advice, preprocessing work/traffic/workspace, amortization, and measured
  `N2,N3` D2+D3 support are explicit.
- Generic skeletonization remains correctly restricted to the entry-oracle
  model.

Primary formula source:

- Renes, Costello, and Batina, [Complete addition formulas for prime order
  elliptic curves](https://iacr.org/archive/eurocrypt2016/96650347/96650347.pdf),
  EUROCRYPT 2016.

### Failure modes

- The decisive unresolved risk is intermediate central-rank growth in the
  norm-indicator chain.
- No universal TT, structured-core, or arithmetic-circuit lower bound follows.
- Low final rank, toy behavior, or a fixed-online result cannot establish a
  complete ECDLP improvement.

### Next concrete action

Derive or refute a gate-by-gate central-rank certificate for the bound RCB plus
norm-indicator circuit; stop before source code if a central dense rank reaches
`Omega(B)` or any reviewed cumulative gate fails.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/red-team-v1.md`
