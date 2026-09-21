---
id: KN-LIT-3799
type: literature
title: "Fast Encryption and Authentication in a Single Cryptographic Primitive"
authors:
  - "Niels Ferguson"
  - "Doug Whiting"
  - "Bruce Schneier"
  - "John Kelsey"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Helix is a high-speed stream cipher with a built-in MAC functionality. On a Pentium II CPU it is about twice as fast as Rijndael or Twofish, and comparable in speed to RC4.

## Key claims (as reported)
- The overhead per encrypted/authenticated message is low, making it suitable for small messages.
- It is efficient in both hardware and software, and with some pre-computation can effectively switch keys on a per-message basis without additional overhead.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28870348 (1).pdf`
- `downloads/28870348 (2).pdf`
- `downloads/28870348.pdf`
