---
id: KN-LIT-1540
type: literature
title: "ALGEBRAIC MODELINGS OF THE SUPERSINGULAR ISOGENY PROBLEM"
authors:
  - "ALESSIO CAMINATA"
  - "ANDREA SANGUINETI"
  - "SILVIA SCONZA"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2607.05160"
  url: "https://arxiv.org/abs/2607.05160"
tags: [cryptanalysis, curve-arithmetic, elliptic-curve, groebner, isogeny, lattice, pqc, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new algebraic modeling of the Supersingular Isogeny Problem as a system of multivariate polynomial equations, in the case where the elliptic curves are connected by an isogeny whose degree is a power of 2 or 3. This modeling relies on Renes formulas for elliptic curves in Montgomery form (degree 2) or triangular form (degree 3).

## Key claims (as reported)
- We investigate several algebraic properties of these systems: we prove that they are zero-dimensional, compute the dimension of their highest degree part, and show that they are not in generic coordinates.
- Experimental results show that solving these systems via Gröbner basis techniques is significantly faster than solving the algebraic modeling with modular polynomials.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2607.05160v1.pdf`
