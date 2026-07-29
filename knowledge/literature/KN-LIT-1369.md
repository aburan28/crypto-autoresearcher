---
id: KN-LIT-1369
type: literature
title: "Decompose and conquer: ZVP attacks on GLV curves"
authors: []
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/076"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/076"
tags: [cryptanalysis, curve-arithmetic, dlp, elliptic-curve, endomorphism, finite-field, glv-gls, pairing, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
While many side-channel attacks on elliptic curve cryptography can be avoided by coordinate randomization, this is not the case for the zero-value point (ZVP) attack. This attack can recover a prefix of static ECDH key but requires solving an instance of the dependent coordinates problem (DCP), which is open in general.

## Key claims (as reported)
- We design a new method for solving the DCP on GLV curves, including the Bitcoin secp256k1 curve, outperforming previous approaches.
- This leads to a new type of ZVP attack on multiscalar multiplication, recovering twice as many bits when compared to the classical ZVP attack.
- We demonstrate a 63% recovery of the private key for the interleaving algorithm for multiscalar multiplication.
- Finally, we analyze the largest database of curves and addition formulas with over 14 000 combinations and provide the first classification of their resistance against the ZVP attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-076.pdf`
