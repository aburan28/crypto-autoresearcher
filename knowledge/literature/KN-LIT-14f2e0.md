---
id: KN-LIT-14f2e0
type: literature
title: "Probably correct row echelon form in the F4 algorithm"
authors:
  - "Alexander Demin"
year: 2026
venue: "arXiv:2609.14433"
identifiers:
  eprint: null
  arxiv: "2609.14433"
  doi: null
  url: null
tags: [index-calculus, f4, groebner, probabilistic, implementation, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Gives the first probability bound for the Monagan-Pearce-Steel probabilistic row-echelon step used by state-of-the-art F4 implementations. Builds a Las Vegas F4 that can beat deterministic F4 on classical examples. Relevant as a correctness and engineering upgrade for bulk decomposition solving. GPU Groebner work found: Hojnacki et al., "Parallel computation of Groebner bases on a GPU", Springer TCSCI 2021, pp. 417-432, doi:10.1007/978-3-030-69984-0_31 (metadata only); Gokavarapu, arXiv:2601.06765 (2026), a design study for GPU symbolic preprocessing in F4/F5 without verified benchmarks. We found no published GPU F4/XL implementation applied to ECDLP decomposition systems.

## Key claims (as reported)

- Bound plus Las Vegas F4 (numbers in paper).

## Relevance to this program

First probability bound for probabilistic row echelon in F4 and a Las Vegas F4 (2026). The in-house Boolean F4 (cryptanalysis experiments/f4-gpu-20260925) and GPU F4 should cite this and the related GPU Gröbner work it lists.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
