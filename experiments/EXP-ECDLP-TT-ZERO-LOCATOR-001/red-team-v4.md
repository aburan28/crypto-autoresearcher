# Direct five-source TT red-team review v4

## Handoff: frozen preflight v4 adversarial audit

### Claim or task

Try to invalidate the v4 accounting repair or any retained mathematical claim.

### Status

`GO`, accounting and paper-preflight scope only. No implementation or
experiment authorization follows.

### Assumptions

- Any stationary exponent claim uses history-uniform conditional
  probabilities, not empirical marginals.
- Per-attempt resources include every applicable target construction,
  compiler, certificate, replay, canonicalization, and downstream term.
- Any batch implementation would need a separately proved resource law and
  concurrent peak-state accounting.

### Evidence so far

- The preflight and dimension-ledger SHA256 values match
  `f07363f317e1ec0fc1b3e759a782ada43909591a9e53269a51e16d21e0d8fcf0`
  and `48cb902701223bda3413e4360736cb38872b2974e38f42b2a76a98e0bfe6e23f`.
- V3 algebraic, rank, dense-TT, output, and model-bound conclusions are
  unchanged.
- V4 includes target specialization, Frobenius, every Hadamard and normalizer,
  final subtraction, sweep, location, certificate, replay, metadata, and
  peak-state separation.
- Exact geometric accounting is conditioned on the complete accepted-span
  history; marginal or averaged probabilities are explicitly rejected.
- History-uniform `p_{r,min}` bounds and the global conditional `p_min`
  binomial gate are correctly oriented and fail closed.
- Attempt multipliers are applied separately to every cumulative work and
  traffic resource while peak state remains a maximum.
- Canonicalization, filtering, linear algebra, and descent remain separately
  gated.

### Failure modes

- Intermediate central TT ranks remain an open and likely fatal obstruction.
- Violating the history-uniform probability condition or omitting a resource
  term invalidates promotion.
- This `GO` establishes neither a compact compiler, Tier B/C passage, novelty,
  nor an ECDLP improvement.

### Next concrete action

Derive or refute the gate-by-gate central-rank certificate for the frozen
RCB-plus-norm-indicator circuit, stopping before source if a central dense rank
reaches `Omega(B)` or any cumulative Tier-B gate fails.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`

