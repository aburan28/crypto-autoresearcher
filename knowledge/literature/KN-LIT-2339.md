---
id: KN-LIT-2339
type: literature
title: "Adaptive versus Static Multi-oracle Algorithms, and Quantum Security of a Split-key PRF"
authors:
  - "Jelle Don"
  - "Serge Fehr"
  - "Yu-Hsuan Huang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the first part of the paper, we show a generic compiler that transforms any oracle algorithm that can query multiple oracles adaptively, i.e., can decide on which oracle to query at what point dependent on previous oracle responses, into a static algorithm that fixes these choices at the beginning of the execution. Compared to naive ways of achieving this, our compiler controls the blow-up in query complexity for each oracle individually, and causes a very mild blow-up only.

## Key claims (as reported)
- In the second part of the paper, we use our compiler to show the security of the very efficient hash-based split-key PRF proposed by Giacon, Heuer and Poettering (PKC 2018), in the quantum random-oracle model.
- Using a split-key PRF as the key-derivation function gives rise to a secure KEM combiner.
- Thus, our result shows that the hash-based construction of Giacon et al. can be safely used in the context of quantum attacks, for instance to combine a well-established but only classically-secure KEM with a candidate KEM that is believed to be quantum-secure.
- Our security proof for the split-key PRF crucially relies on our adaptiveto-static compiler, but we expect our compiler to be useful beyond this particular application.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470113 (1).pdf`
- `downloads/137470113.pdf`
