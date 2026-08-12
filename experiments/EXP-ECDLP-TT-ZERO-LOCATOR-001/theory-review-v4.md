# Direct five-source TT theory review v4

## Handoff: frozen preflight v4 theory audit

### Claim or task

Audit `preflight-v4.md` at SHA256
`f07363f317e1ec0fc1b3e759a782ada43909591a9e53269a51e16d21e0d8fcf0`
and `object-dimension-ledger-v4.md` at SHA256
`48cb902701223bda3413e4360736cb38872b2974e38f42b2a76a98e0bfe6e23f`.

### Status

`GO`, theory and accounting preflight only. No implementation, execution,
canonical claim, or breakthrough claim is authorized.

### Assumptions

- Attempt probabilities are conditioned on the complete reachable history.
- Every online work and cumulative-traffic resource is gated separately.
- Peak-live state is bounded separately and is not multiplied by attempt count.

### Evidence so far

- Both frozen hashes matched independently.
- The v2 mathematical core is preserved: complete RCB addition binding,
  projective equality including `Q=O`, exact Fermat witness tensor, central
  dense-core gate, and exact final-cut-rank theorem.
- V4 restricts exact geometric expectations to the conditionally IID
  rank-state model. Outside that model, history-uniform lower bounds give the
  stated expectation and stochastic-domination bounds.
- The binomial attempt quantile requires a uniform conditional lower bound
  after every prior history and explicitly rejects marginal averages.
- Complete work and traffic now include target-`g_Q` construction, Frobenius
  powering, every sweep and normalization stage, localization, certification,
  replay, and metadata.
- Tier-C inequalities apply independently to every cumulative work or traffic
  resource. Peak state retains its separate exponent gate.

### Failure modes

- History-uniform success bounds remain proof obligations; empirical marginal
  rates cannot replace them.
- Intermediate TT ranks may still reach the fatal dense-core boundary.
- Representation-specific toy ranks do not establish a universal TT theorem.

### Next concrete action

Derive or refute the gate-by-gate central-rank certificate for the bound
RCB-plus-norm-indicator circuit before any source authorization.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`

