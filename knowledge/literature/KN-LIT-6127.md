---
id: KN-LIT-6127
type: literature
title: "Random Sampling for Short Lattice Vectors on Graphics Cards"
authors:
  - "Michael Schneider"
  - "Norman Göttert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, lattice, mov-fr, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a GPU implementation of the Simple Sampling Reduction (SSR) algorithm that searches for short vectors in lattices. SSR makes use of the famous BKZ algorithm.

## Key claims (as reported)
- It complements an exhaustive search in a suitable search region to insert random, short vectors to the lattice basis.
- The sampling of short vectors can be executed in parallel.
- Our GPU implementation increases the number of sampled vectors per second from 5200 to more than 120, 000.
- With this we are the first to present a parallel implementation of SSR and we make use of the computing capability of modern graphics cards to enhance the search for short vectors even more.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170160 (1).pdf`
- `downloads/69170160 (2).pdf`
- `downloads/69170160 (3).pdf`
- `downloads/69170160.pdf`
