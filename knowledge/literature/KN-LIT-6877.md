---
id: KN-LIT-6877
type: literature
title: "Succinct Arguments for RAM Programs via Projection Codes"
authors:
  - "Yuval Ishai"
  - "Rafail Ostrovsky"
  - "Akash Shah"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Motivated by the goal of proving statements that involve small subsets of a big database, we introduce and study the notion of projection codes. A standard error-correcting code allows one to encode a message x into a codeword X, such that even if a constant fraction of X is corrupted, the message x can still be recovered.

## Key claims (as reported)
- A projection code extends this guarantee to any subset of the bits of x.
- Concretely, for every projection of x to a subset s of its coordinates, there is a subset S of comparable size such that the projected encoding X|S forms a robust encoding of the projected message x|s .
- Our first main result is a construction of projection codes with a nearoptimal increase in the length of x and size of s.
- We then apply this to obtain our second main result: succinct arguments for the computation of a RAM program on a (big) committed database, where the communication and the run-time of both the prover and the verifier are close to optimal even when the RAM program run-time is much smaller than the database size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850372 (1).pdf`
- `downloads/140850372.pdf`
