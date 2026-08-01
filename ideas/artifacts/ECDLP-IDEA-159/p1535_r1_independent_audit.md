# P1535 R1 independent nonordinary source-component audit

Status:
`INDEPENDENT_SCOPED_AUDIT_PASS__NONORDINARY_NO_CANDIDATE__FROBENIUS_MOMENT_SUCCESSOR`

This is a theorem-only independent audit of
`non_diagonal_polar_theorem.md`. It reconstructs the ordinary generic-stalk
argument, writes one explicit nonordinary representation through exact source
recovery, screens the named derived, stacky, and noncommutative escape classes,
and charges the complete factor-base path. No Rees algebra, solver, toy curve,
relation campaign, factor-log solve, target descent, or experiment was run.

The audit finds no passing nonordinary source-component representation. It does
isolate one exact target-local finite-field operation that is not supplied by
the nonordinary representation: traces of a Frobenius zero projector in the
fivefold factor algebra. That operation is a concrete instance of P1514's open
structured moment-constructor scope and is routed separately. It is not an
ECDLP algorithm or a breakthrough.

## Frozen inputs and hashes

The audited producer inputs are:

```text
ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md
SHA-256 755fdab79fd2ed0c60054a9b7dfbd32ff7dc6e5e36d93ed9f1dddaa9ac05d7b3

ideas/ECDLP-IDEA-159_non_diagonal_conormal_polar_source_blowup_hypothesis.md
SHA-256 492473589bc49663965253293e71bd59fc7989920b4e1f2742f1adf6d5326cde
```

The closest semantic controls used by this audit are:

```text
IDEA-089 supplied relation algebra -> primitive idempotent splitter
IDEA-091 root-stack inertia labels
IDEA-100 Hopf-Galois normal-basis projectors
IDEA-142 free-field linear-pencil residues
IDEA-207 split central-simple algebra minimal ideals
IDEA-216 normalization/conductor source splitting
P1514 structured target-local moment constructor
P1534 fivefold quotient-algebra support router
```

## 1. Independent reconstruction of the ordinary theorem

Let `X` be the reduced source-labelled all-distinct incidence and let `X_i` be
an irreducible component with generic point `eta_i`. Then

```text
O_(X_i,eta_i) = K(X_i)
```

is a field. For every coherent ideal sheaf `J` on `X`,

```text
J_(eta_i) = 0  or  J_(eta_i) = K(X_i).
```

If `J` is nonzero on `X_i`, a nonzero local generator becomes invertible in the
function field, so coherence makes `J` the unit ideal on a dense open around
`eta_i`. If `J_(eta_i)=0`, then `J` vanishes on the reduced component and its
positive-degree Rees algebra gives no generic blowup chart there.

The remaining producer claims also reconstruct:

1. `Bl_J(X) -> X` is an isomorphism away from `V(J)`, so a proper polar,
   Jacobian, ramification, branch, or discriminant center supplies data only on
   its proper support.
2. Blowing up an invertible ideal is an isomorphism, so a Cartier center does
   not create source atoms.
3. Normalization cannot create exceptional data over a normal open where the
   blowup was already an isomorphism.
4. On a reducible incidence, choosing zero or unit behavior separately at each
   generic component is already a component partition. Refining those choices
   to an exact source word is a source dictionary unless a compact public rule
   and its construction cost are separately supplied.

This proves only the producer's scoped ordinary-Rees negative. It is not a
lower bound against arbitrary nonlinear or implicit arithmetic circuits.

## 2. Explicit nonordinary attempt: the endomorphism algebra

Let `k=F_p`. Freeze a sign-canonical rational x-coordinate factor deck
`F_x subset k` of size `B` and its square-free polynomial

```text
f_F(T) = product_(a in F_x) (T-a).
```

Define the split factor algebra and its fivefold tensor product

```text
A_F = k[T]/(f_F),
A_5 = A_F tensor_k ... tensor_k A_F  (five factors).
```

Evaluation gives

```text
A_5 ~= product_(a in F_x^5) k,
D = dim_k(A_5) = B^5.
```

The explicit nonordinary representation is

```text
E_5 = End_k(A_5) ~= M_D(k).
```

It is target-independent and noncommutative. The left regular map

```text
L : A_5 -> E_5,
h |-> L_h
```

embeds the source algebra as a commutative diagonal subalgebra after base
change to the evaluation basis.

For a finite target chart with x-coordinate `x_R`, put

```text
g_R = S_6(T_1,T_2,T_3,T_4,T_5,x_R) in A_5.
```

In the evaluation basis, `L_(g_R)` is diagonal and

```text
ker(L_(g_R))
  = span_k { e_a : a in F_x^5 and S_6(a_1,...,a_5,x_R)=0 },
```

where `e_a` is the primitive coordinate idempotent for tuple `a`.

This proves exact support semantics, but not a cheaper operation. The useful
source atoms are exactly the primitive idempotents of `A_5` viewed through
`L`. Enlarging to `E_5` adds many unrelated rank-one projectors.

## 3. Why the matrix-algebra atoms are not source atoms

Rank-one idempotents of `M_D(k)` are not a discrete canonical source list. A
rank-one projector depends on a line and a complementary hyperplane, and
conjugation transports it to other rank-one projectors. Minimal right ideals
likewise form a projective family. Reduced norm, determinant, rank, and
conjugacy data do not choose the `D` coordinate lines belonging to source
tuples.

The source projectors are the special diagonal elements `L_(e_a)`. Selecting
that diagonal family requires retaining the embedded commutative algebra
`L(A_5)`; splitting it into its primitive idempotents is the original
relation-algebra/source-splitting operation. Thus there is a strict dichotomy:

```text
forget L(A_5):  rank-one ideals are noncanonical and source-unlabelled;
retain L(A_5):  exact source projectors are the original primitive idempotents.
```

For a connected finite etale cover, geometric monodromy permutes its sheets.
A target-independent construction invariant under this action can select only
monodromy-stable unions until splitting data are supplied. A separating
element `theta in A_5` can break the symmetry only after its characteristic
polynomial is split. Its spectral projector formula

```text
e_i = product_(j != i) (theta-lambda_j)/(lambda_i-lambda_j)
```

requires the eigenvalues or equivalent root/source data. This is IDEA-089's
primitive-idempotent boundary, not a free consequence of noncommutativity.

## 4. Exact survivor inside the commutative subalgebra

The endomorphism attempt exposes a stronger exact control. Because every
coordinate of `A_5` lies in `F_p`, Fermat's identity gives

```text
chi_R = 1 - g_R^(p-1) in A_5.
```

At each source tuple `a`,

```text
chi_R(a) = 1  if g_R(a)=0,
chi_R(a) = 0  if g_R(a)!=0.
```

Hence `chi_R` is the canonical idempotent projector onto the complete x-source
support of the target. It is target-local, public, exact, and contains no
post-hoc source annotation.

Let `Tr` denote the trace of multiplication on the finite `k`-algebra `A_5`.
For multi-indices `nu=(nu_1,...,nu_5)`, define

```text
M_nu(R) = Tr(L_(T_1^nu_1 ... T_5^nu_5 chi_R))
        = sum_(a in supp(chi_R)) a_1^nu_1 ... a_5^nu_5.
```

In particular,

```text
M_0(R) = number of accepted x-tuples.
```

If the support is a singleton `{a}`, then only six traces are needed:

```text
M_0(R)=1,
M_(e_i)(R)=a_i  for i=1,...,5.
```

For bounded multi-source support, a sufficiently complete mixed-moment table
feeds the existing P1514 flat-extension/Prony source decoder. The important
point is that the formulas above construct the desired moments semantically;
they do not compute them within the cost gate.

## 5. All-strata source interpretation

The source deck `A_5` remains reduced because `f_F` is square-free. Repeated
coordinates in different positions are still distinct ordered source tuples,
so collision and repeated-point cases do not create nilpotents in this deck.
Eliminant tangency or multiplicity can therefore be bypassed by retaining the
source-labelled Cartesian algebra rather than inferring sources from an
eliminated polynomial.

The x-only projector does not choose elliptic signs. Once an x-tuple is known,
at most `2^5` sign assignments plus fixed infinity/exception handling are
checked by complete projective addition. This is constant at fixed arity and
is not the asymptotic obstruction. If infinity is admitted to the factor base,
it can be represented by a separate public tag and a constant number of tagged
branches.

Thus the Frobenius projector has a complete exact-source interpretation after
its moments are available. The missing operation is exact structured trace
construction, not final sign lifting.

## 6. Cost of every explicit realization

At the standard five-source balance `B=N^(1/5)`, the split algebra has

```text
D=B^5=N.
```

The explicit costs are:

| Realization | Time/state consequence | Disposition |
|---|---|---|
| Dense `A_5` coefficient or evaluation vector | `Theta(B^5)=Theta(N)` entries | fails |
| Dense `E_5=End(A_5)` | `Theta(B^10)` entries | fails more strongly |
| Repeated squaring of `g_R^(p-1)` in materialized `A_5` | at least the `B^5` payload per dense stage | fails |
| Direct trace by evaluating every source tuple | `Theta(B^5)` per target | fails |
| Reusable 2+3 deck | `Theta(B^3)` setup/time/state and `Theta(B^2)` lookup | setup/state above cap |
| Streamed 2+3 deck | `Theta(B^3)` per target, `Theta(B^4)` for `B` relation targets, `Theta(B^2)` memory | time fails |
| Supplied `chi_R` or its moments | exact positive control | constructor cost omitted |
| Tuple membership oracle `a |-> chi_R(a)` | cheap membership, no source locator | P1515/P1534 control |

No dimension-only runtime lower bound is claimed for a succinct arithmetic
circuit. In particular, the expression `1-g_R^(p-1)` has `O(log p)` formal
multiplication gates. The unresolved issue is whether its six or boundedly many
traces can be contracted exactly without expanding tensor rank, constructing a
degree-`B^5` norm/characteristic polynomial, enumerating the source grid, or
reintroducing a `B^3` join.

## 7. Complete exponent gate for the surviving trace primitive

Write `B=N^beta`, use arity five, and let a reusable trace constructor have
setup `B^s`, per-target query `B^kappa`, memory `B^m`, and output/ambiguity
exponents `o,u` over `N`. Under the favorable constant-density balance
`beta=1/5`, collecting `Theta(B)` relation rows gives the lower accounting

```text
lambda >= max(s/5, (1+kappa)/5, ell, kappa/5+u, 1/5),
mu     >= max(m/5, ell_m, 1/5+o, u).
```

The frozen promotion rectangle `lambda,mu<=0.45` therefore requires at least

```text
s <= 2.25,
kappa <= 1.25,
m <= 2.25,
```

before factor-log and ambiguity terms are added. Direct `kappa=5`, reusable
`s=3`, and streamed `kappa=3` controls all miss this rectangle.

For general `beta` in the sparse random-support model, reciprocal relation
density is `N^(max(0,1-5beta))`; every attempt, failed target, rank row,
factor-log solve, blind mask, and final verification remains charged. These
density and rank assumptions are heuristic and model-bound. The projector and
trace identities themselves are exact.

## 8. Screen of the named nonordinary escape classes

| Class | Generic useful datum | Why it does not pass P1535 |
|---|---|---|
| Derived enhancement | Cotangent/derived structure | Finite etale generic source sheets have zero cotangent complex; singular derived data live on exceptional strata. Splitting perfect objects by generic sheets still uses the primitive idempotents. |
| Root stack or orbifold | Inertia along a rooted divisor | A root stack is unchanged away from its divisor. Rooting every source component requires the source divisor dictionary; uniform generic inertia does not distinguish sheets. This is IDEA-091. |
| Generic gerbe | Uniform stabilizer characters | The same generic stabilizer occurs on every sheet. Component-varying characters are component advice. |
| Azumaya or central-simple algebra | Reduced norm and minimal ideals | Over the split fiber, minimal ideals are conjugate and noncanonical; source-labelled ideals require an oriented splitting. This is IDEA-207. |
| Endomorphism algebra `End(A_5)` | Kernel/projector of `L_(g_R)` | Every useful source projector lies in the original commutative algebra; dense matrix form inflates the payload. |
| Free-field linear pencil | Noncommutative residues | Commuting specialization loses word ancestry; source-faithful residues restore transition/source states. This is IDEA-142. |
| Hopf-Galois action | Normal-basis projectors | It starts after the relation algebra is supplied and does not provide the missing target query. This is IDEA-100. |
| Normalization/conductor | Branch gluing | The reduced generic finite etale fiber is already normal; primitive splitting is root/source finding. This is IDEA-216. |

This table is a semantic screen of explicit classes, not a theorem against every
possible derived, stacky, noncommutative, or categorical construction.

## 9. Literature boundary

The finite-etale and monodromy facts used here are standard: over a separably
closed field, finite etale covers are finite sets, and connected finite etale
covers carry transitive geometric monodromy. The cotangent complex of an etale
map vanishes. Norms of finite locally free algebras are determinants of
multiplication. Root constructions along divisors are unchanged away from the
rooted support.

Primary references:

- The Stacks Project, *Finite etale morphisms*, Tag 0BL6:
  <https://stacks.math.columbia.edu/tag/0BL6>.
- The Stacks Project, *Galois covers of connected schemes*, Tag 03SF:
  <https://stacks.math.columbia.edu/tag/03SF>.
- The Stacks Project, *The cotangent complex*, Lemma 92.8.4, Tag 08R2:
  <https://stacks.math.columbia.edu/tag/08R2>.
- The Stacks Project, *Norms*, Lemma 31.18.6, Tag 0BD2:
  <https://stacks.math.columbia.edu/tag/0BD2>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.

None supplies the required `B^2.25`/`B^1.25` exact Frobenius-projector trace
constructor or a complete below-rho ECDLP path.

## 10. Independent disposition

The producer's ordinary generic-stalk theorem passes in its stated scope. The
explicit nonordinary `End(A_5)` attempt fails because its source projectors are
exactly the primitive idempotents of the original commutative source algebra,
while the full matrix algebra adds noncanonical projective families and a
larger representation. The screened derived, stacky, Azumaya, free-field,
Hopf-Galois, and conductor classes either live on proper exceptional loci,
aggregate generic sheets, begin after the missing relation algebra is supplied,
or require a source-labelled splitting.

P1535 therefore has no passing nonordinary candidate and should be deferred
with an independently verified scoped inconclusive disposition. The broad
existence claim remains open because no universal lower bound is proved.

The exact Frobenius projector and its moment identity are retained as a
mechanism-specific successor to P1514:

```text
given f_F, S_6, and R,
compute Tr(T^nu * (1-S_6^(p-1)))
for enough nu to recover every x-source,
with reusable setup <= B^2.25 and per-target query <= B^1.25.
```

That is a finite-field representation-specific operation and could evade the
generic-group interface if constructed. No such constructor is currently
known or proved. Correct projector semantics, a supplied trace, a toy source,
or one valid relation would not establish a Shoup-bound improvement.

## Exactly one next action

Independently audit the P1536 Frobenius-projector trace primitive against
P1514/P1515/P1534: either derive one exact tensor-contraction, transposed power-
projection, modular-composition, or FFE recurrence inside setup `B^2.25`, query
`B^1.25`, and memory `B^2.25`, with complete source, rank, factor-log, and blind
descent accounting, or freeze a scoped no-candidate receipt. Do not run the
retired P1514 verifier, construct a Rees algebra, or authorize a solver.

