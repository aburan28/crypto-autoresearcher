# ECDLP crossover lane: target-aware elliptic-code syndrome search

Status: proposed / scoped against prior no-go

## Research question

Can elliptic-curve point decomposition be re-encoded as a sparse syndrome problem in an elliptic AG evaluation code in a way that exploits the *special target family* `s_R = -v(-R)` and the multiplication structure of the code, without reconstructing the source-evaluation tensor already ruled out by ECDLP-IDEA-210?

This lane is intentionally narrower than generic Schur-closure decoding. The existing rejection of ECDLP-IDEA-210 remains binding: Schur/t-closure by itself only recovers structure already represented in supplied code coordinates, while explicit five-fold source-labelled addition recreates the missing evaluation tensor/source deck. This proposal does **not** reopen that claim.

## Exact bridge to test

For an elliptic curve `E/F_p` with affine point `P=(x_P,y_P)`, use

`v(P) = (1, x_P, y_P, x_P^2)^T`,

which evaluates a basis of `L(4O) = span{1,x,y,x^2}`.

For four distinct affine points,

`P1 + P2 + P3 + P4 = O`

iff the four evaluation columns are linearly dependent. Therefore a 3-point decomposition

`R = P1 + P2 + P3`, with `Pi` in factor base `B`,

can be represented as a sparse syndrome problem

`V_B z = -v(-R)`, `wt(z)=3`,

where support(`z`) identifies the chosen factor-base points. The coefficients of `z` are code coefficients, not EC scalar coefficients.

The research problem is not to prove this correspondence; it is to exploit structure so that locating useful supports is cheaper than enumerating them.

## Why this is not ECDLP-IDEA-210 again

The new promise is target-aware and batch-oriented:

1. every column of `V_B` lies on the same embedded elliptic curve;
2. the syndrome is not arbitrary, but also comes from that curve: `s_R=-v(-R)`;
3. factor-base design is allowed to optimize the induced code for support search;
4. success requires a support-selection/filtering algorithm that avoids materializing the source tensor;
5. dimension-only code distinguishers do not count as progress.

A valid result must demonstrate an advantage specifically on the special curve-valued syndrome family and survive random-code and random-target controls.

## Toy evidence already established

A fixed exact toy instance over

`E/F_1009: y^2 = x^3 + 2x + 25`

has prime group order 991 and a coordinate-only factor base of 32 points. Exhaustive checking found:

- 35,960 four-point subsets checked;
- 36 singular four-column supports;
- zero disagreements between evaluation-matrix singularity and EC addition;
- relation-matrix rank 31 modulo 991, the maximum possible factor-only rank;
- 4,960 three-point subsets checked for an independently coordinate-selected target;
- 5 decompositions for that target;
- recovered target discrete log 780 from the collected factor relations plus a target decomposition, verified by scalar multiplication.

The row code had dimension 4 and Schur-square dimension 8, while a seeded random 4-dimensional comparator had Schur-square dimension 10. This confirms visible algebraic structure.

However, shortening by every 1-, 2-, and 3-point subset produced constant dimension/Schur-square profiles:

- 1 forced zero: `(dim, square-dim)=(3,6)` for all 32 subsets;
- 2 forced zeros: `(2,3)` for all 496 subsets;
- 3 forced zeros: `(1,1)` for all 4,960 subsets.

So **dimension-only shortening is a negative result** and must not be proposed again as the support filter.

## Primary hypothesis

There exists a multiplication-aware statistic or operator derived from the actual multiplication maps of `L(kO)` evaluations, rather than only their dimensions, that can rank or batch-eliminate candidate supports for curve-valued syndromes at lower amortized cost than direct determinant/subset enumeration.

Candidate families include:

- multiplication-map coefficient signatures under shortening/puncturing;
- low-rank changes of structured multiplication matrices as target syndromes vary;
- target-conditioned bilinear forms induced by `L(aO) x L(bO) -> L((a+b)O)`;
- batch elimination across many `R` sharing one factor-base preprocessing phase;
- coordinate-defined factor bases selected for favorable evaluation-code multiplication structure.

These are hypotheses to falsify, not claims of speedup.

## Required controls

Every experiment must include:

- same-size random linear codes;
- random subsets of curve points versus the proposed factor-base rule;
- arbitrary syndromes versus curve-valued syndromes;
- independent targets not constructed from known factor-base decompositions;
- exact EC re-addition verification of every reported support;
- end-to-end accounting including preprocessing, support search, relation rank gain, linear algebra, and target decomposition.

## Primary metric

`cost_per_new_independent_relation = total_charged_work / increase_in_relation_rank`

Secondary metrics:

- support candidates rejected per unit work;
- target decompositions recovered per unit work;
- amortized online cost after fixed preprocessing;
- memory / materialized tensor size;
- scaling exponents fitted across increasing toy field sizes and factor-base sizes.

## Hard failure conditions

Reject or merge into prior no-go if any candidate method:

- requires explicit materialization of all `B^m` source tuples;
- requires source labels or a decomposition oracle as input;
- merely recognizes the curve/code structure without locating supports;
- improves only a code distinguisher, not support search;
- uses targets generated by summing known factor-base points as its only evidence;
- loses the advantage under independent-target or random-code controls;
- reduces equation count while moving equivalent cost into exponentially growing symbolic messages.

## Next executable experiment

Build `EXP-EC-CODE-001` to reproduce the exact toy bridge and then add candidate multiplication-map features. The first experiment should keep the existing exhaustive enumerator as an oracle, compute features for every partial support, and ask only whether any feature predicts membership in a true target support better than chance without using source labels. A positive signal must then be validated on unseen curves and increasing sizes before any algorithmic speedup claim.

## Relationship to adjacent lanes

- ECDLP-IDEA-210: remains rejected for generic Schur closure / source-tensor reconstruction.
- Semaev/summation-polynomial work: this is a different representation of the same decomposition bottleneck; comparisons must charge all support-search work.
- list-decoding proposals: generic list decoding is not assumed to be efficient here; only the special curve-valued syndrome family is in scope.
- graphical-model / sparse-elimination ideas: may be combined only if intermediate symbolic state size is measured explicitly.

## Promotion criterion

Promote this lane beyond toy status only if a support-selection method achieves a reproducible, cross-curve reduction in charged candidate-search work that grows with problem size, while respecting the no-source-tensor boundary and preserving exact target decomposition correctness.
