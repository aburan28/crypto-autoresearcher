---
id: KN-LIT-2433
type: literature
title: "Almost-everywhere Secure Computation"
authors:
  - "Juan A. Garay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure multi-party computation (MPC) is a central problem in cryptography. Unfortunately, it is well known that MPC is possible if and only  if the  underlying communication network has very large connectivity — in fact, , where is the number of potential corruptions in the network.

## Key claims (as reported)
- This impossibility result renders existing MPC results far less applicable in practice, since many deployed networks have in fact a very small degree.
- In this paper, we show how to circumvent this impossibility result and achieve meaningful security guarantees for graphs with small degree (such as expander graphs and several other topologies).
- In fact, the notion we introduce, which we call almost-everywhere MPC, building on the notion of almost-everywhere agreement due to Dwork, Peleg, Pippenger and Upfal, allows the degree of the network to be much smaller than the total number of allowed corruptions.
- In essence, our definition allows the adversary to implicitly wiretap some of the good nodes by corrupting sufficiently many nodes in the “neighborhood” of those nodes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650305 (1).pdf`
- `downloads/49650305 (2).pdf`
- `downloads/49650305 (3).pdf`
- `downloads/49650305.pdf`
