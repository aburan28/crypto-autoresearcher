---
id: KN-LIT-6424
type: literature
title: "Secure Computation From Millionaire"
authors: []
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The standard method for designing a secure computation protocol for function f first transforms f into either a circuit or a RAM program and then applies a generic secure computation protocol that either handles boolean gates or translates the RAM program into oblivious RAM instructions. In this paper, we show a large class of functions for which a different iterative approach to secure computation results in more efficient protocols.

## Key claims (as reported)
- The first such examples of this technique was presented by Aggarwal, Mishra, and Pinkas (J. of Cryptology, 2010) for computing the median; later, Brickell and Shmatikov (Asiacrypt 2005) showed a similar technique for shortest path problems.
- We generalize the technique in both of those works and show that it applies to a large class of problems including certain matroid optimizations, sub-modular optimization, convex hulls, and other scheduling problems.
- The crux of our technique is to securely reduce these problems to secure comparison operations and to employ the idea of gradually releasing part of the output.
- We then identify conditions under which both of these techniques for protocol design are compatible with achieving simulationbased security in the honest-but-curious and covert adversary models.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520304 (1).pdf`
- `downloads/94520304.pdf`
