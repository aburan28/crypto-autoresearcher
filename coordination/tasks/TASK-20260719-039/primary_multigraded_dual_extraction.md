# TASK-20260719-039 primary multigraded-dual extraction

## Receipt boundary

- Role: idea-generator source receipt; no computation or experiment.
- Primary source: Cummings--Hauenstein, *Multi-graded Macaulay Dual Spaces*,
  arXiv:2310.11587v1 (2023); comparison sources: Laurent--Mourrain
  arXiv:0812.2563, Mourrain arXiv:1705.01328, and
  Berthomieu--Faugere arXiv:2107.02582.
- This receipt does not allocate a proposal, authorize compute, assert a
  lower bound, or change any hypothesis status.

The paper writes `R=C[x_1,...,x_N]`; its `N` is the number of polynomial
variables, not an ECDLP group order. I use `N_grp` for the latter below.

## 1. Exact local and multigraded objects

### Definition 2.9: local dual at a supplied point

For an ideal `I subset R` and a specified `y in C^N`, define

```text
partial^alpha[y](f)=(1/alpha!)(partial^|alpha| f/partial x^alpha)|_(x=y),
D_y=span_C{partial^alpha[y]},
D_y(I)={delta in D_y : delta(f)=0 for every f in I}.
```

Thus `y` is input, not output. If `D_y(I)` is finite dimensional, its
dimension is the multiplicity at the isolated point `y`; a nonisolated point
has infinite-dimensional local dual. Definition 2.9 does not discover an
unknown point.

The field is `C`. The source states no positive-characteristic analogue or
finite-field algorithm for its factorial-normalized differential operators.

### Proposition 2.11: closedness remains centred at `y`

For `I=<f_1,...,f_t>`, anti-differentiation satisfies
`Phi_i(delta)(f)=delta((x_i-y_i)f)`. Proposition 2.11 says
`delta in D_y(I)` exactly when `delta(f_j)=0` for all
generators and every `Phi_i(delta)` is again in `D_y(I)`. This recursively
constructs multiplicity data at the supplied centre; it does not select the
centre from ideal coefficients.

### Definitions 2.1 and 2.5: grading and Hilbert components

Definition 2.1 uses a finitely generated abelian group `M`, with
`R=direct_sum_(a in M) R_a` and `R_a R_b subset R_(a+b)`. An `M`-graded ideal
has homogeneous generators. Definition 2.5 sets
`H_I(a)=dim_C R_a-dim_C(I intersect R_a)`.

The construction assumes finite-dimensional graded pieces. For a grading
matrix `A`, this requires the associated nonnegative weight cone to be
pointed (`ker(A) intersect N^N={0}` in the stated setup).

### Theorem 3.2: zero-centred components

The source extends the grading to differential operators at the origin:

```text
D_0^a=span_C{partial^alpha[0] : A alpha=a}.
```

Theorem 3.2 states that, for an `M`-graded ideal,
`D_0(I)=direct_sum_(a in M) D_0^a(I)` with
`D_0^a(I)=D_0^a intersect D_0(I)`.

This is a decomposition at the fixed origin. It neither finds affine roots
nor turns its component basis into evaluations at unknown roots.

Proposition 3.4 identifies only the component dimension:
`H_I(a)=dim_C D_0^a(I)`.

### Corollary 3.6: exact recursive basis step

For homogeneous `I=<f_1,...,f_t>`, let

```text
C_0^a(I)={delta in D_0^a :
          Phi_i(delta) in D_0^(a-Ae_i)(I) for every variable i}.
```

Corollary 3.6 gives

```text
D_0^a(I)={delta in C_0^a(I) :
          delta(f_j)=0 for generators f_j of degree a}.
```

Lower-degree generator constraints propagate through closedness. The input is
the homogeneous generators plus already computed predecessor components; the
output is a vector-space basis of one zero-centred component. It is not a
point list, multiplication table, or faithful single functional.

Definition 3.7 orders weights by `a<=_omega b` iff `b-a in omega`;
Proposition 3.8 proves a partial order, whose linear extension drives recursion.

## 2. Ideal operations and the right inverse

Corollary 4.3 gives, componentwise,

```text
D_0^a(I+J)=D_0^a(I) intersect D_0^a(J),
D_0^a(I intersect J)=D_0^a(I)+D_0^a(J).
```

Consequently a target fibre `I_R=I_deck+<g_R>` requires the sum-ideal
intersection, not an ideal quotient.

The paper's “ideal quotient” is the colon ideal `I:g={f : fg in I}`, not the
quotient algebra `R/I`. Proposition 4.5 treats quotient by a variable. For
homogeneous `g`, the general operator is `Phi_g(delta)(f)=delta(gf)`.

If `deg(g)=d`, it maps degree `a+d` differential operators to degree `a`.
Lemma 4.7 constructs a linear right inverse `Psi_g` with
`Phi_g(Psi_g(delta))=delta`: choose the lexicographically least exponent
`alpha_0` having nonzero coefficient `g_(alpha_0)` and recursively divide by
that coefficient. This is a right inverse on differential spaces, not an
inverse from a target relation value to its deck sources.

Theorem 4.8 states

```text
Phi_g(D_0^(a+d)(I))=D_0^a(I:g).
```

For homogeneous `J=<g_1,...,g_t>`, the corresponding images sum to the dual
component of `I:J`. Repetition gives saturation. On a finite radical deck,
`I_deck:g` keeps points with `g!=0` and removes points with `g=0`; it therefore
does the opposite point-set selection from `I_deck+<g>`. This is a type
distinction, not a complexity lower bound.

## 3. Exact Section 5 procedures

Section 5 restricts to a `Z^k` grading matrix `A` with finite-dimensional
components, a pointed weight cone having half-space matrix `B_h`, and a
saturated weight semigroup. (`B_h` is not the deck-size parameter below.)

### `SortLatticePoints(A,B_h,a)`

For requested degree `a`, let
`omega_a={s in Z^k : B_h a >= B_h s >= 0}`. The procedure enumerates every
lattice point in `omega_a` and returns a
linear extension of the weight order. Lemma 5.1 proves `omega_a` finite;
Theorem 5.2 proves termination and correctness of the returned order.

### `DualSpace(a,I,A,B_h)`

Inputs are `A`, requested `a`, homogeneous ideal generators and their degrees,
and `B_h`. The procedure:

1. calls `SortLatticePoints`;
2. initializes the degree-zero constant differential;
3. visits all later degrees in the returned order;
4. intersects inverse images of predecessor dual components under each
   variable anti-differentiation map; and
5. imposes generator evaluation equations as in Corollary 3.6.

Its output is a basis of `D_0^a(I)`. It has no stated output for unknown roots,
primary components, a flat moment extension, multiplication matrices, a
faithful functional, or target-source labels.

Applicability not supplied by the paper includes nonhomogeneous affine input
without homogenization, nonpointed or nonsaturated grading data, infinite
components, positive-characteristic arithmetic, automatic unknown-centre
decomposition, and finite-field source labels. Homogenized examples may use
repeated saturation to remove projective components; that does not add a
source inversion theorem.

## 4. Complexity statements and absences

Cummings--Hauenstein state no asymptotic arithmetic, bit, memory, or
output-sensitive complexity bound for either procedure. They state only that
lattice-point computation is the most expensive part of
`SortLatticePoints`, that the Macaulay2 implementation is a proof of concept
and not competitive with optimized Groebner-basis methods, and that complexity
analysis is future work.

In particular, no bound is stated for component count or dimension, lattice
enumeration, inverse-image intersections, generator linear algebra,
coefficient growth, saturation, retained state, target reuse, finite-field
work, or point extraction. No ECDLP setup/query/campaign exponent follows from
this source.

The comparison decoders do not fill that input gap:

- Laurent--Mourrain Theorem 1.4 assumes a supplied sequence on
  `C^+ . C^+` and a flat-rank condition; “sparse” describes the monomial set.
- Mourrain Algorithm 3.1 assumes supplied coefficients `sigma_alpha`.
  Proposition 3.7 gives `O((r+delta) r s)` arithmetic for the downstream
  border-basis construction, excluding construction of its `s` sequence terms.
- Berthomieu--Faugere likewise charge arithmetic and table queries after a
  multidimensional sequence/table is supplied; they do not construct the
  elliptic target-local sequence from ideal coefficients.

## 5. Frozen grading and scoped implication

Only now translate to the frozen five-deck normalization. Use

```text
R_col=k[X_1,Z_1,...,X_5,Z_5],
deg X_i=deg Z_i=e_i in Z^5.
```

For `d=(d_1,...,d_5)`,

```text
dim_k (R_col)_d=product_i(d_i+1).
```

Five square-free size-`B` deck equations have degrees `B e_i`. For the
deck-only complete intersection,

```text
H_(R_col/I_deck)(d)=product_i min(d_i+1,B).
```

At `d=(B-1,...,B-1)`, this component has dimension exactly `B^5`, matching
the affine split algebra `tensor_i k[T_i]/(f_i)`. For the relation fibre,
Corollary 4.3 gives

```text
D_0^d(I_deck+<g_R>)=D_0^d(I_deck) intersect D_0^d(<g_R>).
```

This `B^5` dimension is a control for the natural fully coupled component.
The paper neither proves that every algorithm must construct it nor proves
that a smaller adaptive component is faithful. A `B^5` requirement is
therefore route-specific, not a general lower bound.

With frozen `m_grp=N_grp=B^5`, deck size `n_deck=B`, and five decks, the
campaign caps are `B^(9/4+o(1))` for setup/state or `B` rows and
`B^(5/4+o(1))` for a complete fresh query, versus rho
`B^(5/2+o(1))`. Explicitly materializing the natural `B^5=N_grp` component
misses those caps, but only for this explicit representation. The source gives
neither a smaller faithful construction nor any complete-path rank,
factor-log, scalar-blind reuse, or target-descent bound.

## Claim boundary

The source establishes a coefficient-to-`D_0^a(I)` recursion and a distinct
supplied-point local dual. It establishes neither a source-blind faithful
functional/source inverse nor a no-go theorem. A correct component basis,
Hilbert value, local multiplicity, or source tuple is not an ECDLP breakthrough.

## Factual handoff to TASK-20260719-041

TASK-041 receives the source-established zero-centred component recursion, the
supplied-centre requirement for `D_y(I)`, the sum-ideal intersection required
for `I_deck+<g_R>`, the colon-only scope of Lemma 4.7 and Theorem 4.8, the exact
route-specific natural-component dimension `B^5`, and the absence of a
source-stated faithful-functional, source-inversion, finite-field, or
complexity theorem beyond those boundaries.
