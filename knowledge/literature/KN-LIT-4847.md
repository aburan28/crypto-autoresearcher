---
id: KN-LIT-4847
type: literature
title: "Malleable Proof Systems and Applications"
authors:
  - "Melissa Chase"
  - "Markulf Kohlweiss"
  - "Anna Lysyanskaya"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Malleability for cryptography is not necessarily an opportunity for attack; in many cases it is a potentially useful feature that can be exploited. In this work, we examine notions of malleability for non-interactive zero-knowledge (NIZK) proofs.

## Key claims (as reported)
- We start by defining a malleable proof system, and then consider ways to meaningfully control the malleability of the proof system, as in many settings we would like to guarantee that only certain types of transformations can be performed.
- As our motivating application, we consider a shorter proof for verifiable shuffles.
- Our controlled-malleable proofs allow us for the first time to use one compact proof to prove the correctness of an entire multi-step shuffle.
- Each authority takes as input a set of encrypted votes and a controlledmalleable NIZK proof that these are a shuffle of the original encrypted votes submitted by the voters; it then permutes and re-randomizes these votes and updates the proof by exploiting its controlled malleability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370275 (1).pdf`
- `downloads/72370275 (2).pdf`
- `downloads/72370275 (3).pdf`
- `downloads/72370275.pdf`
