---
id: KN-LIT-5806
type: literature
title: "Post-quantum RSA"
authors:
  - "Daniel J. Bernstein"
  - "Nadia Heninger"
  - "Paul Lou"
  - "Luke Valenta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, pairing, pqc, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes RSA parameters for which (1) key generation, encryption, decryption, signing, and verification are feasible on today’s computers while (2) all known attacks are infeasible, even assuming highly scalable quantum computers. As part of the performance analysis, this paper introduces a new algorithm to generate a batch of primes.

## Key claims (as reported)
- As part of the attack analysis, this paper introduces a new quantum factorization algorithm that is often much faster than Shor’s algorithm and much faster than pre-quantum factorization algorithms.
- Initial pqRSA implementation results are provided.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/pqrsa-20170419.pdf`
