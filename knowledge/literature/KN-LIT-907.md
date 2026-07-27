---
id: KN-LIT-907
type: literature
title: "Online-Extractability in the Quantum Random-Oracle Model?"
authors:
  - "Jelle Don"
  - "Serge Fehr"
  - "Christian Majenz"
  - "Christian Schaffner"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/280"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/280"
tags: [hash, lattice, pairing, pqc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show the following generic result: When a quantum query algorithm in the quantum random-oracle model outputs a classical value t that is promised to be in some tight relation with H(x) for some x, then x can be efficiently extracted with almost certainty. The extraction is by means of a suitable simulation of the random oracle and works online, meaning that it is straightline, i.e., without rewinding, and on-the-fly, i.e., during the protocol execution and (almost) without disturbing it.

## Key claims (as reported)
- The technical core of our result is a new commutator bound that bounds the operator norm of the commutator of the unitary operator that describes the evolution of the compressed oracle (which is used to simulate the random oracle above) and of the measurement that extracts x.
- We show two applications of our generic online extractability result.
- We show tight online extractability of commit-and-open Σ-protocols in the quantum setting, and we offer the first complete post-quantum security proof of the textbook Fujisaki-Okamoto transformation, i.e, without adjustments to facilitate the proof, including concrete security bounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760015 (1).pdf`
- `downloads/132760015.pdf`
