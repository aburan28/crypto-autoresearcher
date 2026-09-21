# Independent Benchmark Review: Asymmetric Layers V1

## Handoff: `2A+3R` cost audit

### Claim or task

Determine whether compressing exact witness-bearing `3R` below `q^(1/2)` is
sufficient for a faster-than-rho algorithm.

### Status

`NEGATIVE RESULT` for sufficiency; `REVISE` overall. The positive scalar
support signal remains.

Review pinned to commit
`10214c603a8b7d6869c0b457c2f96b9235456982`. Source/result hashes and
reported regressions reproduce.

### Evidence

The audited exponents are:

| quantity | exponent |
|---|---:|
| columns | `1/4` |
| `2A` scan | `1/4` |
| materialized `3R` | `3/4` |
| `S*T^2` | `5/4` |
| relation collection | `1/2` |
| ordinary sparse linear algebra | `1/2` |

A same-column homogeneous base has the same principal exponents, so the
asymmetry redistributes support but does not create a global exponent gain.
At online time `q^(1/4)`, generic fixed-generator preprocessing can use
roughly `q^(1/2)` advice and `q^(3/4)` construction; the current candidate
uses about `q^(3/4)` advice and is memory-worse.

For column exponent `c`, query exponent `t`, success penalty `u`, rank penalty
`r`, build exponent `p`, descent exponent `d`, and ordinary sparse-LA exponent
`2c`, a strict one-target rho win requires:

- `p < 1/2`;
- `c+t+u+r < 1/2`;
- `2c < 1/2`;
- `d < 1/2`.

With `c=t=1/4`, both relation collection and linear algebra are exactly on
the boundary. A `3R` compiler below square root is therefore insufficient by
itself.

### Hidden costs

The V1 cyclic model omits witness payloads, point keys, hash-table overhead,
bandwidth, executed point-query costs, coordinate construction, relation
overcollection, rank work, linear algebra, descent, and same-advice generic
preprocessing. Its scalar sampler also constructs an avoidable `O(q)` list.

### Next concrete action

Require same-column homogeneous and same-advice generic comparators, exact
witness lift, complete advice bits/build/peak memory, quotient rank or an
anchor, strict relation and LA slack, and charged individual descent.

