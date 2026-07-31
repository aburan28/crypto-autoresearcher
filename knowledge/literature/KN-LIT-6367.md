---
id: KN-LIT-6367
type: literature
title: "Scalable and Unconditionally Secure Multiparty Computation"
authors:
  - "Ivan Damgård"
  - "Jesper Buus Nielsen⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a multiparty computation protocol that is unconditionally secure against adaptive and active adversaries, with communication complexity O(Cn)k + O(Dn2 )k + poly(nκ), where C is the number of gates in the circuit, n is the number of parties, k is the bitlength of the elements of the field over which the computation is carried out, D is the multiplicative depth of the circuit, and κ is the security parameter. The corruption threshold is t < n/3.

## Key claims (as reported)
- For passive security the corruption threshold is t < n/2 and the communication complexity is O(nC)k.
- These are the first unconditionally secure protocols where the part of the communication complexity that depends on the circuit size is linear in n.
- We also present a protocol with threshold t < n/2 and complexity O(Cn)k + poly(nκ) based on a complexity assumption which, however, only has to hold during the execution of the protocol – that is, the protocol has so called everlasting security.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220565 (1).pdf`
- `downloads/46220565 (2).pdf`
- `downloads/46220565 (3).pdf`
- `downloads/46220565.pdf`
