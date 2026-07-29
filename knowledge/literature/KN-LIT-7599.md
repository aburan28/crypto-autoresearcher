---
id: KN-LIT-7599
type: literature
title: "Engineered Complete Intersections: Algorithmic Aspects"
authors:
  - "Alexander Esterov"
  - "Rafael Mohr"
  - "Yulia Mukhina"
year: 2026
venue: 'arXiv preprint arXiv:2607.23622 [cs.SC, math.AG]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.23622'
  url: https://arxiv.org/abs/2607.23622
tags: [sparse-polynomial-systems, tropical-geometry, mixed-subdivision, bkk, newton-polytope, elimination, eliminant, a-discriminant, homotopy-continuation, solution-counting, software, groebner-alternative]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
Algorithmic machinery for **Engineered Complete Intersections** (ECIs), a class of sparse
polynomial systems: a tropicalization technique generalizing Huber–Sturmfels mixed
subdivisions, a tropical homotopy-continuation algorithm to compute them, and an algorithm
for **Newton polytopes of eliminants**. Implemented as a software package.

## Key claims (as reported)
- A new effective technique to tropicalize ECIs, generalizing the classical mixed
  subdivisions of Huber–Sturmfels (1995), aimed at **efficiently counting solutions of
  square systems in ECI form**.
- A tropical homotopy-continuation algorithm for computing such mixed subdivisions,
  building on Jensen (2016), Malajovich (2017), and Daisey–Ren (2024); usable to solve
  such systems numerically when coupled with Helminck–Henriksson–Ren (2024).
- An algorithm computing **Newton polytopes of eliminants** of ECIs — giving, for example,
  a new route to Newton polytopes of `A`-discriminants. With evaluation–interpolation, an
  efficient approach to computing such eliminants.
- Implemented; practical feasibility demonstrated on a range of examples.

## Relevance to this program
This is a live gap in the corpus. The program costs polynomial-system solving almost
exclusively in the **Gröbner idiom** (`KN-TECH-004`, `KN-TECH-011`, `KN-OPEN-002`), where
the cost model is degree-of-regularity-driven and the systems in question — summation
polynomials and index-calculus relation systems — are notoriously **sparse and highly
structured**. `KN-OPEN-004` already records BKK/mixed-volume elimination as an
under-explored alternative accounting for exactly these systems. This paper is squarely in
that lane: tropical/polytope methods that count and eliminate by Newton-polytope structure
rather than by degree, plus working code.

The honest position is that **no summation-polynomial system is known to be an Engineered
Complete Intersection**, and this paper makes no cryptographic claim. What it offers is
better tooling for the alternative cost model `KN-OPEN-004` asks for. The cheap next step,
should anyone take it, is the discriminating one: check whether a small Semaev summation
system over `F_{2^n}` satisfies the ECI conditions at all. A negative answer closes a lane
cheaply; a positive answer would make the eliminant machinery directly applicable to the
step where index calculus actually spends its time. Neither has been attempted.

Complements [[KN-LIT-7572]] (border bases), ingested in the 2026-07-26 gather for the same
corpus gap from the other direction — non-Gröbner accounts of polynomial-system solving.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-28 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-26, primary category cs.SC, cross-listed math.AG. Preprint — not peer-reviewed,
no DOI or venue as of this entry.

NOT verified here: the definition and scope of Engineered Complete Intersections; the
tropicalization technique and its generalization of mixed subdivisions; the homotopy and
eliminant algorithms and their complexity; the software and its reported performance. **In
particular, whether summation-polynomial or index-calculus relation systems fall in the
ECI class has not been checked and is not claimed by anyone.**
