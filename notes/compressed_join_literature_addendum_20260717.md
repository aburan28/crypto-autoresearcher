# Literature addendum: compressed joins after the materialized-D4 result

**Prepared:** 2026-07-17  
**Scope:** application-specific 3SUM indexing, preprocessed-universe 3SUM, and transfer to prime-order elliptic-curve point decomposition.

This is an addendum rather than an edit to `structured_group_coordinate_predicates_literature_20260717.md`, whose bytes are bound into the preserved `EXP-ECDLP-FIXED-COMPILER-001` development receipt.

## Dinur-Golovnev subfunction inversion

**Status: THEOREM in the integer model.** Dinur and Golovnev give, for every `0<=delta<=1`, a 3SUM-Indexing data structure with

`S = O~(n^(2.5-delta))`, `T = O~(n^delta)`,

and `O~(n^2)` preprocessing. Their improvement decomposes the pair-sum function into subfunctions and uses modular maps plus exact translation to a source pair. It is the first application-dependent improvement over the prior Fiat-Naor frontier in the stated space window. [Dinur and Golovnev, 2026](https://arxiv.org/abs/2512.04258)

The proof uses facts specific to bounded integers:

- maps `y -> y mod p` and `y -> y mod q` are cheap additive homomorphisms;
- collisions are bounded by counting prime divisors of nonzero integer differences;
- a source `b_j` congruent to a required residue can be found in a sorted remainder list;
- the exact translator can binary-search for `b_j = y-a_i`.

**Status: RESTRICTED THEOREM for the direct EC port.** A prime-order group has no nontrivial homomorphism to a smaller finite group. Therefore the modular-map step has no exact compressed quotient analogue on the abstract EC subgroup. This does not exclude nonlinear coordinate maps; it says they require a new collision and translation analysis.

## Kirkpatrick-Kuszmaul-Mathialagan-Vassilevska Williams

**Status: THEOREM in the integer preprocessed-universe model.** The ICALP 2026 result gives randomized query time `O~(n^(1.5+epsilon))`, space `O~(n^(2-2epsilon/3))`, and `O~(n^2)` preprocessing for unknown-universe subset queries against an oblivious adversary. [Kirkpatrick et al., ICALP 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2026.126)

Its high-level split is relevant:

- heavy sum values are handled by modular convolution and stored false positives;
- light values are isolated by random partitions;
- bounded-indegree function inversion retrieves candidate witnesses;
- every reported candidate is checked against the original equation.

The direct implementation is not EC-compatible. It relies on reduction modulo random primes, integer difference factorization, and FFT convolution over the reduced additive universe. A prime-order EC subgroup provides no cheap nontrivial small quotient, and an `x`-coordinate bucket is not additive.

The transferable research pattern is narrower but useful: measure four-sum witness multiplicity, split heavy and light outputs, randomly partition source witnesses to bound local indegree, and charge exact verification. `EXP-ECDLP-COMPRESSED-JOIN-001` first tests whether any public coordinate map supplies enough subfunction locality to make that pattern worthwhile.

## Earlier 3SUM preprocessing frontier

Golovnev, Guo, Horel, Park, and Vaikuntanathan apply Fiat-Naor inversion to obtain `S^3*T=O~(n^6)` for 3SUM-Indexing and explicitly connect data-structure upper/lower bounds to preprocessing-resistant cryptography. [GGHPV, 2020](https://arxiv.org/abs/1907.08355)

This remains a generic function-inversion baseline. It can be instantiated for an EC pair-sum function only after its input domain, output encoding, collision multiplicity, witness translator, preprocessing time, and verification cost are made explicit.

## Decision for AutoLab

1. Do not claim that the integer compiler ports to EC.
2. Preserve the small-quotient obstruction as a restricted theorem.
3. Test nonlinear coordinate routing against a random-label null and a hidden-scalar positive control.
4. Require exact witness output, not membership bits.
5. Require an equal-advice fixed-base BSGS win before restoring the full relation matrix.
6. If coordinate routers are random-like, move to batch sharing or source-tagged algebraic circuits rather than tuning bucket serialization.
