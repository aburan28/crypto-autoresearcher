---
id: KN-LIT-5666
type: literature
title: "Optimal Verification of Operations on Dynamic Sets"
authors:
  - "Charalampos Papamanthou"
  - "Roberto Tamassia"
  - "Nikos Triandopoulos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the design of protocols for set-operation verification, namely the problem of cryptographically checking the correctness of outsourced set operations performed by an untrusted server over a dynamic collection of sets that are owned (and updated) by a trusted source. We present new authenticated data structures that allow any entity to publicly verify a proof attesting the correctness of primitive set operations such as intersection, union, subset and set difference.

## Key claims (as reported)
- Based on a novel extension of the security properties of bilinear-map accumulators as well as on a primitive called accumulation tree, our protocols achieve optimal verification and proof complexity (i.e., only proportional to the size of the query parameters and the answer), as well as optimal update complexity (i.e., constant), while incurring no extra asymptotic space overhead.
- The proof construction is also efficient, adding a logarithmic overhead to the computation of the answer of a set-operation query.
- In contrast, existing schemes entail high communication and verification costs or high storage costs.
- Applications of interest include efficient verification of keyword search and database queries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410091 (1).pdf`
- `downloads/68410091 (2).pdf`
- `downloads/68410091 (3).pdf`
- `downloads/68410091.pdf`
