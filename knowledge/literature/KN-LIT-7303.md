---
id: KN-LIT-7303
type: literature
title: "Two-Party ECDSA from Hash"
authors:
  - "Federico Savasta"
  - "Ida Tucker"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, ecdsa, elliptic-curve, fhe, hash, mov-fr, number-theory, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ECDSA is a widely adopted digital signature standard. Unfortunately, efficient distributed variants of this primitive are notoriously hard to achieve and known solutions often require expensive zero knowledge proofs to deal with malicious adversaries.

## Key claims (as reported)
- For the two party case, Lindell [Lin17] recently managed to get an efficient solution which, to achieve simulation-based security, relies on an interactive, non standard, assumption on Paillier’s cryptosystem.
- In this paper we generalize Lindell’s solution using hash proof systems.
- The main advantage of our generic method is that it results in a simulation-based security proof without resorting to non-standard interactive assumptions.
- Moving to concrete constructions, we show how to instantiate our framework using class groups of imaginary quadratic fields.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940176 (1).pdf`
- `downloads/116940176.pdf`
