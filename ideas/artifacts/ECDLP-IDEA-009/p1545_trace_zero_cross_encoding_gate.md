# P1545 trace-zero cross-encoding theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-009`
- Candidate: `P1545`
- Claim: `CLM-P1545-TRACE-ZERO-CROSS-ENCODING-TRANSFER`
- Evidence scale: exact abelian-variety rigidity, Frobenius-module,
  piecewise-algebraic, independent-generic-encoding, and published trace-zero
  index-calculus cost statements; no experiment
- Contract state: no IDEA-009 contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__RATIONAL_TRANSFER_IS_TRANSLATE_OF_A_HOMOMORPHISM__ORDINARY_GEOMETRIC_ENDOMORPHISMS_COMMUTE_WITH_FROBENIUS__ALGEBRAIC_TRACE_ZERO_TRANSFER_KILLS_THE_RATIONAL_ORDER_N_LINE__EACH_NONPASSING_PIECEWISE_ALGEBRAIC_BRANCH_COVERS_AT_MOST_ONE_SCALAR__INDEPENDENT_GENERIC_CROSS_ENCODING_NEEDS_SQUARE_ROOT_WORK__LANG_AND_FROBENIUS_PREIMAGE_ROUTES_REQUIRE_A_BRANCH_OR_EXCEPTIONAL_MODULE__FULL_TRACE_ZERO_INDEX_CALCULUS_IS_SOURCE_RHO_WORSE__SUMMATION_POLYNOMIAL_AND_FFE_BACKENDS_DO_NOT_CONSTRUCT_THE_TRANSFER__ARBITRARY_ADAPTIVE_COORDINATE_EVALUATOR_AND_SPECIAL_IMAGE_LOCUS_UNCLASSIFIED__INCONCLUSIVE`

The exact algebraic P1501 boundary reconstructs, and two additional gates remove
tempting relabelings. First, a finite catalog of rational output formulas cannot
piece together the missing transfer economically: unless one branch is already a
global algebraic transfer, each translated-homomorphism branch agrees with the
desired scalar law on at most one source scalar. Second, two independent generic
order-`N` encodings have no operation that moves the unknown source coefficient into
the target encoding; source collisions require square-root work.

Coordinate access remains deliberately outside the generic gate. A compact adaptive
finite-field algorithm could in principle use nonalgebraic branch predicates to
compute the hidden coefficient. No such evaluator is supplied. Moreover, an oracle
evaluator into the full trace-zero variety would not suffice: the published Gaudry-
Gorla-Massierer complexity is at least linear in `p` for fixed extension degree at
least three, already worse than source rho for `N` asymptotic to `p`. A passing route
therefore needs both a nonalgebraic cross-encoding evaluator and a substantially more
special image locus with complete source relations and blind descent.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-009_nonequivariant_trace_zero_transfer_hypothesis.md`:
  `7fabf5c4fa94353908eb4e1dbf61dfab9b768ce28f8f391b25e69ff994f8e240`
- `/Volumes/Volume/autolab/ecdlp_index_calculus_state/p1501_ordinary_trace_zero_transfer_obstruction.json`:
  `97949bb077a932d777dd10e25f11050a2e326060e5112f45868f6080473978c3`
- `/Volumes/Volume/autolab/ecdlp_index_calculus_state/p1501_ordinary_trace_zero_transfer_obstruction_audit.json`:
  `b0b912521ff0b4568c3214fdd482ef22a1a19015f38f10302d1b66daca5cb61c`
- `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r11_independent_audit.md`:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`
- `ideas/artifacts/ECDLP-IDEA-160/p1544_r1_independent_audit.md`:
  `db68ae68e99952656db3c4b179b94770f73972f2429f240c579879ea0502782f`

The two P1501 JSON files are historical external evidence named by the current focus
queue. This receipt reads them but writes only in the authoritative checkout. It does
not promote their four toy arithmetic cells to crypto-scale evidence.

## Frozen interface

Let

```text
E/F_p be ordinary,
H=<P> subset E(F_p),
ord(P)=N prime,
N asymptotic to p,
Q=[x]P.
```

For a fixed or slowly growing integer `k>1`, let

```text
A=Res_(F_(p^k)/F_p)(E),
Tr=1+F+...+F^(k-1),
T_k=ker(Tr)^0 subset A,
```

where `F` denotes Frobenius and the connected component convention is immaterial on
the admitted prime-order line. A passing transfer must provide a public pointwise
algorithm

```text
tau:H -> T_k(F_p)[N],
tau([a]P)=[a]tau(P),
tau(P)!=O.
```

It must then provide a target-independent locus `Z` containing the transferred line
with a complete relation, factor-log, and blind-target descent path below source rho.

## Algebraic-map rigidity

Every rational map from a smooth group variety to an abelian variety extends to a
morphism, and every such map is a translation of a group homomorphism. Thus a rational
map

```text
f:E --> A
```

has the form

```text
f(R)=t+phi(R),
```

where `t=f(O)` and `phi:E->A` is an algebraic group homomorphism. If `f(O)=O`, the
map is globally additive; there is no rational but nonhomomorphic escape on a dense
open subset of `E`.

A divisor correspondence from `E` to an abelian target induces a homomorphism on
Jacobians. Since `Jac(E)=E`, it enters the same class after its fixed translation is
removed. Changing from rational maps to resultants, divisor traces, or graph equations
does not change this operation.

## Ordinary Frobenius and trace gate

Weil-restriction adjunction identifies

```text
Hom_(F_p)(E,Res(E))
  with End_(F_(p^k))(E).
```

For an ordinary elliptic curve, the geometric endomorphism algebra is commutative.
Every geometric endomorphism therefore commutes with Frobenius. If `P` is Frobenius
fixed and `u` is any admitted endomorphism, then

```text
F(u(P))=u(F(P))=u(P).
```

Hence the image of the rational order-`N` line remains Frobenius fixed. On a fixed
point, trace is multiplication by `k`:

```text
Tr(u(P))=[k]u(P).
```

When `N` does not divide `k`, trace-zero membership forces `u(P)=O`. Therefore an
ordinary algebraic homomorphism either kills `H` or misses the trace-zero target. The
ordinary inclusion is the special case `u=1` and obeys `Tr(P)=[k]P`.

This theorem is scoped to ordinary curves and algebraic maps. Supersingular distortion
maps, exceptional CM presentation effects, and extension degrees divisible by `N` are
controls, not generic ordinary-prime evidence. Taking `k>=N` already has representation
and arithmetic exponent at least one before relation collection.

## Piecewise-algebraic branch theorem

Suppose an evaluator uses a frozen catalog of rational formulas. On one execution
branch `i`, rigidity gives

```text
f_i(R)=t_i+phi_i(R).
```

Let

```text
S=tau(P),
S_i=phi_i(P).
```

For the branch to be correct on `Q=[x]P`, it must satisfy

```text
t_i+[x]S_i=[x]S.
```

If the same branch is correct for two distinct scalars `x` and `y`, subtraction gives

```text
[x-y](S-S_i)=O.
```

Because `N` is prime and `x!=y mod N`, this forces `S_i=S`; substituting back forces
`t_i=O`. Such a branch is already a global algebraic transfer on `H`, contradicting
the ordinary trace gate. Therefore:

```text
every nonpassing rational branch is correct for at most one scalar.
```

An explicit branch catalog covering `H-{O}` needs at least `N-1` formulas or an
equivalent source table, with state exponent one. A compact adaptive decision program
can have exponentially many paths without storing them explicitly; this theorem does
not rule it out. In that case the branch predicates, state updates, and output formula
must be published. They are the candidate nonalgebraic digit operation and cannot be
credited merely because each leaf is rational.

## Independent generic cross-encoding gate

Consider two independently encoded generic cyclic groups of order `N`:

```text
G=<P>,
J=<S>,
Q=[x]P in G.
```

The requested operation outputs `[x]S` in `J`. In the source oracle, every value
computed from `P,Q` has a formal coefficient

```text
a+b*X mod N,
```

where `X` represents the hidden scalar. In the target oracle, the initial value `S`
and every target group operation produce only known constant coefficients `c`; no
target value contains `X`.

A nontrivial equality between two source formal values identifies at most one possible
`X`. With `q` generic operations and equality tests, at most `O(q^2)` formal pairs can
collide. Until such a collision reveals `x`, every returned target value is `[c]S` for
a known `c` and succeeds with probability at most `1/N`. The standard collision count
therefore gives

```text
Pr[success] <= O(q^2/N)+1/N,
```

so constant success requires `q=Omega(sqrt(N))`.

This is a two-encoding specialization of the Shoup/Maurer-Wolf generic technique, not
a non-generic prime-field lower bound. A pairing, common representation, efficiently
computable isogeny, coordinate formula, or other cross-oracle operation changes the
model and must be analyzed explicitly. P1501 closes the algebraic version of that
cross-operation on ordinary trace-zero targets; the arbitrary coordinate version is
the remaining IDEA-009 operation.

## Frobenius-polynomial and Lang-torsor screen

Every public polynomial in Frobenius sends a rational point to a known scalar multiple
of itself:

```text
g(F)P=g(1)P.
```

Its trace is `[k*g(1)]P`, so for `gcd(k,N)=1` a trace-zero output is zero. Projectors,
idempotents, normal-basis changes, and FFE representations of the same Frobenius module
do not change this calculation.

Trying to invert `F-1` or another Frobenius polynomial changes the operation to a
torsor section. On `E[N]`, `P` lies in the `F=1` kernel. In the generic semisimple case
with distinct eigenvalues `1` and `p mod N`, `P` is not in the image of `F-1`. On an
exceptional nonsemisimple module or at a higher division level, a nonempty preimage has
a kernel-sized branch orbit. A scalar-compatible selected preimage then requires the
same aligned branch/orientation operation audited in P1544. Lang surjectivity over the
algebraic closure is an existence theorem; it does not supply a public scalar-compatible
section or a typed source inverse.

## Trace-zero index-calculus cost gate

Gorla and Massierer apply Gaudry index calculus to the trace-zero variety of dimension

```text
d=k-1
```

for fixed prime extension degree `k`. Their heuristic asymptotic time in the base-field
size is

```text
T_full=tilde O(p^(2-2/d)),
d>=2 fixed.
```

This can beat generic attacks on the full group `T_k`, whose size is about `p^d`.
It does not beat rho on the original prime-field subgroup of size `N` asymptotic to
`p`. Relative to `N`,

```text
k=3, d=2: T_full=N^(1+o(1)),
k>=5:     exponent >1,
source rho: N^(1/2+o(1)).
```

For `k=2`, the trace-zero target has dimension one and is another elliptic-curve
encoding; generic rho remains the applicable baseline. Thus even an oracle transfer
into the full trace-zero variety does not justify a relation campaign for the frozen
source objective.

A passing IDEA-009 successor must place `tau(H)` on a target-independent locus `Z`
with a different decomposition law. Since `|tau(H)|=N`, injectivity alone gives no
smoothness. The required theorem must specify factor atoms in the transferred subgroup,
exact source certificates, relation density and rank, factor logarithms, masked target
descent, and conversion back to `x`.

## Summation-polynomial and FFE screen

Semaev polynomials characterize when supplied x-coordinates lift to elliptic points
whose sum is zero. Weil descent, FFE encodings, Groebner bases, resultants, SAT/SMT,
and sparse linear algebra are backends for constructing or solving the resulting
systems. They do not evaluate `tau(Q)` and do not prove that a factor-base atom in the
full trace-zero variety lies in the transferred order-`N` line.

If `tau` is oracle supplied, the standard trace-zero system has the rho-worse cost above.
If equations are augmented to enforce membership in a special image locus, the defining
equations and source inverse of that locus are exactly the missing mechanism. Replacing
one polynomial-system solver by another, changing normal bases, or increasing extension
degree is a control until both the evaluator and the relation-to-target exponent change.

## Named coordinate route screen

### Coordinate root ordering

A lexicographic extension-field root, least normal-basis word, chosen Groebner solution,
or software root number can define a point-valued set map. It is not automatically
stable under equivalent field bases, curve models, or root permutations. No checked
rule obeys `tau([x]P)=[x]tau(P)`. If a rule uses a different rational formula on each
explicit root cell, the piecewise-algebraic branch theorem applies; if it uses compact
adaptive predicates, those predicates remain the unsupplied operation.

### Endomorphism and pairing routes

Ordinary endomorphisms remain in the Frobenius centralizer. A pairing can move a DLP to
a roots-of-unity target only under the usual embedding-degree and torsion-orientation
conditions; it neither constructs a trace-zero point evaluator nor improves the generic
prime-field family. A supplied distortion map is retained as an oracle instrumentation
control.

### Table, interpolation, and learning routes

An explicit table `Q -> [log_P(Q)]S` has `N` entries. Polynomial interpolation through
all source points, a dense point indicator, or a trained exact classifier that stores
equivalent labels has state exponent one. A compact learned or arithmetic circuit is not
rejected by name, but it must be published, independently verified on blind points, and
analyzed as an exact algorithm rather than inferred from toy generalization.

## Complete cost receipt

Use the root model

```text
lambda=max(c,kappa,beta+u0,beta+u+delta,2*beta,
           u+delta_t,beta+v,v),
mu=max(s,beta,kappa).
```

The algebraic and fixed-catalog routes have no nonzero transfer. The independent generic
route has `c>=1/2` for constant success. A full source table has `s>=1`. The published
full trace-zero relation method has relation work exponent at least one relative to
`N`. None passes `lambda,mu<=0.45`.

The only unclassified route is an explicit compact adaptive coordinate evaluator plus
a special image locus. IDEA-009 supplies no construction exponent `c`, representation
degree `kappa`, base `beta`, attempt cost `u`, relation or target densities `delta` and
`delta_t`, rank model, factor-log path, verification `v`, or state `s` for such a route.
Missing parameters are not assigned optimistic zeros.

## Independent findings

1. The P1501 ordinary algebraic/Frobenius obstruction reconstructs, while its four
   arithmetic cells remain toy-scale evidence.
2. Rational maps and divisor correspondences into an abelian target reduce to a fixed
   translation plus a homomorphism.
3. Ordinary geometric endomorphisms commute with Frobenius; on the rational line,
   trace is `[k]`, so an algebraic trace-zero transfer kills `H` when `N` does not
   divide `k`.
4. Unless one branch is already the forbidden global transfer, a fixed rational output
   formula agrees with the desired cross-encoding scalar law on at most one scalar.
5. Independent generic source and target encodings require square-root work to move the
   unknown coefficient into the target encoding.
6. Frobenius polynomials are scalar on rational points. Frobenius/Lang preimages are
   empty on the generic semisimple line or require a selected torsor branch in exceptional
   modules.
7. Standard full trace-zero index calculus is at least linear in `p` for fixed
   `k>=3`, above rho for the original order-`p` subgroup.
8. Summation polynomials and FFE are relation-system backends; they supply neither the
   transfer nor a source-invertible special image locus.
9. An arbitrary compact adaptive coordinate evaluator with a decomposition-changing
   image locus remains unclassified, but no explicit candidate or complete cost exists.

## Disposition and next action

P1545 is terminal inconclusive within ordinary algebraic maps and correspondences,
fixed piecewise-rational catalogs, independent generic encodings, Frobenius-polynomial
and named Lang-preimage routes, full trace-zero index calculus, and the screened
summation-polynomial/FFE backends. Preserve P1501, IDEA-009, and this receipt. Do not
draft or execute an IDEA-009 relation campaign.

Exactly one next action: rerank outside local lifts, torsion orientation, algebraic
trace-zero transfers, independent cross-encodings, and full trace-zero decomposition.
Bind one mechanism-distinct P1546 theorem question. Reopening IDEA-009 requires an
explicit pointwise coordinate program, model-invariance rule, transferred image-locus
equations, exact source inverse, and complete relation-to-target cost in the proposal.

No generic-prime ECDLP recovery, relation campaign, factor-log solve, blind descent,
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Primary references

1. J. S. Milne, *Abelian Varieties*, Section 3, rational maps into abelian varieties,
   <https://www.jmilne.org/math/CourseNotes/AV.pdf>.
2. Claus Diem and Nils Naumann, *On the Structure of the Weil Restriction of Abelian
   Varieties*, <https://arxiv.org/abs/math/0504359>.
3. Elisa Gorla and Maike Massierer, *Index Calculus in the Trace Zero Variety*,
   <https://arxiv.org/abs/1405.1059>.
4. Ueli Maurer and Stefan Wolf, *Lower Bounds on Generic Algorithms in Groups*,
   <https://crypto.ethz.ch/publications/MauWol98e.html>.
5. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>.

These sources establish the algebraic-map, Weil-restriction, trace-zero index-calculus,
and generic-model controls. The piecewise-algebraic one-scalar lemma and the independent
two-encoding coefficient argument above are direct deductions. None supplies the
missing nonalgebraic pointwise transfer, special image locus, or generic-prime sub-rho
ECDLP algorithm.
