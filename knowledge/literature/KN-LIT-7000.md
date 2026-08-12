---
id: KN-LIT-7000
type: literature
title: "The Insecurity of Esign in Practical Implementations"
authors:
  - "Pierre-Alain Fouque"
  - "Nick Howgrave-Graham"
  - "Gwenaëlle Martinet"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, provable-security, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Provable security usually makes the assumption that a source of perfectly random and secret data is available. However, in practical applications, and especially when smart cards are used, random generators are often far from being perfect or may be monitored using probing or electromagnetic analysis.

## Key claims (as reported)
- The consequence is the need of a careful evaluation of actual security when idealized random generators are implemented.
- In this paper, we show that Esign signature scheme, like many cryptosystems, is highly vulnerable to so called partially known nonces attacks.
- Using a 1152-bit modulus, the generation of an Esign signature requires to draw at random a 768-bit integer.
- We show that the exposure of only 8 bits out of those 768 bits, for 57 signatures, is enough to recover the whole secret signature key in a few minutes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28940501 (1).pdf`
- `downloads/28940501 (2).pdf`
- `downloads/28940501.pdf`
