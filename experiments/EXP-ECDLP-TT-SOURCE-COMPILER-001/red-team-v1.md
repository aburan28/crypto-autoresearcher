# Red-team review v1

## Handoff: repaired v2 source-TT compiler adversarial preflight

### Claim or task

Audit whether v2 can establish exact gatewise construction without producer
`B^5` enumeration or laundering intermediate rank, work, and memory.

### Status

`REVISE`. The mathematical layer remains `GO`; the complete preimplementation
bundle does not.

### Assumptions

- The claim is `MODEL-BOUND` to the frozen circuit, tree, mode order,
  registries, and `B in {3,4,5}`.
- Every vectorized operand is canonical before multiplication or dot product.
- Source preprocessing is target-blind and cannot inspect predecessor or
  verifier artifacts.
- Exact TT/ROABP sum, product, and minimization primitives are prior art.

### Evidence so far

- The corrected `c3` and two-sweep theorem survive adversarial review.
- The first-norm compiler remains distinct from the Fermat locator and from
  the explicit four-sum FIXED-COMPILER.
- V1 accounting exposes large legitimate bond-space objects but leaves
  aggregate work, liveness, and backend policy pending.
- Final semantic and rank checks alone could miss a raw-then-recompress path or
  cumulative counter reset.
- The literature note misattributed arXiv:2509.10725 and used it for the wrong
  theorem lineage.

Required repairs:

1. Bind a restricted producer capability surface, complete source hashes,
   read allowlist, no dynamic code, no child process, no network, and no prior
   artifacts.
2. Freeze phase-by-phase allocation/free events and independent peak liveness.
3. Replace all pending aggregate operation, traffic, artifact, and CPU gates
   with numeric campaign ceilings that never reset by gate or cell.
4. Pin the exact NumPy version, dtype, C order, thread count, kernel allowlist,
   canonical-range checks, per-dot overflow checks, and immediate reductions;
   keep the verifier on arbitrary-precision Python integers.
5. Add live-source enumeration, prior-table, raw-product, cost-reset, dtype,
   unreduced-value, affine-source, and shared-code mutations.
6. Strengthen positive controls for cancellation, tagged zero, high
   provisional/low final rank, gauge equivalence, modewise projective scaling,
   all-nonzero coefficients, target-order invariance, and cumulative refusal.
7. Correct the literature record and preserve the no-speedup claim: avoiding
   tuple enumeration does not imply less work or memory than the tiny toy
   `B^5` table.

### Failure modes

- Encoded enumeration through radix decoding, recursion, or five-dimensional
  NumPy helpers.
- Correct final cores after undeclared raw materialization.
- Peak sampled only after a large temporary is freed.
- Int64 overflow after an unreduced intermediate or wrong dtype.
- Correct final ranks with omitted prefix and two-sweep costs.
- A finite first-norm result described as a locator, relation compiler, or
  ECDLP improvement.

### Next concrete action

Produce and re-review one preimplementation v3 bundle with the capability
boundary, exact backend, numeric aggregate gates, corrected literature, and
live-source mutation schedule before writing producer source.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/red-team-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v1.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/mutation-manifest-v1.json`
