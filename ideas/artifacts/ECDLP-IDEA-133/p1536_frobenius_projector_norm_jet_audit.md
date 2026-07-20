# P1536 independent Frobenius-projector and norm-jet audit

## Record status

- Candidate root: `ECDLP-IDEA-133`
- Focus experiment: `P1536`
- Expansion of: `P1514`
- Artifact class: independent theorem-only reconstruction and scoped no-candidate audit
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__NO_TRACE_RECURRENCE__COLOURED_NORM_JET_SUCCESSOR`
- Evidence scale: exact finite-field identities, representation, literature, and cost audit;
  no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract, verifier, solver, or elliptic fixture: none

The Frobenius projector is exact, but the original singleton interpretation needs a
symmetry correction. On five copies of one factor deck, `S_6` is symmetric, so a generic
all-distinct source occurs with all `5!=120` ordered permutations. The six first moments
from P1535 therefore do not generically recover five coordinates.

This audit gives two exact repairs. Higher moments recover one unordered permutation
orbit, and five target-independent colour decks turn an all-distinct relation into a
genuine simple coloured fiber with constant density loss. For the coloured fiber, a
first-order dual-number norm jet detects uniqueness and returns all five x-coordinates.
The identity is exact and source-free, but every audited implementation of the jet still
constructs or traverses a `B^5` quotient, a `B^3` split side, or an equivalent resultant
payload. No setup-`B^2.25`, query-`B^1.25` recurrence is supplied.

The surviving question is narrower than the original projector claim: whether a compact
compositional factor deck has a jet-preserving non-Cartesian intertwiner that contracts
the coloured first jet before the Cartesian source product is formed. That question is
routed separately. It is not a sub-rho ECDLP algorithm or a breakthrough.

## Frozen inputs and hashes

```text
P1535 independent audit
5d054c32e9cc60de1b5ab0742182e4932fee4c25a4338d07acc893b6c4307712

P1514 append-only scope correction
d718a341153f1ea805c59fe1f45511712fda1805fbcc61103bbe9f1f4159866f

P1533 derivative-resultant control
0de12da09c1bc49aa577431cff5ac09a264a367bce57aa1699c495015c28803f

P1515 compressed-navigator and 2026 kSUM-indexing control
dadcadf45bdea910f0a12e904bdfe32c4a517b0756ef08148de75fb39929e3e5

IDEA-195 non-Cartesian S3 intertwiner hypothesis
b52403859590a549f621fce1d2d71ab2e4da2d90faacbf9c0d3d48fcdb2bc513

P1526/P1527/P1528 ECFFT and Lattes gates
f8abb802b5052f614a6500c722083d3ebbd45d6e54353686ff3283ffa27a88b7
e4972a1c6f4fb796a9efa556c745c4d4d5e4b00e5637e9fca9f3828abb4db120
342e872f1e86297d88bb8684155ed84cf7c3b37351402fba4c296ff986ab141e
```

## 1. Exact projector reconstruction

Let `k=F_p`, let `F_x subset k` be a square-free rational x-coordinate deck of
size `B`, and put

```text
f_F(T)=product_(a in F_x)(T-a),
A_F=k[T]/(f_F),
A_5=A_F tensor_k ... tensor_k A_F.
```

The evaluation map identifies `A_5` with `k^(F_x^5)`. For a finite target chart
with x-coordinate `x_R`, let

```text
g_R=S_6(T_1,T_2,T_3,T_4,T_5,x_R) in A_5.
```

Fermat's identity gives the exact coordinate projector

```text
chi_R=1-g_R^(p-1).
```

For every ordered tuple `a in F_x^5`,

```text
chi_R(a)=1  iff  S_6(a_1,...,a_5,x_R)=0.
```

Consequently, for every multi-index `nu`,

```text
M_nu(R)=Tr_(A_5/k)(T^nu*chi_R)
       =sum_(a in supp(chi_R)) a^nu.
```

This reconstructs P1535 exactly. It is a semantic constructor for the desired moment,
not an algorithm for evaluating the trace in the required cost rectangle.

## 2. Append-only permutation-symmetry correction

The P1535 statement that six traces recover a singleton support is algebraically true,
but a singleton is not the generic same-deck fiber. Since `S_6` is symmetric, an ordered
root with multiplicity profile `lambda=(m_1,...,m_j)` contributes an orbit of size

```text
r(lambda)=5!/(m_1!*...*m_j!).
```

The possible single-orbit sizes are

```text
1, 5, 10, 20, 30, 60, 120.
```

An all-distinct relation contributes `120` ordered roots. For one complete permutation
orbit, every first coordinate moment is the same:

```text
M_(e_i)=(r/5)*(a_1+...+a_5),       i=1,...,5.
```

Thus the five P1535 coordinate traces are redundant on the generic orbit and do not
recover the tuple. This corrects the use of the singleton formula without changing the
projector theorem or rewriting the immutable P1535 receipt.

There is an exact same-deck repair. If the support is exactly one permutation orbit, then

```text
M_(j*e_1)=(r/5)*sum_(i=1)^5 a_i^j,       j=1,...,5.
```

The orbit size `r=M_0` and these five power sums recover the unordered multiset of x-values
by Newton identities. Repeated values are retained with their multiplicities. This needs
higher moments but only a fixed number at arity five.

Multiple source orbits can have a total ordered size equal to one allowed orbit size, so
`M_0` alone is not a sound one-orbit certificate. A complete same-deck acceptor needs
additional mixed moments or direct verification of a reconstructed orbit against the full
projector support. Supplied moments remain an inadmissible constructor oracle.

## 3. Exact coloured-deck repair

Partition a target-independent factor deck into five public disjoint colour classes

```text
F_x=F_1 disjoint_union ... disjoint_union F_5,
|F_i|=Theta(B),
f_i(T)=product_(a in F_i)(T-a).
```

Use the coloured split algebra

```text
A_col= tensor_(i=1)^5 k[T_i]/(f_i),
D=dim_k(A_col)=product_i |F_i|=Theta(B^5).
```

Permuting an all-distinct source tuple moves its entries to the wrong colour factors, so a
relation containing one source from every colour has one ordered coloured representative.
For a random public five-colouring, an all-distinct source multiset is rainbow with
probability

```text
5!/5^5,
```

a positive constant. A constant family of independent public colourings can amplify this
constant without changing an exponent. The colourings must be fixed before targets and all
their setup, failed queries, duplicate relations, and output are charged.

The colour restriction excludes repeated use of one factor point within one coloured
query. It therefore targets the generic all-distinct stratum rather than claiming all-strata
recovery. Repeated-source relations can be rejected; a full algorithm must prove that the
remaining rainbow relation density and signed row distribution still give rank `B`.

## 4. Exact first-order norm jet

Work in the coloured algebra and define the finite locally free norm polynomial

```text
R_R(t,s_1,...,s_5)
  =Norm_(A_col/k)(g_R+t+sum_(i=1)^5 s_i*T_i)
  =product_(a in F_1 x ... x F_5)
       (g_R(a)+t+sum_(i=1)^5 s_i*a_i).
```

Suppose the coloured x-support is the singleton `{a*}`. At the origin, exactly one factor
vanishes. Therefore

```text
R_R(0,0)=0,

dR_R/dt (0,0)=product_(b != a*) g_R(b) != 0,

dR_R/ds_i (0,0)
  =a_i* product_(b != a*) g_R(b),

a_i*=(dR_R/ds_i)(0,0)/(dR_R/dt)(0,0).
```

The branches are exact:

```text
empty support:       R_R(0,0) != 0;
singleton support:   R_R(0,0)=0 and dR_R/dt(0,0) != 0;
support size >=2:    R_R and every first derivative vanish at the origin.
```

Thus one constant-size first jet detects an empty or simple coloured fiber and returns all
five x-coordinates on the simple branch. At most `2^5` sign assignments plus fixed infinity
and exceptional-chart branches then recover and verify every signed lift. No primitive
idempotent, source list, supplied moment, or post-hoc label occurs in the identity.

Equivalently, if `M_g` is multiplication by `g_R`, the derivatives are determinant and
adjugate contractions of the structured operator

```text
M_g=S_6(C_1,...,C_5,x_R),
```

where `C_i` is the companion multiplication for `f_i`. On a corank-one simple fiber,
the adjugate is a rank-one source projector and the derivative ratios are its five coordinate
Rayleigh quotients. This matrix wording is not a cheaper realization.

## 5. Same-deck higher norm jet

The norm identity also repairs the uncoloured permutation orbit, but at a higher constant
derivative order. If the same-deck support is exactly one orbit of size `r`, the first nonzero
homogeneous term has degree `r`. Restricting to `s_2=...=s_5=0` gives

```text
H_r(t,s_1)
  =C*product_(a in orbit)(t+s_1*a_1)
  =C*product_v (t+s_1*v)^(r*m_v/5),
```

where `m_v` is the multiplicity of x-value `v` in the source multiset and `C` is the
nonzero product over nonsupported tuples. Factoring the degree-`r` binary form and using

```text
m_v=5*exponent_v/r
```

recovers the multiset. Since `r<=120`, the derivative order is constant asymptotically,
although it is not a practical small constant on the all-distinct stratum.

This observation does not solve the constructor problem. Computing a degree-120 leading
jet of a norm over `B^5` coordinates is not cheaper merely because the returned object has
constant degree. Multiple permutation orbits also require a sound orbit-separation rule.
The coloured first jet is the sharper successor interface.

## 6. Generic triangular-set and resultant routes

The direct quotient presentation has multidegree

```text
(|F_1|,...,|F_5|),
delta=product_i |F_i|=Theta(B^5).
```

Poteaux and Schost's square-free triangular-set algorithms compute multiplication,
inversion, norm, modular composition, and power projection quasi-linearly in `delta` (up
to their stated finite-field and bit-complexity factors). Their result removes an exponential
overhead in the number of variables; it does not replace `delta` by the constant output-jet
size. Instantiating it here therefore costs `B^(5+o(1))`, outside every P1536 cap.

An iterated resultant writes the same norm as

```text
Res_(T_1)(f_1, ... Res_(T_5)(f_5,g_R+t+sum s_i*T_i) ...).
```

Truncating in `(t,s)` after first order controls only the deformation degree. It does not
control degrees or coefficient traffic in the four surviving source variables after the
first elimination. Balanced elimination and primitive-element conversion likewise retain
the product quotient dimension unless an additional factorization identity is proved.

The multivariate resultant-complexity literature supplies caution about generic succinct
resultants, but no generic hardness statement is used as a lower bound for this structured
Semaev family. The disposition is representation-specific.

## 7. Split, kSUM-indexing, and formal-circuit controls

The exact known controls remain:

| Route | Charged consequence | Disposition |
|---|---|---|
| Dense projector or norm jet | `Theta(B^5)` values or quotient coordinates | fails |
| Reusable `2+3` support | `Theta(B^3)` setup/state | fails setup and memory |
| Streamed `2+3` support | `Theta(B^3)` per target, `Theta(B^4)` campaign | fails time |
| Formal repeated squaring | `O(log p)` gates before quotient reductions and tensor traffic | no charged trace algorithm |
| Generic triangular power projection | `B^(5+o(1))` in quotient dimension | fails |
| P1533 derivative-resultant pattern | exact ratio, missing evaluator and source localizer | semantic control |
| Supplied first jet or moments | exact positive correctness control | constructor omitted |

Dinur and Golovnev's 2026 `kSUM`-Indexing theorem is already frozen in the P1515
compressed-navigator receipt. A five-source query is its `k=6` case. The theorem's
preprocessing builds `(k-1)`-sum information in `B^(5+o(1))` time; its sublinear-query
advice has exponent at least `B^4.5` in the stated range. It therefore does not implement
the coloured norm jet inside `B^2.25/B^1.25`. This is an upper-bound control, not a
conditional or unconditional lower bound.

The constant separation rank of the fixed polynomial `S_6` also does not suffice. Even
the linear polynomial `T_1+...+T_5-x_R` has constant tensor rank while retaining the
five-list sum-indexing problem. A passing contraction must exhibit a new operation, not
only a low-rank expression for tuple membership.

## 8. Special multiplicative and compositional decks

If `B` divides `p-1`, a deck `f(T)=T^B-c` has a compact multiplicative-coset
presentation. This is not a generic-prime factor deck: the required divisor need not exist
at size `p^(1/5+o(1))`. Moreover, retaining only x-values that lift to rational points applies
the quadratic-character filter to `x^3+Ax+B_E`; the surviving factor polynomial is no longer
the monomial deck unless a separate curve-specific identity preserves it. Treating every
coset x-value as a factor point creates false sources.

A compositional polynomial

```text
f=h_d composed ... composed h_1
```

can describe a root tree compactly, but compact roots alone do not contract a five-way
Semaev norm. A generic final coupling still joins five independent leaves. Recursion helps
only if one proves an intertwiner carrying the relevant norm jet through each `h_i` while
retaining a bounded exact source inverse.

For Lattes or isogeny-induced maps, P1526-P1528 give the current scoped controls:
same-field maps are injective on the prime target subgroup below degree `N`, rational kernel
branching is bounded by the subpolynomial cofactor, and kernel-coset lifts duplicate image
log columns. P1527 closes only one canonical list-restricted degree-two family. Other
non-Cartesian maps remain open, but their intertwiner must be written explicitly.

## 9. Extension-field and FFE screen

Moving the deck to `F_(p^d)` can make roots of unity or composition branches available,
but it does not automatically produce rational factor points.

1. A multiplicative subgroup of order `B` requires `B | p^d-1`; uniformly small `d` is
   not guaranteed for a generic prime and chosen `B`.
2. Geometric roots outside `F_p` are not x-coordinates of `E(F_p)` factor points. A public
   trace, norm, or descent map to rational points and every fiber must be charged.
3. A group-homomorphic trace from an extension-field subgroup of order coprime to the
   prime target order has trivial image in that target subgroup. N-torsion lifts instead
   restore N-scale orientation or duplicate one rational image column.
4. A nonhomomorphic coordinate map can have useful images only after it proves rational
   lift density, exact inverse lists, rank after projection, and identical blind descent.
   Merely applying field trace to x-coordinates does not preserve elliptic addition.

No audited FFE route supplies a generic-prime rational coloured deck, a jet-preserving
intertwiner, and a full-rank target-group return inside the cap.

## 10. Relation, rank, factor-log, and descent accounting

At `B=N^(1/5)` and under the favorable random-support model, one unordered all-distinct
x-source orbit has constant expected density. A fixed random five-colouring keeps a rainbow
orbit with probability `5!/5^5`, also constant. These statements are heuristic and
model-bound until a family-specific density theorem or approved measurement exists.

If a jet query costs `B^kappa`, `Theta(B)` known-scalar relation targets cost
`B^(1+kappa)`. With setup and state `B^s,B^m`, the optimistic gate is

```text
lambda >= max(s/5,(1+kappa)/5,2/5,1/5),
mu     >= max(m/5,1/5),
```

before failed colourings, output, rank defects, signed ambiguity, and blind descent. The
P1536 rectangle `s,m<=2.25`, `kappa<=1.25` is necessary, not sufficient.

Rainbow rows must independently reach rank `B`; exact signed lifts may help avoid the four
block-sum dependencies of unsigned one-per-colour rows, but no rank theorem is supplied.
Every factor logarithm must be independently verified. The same public colour family,
simple-fiber test, jet constructor, sign lift, and failure policy must then decompose fresh
masked targets `Q+[t]P`. No target-selected recolouring or known-scalar-only branch rule is
admissible.

Since no qualifying jet evaluator exists, the end-to-end lambda and mu claim is not met.

## 11. Route dispositions

| Route | Independent disposition |
|---|---|
| Frobenius projector identity | exact |
| Same-deck six singleton traces | exact conditional formula, generically defeated by permutation symmetry |
| Same-deck one-orbit higher moments | exact multiset inverse if moments are supplied |
| Five public colour decks | exact symmetry repair with constant heuristic density loss |
| Coloured first-order norm jet | exact simple-fiber source formula |
| Dense quotient, determinant, adjugate, or resultant | `B^5` payload |
| Multivariate power projection | quasi-linear in `B^5` quotient dimension |
| Reusable or streamed `2+3` | `B^3` state or query control |
| 2026 generic kSUM indexing | `B^5` preprocessing and excessive advice |
| Multiplicative subgroup deck | restricted `p-1` family and rational-lift filter unresolved |
| Generic composition tree | no jet intertwiner; leaf coupling remains |
| Same-field Lattes/isogeny tree | scoped P1526-P1528 kernel and duplicate-column controls |
| Extension-field deck | applicability and rational-source return unresolved |
| Jet-preserving non-Cartesian composition | explicit surviving question; no object supplied |

## 12. Independent decision

P1536 does not supply a Frobenius-projector moment recurrence or a complete below-rho
path. The focus candidate is terminal inconclusive, while the broader arbitrary structured-
constructor claim remains deferred and open. Its independently audited disposition is

```text
INDEPENDENT_SCOPED_AUDIT_PASS__NO_TRACE_RECURRENCE__COLOURED_NORM_JET_SUCCESSOR
```

The exact retained result is stronger and narrower than the incoming singleton statement:

```text
five public colour decks + one simple coloured fiber
    => one first-order norm jet recovers all five x-sources exactly.
```

No audited method constructs that jet within setup `B^2.25`, query `B^1.25`, and memory
`B^2.25`. The dense, triangular, split, generic indexing, special-deck, and FFE routes above
are scoped controls, not a universal arithmetic-circuit lower bound.

No relation campaign, factor-log solve, blind descent, generic-order result, Shoup-bound
improvement, or breakthrough exists.

## Exactly one next action

Close P1536 terminal inconclusive, preserve the broader structured-constructor class as
deferred, and audit one P1537 jet-preserving compositional-deck intertwiner bound to
IDEA-195: write an explicit target-independent map and factor-deck
tower for which the first-order coloured norm jet contracts recursively before the
`B^5` Cartesian product is formed, with a bounded exact branch inverse, generic-prime
applicability, setup and memory at most `B^2.25`, query at most `B^1.25`, rainbow rank,
factor logs, and masked descent. If the map descends only a trace, is deck-fixed, uses a
restricted smooth-`p-1` family, or restores a `B^3` transition deck, sign a scoped
no-candidate receipt. Do not run the retired IDEA-195 contract or construct a solver.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Poteaux and Schost, *Modular Composition Modulo Triangular Sets and
  Applications*: <https://cs.uwaterloo.ca/~eschost/publications/mulmodcomp.pdf>.
- Kedlaya and Umans, *Fast Polynomial Factorization and Modular Composition*:
  <https://users.cms.caltech.edu/~umans/papers/KU08-final.pdf>.
- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*, v2:
  <https://arxiv.org/abs/2512.04258>.
- Grenet, Koiran, and Portier, *The Multivariate Resultant Is NP-hard in Any
  Characteristic*: <https://arxiv.org/abs/1210.1451>.

These sources supply the summation-polynomial interface, quotient-dimension algorithms,
current generic indexing control, and generic resultant caution. None supplies the
coloured jet contraction or a generic-prime ECDLP improvement.
