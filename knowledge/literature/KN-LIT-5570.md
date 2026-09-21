---
id: KN-LIT-5570
type: literature
title: "On the Security of Hash Functions Employing Blockcipher Postprocessing"
authors:
  - "Donghoon Chang"
  - "Mridul Nandi"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Analyzing desired generic properties of hash functions is an important current area in cryptography. For example, in Eurocrypt 2009, Dodis, Ristenpart and Shrimpton [8] introduced the elegant notion of “Preimage Awareness” (PrA) of a hash function H P , and they showed that a PrA hash function followed by an output transformation modeled to be a FIL (fixed input length) random oracle is PRO (pseudorandom oracle) i.e. indifferentiable from a VIL (variable input length) random oracle.

## Key claims (as reported)
- We observe that for recent practices in designing hash function (e.g.
- SHA-3 candidates) most output transformations are based on permutation(s) or blockcipher(s), which are not PRO.
- Thus, a natural question is how the notion of PrA can be employed directly with these types of more prevalent output transformations?
- We consider the Davies-Meyer’s type output transformation OT (x) := E(x) ⊕ x where E is an ideal permutation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330151 (1).pdf`
- `downloads/67330151 (2).pdf`
- `downloads/67330151 (3).pdf`
- `downloads/67330151.pdf`
