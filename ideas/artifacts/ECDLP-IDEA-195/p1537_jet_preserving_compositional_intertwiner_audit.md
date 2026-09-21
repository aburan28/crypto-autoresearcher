# P1537 independent jet-preserving compositional-intertwiner audit

## Record status

- Candidate root: `ECDLP-IDEA-195`
- Focus experiment: `P1537`
- Expansion of: `P1536`
- Artifact class: independent theorem-only reconstruction and scoped no-candidate audit
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__EXACT_LOCAL_JET_TRANSPORT__NO_COMPACT_GENERIC_DECK__FINITE_STATE_CLOSURE_SUCCESSOR`
- Evidence scale: exact finite-etale algebra, representation, literature, and cost audit;
  no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract, verifier, solver, finite-field fixture, or relation campaign: none

There is an exact compositional transport identity, but it is not yet a compact
intertwiner. Norm transitivity over the first-order deformation ring carries the
constant coefficient and all six derivatives through any finite factor-deck tower.
On a globally simple coloured fiber, the derivative ratios continue to return the
same five leaf x-coordinates after every level.

This removes one ambiguity from P1536: source preservation itself does not force a
`B^5` table. The missing operation is a bounded-state symbolic realization of the
local norm update over all parent blocks. Enumerating those blocks starts at `B^5`.
Every audited shortcut that avoids enumeration either makes the Semaev relation
descend through a nontrivial deck map, in which case a zero pulls back to a whole
fiber and the first jet vanishes; uses a Lattes/isogeny tree, which is injective on
the rational prime subgroup or has many geometric lifts; filters an auxiliary or
extension-field tree and destroys the intertwiner; or returns to the frozen dense,
`2+3`, resultant, or source-advice controls.

The surviving question is therefore narrower than IDEA-195's arbitrary
non-Cartesian map: whether the seven-channel local norm operator for the restricted
Semaev kernel belongs to an explicit finite-state family closed under every deck
level. No such family is supplied here. This is not a sub-rho ECDLP algorithm or a
breakthrough.

## Frozen inputs and hashes

```text
P1536 independent projector and coloured norm-jet audit
81ec3515b584c36a809c155b5f26127bce91c09d7bfe6bccc425cdef07d51393

IDEA-195 non-Cartesian S3 intertwiner hypothesis
b52403859590a549f621fce1d2d71ab2e4da2d90faacbf9c0d3d48fcdb2bc513

P1526 ECFFT auxiliary-isogeny router gate
f8abb802b5052f614a6500c722083d3ebbd45d6e54353686ff3283ffa27a88b7

P1527 list-restricted canonical branch-locus gate
e4972a1c6f4fb796a9efa556c745c4d4d5e4b00e5637e9fca9f3828abb4db120

P1528 Lattes rational-kernel/cofactor gate
342e872f1e86297d88bb8684155ed84cf7c3b37351402fba4c296ff986ab141e
```

The imported P1478 subgroup-norm result is used only through its ledger record:
one sparse `S3` transition is logarithmic for the special `X^L-1` deck, while the
source-complete two-transition resultant is dense quadratic. No historical run is
re-executed or treated as current evidence.

## 1. Frozen coloured jet interface

Let `k=F_p`, let `F_1,...,F_5` be disjoint public rational x-decks, and put

```text
A_i = k[T_i]/(f_i),
A   = tensor_(i=1)^5 A_i.
```

The `f_i` are square-free and split over `k`. For a finite target chart `R`, set

```text
g_R = S_6(T_1,T_2,T_3,T_4,T_5,x_R) in A.
```

Use the first-order deformation ring

```text
D = k[e_0,e_1,...,e_5]/(e_a*e_b : 0<=a,b<=5)
```

and the marked element

```text
u_R = g_R + e_0 + sum_(i=1)^5 e_i*T_i in A tensor_k D.
```

P1536 proves that

```text
J_R = Norm_(A/k)(u_R)
    = c_R + e_0*j_(R,0) + sum_(i=1)^5 e_i*j_(R,i)
```

has the exact simple-fiber branches

```text
empty support:       c_R != 0;
singleton {a*}:      c_R = 0, j_(R,0) != 0,
                     a_i* = j_(R,i)/j_(R,0);
support size >= 2:   c_R = j_(R,0) = ... = j_(R,5) = 0.
```

The P1537 operation must construct these seven coefficients before expanding the
`Theta(B^5)` Cartesian deck and retain the exact leaf sources on the singleton
branch.

## 2. Exact norm transport through a finite tower

Suppose each colour deck is organized into target-independent finite maps

```text
F_i^(0) -> F_i^(1) -> ... -> F_i^(d_i),
```

where `F_i^(0)=F_i`, the terminal deck has bounded size, and every fiber at one
level has bounded degree. Algebraically, write the corresponding finite-etale
tower as

```text
A_i^(d_i) -> ... -> A_i^(1) -> A_i^(0),
```

where `A_i^(d_i)` has bounded rank over `k`. If the terminal deck is a singleton,
then `A_i^(d_i)=k`.

Tensoring the five towers and base-changing to `D` preserves finite local
freeness. For finite locally free algebras `C -> B -> A`, determinant norms obey

```text
Norm_(A/C)(v) = Norm_(B/C)(Norm_(A/B)(v)).
```

The same equality holds over `D`; reducing modulo its square-zero ideal proves
equality of the constant coefficient and all six first derivatives. Thus norm
transitivity is already an exact jet-preserving compositional identity.

This identity is target-independent at the tower level. Target dependence enters
only through the public coefficient `x_R` in `g_R`, exactly as in P1536.

## 3. Explicit seven-channel local update

Let one product level map a child block `X_y` to a parent tuple `y`. For each
child tuple `a in X_y`, write

```text
q_a = g_R(a),
l_a = e_0 + sum_(i=1)^5 e_i*a_i.
```

The local norm message is

```text
H_y = product_(a in X_y)(q_a+l_a) mod (e)^2
    = h_(y,empty) + e_0*h_(y,0) + sum_(i=1)^5 e_i*h_(y,i),
```

with exact coefficients

```text
h_(y,empty) = product_a q_a,

h_(y,0) = sum_a product_(b!=a) q_b,

h_(y,i) = sum_a a_i*product_(b!=a) q_b.       (1)
```

If a later level receives arbitrary seven-channel messages

```text
M_a = m_(a,empty) + e_0*m_(a,0) + sum_i e_i*m_(a,i),
```

the same square-zero multiplication gives

```text
M_(y,empty) = product_a m_(a,empty),

M_(y,j) = sum_a m_(a,j)*product_(b!=a)m_(b,empty),
           j=0,...,5.                           (2)
```

Equations (1) and (2) are the requested dual-number transport, including every
source coordinate channel. They use no root label after the first local update:
the five marked leaf coordinates are carried by their derivative coefficients.

## 4. Exact singleton source preservation

Assume the full coloured support is the singleton `{a*}`. At the first level,
exactly one parent block `y*` contains `a*`. In that block equation (1) gives

```text
h_(y*,empty)=0,
h_(y*,0)!=0,
h_(y*,i)=a_i* h_(y*,0).
```

Every other block has nonzero constant coefficient. Applying equation (2), the
unique zero message remains unique at every later level and

```text
M_(top,i)/M_(top,0)=a_i*,       i=1,...,5.
```

The proof is induction on tower depth. It also preserves the P1536 empty and
multiple-support gates: no zero block gives a nonzero final constant; two or more
zero blocks make the final constant and complete first jet vanish.

Therefore a finite tower does not intrinsically lose the exact source ratios. A
trace-only objection would be too strong. The obstruction is constructing the
functions or messages on all parent blocks cheaply.

## 5. Why transitivity alone does not contract the deck

Let every local colour map have degree `d_i>=2` and put `d=product_i d_i`.
The first product level has

```text
Theta(B^5/d)
```

parent blocks. Evaluating (1) block by block still costs `Theta(B^5)` field
operations and touches every child tuple. Subsequent levels form a geometric
tail and do not change the leading exponent.

Representing each channel as a dense function on the parent grid has the same
cost. Eliminating colours sequentially returns to iterated resultants; a balanced
`2+3` cut returns to the `B^3` transition side. Norm transitivity explains those
algorithms but does not improve their state or query exponent.

No dimension or degree statement here is used as an unconditional arithmetic-
circuit lower bound. A succinct recurrence could in principle evaluate all top
channels without materializing the grids. Such a recurrence is precisely the
remaining gate.

## 6. Descent-versus-source multiplicity theorem

A standard composed-system shortcut asks that, for a nontrivial product map

```text
pi : X -> Y,
```

the relation itself descend:

```text
g_R = v_R * (G_R composed pi),                  (3)
```

where `v_R` is a unit on the accepted deck. Suppose `G_R(y*)=0` and the accepted
fiber `pi^(-1)(y*)` has size `r>1`. Equation (3) makes every point in that fiber a
zero of `g_R`. The local norm has leading homogeneous term

```text
unit * product_(a in pi^(-1)(y*))
       (e_0+sum_i e_i*a_i),
```

of degree `r`. Hence its constant coefficient and all first derivatives vanish.
The simple-fiber norm jet cannot decode one source.

This gives an exact scoped dichotomy.

1. If the Semaev relation descends through a nontrivial deck fiber, the fast outer
   resultant sees a multiple upstairs support and loses the first-jet branch.
2. If the relation does not descend, equations (1) and (2) remain exact, but the
   seven child functions must be constructed on every block or by a new closed
   symbolic family.
3. If a selector retains only one accepted leaf in every fiber, the accepted deck
   map is injective and provides no compression. Retaining several leaves only on
   favorable target blocks is target-selected source advice.

This theorem does not rule out a non-descending finite-state local norm family. It
rules out presenting ordinary composed-system resultant compression as that family.

## 7. Lattes and isogeny positive control

Let

```text
psi_m(x(P)) = x([m]P)
```

be the Lattes map induced by multiplication by `m`. Elliptic addition commutes
with `[m]`, so this is the natural exact branch-transport positive control.

On the rational prime subgroup `G=<P>` of order `N`, if `gcd(m,N)=1`, then `[m]`
is a permutation. Its Kummer label identifies only the ordinary sign pair. No
growing rational deck fiber or factor-base compression is created. If `N|m`, the
map collapses the whole subgroup and its degree already carries `N`-scale work.

Over the algebraic closure, a parent signed relation has many exact lifts. For
five sources and fixed target lift, write each source lift as `P_i+K_i` with
`K_i in E[m]`. The lift condition is one linear equation

```text
sum_(i=1)^5 epsilon_i*K_i = K_R.
```

Choosing four kernel elements determines the fifth, giving

```text
|E[m]|^4 = m^8
```

signed geometric lifts on the separable generic stratum. The first jet therefore
vanishes on the full geometric fiber, and exact branch output grows under
iteration. Kummer signs change only a bounded factor.

Rational kernel branching from the full curve cofactor is covered by P1528: after
projection to the prime subgroup, kernel-coset lifts give duplicate factor-log
columns. Thus the Lattes family demonstrates exact algebraic closure without the
needed rational simple-fiber compression.

## 8. Auxiliary ECFFT trees

ECFFT supplies a genuine bounded-degree rational tree over every sufficiently
large finite field by using x-coordinates from a smooth subgroup on a chosen
auxiliary elliptic curve. The tree is an excellent polynomial-arithmetic object,
but its leaves are not automatically x-coordinates of points on the target curve.

Applying the auxiliary labels directly to target x-coordinates gives no Semaev
intertwiner. Filtering auxiliary leaves by the target quadratic-lift predicate
breaks the full preimage fibers and the composed deck. Hashing auxiliary leaves
to target points likewise destroys equations (1) and (3).

If a nonconstant morphism from the auxiliary elliptic curve to the target is
supplied and normalized at the origins, it is a group homomorphism and hence an
isogeny. Its restriction to the prime subgroup returns to the injectivity and
cofactor controls above. This is the exact P1526 boundary; ECFFT acceleration
after a dense source polynomial is supplied is a backend, not the missing map.

## 9. Multiplicative, additive, and extension-field towers

The deck `T^B-c` and its power-map tower can make local norms unusually sparse.
It requires the corresponding rational roots, hence a `B`-sized divisor in
`p-1` or a charged extension. This is not uniform generic-prime applicability.
Keeping only roots for which `T^3+A*T+B_E` is a square destroys the monomial
fiber unless another identity absorbs the character selector.

Chebyshev and Dickson towers are the analogous multiplicative-group quotients;
their large split preimage trees have the same smooth-order or extension issue.
Artin-Schreier and linearized towers are `p`-primary. A deck of size
`N^(1/5)` inside a generic prime field is not obtained from a proper additive
subfield, because the prime field has no such subfield.

Over `F_(p^d)`, a group-homomorphic trace of a division preimage satisfies

```text
[m] Tr(X) = Tr([m]X).
```

For a rational parent and `gcd(m,N)=1`, its prime-subgroup image is therefore a
known scalar multiple of the parent, not a growing independent factor base.
Kernel differences either trace to zero or duplicate the same projected column.
A nonhomomorphic coordinate return must separately prove rational lift density,
the complete inverse list, signed rank, and identical blind descent; no audited
map does so.

## 10. The actual finite-state closure gate

For one public level map `h=(h_1,...,h_5)`, define the local operator

```text
L_h : (q_empty,q_0,...,q_5)
      -> (H_empty,H_0,...,H_5)
```

by equations (1) and (2), with all child fibers taken exactly. A qualifying
intertwiner must exhibit explicit target-independent representation families

```text
C_0, C_1, ..., C_d
```

such that:

1. the restricted Semaev seed and its six markers have a representation in `C_0`;
2. `L_(h_j)` maps `C_(j-1)` to `C_j` by public formulas without enumerating child
   or parent grids;
3. every channel, pole, multiplicity, and exceptional chart is preserved;
4. the terminal state evaluates the exact seven top coefficients;
5. a simple accepted top state returns all five original rational x-sources;
6. total setup and resident state are at most `B^2.25`, and one target update is
   at most `B^1.25`.

A closed partition function, norm zero bit, or recurrence for only the constant
channel fails item 5. A recurrence fitted after seeing source tuples fails item 2.
A representation whose conditioning enumerates one path per leaf fails items 5
and 6.

This gate is operation-level distinct from generic modular composition: it asks
for closure of one seven-channel restricted kernel under a local product map. It
is also narrower than a generic tensor-rank claim. The nearest controls are
P1478's one-transition sparse norm/dense composition and IDEA-102's proposed
finite-field Yang-Baxter or star-triangle reordering. Neither supplies this
closure for a rational target factor deck.

## 11. Relation, rank, factor-log, and descent accounting

Retain the favorable P1536 normalization

```text
B=N^(1/5),
```

constant simple-rainbow relation density, and one returned row per successful
query. If finite-state setup and resident memory cost `B^s,B^m` and one target
costs `B^kappa`, then before failed colourings, output, rank defects, and descent,

```text
lambda >= max(s/5,(1+kappa)/5,2/5,1/5),
mu     >= max(m/5,1/5).
```

Promotion still requires `s,m<=2.25`, `kappa<=1.25`, and complete
`lambda,mu<=0.45`. The exact transport theorem supplies none of these upper
bounds. Block enumeration has `kappa=5`; the split transition control has
`kappa=3` or reusable state exponent `3`; both fail.

Even a passing finite-state evaluator would still need a theorem or approved
measurement for constant simple-rainbow density and `B` independent signed rows,
verification of every factor logarithm, and the identical scalar-blind evaluator
on fresh masks `Q+[r]P`. No target-selected tower, recolouring, branch choice, or
known-scalar-only conditioning is admissible.

## 12. Route dispositions

| Route | Independent disposition |
|---|---|
| Finite-tower norm transitivity over the dual-number ring | exact |
| Seven-channel local update | exact |
| Singleton source-ratio preservation through the tower | exact |
| Enumerated parent-block recursion | `B^5` work |
| Sequential or balanced elimination | dense resultant or `B^3` transition state |
| Relation descends through a nontrivial deck map | whole-fiber zeros; first jet vanishes |
| One accepted leaf per deck fiber | injective accepted map; no compression |
| Lattes/isogeny tower on the rational prime subgroup | permutation after sign quotient |
| Full geometric Lattes fibers | `m^8` signed lifts per five-source parent relation |
| ECFFT auxiliary tree | no target-addition intertwiner; isogeny return is injective |
| Power, Chebyshev, or Dickson deck | smooth-order/restricted-prime and rational-lift obstruction |
| Extension-field division tree | duplicate/trivial homomorphic return or missing nonhomomorphic inverse |
| Bounded-state seven-channel closure | explicit surviving question; no object supplied |

## 13. Independent decision

P1537 reconstructs an exact jet-preserving compositional identity but does not
construct it within the focus rectangle. Its scoped disposition is

```text
INDEPENDENT_SCOPED_AUDIT_PASS__EXACT_LOCAL_JET_TRANSPORT__NO_COMPACT_GENERIC_DECK__FINITE_STATE_CLOSURE_SUCCESSOR
```

The retained theorem is

```text
finite rational deck tower + one simple coloured Semaev source
    => seven local norm channels preserve the exact five leaf ratios at every level.
```

This is stronger than saying that only a trace descends, and weaker than an
algorithm. No audited generic-prime tower represents and updates those channels
without `B^5` blocks, `B^3` transition state, whole-fiber multiplicity, restricted
prime families, extension-return loss, or source advice. The negative result is
scoped to the explicit tower, outer-composition, Lattes, ECFFT, power-map, and FFE
realizations above; it is not a universal arithmetic-circuit lower bound.

No relation campaign, factor-log solve, blind descent, generic-order result,
Shoup-bound improvement, or breakthrough exists.

## Exactly one next action

Close P1537 terminal inconclusive and audit one P1538 bounded-state local-norm
renormalization gate bound jointly to IDEA-195 and IDEA-102: write an explicit
finite-field star-triangle, Yang-Baxter, transfer, or other algebraic identity whose
state family is closed under the seven-channel operator `L_h` for a public rational
factor deck and whose conditioned terminal state returns the five leaf sources
inside setup and memory `B^2.25` and query `B^1.25`; or sign a scoped no-candidate
receipt. Do not run the retired IDEA-195 or IDEA-102 contracts, construct a solver,
or generate a toy fixture.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- The Stacks Project, finite locally free morphisms and determinant norms:
  <https://stacks.math.columbia.edu/tag/02K9>.
- Milne, *Abelian Varieties*, rigidity and the translation-plus-homomorphism
  theorem: <https://www.jmilne.org/math/articles/1986b.pdf>.
- Ben-Sasson, Carmon, Kopparty, and Levit, *ECFFT Part I*:
  <https://arxiv.org/abs/2107.08473>.
- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>.
- Chtcherba, Kapur, and Minimair, *Cayley-Dixon construction of Resultants of
  Multi-Univariate Composed Polynomials*:
  <https://shu.elsevierpure.com/en/publications/cayley-dixon-construction-of-resultants-of-multi-univariate-compo/>.
- Felder, *Elliptic quantum groups*:
  <https://arxiv.org/abs/hep-th/9412207>.

These sources supply the finite norm, elliptic/Kummer map, composed-system, ECFFT,
and integrability controls. None supplies the required seven-channel finite-state
closure or a generic-prime ECDLP improvement.
