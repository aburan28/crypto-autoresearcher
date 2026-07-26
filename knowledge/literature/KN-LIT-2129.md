---
id: KN-LIT-2129
type: literature
title: "A New Approach to Efficient Non-Malleable Zero-Knowledge?"
authors:
  - "Allen Kim"
  - "Xiao Liang"
  - "Omkant Pandey"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, survey, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-malleable zero-knowledge, originally introduced in the context of man-in-the-middle attacks, serves as an important building block to protect against concurrent attacks where different protocols may coexist and interleave. While this primitive admits almost optimal constructions in the plain model, they are several orders of magnitude slower in practice than standalone zero-knowledge.

## Key claims (as reported)
- This is in sharp contrast to non-malleable commitments where practical constructions (under the DDH assumption) have been known for a while.
- We present a new approach for constructing efficient non-malleable zeroknowledge for all languages in N P, based on a new primitive called instance-based non-malleable commitment (IB-NMC).
- We show how to construct practical IB-NMC by leveraging the fact that simulators of sub-linear zero-knowledge protocols can be much faster than the honest prover algorithm.
- With an efficient implementation of IB-NMC, our approach yields the first general-purpose non-malleable zero-knowledge protocol that achieves practical efficiency in the plain model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070291 (1).pdf`
- `downloads/135070291.pdf`
