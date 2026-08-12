# Direct five-source TT accounting review v4

## Handoff: frozen preflight v4 accounting audit

### Claim or task

Confirm that the v3 accounting `GO` remains valid and that v4 repairs the
history-conditioned attempt and complete-resource equations.

### Status

`GO`, accounting and history-conditioned resource layer only. No
implementation, rank certificate, or ECDLP improvement is authorized.

### Assumptions

- Conditional lower bounds hold for every reachable full history, not merely
  on average.
- Stationary exponent formulas use history-uniform success bounds and
  per-attempt resource bounds.
- Work, cumulative traffic, retained storage, and peak state remain separate
  resources.

### Evidence so far

- The reviewed preflight SHA256 is
  `f07363f317e1ec0fc1b3e759a782ada43909591a9e53269a51e16d21e0d8fcf0`.
- The reviewed ledger SHA256 is
  `48cb902701223bda3413e4360736cb38872b2974e38f42b2a76a98e0bfe6e23f`.
- All v3 accounting surfaces remain: raw Hadamard allocation, exact normalizer
  work, logarithmic chain, canonical byte factors, Tier A/B/C gates, final
  storage, `D2+D3` construction counts, and online/offline placement.
- Target equations now include `W_g`, `W_Frob`, every `S_j+N_j`, `W_1minus`,
  `W_sweep`, `W_locate`, `W_cert`, and `W_replay`, with matching traffic and
  metadata terms.
- Peak liveness is correctly a maximum rather than an attempt-multiplied
  cumulative resource.
- Exact geometric accounting is limited to the conditionally IID rank-state
  model. History-uniform `p_{r,min}` bounds imply the stated expectation and
  stochastic-domination bounds in the general adaptive case.
- The global binomial confidence gate requires success probability at least
  `p_min` conditional on every prior history until all increments are found.
- The exponent gate `tau_d+rho+delta_epsilon+delta_eta<2.5` applies separately
  to each cumulative work or traffic resource.

### Failure modes

- Marginal success observations cannot instantiate the history-uniform gate.
- Intermediate TT ranks may still reach the fatal dense-core boundary.
- Accounting completeness does not establish a compact compiler.

### Next concrete action

Record this v4 accounting `GO` and require a gate-by-gate central-rank
certificate before any implementation preflight.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`

