---
id: KN-LIT-4450
type: literature
title: "Improving Bounds on Elliptic Curve Hidden Number Problem for ECDH Key Exchange"
authors:
  - "Jun Xu"
  - "Santanu Sarkar"
  - "Huaxiong Wang"
  - "Lei Hu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, ecdsa, elliptic-curve, finite-field, lattice, pairing, prime-field, protocol, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Elliptic Curve Hidden Number Problem (EC-HNP) was first introduced by Boneh, Halevi and Howgrave-Graham at Asiacrypt 2001. To rigorously assess the bit security of the Diffie–Hellman key exchange with elliptic curves (ECDH), the Diffie–Hellman variant of EC-HNP, regarded as an elliptic curve analogy of the Hidden Number Problem (HNP), was presented at PKC 2017.

## Key claims (as reported)
- This variant can also be used for practical cryptanalysis of ECDH key exchange in the situation of side-channel attacks.
- In this paper, we revisit the Coppersmith method for solving the involved modular multivariate polynomials in the Diffie–Hellman variant of ECHNP and demonstrate that, for any given positive integer d, a given sufficiently large prime p, and a fixed elliptic curve over the prime field Fp , 1 if there is an oracle that outputs about d+1 of the most (least) significant bits of the x-coordinate of the ECDH key, then one can give a heuristic algorithm to compute all the bits within polynomial time in log2 p.
- When 1 d > 1, the heuristic result d+1 significantly outperforms both the rigorous 5 bound 6 and heuristic bound 12 .
- Due to the heuristics involved in the Coppersmith method, we do not get the ECDH bit security on a fixed curve.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910066 (1).pdf`
- `downloads/137910066.pdf`
