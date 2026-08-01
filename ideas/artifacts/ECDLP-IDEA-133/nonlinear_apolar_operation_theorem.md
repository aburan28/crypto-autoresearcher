# P1514 nonlinear apolar operation theorem receipt

## Decision

`SCOPED_NEGATIVE_STANDARD_FLAT_EXTENSION_AND_MOMENT_CONSTRUCTORS__ARBITRARY_STRUCTURED_MOMENT_ORACLE_OPEN`

This receipt does not prove or exhibit the operation required by ECDLP-IDEA-133.
It proves a narrower separation: flat extension and border-basis algorithms decode
an already supplied truncated functional, while the standard exact routes from the
public recursive-`S3` equations to that functional materialize a source join or a
dense Macaulay/quotient object above the frozen cost gate. A new structured
target-local moment constructor is not ruled out.

There is no ECDLP breakthrough claim. No elliptic experiment, relation collection,
factor-log solve, blind descent, or discrete-log recovery was attempted.

## Frozen scale and gate

Let the prime-order subgroup have order `N`, let the public factor base have size
`B=N^(1/5)`, and use ordered signed five-source tuples. This is the favorable
constant-density point because `B^5/N=Theta(1)`. In `B`-coordinates:

- Pollard rho is `B^(5/2+o(1))` time.
- The IDEA-133 promotion cap `N^0.45` is `B^2.25`.
- Relation collection needs `Theta(B)` successful rows and, at constant density,
  `Theta(B)` target queries.
- If one target query costs `B^kappa`, the charged relation-generation exponent is
  `B^(1+kappa)`. Strict sub-rho requires `kappa<1.5`; the `N^0.45` cap requires
  `kappa<=1.25`.
- A target-local working set must be at most `B^2.25` for the memory cap. A
  target-independent preprocessing object must obey the same complete-path cap.

The per-query threshold is stricter than comparing one isolated target query with
rho. A `B^2` target query is individually below `B^2.5`, but `B` such queries cost
`B^3=N^0.6` before factor-log linear algebra or descent.

## Frozen relation-fiber interface

Let `J` be the signed factor-base label set, with `|J|=Theta(B)`, and let
`c:J -> F_p` be a public injective source code. For a fixed public target `R`, define

```text
S_R = {(j1,...,j5) in J^5 : P(j1)+...+P(j5)=R},
```

with the projective recursive-`S3` verifier carrying ordering, signs, infinity,
repeated points, and multiplicity. Write `Z_R` for the corresponding finite scheme
in five code coordinates, and `A_R=F_p[X1,...,X5]/I_R` for its coordinate algebra.

On a reduced fiber, the natural source-biconditional functional has the form

```text
Lambda_R(f) = sum_{z in S_R} w_z f(z),  w_z != 0.
```

Its infinite Hankel operator has rank `|S_R|` when the evaluations are distinct.
For a nonreduced fiber the evaluation terms must be replaced by inverse-system
derivative functionals. Exact multiplicity recovery from one functional requires

```text
ann(Lambda_R) = I_R.
```

Equivalently, the full finite algebra must be represented faithfully by that cyclic
dual functional; a single such functional describes an Artinian Gorenstein
quotient. Therefore the IDEA-133 one-functional interface also owes either a proof
that every admitted exceptional fiber is Gorenstein or a charged multi-functional
replacement. A flat rank observed on a reduced or favorable fiber does not supply
that missing all-strata proof.

Given a faithful `Lambda_R`, a flat truncation and the five multiplication operators
do provide the requested source biconditional: their joint generalized eigenspaces
recover the five public codes, and the inverse of `c` recovers the signed labels.
This establishes that output rank can be `O(1)` at constant relation density. It
does not establish that `Lambda_R` can be constructed in `B^1.25` work per query.

## Lemma 1: flat extension is a decoder, not a constructor

Laurent and Mourrain's sparse flat-extension theorem starts with
`Lambda in Span(C+ . C+)^*`, hence with every truncated value `Lambda(ab)` needed
by the two Hankel matrices. Under the stated rank equality it constructs a unique
infinite flat extension and the associated multiplication algebra. The theorem does
not derive those input values from generators of `I_R`.

Mourrain's border-basis algorithm has the same boundary. Its explicit input is the
known coefficient set `sigma_alpha` of a multi-index sequence. Its arithmetic bound
is output-sensitive in the rank, border size, and number of known sequence terms,
but the cost of producing those terms is outside the algorithm.

Consequently, supplied moments are a valid positive control for source decoding but
are inadmissible as the ECDLP-IDEA-133 constructor. A small flat matrix demonstrates
only that the back end is small after the relation-weighted moments are known.

## Lemma 2: every required moment already contains the target-local join

For the reduced canonical functional with unit weights,

```text
Lambda_R(X1^a1 ... X5^a5)
  = sum_{(j1,...,j5) in S_R}
      c(j1)^a1 ... c(j5)^a5.
```

Thus even `Lambda_R(1)` is the target-fiber count in `F_p`; the code-coordinate
moments are source-weighted sums. Enough separating moments plus flat extension
recover all tuples by the assumed multiplication/source biconditional. Therefore a
routine that constructs those moments from public equations is already a relation
reporter, not a cheaper postprocessing step.

This is a reduction from a qualifying moment constructor to exact source reporting.
It is not a lower bound against every possible reporter. It identifies precisely the
operation that remains to be invented and charged.

## Lemma 3: the standard source-enumeration routes fail the gate

Directly evaluating the moment formula over `J^5` visits `B^5` source states per
target. A favorable two-plus-three meet-in-the-middle split has decks of sizes `B^2`
and `B^3`. Materializing or scanning the larger deck costs `B^3`, which exceeds rho
by `B^0.5`, exceeds the `B^2.25` memory cap, and gives `B^4=N^0.8` work across
`Theta(B)` relation queries.

This agrees with the frozen P1476-P1478 boundary: an admissible complete five-ary
membership mechanism needs a target-query exponent below `1.5`, and at most `1.25`
for the stronger promotion cap. Recasting the source join as entries of a moment
matrix does not change either deck.

## Lemma 4: the cited dense Macaulay trace constructor fails the gate

There is a standard exact route from polynomial generators to moments and
multiplication matrices: construct a Macaulay-type matrix, take a nullspace vector
as a truncated moment sequence, form the quotient basis and moment/trace matrices,
then recover multiplication operators. Janovitz-Freireich, Mourrain, Ronyai, and
Szanto give this route and its degree bounds.

Freeze a favorable five-code-variable model with the five source-membership
polynomials of degree `B` and one relation equation of degree only `2`. This
understates the degree introduced when point coordinates are interpolated from
source codes. In the cited `s>m`, finite-projective-root bound with `m=5`,

```text
k = sum of the largest m+1 degrees - m = 5B-3,
delta = k+1 = 5B-2.
```

The construction uses a Macaulay nullspace vector indexed by monomials through at
least degree `delta-1=5B-3`. Its coordinate count is therefore at least

```text
binomial((5B-3)+5, 5) = binomial(5B+2, 5) = Theta(B^5).
```

Adding the recursive-`S3` intermediate variables can only increase the dense total-
degree monomial count at this cutoff. The standard construction therefore has a
target-local input/state vector of `Theta(B^5)=Theta(N)` before nullspace, moment-
matrix, trace, or eigenspace costs. Repeating it for relation collection gives at
least `B^6=N^1.2` coordinate traffic.

This is a dimension statement about the cited dense Macaulay representation under
its hypotheses. It is not a lower bound against sparse, multihomogeneous, black-box,
or elliptic-specific polynomial-system algorithms. Such an algorithm would still
have to provide the missing moment constructor and complete cost recurrence.

## Route classification

| Route | Moments constructed from `(E,F,R)`? | P1512/P1513 independent? | Charged gate |
|---|---:|---:|---|
| Supplied flat Hankel matrix | No | Formally yes | Inadmissible input oracle |
| Supplied sequence plus border basis | No | Formally yes | Inadmissible input oracle |
| Direct sum over accepted source tuples | Only after reporting sources | Yes | `B^5` direct or `B^3` meet-in-middle fails |
| Dense Macaulay nullspace and trace matrices | Yes, in the cited representation | Yes | `Theta(B^5)` coordinates fails |
| P1513 common norm/gcd feeding moments | Yes | No | Already closed in its tested representations |
| New structured nonlinear moment oracle | Not known | Not proved | Open |

The dense Macaulay route is useful as an independence control: it does not need a
P1512 scalar-linear atomizer or the P1513 common norms, but it is much too large.
Conversely, the compact flat-extension decoder can be small, but its input is the
unconstructed relation reporter. No screened route satisfies both independence and
cost.

## Complete-path exponent receipt

At `beta=1/5` and constant relation density, let a moment constructor cost `B^kappa`
time and `B^nu` memory per target. Ignoring later costs can only favor the proposal:

```text
lambda_relation = (1+kappa)/5,
mu_constructor = nu/5.
```

The IDEA-133 cap requires `kappa<=1.25` and `nu<=2.25`. The standard favorable
meet-in-the-middle constructor has `kappa=nu=3`, hence
`lambda_relation=0.8` and `mu_constructor=0.6`. The dense Macaulay coordinate vector
has `kappa=nu=5`, hence `lambda_relation=1.2` and `mu_constructor=1.0`. Neither
allows a complete factor-base solve or blind descent to be added below the cap.

A supplied `O(1)`-rank moment decoder cannot be assigned `kappa=0`: that omits the
exact operation under test. No fixed `lambda,mu<=0.45` recurrence exists for the
proposed public-input constructor.

## Independence and conclusion

The theorem gate asked for all of the following at once:

1. an explicit public-input `Lambda_R` constructor;
2. flatness and an exact signed-source/multiplicity biconditional on every stratum;
3. independence from P1512 atomization and P1513 common norms; and
4. complete time and memory exponents at most `0.45`.

The supplied-moment routes satisfy neither item 1 nor item 4. The dense Macaulay
route supplies item 1 and is semantically independent for item 3, but fails item 4;
it also needs a fiber-specific Gorenstein or multi-functional treatment for item 2.
The direct join fails item 4. No remaining route has an explicit operation to audit.

Therefore P1514 is `inconclusive` overall, with a scoped negative for flat extension,
border-basis decoding, direct source moments, and the cited dense Macaulay trace
constructor. IDEA-133 must remain theorem-deferred. This receipt does not establish
an arithmetic-circuit lower bound, rule out all nonlinear apolar algorithms, or
change the generic Shoup boundary.

## Primary sources

- Monique Laurent and Bernard Mourrain, [A Sparse Flat Extension Theorem for Moment Matrices](https://arxiv.org/abs/0812.2563), especially Theorems 1.4 and 1.5.
- Bernard Mourrain, [Fast algorithm for border bases of Artinian Gorenstein algebras](https://arxiv.org/abs/1705.01328), especially Algorithm 3.1 and its supplied-sequence input.
- I. Janovitz-Freireich, B. Mourrain, L. Ronyai, and A. Szanto, [On the computation of matrices of traces and radicals of ideals](https://arxiv.org/abs/0901.2778), especially Theorems 3.4-3.5 and Definitions 3.8-3.10.
- Igor Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031).

## Exactly one next executable action

Create and run an independent deterministic audit that freezes this receipt, checks
the `B`, `N`, rho, promotion-cap, relation-query, meet-in-the-middle, and Macaulay
dimension formulas, and mutation-tests every decision boundary before the focus
queue is advanced.
