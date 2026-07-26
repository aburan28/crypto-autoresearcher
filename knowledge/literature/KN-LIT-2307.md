---
id: KN-LIT-2307
type: literature
title: "Accumulators in (and Beyond) Generic Groups: Non-Trivial Batch Verification Requires Interaction"
authors:
  - "Gili Schul-Ganz"
  - "Gil Segev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, complexity-theory, hash, number-theory, pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We prove a tight lower bound on the number of group operations required for batch verification by any generic-group accumulator that stores a less-than-trivial amount of information. Specifically, we show that Ω(t · (λ/ log λ)) group operations are required for the batch verification of any subset of t ≥ 1 elements, where λ ∈ N is the security parameter, thus ruling out non-trivial batch verification in the standard non-interactive manner.

## Key claims (as reported)
- Our lower bound applies already to the most basic form of accumulators (i.e., static accumulators that support membership proofs), and holds both for known-order (and even multilinear) groups and for unknownorder groups, where it matches the asymptotic performance of the known bilinear and RSA accumulators, respectively.
- In addition, it complements the techniques underlying the generic-group accumulators of Boneh, Bünz and Fisch (CRYPTO ’19) and Thakur (ePrint ’19) by justifying their application of the Fiat-Shamir heuristic for transforming their interactive batch-verification protocols into non-interactive procedures.
- Moreover, motivated by a fundamental challenge introduced by Aggarwal and Maurer (EUROCRYPT ’09), we propose an extension of the genericgroup model that enables us to capture a bounded amount of arbitrary non-generic information (e.g., least-significant bits or Jacobi symbols that are hard to compute generically but are easy to compute non-generically).
- We prove our lower bound within this extended model, which may be of independent interest for strengthening the implications of impossibility results in idealized models.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550166 (1).pdf`
- `downloads/12550166.pdf`
