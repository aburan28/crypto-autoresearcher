# Direct five-source TT red-team v3

## Handoff: frozen preflight v3 red-team

### Claim or task

Audit `preflight-v3.md` at SHA256
`c44c079ee393336d4e7c24e2d93ae80e61ea14c75d41a9860c9f0f63c9593864`
and `object-dimension-ledger-v3.md` at SHA256
`5132e0afe758d351fb13dfca26cbe3296415493a2e4ab9edb58e28a4f364e463`.

### Status

`GO`, paper/accounting preflight only. No implementation or run is authorized.

### Assumptions

- `epsilon_r*eta_r` is the conditional per-attempt rank-increment probability
  under the preregistered target distribution; otherwise `p_min` must hold
  uniformly over every reachable history.
- Total relation traffic multiplies per-attempt traffic by the expected or
  preregistered-quantile attempt count.
- Certificate and independent-replay traffic remain charged.

### Evidence so far

- Both frozen hashes match.
- V2 algebra, projective completeness, exact rank theorems, dense-TT scope,
  circularity boundary, and output requirements are unchanged.
- V3 adds the cumulative canonical-byte traffic equation and conservative
  `b_K*m*B*r^6` sufficient gate.
- Tier A/B/C operations, traffic, retained bytes, and peak workspace are
  separated without adding unlike units.
- Rank-dependent expected and confidence-quantile attempt accounting and the
  stationary exponent gate are explicit.
- D2+D3 preprocessing and advice mismatch are disclosed instead of assuming an
  equal-advice comparator.
- Tier C promotion is conjunctive across every dimension-separated pipeline
  exponent and the relation-attempt gate.

### Failure modes

- Using an average `eta_r` without a state-uniform conditional justification.
- Checking per-target traffic without the attempt multiplier.
- Treating the conservative `O(P*S_j)` access schedule as universal.
- Promoting a Tier A/B compiler observation to Tier C.

The open central-rank obstruction remains. This GO does not establish a compact
compiler or an ECDLP improvement.

### Next concrete action

Derive or refute the gate-by-gate central-rank certificate for the bound RCB
plus norm-indicator circuit, stopping before source code if a central dense
rank reaches `Omega(B)` or any cumulative Tier B gate fails.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v3.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v3.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/red-team-v2.md`
