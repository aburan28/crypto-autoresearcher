---
id: KN-LIT-4104
type: literature
title: "Generic Universal Forgery Attack on Iterative Hash-based MACs"
authors:
  - "Thomas Peyrin"
  - "Lei Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, pollard-rho, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we study the security of iterative hash-based MACs, such as HMAC or NMAC, with regards to universal forgery attacks. Leveraging recent advances in the analysis of functional graphs built from the iteration of HMAC or NMAC, we exhibit the very first generic universal forgery attack against hash-based MACs.

## Key claims (as reported)
- In particular, our work implies that the universal forgery resistance of an n-bit output HMAC construction is not 2n queries as long believed by the community.
- The techniques we introduce extend the previous functional graphs-based attacks that only took in account the cycle structure or the collision probability: we show that one can extract much more meaningful secret information by also analyzing the distance of a node from the cycle of its component in the functional graph.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410134 (1).pdf`
- `downloads/84410134 (2).pdf`
- `downloads/84410134 (3).pdf`
- `downloads/84410134.pdf`
