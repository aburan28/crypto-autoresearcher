---
id: KN-LIT-4524
type: literature
title: "Instruction Set Extensions for Fast Arithmetic"
authors:
  - "Johann Großschädl"
  - "Erkay Savaş"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, finite-field, implementation, pairing, prime-field, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Instruction set extensions are a small number of custom instructions specifically designed to accelerate the processing of a given kind of workload such as multimedia or cryptography. Enhancing a general-purpose RISC processor with a few application-specific instructions to facilitate the inner loop operations of public-key cryptosystems can result in a significant performance gain.

## Key claims (as reported)
- In this paper we introduce a set of five custom instructions to accelerate arithmetic operations in finite fields GF(p) and GF(2m ).
- The custom instructions can be easily integrated into a standard RISC architecture like MIPS32 and require only little extra hardware.
- Our experimental results show that an extended MIPS32 core is able to perform an elliptic curve scalar multiplication over a 192-bit prime field in 36 msec, assuming a clock speed of 33 MHz.
- An elliptic curve scalar multiplication over the binary field GF(2191 ) takes only 21 msec, which is approximately six times faster than a software implementation on a standard MIPS32 processor.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560132 (1).pdf`
- `downloads/31560132 (2).pdf`
- `downloads/31560132.pdf`
