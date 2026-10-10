---
id: KN-LIT-fc822d
type: literature
title: "On the Menezes-Teske-Weng conjecture (Mesnager, Kim, Choe, Tang) -- proof of Conjecture 15 of Weak Fields for ECC"
authors:
  - "Sihem Mesnager"
  - "Kwang Ho Kim"
  - "Junyop Choe"
  - "Chunming Tang"
year: 2020
venue: "Cryptography and Communications 12(1) (2020) 19-27 (venue as reported by DBLP via web search, not read); arXiv:1807.01858 (v1, 5 July 2018, read)"
identifiers:
  eprint: null
  doi: null
  arxiv: "1807.01858"
  url: "https://arxiv.org/abs/1807.01858"
tags: [weak-fields, ghs, generalized-ghs, hess, binary-field, quadratic-equation, trace, conjecture-proved, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-09"
superseded_by: null
---

## Contribution

Proves Conjecture 15 of KN-LIT-d7995a (Menezes-Teske-Weng, Weak Fields for
ECC), which that paper had only checked experimentally (10000 random beta at
each of thirteen field sizes, 30 <= N <= 222). The conjecture is the
correctness condition for Algorithm 11 there: the test that decides whether
b in F_{q^6} admits b = (gamma_1 gamma_2)^2 with Ord_{gamma_i} | X^4+X^2+1,
i.e. whether a curve over F_{2^{6l}} with Tr(a) = 0 reduces under Hess'
generalized GHS to a genus-15 (or genus-12) curve over F_{2^l}.

## Statement proved (read from arXiv v1)

- **Conjecture 1.1** (= Conjecture 15 of [MTW]): q = 2^l, beta in
  F_{q^6}^*. If u^2 + (beta^{q^4-1} + beta^{q^2-1} + 1) u + beta^{q^2-1} = 0
  has two solutions u_1, u_2 in F_{q^6}, then both satisfy
  u^{q^2+1} + u + 1 = 0.
- **Theorem 2.1** (more general, over a cubic extension): q = 2^s, beta in
  F_{q^3}^*. If u^2 + (beta^{q^2-1} + beta^{q-1} + 1) u + beta^{q-1} = 0 for
  some u in F_{q^3}, then u^{q+1} + u + 1 = 0. Moreover, when
  Tr_{q^3/q}(beta) != 0, the quadratic holds for u in F_{q^3} iff
  u^{q+1} + u + 1 = 0 and beta u + beta^q + beta in F_q. The conjecture
  follows by taking q^2 for q.
- The paper then determines the null space of a class of linear
  polynomials using the result (not read in detail; not needed here).

## Key claims: verified versus reported

The proof of Theorem 2.1 is a short direct manipulation of the quadratic and
was read but not independently re-derived. The published venue and page
range come from a DBLP listing surfaced by web search and were not fetched;
the arXiv record was. An IACR ePrint mirror (2018/659) was also reported by
the search and is not recorded as an identifier because it was not fetched.

## Relevance to this program

Closes the one conjectural step in the Section 5.3 argument of
KN-LIT-d7995a: the membership test for the Hess genus-15 family over
F_{2^{6l}} is now proven sound, so a class screen that implements Algorithm
11 (see KN-LIT-d7995a, "Relevance", and KN-LIT-f64d86) rests on a theorem,
not on the 2003 experiments. Nothing here changes any cost estimate.

## Provenance

Retrieved 2026-10-09 from `https://arxiv.org/pdf/1807.01858` (134,886
bytes, 10 pages), text extracted with `pdftotext -layout`. Retrieval
record: `inputs/MTW-WEAK-FIELDS-20261009/provenance.json`.

## Local copies

- `inputs/MTW-WEAK-FIELDS-20261009/sources/mesnager-kim-choe-tang-arxiv-1807.01858v1.pdf` and `.txt`
