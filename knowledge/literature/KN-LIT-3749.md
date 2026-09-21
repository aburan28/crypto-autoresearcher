---
id: KN-LIT-3749
type: literature
title: "Extending the Salsa20 nonce"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces the XSalsa20 stream cipher. XSalsa20 is based upon the Salsa20 stream cipher but has a much longer nonce: 192 bits instead of 64 bits.

## Key claims (as reported)
- XSalsa20 has exactly the same streaming speed as Salsa20, and its extra nonce-setup cost is slightly smaller than the cost of generating one block of Salsa20 output.
- This paper proves that XSalsa20 is secure if Salsa20 is secure: any fast attack on XSalsa20 using q queries and succeeding with probability p can be converted into a fast attack on Salsa20 succeeding with probability at least p/(q + 1).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/xsalsa-20110204.pdf`
