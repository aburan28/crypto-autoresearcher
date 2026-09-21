---
id: KN-LIT-4645
type: literature
title: "Lattice-Based Blind Signatures, Revisited"
authors:
  - "Eduard Hauck"
  - "Eike Kiltz"
  - "Julian Loss"
  - "Ngoc Khanh Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, lattice, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We observe that all previously known lattice-based blind signature schemes contain subtle flaws in their security proofs (e.g., Rückert, ASIACRYPT ’08) or can be attacked (e.g., BLAZE by Alkadri et al., FC ’20). Motivated by this, we revisit the problem of constructing blind signatures from standard lattice assumptions.

## Key claims (as reported)
- We propose a new three-round lattice-based blind signature scheme whose security can be proved, in the random oracle model, from the standard SIS assumption.
- Our starting point is a modified version of the (insecure) BLAZE scheme, which itself is based Lyubashevsky’s threeround identification scheme combined with a new aborting technique to reduce the correctness error.
- Our proof builds upon and extends the recent modular framework for blind signatures of Hauck, Kiltz, and Loss (EUROCRYPT ’19).
- It also introduces several new techniques to overcome the additional challenges posed by the correctness error which is inherent to all lattice-based constructions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171251 (1).pdf`
- `downloads/12171251.pdf`
