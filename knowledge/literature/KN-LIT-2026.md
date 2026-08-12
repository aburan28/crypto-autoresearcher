---
id: KN-LIT-2026
type: literature
title: "A Design Methodology for a DPA-Resistant Cryptographic LSI with RSL Techniques"
authors:
  - "Minoru Saeki"
  - "Daisuke Suzuki"
  - "Koichi Shimizu"
  - "Akashi Satoh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A design methodology of Random Switching Logic (RSL) using CMOS standard cell libraries is proposed to counter power analysis attacks against cryptographic hardware modules. The original RSL proposed in 2004 requires a unique RSL-gate for random data masking and glitch suppression to prevent secret information leakage through power traces.

## Key claims (as reported)
- However, our new methodology enables to use general logic gates supported by standard cell libraries.
- In order to evaluate its practical performance in hardware size and speed as well as resistance against power analysis attacks, an AES circuit with the RSL technique was implemented as a cryptographic LSI using a 130-nm CMOS standard cell library.
- From the results of attack experiments that used a million traces, we confirmed that the RSL-AES circuit has very high DPA and CPA resistance thanks to the contributions of both the masking function and the glitch suppressing function.
- This is the first result demonstrating reduction of the side-channel leakage by glitch suppression quantitatively on real ASIC.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470189 (1).pdf`
- `downloads/57470189 (2).pdf`
- `downloads/57470189 (3).pdf`
- `downloads/57470189.pdf`
