---
id: KN-LIT-3352
type: literature
title: "Cycle Slicer: An Algorithm for Building Permutations on Special Domains"
authors:
  - "Sarah Miracle"
  - "Scott Yilek"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce an algorithm called Cycle Slicer that gives new solutions to two important problems in format-preserving encryption: domain targeting and domain completion. In domain targeting, where we wish to use a cipher on domain X to construct a cipher on a smaller domain S ⊆ X , using Cycle Slicer leads to a significantly more efficient solution than Miracle and Yilek’s Reverse Cycle Walking (ASIACRYPT 2016) in the common setting where the size of S is large relative to the size of X .

## Key claims (as reported)
- In domain completion, a problem recently studied by Grubbs, Ristenpart, and Yarom (EUROCRYPT 2017) in which we wish to construct a cipher on domain X while staying consistent with existing mappings in a lazily-sampled table, Cycle Slicer provides an alternative construction with better worst-case running time than the Zig-Zag construction of Grubbs et al.
- Our analysis of Cycle Slicer uses a refinement of the Markov chain techniques for analyzing matching exchange processes, which were originally developed by Czumaj and Kutylowski (Rand.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240227 (1).pdf`
- `downloads/106240227.pdf`
