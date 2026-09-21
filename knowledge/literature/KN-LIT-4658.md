---
id: KN-LIT-4658
type: literature
title: "Lattice-Based Succinct Arguments for NP with Polylogarithmic-Time Verification"
authors:
  - "Jonathan Bootle⋆"
  - "Alessandro Chiesa"
  - "Katerina Sotiraki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, pqc, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Succinct arguments that rely on the Merkle-tree paradigm introduced by Kilian (STOC 92) suffer from larger proof sizes in practice due to the use of generic cryptographic primitives. In contrast, succinct arguments with the smallest proof sizes in practice exploit homomorphic commitments.

## Key claims (as reported)
- However these latter are quantum insecure, unlike succinct arguments based on the Merkletree paradigm.
- A recent line of works seeks to address this limitation, by constructing quantumsafe succinct arguments that exploit lattice-based commitments.
- The eventual goal is smaller proof sizes than those achieved via the Merkle-tree paradigm.
- Alas, known constructions lack succinct verification.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850386 (1).pdf`
- `downloads/140850386.pdf`
