# Literature Review: coordinate SGCP family persistence

**Prepared:** 2026-07-20
**Status:** primary-source refresh, `NOVELTY-UNVERIFIED`

## Closest structured-model result

Corrigan-Gibbs, Henzinger, and Wu define a structured generic-group model with
a free compatible partial operation. Their prime-order results bound online
advantage using the fraction `delta` of labels constrained by that operation;
the preprocessing form has the two terms
`soft-O(S*T^2/q + delta*T)`. Their tightness construction is for the class of
all structured label spaces. It does not show that a conventional elliptic
coordinate predicate, recursive addition circuit, or balanced witness forest
attains the escape term.

Primary source: [The Structured Generic-Group Model](https://eprint.iacr.org/2026/384)

**Gap tested here:** instantiate the model with actual EC evaluations on more
than one curve and measure both constrained density and the support sacrificed
by injectivity and unique factorization.

## Elliptic sum-product results do not answer the sparse factor-base question

Ahmadi and Shparlinski prove a sum-product alternative for sets of scalar
indices: at least one of a coordinate-sum set and a coordinate set produced by
index multiplication is large. This is not an expansion theorem for repeated
EC group sums of a sparse set selected by `L(x)=0`, and it supplies neither
formal witness-factorization compatibility nor decomposition witnesses.

Primary source: [On the Sum-Product Problem on Elliptic Curves](https://arxiv.org/abs/0806.0640)

**Gap tested here:** measure finite `2F`, `4F`, and `8F` support and additive
energy for explicit sparse coordinate root sets, while separately measuring
the smaller support retained by a valid formal order ideal.

## Preprocessed final joins are related to 3SUM-Indexing, not solved by it

Dinur and Golovnev improve integer 3SUM-Indexing to a time-space tradeoff
`T*S = soft-O(n^2.5)` in a parameter range by decomposing the inversion target
into application-specific subfunctions. Their construction uses integer
addition and residue structure. No source checked ports its subfunctions,
collision control, or signed witness recovery to elliptic-curve addition.

Primary source: [Improved Time-Space Tradeoffs for 3SUM-Indexing](https://arxiv.org/abs/2512.04258)

**Boundary:** EXP-SGCP-EMBED-002 does not implement an online final-join data
structure. It only measures whether the structured operand sets survive a
valid coordinate embedding across a toy family.

## Predecessor evidence

EXP-SGCP-EMBED-001 gives one concrete, independently verified five-bit
instantiation. Its exact valid embeddings constrain `20/23`, `17/23`, and
`14/23` labels and retain final support `13/23`, `7/23`, and `7/23` for
`B in {4,6,8}`. The full-support baseline is invalid. This is evidence that the
translation is nonvacuous and lossy on one curve, not evidence of persistence
or scaling.

Local source: `experiments/EXP-SGCP-EMBED-001/analysis-v1.md`

## Novelty boundary

No novelty claim is authorized. Before publication, search must additionally
cover coordinate-defined additive energy, partial semigroup/monoid embeddings,
maximum-coverage independent-set certification, rational-map factor bases,
and any post-2026 work citing the structured generic-group paper.
