# P1530 R1-R2 independent theorem and literature audit

## Record status

- Candidate: `ECDLP-IDEA-003`
- Focus experiment: `P1530`
- Artifact class: independent theorem-only reconstruction
- Decision: `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__RERANK_TYPE2_PERIOD`
- Evidence scale: exact algebra, primary-source cost reconstruction, and scoped route
  analysis; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

This audit rederives the P1530 claims from group and curve definitions and from the cited
primary sources. It imports no producer code, run output, point fixture, or known discrete
logarithm. It preserves the producer and literature-correction receipts unchanged.

## Bound receipts

- `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`
  - SHA-256: `7ad6ee0d5a038dbb086eb32d65e40cda79cba20bf2288c0bee473e9e96c2fc0f`
- `ideas/artifacts/ECDLP-IDEA-003/p1530_orbit_distinguisher_literature_audit.md`
  - SHA-256: `4a2108cdad0445286fe4970e17ec16f34e70f0bbea314cad53d6d81861bd71b6`

## A1: rational-map and branch-trace reconstruction

Let `E/F_p` be an elliptic curve and `G=<P>` a rational subgroup of prime order
`ell`. Every rational map `phi:E->E` extends to a morphism. After translating by
`-phi(O)`, it preserves the identity and is a group homomorphism. Therefore, on `G`,

```text
phi([u]P) = [a*u+t]P
```

whenever the image lies in `G`. For `1<D<ell`, agreement with `[u^D]P` requires a
root of the nonzero degree-`D` polynomial

```text
u^D-a*u-t in F_ell[u],
```

so one section agrees on at most `D` scalars.

For a finite correspondence `C` with maps `pi,psi:C->E`, the complete group sum of
the `psi` images over a `pi` fiber induces `psi_* pi^*` on `Pic^0(E)`, up to a fixed
translation. This complete symmetric trace is likewise affine on `G`. These arguments
verify the producer's R1 and R2 scopes. They do not cover a nonsymmetric implicit branch
selector.

## A2: materialized-section retry reconstruction

Suppose one attempt exposes `ell^(beta+o(1))` rational sections. Their union agrees
with `[u^D]P`, for `D=ell^(alpha+o(1))`, on at most
`ell^(alpha+beta+o(1))` scalars. Thus the inverse success-density exponent obeys

```text
delta >= max(0,1-alpha-beta).
```

If correspondence membership is not itself a scalar-power certificate, every false
candidate must pay Cheon recovery and final `[x]P=Q` verification. With

```text
chi(alpha)=max(alpha/2,(1-alpha)/2),
```

the retry exponent satisfies

```text
lambda >= beta+delta+chi(alpha)
       >= 1-alpha+chi(alpha)
       > 1/2.
```

The last inequality is `3(1-alpha)/2>=3/4` for `alpha<=1/2` and
`1-alpha/2>1/2` for `alpha>1/2`. The R3 lower bound is correct within its stated
materialized-section and Cheon-only-verification scope.

## A3: orbit normal form and type-1 costs

Let `H_D` be the unique order-`D` subgroup of `F_ell^*`, and let

```text
U_(D,theta) = {u in F_ell^*:u^D=theta} = u0*H_D.
```

For nonzero uniform `s`, the scalar `s*x` is uniform in `F_ell^*`, so

```text
Pr[(s*x)^D=theta] = D/(ell-1).
```

On acceptance, with `T=[theta]P`,

```text
[s^(-D)]T = [s^(-D)*theta]P = [x^D]P.
```

This verifies the constant-output reduction.

On Gallant's coprime factor families `ell-1=A*B`, take `B=D`, an order-`B`
element `beta0`, an order-`A` element `alpha0`, and
`theta=(alpha0^a)^B`. Then

```text
{[u]P:u^B=theta}
  = {[alpha0^a*beta0^j]P:0<=j<B},
```

exactly Gallant's type-1 orbit. The novelty correction is therefore correct. If `A`
and `B` are not coprime, the set remains a scalar-subgroup coset, but Gallant's stated
recovery decomposition is not imported without a separate factor argument.

For indicator query exponent `q`, Gallant's type-1 cost is

```text
lambda_1(alpha,q)=max(1-alpha,alpha/2,1-alpha+q)
                 =max(alpha/2,1-alpha+q).
```

For `0<=q<1/2`, its minimum occurs at

```text
alpha=2(1+q)/3,      lambda_1=(1+q)/3.
```

In particular `q=0` gives `lambda_1=1/3` at `alpha=2/3`. Generic orbit BSGS has
`q=alpha/2`, giving `1-alpha/2>1/2`; a full table has
`max(alpha,1-alpha)>=1/2`. These cost claims pass.

## A4: sign scope

An `x`-coordinate predicate identifies `R` and `-R`. It is sign-complete for the
order-`D` orbit exactly when `-1 in H_D`, equivalently when `D` is even. If `D` is
odd, an `x`-only label merges the two distinct cosets `uH_D` and `-uH_D`; a signed
coordinate or a doubled order-`2D` orbit must be charged. The producer and R2 receipt
already leave this exception visible. A successor must state which case it uses.

## A5: structured-generic comparison

The orbit fraction is `delta_orbit=D/ell`. The structured generic-group theorem gives
an `Omega(min(sqrt(ell),1/delta))` query bound when a partial binary label operation
constrains a `delta` fraction of labels. An arbitrary unary orbit indicator is not, by
itself, an instantiation of that partial-operation model. Therefore the R2 comparison

```text
Omega(min(sqrt(ell),ell^(1-alpha)))
```

is accepted only as a density sanity check under the receipt's explicit modeling
assumption. It is not evidence for or against a concrete EC-coordinate predicate.

## A6: a sharper surviving coordinate operation

The primary-source review exposes a more precise successor than type-1 membership.
For `H=<beta0>` of order `B=D`, define the partial elliptic period

```text
eta_H(R) = sum_(h in H/{+1,-1}) x([h]R)       if -1 in H,
```

with the signed analogue required otherwise. Multiplication by an element of `H`
permutes the summands, so `eta_H` is exactly constant on every `H` orbit. It becomes a
Gallant type-2 distinguisher if one proves the missing biconditional

```text
eta_H([u]P)=eta_H([v]P)  iff  u/v in H.
```

Brieulle, De Feo, Doliskani, Flori, and Schost use the same elliptic-period sum over a
scalar subgroup to canonically describe Frobenius orbits in an auxiliary finite-field
embedding problem. Their result does not prove the biconditional above on a rational
prime-order target subgroup: target Frobenius acts as one, and their field-generation
property is itself stated conjecturally. Their published evaluator also computes one
term per subgroup element.

Gallant's type-2 algorithm has

```text
lambda_2(alpha,q)
  = max((1-alpha)/2,alpha/2,(1-alpha)/2+q).
```

At `alpha=1/2,q=0`, this is `1/4`. More generally, for any fixed `0<alpha<1`, an
orbit label gives strict sub-rho time only if

```text
q < alpha/2,
```

with setup and memory separately below `1/2`. Even granting a generic same-orbit BSGS
comparison of cost `q=alpha/2` as though it were a reusable canonical label, Gallant's
outer stage lands exactly on rho; constructing a canonical generic label may cost more.
Direct elliptic-period evaluation has `q=alpha` and is above rho. The mechanism-new
question is thus a strict square-root improvement for evaluating a collision-free partial
elliptic period, not another orbit reduction.

## A7: FFE Frobenius-intertwiner gate

The natural FFE proposal is to make the order-`D` scalar action a Frobenius cycle. A
large scoped obstruction is exact.

Let `Phi:E->A` be a homomorphism defined over `F_(p^k)`, nonzero on `G`, and suppose
its image satisfies

```text
pi_A(Phi(R)) = Phi([beta0]R)       for every R in G,
```

where `pi_A` is `p`-Frobenius and `beta0` has order `D` modulo `ell`. Iterating `k`
times and using the field of definition gives

```text
Phi(R) = pi_A^k(Phi(R)) = Phi([beta0^k]R).
```

Because `G` has prime order and `Phi` is nonzero on `G`, its restriction is injective.
Hence `beta0^k=1 mod ell`, so

```text
D divides k.
```

Any exact homomorphic Frobenius-cycle encoder therefore needs extension degree at least
`D`, restoring `ell^alpha` base-field representation traffic. An `F_p`-rational
homomorphism is the special case `k=1` and cannot map the rational eigenline to a
nontrivial `beta0` eigenline. This gate does not cover a nonlinear, nonhomomorphic
coordinate encoder with an independently proved biconditional.

## A8: low-degree endomorphism invariant gate

Suppose a nonconstant rational function `f` on `E` globally satisfies

```text
f o psi = f
```

for an isogeny `psi:E->E` of degree greater than one. Degrees give

```text
deg(f o psi)=deg(f)*deg(psi)>deg(f),
```

a contradiction. Degree-one automorphisms fixing the origin have bounded order on an
ordinary elliptic curve, so they cannot generate a growing `D` orbit. Thus a compact
global rational invariant of a low-degree endomorphism does not instantiate `eta_H`.
An equality that holds only on the finite target subgroup, represented modulo its
vanishing ideal, remains outside this gate.

## Primary-source checks

- Gallant, *Finding discrete logarithms with a set orbit distinguisher*:
  <https://eprint.iacr.org/2010/370.pdf>
  defines type-1 and type-2 orbit distinguishers and gives their DLP costs.
- Brieulle, De Feo, Doliskani, Flori, and Schost,
  *Computing Isomorphisms and Embeddings of Finite Fields*:
  <https://cs.uwaterloo.ca/~eschost/publications/ffisom.pdf>
  defines elliptic periods as scalar-subgroup `x`-coordinate sums, leaves their full
  field-generation property conjectural, and charges one scalar multiplication per
  subgroup term in the direct evaluator.
- Corrigan-Gibbs, Henzinger, and Wu, *The Structured Generic-Group Model*:
  <https://eprint.iacr.org/2026/384>
  supplies the model-bound density comparison, not a direct unary-predicate theorem.

## Decision

The R1 producer theorem and R2 prior-art correction pass this independent scoped audit.
No type-1 coordinate tester or sub-rho ECDLP algorithm is produced. P1530 should become
terminal `inconclusive`, with its open mathematical exceptions preserved.

The audit also identifies one mechanism-specific successor:

```text
PARTIAL-ELLIPTIC-PERIOD-TYPE2:
prove coset separation and evaluate eta_H(R) with q<alpha/2
without D term materialization, a D-dimensional FFE, or a hidden DLP selector.
```

This successor is literature-derived and novelty-unverified. Its direct evaluator is
above rho. It is not a breakthrough.

## Exactly one next action

Freeze a theorem-only P1531 specification for the partial elliptic-period type-2 label,
including the coset-separation biconditional, even/sign-complete parameter family,
Gallant type-2 cost rectangle, direct-period control, the degree-`D` FFE obstruction,
and one explicit transfer-operator, summation-polynomial, or ECFFT compression recurrence
or a scoped no-candidate disposition; do not authorize a contract or toy fixture.
