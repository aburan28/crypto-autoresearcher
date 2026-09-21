# Theory note: small-quotient obstruction and nonlinear coordinate loophole

## Claim T-CJ-001

**Status: RESTRICTED THEOREM.**

Let `G` be a group of prime order `q`, let `H` be a finite group with `|H| < q`, and let `phi:G->H` be a group homomorphism. Then `phi` is trivial.

### Proof

The image `phi(G)` is a subgroup of `H` and a quotient of `G`. Its order therefore divides both `|G|=q` and `|H|`. Since `q` is prime and `|H|<q`, the only common divisor is one. Hence `|phi(G)|=1`, so `phi` maps every element of `G` to the identity of `H`. QED.

### Consequence

An integer 3SUM router can use reduction modulo a much smaller prime because `Z -> Z/rZ` is a nontrivial homomorphism with a compressed range. A prime-order EC subgroup has no analogous nontrivial smaller quotient. If the target group has at least `q` elements, the map supplies no range-size compression; if it has fewer, an exact homomorphism is constant.

### What this does not prove

The theorem does not rule out:

- nonlinear coordinate maps such as `x mod r`;
- a multi-valued relation rather than a function;
- lossy hashing followed by exact verification;
- maps into rings or varieties whose size is not the advice cost;
- batch algorithms sharing work across targets;
- source-tagged witness states;
- auxiliary curves, isogenies, endomorphisms, or extension-field representations;
- an algorithm that avoids quotient routing entirely.

It blocks only the direct plan "replace integer reduction modulo a small prime with an exact small EC quotient."

## Coordinate-router hypothesis

**Status: HYPOTHESIS.**

A nonlinear feature `h(P)` may still make the ternary relation

`h(a+b), h(a), h(b)`

sparser than a random labeling when `a,b` lie in a coordinate-defined support rather than the whole group. The relevant quantity is not whether `h` is a homomorphism, but whether the exact route relation has fewer distinct triples and lower verified candidate work after bucket populations are charged.

## Information accounting

Let `n=|D2|`, let `r` be the number of buckets, and let `E_h` be the number of distinct route triples. A fixed-width lower estimate for the router payload contains at least:

- `n` encoded D2 points;
- `2n` factor-base indices for canonical pair witnesses;
- bucket-directory information;
- `E_h * 3*ceil(log2 r)` route bits.

For a random label and sufficiently populated bucket pairs, `E_h` approaches `r^3`; for an addition-compatible representation it can approach `O(r^2)`. This is only a counting diagnostic. Exact query work also depends on bucket populations and on how many false candidates survive each route.

## Proof and disproof tracks

### Proof track

1. Find a public coordinate family for which `E_h=o(r^3)` on `D2` while `D4` remains expansive.
2. Explain the sparsity using an addition-law invariant, algebraic correspondence, or additive-combinatorial statement.
3. Prove that witness recovery and route evaluation have the claimed cost without hidden discrete logs.
4. Restore relation rank, linear algebra, and individual descent.

### Disproof track

1. Show route triples match a random-label occupancy model after bucket populations are conditioned on.
2. Construct coordinate-family counterexamples where apparent route sparsity comes only from empty buckets.
3. Show exact verification work cancels any route-table compression.
4. Derive a restricted expansion theorem for the tested coordinate features and support regime.

## Strongest permitted negative

If every tested coordinate feature fails, the conclusion is:

> No improvement was found for these public coordinate bucket maps, bucket counts, factor-base families, and toy curves; direct small-homomorphic routing is separately excluded by T-CJ-001.

It is not a theorem against index calculus or all coordinate compilers.
