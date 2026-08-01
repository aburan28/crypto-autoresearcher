---
id: KN-LIT-317
type: literature
title: "Improved Algorithm for the Isogeny Problem for Ordinary Elliptic Curves"
authors:
  - "Steven Galbraith"
year: 2011
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1105.6331"
  url: "https://arxiv.org/abs/1105.6331"
tags: [class-group, complexity-theory, dlp, elliptic-curve, endomorphism, finite-field, isogeny, number-theory, prime-field, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A low storage algorithm for constructing isogenies between ordinary elliptic curves was proposed by Galbraith, Hess and Smart (GHS). We give an improvement of this algorithm by modifying the pseudorandom walk so that lower-degree isogenies are used more frequently.

## Key claims (as reported)
- This is motivated by the fact that high degree isogenies are slower to compute than low degree ones.
- We analyse the running time of the parallel collision search algorithm when the partitioning is uneven.
- We also give experimental results.
- We conclude that our algorithm is around 14 times faster than the GHS algorithm when constructing horizontal isogenies between random isogenous elliptic curves over a 160-bit prime field.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1105.6331v1 (1).pdf`
- `downloads/1105.6331v1.pdf`
