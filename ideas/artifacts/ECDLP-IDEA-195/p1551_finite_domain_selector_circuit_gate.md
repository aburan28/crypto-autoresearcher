# P1551 finite-domain S3 selector-circuit theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-195`
- Candidate: `P1551`
- Claim: `CLM-P1551-FINITE-DOMAIN-S3-SELECTOR-CIRCUIT`
- Evidence scale: exact split-algebra, Frobenius-projector, rank-two Semaev,
  endpoint-convolution, and explicitly represented quotient-cost statements;
  no experiment
- Contract state: the IDEA-195 contract remains retired, `review_required`,
  unapproved, and zero-run
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_CANDIDATE__FERMAT_EQUALITY_MASK_IS_THE_P1536_FROBENIUS_PROJECTOR__FROBENIUS_IS_IDENTITY_ON_THE_SPLIT_SOURCE_ALGEBRA__HIGH_REDUCED_DEGREE_IS_POINTWISE_SUCCINCT_BUT_DOES_NOT_COMPUTE_GLOBAL_SOURCE_MOMENTS__RANK_TWO_REMAINDER_NORM_GCD_DECIDES_ONLY_A_SUPPLIED_EDGE__STANDARD_MODULAR_COMPOSITION_NORM_TRACE_AND_POWER_PROJECTION_ARE_CHARGED_IN_EXPLICIT_QUOTIENT_DIMENSION__EVERY_SOURCE_FAITHFUL_EXPLICIT_FIVE_DECK_MERGE_REACHES_AT_LEAST_B3_STATE_OR_B5_FULL_STATE__ENDPOINT_GROUP_ALGEBRA_COEFFICIENT_AND_SOURCE_MOMENT_NORMAL_FORM_EXACT__POINT_BASIS_RESTORES_B3_SEPARATOR__CHARACTER_BASIS_REQUIRES_HIDDEN_SCALAR_ORIENTATION_OR_N_MODES__NO_UNREPRESENTED_NONCHARACTER_COEFFICIENT_EXTRACTOR_SUPPLIED__ARBITRARY_CIRCUIT_LOWER_BOUND_NOT_CLAIMED__INCONCLUSIVE`

P1551 freezes the compact finite-field grammar left open by P1550. The
strongest apparent escape is exact but already known: in the split product of
the five factor decks, raise the Semaev value to `p-1` to obtain its equality
indicator. The reduced coordinate degree can be enormous while the formal
powering circuit is short.

That observation does not select a path. On the split factor algebra,
Frobenius is the identity and every admitted arithmetic or equality gate acts
pointwise. Recovering a source requires a trace, norm jet, endpoint
coefficient, or equivalent aggregation over the hidden source tuples. The
P1536 coloured norm jet gives an exact simple-fiber source formula, but its
standard realizations have represented dimension `B^5`; the balanced split
has `B^3` state. Rank-two remainder, norm, and gcd give a real `O(B)` test and
constant-list lift only after the two adjacent path states are supplied.

Within the frozen grammar, every coefficient-complete route therefore has an
exact dichotomy. It either stays pointwise or probes supplied edges and emits
no target-conditioned five-source path, or it invokes modular composition,
power projection, norm, trace, or elimination over an explicitly represented
multi-deck quotient. Exact source replay then reaches at least a three-deck
object of dimension `B^3`, and the direct five-deck object has dimension
`B^5`. Both exceed the `B^(9/4)` setup/state and `B^(5/4)` query rectangle.

This is a grammar theorem, not a representation-independent arithmetic- or
Boolean-circuit lower bound. A new noncharacter, nonenumerative coefficient
extractor whose state is not an explicit source quotient remains outside the
grammar. No such operation is supplied here, and IDEA-012, IDEA-156,
IDEA-199, and IDEA-266 already record that missing interface. Renaming it as
an oracle is not a successor algorithm.

There is no sub-rho ECDLP algorithm, Shoup-bound improvement, or breakthrough.

## Hash-bound inputs

- `ideas/artifacts/ECDLP-IDEA-195/p1550_high_branching_s3_path_locator_gate.md`:
  `b41bb7919b3b32fe062369139d450649912f94edb63b72d72f5bc397665700c3`
- `ideas/artifacts/ECDLP-IDEA-133/p1536_frobenius_projector_norm_jet_audit.md`:
  `81ec3515b584c36a809c155b5f26127bce91c09d7bfe6bccc425cdef07d51393`
- `ideas/ECDLP-IDEA-012_aggregate_complement_divisor_compression_hypothesis.md`:
  `aef88ea4ba5053c214325396a6bfebdcbf0d3ce15f8454fb29336cfa3d185363`
- `ideas/rejected/ECDLP-IDEA-080_microlocal_characteristic_cycle_atomization_hypothesis.md`:
  `63d9192daf67b05f94ef8db1c8837949430ce8570403a0215c87e140490e60d5`
- `ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md`:
  `228c2d55df137225c92f2a14afca188d09bc8917ced63b6c4d4ac2027accda39`
- `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md`:
  `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e`
- `ideas/artifacts/ECDLP-IDEA-068/p1513_common_norm_route_screen.md`:
  `9ec1a5010d7774ee74ff8af7d910bced915cec76213ddd5beca1b7c7aac5c8a8`
- `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r11_independent_audit.md`:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`
- `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md`:
  `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1`
- `ideas/artifacts/ECDLP-IDEA-003/p1533_r1_independent_audit.md`:
  `0de12da09c1bc49aa577431cff5ac09a264a367bce57aa1699c495015c28803f`

P1550 supplies the generic-prime one-step primitive, rational-branch capture
theorem, explicit-catalog work bounds, and finite-domain degree floor. P1536
supplies the exact equality projector and coloured norm jet. The remaining
records are semantic controls for aggregate divisor convolution, collapsed
source annotations, conditional coefficient extraction, ranked endpoint
coefficients, standard norm construction, local separators, dynamic source
trees, and Fourier/resultant coordinates. None is promoted or generalized.

## Frozen finite-domain circuit grammar

Let

```text
E/F_p be ordinary,
G=<P> subset E(F_p),
|G|=N prime,
B=N^(1/5),
F_i subset G, |F_i|=Theta(B), i=1,...,5.
```

The `F_i` are public coloured exact signed factor sets. For every colour, let

```text
X_i={x(A):A in F_i},
f_i(T)=product_(a in X_i)(T-a).
```

Each `f_i` is squarefree. A public `O(B)` signed dictionary records every
admitted point over each root, including the preregistered infinity and
exceptional-chart conventions. The exact signed dictionary is charged; an
x-coordinate hit is not an oriented source.

The grammar admits only the following target-independent operations.

1. Base-field arithmetic, complete projective elliptic-curve arithmetic, and
   the fixed projective charts of `S_3` and `S_6`.
2. For supplied exact states `U,V`, reduction of `f_i` modulo the quadratic
   `S_3(x(U),x(V),T)`, its rank-two norm, and a degree-at-most-two gcd plus
   exact signed point checks.
3. For an explicit source subset `I`, arithmetic in

   ```text
   A_I=tensor_(i in I) F_p[T_i]/(f_i),
   dim_Fp(A_I)=product_(i in I) deg(f_i)=Theta(B^|I|).
   ```

   Coefficient, triangular, primitive-element, and split-value
   representations are all charged by their retained field-element traffic.
4. Public powering, Frobenius, and Fermat equality masks inside one such
   explicitly represented `A_I`.
5. A constant number of modular-composition, power-projection, trace, norm,
   resultant, or transposed stages over explicitly named quotient algebras.
   Their input, output, temporary state, and reductions are charged in the
   represented dimensions.
6. Constant-size square-zero marker rings and exact projective verification
   after a source candidate has been returned.

The grammar does not admit an unnamed global `TRACE`, endpoint coefficient
oracle, source unranking oracle, root iterator, branch catalog, target-fitted
coefficient, advice table, learned selector, unrestricted Boolean program, or
free transposed operation. A compact formula is credited only after its input
and output representations and every aggregation stage are typed.

The reduced-degree condition is also frozen. Coordinate functions are reduced
modulo the exact factor and finite-domain equations. P1550's
`B^(11/4)` floor is required for an explicitly enumerated finite-domain
rational family to fit the relation-work count. A short circuit attaining
that reduced degree is necessary evidence for the proposed escape, but degree
alone supplies neither source output nor a cost bound.

## Equality projector reconstruction and semantic deduplication

Put

```text
A_col=tensor_(i=1)^5 F_p[T_i]/(f_i),
D=dim_Fp(A_col)=Theta(B^5),
g_R=S_6(T_1,T_2,T_3,T_4,T_5,x(R)).
```

Because every `f_i` splits into distinct linear factors over `F_p`, evaluation
gives

```text
A_col isomorphic to F_p^(X_1 x ... x X_5).
```

Fermat's identity gives the exact pointwise mask

```text
chi_R=1-g_R^(p-1),
chi_R(a_1,...,a_5)=1 iff g_R(a_1,...,a_5)=0.
```

This can have very high reduced degree and a short formal repeated-squaring
description. It is exactly the P1536 Frobenius projector and the indicator
used by IDEA-156; it is not a new selector.

Frobenius does not mix source coordinates. Since `A_col` is a product of
copies of `F_p`,

```text
h^p=h for every h in A_col.
```

Public powering constructs a pointwise predicate. The desired source moments
are instead global linear functionals such as

```text
M_nu(R)=Tr_(A_col/F_p)(T^nu*chi_R).
```

The equality-mask circuit contains no operation that computes this trace from
its succinct syntax. Expanding the mask in the split basis touches `B^5`
coordinates; reducing it in the dense quotient retains `B^5` coefficients.
Writing `Tr` after the formula is therefore an omitted constructor, not a
constant-cost consequence of the short powering chain.

## Pointwise-versus-aggregation lemma

Under the evaluation isomorphism, base-field arithmetic, Frobenius, powering,
and equality masks act independently on every source tuple. They may change
the value attached to a tuple but do not combine values from two tuples and
do not expose an index of a nonzero tuple. Consequently, a circuit containing
only those gates can decide a supplied coordinate or retain a succinct
pointwise predicate, but it cannot return a hidden source index.

The rank-two Semaev primitive has the same exact boundary. Given `U,V`, it
tests whether one of at most two Kummer transition candidates lies in one
factor deck and lifts a hit to a constant signed list. It has no quantified
input over unknown `U,V`. Supplying those states is already a path prefix;
producing them from the target requires either a P1550 branch, a source table,
or a multi-deck aggregation.

Thus a source-complete circuit in the frozen grammar must invoke at least one
nonpointwise stage. The only admitted nonpointwise stages are explicitly
represented quotient operations. This establishes the grammar dichotomy:

```text
pointwise or supplied-edge path  -> no target-conditioned five-source output;
explicit quotient aggregation   -> represented source-product traffic.
```

The lemma does not claim that no other arithmetic operation can aggregate a
succinct predicate. It says that such an operation is absent from the frozen
syntax and must be written and costed before it can be evaluated.

## Explicit quotient and merge-size gate

The direct quotient has dimension `B^5`. Standard squarefree triangular-set
algorithms make multiplication, modular composition, norm, trace, and power
projection quasi-linear in the represented quotient dimension, up to their
stated field and logarithmic factors. They improve dependence on presentation
parameters; they do not replace dimension `B^5` by the constant number of
requested moments.

A staged source-faithful computation does not repair the cap. Label each
intermediate object by the set of source colours whose exact coordinates or
square-zero source channels it retains. Any merge tree that ends with all
five colours has an intermediate node carrying at least three colours, or it
forms the all-five object in one stage. Under the admitted tensor-quotient
representation, those cases have dimensions at least

```text
B^3 and B^5,
```

respectively. Eliminating a source coordinate before recording its exact
marker coefficient makes source replay incomplete. Contracting it to a
constant-size exact source statistic without forming the represented object
would be the unrepresented extractor that the grammar does not contain.

The same accounting appears in a balanced split. Two source decks can be
listed in `B^2` state, but the complementary three-source side has `B^3`
states or `B^3` streamed work per target. A constant-rank expression for
`S_6` does not change this: even a linear five-list sum has constant tensor
rank while retaining the endpoint-indexing problem.

At `B=N^(1/5)`, the P1551 caps are

```text
setup/state <= B^(9/4)=N^0.45,
one target query <= B^(5/4)=N^0.25.
```

An explicit `B^3=N^0.60` merge already fails setup and memory; a streamed
`B^3` merge fails query. The direct `B^5=N` quotient is still farther outside
the rectangle. Materializing the P1550 degree floor
`B^(11/4)=N^0.55` as coefficients or values also fails setup before relation
collection begins.

## Exact endpoint-convolution normal form

The missing aggregation has a useful exact normal form. Let `F_p[G]` denote
the group algebra with basis `[A]` for `A in G`, and multiplication
`[A][B]=[A+B]`. Define

```text
U_i=sum_(A in F_i) [A].
```

Then

```text
[R](U_1*U_2*U_3*U_4*U_5)
```

is the number modulo `p` of exact coloured signed tuples satisfying

```text
A_1+A_2+A_3+A_4+A_5=R.
```

Source moments can be included exactly. Work over

```text
D=F_p[eps_1,...,eps_5,eta_1,...,eta_5]/m^2,
m=(eps_1,...,eps_5,eta_1,...,eta_5),
```

and set

```text
U_i^~=sum_(A in F_i)
      (1+eps_i*x(A)+eta_i*y(A))*[A].
```

For `U^~=product_i U_i^~`, its endpoint coefficients satisfy

```text
C_R       =[R][1]U^~
X_(i,R)   =[R][eps_i]U^~
Y_(i,R)   =[R][eta_i]U^~,
```

where `C_R` is the tuple count modulo `p`, while `X_(i,R)` and `Y_(i,R)` are
the sums of the corresponding source coordinates over all tuples. If the
coloured fiber contains exactly one tuple, these ten marker coefficients
return all five exact signed points and direct projective verification proves
the row.

This is an exact positive diagnostic, not a complete selector. On a multiple
fiber, the markers are aggregate moments rather than one source tuple, and a
field-valued count does not certify integer uniqueness. P1536's norm-jet
derivative gives an exact simple-fiber test in the full source algebra, but
its constructor has the same represented-dimension obstruction. Repeated,
unsigned, infinity, tangent, and nonreduced strata require their own exact
source channels; none is supplied by the scalar endpoint coefficient.

The identity semantically matches IDEA-012's Abel-Jacobi convolution,
IDEA-080's aggregate skyscraper multiplicity, IDEA-156's conditional
coefficient oracle, and IDEA-199's endpoint coefficient deck. It explains the
residual but does not make that residual novel.

## Endpoint representation controls

The point basis of `F_p[G]` makes input insertion public, but multiplication
is elliptic endpoint convolution. Explicit pair sums use `B^2` entries; any
exact `2+3` join materializes or streams the `B^3` side. Attaching the marker
channels preserves source moments but does not reduce support.

Over a splitting field, the character basis diagonalizes convolution. For
`G=<P>` of order `N`, however, evaluating a character on `A=[a]P` requires
the hidden scalar orientation `a`, an equivalent pairing/extension-field
orientation, or all `N` endpoint modes. Scalar labels would reveal the
factor-base logarithms that relation collection is meant to compute. All
`N=B^5` modes miss the cap. This is a control on the standard Fourier
realization, not a theorem against every noncharacter representation.

ECFFT does not supply the missing transform. It evaluates polynomials on an
auxiliary smooth-order elliptic-curve tree; it does not diagonalize addition
in the arbitrary prime-order target group or attach exact Semaev sources to a
target coefficient. Extension-field factor decks likewise need an exact
rational-point return, inverse fibers, rank, and masked descent; a coordinate
field trace does not preserve elliptic addition.

## Route dispositions

| Route | Exact result | P1551 disposition |
|---|---|---|
| Fermat equality mask | exact pointwise Semaev indicator | P1536/IDEA-156 semantic duplicate; trace absent |
| Public Frobenius | identity on the split `F_p` source algebra | no source mixing or aggregation |
| Rank-two remainder/norm/gcd | `O(B)` supplied-edge test and constant-list lift | no path-state generator |
| Dense projector or norm jet | exact simple-fiber formulas | `B^5` coefficients or values |
| Triangular modular composition/power projection | quasi-linear in represented quotient dimension | `B^5` source product |
| Balanced point or quotient split | exact endpoint join | `B^3` state or query |
| Endpoint group-algebra markers | exact count and conditional source moments | coefficient extractor and multiple-fiber unranking absent |
| Character/Fourier endpoint basis | diagonal convolution after scalar orientation | hidden DLP/pairing orientation or `N` modes |
| Ranked subset/source DP | exact on explicit source subsets | IDEA-199 coefficient-deck duplicate |
| Dynamic evaluation/source tree | exact after supplied triangular source algebra | IDEA-266 constructor duplicate |
| Dense high-degree finite-domain branch | can meet the degree floor | coefficient/value state exceeds cap |
| Arbitrary compact selector circuit | not classified | outside the frozen grammar; no lower bound claimed |

## Complete cost and all-strata boundary

The most favorable random-support model gives constant expected five-source
relation density at `B=N^(1/5)`. Granting that density, one needs `Theta(B)`
independent known-scalar relation rows, factor-log linear algebra, and the
identical circuit on fresh masked targets `Q+[t]P`.

No admitted P1551 route reaches that stage. The first source-complete
aggregation already costs at least `B^3`, giving time or memory exponent at
least `3/5=0.60`. The direct quotient costs `B^5=N`. These bounds precede
failed targets, duplicate rows, rank defects, signed ambiguity, factor-log
verification, blind descent, output, and bit complexity.

The coloured projector is also not an all-strata relation algorithm. A fixed
partition excludes repeated use of one point across colours, x-coordinates do
not determine signs, and multiple coloured fibers are not unranked by first
moments. A complete circuit must handle or preregister every signed,
repeated-source, tangent, infinity, multiple-fiber, and nonreduced branch and
then prove that the retained rows reach rank `B`. No such circuit or rank
theorem is supplied.

Therefore neither `lambda<=0.45` nor `mu<=0.45` is established. No relation
campaign, factor-log solve, masked descent, or scalar recovery is authorized.

## Scoped theorem and residual

Within the frozen P1551 grammar:

1. Pointwise powering, Frobenius, and equality masks do not aggregate hidden
   source coordinates.
2. Rank-two remainder, norm, and gcd do not quantify over unknown path states.
3. Every admitted aggregation is charged over an explicit source quotient or
   endpoint-support representation.
4. Exact source-faithful staged aggregation reaches at least `B^3` represented
   traffic, while the direct five-deck projector has `B^5` traffic.
5. Hence no circuit written in this grammar meets the
   `B^(9/4)/B^(5/4)` rectangle or the complete `lambda,mu<=0.45` gate.

The preserved residual is narrower:

```text
an explicitly written noncharacter, nonenumerative endpoint-coefficient
and source-unranking operation whose representation is not an explicit
source quotient, branch/root list, scalar-index table, or B^3 support deck.
```

This receipt does not prove that residual impossible. It records that no such
operation is present and that the residual is already the missing-oracle
interface of IDEA-012, IDEA-156, IDEA-199, and related source-router entries.
It must not be queued as a novel algorithm without a mechanism-new identity.

## Independent decision

P1551 is terminal inconclusive within its frozen finite-field circuit grammar.
It preserves P1550's generic-prime one-step S3 primitive and finite-domain
degree exception, and it adds an exact pointwise-versus-aggregation boundary
plus the endpoint group-algebra coefficient/source-moment normal form. It does
not close unrestricted finite-field circuits or prove a generic lower bound.

No experiment ran. No contract, solver, fixture, relation campaign,
factor-log solve, masked descent, Shoup-bound improvement, or breakthrough
exists.

## Exactly one next action

Close P1551 terminal inconclusive and perform a corpus-wide operation-level
rerank as P1552. Review every active, deferred, rejected, anomalous, and
`REVISE` entry before admitting one mechanism-distinct theorem candidate.
Treat a generic endpoint coefficient extractor, conditional coefficient
oracle, source annotations, solver swap, parameter change, dense resultant,
and supplied source algebra as controls. The next candidate must publish one
explicit identity or representation that removes the aggregation obstruction,
give exact all-strata source output, and fit the complete
`lambda,mu<=0.45` path before any contract or experiment. If no such operation
survives semantic deduplication, record the theorem-deferred frontier rather
than relabeling the missing oracle.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.
- Poteaux and Schost, *Modular Composition Modulo Triangular Sets and
  Applications*:
  <https://cs.uwaterloo.ca/~eschost/publications/mulmodcomp.pdf>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*:
  <https://arxiv.org/abs/2512.04258>.
- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I*: <https://arxiv.org/abs/2107.08473>.

These sources establish the Semaev interface, represented triangular-set
algorithms, a current indexing control, and the scope of ECFFT. None supplies
the missing endpoint coefficient/source-unranking operation or a
generic-prime ECDLP improvement.
