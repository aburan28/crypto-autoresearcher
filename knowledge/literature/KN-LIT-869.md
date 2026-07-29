---
id: KN-LIT-869
type: literature
title: "Faster Key Generation of Supersingular Isogeny Diffie-Hellman"
authors:
  - "Kaizhan Lin"
  - "Fangguo Zhang"
  - "Chang-An Zhao"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1320"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1320"
tags: [curve-arithmetic, elliptic-curve, isogeny, pqc, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Supersingular isogeny Diffie-Hellman (SIDH) is attractive for its relatively small public key size, but it is still unsatisfactory due to its efficiency, compared to other post-quantum proposals. In this paper, we focus on the performance of SIDH when the starting curve is E6 : y 2 = x3 + 6x2 + x, which is fixed in Round-3 SIKE implementation.

## Key claims (as reported)
- Inspired by the previous work [7, 10], we present several tricks to accelerate key generation of SIDH and each process of SIKE.
- Our experimental results show that the performance of this work is at least 6.09% faster than that of the current SIKE implementation, and we can further improve the performance when large storage is available.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1320.pdf`
