---
id: KN-LIT-316c94
type: literature
title: "Hamming ideals and Gröbner bases for ISD-like syndrome decoding"
authors:
  - "Roberto La Scala"
  - "Michela Marchesin"
  - "Sharwan K. Tiwari"
year: 2026
venue: "preprint, 2026 (venue and identifier not recorded in the text read; see Not verified here)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [syndrome-decoding, information-set-decoding, hamming-weight, hamming-ideal, elementary-symmetric-functions, lucas-theorem, groebner, boolean-polynomials, classic-mceliece, code-based, prange, multisolve, negative-result, point-decomposition, factor-base, external-provenance]
confidence: reported
citation_verified: read
added: "2026-09-30"
superseded_by: null
---

## Provenance of this entry

The full text was pasted into the producing session by the user on
2026-09-30 and read in full by the agent that wrote this entry
(provenance `retrieved`, not `recalled`). The text as read carried no
ePrint, arXiv or DOI identifier, and none is guessed here; the entry lands
in the `SOURCES.md` gap table until someone records one. The paper is not
vendored under `inputs/`.

## Contribution

Models the Hamming-weight constraint `wt(v) = t` on `v ∈ F_2^n` as an
ideal, so that syndrome decoding can be attacked by Gröbner bases with the
weight condition inside the algebra rather than enforced by enumeration.

- **Hamming variety and ideal.** By Lucas' theorem the binary digits of
  `wt(v)` are the Boolean elementary symmetric functions `e_{2^k}(v)`, so
  `H_t = {v : wt(v) = t}` is cut out, modulo the field equations
  `x_i^2 + x_i`, by `e_{2^k}(v) = t_k` for the digits `t_k` of `t`
  (their Theorem 2.3). Only digits up to
  `L = ⌈log₂(max(t, n−t) + 1)⌉ − 1` are needed (Theorem 2.5).
- **Three lifted presentations** with auxiliary variables along a balanced
  binary split of the coordinates, because `e_{2^k}` alone has `C(n, 2^k)`
  monomials: **C-Hamming** (the convolution
  `e_d^{(a,b)} = Σ_k e_k^{(a,m)} e_{d−k}^{(m+1,b)}`, `O(nL)` variables,
  quadratic; Theorem 3.5), **FC-Hamming** (only power-of-two ESFs kept,
  every other `e_j` replaced by its Lucas factorisation
  `Π_{h ∈ bits(j)} e_{2^h}`, `O(n)` variables, degree up to `L + 1`;
  Theorem 4.5), and **QFC-Hamming** (the Lucas products given their own
  variables, `O(nL)` variables, quadratic; Section 5).
- **GBDecode / MultiSolve / OracleT.** An ISD-like decoder that fixes only
  `r ≤ k` coordinates of an information set and solves the rest
  algebraically; `MultiSolve` calls a degree-truncated Gröbner computation
  with a timeout (`GroebnerSafe`) at every node of a binary assignment tree
  and branches when the basis is not linear (`OracleT`: every node is tried);
  tame means the basis is `1` or linear. A residual-weight bound prunes
  branches whose assigned ones already reach `t`.

## Key claims (as reported)

- On Classic McEliece Category 1 parameters the algebraic decoder does
  **not** beat Prange: fixing an entire information set (`r = k`) is the
  cheapest configuration, and each coordinate left free costs Gröbner calls
  that outweigh the combinatorial gain (they quote a `1.24`-bit gain at
  `r = k − 10` that the algebra does not repay).
- The lifted presentations keep every generator at bounded degree with
  `O(n)` or `O(n log n)` auxiliary variables, against `C(n, 2^k)` monomials
  for the unlifted digit equations.

Neither claim was re-derived or re-run here; the McEliece numbers are
reported, not verified.

## Relevance to this program

The construction gives any set defined by a weight condition an algebraic
membership ideal of bounded degree. In a **normal basis** of `F_{2^n}`
Frobenius is a cyclic shift of coordinates, so the weight-bounded set
`F_w = {P : wt_NB(x(P)) ≤ w}` on a binary Koblitz curve is a
Frobenius-stable orbit union at every `n` (prime or not) with a popcount
membership test and, by this paper, a bounded-degree membership ideal. That
is the object `RQ-FROB-7d8dd4` and `KN-OPEN-095df5` ask about: a
Galois-invariant factor base with an explicit algebraic description.
`EV-ICPERF-988da7` transfers the paper's MultiSolve/OracleT search to point
decomposition on `K_0 : y² + xy = x³ + 1` over `F_{2^n}` with Semaev's `S₃`
Weil-descended in normal-basis coordinates and finds the paper's own
McEliece verdict transferred intact at `n ≤ 19`: correct on every target,
resolving only after nearly all coordinates of one summand are fixed, calls
per target growing as `|F_w|^{1.9–2.5}` against the exhaustive oracle's
`|F_w|`. The open remainder is `KN-OPEN-5e3dd0`.

## Not verified here

- Venue and identifier: not present in the text read; not searched for.
- The Classic McEliece cost figures and the `1.24`-bit comparison: reported.
- Theorem numbering follows the text as read (2.3, 2.5, 3.5, 4.5, Section 5)
  and may differ in a published version.
