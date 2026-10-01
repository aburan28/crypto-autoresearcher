---
id: KN-LIT-074c32
type: literature
title: "On the Use of the Negation Map in the Pollard Rho Method"
authors:
  - "Joppe W. Bos"
  - "Thorsten Kleinjung"
  - "Arjen K. Lenstra"
year: 2010
venue: "ANTS IX, LNCS 6197, pp. 66-82"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-642-14518-6_9"
  url: "https://infoscience.epfl.ch/record/164553"
tags: [pollard-rho, negation-map, fruitless-cycles, equivalence-classes, simd, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Shows that walks on {+-P} classes get trapped in fruitless cycles (2-cycles with probability ~1/(2r) per step for r-adding walks, plus longer cycles). Earlier countermeasures suffer recurring cycles. The paper gives better countermeasures but concludes the practical gain is far below the theoretical sqrt(2), especially on SIMD hardware.

## Key claims (as reported)

- Best practical negation speed-up found: 1.29 (vs sqrt(2) ~ 1.414 in theory).

## Relevance to this program

Fruitless cycles are the price of walking on {±P} classes: 2-cycles with probability ~1/(2r) per step for r-adding walks, plus longer cycles and recurring cycles under naive escapes. Practical negation gain found: 1.29 (theory √2). Directly relevant to the ECC2K-130 table walk's 4- and 6-step cycles and to EXP-RHO-60da4f, whose escape rules all lost to plain rho.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
