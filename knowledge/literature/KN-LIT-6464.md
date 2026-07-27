---
id: KN-LIT-6464
type: literature
title: "Secure Sampling with Sublinear Communication Seung Geol Choi1 , Dana Dachman-Soled2"
authors:
  - "S. Dov Gordon"
  - "Linsheng Liu"
  - "Arkady Yerukhimovich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Random sampling from specified distributions is an important tool with wide applications for analysis of large-scale data. In this paper we study how to randomly sample when the distribution is partitioned among two parties’ private inputs.

## Key claims (as reported)
- Of course, a trivial solution is to have one party send a (possibly encrypted) description of its weights to the other party who can then sample over the entire distribution (possibly using homomorphic encryption).
- However, this approach requires communication that is linear in the input size which is prohibitively expensive in many settings.
- In this paper, we investigate secure 2-party sampling with sublinear communication for many standard distributions.
- We develop protocols for L1 , and L2 sampling.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470115 (1).pdf`
- `downloads/137470115.pdf`
