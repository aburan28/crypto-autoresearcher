---
id: KN-LIT-6059
type: literature
title: "qDSA: Small and Secure Digital Signatures with Curve-based Diffie–Hellman Key Pairs"
authors:
  - "Joost Renes"
  - "Benjamin Smith"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, ecdsa, elliptic-curve, hyperelliptic, implementation, jacobian, mov-fr, pairing, protocol, provable-security, signature, summation-polynomial, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
qDSA is a high-speed, high-security signature scheme that facilitates implementations with a very small memory footprint, a crucial requirement for embedded systems and IoT devices, and that uses the same public keys as modern Diffie–Hellman schemes based on Montgomery curves (such as Curve25519) or Kummer surfaces. qDSA resembles an adaptation of EdDSA to the world of Kummer varieties, which are quotients of algebraic groups by ±1. Interestingly, qDSA does not require any full group operations or point recovery: all computations, including signature verification, occur on the quotient where there is no group law.

## Key claims (as reported)
- We include details on four implementations of qDSA, using Montgomery and fast Kummer surface arithmetic on the 8-bit AVR ATmega and 32-bit ARM Cortex M0 platforms.
- We find that qDSA significantly outperforms state-of-the-art signature implementations in terms of stack usage and code size.
- We also include an efficient compression algorithm for points on fast Kummer surfaces, reducing them to the same size as compressed elliptic curve points for the same security level.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240214 (1).pdf`
- `downloads/106240214.pdf`
