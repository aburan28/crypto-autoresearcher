---
id: KN-LIT-5292
type: literature
title: "Observations on the SIMON block cipher family"
authors:
  - "Stefan Kölbl"
  - "Gregor Leander"
  - "Tyge Tiessen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we analyse the general class of functions underlying the Simon block cipher. In particular, we derive efficiently computable and easily implementable expressions for the exact differential and linear behaviour of Simon-like round functions.

## Key claims (as reported)
- Following up on this, we use those expressions for a computer aided approach based on SAT/SMT solvers to find both optimal differential and linear characteristics for Simon.
- Furthermore, we are able to find all characteristics contributing to the probability of a differential for Simon32 and give better estimates for the probability for other variants.
- Finally, we investigate a large set of Simon variants using different rotation constants with respect to their resistance against differential and linear cryptanalysis.
- Interestingly, the default parameters seem to be not always optimal.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160345 (1).pdf`
- `downloads/92160345 (2).pdf`
- `downloads/92160345.pdf`
