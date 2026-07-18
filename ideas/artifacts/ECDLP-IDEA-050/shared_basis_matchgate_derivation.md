# IDEA-050 Shared-Basis Matchgate Derivation Gate

Date: 2026-07-17

## Missing Definition Repaired

The IDEA-050 hypothesis names an "elliptic addition signature" without fixing
which finite tensor contains the factor-base source choices.  Testing only the
signs of four already selected x-coordinate lifts is inadequate: it can produce
a matchgate while leaving the hard factor-base tuple search outside the tensor.

For this gate, freeze a four-point exact factor base

```text
F = [P, -P, 2P, -2P]
```

on a prime-order ordinary curve.  Encode each index in two bits using
`00,01,10,11`.  The complete four-source relation tensor is the arity-eight
Boolean tensor

```text
f_T(i1,i2,i3,i4) = 1 iff F[i1]+F[i2]+F[i3]+F[i4] = T,
                    0 otherwise.
```

Every one of the `4^4=256` source tuples is retained.  The identity-target
tensor has 36 valid source tuples on every frozen fixture.

## Shared Basis Action

Let

```text
B = [[a,b],[c,d]] in GL(2,F_p).
```

The same public matrix acts on all eight Boolean legs:

```text
g_y = sum_x f_x product_j B[y_j,x_j].
```

This is the reusable shared holographic-basis interpretation of IDEA-050.
Multiplying `B` by a nonzero scalar only scales `g`, so exhaustive search uses
the unique representative whose first nonzero entry is one.  This gives exactly
`p*(p^2-1)` projective basis classes.

## Exact Matchgate Gate

A standard Boolean matchgate signature must have definite parity: all odd
entries or all even entries vanish.  Every parity-passing tensor must also obey
the matchgate identities.  For bit strings `alpha,beta` and differing positions
`p1<...<pl`, freeze the convention

```text
sum_(j=1..l) (-1)^j
  g[alpha xor e_pj] g[beta xor e_pj] = 0.
```

All `2^8` choices of each bit string are checked.  A deterministic Pfaffian
minor signature is the positive identity control.  Transporting it through the
inverse of `[[1,1],[1,-1]]` and applying that shared basis must recover the
original signature exactly and pass every identity.

## Frozen Curve Panel

All curves have prime group order and nonzero trace modulo `p`, hence are
ordinary.

| p | a | b | #E |
|---:|---:|---:|---:|
| 11 | 1 | 5 | 11 |
| 13 | 0 | 2 | 19 |
| 17 | 1 | 3 | 17 |
| 19 | 0 | 2 | 13 |
| 23 | 1 | 4 | 29 |

For each curve, choose the lexicographically first affine point as `P`, verify
its prime order, build the factor base above, enumerate all 256 source tuples,
and exhaust every projective shared basis over `F_p`.

## Controls And Boundary

- The transported Pfaffian control must have at least one recovered matchgate
  basis and no identity residual.
- A deterministic random 36-support tensor is scanned with the same complete
  basis catalog on every field.
- A four-sign tensor with support only at `0000` and `1111` must pass after a
  Hadamard basis, while being labelled inadequate because it starts after the
  four x-coordinate sources have already been selected.
- Mutating one source tuple, determinant test, parity decision, or matchgate
  residual must fail the independent audit.

A zero matchgate-basis count on the complete elliptic tensors rejects the shared
binary-basis formulation before scaling.  It does not rule out independent
per-leg transforms, larger local domains, extension-field bases, or a different
source-complete network.  Any successor must define that representation and
charge its compilation, contraction, and source self-reduction costs.
