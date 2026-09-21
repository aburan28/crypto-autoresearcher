# P1538 bounded-state local-norm closure audit

## Record status

- Candidate roots: `ECDLP-IDEA-102` and `ECDLP-IDEA-195`
- Focus experiment: `P1538`
- Expansion of: `P1537`
- Artifact class: independent theorem-only reconstruction and scoped no-candidate audit
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__VALUE_SPACE_CLOSURE_EXACT__INTERIOR_PROJECTOR_BREAKS_TRANSLATION_CLOSURE__BOUNDARY_LINEAR_TRANSFER_FAILS_RANK_DENSITY__NONLINEAR_IMPLICIT_RECURRENCE_UNSUPPLIED`
- Evidence scale: exact dual-number, projector, tensor-flattening, and cost audit;
  no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract, verifier, solver, finite-field fixture, or relation campaign: none

The seven-channel P1537 message is already closed under multiplication in a
seven-dimensional square-zero algebra. That exact local identity preserves a
singleton source and all five coordinate ratios, but it processes one message per
child block and therefore does not compress the `B^5` leaf domain.

This audit tests the nearest stronger proposal: use a finite-field transfer,
star-triangle, Yang-Baxter, matchgate, or matrix-product identity to contract the
domain while preserving the seven channels. It separates two placements of the
factor-base restriction. If a diagonal factor-base projector is inserted into a
translation-covariant regular-state local identity, it is noncentral for every
proper nonempty factor base and that specific closure is lost. If the projector is
left at the boundary, bulk integrability can survive; the prior wording that every
factor-base indicator necessarily breaks the identity was too broad. But the exact
target-versus-source transfer object then has flattening rank equal to the endpoint
support. Any explicit linear transfer state with one accepted simple witness obeys
the favorable work envelope

```text
max(S,B*N/S) >= sqrt(B*N) = N^(3/5)       for B=N^(1/5).
```

The same bound applies after adjoining the six derivative channels because
reduction to the constant channel recovers the original incidence matrix. Local
Yang-Baxter moves, gauge changes, canonical MPS forms, or Pfaffian rewrites preserve
the represented tensor and cannot lower this flattening rank when their cut state
is explicit.

This is a scoped result. It does not lower-bound an implicit FFT-like evaluator, a
nonlinear arithmetic recurrence, a multirow source generator, or a target batch
that is never materialized as linear components. No such operation is supplied by
IDEA-102, IDEA-195, the concurrent IDEA-242 record, or the audited controls. P1538
therefore closes terminal inconclusive and returns the two roots to theorem-deferred
status. There is no sub-rho ECDLP algorithm or breakthrough.

## Frozen inputs and hashes

```text
P1537 independent jet-preserving compositional-intertwiner audit
5b0112a1efc6043150d998fb1c38217c602a00186f7982443aaab7a443acf249

IDEA-102 elliptic dynamical-R transfer hypothesis
9a42e6f725a3c38f437e9ba8b861df7c83cc70877f21bb4dc3b4af9211df2546

IDEA-242 coloured norm-jet compositional-tower hypothesis
3aac5da1508f68059a186cdf6b8f9ae3d272a2906403588f83ac560154bbe338

IDEA-253 injective-MPS gauge source-lift hypothesis
2f7fc358b0a9a2deb825e2c47495ba0ccb5a45582547e841f0b4585c955ba741

IDEA-001 exact spectral rank/density gate
e572713a3910ef6a3e31ac360123aa8b5135c75d4210cbfb579e6831e9746fca

IDEA-050 shared-basis matchgate derivation gate
5059de6ae5e67acf73759e61b53bf57174cc95bbdf4c1f29d51dd2fc6cf82e0c
```

IDEA-242 appeared from a concurrent corpus writer after P1537 was hash-bound. Its
mechanism is the same operation-level question as P1537: norm transitivity plus
first-order jet transport through a composition tower, followed by a bounded exact
branch inverse. It is consumed here as a semantic duplicate/control, not promoted
as an independent mechanism. The concurrent record remains untouched.

## 1. Frozen coloured transfer tensor

Let `G=<P>` have prime order `N`, and let

```text
F_1,...,F_5 subset G
```

be disjoint public coloured factor decks of size `Theta(B)`. Signs and Kummer
charts are frozen as in P1537. For an endpoint `R in G`, define the exact coloured
incidence tensor

```text
I(R;a_1,...,a_5) = 1 if a_1+...+a_5=R,
                    0 otherwise,
```

for `a_i in F_i`. Put

```text
C = F_1+F_2+F_3+F_4+F_5,
S = |C|.
```

The P1537 marked norm uses

```text
D = F_p[e_0,...,e_5]/(e_a*e_b : 0<=a,b<=5)
```

and returns one constant plus six derivative channels. On an endpoint with exactly
one accepted coloured source tuple, its ratios recover all five x-coordinates. An
endpoint with zero tuples has nonzero norm constant, while two or more zero leaves
annihilate the complete first jet.

Let `U subset C` be the endpoints having exactly one accepted coloured source under
all frozen sign, repetition, infinity, and chart rules. Only `U` can produce the
simple-fiber one-witness rows audited here, and

```text
|U| <= S.
```

## 2. Exact value-space closure is the positive control

Write a local seven-channel message as

```text
M = c + sum_(j=0)^5 e_j*d_j in D.
```

For child messages `M_a`, multiplication in `D` gives

```text
C       = product_a c_a,
D_j     = sum_a d_(a,j) product_(b!=a)c_b.        (1)
```

Associativity and commutativity imply the exact local identities

```text
(M_1*M_2)*M_3 = M_1*(M_2*M_3),
M_1*M_2       = M_2*M_1.                          (2)
```

Thus any binary tree, transfer direction, or bounded local regrouping returns the
same seven top coefficients. Equation (2) is the minimal finite-field
star/associativity positive control. It is exact in every characteristic and
requires no analytic theta functions.

But the seed contains one scalar factor for each coloured source tuple. A binary
tree changes depth and live value-space dimension, not the number of seed messages:

```text
number of leaves = |F_1|*...*|F_5| = Theta(B^5).
```

The fixed seven-dimensional algebra is therefore not the bounded-domain family
`C_j` required by P1538. A qualifying identity must aggregate the functions over
many source blocks before their individual values are formed.

## 3. Where the factor-base projector lives

An integrable full-state model and the restricted ECDLP tensor are distinct
objects. Let `V=k[G]` be the regular state space with basis `{delta_x:x in G}`.
For `t in G`, let

```text
T_t delta_x = delta_(x+t)
```

and let the diagonal projector for a public subset `F subset G` be

```text
P_F delta_x = 1_F(x) delta_x.
```

There are three possible placements.

1. `P_F` is inserted inside every local weight or transition.
2. `P_F` remains on an external source boundary leg.
3. `P_F` is treated as an integrable defect with its own intertwining equation.

These placements must not be conflated. A boundary weight can leave a bulk
Yang-Baxter identity unchanged even though an interior insertion destroys the
same local family. This corrects the broad form of IDEA-102's indicator objection.

## 4. Interior projector theorem for the translation-regular control

For every `t in G`, direct evaluation gives

```text
P_F T_t delta_x = 1_F(x+t) delta_(x+t),
T_t P_F delta_x = 1_F(x)   delta_(x+t).
```

Therefore

```text
P_F T_t = T_t P_F for every t in G
```

if and only if `1_F(x+t)=1_F(x)` for all `x,t`. Because the regular action of `G`
is transitive, this holds if and only if

```text
F is empty or F=G.                                (3)
```

Consequently a proper nonempty factor-base projector is not a central
translation-covariant local weight. Any star-triangle or transfer identity whose
closure proof requires every inserted local operator to commute with the regular
translations loses that proof after the projector is inserted.

This theorem is deliberately scoped. Some integrable models admit noncentral
boundaries or defects satisfying reflection, defect Yang-Baxter, or separate
intertwining equations. P1538 would have to exhibit that equation over the finite
field for the actual rational factor-base predicate. Naming a defect, boundary
matrix, or spectral parameter is not such an equation.

## 5. Boundary projector branch

Leave `P_(F_i)` on the five physical source legs and keep the bulk identity on its
native state space. Then the global restricted tensor is still exactly `I`; the
local identity may reorder its contraction without changing endpoint/source
incidence.

Flatten `I` with endpoint rows and complete source-tuple columns. The column for
`(a_1,...,a_5)` is the standard basis vector

```text
delta_(a_1+...+a_5).
```

The distinct columns are precisely `{delta_R:R in C}`. Hence over every
coefficient field

```text
rank I_(R | a_1,...,a_5) = S.                    (4)
```

This is an exact identity. It does not rely on generic tensor-rank heuristics,
toy curves, or random factor bases.

## 6. Explicit linear transfer-state theorem

Consider a target-uniform linear transfer realization in which all endpoint
dependence crosses one represented cut state of dimension `r`. After fixing its
public local weights, gauges, and transfer direction, it has the separated form

```text
I(R;a_1,...,a_5) = sum_(j=1)^r A_j(R) B_j(a_1,...,a_5).    (5)
```

This includes an explicit retained character list, an explicit transfer boundary
vector, a matrix pairing after vectorizing its entries, and an MPS sweep after the
cut bonds are tensor-producted. Equation (4) implies

```text
r >= S.                                           (6)
```

An invertible Yang-Baxter move, star-triangle move, local basis change, MPS gauge
normalization, or exact matchgate rewrite changes the factors in (5) but not the
represented tensor. It therefore cannot lower the target/source flattening rank.
If a network has several cut bonds, `r` is their product dimension, namely the
actual transfer state carried across that cut.

This does not claim that every compact arithmetic circuit has cost proportional to
matrix rank. An FFT is the standard warning: a full-rank transform can have a fast
implicit algorithm. Equation (6) closes only realizations that retain, traverse,
or materialize their exact linear cut state or components.

## 7. The derivative channels do not remove the rank gate

Let an exact seven-channel transfer over `D` have represented cut module `W` and
produce

```text
J = J_empty + e_0*J_0 + ... + e_5*J_5.
```

Reducing modulo `(e_0,...,e_5)` returns the constant-channel incidence/norm
transfer. Any separated `D`-linear representation of rank `r_D` therefore reduces
to a representation of `I` with rank at most `r_D`, so

```text
r_D >= S.                                         (7)
```

Tangent insertions may make source recovery possible on a singleton fiber, but
they cannot make the constant-channel flattening smaller. Conversely, retaining
only the constant partition function or norm-zero bit fails exact source output.
The seven channels are necessary for the P1537 inverse and nonbeneficial for the
explicit linear state lower bound.

## 8. Exact rank-density cost envelope

A uniformly sampled known-log endpoint lands in the accepted simple set `U` with
probability `|U|/N`. Even under the favorable assumptions that every accepted
endpoint returns one independently useful row and all target queries outside `U`
are otherwise free, collecting `B` rows needs at least

```text
L_rel >= B*N/|U| >= B*N/S                       (8)
```

attempts in expectation.

An explicit linear transfer state pays at least `S` represented components by
(6) and at least `B*N/S` target attempts by (8). Therefore

```text
W >= max(S,B*N/S) >= sqrt(B*N).                  (9)
```

At the frozen campaign value `B=N^(1/5)`,

```text
W >= N^(3/5).                                    (10)
```

The optimum already exceeds rho and the generic Shoup boundary before charging
weight construction, poles, derivative channels, source conditioning, failed
colourings, rank defects, factor-log linear algebra, masked descent, verification,
output, or memory traffic.

The P1538 state cap `B^2.25=N^0.45` is also incompatible with an explicit support
state near the favorable optimum `S=sqrt(BN)=N^0.6`. Forcing `S<=N^0.45` only makes
the attempt term at least `B*N/S=N^0.75`.

## 9. Standard route screens

### 9.1 Dynamical Yang-Baxter and star-triangle

Felder-type elliptic dynamical weights are an exact positive control on their
native analytic/algebraic state data. They do not by themselves identify the
ECDLP curve, the public rational factor decks, or conditioned leaf coordinates.

- Interior factor-base projectors fail the translation-regular centrality control
  in (3), unless a new finite-field defect equation is proved.
- Boundary projectors may preserve the bulk identity, but an explicit target/source
  transfer state obeys (6)-(10).
- A commuting transfer family or partition function without the six tangent
  channels is source-incomplete.
- Bethe roots or spectral divisors are supplied state unless an endpoint-only
  compiler and exact conditioned source inverse are given and charged.

No explicit finite-field weight/defect equation satisfying all four requirements is
present in IDEA-102.

### 9.2 Matchgate and Pfaffian networks

IDEA-050 correctly places every source choice inside an arity-eight Boolean tensor
before asking for a shared matchgate basis. Its frozen finite checks are controls,
not theorem evidence here. A supplied Pfaffian signature contracts efficiently,
but compiling generic five-source incidence into that signature is still the
missing operation.

IDEA-243's concurrent Pfaffian-derivative router reaches the same boundary: a
source-faithful skew pencil materializes the incidence tensor, while complementary
Pfaffians after a source position is known repeat derivative localization. An exact
Pfaffian rewrite of a supplied tensor does not alter (4).

### 9.3 Matrix-product and transfer gauges

IDEA-253's injective-MPS proposal fixes internal gauge nonuniqueness only after the
global state/tensor and physical dictionary are supplied. For a sweep separating
the endpoint from all source legs, the product bond dimension is at least `S` by
(4). A compact local description with an implicit high-rank state lies outside this
explicit-state theorem and still needs an endpoint compiler plus exact source
unranking.

### 9.4 Norm-jet composition tower

The concurrent IDEA-242 hypothesis and P1537 share the same exact positive theorem:
norm transitivity and square-zero chain rules preserve the seven channels. Equation
(1) is already the complete local update. Calling the seven-value message a transfer
state does not aggregate its `B^5` domain. A bounded exact branch inverse after an
explicit source path is supplied is not a constructor for that path.

### 9.5 ECFFT, Lattes, and special decks

P1537 already screens these realization classes. ECFFT provides an auxiliary
polynomial tree without a target Semaev intertwiner. Lattes maps are permutations on
the rational prime subgroup after Kummer sign, while geometric fibers create
multiple zero leaves. Power, Dickson, and extension-field decks are restricted-prime
or lose rational source return. Integrable notation does not change those map
obstructions.

## 10. What remains outside the theorem

The following operations are not disproved:

1. a nonlinear arithmetic recurrence that consumes a succinct description of all
   endpoints without retaining an `S`-component linear state;
2. an implicit target batch whose successful endpoints and exact source rows are
   emitted without touching failed targets separately;
3. a multirow generator whose output-sensitive cost and independent row rank beat
   the one-simple-witness model;
4. a finite-field defect or boundary identity specialized to the actual rational
   factor-base predicate, with a compact endpoint-only compiler and exact source
   conditioning; or
5. a list-specific support-changing operation that changes `C` rather than linearly
   refactoring the same incidence tensor.

To reopen P1538, one of these must be written as explicit equations. It must define
the representation family, constructor, every seven-channel update, exceptional
branches, source inverse, and complete costs. Merely naming FFT, FFE, Yang-Baxter,
Bethe ansatz, matchgate, MPS, ECFFT, norm transitivity, or a spectral curve is not an
executable candidate.

## 11. Complete-path accounting

Under the favorable simple-rainbow model, let setup and resident state be
`B^s,B^m`, per-target work be `B^kappa`, accepted relation density be
`N^(-delta)`, output exponent be `N^o`, rank gain be `N^r`, target ambiguity be
`N^u`, and factor-log completion be `N^ell,N^ell_m`. The complete path remains

```text
lambda = max(s/5,(1/5)+delta+kappa/5-r+o,ell,
             delta_t+kappa/5+o+u,1/5),

mu     = max(m/5,1/5+o,ell_m,u).
```

P1538 requires `s,m<=2.25`, `kappa<=1.25`, and complete
`lambda,mu<=0.45`. The explicit linear branch fails earlier by (10). No audited
nonlinear branch supplies upper bounds for the constructor, density, rank, factor
logs, masked descent, or memory, so it cannot be promoted by omission.

## 12. Route dispositions

| Route | Independent disposition |
|---|---|
| Seven-dimensional dual-number value messages | exact closure, `B^5` seed work |
| Associativity/commutativity regrouping | exact local positive control, no domain compression |
| Proper interior projector in translation-regular state model | noncentral; scoped closure failure |
| Factor-base projector on boundary legs | bulk identity may survive |
| Exact endpoint/source incidence flattening | rank exactly `S=|F_1+...+F_5|` |
| Explicit linear transfer/MPS cut state | state at least `S` |
| Seven derivative channels | source-complete on singleton; rank at least constant-channel rank |
| One-simple-witness explicit linear transfer | favorable work at least `sqrt(BN)=N^0.6` |
| Matchgate/Pfaffian rewrite of supplied tensor | representation control; constructor missing |
| MPS canonical gauge of supplied state | gauge control; physical dictionary/source compiler missing |
| IDEA-242 norm-jet tower | semantic duplicate of P1537 transport question |
| Nonlinear implicit batch or arithmetic recurrence | outside theorem; no object supplied |
| Finite-field factor-base defect equation | outside theorem; no object supplied |

## 13. Independent decision

P1538 reconstructs one exact finite-state identity only in value space and closes
the nearest explicit linear integrability realizations. Its scoped disposition is

```text
INDEPENDENT_SCOPED_AUDIT_PASS__VALUE_SPACE_CLOSURE_EXACT__INTERIOR_PROJECTOR_BREAKS_TRANSLATION_CLOSURE__BOUNDARY_LINEAR_TRANSFER_FAILS_RANK_DENSITY__NONLINEAR_IMPLICIT_RECURRENCE_UNSUPPLIED
```

The retained corrections and theorems are:

```text
boundary factor-base weights need not break a bulk integrability identity;

interior proper factor-base projection is noncentral in the regular translation
control;

explicit exact linear endpoint/source transfer state + one simple witness
    => work at least sqrt(B*N)=N^0.6 for B=N^0.2;

adjoining the P1537 first jet preserves, rather than removes, that rank gate.
```

The negative scope is explicit linear cut states/components, translation-regular
interior projectors, supplied matchgate/Pfaffian/MPS tensors, and reassociation of
the local norm product. It is not an arithmetic-circuit lower bound and does not
exclude nonlinear implicit batching, multirow output, or a new factor-base defect
identity.

No explicit survivor, relation campaign, factor-log solve, blind descent,
generic-order result, Shoup-bound improvement, or breakthrough exists.

## Exactly one next action

Close P1538 terminal inconclusive, return IDEA-102 and IDEA-195 to
theorem-deferred status, and rerank the focus queue without creating another
integrability/transfer successor. Reopen this lane only when a mechanism-new record
supplies an explicit nonlinear seven-channel recurrence or finite-field factor-base
defect equation together with its endpoint compiler, exact source inverse, and
complete sub-rho costs. Do not run either retired contract or any concurrent retired
preflight.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.
- Felder, *Elliptic quantum groups*:
  <https://arxiv.org/abs/hep-th/9412207>.
- Etingof, *Geometric crystals and set-theoretical solutions to the quantum
  Yang-Baxter equation*: <https://arxiv.org/abs/math/0112278>.
- Perez-Garcia, Verstraete, Wolf, and Cirac, *Matrix Product State
  Representations*: <https://arxiv.org/abs/quant-ph/0608197>.
- Knuth, *Overlapping Pfaffians*: <https://arxiv.org/abs/math/9503234>.

These sources supply the summation-polynomial, generic lower-bound, integrability,
MPS, and Pfaffian controls. None supplies a finite-field arbitrary-factor-base
defect, nonlinear seven-channel implicit recurrence, exact point-source inverse,
or a complete generic-prime ECDLP improvement.
