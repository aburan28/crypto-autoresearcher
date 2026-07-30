---
id: KN-LIT-6045
type: literature
title: "PUFKY: A Fully Functional PUF-based Cryptographic Key Generator"
authors:
  - "Roel Maes"
  - "Anthony Van Herrewege"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present PUFKY: a practical and modular design for a cryptographic key generator based on a Physically Unclonable Function (PUF). A fully functional reference implementation is developed and successfully evaluated on a substantial set of FPGA devices.

## Key claims (as reported)
- It uses a highly optimized ring oscillator PUF (ROPUF) design, producing responses with up to 99% entropy.
- A very high key reliability is guaranteed by a syndrome construction secure sketch using an efficient and extremely low-overhead BCH decoder.
- This first complete implementation of a PUF-based key generator, including a PUF, a BCH decoder and a cryptographic entropy accumulator, utilizes merely 17% (1162 slices) of the available resources on a low-end FPGA, of which 82% are occupied by the ROPUF and only 18% by the key generation logic.
- PUFKY is able to produce a cryptographically secure 128-bit key with a failure rate < 10−9 in 5.62 ms.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280300 (1).pdf`
- `downloads/74280300 (2).pdf`
- `downloads/74280300 (3).pdf`
- `downloads/74280300.pdf`
