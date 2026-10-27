---
id: KN-LIT-0b036e
type: literature
title: "Matrix multiplication exponent bounds in openai/math family 107 (omega(C) <= 9/4; omega < 2.258; omega(F) < 2.3710549 over every field)"
authors:
  - "OpenAI (unnamed internal model; no human author listed)"
year: 2026
venue: "openai/math repository, family 107 (manuscripts dated 2026-09-24 and 2026-10-02), present since the initial commit adc7f12 (2026-10-06)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://github.com/openai/math/blob/main/lean/docs/107.md"
tags: [matrix-multiplication, omega, linear-algebra, groebner, f4, characteristic-2, first-fall-degree, galactic, openai-math, unverified-proof]
confidence: reported
citation_verified: read
added: "2026-10-27"
superseded_by: null
---

## Contribution (as reported)
- **`ω(ℂ) <= 9/4`.** Manuscript `Matrix-Multiplication-Nine-Fourths-October-2-2026`,
  in the arithmetic-operation model.
- **`ω < 2.258` and dual exponent `α > 0.465`, in characteristic 0.**
  Manuscript `Complex-Matrix-Multiplication-Below-2.258-and-Rectangular-Bounds`.
  The bound also holds "outside finitely many positive characteristics",
  which are not computed.
- **`ω(F) < 2.371054886006746` for every field `F`.** Manuscript
  `Staggered-extraction-for-exact-matrix-multiplication-over-every-field`.
  This is `2.8·10^-4` below the published `2.371339` (Alman et al., SODA
  2025).

**Lean scope** (`lean/docs/107.md`, unchanged since `adc7f12`):
- `complex_omega_le_nine_quarters`: `ω(ℂ) <= 9/4`, plus the dual and
  rectangular bounds.
- `omega_lt_source_constant`: `ω(F) < 2.371054886…` for every field.

Neither Comparator statement was compared with its paper here, and the Lean
was not built.

## Characteristic 2 (what binary-field index calculus needs)
- **`2.371054886…`**: claimed formalized for every field, so it applies to
  characteristic 2 if the formalization is faithful.
- **`2.258`**: undetermined at `p = 2`. The excluded primes divide an
  uncomputed denominator.
- **`9/4`**: conditional. See `KN-OPEN-57907f`.
  - The paper's only characteristic-dependent step found by
    `crypto/src/cryptanalysis/matmul_exponent.rs` (2026-10-07) is a
    primitive `L`-th root of unity with `L = 5M`. That step transfers to
    `GF(2^k)`, and is tested there for `k = 3..18`.
  - Appendix A (detecting characters) uses finite-dimensional separation,
    compactness and a fixed-point theorem in Strassen's asymptotic spectrum.
    None of these depends on the field on its face.
  - The corpus states and formalizes `9/4` only over `ℂ`. That is an
    unexplained gap, not evidence against characteristic 2.

## Correction of an internal record
The 2026-10-07 review in `crypto` (literature-note addendum, and
`matmul_exponent.rs`) treated the characteristic-0 `9/4` proof as one that
"nobody here has verified". It did not mention that the corpus already
claimed a Lean proof on 2026-10-06. A first draft of the 2026-10-26 addendum
(`crypto` PR #2680) said 107 "now has" a Lean scope. That was wrong, and was
corrected before merge after `git log lean/docs/107.md`.

## Relevance
- **Model only.** `ω` enters the summation-polynomial cost model through the
  Kousidis–Wiemers formula (`c = 2ω/3`). At `n = 131`, `ω = 9/4` gives
  `2^68.96`, above both generic (`2^65.5`) and rho (`2^60.8`). That model
  assumes first fall degree, which is contested.
- **The turning point moves.** It falls from `n = 357` (published `ω`) to
  `n = 227` (`9/4`).
- Every row is existence-only or galactic. No practical algorithm reaches
  these exponents.

## Limits
- The proofs are unverified here, and their Lean statements were not
  compared with the papers.
- Arithmetic complexity only, with no practical crossover.
