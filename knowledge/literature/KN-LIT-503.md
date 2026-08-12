---
id: KN-LIT-503
type: literature
title: "FAST COMPUTATION OF ISOMORPHISMS BETWEEN FINITE FIELDS USING ELLIPTIC CURVES"
authors:
  - "ANAND KUMAR NARAYANAN"
year: 2016
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1604.03072"
  url: "https://arxiv.org/abs/1604.03072"
tags: [complexity-theory, cryptanalysis, dlp, elliptic-curve, endomorphism, factoring, finite-field, isogeny, mov-fr, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a randomized algorithm to compute isomorphisms between finite fields using elliptic curves. To compute an isomorphism between two fields of cardinality q n , our algorithm takes   n1+o(1) log1+o(1) q + max lnl +1+o(1) log2+o(1) q + O(l log 5 q) l time, where l runs through primes dividing n but not q(q − 1) and nl denotes the highest power of l dividing n.

## Key claims (as reported)
- Prior to this work, the best known run time dependence on n was quadratic.
- Our run time dependence on n is at worst quadratic but is subquadratic if n has no large prime factor.
- In particular, the n for which our run time is nearly linear in n have natural density at least 3/10.
- The crux of our approach is finding a point on an elliptic curve of a prescribed prime power order or equivalently finding preimages under the Lang map on elliptic curves over finite fields.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1604.03072v3.pdf`
