---
id: KN-LIT-3847
type: literature
title: "Faster Pairing Computations on Curves with High-Degree Twists"
authors:
  - "Craig Costello"
  - "Tanja Lange"
  - "Michael Naehrig"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, hyperelliptic, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Research on efficient pairing implementation has focussed on reducing the loop length and on using high-degree twists. Existence of twists of degree larger than 2 is a very restrictive criterion but luckily constructions for pairing-friendly elliptic curves with such twists exist.

## Key claims (as reported)
- In fact, Freeman, Scott and Teske showed in their overview paper that often the best known methods of constructing pairing-friendly elliptic curves over fields of large prime characteristic produce curves that admit twists of degree 3, 4 or 6.
- A few papers have presented explicit formulas for the doubling and the addition step in Miller’s algorithm, but the optimizations were all done for the Tate pairing with degree-2 twists, so the main usage of the highdegree twists remained incompatible with more efficient formulas.
- In this paper we present efficient formulas for curves with twists of degree 2, 3, 4 or 6.
- These formulas are significantly faster than their predecessors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/60560227 (1).pdf`
- `downloads/60560227 (2).pdf`
- `downloads/60560227 (3).pdf`
- `downloads/60560227 (4).pdf`
- `downloads/60560227.pdf`
