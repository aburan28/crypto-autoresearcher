# EXP-ECDLP-1bef8f Stage 0 implementation note

Scope: Stage 0 fixture reproduction only, authorized by
`DEC-20260913-0f8468`. Stages 1–3 are not implemented or entered.

The pre-existing untracked draft was audited before execution. The curve
arithmetic, exhaustive two-directional relation check, asymmetric-height
enumeration, sparse-polynomial expansion, exact-rational decimal rendering,
whole-group indexing, ordered convolution, and seeded matched-null construction
were checked against anchors (a)–(e) in the frozen specification.

Changes required before launch:

- Removed 60 additional random generic-control draws. The contract permits no
  stochastic sampling beyond the 60 seeded matched-null draws. The partially
  applicable relabelled-`Z/nZ` density control now deterministically forgets
  curve and height labels after indexing and recomputes the complete count
  vector in `Z/nZ`.
- Corrected KF-1. The draft had accurately computed
  `P(m)/P(m+1) = c_H` but then incorrectly said the finite sequence did not
  decrease. With `c_H > 1`, it does decrease by a constant factor. The repaired
  control computationally verifies the frozen claim actually at issue:
  multiplying `n/c_H^m` by `c_H^m` recovers `n`, and the formal exponent of
  `n` remains exactly one for every tested arity. It does not turn a
  constant-factor change into an exponent claim.
- Captured git revision and dirty state before artifact creation, corrected
  execution-session model provenance, represented certificate kind `none` with
  null verification fields, and recorded the resource-limited exact command.
- Added explicit matched-null checks for size, negation closure, and conserved
  mean on every draw.

No frozen anchor, success criterion, sample count, seed, or interpretation was
changed. The implementation uses only Python standard-library integer arithmetic
and `fractions.Fraction` for anchor computations. Decimal anchor comparisons are
rendered from exact rationals with integer arithmetic.

Protocol deviation: the implementation note is stored here instead of the
repository-standard experiment-root `implementation.md`, because the assigned
write scope permits `implementation/**` but not that root path.

Binding limit: the density/coverage observable has already collided with the
matched negation-closed null. Reproducing it is only a fixture check and cannot
support a claim about the height box, coverage, additive structure, or ECDLP.
