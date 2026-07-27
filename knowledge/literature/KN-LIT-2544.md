---
id: KN-LIT-2544
type: literature
title: "Anonymous Counting Tokens"
authors:
  - "Fabrice Benhamouda⋆"
  - "Mariana Raykova"
  - "Karn Seth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new primitive called anonymous counting tokens (ACTs) which allows clients to obtain blind signatures or MACs (aka tokens) on messages of their choice, while at the same time enabling issuers to enforce rate limits on the number of tokens that a client can obtain for each message. Our constructions enforce that each client will be able to obtain only one token per message and we show a generic transformation to support other rate limiting as well.

## Key claims (as reported)
- We achieve this new property while maintaining the unforgeability and unlinkability properties required for anonymous tokens schemes.
- We present four ACT constructions with various trade-offs for their efficiency and underlying security assumptions.
- One construction uses factorization-based primitives and a cyclic group.
- It is secure in the random oracle model under the q-DDHI assumption (in a cyclic group) and the DCR assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438179 (1).pdf`
- `downloads/14438179.pdf`
