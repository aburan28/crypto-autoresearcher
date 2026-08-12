---
id: KN-LIT-302
type: literature
title: "A LOW-MEMORY ALGORITHM FOR FINDING SHORT PRODUCT REPRESENTATIONS IN FINITE GROUPS"
authors:
  - "GAETAN BISSON"
  - "ANDREW V. SUTHERLAND"
year: 2011
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1101.0564"
  url: "https://arxiv.org/abs/1101.0564"
tags: [class-group, complexity-theory, dlp, elliptic-curve, finite-field, isogeny, number-theory, pollard-rho, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a space-efficient algorithm for solving a generalization of the subset sum problem in a finite group G, using a Pollard-ρ approach. Given an element z and a sequence of elements S, our algorithm attempts to find a subsequence of S whose product in G is equal to z.

## Key claims (as reported)
- For a random sequence S of length d log2 n, where n = #G and d ⩾ 2 is a constant, we √ find that its expected running time is O( n log n) group operations (we give a rigorous proof for d > 4), and it only needs to store O(1) group elements.
- We consider applications to class groups of imaginary quadratic fields, and to finding isogenies between elliptic curves over a finite field.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1101.0564v1.pdf`
