# Direct five-source TT theory review v3

## Handoff: frozen preflight v3 theory audit

### Claim or task

Audit `preflight-v3.md` at SHA256
`c44c079ee393336d4e7c24e2d93ae80e61ea14c75d41a9860c9f0f63c9593864`
and `object-dimension-ledger-v3.md` at SHA256
`5132e0afe758d351fb13dfca26cbe3296415493a2e4ab9edb58e28a4f364e463`.

### Status

`REVISE`, accounting layer only. V3 preserves the complete v2 theory GO.

### Assumptions

- Attempts use a preregistered target distribution.
- Rank-increment probability may depend on the complete accepted-row span and
  history, not only its dimension.
- Work, cumulative traffic, retained bytes, and peak state remain separate.

### Evidence so far

- RCB completeness, projective equality, pre-indicator rank, final cut ranks,
  central dense-core gate, and entry-oracle negative remain sound.
- Tier A/B/C separation, canonical traffic condition, and D2+D3 construction
  counts are correctly scoped.
- `b_K*m*B*r^6=o(B^2)` follows as a sufficient traffic condition from the
  conservative access schedule and `P<=r^2`.

### Failure modes

- `E[A]=sum_r 1/(epsilon_r*eta_r)` and independent geometric waiting times are
  exact only when conditional success is constant over every rank-`r` history,
  or under an explicit conditionally IID model.
- A binomial confidence gate needs `p_min` to lower-bound success conditional
  on every prior history until all increments are obtained. A marginal average
  is insufficient.
- The stationary exponent inequality applies separately to every cumulative
  work and traffic resource. Peak state is not multiplied by attempt count.
- Cumulative target work/traffic must explicitly include `g_Q` specialization,
  Frobenius work, certificate output, and independent replay.

### Next concrete action

Issue a versioned repair using full-history conditional probabilities or
uniform conditional lower bounds, and expand every target resource equation to
include specialization, Frobenius, certificates, and replay.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v3.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v3.md`
