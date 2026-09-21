---
id: KN-LIT-4661
type: literature
title: "Lattice-Based Timed Cryptography"
authors:
  - "Russell W. F. Lai"
  - "Giulio Malavolta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, hash, lattice, mpc, pairing, pqc, provable-security, quantum, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Timed cryptography studies primitives that retain their security only for a predetermined amount of time, such as proofs of sequential work and time-lock puzzles. This feature has proven to be useful in a large number of practical applications, e.g. randomness generation, sealed-bid auctions, and fair multi-party computation.

## Key claims (as reported)
- However, the current state of affairs in timed cryptography is unsatisfactory: Virtually all efficient constructions rely on a single sequentiality assumption, namely that repeated squaring in unknown order groups cannot be parallelised.
- This is a single point of failure in the classical setting and is even false against quantum adversaries.
- In this work we put forward a new sequentiality assumption, which essentially says that a repeated application of the standard lattice-based hash function cannot be parallelised.
- We provide concrete evidence of the validity of this assumption and, to substantiate its usefulness, we show how it enables a new proof of sequential work, with a stronger sequentiality guarantee than prior hash-based schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850218 (1).pdf`
- `downloads/140850218.pdf`
