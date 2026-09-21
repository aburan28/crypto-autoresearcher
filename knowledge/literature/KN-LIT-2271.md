---
id: KN-LIT-2271
type: literature
title: "A Unified Approach to MPC with Preprocessing using OT"
authors:
  - "Tore Kasper Frederiksen"
  - "Marcel Keller"
  - "Emmanuela Orsini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, mov-fr, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SPDZ, TinyOT and MiniMAC are a family of MPC protocols based on secret sharing with MACs, where a preprocessing stage produces multiplication triples in a finite field. This work describes new protocols for generating multiplication triples in fields of characteristic two using OT extensions.

## Key claims (as reported)
- Before this work, TinyOT, which works on binary circuits, was the only protocol in this family using OT extensions.
- Previous SPDZ protocols for triples in large finite fields require somewhat homomorphic encryption, which leads to very inefficient runtimes in practice, while no dedicated preprocessing protocol for MiniMAC (which operates on vectors of small field elements) was previously known.
- Since actively secure OT extensions can be performed very efficiently using only symmetric primitives, it is highly desirable to base MPC protocols on these rather than expensive public key primitives.
- We analyze the practical efficiency of our protocols, showing that they should all perform favorably compared with previous works; we estimate our protocol for SPDZ triples in F240 will perform around 2 orders of magnitude faster than the best known previous protocol.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520267 (1).pdf`
- `downloads/94520267.pdf`
