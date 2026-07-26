---
id: KN-LIT-2166
type: literature
title: "A non-PCP Approach to Succinct Quantum-Safe Zero-Knowledge ?"
authors:
  - "Jonathan Bootle"
  - "Vadim Lyubashevsky"
  - "Ngoc Khanh Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, lattice, pairing, pqc, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Today’s most compact zero-knowledge arguments are based on the hardness of the discrete logarithm problem and related classical assumptions. If one is interested in quantum-safe solutions, then all of the known techniques stem from the PCP-based framework of Kilian (STOC 92) which can be instantiated based on the hardness of any collisionresistant hash function.

## Key claims (as reported)
- Both approaches produce asymptotically logarithmic sized arguments but, by exploiting extra algebraic structure, the discrete logarithm arguments are a few orders of magnitude more compact in practice than the generic constructions.
- In this work, we present the first (poly)-logarithmic, potentially postquantum zero-knowledge arguments that deviate from the PCP approach.
- At the core of succinct zero-knowledge proofs are succinct commitment schemes (in which the commitment and the opening proof are sub-linear in the message size), and we propose two such constructions based on the hardness of the (Ring)-Short Integer Solution (Ring-SIS) problem, each having certain trade-offs.
- For commitments to N secret values, the communication complexity of our first scheme is Õ(N 1/c ) for any positive integer c, and O(log2 N ) for the second.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171046 (1).pdf`
- `downloads/12171046.pdf`
