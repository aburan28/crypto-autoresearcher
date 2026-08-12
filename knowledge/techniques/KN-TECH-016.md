---
id: KN-TECH-016
type: technique
title: Sum-product and additive-combinatorics bounds over F_p
tags: [sum-product, additive-combinatorics, finite-field, equidistribution, quasirandom, incidence, ecdlp]
confidence: reported
complexity: threshold max(|A+A|,|A*A|) >= c|A|^{1+eps} for p^delta < |A| < p^{1-delta}; expander-mixing incidence |I - mn/p| <= sqrt(p*m*n)
applicability: bounding the additive/multiplicative structure and equidistribution of factor-base coordinate sets
source_refs: [KN-LIT-038, KN-LIT-019]
added: 2026-07-22
superseded_by: null
---

## Method
Sum-product estimates (Bourgain-Katz-Tao, KN-LIT-038; Garaev for large subsets)
bound how additively- and multiplicatively-structured a subset A of F_p can
simultaneously be: away from the trivial extremes, max(|A+A|, |A*A|) grows
strictly faster than |A|. Combined with expander-mixing / incidence bounds
(KN-LIT-019), they control the equidistribution of point/coordinate sets and the
count of collinear (chord) configurations.

## Program usage
Underpins the *equidistribution / quasirandomness assumptions* the program makes
about relation x-coordinates -- which set the baseline windowed density
(KN-TECH-015) and the generic rich-line ceiling (RQ-INCB-001). These bounds tend
to CLOSE structure-exploiting proposals: if coordinates equidistribute, windowed
(Coppersmith) and AP-structured (RQ-STR-001) harvesting gain nothing, and chord
arrangements sit at the generic Szemeredi-Trotter ceiling. A measured curve-
specific EXCESS over these bounds would be the interesting (non-generic) signal.

## Applicability limits
Bounds are strongest for large sets relative to p and carry characteristic-p
range restrictions. NOTE (honest gap): the program's research-direction docs
invoke a specific "elliptic-curve coordinate sets are quasirandom" claim
attributed to "Liu-Gao, Acta Math. Sinica 2009," but that citation could NOT be
confirmed against any primary index and is treated as UNCITED here; the
equidistribution of EC-derived coordinate sets should rest on verifiable
Weil-bound / sum-product arguments, not that reference, until a real source is
found.
