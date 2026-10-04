---
id: KN-LIT-4fe9d2
type: literature
title: "New results on quasi-subfield polynomials (read at source): beta >= 3/4 for every completely splitting linearized QSP, new families, and the beta < 0.103 threshold for beating generic ECDLP algorithms"
authors: [Euler Marie, Petit Christophe]
year: 2020
venue: arXiv 1909.11326v2 [cs.CR] (v1 2019-09-25); the listing names a journal version, Finite Fields and Their Applications 2021, DOI 10.1016/j.ffa.2021.101881, which was not read
identifiers:
  eprint: null
  doi: null
  arxiv: "1909.11326"
  url: https://arxiv.org/abs/1909.11326v2
  source_package: inputs/EULER-PETIT-2019-QSP
tags: [quasi-subfield-polynomial, linearized-polynomial, companion-matrix, splitting-polynomial,
  additive-subgroup, multiplicative-subgroup, mersenne-prime, solinas-prime, index-calculus,
  ecdlp, complexity-estimate, lower-bound, rank-metric-codes, primary-source, retrieved]
confidence: reported
citation_verified: read
provenance: retrieved
frozen_source: inputs/EULER-PETIT-2019-QSP/
source_record: SRC-EULER-PETIT-2019-QSP
verified_by: cloud-agent session on branch claude/ecc2k-130-quasi-subfield-poly-nhcj1f, 2026-09-16; frozen bytes and hashes in inputs/EULER-PETIT-2019-QSP/provenance.json
added: 2026-09-16
superseded_by: null
---

## Why this record exists

The only follow-up to `KN-LIT-0a321c` (Huang-Kosters-Petit-Yeo-Yun) that an
arXiv search for "quasi-subfield" surfaces on 2026-09-16. It carries the
theorem that closes the linearized (additive-subgroup) branch of that line and
the cleaner complexity bookkeeping that turns the line's fate into one number,
`beta`. Read from the frozen arXiv v2 text at
`inputs/EULER-PETIT-2019-QSP/paper_fulltext.md`; the journal version was not
fetched.

## Definitions (Section 1, as read)

For `L(X) = X^{p^{n'}} - lambda(X) in F_{p^n}[X]` splitting completely (or
with about `p^{n'}` roots), with `l := log_p deg lambda`, the **quality**
`beta(L) := l n / n'^2`; a QSP is one with `beta <= 1` (Definition 2). This is
Huang et al.'s Definition 3.1 renormalised. Lemma 1 restates their Lemma 4.1.

## Key claims (as read)

- **Theorem 1.** If `L = X^{p^{n'}} - (a_l X^{p^l} + ... + a_0 X)` is
  linearized with `l >= 1` and splits completely over `F_{p^n}`, then
  `beta >= 3/4`. Equality example `X^{p^2} + X^p + X` over `F_{p^3}`. Proved
  through Lemma 2: `n >= n' + (n' - l) floor((n' - 1)/l)`, itself proved by a
  symbolic study of powers of the companion matrix (Proposition 1, the
  McGuire-Sheekey / Csajbok et al. criterion: `L` splits completely iff
  `A_L = C_L C_L^sigma ... C_L^{sigma^{n-1}} = I`). Section 2.3: for
  linearized trinomials the same bound was obtained independently by McGuire
  and Mueller.
- **Proposition 2.** For `f in F_p[X]`: `L_f` splits completely over
  `F_{p^n}` iff `L_f | X^{p^n} - X` iff `f | X^n - 1`. (So `F_p`-coefficient
  linearized QSPs over `F_{p^n}` are exactly the divisors of `X^n - 1`.)
- **Proposition 3 (inversion)** maps a completely splitting `L_f` to
  `L_{(X^n - 1)/f}` with `beta` transformed by
  `1 - (n'/(n - n'))^2 (1 - beta(L_f))`; **Proposition 4** lists
  `beta`-preserving transformations defining equivalence classes.
- **Proposition 5** (linearized families): Type 1 = Huang et al.'s Lemma 4.3;
  Type 1bis `X^{p^{n-1}} + ... + X^p + X` with `n' = n - 1`,
  `beta = 1 - 1/(n-1)^2`, for every `n`; Type 2 with `n = q^{d+1} - 1`,
  `beta = 1 - q^{d-1}/(1 + q + ... + q^{d-1})^2`; Type 3 = inverses.
  Section 3.4: Type 2 at `p = 2` gives Mersenne-number `n` and refutes the
  Mersenne heuristic of Huang et al.'s Appendix C.1.
- **Proposition 6** (multiplicative `X^{p^{n'}} - X^a`): three families, needing
  respectively `n = 2ik` even; `p = kn + k - 1` prime with `n' = 1`; or
  `p = kn - k - (-1)^n` prime with `n' = n - 1`. The example `X^8 - X^3` over
  `F_{2^4}` has `beta ~ 0.70 < 3/4`, showing Theorem 1 is specific to
  linearized polynomials. The last two families exist only for `p` of
  Solinas shape and give `beta ~ 1`.
- **Proposition 7** rewrites Huang et al.'s Theorem 3.2 with `kappa` in place
  of `4.876`:
  `O~( m! p^{n(1 + kappa beta (n'm/n)^2 - n'm/n) + n'} m^{5.188} 3^{kappa m^2} + m p^{2n'} )`.
  **Proposition 8**: with `alpha = n'm/n`, the exponent is minimised at
  `alpha_beta = 1/(2 kappa beta)`, giving
  `O~(p^{max(2 alpha_beta/m, 1 - alpha_beta(1/2 - 1/m)) n})`, hence for
  `m >> 1` `O~(p^{(1 - alpha_beta/2) n})`; beating brute force needs
  `m > max(2 alpha_beta, 2)`; beating generic algorithms needs
  `alpha_beta > 1`. **Remark 1**: at `kappa = 4.876` that is `beta < 0.103`;
  the table gives exponent `0.949` at `beta = 1`, `0.744` at `0.2`, `0.487`
  at `0.1`.
- **Section 4.4 (impact).** With Theorem 1, `alpha_beta < 1/7` for every
  linearized QSP, so "it is not possible to beat generic algorithms with
  `L`"; all QSPs exhibited in the paper have `beta > 0.7` and `alpha_beta < 1`.
  Abstract: "Our results do not allow to derive any speedup for the new ECDLP
  algorithm compared to previous approaches."
- **Section 5.** Classification of all QSPs is left open; "further work will
  be needed to improve Huang et al.'s approach with new ideas and better QSP
  families, or to provide a definite proof that it will not improve on
  generic algorithms."

## Discrepancy noted in the source (not adjudicated)

Section 4.4 says that `kappa < 1.5` would give `alpha_beta > 1` at
`beta = 3/4`. From Proposition 8's own `alpha_beta = 1/(2 kappa beta)`, that
requires `kappa < 2/3`. Recorded here so no downstream record inherits the
`1.5` figure without checking it.

## What is verified here and what is not

Statements above are located in the frozen text. The proof of Lemma 2
(Section 2.2, Appendix A) and the proofs of Propositions 5 and 6 were skimmed,
not checked. The claim that Theorem 1 was obtained independently by McGuire
and Mueller is relayed, not checked.

## Relevance to this program

Theorem 1 plus Proposition 2 decide the additive branch at `n = 131` with no
computation: over `F_2` the only divisors of `X^131 - 1` are `X + 1` and the
irreducible `Phi_131` (since `ord_131(2) = 130`), so the only
`F_2`-coefficient linearized QSPs are the subfield `F_2` and Type 1bis with
`beta ~ 1`; over `F_{2^131}` coefficients Theorem 1 caps the quality at
`beta >= 3/4`, i.e. exponent `>= 0.93` at `kappa = 4.876`. Proposition 6's
families do not admit `p = 2, n = 131`. What Theorem 1 does **not** cover is
a non-linearized `lambda` (any `lambda` with a term whose degree is not a
power of `p`), and that is where `RQ-QSP-f9bbdb` places the remaining
question. Every number here is re-derived in `analysis/qsp-ecc2k130/`.

## Limits of applicability

The complexity statements inherit every heuristic of `KN-LIT-0a321c`
(Section 4.3 restates them) and the Rojas solver model; Proposition 8's
asymptotics assume `m >> 1` with `m` fixed, a regime that does not exist at a
concrete `n` where `m` is an integer near `n/n'`.
