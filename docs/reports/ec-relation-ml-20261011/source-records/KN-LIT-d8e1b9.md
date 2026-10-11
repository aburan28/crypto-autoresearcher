---
id: KN-LIT-d8e1b9
type: literature
title: "Complexity bounds on Semaev's naive index calculus method for ECDLP"
authors:
  - "Kazuhiro Yokoyama"
  - "Masaya Yasuda"
  - "Yasushi Takahashi"
  - "Jun Kogure"
year: 2020
venue: "Journal of Mathematical Cryptology 14:460-485"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1515/jmc-2019-0029"
  url: null
tags: [index-calculus, prime-field, lower-bound, semaev, naive-index-calculus, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Structural analysis of the Groebner-basis computation for the PDP ideal in Semaev's naive index calculus: the computation is an extension of the extended Euclidean algorithm. This gives a lower bound on its cost and a proof, under simple statistical assumptions on summation polynomials, that the naive method cannot beat generic algorithms. It is the strongest negative result for prime-field summation-polynomial IC.

## Key claims (as reported)

- Naive Semaev IC provably no more efficient than rho/BSGS (under stated statistical assumptions).

## Relevance to this program

Proves (under stated statistical assumptions) that naive Semaev index calculus over F_p cannot beat generic algorithms. The program's prime-field IC negatives (KN-FIND-0618ab and the GOAL-ECDLP-001 lanes) should be scoped against this theorem.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-4558 (bulk stub or misattributed entry; see that file's `superseded_by`).
