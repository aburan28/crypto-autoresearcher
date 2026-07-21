# P1553 Query2P1 indexing gate R3

## Classification

- Owner: existing P1553/P1513/P1551/P1516 frontier; no P1554.
- Evidence: theorem-only producer plus independent red team; no run.
- Status: `REVISE_SCOPED_REDUCTION`.
- Labels: `theorem-only`, `non-run`, `model-bound`,
  `novelty-unverified`.
- Cryptanalytic result: no relation campaign, independent relation-rank
  theorem, factor-log solve, scalar-blind descent, Shoup-bound improvement,
  or ECDLP breakthrough.

The R2 finite-deck closeout reduced the remaining reporter question to an exact
`2+2+1` decision operation. R3 reconstructs current indexing upper bounds,
tests small quotients and coordinate encodings, and types the exact
resultant/norm routes. It also corrects the producer's proposed `PCZT-E`
reduction: in the stated access model, `PCZT-E` is `Query2P1` renamed and its
whole-divisor translation gate assumes the missing operation.

The smallest non-tautological residual is the explicit target-label
common-factor object `z_R(T)` defined below. No algorithm constructs it inside
the frozen rectangle.

## Hash-bound review chain

| Receipt | SHA-256 |
|---|---|
| `ideas/artifacts/ECDLP-IDEA-012/p1553_finite_deck_weighted_endpoint_gate_r2.md` | `55acc1457e7fd5a740da57c2c1db957374c7c18561c67b1748176dc8c61fcda5` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_report.yaml` | `60488d10253b4161562704e048a5e57dda33e031051ed00cf43ad339ac9125bb` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_theorem_gate.md` | `0f6d5e1caabbe2edfd84f76404805e2d4df5316263d384ad0e10f0b685527f92` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-RT-R1/red_team_report.yaml` | `982ed54f11ddcc7ae80b87b49eae8f8b880d7e67b8adebc249a67394af324647` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-RT-R1/query2p1_red_team.md` | `626e411cebe1c02e5c1437a04deb6822dfffb752e3a1969579694e89f8fe9a06` |

The producer verdict is a conditional reduction plus scoped named-route
failure. The independent red team reconstructs the indexing, quotient, carry,
and conditional generic controls, but rejects `PCZT-E` as a narrower reduction.
Both receipts allocate no contract, experiment, shared status change, P1554,
or breakthrough claim.

## Frozen interface

Let `G=<P>` be a prime-order subgroup of `E(F_p)` with

```text
N=p^(1+o(1)),       B=N^(1/5).
```

There are five signed, source-labelled decks `F_1,...,F_5`, each of size
`Theta(B)`, and a fresh point target `R`. Preprocessing builds two dyadic
pair-divisor indexes

```text
D_12={(a_1,a_2,u=a_1+a_2)},
D_34={(a_3,a_4,v=a_3+a_4)}.
```

Each pair occurrence belongs to `O(log^2 B)` canonical ancestor pairs, so the
construction and retained occurrence state are

```text
O(B^2 log^2 B)=B^(2+o(1)).
```

For canonical dyadic restrictions `I_1,...,I_5`, the query must decide exactly

```text
C_R=sum_(u+v+a=R) m_12(u)m_34(v)m_5(a) != 0
```

and support `O(log B)` charged restriction queries that recover one fully
labelled source tuple. Final group addition verifies the tuple. Counts and
multiplicities are permitted but are stronger than the required existence bit.

The intermediate rectangle is

```text
preprocessing, advice, and retained state <= B^(9/4+o(1)),
total online time and workspace            <= B^(5/4+o(1)).
```

Target-dependent advice, a scalar representative or residue of `R`, omitted
signs, and incomplete elliptic charts are not granted.

## Current indexing controls

The checked primary upper bounds do not enter the rectangle on a natural
encoding.

| Route | Preprocessing | Advice/state under the query cap | Total query | Additional failure |
|---|---:|---:|---:|---|
| Dinur--Golovnev on two `B^2` pair lists, one target | `B^4` | at least `B^(15/4)` | at most `B^(5/4)` | fixed lists, no dyadic subsets, no additive point-to-integer map |
| Dinur--Golovnev with all `B` fifth shifts | `B^4` | at least `B^(19/4)` | at most `B^(5/4)` | same mapping and restriction failures |
| Dinur--Golovnev asymmetric pair versus pair-plus-fifth | `B^5` | at least `B^(19/4)` | at most `B^(5/4)` | materializes a `B^3` side |
| Dinur--Golovnev full five-summand control | `B^5` | best `B^(9/2)` | best `B` | does not enforce separate source colours |
| Kasliwal--Polak--Sharma, unknown target universe | `B^4` | `B^4` | `B^3` | integer addition; occurrence wrapper still needed |
| Kirkpatrick--Kuszmaul--Mathialagan--Vassilevska Williams | `B^4` | at least `B^(10/3)` | at least `B^3` | randomized oblivious-adversary guarantee |

For the Dinur--Golovnev two-list substitution, `n=B^2` gives

```text
S=B^(5-2 delta),       T=B^(2 delta).
```

One target forces `delta<=5/8`. Sweeping the fifth deck costs
`B^(1+2 delta)`, forcing `delta<=1/8`. These are positive algorithm controls,
not lower bounds against a new data structure.

## Prime-order quotient and scalar-carry correction

If `q:G->H` is a group homomorphism, then `ker(q)` has order `1` or `N`.
Therefore `q` is constant or injective, and there is no nonconstant
homomorphic quotient with image smaller than `N`.

This lemma is deliberately narrow. It does not rule out nonhomomorphic
coordinate algorithms, target-local state, special decks, or known-scalar
integer hashing.

If canonical scalar representatives `x_i,r in [0,N)` are known, then

```text
sum_i x_i = r (mod N)  iff  sum_i x_i = r+cN
```

for constantly many wraps `c`. Integer modular hashing can enumerate those
wraps and the ordinary base-`m` carries exactly. The unavailable step on a
fresh point challenge is obtaining the scalar representative or its residue.

For `m=B^3`, an oracle for `r_0=log_P(R) mod m` leaves `B^2` candidates and

```text
R-[r_0]P=[t]([m]P),       0<=t<Theta(B^2).
```

BSGS completes `t` in `B` group work and `B` memory. Thus the residue oracle
already supplies powerful partial-DLP information; integer carry hashing
itself remains a valid countercontrol.

## Exact algebraic route gates

### Shifted pair-divisor resultants

On the additive-line control, one fifth point `a` can be tested by

```text
Res_U(H_12(U),H_34(R-a-U))=0.
```

An elliptic realization must use complete signed coordinate-section rings,
saturate denominator and base-locus components, and handle tangent, vertical,
infinity, repeated-support, and nonreduced strata. One standard degree-`B^2`
test costs `B^(2+o(1))` represented work; `B` shifts cost `B^(3+o(1))`.
Eliminating the shift symbol into a dense packed polynomial can expose `B^4`
coefficients.

### Target-label quotient norm

Assign distinct public occurrence labels `t_a` to the selected fifth deck and
define

```text
g_I(T)=product_(a in I_5)(T-t_a),
A_5=F_p[T]/g_I(T)=Map(I_5,F_p).
```

Interpolate the complete signed points `R-a` in `A_5`. A degree-`B^2` pair
divisor over this `B`-dimensional algebra carries `B^3` base-field
coordinates. Standard resultant, norm, triangular, modular-composition,
power-projection, and explicit split-ring realizations therefore cost
`B^(3+o(1))` online work. Packing the fifth targets changes the syntax, not
the represented dimension.

### Dynamic splitting

For a no-relation query, every component intersection value is nonzero. The
resultant is a unit in `A_5`, so there is no zero divisor on which a dynamic
evaluator can split early. A brancher must inspect every component or invoke a
genuine aggregate unit/common-factor test. Standard componentwise evaluation
again costs `B^3`. Positive-parent source replay also asks negative child
queries, so an early-hit analysis is not a worst-case bound.

This rejects branching-only speedups. It is not a lower bound against a new
aggregate or representation-sensitive algorithm.

## `PCZT-E` correction

The producer defines

```text
K_R(U)=product_(a in I_5) H_34(R-a-U)
```

and asks whether `H_12` and `K_R` have a common zero. Distributing the
existential quantifier through the product gives exactly `Query2P1`. The
producer grants the same inputs, restrictions, output, witness, and resource
contract as the original query.

Calling each translation of the whole degree-`B^2` divisor one gate hides the
missing operation. Dense translated sections expose `B^2` coefficients for
each of `B` shifts; leaf products expose `B^2` pair endpoints for each shift;
and a symbolic label parameter exposes a degree-`B^2` section over the
`B`-dimensional algebra `A_5`. Every standard representation restores `B^3`
traffic.

Therefore `PCZT-E` is not a narrower reduction or a new hypothesis owner. It
is compact syntax for the P1513 translated-product locator, the P1551 endpoint
aggregation oracle, and the P1516 missing target-local collision router.

## Smallest non-tautological residual

Let `A_I(T)` interpolate the selected complete signed fifth point in `A_5`.
Define

```text
r_R(T)=the complete elliptic intersection resultant of
       D_12 and (tau_(R-A_I(T)) o [-1])_*D_34,
       reduced modulo g_I(T),

z_R(T)=gcd(g_I(T),r_R(T)).
```

The required operation returns `z_R(T)`, an equivalent nontrivial factor, or
a unit certificate. Its degree is at most `B`. A nonconstant factor identifies
exactly the fifth occurrence labels extendible to a selected pair-pair
relation. Repeated calls on canonical restrictions must recover the two pair
sources and the fifth source within the total online cap, followed by direct
group verification.

Unlike `PCZT-E`, this has an explicit algebraic output and a checkable
componentwise meaning. It is stronger than a cancellation-prone trace,
moment, or checksum, and it does not confuse a common root with a weighted
coefficient.

No audited algorithm constructs `z_R` from the compact dyadic trees inside
the rectangle. Standard dense-section, resultant, quotient-ring, norm,
triangular, power-projection, and componentwise routes expose `B^3` traffic.
A complete-chart, source-labelled, representation-sensitive construction
remains the sole explicit exception.

## Other representation controls

- Exact FFE equality masks provide constant-size point predicates but no
  sub-`B^3` contraction.
- Semaev x-coordinate summation polynomials accept some compatible signs;
  adding signed y-coordinate and chart equations restores exact leaves but not
  the missing aggregation.
- Every nontrivial character of the prime-order point group has order `N`.
  Exact Fourier inversion uses `N=B^5` modes, while evaluating a character on
  an unoriented point requires scalar information or another unconstructed
  representation map.
- Extension-field and pairing routes must charge field degree, construction,
  orientation, target-group DLP, and return to rational points.
- ECFFT accelerates polynomial arithmetic through an auxiliary smooth-order
  tree; it does not diagonalize addition in the prime-order target group.
- Dynamic triangular and equiprojectable methods consume a represented
  zero-dimensional source algebra; they do not construct the compact source
  algebra for free.

Special decks and untested target-local, randomized exact, word-RAM,
cell-probe, arithmetic-circuit, and representation-sensitive algorithms remain
outside the scoped route failures.

## Conditional generic-preprocessing control

Maurer--Portmann--Zhu bound generic DLP extraction success in their
preprocessing model by a constant multiple of

```text
advice_bits * (k_main+1)^2 / N.
```

At the frozen caps,

```text
B^(9/4) * (B^(5/4))^2 = B^(19/4) < B^5=N.
```

A complete generic DLP extraction reduction with constant success at these
resources would therefore conflict with that model. `Query2P1` and `z_R` are
not themselves generic DLP extraction, and curve coordinates are non-generic
information. This supplies no Query2P1, coordinate, Semaev, circuit, or ECDLP
lower bound. It instead requires any complete positive path to exploit the
prime-field representation or leave the model hypotheses.

## Operation-level deduplication

| Owner | Same operation and information flow |
|---|---|
| P1513 / IDEA-121 | Translated pair-divisor product and common-factor localization; standard norm costs `B^3`. |
| P1551 / IDEA-195 | Endpoint existence or coefficient aggregation followed by exact labelled source unranking. |
| P1516 | Two `B^2` target-independent pair states plus the absent target-local collision router. |
| IDEA-138 / IDEA-156 | Witness self-reduction from a supplied exact conditional predicate; replay does not construct the predicate. |
| IDEA-199 | Endpoint coefficient access and source unranking from a compact transform; changing the backend does not supply the coefficient deck. |
| IDEA-266 | Dynamic zero-divisor splitting after a source algebra is supplied; no-relation branching does not construct the aggregate certificate. |

The `z_R` output sharpens the existing residual. It is not a mechanism-new
candidate and receives no new ID.

## Complete-path gate

Even a passing `z_R` construction must still prove:

- a complete signed and confluent chart model on every admitted restriction;
- total `O(log B)` source replay inside the online cap;
- sufficient generic-prime relation density and `Theta(B)` independent rows;
- factor-log completion and verification;
- the identical target-uniform operation for scalar-blind `Q+[t]P` descent;
- failure, retry, ambiguity, output, bit-time, and bit-memory accounting; and
- complete exponents `lambda,mu<=0.45`.

None is supplied by the indexing, quotient, resultant, norm, FFE, Semaev,
dynamic-evaluation, or generic-preprocessing controls.

## Disposition

`REVISE_SCOPED_REDUCTION__CURRENT_INTEGER_INDEXES_REQUIRE_B4_PREPROCESSING_OR_ADVICE_ABOVE_CAP__TARGET_SCALAR_RESIDUES_ARE_PARTIAL_DLP_NOT_FREE_POINT_HASHES__PRIME_ORDER_SUBGROUP_HAS_NO_NONTRIVIAL_SMALL_HOMOMORPHIC_QUOTIENT__KNOWN_SCALAR_CARRY_HASHING_RETAINED_AS_COUNTERCONTROL__GENERIC_PREPROCESSING_Q2S_BENCHMARK_FAILS_FROZEN_RECTANGLE__SHIFTED_PAIR_DIVISOR_RESULTANT_EXACT__STANDARD_TARGET_POLYNOMIAL_QUOTIENT_NORM_COSTS_B3__DYNAMIC_ZERO_DIVISOR_SPLITTING_DOES_NOT_CLOSE_NO_RELATION_BRANCH__PCZT_E_IS_QUERY2P1_RENAMED__TARGET_LABEL_COMMON_FACTOR_Z_R_OPEN__P1513_P1551_P1516_MERGE__ALL_STRATA_RANK_LOGS_DESCENT_UNSUPPLIED__NO_P1554__NO_RUN__NO_BREAKTHROUGH`.

No contract, solver, fixture, experiment, relation campaign, factor-log solve,
blind descent, scalar recovery, Shoup-bound improvement, or breakthrough is
authorized or claimed.

## Exactly one next action

Under existing P1553/P1513/P1551/P1516 ownership, write one theorem-only
specification of `z_R(T)=gcd(g_I(T),r_R(T))`. Either give a complete-chart,
source-labelled algorithm that constructs `z_R` from the dyadic pair trees
within `B^(9/4+o(1))` preprocessing/advice and `B^(5/4+o(1))` total online
time/workspace including every replay query, or preserve it as the sole
explicit representation-sensitive exception with the standard `B^3` route
charged. Create no P1554, contract, solver, fixture, experiment, or
breakthrough claim.

## Primary references

- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*,
  <https://arxiv.org/abs/2512.04258v2>.
- Kasliwal, Polak, and Sharma, *3SUM in Preprocessed Universes: Faster and
  Simpler*, <https://arxiv.org/abs/2410.16784v3>.
- Kirkpatrick, Kuszmaul, Mathialagan, and Vassilevska Williams,
  *Preprocessed 3SUM for Unknown Universes with Subquadratic Space*,
  <https://arxiv.org/abs/2602.11363v1>.
- Maurer, Portmann, and Zhu, *Unifying Generic Group Models*,
  <https://eprint.iacr.org/2020/996>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*, <https://eprint.iacr.org/2004/031>.
- Kedlaya and Umans, *Fast Polynomial Factorization and Modular Composition*,
  <https://users.cms.caltech.edu/~umans/papers/KU08-final.pdf>.
