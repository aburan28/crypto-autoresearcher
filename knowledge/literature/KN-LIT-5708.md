---
id: KN-LIT-5708
type: literature
title: "Packing Messages and Optimizing Bootstrapping in GSW-FHE"
authors:
  - "Ryo Hiromasa"
  - "Masayuki Abe"
  - "Tatsuaki Okamoto"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, number-theory, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first fully homomorphic encryption (FHE) scheme that encrypts matrices and supports homomorphic matrix addition and multiplication. This is a natural extension of packed FHE and thus supports more complicated homomorphic operations.

## Key claims (as reported)
- We optimize the bootstrapping procedure of Alperin-Sheriff and Peikert (CRYPTO 2014) by applying our scheme.
- Our optimization decreases the lattice approximation factor from Õ(n3 ) to Õ(n2.5 ).
- By taking a lattice dimension as a larger polynomial in a security parameter, we can also obtain the same approximation factor as the best known one of standard latticebased public-key encryption without successive dimension-modulus reduction, which was essential for achieving the best factor in prior works on bootstrapping of standard lattice-based FHE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200146 (1).pdf`
- `downloads/90200146 (2).pdf`
- `downloads/90200146 (3).pdf`
- `downloads/90200146 (4).pdf`
- `downloads/90200146.pdf`
