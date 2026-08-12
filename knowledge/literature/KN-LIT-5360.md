---
id: KN-LIT-5360
type: literature
title: "On Invertible Sampling and Adaptive Security Yuval Ishai1,? , Abishek Kumarasubramanian2"
authors:
  - "Claudio Orlandi"
  - "Amit Sahai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure multiparty computation (MPC) is one of the most general and well studied problems in cryptography. We focus on MPC protocols that are required to be secure even when the adversary can adaptively corrupt parties during the protocol, and under the assumption that honest parties cannot reliably erase their secrets prior to corruption.

## Key claims (as reported)
- Previous feasibility results for adaptively secure MPC in this setting applied either to deterministic functionalities or to randomized functionalities which satisfy a certain technical requirement.
- The question whether adaptive security is possible for all functionalities was left open.
- We provide the first convincing evidence that the answer to this question is negative, namely that some (randomized) functionalities cannot be realized with adaptive security.
- We obtain this result by studying the following related invertible sampling problem: given an efficient sampling algorithm A, obtain another sampling algorithm B such that the output of B is computationally indistinguishable from the output of A, but B can be efficiently inverted (even if A cannot).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477470 (1).pdf`
- `downloads/6477470 (2).pdf`
- `downloads/6477470 (3).pdf`
- `downloads/6477470.pdf`
