# IDEA-058 Quadratic-Phase Derivation

## Scope

This artifact freezes the first exact IDEA-058 gate. It reuses P1504's
source-complete four-slot tensor and asks whether its relation indicator has a
short exact quadratic-phase expansion that remains useful after source
conditioning. The coefficient ring is `QQ`; every phase takes values in
`{+1,-1}`. No approximation, amplitude threshold, or target-selected phase is
allowed.

## Frozen Tensor

Each of four ordered source slots selects one point from

```text
[P, -P, 2P, -2P]
```

with two-bit labels `00,01,10,11`. For an eight-bit word

```text
z = (A_0,B_0,A_1,B_1,A_2,B_2,A_3,B_3),
```

let `F(z)=1` exactly when the four selected elliptic points sum to the identity,
and let `F(z)=0` otherwise. P1504 exhaustively verified all 256 words on five
ordinary prime-order curves and found support size 36.

The point labels have known scalar weights `[1,-1,2,-2]`. Every fixture order
is greater than eight, while the integer sum of four weights is in `[-8,8]`.
Consequently

```text
F(z) = 1  iff  w(z_0)+w(z_1)+w(z_2)+w(z_3) = 0 over ZZ.
```

This proves before phase fitting that all five tensors are identical. The
fixture does not expose curve coordinates, exceptional addition charts,
Semaev polynomials, or unknown factor-base discrete logs.

## Quadratic-Phase Grammar

For parameters `(c,l_A,l_B,w,a_A,a_B,a_AB)` in `GF(2)^7`, define

```text
q(z) = c
     + l_A sum_i A_i + l_B sum_i B_i
     + w sum_i A_i B_i
     + a_A sum_{i<j} A_i A_j
     + a_B sum_{i<j} B_i B_j
     + a_AB sum_{i!=j} A_i B_j                 mod 2,

chi_q(z) = (-1)^q(z).
```

The 128 phase columns are invariant under simultaneous permutation of the four
source slots. Their exact rank over `QQ` is 29.

## Exact 20-Term Certificate

Sage `Matrix(QQ,256,128).solve_right(vector(QQ,F))`, with parameters in binary
shortlex order from `0000000` through `1111111`, returns the following nonzero
certificate. This is an exact upper bound, not a certified minimum-support
decomposition.

| phase parameters | coefficient |
|---|---:|
| `0000000` | `3/8` |
| `0000001` | `-1/4` |
| `0000010` | `-1/8` |
| `0000100` | `1/8` |
| `0000110` | `-1/8` |
| `0001000` | `1/4` |
| `0001001` | `-3/8` |
| `0001011` | `1/8` |
| `0001101` | `-1/8` |
| `0001111` | `1/8` |
| `0010000` | `3/8` |
| `0010001` | `-1/4` |
| `0010010` | `-1/8` |
| `0010100` | `1/8` |
| `0010110` | `-1/8` |
| `0100000` | `3/8` |
| `0100001` | `-1/4` |
| `0100010` | `-1/8` |
| `0100100` | `1/8` |
| `0100110` | `-1/8` |

Thus `F(z)=sum_q c_q chi_q(z)` for all 256 words. The coefficient denominators
divide eight. A full Boolean Walsh expansion is an exact generic control: it
has 64 nonzero coefficients, with unnormalized spectrum

```text
0 (192 times), 4 (36 times), -12 (24 times), 36 (4 times).
```

The invariant grammar therefore compresses this fixed scalar predicate from 64
Walsh terms to at most 20 phase terms. Five independently seeded random
36-support tensors have augmented rank 30 against the rank-29 invariant
dictionary and are not representable by this grammar.

## Conditioned Source Counts

For every prefix length `k=0,...,8` and every prefix `u` in `{0,1}^k`, exact
restriction and suffix summation gives

```text
number of valid completions of u
  = sum_q c_q sum_{v in {0,1}^{8-k}} chi_q(u || v).
```

There are `1+2+...+256=511` such prefix conditions. Exhaustive rational replay
has zero mismatches. Choosing the lexicographically first next bit with a
nonzero completion count recovers mask 5, source indices `[0,0,1,1]`, and the
relation `P+P-P-P=O` on every fixture. This establishes exact self-reduction for
the frozen tensor only.

## Generic Character Control

For a cyclic group of prime order `N`, the complete character identity is

```text
delta(sum_i s_i = 0 mod N)
  = (1/N) sum_{k=0}^{N-1} zeta_N^(k sum_i s_i).
```

It uses `N` phases. Evaluating it on a public elliptic factor base requires the
scalar labels `s_i`, which are the discrete-log advice the algorithm is meant to
recover unless the factor base was itself manufactured from known multiples.
The frozen P1504 tensor is exactly such a manufactured-label control.

## Decision Boundary

Retain the 20-term identity as positive exact toy algebra and a useful verifier
control. It does not satisfy IDEA-058's curve-specific public identity premise:

- term count 20 is for one fixed eight-bit tensor and has no asymptotic exponent;
- the tensor is scalar-only and identical across all curves;
- no public coordinate-to-phase construction for a generic factor base exists;
- the generic cyclic character substitute costs `N` phases and leaks scalar labels;
- no relation collection, rank, descent, or end-to-end cost improves on rho.

A successor must derive a scalable phase family directly from public elliptic
coordinates or complete addition polynomials, prove a subcritical exact term
bound, and preserve conditioned source recovery without hidden scalar advice.
