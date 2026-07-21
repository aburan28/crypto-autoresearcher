# Target-label common-factor theorem gate

Task: `TASK-20260718-P1553-ZR-P1`
Role: Idea Generator
Date: 2026-07-18
Verdict: **scoped negative for the named represented-algebra routes; one compact
representation-sensitive exception remains open**

This is theorem and primary-literature analysis only. No experiment, solver,
fixture, timing run, relation campaign, contract, P1554 allocation, shared-file
edit, official status change, Shoup-bound claim, or breakthrough claim is made.

## 1. Terminal statement

Let `n=Theta(B^2)` be each restricted pair-divisor degree and let
`m=Theta(B)` be the number of selected fifth occurrences. There is an exact,
coefficient-complete definition

```text
r_R(T) in K[T]/g_I(T),
z_R(T)=gcd(g_I(T),r_R(T)),
```

over a fixed cubic extension `K/F_p`. Componentwise,
`r_R(t_a)=0` exactly when the labelled fifth occurrence `a` extends to at
least one selected labelled pair-pair relation. Thus

```text
z_R(T)=product_(a extendible)(T-t_a).
```

Once the `m` coefficients of `r_R mod g_I` are represented, fast univariate
gcd, factor-to-label extraction, and fifth-label output cost
`B^(1+o(1))` field or word operations and `B^(1+o(1))` workspace. That is the
easy downstream operation.

No named standard route constructs the input `r_R mod g_I` inside the frozen
online cap. A degree-`n` translated pair polynomial over the `m`-dimensional
split label algebra has `n*m=B^3` base-field coordinates. Componentwise
resultants, quotient-ring resultants, multipoint and remainder trees,
transposed or truncated resultant evaluation, structured Sylvester methods,
modular composition, power projection, half-gcd, regular subresultants, and
provenance forests either construct those coordinates, perform `m` degree-`n`
tests, or assume the residue/common factor before their fast step. Their
standard online work is `B^(3+o(1))`; even a streamed component needs
`B^(2+o(1))` temporary polynomial state.

This is a representation and input-construction obstruction, not an
arithmetic-circuit, data-structure, word-RAM, cell-probe, coordinate, generic
group, Shoup, or ECDLP lower bound. In particular, a gauge-invariant nonlinear
or variable-coefficient orbit-product locator for the favorable mutation in
Section 7 remains open.

## 2. Frozen complete elliptic model

Assume `p>3` and fix the signed projective Weierstrass model

```text
E/F_p: Y^2 Z = X^3 + a_E X Z^2 + b_E Z^3,
4 a_E^3 + 27 b_E^2 != 0,
O=[0:1:0].
```

The sign of a finite occurrence is its actual `Y` coordinate. It is never
replaced by an x-coordinate sign choice.

### 2.1 Charts, branch selectors, and saturation

Every rational point is normalized in exactly one of these charts:

```text
C_inf: Z=0, containing only O;
C_aff: Z!=0, normalized as [x:y:1].
```

Negation is `[X:Y:Z] -> [X:-Y:Z]`. Addition of normalized finite points uses
the following ordered cover; identity branches are tested first.

```text
P=O:                         P+Q=Q
Q=O:                         P+Q=P
x_P=x_Q and y_P+y_Q=0:       P+Q=O                 (vertical)
P=Q and 2y_P!=0:             lambda=(3x_P^2+a_E)/(2y_P)  (tangent)
x_P!=x_Q:                    lambda=(y_Q-y_P)/(x_Q-x_P)  (secant)
x_3=lambda^2-x_P-x_Q,        y_3=lambda(x_P-x_3)-y_P.
```

The case `P=Q`, `y_P=0` is the vertical branch and returns `O`. The tangent
graph is saturated by `2y_P`; the secant graph is saturated by `x_Q-x_P`;
the finite graph is saturated by `Z_P Z_Q`; and identity/vertical components
are retained separately. Equivalently, over every split coefficient algebra
the exact selectors use

```text
nz(d)=d^(p-1),       inv0(d)=d^(p-2),
```

For a component value in `F_p`, put `eq(d)=1-nz(d)`. With `o_P,o_Q` the
normalized infinity flags, the following disjoint priority masks are
coefficient-complete in the split algebra:

```text
b_Pinf = o_P,
b_Qinf = (1-o_P)o_Q,
f      = (1-o_P)(1-o_Q),
e_x    = eq(x_P-x_Q),
e_y    = eq(y_P-y_Q),
e_neg  = eq(y_P+y_Q),
b_vert = f e_x e_neg,
b_tan  = f e_x e_y (1-e_neg),
b_sec  = f (1-e_x).
```

On curve points in characteristic greater than three these masks sum to one:
equal finite x-coordinates have equal or opposite y-coordinates, and the
order-two case belongs to `b_vert`. Multiply each branch output and its output
infinity flag by its mask, using `inv0(2y_P)` only on `b_tan` and
`inv0(x_Q-x_P)` only on `b_sec`. Sequential composition gives the same exact
selectors for `R-A_I(T)-v`. Thus all coordinate coefficients exist in `A_I`;
this semantic coefficient completeness does not assert that the dense
target-dependent coefficient vector is cheap to construct.

Denominator clearing is never allowed to create a component. The branches
overlap only where the projective outputs agree. This supplies a finite
complete chart for all identity, tangent, vertical, and infinity cases.

### 2.2 A sign-complete univariate point key

Fix an irreducible cubic `h(S) in F_p[S]`, put

```text
K=F_p[theta]/h(theta),
kappa([x:y:1])=x+theta*y,
kappa(O)=theta^2.
```

The basis `1,theta,theta^2` proves that `kappa` is injective on `E(F_p)`:
two finite keys agree only when both signed coordinates agree, and no finite
key equals `theta^2`. Extension degree three is constant, so one `K` element
costs `Theta(log p)=B^o(1)` bits and a constant number of base-field words.

This key is an exact coefficient representation, not an additive quotient of
the point group. Group addition is completed in the projective chart first;
only then is `kappa` applied.

## 3. Occurrences, multiplicities, and dyadic restrictions

Each coloured source deck `F_i` contains signed point occurrences
`(i,label,P)`. Labels remain distinct when points coincide. A balanced dyadic
tree is fixed on each source order. An admitted `I_i` is one canonical node;
an interval or other admitted restriction may be a disjoint union of
`O(log B)` nodes, with every node-pair combination charged.

For node restrictions `I_1,I_2,I_3,I_4`, define ordered pair occurrences

```text
D_12={(alpha_1,alpha_2,u=P_alpha1+P_alpha2)},
D_34={(alpha_3,alpha_4,v=P_alpha3+P_alpha4)}.
```

Every occurrence keeps its ordered source labels, complete addition branch,
and dyadic ancestors. Each leaf pair belongs to `O(log^2 B)` ancestor-node
pairs. Pair construction, endpoint keys, monic product-polynomial
coefficients, labels, and backpointers therefore cost

```text
B^(2+o(1)) word operations,
B^(2+o(1)) retained words,
B^(2+o(1)) bits after suppressing log(p) and log(B) factors.
```

If several pair occurrences have endpoint `u`, write their number as
`m_12(u)` and include `(U-kappa(u))^m_12(u)` in the pair polynomial. The same
rule defines `m_34(v)`. Repeated support is therefore a nonreduced effective
pair divisor, while the occurrence sidecar remains reduced and fully labelled.

The fifth deck has distinct public occurrence labels `t_a in F_p`, even when
two occurrences have the same point. Since `B<p`, define the squarefree label
polynomial and split algebra

```text
g_I(T)=product_(a in I_5)(T-t_a),
A_I=K[T]/g_I(T)=Map(I_5,K),       dim_K(A_I)=m.
```

The fifth product tree costs `B^(1+o(1))` setup and state. The fresh target
`R` is absent from every preprocessed coefficient, seed, table, and pointer.

## 4. Exact definitions of r_R and z_R

Let `A_I(T)` denote the branch-separated projective coordinate interpolants
whose component at `t_a` is the signed point `a`. For every `v in D_34`, use
the complete chart of Section 2 to form, componentwise in `A_I`,

```text
Q_(R,v)(T)=R-A_I(T)-v.
```

Define monic polynomials

```text
H_12(U)=product_(pair occurrences in D_12)(U-kappa(u)) in K[U],

H_34^R(U,T)=product_(pair occurrences in D_34)
             (U-kappa(Q_(R,v)(T))) in A_I[U].
```

Their degrees in `U` are `n_12,n_34<=Theta(B^2)`. The second polynomial has
`(n_34+1)m=Theta(B^3)` base-field coordinates in the standard represented
quotient basis. Now define

```text
r_R(T)=Res_U(H_12(U),H_34^R(U,T)) mod g_I(T) in A_I,
z_R(T)=monic gcd_K[T](g_I(T), representative_(degree<m)(r_R(T))).
```

### Theorem 1: exact component meaning

For every selected fifth occurrence `a`, specialization at `T=t_a` commutes
with the Sylvester determinant because `A_I` is a squarefree split algebra.
Both specialized input polynomials are monic, hence

```text
r_R(t_a)
 = product_(u occurrence in D_12, v occurrence in D_34)
   (kappa(u)-kappa(R-a-v)),
```

up to the fixed harmless resultant sign. Since `K` is a field and `kappa` is
injective,

```text
r_R(t_a)=0
iff exists labelled pair occurrences u,v with u+v+a=R.
```

There is no trace or moment cancellation in this product. The complete group
law makes the biconditional valid when an addition is tangent, vertical,
passes through `O`, or uses an identity branch.

### Theorem 2: exact common factor

Because `g_I` is squarefree with roots exactly the occurrence labels,

```text
z_R(T)=product_(a in I_5: r_R(t_a)=0)(T-t_a).
```

Thus `z_R=1` is the exact no-relation unit certificate, `z_R=g_I` means every
fifth occurrence extends, and every intermediate monic factor lists exactly
the extendible fifth labels.

For one label `a`, the number of labelled pair-pair rows is

```text
c_a=sum_(u+v+a=R) m_12(u)m_34(v).
```

The pair-polynomial gcd at that component retains root multiplicity
`min(m_12(u),m_34(R-a-u))`; the row count uses the product above. The
squarefree `z_R` deliberately records the fifth occurrence once and does not
claim to encode `c_a`. Repeated roots and nonreduced pair divisors cannot
create or erase a fifth factor: resultant vanishing records nonempty common
support, while occurrence labels and restricted replay recover an actual row.

### 4.1 Coordinate-free Fitting-ideal cross-check

The same support can be defined without the affine key. Over
`S=Spec(A_I)`, let `mathcal D_12` be the constant finite effective pair divisor
on `E_K x S`, and let `mathcal D_34^R` be the branch-complete translated pair
divisor whose component at `t_a` is `R-a-D_34`. For the finite projection
`pi:E_K x S -> S`, set

```text
M_R = pi_* O_(mathcal D_12 intersection mathcal D_34^R)
    = pi_* O_(E_K x S)/(I_12+I_34^R).
```

This scheme-theoretic intersection retains tangency and nonreduced length.
For every split component `a`, `(M_R)_a` is zero exactly when the two effective
divisors are disjoint and is a nonzero finite-dimensional `K`-vector space
exactly when `a` extends to a relation. The support theorem for Fitting ideals
therefore gives

```text
V(Fitt_0(M_R)) = Supp(M_R) = {extendible fifth labels}.
```

In `A_I=product_a K`, the component of `Fitt_0(M_R)` is the unit ideal off
that support and the zero ideal on it. Hence it is the principal ideal
generated by `z_R mod g_I`; equivalently, any element with the same component
zero set has gcd `z_R` with `g_I`. The resultant element `r_R` is one such
element. This independently checks the support semantics and explains why
intersection multiplicity cannot create a false fifth label.

The formulation does not improve complexity by itself. A standard finite
presentation of `M_R`, a Sylvester presentation after a chart, or its full
Fitting matrix has degree/row scale `n` over the width-`m` algebra `A_I` and
therefore exposes `n*m=B^3` base-field coordinates. A compact presentation
whose target-dependent Fitting generator is constructed below that width is
exactly the unproved representation-sensitive exception, not a consequence of
the support theorem.

## 5. Constructor versus output extraction

Put `n=Theta(B^2)` and `m=Theta(B)`. The following two operations are not
interchangeable.

**Given the represented residue.** If all `m` coefficients of
`r_R mod g_I` are supplied, half-gcd or another fast polynomial-gcd algorithm
computes `z_R` in

```text
B^(1+o(1)) K-operations,
B^(1+o(1)) workspace,
B^(1+o(1)) bit operations after log(p) suppression.
```

Gcds with the fifth subproduct tree identify labels at the same exponent.

**Constructing the residue.** The standard quotient input
`H_34^R in A_I[U]` has `n*m=B^3` base-field slots. Alternatively, split
evaluation performs `m` degree-`n` translated resultant tests, again
`n*m=B^3` work. Output degree `m`, a fast final gcd, or an output-sensitive
factor routine does not pay this input-construction bill.

## 6. Exhaustion of named represented-algebra routes

All exponents below suppress polylogarithmic factors. `P,S,Q,W` mean
preprocessing work, retained state, total online work, and peak online
workspace in base-field words. A word has `Theta(log p)` bits, labels and
pointers have `O(log B)` bits, and the constant extension `K/F_p` changes no
exponent.

| Route | Coefficient ring, bidegree, and represented input | `P/S/Q/W` in B | No-relation behavior and gate |
|---|---|---|---|
| Componentwise resultants | `m` pairs of monic degree-`n` polynomials in `K[U]` | `2/2/3/2` | All `m` resultants are nonzero. Streaming avoids `B^3` memory but one degree-`B^2` polynomial already exceeds `W=B^(5/4)`. |
| Quotient-ring resultant | One degree-`n` polynomial over `A_I`, represented width `n*m=B^3` | `2/2/3/3` explicitly; recomputation can lower memory only by repeating work | The resultant is a unit in `A_I`; regular computation must produce or traverse all coefficient blocks. |
| Multipoint/remainder trees | A supplied dense shift eliminant has additive-line degree `n_12*n_34=Theta(B^4)`; a supplied residue has degree `<m` | `2/2/4/4` for the dense eliminant, or `2/2/1/1` only after `r_R` is supplied | Borodin--Moenck/Bernstein trees accelerate reduction or evaluation of represented coefficients. They do not create the target-shift eliminant or its residue from the pair product trees. Evaluating `m` degree-`n` tests is `B^3`. |
| Transposed or truncated resultant evaluation | Moroz--Schost type input with truncation/output width `k=m` and degree bound `d=n` | `2/2/3/2` even under favorable workspace | The primary bound is soft-`O(kd)=B^3`. A fixed local truncation does not locate arbitrary fifth labels. Transposition preserves the `kd` domain/codomain width and is linear; common-factor location is nonlinear. |
| Structured Sylvester displacement | A `2n` Sylvester matrix over `A_I`, or a direct sum of `m` scalar Sylvester matrices | `2/2/3/(2..3)` | Scalar Sylvester matrices have constant Toeplitz-like displacement rank, but the split direct sum has `m` blocks and `Theta(nm)=B^3` generator coordinates. Constant block rank over `A_I` still has `m` base coordinates per block. |
| Addition-law/Cauchy displacement | Secant denominators form Cauchy-like `n by m` leaf arrays; tangent, vertical, identity, and infinity selectors are separate saturated branches | `2/2/3/(2..3)` in the represented route | A fast supplied Cauchy matrix-vector product does not form the elementary-symmetric coefficient blocks or their nonlinear resultant. The complete translated leaf array has `n*m=B^3` entries. Branch-selector incidence and source labels cannot be discarded. |
| Modular composition and power projection | Degree `n` over `A_I`, or a triangular/flattened algebra of dimension `n*m=B^3` | `2/2/3/3` | Kedlaya--Umans over the finite ring retains `log|A_I|=Theta(m log p)`; triangular and primitive-element forms retain dimension `nm`. Power projection is the transpose of a linear map and does not compute the nonlinear gcd. |
| Half-gcd and regular subresultants | `m` degree-`n` component pairs, or a supplied degree-`m` residue pair | `2/2/3/2` before `r_R`; `2/2/1/1` after it | In a no-relation query every component resultant is a unit, so dynamic evaluation has no zero divisor on which to split. Half-gcd is fast only after its polynomial inputs exist. |
| Subresultant/provenance forest | Product/remainder tree plus live gcd factors and occurrence backpointers | Root construction remains `Q=B^3`; propagation is output-sensitive only after the root factor exists | IDEA-063/P1428 already owns this operation. Propagation can recover supplied row/root incidence; it does not construct `r_R`, and high overlap can restore explicit incidence output. |
| Generic compact-circuit factor extraction | Product-tree circuit size `B^(2+o(1))`, hidden shift-resultant degree up to `B^4`, desired factor degree `B` | No proved `Q,W` inside the rectangle | Standard dense and straight-line reductions depend on represented degree or conversion. A genuinely output-sensitive nonlinear common-factor algorithm on the compact complete-chart circuit remains outside the negative. |

### 6.1 The displacement and target-update calculation

In the split basis of `A_I`, multiplication by a represented coefficient
`c(T)` is

```text
diag(c(t_a): a in I_5).
```

For two targets, the update difference has rank exactly the number of labels
on which the coefficient changes. For a generic coefficient and generic fresh
target shift this is `m=Theta(B)`, not `O(1)`. There are `Theta(n)` represented
coefficient blocks. Therefore the natural split/block-Sylvester or resolvent
update exposes `Theta(nm)=B^3` changed scalar coordinates. This proves the
rank statement for that frozen represented update.

The input family is generated by only `B^2` pair leaves and the fresh target,
so this is not a lower bound against an algorithm acting on the unexpanded
generator. It shows precisely why a standard displacement or Woodbury theorem
for a supplied matrix cannot be credited as that algorithm. At a relation hit
the relevant resultant or Schur object is singular as well, so inverse
maintenance still needs a separate exact factor and source backsolve.

## 7. Favorable fifth-orbit mutation

Freeze only the fifth coloured deck as

```text
F_5={A_j=A_0+[j]T: 0<=j<B},
```

with public `A_0,T` and occurrence label `t_j`. Leave `F_1,...,F_4` generic.
The online start `R-A_0` remains fresh; preprocessing may contain `A_0,T` and
target-independent net constants but no value depending on `R`.

This mutation does not make all decks small-doubling. Under the random-endpoint
heuristic, the generic four-deck sum has `B^4` labelled tuples and each of the
`B` orbit shifts has expected mass `B^4/N=1/B`, leaving constant expected
target coverage after summing the shifts. Correlation, useful relation density,
and row rank are unproved and remain `heuristic` and `model-bound`. Structuring
all five decks would instead collapse endpoint support and restore the known
blind-target density failure; that mutation is not admitted here.

The orbit gives the divisor recurrence

```text
D_(j+1)=tau_(-T)(D_j),
D_j=(tau_(R-A_0-[j]T) o [-1])_*D_34.
```

It does not by itself give a cheap coefficient or common-factor recurrence:

1. Evaluating the `B` orbit points costs only `B^(1+o(1))`, but they are
   supplied shift parameters, not the `B` resultants.
2. Evaluating all translated endpoints for `n` pair occurrences writes
   `nB=B^3` signed keys.
3. Updating or storing one dense degree-`n` divisor per shift writes `B^3`
   coefficients; even one target-dependent degree-`n` vector uses `B^2`
   workspace.
4. A scalar product `product_j r_R(t_j)` is an exact existence/unit test but
   does not return every factor or pair source. Exact subinterval products
   could support bisection only if their construction, all negative branches,
   and pair-restriction replay also fit the total online cap.

Even grant an optimistic factorial-style baby-step/giant-step evaluator for a
**supplied** polynomial- or rational-coefficient shift recurrence. Replacing
`B` explicit degree-`n` updates by `B^(1/2+o(1))` represented blocks still costs

```text
n B^(1/2+o(1)) = B^(5/2+o(1))
```

base-field work at `n=B^2`, before labelled factor reporting and restriction
replay. This favorable control is already above the `B^(5/4)` online cap, and
the cited recurrence algorithms do not prove that the elliptic translated
divisor family has their required compact recurrence. It therefore cannot be
credited as the missing orbit-product locator.

P1540 already proves that standard Hankel displacement rank is tautological
and that a constant-coefficient recurrence for a consecutive translated
x-coordinate block has order `Omega(B)`. An elliptic-net recurrence can
evaluate supplied orbit terms but does not locate zeros or construct this
translated divisor product for free. Those facts reject constant-recurrence,
supplied-term, and explicit `B^3` endpoint implementations here.

They do not reject a gauge-invariant nonlinear or variable-coefficient
elliptic-net/division-polynomial operation that directly returns the
target-label factor or exact subinterval unit products from the compact pair
trees. Such a route must:

- be invariant under elliptic-net quadratic rescaling;
- keep zero denominators as vertical/infinity relation strata;
- construct every target-dependent initial value inside `B^(5/4+o(1))` time
  and workspace;
- avoid a degree-`B^2` target coefficient vector and all `B^3` translated
  endpoints;
- return all fifth labels or support charged all-negative subinterval replay;
- support the same restricted operation for both pair trees and all sources;
  and
- pass the complete relation, rank, factor-log, and blind-descent gate below.

No checked primary source supplies that operation. It remains the sole concrete
favorable representation-sensitive exception from this task.

## 8. Source replay and full conditional ECDLP path

Given a subset-stable `z_R` constructor, select a factor of `z_R` to restrict
`I_5`, then bisect one source node at a time. Test the left child; if it is a
unit, test or retain the right child. Across five decks this uses at most

```text
2*sum_i ceil(log_2 |I_i|)+O(1)=O(log B)
```

constructor calls, including negative calls. Endpoint multiplicity is never
used as a source label. At singleton leaves, add the five signed points with
the complete projective law and accept only if the sum is exactly `R`.

The favorable complete campaign, conditional on one constructor whose **total**
replay cost is `B^(5/4+o(1))`, is:

1. Preprocess the pair/fifth trees in `B^(2+o(1))` work and state.
2. Query `Theta(B)` independently sampled known-log targets `[s_j]P`. Under
   the unproved random-endpoint density control, obtain `Theta(B)` verified
   five-sparse rows in total `B^(9/4+o(1))` work.
3. Prove the rows have rank `B-O(1)`, retain duplicates and failures, and solve
   factor logs. Sparse Wiedemann costs `B^(2+o(1))` field operations and
   `B^(1+o(1))` live vector state under the favorable full-rank model. Verify
   every log by scalar multiplication.
4. For a fresh challenge `Q=[x]P`, sample known masks `t`, query
   `R=Q+[t]P` with the identical constructor, and charge every failed mask.
5. For a verified decomposition, return
   `x=sum(factor logs)-t mod N` and accept only if `[x]P=Q`.

With constant relation and target success density, constant ambiguity, verified
rank, and a passing constructor, the exponents would be

```text
lambda=max(2/5, (1+5/4)/5, 2/5, (5/4)/5, 1/5)=0.45,
mu=max(2/5, (5/4)/5, 1/5)=0.40.
```

This accounting is a conditional gate, not an achieved path. Relation density,
independent rank, the constructor, orbit-deck correlations, factor-log input,
and blind descent are not established.

## 9. Operation-level deduplication

`z_R` is the same mechanism-level compact-input common-factor and source-jet
operation already isolated by P1513/IDEA-121. The target-label polynomial
changes the output coordinate from an endpoint/common-norm factor to fifth
occurrence labels, but the information flow remains

```text
compact B^2 pair-product input
 -> nonlinear unknown common-factor locator
 -> exact restricted source replay/jets.
```

Consequently:

- P1513/IDEA-121 owns the common-factor/source-jet locator. `z_R` is not a
  novel mechanism or new owner.
- IDEA-063 owns balanced remainder/subresultant propagation after a common
  factor exists. A forest does not construct the root residue.
- IDEA-071 owns Cauchy/displacement determinant reporting. Low displacement
  rank or a faster determinant is a backend without source output.
- IDEA-199 owns endpoint coefficient access followed by source unranking.
  A transform name does not supply the coefficient deck.
- IDEA-266 owns dynamic splitting after a source algebra is represented. The
  no-relation unit branch receives no early split.
- IDEA-322 owns Woodbury target-shift resolvents. Natural target updates have
  rank `B` per split coefficient and singular hits require the missing factor
  and backsolve.
- P1540 owns the elliptic-net constant-recurrence and translated-pole control.
  Only its explicitly preserved gauge-invariant nonlinear or
  variable-coefficient orbit locator remains open here.

Remainder trees, displacement rank, half-gcd, target-shift resolvents, modular
composition, and solver substitutions receive no novelty credit by themselves.

## 10. Primary-literature controls

Only primary sources are used for algorithmic controls:

1. Borodin and Moenck, *Fast modular transforms*,
   <https://doi.org/10.1016/S0022-0000(74)80029-2>, for fast represented
   multipoint/remainder arithmetic.
2. Bernstein, *Scaled remainder trees*,
   <https://doi.org/10.1016/j.jalgor.2004.04.009>, for batched remainder
   propagation on supplied polynomial families.
3. Moroz and Schost, *A Fast Algorithm for Computing the Truncated
   Resultant*, <https://arxiv.org/abs/1609.04259>, for the soft-`O(kd)`
   truncated-resultant control.
4. Kedlaya and Umans, *Fast Polynomial Factorization and Modular
   Composition*, <https://doi.org/10.1137/08073408X>, for finite-ring modular
   composition with the coefficient-ring bit width charged.
5. Poteaux and Schost, *Modular Composition Modulo Triangular Sets and
   Applications*, <https://cs.uwaterloo.ca/~eschost/publications/mulmodcomp.pdf>,
   for cost in represented triangular-algebra dimension.
6. Neiger, Salvy, Schost, and Villard, *Faster Modular Composition*,
   <https://arxiv.org/abs/2110.08354>, and *Faster Modular Composition Using
   Two Relation Matrices*, <https://arxiv.org/abs/2601.17422>, for current
   dense algebraic modular-composition controls.
7. Kailath, Kung, and Morf, *Displacement ranks of matrices and linear
   equations*, <https://doi.org/10.1016/0022-247X(79)90124-0>, for the
   distinction between a supplied low-displacement matrix and its generators.
8. Sherman and Morrison, *Adjustment of an inverse matrix corresponding to a
   change in one element of a given matrix*,
   <https://doi.org/10.1214/aoms/1177729893>, for inverse maintenance on a
   supplied nonsingular rank-one update, not singular-hit source recovery.
9. Stange, *Elliptic Nets and Elliptic Curves*,
   <https://arxiv.org/abs/0710.1316>, for net recurrences, scale equivalence,
   and coordinate-difference identities.
10. Lauter and Stange, *The elliptic curve discrete logarithm problem and
    equivalent hard problems for elliptic divisibility sequences*,
    <https://arxiv.org/abs/0803.0728>, for the distinction between term
    evaluation and orbit-index location.
11. Wiedemann, *Solving sparse linear equations over finite fields*,
    <https://doi.org/10.1109/TIT.1986.1057137>, for the conditional sparse
    factor-log linear-algebra control.
12. Bostan, Gaudry, and Schost, *Linear Recurrences with Polynomial
    Coefficients and Application to Integer Factorization and Cartier--Manin
    Operator*, <https://doi.org/10.1137/S0097539704443793>, for the favorable
    baby-step/giant-step recurrence control on a supplied recurrence, not an
    elliptic orbit-product constructor.
13. Fitting, *Die Determinantenideale eines Moduls*,
    <https://eudml.org/doc/146122>, for zeroth Fitting ideals and finite-module
    support; it supplies no compact presentation or source inverse.
14. Semaev, *Summation polynomials and the discrete logarithm problem on
    elliptic curves*, <https://eprint.iacr.org/2004/031>, for the neighboring
    x-coordinate relation equations; supplied signs and complete charts remain
    additional obligations.

None of these sources supplies the compact complete-chart `r_R mod g_I`
constructor or the required labelled source replay.

## 11. Claim boundary and exactly one next action

The supported terminal verdict is:

```text
SCOPED_NEGATIVE_NAMED_REPRESENTED_ALGEBRA_ROUTES__EXACT_COMPLETE_CHART_TARGET_LABEL_FACTOR_DEFINED__R_MOD_G_INPUT_CONSTRUCTION_DISTINCT_FROM_FAST_GCD__STANDARD_MULTIPOINT_REMAINDER_TRANSPOSED_RESULTANT_SYLVESTER_DISPLACEMENT_MODULAR_COMPOSITION_SUBRESULTANT_AND_COMMON_FACTOR_ROUTES_RESTORE_B3__NO_RELATION_IS_A_UNIT_WITH_NO_DYNAMIC_SPLIT__Z_R_IS_P1513_COMMON_FACTOR_SOURCE_JET_OPERATION_NOT_NOVEL__F5_ONLY_SCALAR_ORBIT_PRESERVES_HEURISTIC_COVERAGE__CONSTANT_RECURRENCE_AND_SUPPLIED_TERM_ROUTES_REJECTED__GAUGE_INVARIANT_NONLINEAR_OR_VARIABLE_COEFFICIENT_ORBIT_PRODUCT_LOCATOR_OPEN__ALL_STRATA_REPLAY_RANK_LOGS_DESCENT_UNSUPPLIED__NO_RUN__NO_P1554__NO_BREAKTHROUGH
```

Untested exceptions preserved: a compact complete-chart arithmetic or Boolean
circuit, target-local data structure, randomized exact method with detected
failure, word-RAM or cell-probe structure, special pair decks, a genuinely
output-sensitive product-circuit gcd, and the Section 7 nonlinear or
variable-coefficient orbit-product locator. Failure of the named algorithms
does not close any of these classes.

Exactly one next action: obtain an independent theorem-only red-team audit of
the Section 7 compact orbit-product exception, requiring an oracle-free,
gauge-invariant construction of `r_R mod g_I` or exact dyadic subinterval unit
products inside the total `B^(5/4+o(1))` online cap, with no degree-`B^2`
target vector, `B^3` translated endpoints, supplied orbit-resultant terms, or
unpaid source replay; otherwise preserve the exception without a run.

## 12. Local input bindings

SHA-256 was computed over every local byte stream read. The dispatch task was
canonicalized as

```text
jq -S -c '.tasks[] | select(.id == "TASK-20260718-P1553-ZR-P1")'
```

and hashes to
`097e162498892b53d17ed42ee2b9f9f9413d63c187e2a36ac4116cdb16a523c9`.

| Local input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_query2p1_indexing_gate_r3.md` | `b2ee5934e295ab1f0d6b43452898e520d0cb18e718a8f5865694b25909b0df5e` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_report.yaml` | `60488d10253b4161562704e048a5e57dda33e031051ed00cf43ad339ac9125bb` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_theorem_gate.md` | `0f6d5e1caabbe2edfd84f76404805e2d4df5316263d384ad0e10f0b685527f92` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-RT-R1/red_team_report.yaml` | `982ed54f11ddcc7ae80b87b49eae8f8b880d7e67b8adebc249a67394af324647` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-RT-R1/query2p1_red_team.md` | `626e411cebe1c02e5c1437a04deb6822dfffb752e3a1969579694e89f8fe9a06` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md` | `6fcca1d12e911f6eb2142ac96b6d0a83b6ac20db11efd06bc24c0abb7c99dc48` |
| `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` | `18cebc9c209c6ba0d705e43da7f921885e60d3436b201375e306e14f4ae0bdb2` |
| `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` | `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e` |
| `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` | `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1` |
| `ledger/FINDING-PF-IC-001.md` | `21cb3cf8d4680692d8ac72bdc303269d1d07d0949172c2d1d4497652608e339b` |
| `focus/current_plan.json` | `422e513d0ca4307c25e58ce8f97b11e87957a6ee4b7a76afeb6a9a0cf6085d66` |
| `ideas/artifacts/ECDLP-IDEA-068/p1513_common_norm_route_screen.md` | `9ec1a5010d7774ee74ff8af7d910bced915cec76213ddd5beca1b7c7aac5c8a8` |
| `ideas/artifacts/ECDLP-IDEA-068/p1513_shared_bivariate_norm_identity.md` | `f3207d0634e04e61e7768548f03014989c65f6319330645cbd1b165f9c00fa73` |
| `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` | `fcbf0e6d6ef068ee7aea1c9c091d7eb69c77e23f181c173cbc3f55f626a4e73a` |
| `ideas/rejected/ECDLP-IDEA-071_elliptic_cauchy_displacement_reporter_hypothesis.md` | `27c6880d52b310f03c1d532b3ed68d9e192576b01815d3003501187a64571b5e` |
| `ideas/rejected/ECDLP-IDEA-322_woodbury_target_shift_resolvent_router_hypothesis.md` | `2a34a461916dbda58cdbe6052a2c8a2197441d329989f5cde642a67296994ff2` |
| `ideas/artifacts/ECDLP-IDEA-006/p1540_elliptic_net_translated_pole_annihilator_gate.md` | `d9a4040230022c24f7011932ef7cd9b5bcea51236a80c042bb498d2012428437` |
| `coordination/dispatch_queue.json` | `a66de0941f2a047b473f323ecf70364867c4a21da6307085c1e91cee02bfd370` |

The first thirteen entries are the dispatch read scope. The next six are the
coordinator-requested semantic-dedup and orbit controls. The dispatch queue is
bound separately as the source of the exact task object.
