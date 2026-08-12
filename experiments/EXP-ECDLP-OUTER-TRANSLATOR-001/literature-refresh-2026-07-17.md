# Literature refresh: outer-aware prime-field decomposition

## Status

`OPEN`, with established algebraic components and an unestablished complexity
advantage. No primary source located supplies an exact reusable batched `m=5`
prime-field point-decomposition data structure with advice `o(B^3)`, online work
`o(B^2)`, and full signed-witness recovery for arbitrary targets.

Failure to locate such a result is a search boundary, not a novelty proof.

## Closest work

### Summation polynomials

Semaev proves the summation-polynomial zero criterion and recursive resultant
construction. Direct five-leaf target decomposition uses `f6`; the present
`f4` is valid only because two pairs are first represented as exact D2 aggregate
points, followed by orientation and leaf recovery.

- I. Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves* (2004): https://eprint.iacr.org/2004/031.pdf

McGuire and Mueller give direct fast evaluation methods for summation
polynomials, including a specialized quadratic-resultant core. Their arithmetic
vector is a mandatory comparator: evaluating `f4` faster does not itself avoid
enumerating tuples or recover witnesses.

- G. McGuire and C. Mueller, *Fast evaluation of summation polynomials*:
  https://eprint.iacr.org/2017/1262.pdf

### Prime-field factor bases and decomposition

Petit, Kosters, and Messeng construct prime-field factor bases from a high-degree
`L(x)` composed of low-degree rational maps. The dedicated decomposition-system
cost remains open, and their concrete decomposition experiments concern two
points rather than fixed-factor-base arbitrary-target `m=5` batching.

- C. Petit, M. Kosters, and A. Messeng, *Algebraic approaches for the elliptic
  curve discrete logarithm problem over prime fields* (PKC 2016):
  https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf

The harness's `rational_union` is not that construction. It labels an explicit
finite accepted-root set by square and Mobius source maps; materializing
`P_b(T)=product(T-t_i)` can discard the recursive low-degree structure that
motivates compositional `L`.

Amadori, Pintore, and Sala provide the nearest concrete prime-field `m=5`
experiments. Their challenge-dependent random point sets and Groebner systems at
small primes are not a reusable factor base, arbitrary-target translator, or
many-target compiler.

- A. Amadori, F. Pintore, and M. Sala, *On the discrete logarithm problem for
  prime-field elliptic curves*: https://eprint.iacr.org/2017/609.pdf

Kosters and Yeo give mathematical cautions about summation-polynomial solving
and heuristic degree claims.

- M. Kosters and S. L. Yeo, *Notes on summation polynomials*:
  https://arxiv.org/abs/1503.08001

### Neighboring extension-field attacks

Gaudry, Diem, Joux-Vitse, and symmetrized summation-polynomial attacks obtain
structure from extension fields, Weil restriction, subfields, or torsion. Their
settings must not be conflated with five-term decomposition over `F_p`.

- Joux and Vitse: https://eprint.iacr.org/2010/157.pdf
- Faugere, Huot, Joux, Renault, and Vitse:
  https://www.iacr.org/archive/eurocrypt2014/84410158/84410158.pdf

## What this experiment reimplements

1. Exact `D2+D3` is a standard `2|3` meet-in-the-middle or fixed-arity
   `5`-SUM-indexing query. It is complete for the represented factor base, but
   it is not a proved lower bound for all preprocessed EC data structures.
2. The proposed source and D2 root products are nested classical resultants or
   norms, followed by polynomial gcd/common-root extraction.
3. Product/remainder trees, multipoint evaluation, and modular composition are
   established polynomial tools. Their existence does not automatically create
   a low-degree eliminant, avoid input construction, or recover EC witnesses.

Relevant general algorithm references include:

- Kedlaya and Umans, modular composition and multipoint evaluation:
  https://authors.library.caltech.edu/records/6bpbb-0gh88
- Bhargava et al., finite-field multivariate multipoint evaluation:
  https://arxiv.org/abs/2205.00342
- Kopelowitz and Porat, preprocessed k-SUM tradeoffs:
  https://arxiv.org/abs/1907.11206

These results are comparison points, not automatic transfers to EC witness
decomposition.

## Explicit-output boundary

If reduced `H_Q` is explicitly emitted as a dense polynomial of degree
`Theta(|D2_x|)=Theta(B^2)`, coefficient writes alone cost `Omega(B^2)` field
elements. A sub-D2 translator must keep the object implicit or sparse, avoid
constructing it, exploit stronger root structure, or share sufficient work over
targets. This is a restricted output-size statement, not a universal lower
bound.

Keeping `x(Q)` symbolic can make a batch template grow toward degree `B^3` in
the target coordinate and a dense grid approaching `B^5`. The experiment must
report that bound even if it specializes each target separately.

## Fixed-curve preprocessing boundaries

Generic fixed-group preprocessing obeys the established `S*T^2` tradeoff up to
logarithmic factors. It constrains generic DLP algorithms, not this coordinate
translator without a reduction.

- Corrigan-Gibbs and Kogan:
  https://people.eecs.berkeley.edu/~henrycg/pubs/eurocrypt18discrete/
- Rotem and Segev:
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12

The structured generic-group result similarly requires an actual partial
operation, constrained-label fraction, and model embedding; x-quotients and
nonunique Semaev decompositions do not instantiate it automatically.

- Corrigan-Gibbs, Henzinger, and Wu:
  https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/

## Precise gap

For fixed `E/F_p` and target-independent `F` of size `B about p^(1/5)`, produce
exact signed five-leaf witnesses for independent targets with no target-specific
advice and measured advice `o(B^3)` plus online work `o(B^2)`, including
construction, bandwidth, and recovery.

Even this is not yet a sub-rho ECDLP algorithm. About `B` relations with
`B=p^(1/5)` require decomposition closer to `T=o(B^(3/2))=o(p^(3/10))`, plus
preprocessing, rank, sparse linear algebra, and individual descent below the
square-root total frontier.

## Contract obligations

- call `D2+D3` a complete comparator, not a floor;
- compare direct `f4` arithmetic with nested root products;
- disclose explicit, sparse, or implicit `H_Q` representation and writes;
- separate `rational_union` from genuine compositional `L`;
- state one-shot and `K in {1,B,16B}` amortization;
- recover signs, identity routes, and all five factor leaves;
- preserve the `0.8x` gates as toy continuation thresholds only;
- require the stronger full-pipeline exponent obligation for any ECDLP claim.
