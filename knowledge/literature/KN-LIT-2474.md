---
id: KN-LIT-2474
type: literature
title: "An Efficient Countermeasure against Correlation Power-Analysis Attacks with Randomized Montgomery Operations for DF-ECC Processor"
authors:
  - "Jen-Wei Lee"
  - "Szu-Chi Chung"
  - "Hsie-Chia Chang"
  - "Chen-Yi Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, elliptic-curve, finite-field, implementation, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Correlation power-analysis (CPA) attacks are a serious threat for cryptographic device because the key can be disclosed from data-dependent power consumption. Hiding power consumption of encryption circuit can increase the security against CPA attacks, but it results in a large overhead for cost, speed, and energy dissipation.

## Key claims (as reported)
- Masking processed data such as randomized scalar or primary base point on elliptic curve is another approach to prevent CPA attacks.
- However, these methods requiring pre-computed data are not suitable for hardware implementation of real-time applications.
- In this paper, a new CPA countermeasure performing all field operations in a randomized Montgomery domain is proposed to eliminate the correlation between target and reference power traces.
- After implemented in 90-nm CMOS process, our protected 521-bit dual-field elliptic curve cryptographic (DF-ECC) processor can perform one elliptic curve scalar multiplication (ECSM) in 4.57ms over GF (p521 ) and 2.77ms over GF (2409 ) with 3.6% area and 3.8% power overhead.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280547 (1).pdf`
- `downloads/74280547 (2).pdf`
- `downloads/74280547 (3).pdf`
- `downloads/74280547.pdf`
