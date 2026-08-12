---
id: KN-LIT-1000
type: literature
title: "Local Inversion of maps: Black box Cryptanalysis"
authors:
  - "Virendra Sule"
year: 2022
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2207.03247"
  url: "https://arxiv.org/abs/2207.03247"
tags: [cryptanalysis, dlp, elliptic-curve, finite-field, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper is a short summery of results announced in a previous paper on a new universal method for Cryptanalysis which uses a Black Box linear algebra approach to computation of local inversion of nonlinear maps in finite fields. It is shown that one local inverse x of the map equation y = F (x) can be computed by using the minimal polynomial of the sequence y(k) defined by iterates (or recursion) y(k + 1) = F (y(k)) with y(0) = y when the sequence is periodic.

## Key claims (as reported)
- This is the only solution in the periodic orbit of the map F .
- Further, when the degree of the minimal polynomial is of polynomial order in number of bits of the input of F (called low complexity case), the solution can be computed in polynomial time.
- The method of computation only uses the forward computations F (y) for given y which is why this is called a Black Box approach.
- Application of this approach is then shown for cryptanalysis of several maps arising in cryptographic primitives.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2207.03247v2 (1).pdf`
- `downloads/2207.03247v2.pdf`
