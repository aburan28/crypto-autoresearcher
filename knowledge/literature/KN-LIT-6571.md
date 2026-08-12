---
id: KN-LIT-6571
type: literature
title: "Seven-Property-Preserving Iterated Hashing: ROX"
authors:
  - "Elena Andreeva"
  - "Gregory Neven"
  - "Bart Preneel"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Nearly all modern hash functions are constructed by iterating a compression function. At FSE’04, Rogaway and Shrimpton [28] formalized seven security notions for hash functions: collision resistance (Coll) and three variants of second-preimage resistance (Sec, aSec, eSec) and preimage resistance (Pre, aPre, ePre).

## Key claims (as reported)
- The main contribution of this paper is in determining, by proof or counterexample, which of these seven notions is preserved by each of eleven existing iterations.
- Our study points out that none of them preserves more than three notions from [28].
- As a second contribution, we propose the new Random-Oracle XOR (ROX) iteration that is the first to provably preserve all seven notions, but that, quite controversially, uses a random oracle in the iteration.
- The compression function itself is not modeled as a random oracle though.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330128 (1).pdf`
- `downloads/48330128 (2).pdf`
- `downloads/48330128 (3).pdf`
- `downloads/48330128.pdf`
