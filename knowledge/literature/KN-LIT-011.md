---
id: KN-LIT-011
type: literature
title: Data Structures Meet Cryptography - 3SUM with Preprocessing
authors: [Golovnev Alexander, Guo Siyao, Horel Thibaut, Park Sunoo, Vaikuntanathan Vinod]
year: 2020
venue: STOC 2020 (52nd ACM SIGACT Symposium on Theory of Computing)
identifiers:
  eprint: null
  doi: 10.1145/3357713.3384342
  url: https://arxiv.org/abs/1907.08355
tags: [3sum, 3sum-indexing, fine-grained, data-structures, preprocessing, lower-bound, collinear, cryptography]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Studies 3SUM-Indexing (3SUM with preprocessing): preprocess a set into space S so
that "is t a 2-sum?" queries run in time T. Connects data-structure problems to
cryptography against preprocessing attacks.

## Key claims (as reported)
- **Upper bound:** via Fiat-Naor inversion, a suite of algorithms with
  S^3 * T = O~(N^6) on an N-element instance.
- **Lower bounds** generalize to a range of geometric problems, explicitly
  including **three points on a line** (collinearity), polygon containment, etc.

## Relevance to this program
Two direct hits:
1. Their "three points on a line" lower-bound family is exactly the collinearity
   formulation of m=3 EC decomposition (Prop. 4 / the GPT bridge): by the
   chord-tangent law, P+Q+R=O iff the three points are collinear.
2. Their Fiat-Naor upper bound is the state of the art against which this
   program's Theorem 8 requirement (S*T = o(B^2)) can be CALIBRATED -- see
   KN-FIND-FIATNAOR-CALIB-001. The curve touches S*T = B^2 only at (S,T)=(B^2,1)
   and never enters the o(B^2) region.

## Not verified here
Full paper not read; the S^3*T = O~(N^6) form and the geometric lower-bound list
are relayed from the abstract/summary, not re-derived.
