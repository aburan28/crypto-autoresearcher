# P1540 R1 independent elliptic-net locator audit

## Status and claim boundary

- Record type: independent theorem-only audit
- Root hypothesis: `ECDLP-IDEA-006`
- Candidate: `P1540`
- Claim: `CLM-P1540-ELLIPTIC-NET-TARGET-ANNIHILATOR`
- Evidence scale: exact symbolic reconstruction and literature controls; no experiment
- Contract state: `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml`
  remains `review_required` and was not executed or revised
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__NET_RATIO_AND_TRANSLATED_POLE_BOUNDS_RECONSTRUCT__LINEAR_COMPLEXITY_METHOD_IS_PRIOR_ART__CONSTANT_DIMENSION_NONLINEAR_STATE_IS_QRT_TRANSLATION_CONJUGATE_TO_E__LOW_DEGREE_RATIONAL_ADDITIVE_OR_MULTIPLICATIVE_LINEARIZATION_REQUIRES_A_FULL_N_ORBIT_DIVISOR__NO_DIRECT_INDEX_DECODER__INCONCLUSIVE`

The producer's net identity, displacement correction, and translated-pole count
reconstruct. Its claim that the finite-block pole method is absent from the cited
literature does not survive review: translated rational functions on elliptic curves
and zero-versus-pole linear-complexity arguments are established prior art. The exact
constant here is a useful specialization, not a novelty claim.

The previously open nonlinear-state branch can be made exact. Consecutive translated
`x`-coordinates obey a constant-dimensional QRT recurrence, but the two-coordinate
state is birationally conjugate to translation by `P` on the original elliptic curve.
It is therefore an exact re-encoding of the ECDLP orbit, not an index decoder. No
variable-coefficient or nonlinear operation with direct scalar recovery and complete
cost below the P1540 gate is supplied.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md`:
  `a87796ff5d484574110a438eadfa9a6afbecdafe485667490bbeb32b86906bde`
- `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml`:
  `64dbd7389d693378909eb17dd9f25b5d598099ea51eed961345c8738eac70f3f`
- `ideas/artifacts/ECDLP-IDEA-006/p1540_elliptic_net_translated_pole_annihilator_gate.md`:
  `d9a4040230022c24f7011932ef7cd9b5bcea51236a80c042bb498d2012428437`
- `ideas/artifacts/ECDLP-IDEA-003/p1533_r1_independent_audit.md`:
  `0de12da09c1bc49aa577431cff5ac09a264a367bce57aa1699c495015c28803f`

## Independently reconstructed producer statements

### Elliptic-net coordinate ratio

For Stange's rank-two net `W(v)=Psi_v(P,Q)`, Lemma 4.2 gives

```text
W(v)^2 W(w)^2 (x(v.P)-x(w.P)) = -W(v+w)W(v-w).
```

The parallelogram law for a quadratic net scaling cancels in this quotient, so the
coordinate difference is gauge invariant wherever the affine denominator is nonzero.
The missing denominator-zero points are relation charts, not discardable samples. In
particular, under the standard nondegeneracy assumptions,

```text
W(a,1)=0  iff  [a]P+Q=O.
```

For `Q=[x]P`, evaluating `W(a,1)` quickly does not locate its unique zero
`a=-x mod N`. That location problem is the target problem.

### Hankel displacement

For every scalar sequence and its Hankel matrix `H_(i,j)=s_(i+j)`, the standard shift
displacement

```text
Z_m H-H Z_n^T
```

is supported on one boundary row and one boundary column. Its rank is at most two
independently of the sequence. This metric is exact but tautological. It neither
implies low ordinary Hankel rank nor supplies an annihilator or index decoder.

### Translated-pole independence and finite blocks

Let `P` have order `N`, and put `f_n(R)=x(R+[n]P)`. The sole pole of `f_n` is a
double pole at `-[n]P`. The `N` pole locations are distinct, so inspecting them one at
a time proves that `f_0,...,f_(N-1)` are linearly independent.

If a nonzero constant recurrence of order `r<M` holds on all windows of a consecutive
finite block `s_i=x(R+[i]P)`, define

```text
F(Z)=sum_(j=0)^r c_j x(Z+[j]P).
```

The function is nonzero, has pole degree at most `2(r+1)`, and vanishes at the
`M-r` distinct block starts. Hence

```text
M-r <= 2(r+1),
r >= ceil((M-2)/3).
```

For the complete finite subgroup block of length `N-1`, this gives
`r>=ceil((N-3)/3)`. The coefficients may be chosen after seeing the public curve,
points, or block; after selection they are field constants, so the same count applies.

This reconstructs the producer's scoped theorem. It closes constant-coefficient
translated-`x` annihilators, not arbitrary variable-coefficient or nonlinear circuits.

## Novelty correction for the pole method

The proof pattern is not new. Hess and Shparlinski's elliptic-curve generator work and
Merai and Winterhof's linear-complexity-profile analysis study sequences `f(nG)` by
forming linear combinations of translated rational functions and comparing distinct
zeros with pole degree. The P1540 theorem is a direct `f=x`, consecutive-block
specialization with an explicit constant.

This does not invalidate the theorem. It changes its label from a potentially new
producer lemma to an independently checked, prior-art-aligned control. No novelty or
breakthrough credit attaches to the pole count.

## Exact nonlinear adjacent-coordinate state

Work over a field of characteristic other than two on

```text
E: y^2=f(x)=x^3+A*x+B.
```

Let `P=(u,v)` have prime order `N>2`, so `v!=0`. Define

```text
phi_P(R)=(X,Y)=(x(R),x(R+P)).
```

For `R=(X,y)`, the addition law gives

```text
Y=(y-v)^2/(X-u)^2-X-u,
2*v*y=f(X)+f(u)-(Y+X+u)(X-u)^2.
```

Thus, away from the usual affine exceptional chart, the oriented pair `(X,Y)` recovers
`R` rationally:

```text
x(R)=X,
y(R)=[f(X)+f(u)-(Y+X+u)(X-u)^2]/(2*v).
```

After eliminating `y`, the image lies on the fixed Semaev biquadratic

```text
S_3(X,u,Y)=
  (X-u)^2*Y^2
  -2*((X+u)*(X*u+A)+2*B)*Y
  +(X*u-A)^2-4*B*(X+u)=0.
```

Indeed the squared inverse equation equals `(X-u)^2*S_3(X,u,Y)`. Saturating the
exceptional factor and restoring projective charts gives a genus-one curve `C_P`
birational to `E`. The second coordinate chooses the orientation that an `x`-coordinate
alone loses.

### Differential-addition recurrence

For finite `A_0=(a,alpha)` and `B_0=(b,beta)` with `a!=b`, direct addition and
subtraction give

```text
x(A_0+B_0)+x(A_0-B_0)
  =2*(f(a)+f(b))/(a-b)^2-2*a-2*b.
```

Therefore `X_n=x(R+[n]P)` obeys

```text
X_(n+1)+X_(n-1)
  =2*(f(X_n)+f(u))/(X_n-u)^2-2*X_n-2*u.
```

Define the birational QRT update

```text
G_P(T)=2*(f(T)+f(u))/(T-u)^2-2*T-2*u,
F_P(X,Y)=(Y,G_P(Y)-X).
```

Then

```text
F_P(phi_P(R))=phi_P(R+P).
```

The identity also checks purely in the biquadratic coordinate ring. If
`Z=G_P(Y)-X`, then after clearing denominators,

```text
(Y-u)^4*S_3(X,u,Y)=numerator(S_3(Y,u,Z)).
```

Hence the update preserves `C_P` exactly, including the projective continuation through
affine denominator zeros.

### Consequence for index recovery

The recurrence has two field elements of nonlinear state, so state dimension alone is
constant. But `phi_P` and its rational inverse use `O(1)` field operations and conjugate
`F_P` to the original translation `tau_P:R->R+P`. For a target `Q=[x]P`, the state
`phi_P(Q)` is precisely the `x`-th point of this QRT orbit from `phi_P(O)`, interpreted
in a projective chart.

An algorithm that locates the QRT iterate index with time `T` and memory `M` solves the
original ECDLP with `T+O(1)` time and `M+O(1)` state. Conversely, scalar multiplication
computes the state from a known index with the ordinary addition-chain cost. The QRT
state is therefore representation-equivalent to the ECDLP orbit. This is a reduction,
not a lower bound against a future coordinate-specific algorithm; the missing
sub-square-root orbit-index decoder would itself be the breakthrough.

## Rational linearization screens

Assume `char(K)` does not divide `N`, as for the generic prime-to-characteristic
cryptographic subgroup lane.

### Multiplicative eigenfunction

Suppose a nonconstant `h in K(E)` satisfies

```text
h(R+P)=c*h(R)
```

for a field constant `c`. Its divisor is invariant under translation by `P`. Translation
acts freely in orbits of size `N`, and every multiplicity is constant on an orbit.
Every nonempty zero or pole divisor therefore has degree at least `N`. A rational
multiplicative coordinate of degree `o(N)` cannot linearize this translation.

This is the divisor version of the Fourier boundary. Over a splitting field the
eigenvalue can be `zeta^j`, while a target shift contributes `zeta^(j*x)`; recovering
`x` is an order-`N` field DLP unless a separately charged transfer algorithm is given.

### Additive coordinate

Suppose

```text
h(R+P)=h(R)+c.
```

Iterating `N` times gives `N*c=0`, hence `c=0`. A nonconstant invariant `h` factors
through the quotient isogeny `E->E/<P>` and again has a full `N`-point pole orbit. Thus
there is no low-degree rational additive logarithm in the prime-to-characteristic lane.
The anomalous characteristic-`p` formal-log case is an excluded positive control.

### Finite-dimensional rational state

For any finite-dimensional translation-stable subspace of `K(E)`, the union of pole
supports is translation invariant. If the space contains a nonconstant function, that
union contains at least one full `N`-point orbit. An explicit pole dictionary or generic
Riemann-Roch basis therefore carries order-`N` geometric support.

This observation does not classify succinct formulas, implicit nonlinear states, or
target-specific circuits. The QRT state itself is the counterexample to a blanket
dimension claim: it is succinct and constant-dimensional, but it preserves the full
genus-one orbit and lacks an index decoder.

## Variable-coefficient, Lax, and EDS route screen

1. Coefficients rational in the current adjacent state reproduce the QRT update or
   another rational presentation of translation on `C_P`. Fast next-state evaluation
   does not locate a supplied state's iterate number.
2. A QRT Lax pair packages the invariant biquadratic and spectral curve. For the present
   map that spectral curve is the same genus-one translation system; moving to its
   Jacobian returns an elliptic-curve DLP unless a new index decoder is supplied.
3. Elliptic divisibility and elliptic-net recurrences efficiently evaluate distant
   terms. Lauter and Stange's EDS discrete-log formulation isolates locating the hidden
   index as the hard operation and gives a prior-art equivalence control.
4. Periodic or public variable coefficients are not globally classified here. Any
   proposed survivor must specify the exact coefficient constructor, gauge behavior,
   exceptional charts, state ambiguity, and direct scalar decoder. None appears in the
   hypothesis, contract, producer receipt, or audited literature routes.
5. An arbitrary list-specific nonlinear locator remains logically open. Naming a solver,
   recurrence backend, Lax matrix, or spectral invariant without an index-output map does
   not instantiate that locator.

## Complete cost transfer

The maps `phi_P`, `phi_P^(-1)`, and `F_P` require `O(1)` field operations on their valid
charts. Let a claimed QRT/net-state index decoder have time exponent `tau`, memory
exponent `mu`, and setup exponent `a`. The direct reduction above gives an ECDLP solver
with

```text
lambda=max(a,tau)+o(1),
memory=mu+o(1).
```

There is no extra factor-base, relation-matrix, or descent gain to credit. The state
conversion itself has exponent zero, while no decoder with `tau<=0.40` or complete
`lambda,mu<=0.45` is supplied. Fourier labeling instead invokes another order-`N` DLP;
generic search retains exponent one half.

The existing `review_required` contract measures a displacement quantity that every
sequence passes and cannot test this missing operation. Executing it would produce no
decision-relevant evidence.

## Literature boundary

1. Katherine E. Stange, *Elliptic Nets and Elliptic Curves*,
   <https://arxiv.org/abs/0710.1316>. This supplies the net-to-coordinate and zero
   interfaces and quadratic scale equivalence.
2. Kristin E. Lauter and Katherine E. Stange, *The elliptic curve discrete logarithm
   problem and equivalent hard problems for elliptic divisibility sequences*,
   <https://arxiv.org/abs/0803.0728>. This is the index-location and finite-field-DLP
   transfer control.
3. Arne Winterhof and Laszlo Merai, *On the linear complexity profile of some sequences
   related to elliptic curves*, <https://arxiv.org/abs/1509.06909>. This supplies the
   translated-rational-function zero/pole prior-art boundary.
4. Andrew N. W. Hone, *ECM Factorization with QRT Maps*,
   <https://arxiv.org/abs/2001.09076>. This records QRT orbits as elliptic translations,
   their second-order recurrences, and their EDS connection.
5. Peter H. van der Kamp, G. R. W. Quispel, and D. I. McLaren's QRT literature is
   represented here by Howes, Joshi, and Kassotakis, *A Lax pair for the complete QRT
   mapping*, <https://arxiv.org/abs/1304.4351>. A Lax representation is a structural
   control, not an iterate-index decoder.

The literature controls do not prove the Shoup generic lower bound for every
coordinate-aware algorithm. They prevent recurrence evaluation, spectral packaging,
and a translated-function pole count from being credited as index recovery.

## Independent decision

The P1540 review trigger is satisfied within its exact scope:

- the net ratio, relation zero, gauge rule, Hankel metric correction, translated-function
  independence, and finite-block pole bound reconstruct;
- the pole argument is relabeled as prior-art-aligned rather than novel;
- the strongest explicit nonlinear adjacent-coordinate state is derived exactly and is
  birationally conjugate to translation on `E`;
- low-degree rational additive and multiplicative linearizations require a full
  order-`N` divisor orbit;
- Fourier, EDS, QRT, and Lax routes retain an order-`N` index problem; and
- no explicit variable-coefficient or nonlinear direct decoder meets the cost gate.

P1540 is terminal inconclusive. IDEA-006 remains preserved as an open hypothesis only
for a mechanism-new locator outside the closed classes. No contract, implementation,
fixture, rank sweep, relation campaign, factor-log solve, or descent is authorized by
this result.

## Exactly one next action

Rerank outside elliptic-net recurrence, translated-coordinate linear complexity,
scalar-orbit period, QRT/Lax state, and Fourier eigenvalue families. Admit one successor
only if it names an exact mechanism-distinct construction or degree operation with a
direct factor-base-to-target path and complete sub-rho costs; do not execute the
`review_required` IDEA-006 contract.
