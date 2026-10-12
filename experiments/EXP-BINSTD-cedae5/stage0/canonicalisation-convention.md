# Canonicalisation convention — EXP-BINSTD-cedae5 Stage 0

Frozen before Stage 1. Experiment `EXP-BINSTD-cedae5`, task
`TASK-20261001-e57118`, hypothesis `H-BINSTD-fe6b59`.

## Residual

For an unordered free-leg pair `(P1, P2)` drawn from window `V` (or `V'_0`),
the residual is

```text
L = -(P1 + P2)
```

computed with the ordinary binary-curve group law
`Y^2 + XY = X^3 + A X^2 + B` over `F_{2^n}`. The identity `O` is recorded
separately; pairs with `P1+P2 = O` produce no finite residual and are
excluded from the hash table (counted under `identity_sum_pairs`).

## Sign fold via `x(L)`

On a binary curve, negation preserves the abscissa:

```text
-(x, y) = (x, x + y)
```

so `x(L) = x(-L)`. The hash key is therefore the integer encoding of
`x(L)` in the polynomial basis. Matching on `x(L)` identifies `{L, -L}`
and is the sign fold required by the HOLD-Q instrument description.

## Optional Frobenius note

Frobenius orbit folding (`φ`-orbit canonicalisation as priced in
`IDEA-20260922-6cf862`) is **not** applied in this experiment. Residuals
are keyed by raw `x(L)` only. Any Koblitz endomorphism speedup or orbit
compression is out of scope for Stages 0–4; disclosing this keeps the
toy census comparable to the `Z/(4ℓ)` replica, which has no Frobenius.

## Hash table discipline (`F2` sweep only)

The hash table is consumed within a single sweep of one window on one
curve (or one generic replica). No artefact is claimed reusable as `F7`
advice for an unrelated future target without re-derivation
(`f2_not_f7_boundary` control).

## Combined-relation certificate

Two attempts with the same key `x(L)` yield a weight-≤4 relation among
window points. Every claimed combined (and full) relation is independently
re-summed on a freshly constructed curve object and must equal `O`
(`certificate.kind: decomposition`). Truncating the key to 8 bits
(Stage 4) must produce a measurable certificate failure rate.

## Windows

- `V`: polynomial-basis window `{P : deg(x(P)) < 9}` on RC-1 (`n=17`).
- `V'_0`: aligned half `{P ∈ V : c_0(x(P)) = 0}` where `c_0` is the
  constant term of `x` (least bit). Predicted ~2× collision rate vs `V`
  if residuals concentrate on one coset of `2E` (structural check, not a fail).
