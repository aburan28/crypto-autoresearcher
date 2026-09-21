---
id: KN-LIT-5271
type: literature
title: "Oblivious Parallel RAM and Applications"
authors:
  - "Elette Boyle"
  - "Kai-Min Chung"
  - "Rafael Pass"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of cryptography for parallel RAM (PRAM) programs. The PRAM model captures modern multi-core architectures and cluster computing models, where several processors execute in parallel and make accesses to shared memory, and provides the “best of both” circuit and RAM models, supporting both cheap random access and parallelism.

## Key claims (as reported)
- We propose and attain the notion of Oblivious PRAM.
- We present a compiler taking any PRAM into one whose distribution of memory accesses is statistically independent of the data (with negligible error), while only incurring a polylogarithmic slowdown (in both total and parallel complexity).
- We discuss applications of such a compiler, building upon recent advances relying on Oblivious (sequential) RAM (Goldreich Ostrovsky JACM’12).
- In particular, we demonstrate the construction of a garbled PRAM compiler based on an OPRAM compiler and secure identity-based encryption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620777 (1).pdf`
- `downloads/95620777.pdf`
