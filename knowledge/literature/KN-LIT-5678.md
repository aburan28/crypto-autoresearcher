---
id: KN-LIT-5678
type: literature
title: "Optimizing Authenticated Garbling for Faster Secure Two-Party Computation"
authors:
  - "Jonathan Katz"
  - "Samuel Ranellucci"
  - "Mike Rosulek"
  - "Xiao Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
(CCS 2017) recently proposed a protocol for malicious secure two-party computation that represents the state-of-theart with regard to concrete efficiency in both the single-execution and amortized settings, with or without preprocessing. We show here several optimizations of their protocol that result in a significant improvement in the overall communication and running time.

## Key claims (as reported)
- Specifically: – We show how to make the “authenticated garbling” at the heart of their protocol compatible with the half-gate optimization of Zahur et al.
- We also show how to avoid sending an information-theoretic MAC for each garbled row.
- These two optimizations give up to a 2.6× improvement in communication, and make the communication of the online phase essentially equivalent to that of state-of-the-art semi-honest secure computation. – We show various optimizations to their protocol for generating AND triples that, overall, result in a 1.5× improvement in the communication and a 2× improvement in the computation for that step.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993319 (1).pdf`
- `downloads/10993319.pdf`
