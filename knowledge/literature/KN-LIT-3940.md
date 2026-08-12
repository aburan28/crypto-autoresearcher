---
id: KN-LIT-3940
type: literature
title: "FourQ on embedded devices with strong countermeasures against side-channel attacks"
authors:
  - "Oscar Reparaz"
  - "Hwajeong Seo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, implementation, protocol, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work deals with the energy-efficient, high-speed and high-security implementation of elliptic curve scalar multiplication and elliptic curve Diffie-Hellman (ECDH) key exchange on embedded devices using FourQ and incorporating strong countermeasures to thwart a wide variety of side-channel attacks. First, we set new speed records for constant-time curve-based scalar multiplication and DH key exchange at the 128-bit security level with implementations targeting 8, 16 and 32-bit microcontrollers.

## Key claims (as reported)
- For example, our software computes a static ECDH shared secret in ∼6.9 million cycles (or 0.86 seconds @8MHz) on a low-power 8-bit AVR microcontroller which, compared to the fastest Curve25519 and genus-2 Kummer implementations on the same platform, offers 2x and 1.4x speedups, respectively.
- Similarly, it computes the same operation in ∼496 thousand cycles on a 32-bit ARM CortexM4 microcontroller, achieving a factor-2.9 speedup when compared to the fastest Curve25519 implementation targeting the same platform.
- Second, we engineer a set of side-channel countermeasures taking advantage of FourQ’s rich arithmetic and propose a secure implementation that offers protection against a wide range of sophisticated side-channel attacks.
- Finally, we perform a differential power analysis evaluation of our software running on an ARM Cortex-M4, and report that no leakage was detected with up to 10 million traces.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529146 (1).pdf`
- `downloads/10529146.pdf`
