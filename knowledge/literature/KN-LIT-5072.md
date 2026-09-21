---
id: KN-LIT-5072
type: literature
title: "Network-Agnostic Security Comes (Almost) for Free in DKG and MPC"
authors:
  - "Renas Bacho"
  - "Daniel Collins"
  - "Chen-Da Liu-Zhang"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Distributed key generation (DKG) protocols are an essential building block for threshold cryptosystems. Many DKG protocols tolerate up to ts < n/2 corruptions assuming a well-behaved synchronous network, but become insecure as soon as the network delay becomes unstable.

## Key claims (as reported)
- On the other hand, solutions in the asynchronous model operate under arbitrary network conditions, but only tolerate ta < n/3 corruptions, even when the network is well-behaved.
- In this work, we ask whether one can design a protocol that achieves security guarantees in either scenario.
- We show a complete characterization of network-agnostic DKG protocols, showing that the tight bound is ta +2ts < n.
- As a second contribution, we provide an optimized version of the network-agnostic multi-party computation (MPC) protocol by Blum, Liu-Zhang and Loss [CRYPTO’20] which improves over the communication complexity of their protocol by a linear factor.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850365 (1).pdf`
- `downloads/140850365.pdf`
