---
id: KN-LIT-031
type: literature
title: Grobner bases of ideals invariant under a commutative group - the non-modular case
authors: [Faugere Jean-Charles, Svartz Jules]
year: 2013
venue: ISSAC 2013, ACM, pp. 347-354
identifiers:
  eprint: null
  doi: 10.1145/2465506.2465944
  url: https://inria.hal.science/hal-00819337
tags: [groebner-basis, symmetry, invariant, character-grading, equivariant, block-decomposition, solving]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Algorithms to compute Grobner bases of ideals invariant under a finite
*commutative* matrix group in the non-modular case (group order invertible in
the base field). Simultaneously diagonalizing the group and applying the
corresponding linear change of variables induces a grading by the character
group ("G-degree") preserved throughout, so the Macaulay matrices split into
independent smaller blocks indexed by characters.

## Key claims (as reported)
- Character-graded block splitting of the F4/F5 Macaulay matrices (KN-TECH-011)
  cuts the linear-algebra cost; speedups scale with the group order.
- Constructive: the representation-theoretic decomposition (KN-LIT-030) is turned
  into an actual solving algorithm.

## Relevance to this program
The direct constructive template for the program's equivariant index-calculus
candidate (RQ-EQJ-001): decompose an invariant Semaev system into
character/isotypic blocks to cut Grobner-solving cost. NOTE the scope gap: this
paper handles COMMUTATIVE groups, whereas the program's target symmetry is the
non-abelian G = S_{m-1} semidirect (Z/2)^{m-1}; the abelian normal part
(Z/2)^{m-1} fits directly, but the S_{m-1} factor needs the full
(non-commutative) isotypic machinery of KN-LIT-030 / KN-TECH-012. Whether the
non-trivial blocks carry a useful relation share is the measured question.

## Not verified here
Full paper not read; the character-grading block-splitting relayed from the
abstract and HAL record (hence confidence: reported). Fields confirmed against
the ACM DL DOI and HAL hal-00819337 via search; proceedings ISBN not confirmed.
