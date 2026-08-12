---
id: KN-LIT-3851
type: literature
title: "Faster Sounder Succinct Arguments and IOPs"
authors:
  - "Justin Holmgren"
  - "Ron D. Rothblum"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, glv-gls, hash, pairing, quantum, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Succinct arguments allow a prover to convince a verifier that a given statement is true, using an extremely short proof. A major bottleneck that has been the focus of a large body of work is in reducing the overhead incurred by the prover in order to prove correctness of the computation.

## Key claims (as reported)
- By overhead we refer to the cost of proving correctness, divided by the cost of the original computation.
- In this work, for a large class of Boolean circuits C = C(x, w), we construct succinct arguments for the language {x : ∃w C(x, w) = 1}, with 2−λ soundness error, and with prover overhead polylog(λ).
- This result relies on the existence of (sub-exponentially secure) linear-size computable collision-resistant hash functions.
- The class of Boolean circuits that we can handle includes circuits with a repeated sub-structure, which arise in natural applications such as batch computation/verification, hashing and related block chain applications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070413 (1).pdf`
- `downloads/135070413.pdf`
