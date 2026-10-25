---
id: KN-LIT-c1e815
type: literature
title: "Acceleration of index calculus for solving ECDLP over prime fields and its limitation (abstract plus two secondary restatements): hybrid method, (x1+x2, x1x2) symmetrisation and GCD solving on the Amadori variant; neither APS nor PKM outperforms rho; cost at least p^{2/3}"
authors:
  - "Momonari Kudo"
  - "Yuki Yokota"
  - "Yasushi Takahashi"
  - "Masaya Yasuda"
year: 2018
venue: "CANS 2018, LNCS 11124, pp. 377-393"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-030-00434-7_19"
  url: null
tags: [index-calculus, prime-field, summation-polynomial, groebner, hybrid-method, symmetrisation, gcd-solving, limits, ecdlp]
confidence: reported
citation_verified: web
added: "2026-10-25"
superseded_by: null
---

## Contribution

Accelerates the Amadori–Pintore–Sala variant (KN-LIT-1e6270) and analyses
its limitation. Supersedes the stub KN-LIT-17ea20 by adding what the
accessible sources say the three accelerations are and what the limit is.
**The full text is paywalled and was not read**; everything below is from
the abstract (Wayback copy of the Springer page) and two secondary
restatements by other authors.

## Key claims (as reported)

- Abstract (verbatim): "In 2018, Amadori et al. proposed a new variant of
  index calculus ... The variant drastically decreases the number of required
  Gröbner basis computations, and it outperforms other index calculus
  algorithms for the ECDLP over prime fields. In this paper, we provide
  several improvements to accelerate to solve systems of multivariate
  equations arising in the variant. A main improvement is to apply the hybrid
  method, which mixes exhaustive search and Gröbner bases techniques ... We
  also make use of symmetries of summation polynomials. We show experimental
  results of our improvements, and give their complexity analysis to discuss
  a limitation of our acceleration in both theory and practice."
- Dzierzkowski–Wroński 2024 §3.2.4 (KN-LIT-44eaba, full text read): the
  three improvements are (1) the hybrid approach of Bettale–Faugère–Perret,
  (2) the symmetrisation `t_1 = x_1 + x_2, t_2 = x_1 x_2` so that
  `f_3(t_1, t_2, x_R)` has total degree 2 instead of 4, and (3) "solving
  system via GCD computation, where efficient computation of
  `GCD(f_3(x_1, x_Q, x_R), f(x_1)) ∈ F_p[x_1]` is used"; "These three
  improvements significantly accelerate the variant of Amadori even though
  this method's complexity is at least `p^{2/3}`, compared to the complexity
  `p^{1/2}` of Pollard's rho and baby step – giant step methods."
- Yokoyama–Yasuda–Takahashi–Kogure 2020 §1 (KN-LIT-8bf122, full text read):
  "An experimental study by [Kudo et al. 2018] showed that both methods of
  [Amadori et al., Petit et al.] do not outperform generic algorithms such as
  the rho method for solving ECDLP over prime fields."
- A predecessor workshop paper exists: Yokota, Kudo, Yasuda, "Practical limit
  of index calculus algorithms for ECDLP over prime fields", WCC 2017 (text not
  retrievable).

## Relevance to this program

The GCD step (3) computes exactly what the aburan28/crypto direct-subtraction
oracle computes (the `S_3` root in `X` is `x(R ∓ F_i)`), at `Õ(B)` instead of
`O(B)`; the hybrid (1) fixes variables and then pays the split-base Groebner
floor on the rest, so it is dominated by MITM enumeration; the symmetrisation
(2) is in `symmetrized_semaev.rs`. See `KR-IC-dbf1b0`.

## Not verified here

Everything: the paper's own tables, the exact complexity statement and the
scope of "limitation" are known only through the abstract and the two
restatements above.

## Provenance

Abstract and secondary sources read on 2026-10-24 by delegated literature
lanes of the session recorded in DEC-20261025-48232f; Crossref record
confirms APS as reference [1] of this paper.
