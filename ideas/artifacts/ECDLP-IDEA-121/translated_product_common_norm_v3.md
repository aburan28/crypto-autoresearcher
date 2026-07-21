# IDEA-121 Translated-Product Common-Norm Gate V3

Status: `SCOPED_NEGATIVE_COMPOSED_SUM_AND_AUTOCORRELATION_GRAMMAR__SOURCE_JET_IDENTITY_POSITIVE__SPECIALIZED_LOCATOR_OPEN`

This theorem-only receipt executes the P1553 equation (13) handoff under the
existing P1513/`ECDLP-IDEA-121` owner. It derives the exact translated-product
and source-jet identities, then charges the standard composed-sum, quotient,
Newton-series, logarithmic-derivative, truncated-resultant, product-tree,
low-rank-update, and preprocessed-3SUM realizations.

The identities are positive algebraic facts. They are not a common-factor
locator, relation campaign, target descent, scalar recovery, Shoup-bound
improvement, or ECDLP breakthrough. No contract, solver, fixture, timing run, or
toy relation campaign is authorized or executed.

## 1. Frozen interface and cost rectangle

Let `E/F_p` contain the public prime-order subgroup `<P>` of order
`N=p^(1+o(1))`, and put

```text
B = N^(1/5),
M = B^2.
```

Use five pairwise-disjoint, signed, coloured factor decks `A_1,...,A_5`,
each of size `Theta(B)`, and either a known-log target deck `T` of size
`Theta(B)` or one fresh masked target `Q+[r]P`. Signs are represented by actual
points, not inferred from x-coordinates after the fact.

For the relation campaign form three source-labelled endpoint multisets

```text
X = {R_t - A_(1,k) : t,k},
Y = {A_(2,i) + A_(3,j) : i,j},
Z = {A_(4,a) + A_(5,b) : a,b}.                 (1)
```

Each multiset has `Theta(M)=Theta(B^2)` occurrences before endpoint
coalescing. A six-list row is exactly

```text
x + y + z = O,  x in X, y in Y, z in Z.         (2)
```

The favorable P1552 rectangle permits

```text
target-independent setup/state       <= B^(9/4+o(1)),
B-target relation campaign           <= B^(9/4+o(1)),
one fresh scalar-blind target query   <= B^(5/4+o(1)). (3)
```

The output is not an endpoint bit. It must include the target, all five signed
factor occurrences, colours, charts, repetitions, multiplicity, and exact
elliptic replay. Duplicate rows must be removed before rank is credited.

## 2. Exact translated-product identity

First use the additive-line normal form from P1553 equation (13). For a
multiset `D`, let

```text
f_D(U) = product_(d in D) (U-d),
```

with one factor per labelled occurrence. Define the composed-sum polynomial

```text
C_(Y,Z)(U)
  = Res_V(f_Y(V), (-1)^M f_Z(-U-V))
  = product_(y in Y,z in Z) (U+y+z).            (4)
```

Then

```text
G_X(U) = gcd(f_X(U), C_(Y,Z)(U))                (5)
```

has support exactly on the endpoints participating in (2).

The coordinate-free elliptic version is equally exact. Regard `X,Y,Z` as
effective occurrence divisors and let `mu:E x E -> E` be addition. Define

```text
S_(Y,Z) = [-1]_* mu_*(Y x Z),
I_X     = gcd_divisor(X,S_(Y,Z)).                (5e)
```

Here `gcd_divisor` takes the coefficientwise minimum of two effective
divisors. Its support is exactly (2). In a frozen complete addition chart,
local equations for (5e) give (4)-(5); P1510's source-marked
Semaev-resultant leaves provide an x-coordinate representation with every sign
and return branch retained. This does not claim that one global affine
coordinate linearizes elliptic addition or that all the sections live in one
unidentified trivial line bundle. Equation (4) is a normal form for the support
and multiplicity calculation, not a new global group coordinate.

### Multiplicity

Let `m_X(x),m_Y(y),m_Z(z)` be occurrence multiplicities. The order of (4) at
`U=x` is

```text
b_x = sum_(y+z=-x) m_Y(y)*m_Z(z),               (6)
```

and the ordinary gcd records only

```text
ord_x(G_X) = min(m_X(x), b_x).                  (7)
```

Thus a squarefree gcd can prove endpoint participation while erasing the number
of source rows above that endpoint. Multiplicity is a separate mandatory output;
it cannot be reconstructed from the exponent in (5) when `m_X(x)<b_x`.

## 3. Exact source-jet identity

Assign public injective codes `c_X,c_Y,c_Z` to labelled pair occurrences. One
base-field element suffices for each `Theta(B^2)` catalogue because
`p=B^(5+o(1))`; a fixed number of independent code channels may instead be
used to make colour, sign, chart, and both indices explicit.

The explicit `B^2` pair decks permit one occurrence-local equation for every
signed pair endpoint; constructing these equations is allowed setup, not the
missing locator. For every translated-product occurrence leaf
`L_(y,z)(U)` in the chosen complete chart, form the source-marked factor

```text
L_(y,z)(U) + s_0 + c_Y(y)*s_Y + c_Z(z)*s_Z.     (8)
```

Let `C_(Y,Z)(U;s)` be the product of (8), with occurrence multiplicity. At a
root `x`, its first nonzero local Hasse form is

```text
J_x(s_0,s_Y,s_Z)
  = u_x * product_(y+z=-x)
      (s_0 + c_Y(y)*s_Y + c_Z(z)*s_Z)
          ^(m_Y(y)*m_Z(z)),                     (9)
```

where `u_x` is the product of the nonvanishing unmarked leaves and is a unit.
If one x-coordinate leaf folds several signed endpoint branches, the frozen
complete-chart decomposition is applied before (8); otherwise the marker would
identify a folded branch rather than an actual signed point.
For a simple source fibre, (9) gives the exact ratios

```text
(partial_(s_Y) C)/(partial_(s_0) C) = c_Y(y),
(partial_(s_Z) C)/(partial_(s_0) C) = c_Z(z).   (10)
```

For a multiple fibre, factoring the leading homogeneous form (9) returns the
multiset of paired source codes and multiplicities. The analogous marked local
form of `f_X` returns the target/factor-start occurrence. Complete addition
charts and Hasse, rather than ordinary, derivatives retain tangent, vertical,
return, and nonreduced cases.

Equations (6)-(10) are the positive result of this receipt: the translated
product has an exact multiplicity and signed-source inverse *if the locator
also returns the required local marked form*. They do not show how to locate
the relevant roots within (3).

## 4. Relation to the original P1513 circuit

P1513 keeps one shared circuit

```text
H(U,W) = product_(i,j) P_(i,j)(U,W)             (11)
```

with `B^2` constant-degree leaves and selector polynomials `T,F` of degree
`B`. Its two norms have degree `B^3`, while their expected common factor has
degree `B`.

The three-pair normal form (4) and the two-norm form (11) encode the same
six-list endpoint relation after regrouping the target/factor-start pair and
the two transition pairs. They expose different standard costs:

```text
full pair-pair composed sum (4)       degree M^2 = B^4,
each explicit P1513 selector norm     degree B^3,
expected common output                degree B.
```

Consequently, expanding (4) is worse than the already closed dense P1513
norms. A valid V3 algorithm would have to use the nested `B x B` source
structure without producing either the `B^4` composed sum or a `B^3` norm.

## 5. Full composed-sum and quotient routes

### 5.1 Explicit composed sum

Bostan, Flajolet, Salvy, and Schost compute the composed sum of degree-`m`
and degree-`n` polynomials in quasi-linear time in its output degree `D=mn`.
Here `m=n=M`, so the represented output and the near-optimal algorithm both
have size/work

```text
D = M^2 = B^4.                                  (12)
```

Fast computation in the size of the full special resultant is not
output-sensitive in the `Theta(B)` intersection.

### 5.2 Resultant modulo the query divisor

Avoiding (12) by asking directly for `C_(Y,Z) mod f_X` places the computation
in

```text
A_X tensor A_Y
  = K[U,V]/(f_X(U),f_Y(V)),
dim_K(A_X tensor A_Y) = M^2 = B^4.              (13)
```

The element whose norm is required is `f_Z(-U-V)`. Standard quotient,
triangular-set, multiplication-matrix, norm, determinant, half-gcd over the
coefficient algebra, primitive-element, and power-projection realizations all
represent (13), or an equivalent number of base-field coordinates. A change
of basis does not reduce the dimension.

Moroz-Schost truncated resultants cost soft-`O(kd)` for truncation order `k`
and input degree `d`. Setting both to `M` gives `M^2=B^4`; truncating at a fixed
point also does not locate the unknown roots of `f_X`.

**Scoped decision:** the explicit composed-sum and standard query-quotient
routes fail before source output, rank, or descent.

## 6. Newton-series and logarithmic-derivative routes

The Newton representation makes the source of (12) transparent. A monic
degree-`D` composed sum is determined by its first `D` power sums (under the
present large-characteristic regime), and the published near-optimal algorithm
computes that represented result. Computing only `Theta(M)` moments is cheap,
but does not determine its intersection with an arbitrary degree-`M` query
divisor.

The following generic interface control is exact. Let `D=M^2`, assume `M|D`,
and set

```text
f_X(U) = U^M-1,
R_0(U) = U^D-1,
R_1(U) = U^D.                                   (14)
```

`R_0` and `R_1` have identical power sums through order `D-1`, hence certainly
through order `M`, but

```text
gcd(f_X,R_0)=f_X,
gcd(f_X,R_1)=1.                                 (15)
```

This is a mutation control for a generic moment interface, not a claim that
both polynomials in (14) occur as P1513 elliptic norms. It proves that a
proposal using only a short prefix of generic Newton data needs an additional
special-family theorem.

Logarithmic derivatives do not supply that theorem. For squarefree norms
`N_T,N_F`, common roots are the double poles of

```text
(N_T'/N_T)*(N_F'/N_F),                          (16)
```

while roots belonging to only one norm remain simple poles. This is an exact
pole-order characterization. However, extracting the repeated-pole denominator
from a generic rational function requires the represented union denominator or
enough Pade/moment data to determine it. In (14), `R_0'/R_0` and `R_1'/R_1`
also agree to high order at infinity while (15) differs. Computing a log
derivative modulo `f_X` requires inversion of the same element whose
noninvertibility/common factor is being sought.

**Scoped decision:** short Newton prefixes, short log-derivative expansions,
and repeated-pole tests are exact diagnostics but not locators in the admitted
generic interfaces.

## 7. Product trees, pairwise gcds, and correlation indexing

For specialized norm factors `h_t(W)=H(t,W)` and `h_k(W)=H(k,W)`, one always
has the support identity

```text
rad gcd(product_t h_t, product_k h_k)
  = rad product_(t,k) gcd(h_t,h_k).              (17)
```

Without the radical, the right side overcounts a factor shared by several
members of either family. Equation (17) exposes multiplicity rather than
removing work: there are `B^2` outer pairs, and each pair gcd is itself the
intersection of two `B^2`-leaf translated endpoint products.

Using the explicit pair decks, (2) is a cross-correlation query:

```text
for x in X, report Y intersect (-x-Z).           (18)
```

The campaign has `|X|=|Y|=|Z|=M`. Listing `Y+Z` costs `M^2=B^4` state/work;
scanning one explicit deck for every `x` also costs `M^2=B^4`. Random generic
collision search reaches the separately preserved `B^(5/2)` first-hit boundary
but does not output the `Theta(B)` independent campaign rows inside
`B^(9/4)`.

At list size `n=M=B^2`, the available state `B^(9/4)=n^(9/8)` lies below the
`n^(3/2)` to `n^(7/4)` range in which Dinur-Golovnev's improved
`T*S=n^(5/2)` 3SUM-indexing tradeoff applies. The current unknown-universe and
preprocessed-universe 3SUM algorithms use `n^2=B^4` preprocessing, already
outside (3). These are positive algorithm comparisons, not lower bounds against
the special elliptic family.

**Scoped decision:** standard product/remainder trees and current correlation
indexing do not meet the campaign rectangle.

## 8. Natural low-rank target updates are full rank

The Woodbury control can be made exact in the natural endpoint quotient. Let

```text
A_Y = K[V]/(f_Y(V))
```

on the squarefree control. Over a splitting field, multiplication by a target-
translated product is diagonal, with entries `q(y+c)` for `y in Y`. Therefore

```text
rank(M_(q(V+c))-M_(q(V)))
  = number of y in Y with q(y+c) != q(y).        (19)
```

For a generic nonzero translation and generic deck this is `M=B^2`, not
bounded rank. Restricting to a source-faithful factor-deck quotient does not
turn (19) into a rank-one update. An exceptional low-rank identity remains
logically possible, but it must be proved from the elliptic product family and
must retain the source inverse; Woodbury cannot assume it.

**Scoped decision:** the natural quotient/multiplication-matrix target update
fails the `B^(5/4)` online cap before inversion or back-substitution.

## 9. Source recovery is not free after an endpoint gcd

Suppose a locator returns only the degree-`Theta(B)` campaign factor `G_X`.
There are two standard ways to recover `Y,Z` sources:

1. For each of `Theta(B)` roots, scan one `M=B^2` pair deck and hash into the
   other. This costs `B*M=B^3`.
2. Compute the marked norm (8) modulo `G_X`. The standard quotient contains
   `deg(G_X)*deg(f_Y)=B*M=B^3` base-field coordinates.

Thus the direct equation-(13) representation loses the favorable conditional
decoder unless the unknown locator carries (9) during its own recurrence. This
does not contradict P1513 V2's narrower observation that a source-aware
algorithm operating directly on both original `B^2`-leaf transition circuits
might decode in a quadratic-sized target/start quotient once `G` is supplied.
It shows that an unlabeled endpoint gcd from the regrouped pair divisors is not
such an algorithm.

Multiple source fibres strengthen the requirement. The gcd exponent in (7)
can cap `b_x`, ordinary first derivatives vanish for `b_x>1`, and a complete
reporter must return and factor the first nonzero Hasse form (9), not silently
keep one row.

## 10. Separate fresh-target recurrence

For one fresh masked target, replace the campaign deck `X` by

```text
X_Q = {Q+[r]P-A_(1,k) : k},  |X_Q|=Theta(B).    (20)
```

The expected number of five-source decompositions is constant. The standard
translated-product routes have the following online costs after retaining only
the permitted `B^(9/4)` target-independent state:

```text
scan Y against Z for all x in X_Q       B*M = B^3,
norm in K[U,V]/(f_(X_Q),f_Y)            B*M = B^3,
materialize the source correlation Y+Z  M^2 = B^4 setup,
natural target-shift operator            rank M = B^2.
```

All exceed `B^(5/4)`. Running a hypothetical `B^(9/4)` batch locator again
with `Q` and `B-1` filler targets is also not the required online recurrence;
it charges `B^(9/4)` to one fresh target and supplies no target-independent
query bound.

A valid successor must therefore provide a target-independent data structure
of size at most `B^(9/4)` and an exact scalar-blind query recurrence at most
`B^(5/4)`, including source jets, misses, multiplicity, and verification. No
screened route does so.

## 11. Circuit-GCD controls and exact scope

Generic constant-depth and straight-line-program GCD theorems do not give the
required exponent. They either consume dense coefficient/degree parameters or
assume circuits for the two degree-`B^3` norms, whose construction is the
missing conversion.

Qiu, Cao, Huang, Feng, and Gao prove that a universally output-sensitive sparse
univariate GCD algorithm over finite fields, polynomial in input sparsity,
output sparsity, logarithmic degree, and field size, would imply `NP subseteq
BPP`. Their result concerns arbitrary sparse monomial inputs, not the fixed
elliptic translated-product family, so it is not a lower bound here. It does
rule out treating "small input description plus small gcd" as a generic
published algorithm without a special-family recurrence.

This receipt does **not** rule out:

1. a specialized product-circuit common-factor algorithm near-linear in the
   `B^2` leaves plus the `B` output;
2. a value-sensitive elliptic circuit using nonzero determinant data rather
   than only endpoint support;
3. an elliptic composed-sum remainder theorem that avoids the tensor dimension
   (13) and proves its own coefficient and bit recurrence;
4. a nonhomomorphic list-specific data structure outside current 3SUM-indexing
   models;
5. a source-preserving arithmetic, Boolean, or cell-probe algorithm outside
   the frozen grammar; or
6. a special factor-deck family with generic-prime applicability, full factor
   rank, exact source replay, and blind descent.

Any such result is a mechanism-new theorem. It cannot cite the identities
above as its runtime.

## 12. Complete exponent receipt

| Object or route | Work/state in `B` | Decision |
|---|---:|---|
| three explicit source-labelled pair decks | `B^2` | fits setup/state |
| expected campaign endpoint output | `B` | output fits |
| P1553 generic first hit | `B^(5/2)` | rho boundary; misses cap |
| P1513 dense selector norm | `B^3` | fails |
| post-hoc source recovery from endpoint `G` | `B^3` | fails |
| fresh-target direct scan or marked quotient | `B^3` | fails query |
| full composed-sum/difference divisor | `B^4` | fails |
| standard query-quotient algebra | `B^4` | fails |
| natural target-shift update rank | `B^2` | fails query |
| required relation campaign | `B^(9/4)` | unsupplied |
| required fresh target | `B^(5/4)` | unsupplied |

The locator fails before independent relation rank, factor-log solving, blind
descent, output ambiguity, and scalar verification can be credited. Pollard rho
remains the better complete algorithm.

## 13. Decision

```text
translated-product support identity:          pass
exact occurrence multiplicity formula:        pass
simple and multiple-fibre source-jet identity: pass
composed-sum output route inside rectangle:   absent
query-quotient route inside rectangle:        absent
short Newton/log-derivative locator:           absent
current correlation/indexing route:            absent
bounded-rank natural target update:             false generically
post-hoc exact source unranking inside cap:     absent
separate B^(5/4) masked-target recurrence:      absent
complete lambda,mu<=0.45 path:                  absent
scoped disposition:                             terminal inconclusive
breakthrough:                                   none
```

The standard translated-product/composed-sum grammar is closed in its stated
representation models. P1513/`ECDLP-IDEA-121` remains deferred only for the
explicit unrestricted exceptions in Section 11; no new P1554 candidate is
created.

## 14. Exactly one next executable action

Preserve this hash-bound scoped negative and advance the semantically distinct
`ECDLP-IDEA-133` target-local apolar/projector theorem gate already named by
P1513. Require one coefficient-complete recurrence for the sparse target
projector and its source jets inside `B^(9/4)/B^(5/4)`, or a versioned scoped
obstruction. Do not create a contract, solver, fixture, timing run, or toy
relation campaign before theorem review.

## Primary references checked

- Bostan, Flajolet, Salvy, and Schost, *Fast Computation of Special
  Resultants*: <https://cs.uwaterloo.ca/~eschost/publications/BoFlSaSc05.pdf>.
- Moroz and Schost, *A Fast Algorithm for Computing the Truncated Resultant*:
  <https://arxiv.org/abs/1609.04259>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*:
  <https://arxiv.org/abs/2512.04258>.
- Kirkpatrick, Kuszmaul, Mathialagan, and Vassilevska Williams,
  *Preprocessed 3SUM for Unknown Universes with Subquadratic Space*:
  <https://arxiv.org/abs/2602.11363>.
- Kasliwal, Polak, and Sharma, *3SUM in Preprocessed Universes: Faster and
  Simpler*: <https://arxiv.org/abs/2410.16784>.
- Andrews and Wigderson, *Constant-Depth Arithmetic Circuits for Linear
  Algebra Problems*: <https://arxiv.org/abs/2404.10839>.
- Bhattacharjee, Kumar, Rai, Ramanathan, Saptharishi, and Saraf,
  *Constant-depth circuits for polynomial GCD over any characteristic*:
  <https://arxiv.org/abs/2506.23220>.
- Qiu, Cao, Huang, Feng, and Gao, *Output-sensitive Sparse Polynomial GCD over
  Finite Fields is NP-hard*: <https://arxiv.org/abs/2606.12144>.
- Kedlaya and Umans, *Fast Polynomial Factorization and Modular Composition*:
  <https://doi.org/10.1137/08073408X>.
- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.

These references supply the positive composed-sum, truncated-resultant,
circuit-GCD, sparse-GCD, and preprocessing controls. None supplies the
P1513 source-labelled product-circuit locator or a below-rho generic-prime
ECDLP algorithm.
