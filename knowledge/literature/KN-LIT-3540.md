---
id: KN-LIT-3540
type: literature
title: "Efficient Collision-Resistant Hashing from Worst-Case Assumptions on Cyclic Lattices"
authors:
  - "Chris Peikert"
  - "Alon Rosen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, hash, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The generalized knapsack function is defined as fa (x) = P i ai · xi , where a = (a1 , . . . , am ) consists of m elements from some ring R, and x = (x1 , . . . , xm ) consists of m coefficients from a specified subset S ⊆ R. Micciancio (FOCS 2002) proposed a specific choice of the ring R and subset S for which inverting this function (for random a, x) is at least as hard as solving certain worst-case problems on cyclic lattices.

## Key claims (as reported)
- We show that for a different choice of S ⊂ R, the generalized knapsack function is in fact collision-resistant, assuming it is infeasible to approximate the shortest vector in n-dimensional cyclic lattices up to factors Õ(n).
- For slightly larger factors, we even get collision-resistance for any m ≥ 2.
- This yields very efficient collision-resistant hash functions having key size and time complexity almost linear in the security parameter n.
- We also show that altering S is necessary, in the sense that Micciancio’s original function is not collision-resistant (nor even universal one-way).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/38760145 (1).pdf`
- `downloads/38760145 (2).pdf`
- `downloads/38760145 (3).pdf`
- `downloads/38760145.pdf`
