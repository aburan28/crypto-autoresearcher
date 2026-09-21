---
id: KN-LIT-7630
type: literature
title: "Constructing Isogenies Between Elliptic Curves Over Finite Fields"
authors:
  - "Steven D. Galbraith"
year: 1999
venue: "LMS Journal of Computation and Mathematics 2:118–138 (author PDF dated 2011 reprint)"
identifiers:
  eprint: null
  doi: "10.1112/S1461157000000097"
  arxiv: null
  url: "https://www.math.auckland.ac.nz/~sgal018/iso.pdf"
tags: [isogeny, ordinary-curves, endomorphism-ring, conductor, ecdlp, galbraith, prime-field]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Contribution

Gives a probabilistic algorithm to construct an $\mathbb{F}_p$-isogeny between two
ordinary elliptic curves with the same number of points (algorithmic Tate
isogeny theorem). Worst-case complexity is exponential; the hard case is when
the endomorphism-ring conductor gap is large.

## Key claims (from fetched author PDF abstract/intro)

- Same $\#E(\mathbb{F}_p)$ $\Rightarrow$ an $\mathbb{F}_p$-isogeny exists (Tate); the paper constructs one.
- Uses Kohel-style endomorphism-ring computation and walks in the ordinary
  isogeny graph / volcano.
- Discusses significance for ECDLP equivalence across an isogeny class; the
  conductor gap is the principal obstruction to efficient transfer.

## Relevance to GOAL-ECTD-001

Central reference for translating ECDLP between ordinary prime-field curves.
The large-prime conductor-gap case is the briefing's prioritized vertical
trapdoor boundary.

## Local copies

- `inputs/ECTD-TESKE-20260731/sources/galbraith-iso.pdf`
  (sha256 `77362b01d48d9391cb648d7960f2d7935982b8f81dab96a5fd15bb8a0b49bcb8`, 21 pages)
