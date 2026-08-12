# Direct five-source TT accounting review v3

## Handoff: frozen preflight v3 accounting audit

### Claim or task

Verify `preflight-v3.md` at SHA256
`c44c079ee393336d4e7c24e2d93ae80e61ea14c75d41a9860c9f0f63c9593864`
and `object-dimension-ledger-v3.md` at SHA256
`5132e0afe758d351fb13dfca26cbe3296415493a2e4ab9edb58e28a4f364e463`.

### Status

`GO`, accounting layer only.

No implementation, rank claim, or ECDLP improvement is authorized.

### Assumptions

- Vilmart's `O(r*s)` bound is an arithmetic-operation upper bound, not a
  traffic theorem.
- Geometric waiting times and binomial confidence bounds are used only under
  their stated probabilistic assumptions.
- Byte gates include canonical widths and metadata.
- Tier claims remain separate from the open central-rank certificate.

### Evidence so far

- The cumulative byte equation now includes Frobenius, all Hadamard and
  normalizer stages, final subtraction, sweep, locator, and metadata.
- `b_K*m*B*r^6=o(B^2)` and
  `r=o((B/(b_K*m))^(1/6))` are correctly labeled conservative route-specific
  traffic conditions.
- Tier A has explicit `O(B^3)` ceilings and strict `o(B^2)` online gates;
  Tier B remains strict; Tier C tests every unlike dimension separately.
- The expected attempt count, geometric confidence quantile, conservative
  binomial bound, and exponent condition
  `tau+rho+delta_epsilon+delta_eta<2.5` are correct under their assumptions.
- D2+D3 charges `Theta(B^2+B*N2)` construction events, `N2+N3` complete-record
  writes, and at most `N2` reads/probes per target. It is not called a lower
  bound or automatically equal-advice.
- No earlier raw-rank, logarithmic-chain, canonical-byte, final-storage,
  Frobenius, direct-sum, locator, or online-placement repair regressed.

### Failure modes

- Intermediate ranks may still reach the fatal dense-core boundary.
- No coordinate-specific compact compiler or rank certificate is proved.
- Accounting GO is not implementation approval or a sub-rho result.

### Next concrete action

Obtain the remaining exact-byte theory and red-team decisions, then derive the
gate-by-gate central-rank certificate before source authorization.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v3.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v3.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/accounting-review-v2.md`
