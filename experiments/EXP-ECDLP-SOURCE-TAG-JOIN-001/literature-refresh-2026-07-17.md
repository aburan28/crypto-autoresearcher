# Literature refresh: source tags, structured groups, and batch decomposition

## Status

`LITERATURE-DERIVED`, refreshed 2026-07-17. This note maps the verified
development negative to nearby theory. It does not claim novelty.

## Structured generic groups

Corrigan-Gibbs, Henzinger, and Wu introduce a structured generic-group model
with free access to a partial binary operation on labels. If that operation
constrains a `delta` fraction of labels, their main lower bound gives online
query complexity `Omega(min(sqrt(q), 1/delta))` in the stated model. Their
simplest structured label space assumes a unique factorization into prime
labels. The paper explicitly lists special-case elliptic-curve algorithms among
the attacks not yet modeled, and says that transferring preprocessing lower
bounds into this structured setting needs new non-black-box arguments.

Sources:

- [author page and abstract](https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/)
- [full EUROCRYPT 2026 paper](https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf)

`MODEL-BOUND`: the present source-tag compiler does not instantiate that model
cleanly. A semantic D2 point may have several factor-pair provenances, while the
experiment binds only one selected witness. Recursive addition-law circuits,
all-witness states, coordinate predicates such as `L(x)=0`, and batched target
decomposition therefore remain concrete proof obligations rather than corollaries
of the density theorem.

## Fixed-curve preprocessing

Corrigan-Gibbs and Kogan prove that a generic prime-order discrete-log algorithm
using `S` bits of group-specific advice, online time `T`, and success probability
`epsilon` satisfies `S*T^2 = Omega(epsilon*N)` up to logarithmic factors. They
also give matching generic preprocessing attacks across the parameter range.

Source:

- [EUROCRYPT 2018 paper page](https://people.eecs.berkeley.edu/~henrycg/pubs/eurocrypt18discrete/)

`MODEL-BOUND`: a coordinate-specific compiler can matter only by making
non-black-box use of the curve representation. The development `S*T^2`
comparisons are diagnostics against that frontier, not a theorem that the tested
curves satisfy a concrete lower bound.

## Prime-field rational-map factor bases

Petit, Kosters, and Messeng define prime-field factor bases of the form
`F = {(x,y) in E(F_p) : L(x)=0}`, with a large-degree rational map `L` expressed
as a composition of low-degree maps. Point decomposition is then represented by
a summation-polynomial system coupled to the recursive map equations. Their
algorithms are small-parameter experiments whose asymptotics depend on poorly
understood algebraic-system solving.

Source:

- [PKC 2016 paper](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf)

`OPEN`: `ordinal_sum`, `source_x_sum`, and `parameter_mix` only label the public
construction records of already-enumerated factor points. They do not compile
the recursive equations of `L`, exploit a divisor structure, or solve an
`m >= 5` point-decomposition system. The verified source-tag negative therefore
does not test the central algebraic mechanism of the rational-map proposal.

## Coordinate expansion

Ahmadi and Shparlinski prove an elliptic-curve sum-product statement: for
appropriate scalar sets, at least one of a coordinate-sum set and a
coordinate-of-product set is large. This is evidence that coordinate maps can be
studied with character-sum and additive-combinatorial tools, but it does not
directly bound the collision energy of a set `{P : L(x(P))=0}` under elliptic
addition or the fanout of a recursive decomposition circuit.

Source:

- [On the Sum-Product Problem on Elliptic Curves](https://arxiv.org/abs/0806.0640)

`OPEN`: prove or experimentally falsify a coordinate-specific bound for
`|F+F|`, source-conditioned collision energy, and conditional complement fanout
for compositional rational-map factor bases.

## Batch gap

The literature search found point-decomposition work based on summation
polynomials and rational maps, but did not locate a primary paper whose central
algorithm amortizes prime-field point decomposition over many independent
targets while charging the shared preprocessing and memory traffic. This is a
search result, not a novelty claim; a broader citation review is required before
using that label.

The concrete experimental gap is sharper than generic "batching": given a fixed
curve and factor base, can `K` targets share evaluation of the outer predicates
for `Q_k-f`, or share a recursive addition-law circuit, so that amortized field
operations per target fall with `K`? This explicitly escapes the same-outer-scan
theorem tested by `EXP-ECDLP-SOURCE-TAG-JOIN-001`.

## Next literature action

Search algebraic multipoint evaluation, batched resultants, modular composition,
and incidence bounds for translates of elliptic-coordinate varieties. For each
candidate primitive, require an explicit translation to the full D5 witness
problem and compare against batched exact-D2 lookup, batched materialized D4,
fixed-base BSGS, and parallel rho.
