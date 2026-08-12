---
id: KN-LIT-5313
type: literature
title: "On Bounded Distance Decoding with Predicate: Breaking the “Lattice Barrier” for the Hidden Number Problem"
authors:
  - "Martin R. Albrecht"
  - "Nadia Heninger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdsa, lattice, pairing, provable-security, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based algorithms in cryptanalysis often search for a target vector satisfying integer linear constraints as a shortest or closest vector in some lattice. In this work, we observe that these formulations may discard non-linear information from the underlying application that can be used to distinguish the target vector even when it is far from being uniquely close or short.

## Key claims (as reported)
- We formalize lattice problems augmented with a predicate distinguishing a target vector and give algorithms for solving instances of these problems.
- We apply our techniques to lattice-based approaches for solving the Hidden Number Problem, a popular technique for recovering secret DSA or ECDSA keys in side-channel attacks, and demonstrate that our algorithms succeed in recovering the signing key for instances that were previously believed to be unsolvable using lattice approaches.
- We carried out extensive experiments using our estimation and solving framework, which we also make available with this work.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960172 (1).pdf`
- `downloads/126960172.pdf`
