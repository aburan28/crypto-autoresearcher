---
id: KN-LIT-2625
type: literature
title: "Aurora: Transparent Succinct Arguments for R1CS"
authors:
  - "Eli Ben-Sasson"
  - "Alessandro Chiesa"
  - "Michael Riabzev"
  - "Nicholas Spooner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pqc, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We design, implement, and evaluate a zero knowledge succinct noninteractive argument (SNARG) for Rank-1 Constraint Satisfaction (R1CS), a widely-deployed NP language undergoing standardization. Our SNARG has a transparent setup, is plausibly post-quantum secure, and uses lightweight cryptography.

## Key claims (as reported)
- A proof attesting to the satisfiability of n constraints has size O(log2 n); it can be produced with O(n log n) field operations and verified with O(n).
- At 128 bits of security, proofs are less than 250 kB even for several million constraints, more than 10× shorter than prior SNARGs with similar features.
- A key ingredient of our construction is a new Interactive Oracle Proof (IOP) for solving a univariate analogue of the classical sumcheck problem [LFKN92], originally studied for multivariate polynomials.
- Our protocol verifies the sum of entries of a Reed–Solomon codeword over any subgroup of a field.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760150 (1).pdf`
- `downloads/114760150.pdf`
