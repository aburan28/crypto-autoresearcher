---
id: KN-LIT-5154
type: literature
title: "New Techniques for Obfuscating Conjunctions"
authors:
  - "James Bartusek"
  - "Tancrède Lepoint"
  - "Fermi Ma"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A conjunction is a function f (x1 , . . . , xn ) = i∈S li where S ⊆ [n] and each li is xi or ¬xi . (CRYPTO 2018) recently proposed obfuscating conjunctions by embedding them in the error positions of a noisy Reed-Solomon codeword and placing the codeword in a group exponent.

## Key claims (as reported)
- They prove distributional virtual black box (VBB) security in the generic group model for random conjunctions where |S| ≥ 0.226n.
- While conjunction obfuscation is known from LWE [47, 31], these constructions rely on substantial technical machinery.
- In this work, we conduct an extensive study of simple conjunction obfuscation techniques. – We abstract the Bishop et al. scheme to obtain an equivalent yet more efficient “dual” scheme that handles conjunctions over exponential size alphabets.
- We give a significantly simpler proof of generic group security, which we combine with a novel combinatorial argument to obtain distributional VBB security for |S| of any size. – If we replace the Reed-Solomon code with a random binary linear code, we can prove security from standard LPN and avoid encoding in a group.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760313 (1).pdf`
- `downloads/114760313.pdf`
