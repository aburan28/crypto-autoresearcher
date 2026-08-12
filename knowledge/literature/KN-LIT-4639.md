---
id: KN-LIT-4639
type: literature
title: "Lattice sieving via quantum random walks"
authors:
  - "André Chailloux"
  - "Johanna Loyer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based cryptography is one of the leading proposals for post-quantum cryptography. The Shortest Vector Problem (SVP) is arguably the most important problem for the cryptanalysis of latticebased cryptography, and many lattice-based schemes have security claims based on its hardness.

## Key claims (as reported)
- The best quantum algorithm for the SVP is due to Laarhoven [Laa16] and runs in (heuristic) time 20.2653d+o(d) .
- In this article, we present an improvement over Laarhoven’s result and present an algorithm that has a (heuristic) running time of 20.2570d+o(d) where d is the lattice dimension.
- We also present time-memory trade-offs where we quantify the amount of quantum memory and quantum random access memory of our algorithm.
- The core idea is to replace Grover’s algorithm used in [Laa16] in a key part of the sieving algorithm by a quantum random walk in which we add a layer of local sensitive filtering.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900142 (1).pdf`
- `downloads/130900142.pdf`
