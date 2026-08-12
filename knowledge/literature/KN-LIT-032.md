---
id: KN-LIT-032
type: literature
title: Tensor-Train Decomposition
authors: [Oseledets Ivan V.]
year: 2011
venue: SIAM Journal on Scientific Computing, 33(5):2295-2317
identifiers:
  eprint: null
  doi: 10.1137/090752286
  url: https://epubs.siam.org/doi/10.1137/090752286
tags: [tensor-train, tensor-network, low-rank, bond-rank, truncation, contraction, semaev]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Defines the tensor-train (TT) / matrix-product format: a d-dimensional tensor is
represented by a chain of 3-index core tensors linked by TT-ranks (bond
dimensions), so each entry is a contracted product of matrices. Storage and
basic operations scale linearly in d and polynomially in the ranks -- avoiding
the curse of dimensionality when ranks stay small.

## Key claims (as reported)
- Stable TT-SVD construction from a full tensor; rank-truncation/rounding with
  computable error bounds.
- The tree-structured counterpart (better matching a branching recursion) is the
  hierarchical Tucker / H-Tucker format: Grasedyck, "Hierarchical Singular Value
  Decomposition of Tensors," SIAM J. Matrix Anal. Appl. 31(4):2029-2054, 2010
  (doi:10.1137/090764189). Rank vocabulary: Kolda-Bader, "Tensor Decompositions
  and Applications," SIAM Review 51(3):455-500, 2009 (doi:10.1137/07070111X).

## Relevance to this program
The representation underlying the program's tensor-network candidate
(RQ-TTN-001, EXP-TTN-001): read the recursive Semaev resultant tree as a
(tree) tensor network and contract with rank-truncation, making *bond rank* --
not dense-resultant degree -- the complexity invariant (KN-OPEN-007). CRITICAL
caveat: exact (untruncated) contraction equals the dense resultant cost; the
candidate lives or dies on whether the bond rank needed for high recall grows
sub-exponentially. Over F_p there is no SVD norm, so truncation must be exact
rank-revealing (border-rank viewpoint) with empirically measured recall -- a real
obstruction, and the program's TTN experiment reported a scoped negative.

## Not verified here
Full paper not read; TT format and rank-truncation relayed from the abstract and
standard references. Fields (incl. Grasedyck, Kolda-Bader) confirmed against SIAM
DOI records via search, not by fetching the primary pages.
