---
id: KN-LIT-3826
type: literature
title: "Faster and Timing-Attack Resistant AES-GCM"
authors:
  - "Emilia Käsper"
  - "Peter Schwabe ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, implementation, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a bitsliced implementation of AES encryption in counter mode for 64-bit Intel processors. Running at 7.59 cycles/byte on a Core 2, it is up to 25% faster than previous implementations, while simultaneously offering protection against timing attacks.

## Key claims (as reported)
- In particular, it is the only cache-timing-attack resistant implementation offering competitive speeds for stream as well as for packet encryption: for 576-byte packets, we improve performance over previous bitsliced implementations by more than a factor of 2.
- We also report more than 30% improved speeds for lookup-table based Galois/Counter mode authentication, achieving 10.68 cycles/byte for authenticated encryption.
- Furthermore, we present the first constant-time implementation of AES-GCM that has a reasonable speed of 21.99 cycles/byte, thus offering a full suite of timing-analysis resistant software for authenticated encryption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470001 (1).pdf`
- `downloads/57470001 (2).pdf`
- `downloads/57470001 (3).pdf`
- `downloads/57470001.pdf`
