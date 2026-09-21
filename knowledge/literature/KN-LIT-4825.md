---
id: KN-LIT-4825
type: literature
title: "Lucky Microseconds: A Timing Attack on Amazon’s s2n Implementation of TLS"
authors:
  - "Martin R. Albrecht"
  - "Kenneth G. Paterson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, protocol, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
s2n is an implementation of the TLS protocol that was released in late June 2015 by Amazon. It is implemented in around 6,000 lines of C99 code.

## Key claims (as reported)
- By comparison, OpenSSL needs around 70,000 lines of code to implement the protocol.
- At the time of its release, Amazon announced that s2n had undergone three external security evaluations and penetration tests.
- We show that, despite this, s2n — as initially released — was vulnerable to a timing attack in the case of CBC-mode ciphersuites, which could be extended to complete plaintext recovery in some settings.
- Our attack has two components.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650136 (1).pdf`
- `downloads/96650136.pdf`
