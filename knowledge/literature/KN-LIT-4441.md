---
id: KN-LIT-4441
type: literature
title: "Improved Single-Round Secure Multiplication Using Regenerating Codes"
authors:
  - "Mark Abspoel"
  - "Ronald Cramer"
  - "Daniel Escudero"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [extension-field, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2016, Guruswami and Wootters showed Shamir’s secretsharing scheme defined over an extension field has a regenerating property. Namely, we can compress each share to an element of the base field by applying a linear form, such that the secret is determined by a linear combination of the compressed shares.

## Key claims (as reported)
- Immediately it seemed like an application to improve the complexity of unconditionally secure multiparty computation must be imminent; however, thus far, no result has been published.
- We present the first application of regenerating codes to MPC, and show that its utility lies in reducing the number of rounds.
- Concretely, we present a protocol that obliviously evaluates a depth-d arithmetic circuit in d + O(1) rounds, in the amortized setting of parallel evaluations, with o(n2 ) ring elements communicated per multiplication.
- Our protocol makes use of function-dependent preprocessing, and is secure against the maximal adversary corrupting t < n/2 parties.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900066 (1).pdf`
- `downloads/130900066.pdf`
