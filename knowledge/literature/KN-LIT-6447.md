---
id: KN-LIT-6447
type: literature
title: "Secure Multi-party Quantum Computation with a Dishonest Majority"
authors:
  - "Yfke Dulek"
  - "Alex B. Grilo"
  - "Stacey Jeffery"
  - "Christian Majenz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The cryptographic task of secure multi-party (classical) computation has received a lot of attention in the last decades. Even in the extreme case where a computation is performed between k mutually distrustful players, and security is required even for the single honest player if all other players are colluding adversaries, secure protocols are known.

## Key claims (as reported)
- For quantum computation, on the other hand, protocols allowing arbitrary dishonest majority have only been proven for k = 2.
- In this work, we generalize the approach taken by Dupuis, Nielsen and Salvail (CRYPTO 2012) in the two-party setting to devise a secure, efficient protocol for multi-party quantum computation for any number of players k, and prove security against up to k − 1 colluding adversaries.
- The quantum round complexity of the protocol for computing a quantum circuit of {CNOT, T} depth d is O(k · (d + log n)), where n is the security parameter.
- To achieve efficiency, we develop a novel public verification protocol for the Clifford authentication code, and a testing protocol for magic-state inputs, both using classical multi-party computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105255 (1).pdf`
- `downloads/12105255.pdf`
