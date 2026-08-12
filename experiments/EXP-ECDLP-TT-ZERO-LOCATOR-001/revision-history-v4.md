# Direct five-source TT revision history v4

## Claim boundary

This record binds the immutable paper-preflight sequence. A later `GO` means
only that the stated mathematics and accounting are internally reviewable. It
does not authorize implementation or establish a compact compiler.

## Frozen sources

| Version | Preflight SHA256 | Dimension-ledger SHA256 | Outcome |
|---|---|---|---|
| v1 | `5db581dae9305fe43190f766ac3a450bd17830adeaab0c1118859988cb52c720` | `586148e92bab079a39917ef639c5de2a301b3172b79c5b2872a5ccb4884e01ce` | `REVISE` |
| v2 | `b90c09448b740d198b52afbf9743735e0fca12dc51a0011352610fb2fdf49ce1` | `92435885c64f912627e7a212712561f907aa84485c0f326d818e245d4b9fe9fa` | Theory `GO`; accounting `REVISE`; red team `GO` |
| v3 | `c44c079ee393336d4e7c24e2d93ae80e61ea14c75d41a9860c9f0f63c9593864` | `5132e0afe758d351fb13dfca26cbe3296415493a2e4ab9edb58e28a4f364e463` | Accounting and red team `GO`; theory `REVISE` on accounting layer |
| v4 | `f07363f317e1ec0fc1b3e759a782ada43909591a9e53269a51e16d21e0d8fcf0` | `48cb902701223bda3413e4360736cb38872b2974e38f42b2a76a98e0bfe6e23f` | Theory, accounting, and red team `GO`; implementation `NO-GO` |

## Versioned repairs

### V1 to v2

- Replaced the inherited three-source `G_Q` abstraction with a direct
  five-source complete projective addition circuit.
- Bound the addition law to the registered RCB complete formula and included
  the identity target route.
- Proved exact projective equality, exact final-cut ranks, and the distinction
  between low final rank and compact construction.
- Added the explicit rank-two scalar whose zero indicator has central rank
  exactly `B^2`, rejecting a universal constant-rank indicator theorem.
- Added raw Hadamard ranks, exact-normalization work, output localization,
  replay, and Tier A/B/C boundaries.

### V2 to v3

- Replaced the undercharged normalizer estimate by the source-bound exact
  `O(P*S_j)` law with `P<=r^2`.
- Added standard dense raw Hadamard allocation
  `B*(2*r^2+3*r^4)` and separate work, traffic, retained-storage, and peak
  state gates.
- Added canonical byte traffic, logarithmic chain length, relation-attempt
  yield, linear algebra, and descent accounting.

### V3 to v4

- Conditioned every attempt probability on the complete reachable history.
- Restricted exact geometric expectations to the conditionally IID
  rank-state model and supplied history-uniform upper bounds otherwise.
- Required the global binomial gate to use a lower bound valid after every
  prior history, rejecting marginal averages.
- Added target-`g_Q` construction, Frobenius, all sweep/normalization stages,
  final subtraction, localization, certification, replay, metadata, and the
  matching traffic terms.
- Applied the stationary exponent gate separately to every cumulative work
  and traffic resource while keeping peak-live state as a maximum.

## Surviving exact statements

- The bound complete projective circuit has a constant formal pre-indicator
  CP/TT upper bound.
- `1-g_Q^(p^2-1)` is the exact five-source equality indicator.
- Every final TT cut rank equals the number of distinct matching partial sums
  across that cut.
- Generic entry-oracle reconstruction cannot exploit unknown sparse support
  merely from a promised low output rank.
- A universal constant-rank-to-low-rank finite-field indicator theorem is
  false, even for five modes.

## Open obligation

The actual gate-by-gate intermediate central ranks of the bound EC circuit are
not known. This is the immediate proof/disproof target and the reason source
code remains unauthorized.

## Handoff: central-rank boundary

### Claim or task

Prove a witness-preserving sublinear central-rank schedule for the frozen EC
circuit or exhibit a dense minor that reaches the Tier-B boundary.

### Status

`OPEN`

### Assumptions

- Frozen mode order, field, RCB circuit, Frobenius chain, and exact arithmetic.
- All row-space construction, normalization, traffic, and certificates are
  charged.

### Evidence so far

- Final ranks are exactly characterized but do not control construction.
- Generic rank-two inputs can attain central indicator rank `B^2`.
- V4 accounts completely for any proposed intermediate-rank schedule.

### Failure modes

- The proof controls only final support rather than intermediate powers.
- A basis exists abstractly but costs `Omega(B^2)` to construct or move.
- Mode reordering loses source provenance or merely moves the dense cut.

### Next concrete action

Analyze the first norm-Hadamard gate of the bound RCB circuit and either give
an explicit row-space basis with construction cost or a certified nonsingular
minor family.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`

