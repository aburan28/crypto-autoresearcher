# P1542 pairing lift-return geometry gate

## Status and claim boundary

- Record type: theorem-only producer gate
- Root hypothesis: `ECDLP-IDEA-008`
- Candidate: `P1542`
- Claim: `CLM-P1542-PARTIAL-PAIRING-LIFT-RETURN-CYCLE`
- Evidence scale: exact Frobenius-eigenspace, rational-map, degree, and cost statements;
  no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `UNREVIEWED_SCOPED_GEOMETRIC_NO_GO__ORDINARY_GEOMETRIC_ENDOMORPHISMS_PRESERVE_FROBENIUS_EIGENLINES_AND_DO_NOT_SUPPLY_A_DISTORTION_LIFT__RATIONAL_MAPS_FROM_A_PAIRING_TORUS_TO_E_ARE_CONSTANT__A_UNIVARIATE_RATIONAL_RETURN_VALID_ON_M_TARGET_VALUES_HAS_DEGREE_AT_LEAST_M_OVER_5__SYMMETRIC_CORRESPONDENCE_TRACE_IS_CONSTANT__COMPACT_HIGH_DEGREE_OR_NONSYMMETRIC_COVER_BRANCH_RETURN_UNSUPPLIED__OPEN`

IDEA-008 remains operation-distinct from P1530 only if it constructs both sides of an
outward-and-back cycle:

```text
G x G -> pairing target -> G.
```

The abstract scalar-power correspondence and Cheon recovery are already controls. The
new operation must obtain a nondegenerate second pairing direction from a rational
ordinary subgroup and return selected target values to source points without a source or
target discrete logarithm.

This receipt freezes two exact geometric obstructions. Ordinary geometric endomorphisms
do not cross the Frobenius eigenlines that pair nondegenerately, and a rational map from
an algebraic torus to an elliptic curve is constant. A finite-domain return can evade the
second statement only by failing to extend rationally; explicit low-degree coordinate
interpolation then pays linear degree in the accepted domain. Compact high-degree
circuits and nonsymmetric branches of nonrational covers remain open and unsupplied.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-008_partial_pairing_return_cycle_hypothesis.md`:
  `0566ffabe87b88f3c92500dbeeee3ebe6a6a561c482ca1eaa40e48226d403142`
- `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`:
  `7ad6ee0d5a038dbb086eb32d65e40cda79cba20bf2288c0bee473e9e96c2fc0f`
- `ideas/artifacts/ECDLP-IDEA-003/p1530_r1_r2_independent_audit.md`:
  `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`
- `ideas/artifacts/ECDLP-IDEA-007/p1541_r1_independent_audit.md`:
  `0cd9b2a3e42056d61c4b365af626bbf0a21e2f8bb666ffb1da098c31755e26a5`
- `ledger/H-ISO-001.yaml`:
  `dd4253ed30194fc390506894194349ecb6b62ae0f9052d27ff00f2ef293df59b`
- `ledger/EV-ISO-001.yaml`:
  `1ba53e3c49d1fcb1b0cfea1af2508839a32b2140241f145081d25cbf689db581`

## Exact pairing interface

Let `E/F_p` be ordinary, let `G=<P> subset E(F_p)` have prime order `N` with
`gcd(N,p)=1`, and let `pi` denote geometric Frobenius. Over a splitting field,
`E[N]` is two-dimensional over `F_N`. Since `P` is rational, it lies in the
`1`-eigenspace of `pi`. The determinant of Frobenius is `p`, so when the two roots are
distinct,

```text
E[N]=V_1 direct_sum V_p,
pi|V_1=1,
pi|V_p=p mod N.
```

A nondegenerate Weil or reduced Tate pairing needs independent source directions. The
pairing of a cyclic line with itself is trivial or degenerate; scalar-compatible inputs
must therefore place one copy in `V_1` and one in an independent direction such as
`V_p`.

If `T in V_p` is public, computing `[a]T` from `[a]P` without `a` is itself a
scalar-compatible cross-line map. IDEA-008 may not assume it as a lift oracle.

## Ordinary distortion-map gate

For an ordinary elliptic curve over a finite field, the geometric endomorphism algebra
is an imaginary quadratic field and is commutative. Every geometric endomorphism
`alpha` therefore commutes with Frobenius:

```text
alpha*pi=pi*alpha.
```

For `R in V_1`,

```text
pi(alpha(R))=alpha(pi(R))=alpha(R),
```

so `alpha(R)` remains in `V_1`. No geometric endomorphism of the ordinary curve maps
the rational `N`-torsion line to the distinct `p`-eigenline. Thus the standard
distortion-map route that works for selected supersingular curves is unavailable in the
generic ordinary lane.

This gate closes only endomorphism-based lifts on the same ordinary curve under distinct
eigenvalues. It does not classify correspondences through an auxiliary abelian variety,
nongeometric algorithms on finite torsion sets, or low-embedding-degree exceptions.
Each escape must construct its branch and charge its extension and calibration state.

If `p=1 mod N`, the eigenspaces can merge and `mu_N` lies in the base field. That is an
embedding-degree-one/MOV-special family, not generic ordinary-prime evidence; the direct
finite-field DLP cost is the control.

## Rational return from the pairing torus is constant

Let `T` be the algebraic torus containing the pairing target, for example `G_m` or a
restriction-of-scalars/norm-one torus over the base field. A standard theorem on maps
to abelian varieties says every rational map from a group variety to an abelian variety
is a homomorphism followed by a translation.

There is no nonzero algebraic-group homomorphism from a connected affine torus to a
proper abelian variety. Therefore every rational map

```text
rho:T dashrightarrow E
```

is constant.

In particular, no globally rational coordinate formula on the pairing target can
return `zeta^(ab)` to `[ab]P` on a Zariski-dense domain. A total algebraic return is
not merely absent from the hypothesis; it is excluded in this rational-map class.

The finite subgroup `mu_N` is not Zariski dense as `N` varies instance by instance, and
an arbitrary lookup map on its points need not extend to `T`. Finite-domain or
instance-dependent return circuits remain outside this theorem.

## Explicit univariate degree floor

The finite-domain exception still has a direct low-degree screen. Work over a field that
splits `mu_N`, write a short Weierstrass model

```text
E:y^2=x^3+a*x+b,
```

and suppose a return on a set `S subset mu_N` of `M` distinct values is represented by

```text
x=A(z)/B(z),
y=C(z)/D(z),
```

where every numerator and denominator has degree at most `d` and denominators do not
vanish on `S`. Clearing denominators in the curve equation gives

```text
H(z)=C(z)^2*B(z)^3
     -A(z)^3*D(z)^2
     -a*A(z)*B(z)^2*D(z)^2
     -b*B(z)^3*D(z)^2.
```

The polynomial `H` has degree at most `5d`. If the formulas return points of `E` on
all `M>5d` inputs, then `H` is identically zero. The pair `(A/B,C/D)` defines a
rational map `G_m dashrightarrow E`, hence is constant by the previous theorem.

Consequently every nonconstant explicit univariate rational return valid on `M`
accepted pairing values satisfies

```text
d>=ceil(M/5).
```

If the accepted return domain has density `N^(-delta+o(1))` in `mu_N`, then

```text
M=N^(1-delta+o(1)),
degree=N^(1-delta+o(1)).
```

Materializing generic coefficients or values at that scale fails a sub-rho setup gate
whenever `1-delta>=1/2`. Degree alone is not an arithmetic-circuit lower bound: repeated
squaring can represent special high-degree functions compactly. A compact modular
circuit whose correctness uses `z^N=1` remains open and must expose its branch labels,
certificate, and evaluation cost.

## Correspondence and branch boundary

A finite-domain return may be represented by a curve or higher-dimensional variety `C`
with maps

```text
q:C -> T,
psi:C -> E.
```

For a generic target `z`, the complete group-sum trace of the `psi` images over
`q^(-1)(z)` is a rational map from `T` to `E`, up to a fixed translation. It is
therefore constant. Norms, complete deck sums, and symmetric branch aggregation do not
return the target exponent.

A surviving correspondence must select a nonsymmetric branch. It must provide:

1. a target-independent equation for `C`, `q`, and `psi`;
2. a public branch predicate and complete certificate;
3. the density of inputs with a selectable branch;
4. the cost of finding that branch without a target-field or source-group DLP;
5. every branch, ramification, extension, and failed-attempt cost; and
6. proof that the returned point has the product scalar, not merely correspondence
   membership.

This is the pairing-return analogue of P1530's nonsymmetric branch boundary. P1542 does
not claim that every such cover is impossible.

## Finite-group return semantics

Fix a nondegenerate pairing base `zeta=e_N(P,T)`. On labeled inputs,

```text
e_N([a]P,[b]T)=zeta^(a*b).
```

The desired total return on `mu_N` is the abstract group isomorphism

```text
zeta^c |-> [c]P.
```

Evaluating this map is a pairing-inversion/source-return problem. It gives a
self-bilinear operation when composed with the pairing and would make source-group DH
easy. This explains its power but is not an unconditional reduction from return
evaluation to a DLP.

A partial return must define a recognizable subset on which this isomorphism can be
evaluated. An explicit table of accepted labels and source points has size `M`; a
membership predicate without the source output is insufficient; and a certificate that
uses `c=log_zeta(z)` has invoked the target DLP.

## Whole-cycle density gate

Let one complete attempt at the fixed multiplication/squaring circuit for public
`D | N-1` cost `N^(r+o(1))`, and let the probability that every required lift and return
succeeds be `N^(-Delta+o(1))`. The charged acquisition exponent is

```text
r+Delta.
```

Per-gate acceptance fractions cannot replace `Delta`. If `L=Theta(log N)` gates behave
independently with constant success `eta<1`, then

```text
eta^L=N^(-Theta(1)),
```

which contributes a nonzero density exponent. Correlated domains or a circuit-specific
closure may improve this, but that closure is a theorem obligation, not an assumption.

After a valid `[x^D]P` is obtained, Cheon's recovery term is

```text
chi(alpha)=max(alpha/2,(1-alpha)/2),
D=N^(alpha+o(1)).
```

Near `alpha=1/2`, Cheon costs `N^(1/4+o(1))`; the return acquisition remains the
dominant unknown.

## Complete cost gate

Let setup exponent be `c`; calibration sample exponent `gamma` with per-sample cost
`r_0`; applicable calibration algebra exponent `omega_cal*gamma`; full-cycle attempt and
density exponents `r,Delta`; return state exponent `s`; final ambiguity exponent `v`;
and Cheon divisor exponent `alpha`. Then

```text
lambda=max(c,gamma+r_0,omega_cal*gamma,r+Delta,
           alpha/2,(1-alpha)/2,v),
mu=max(s,gamma,alpha/2,(1-alpha)/2).
```

Promotion requires `lambda,mu<=0.45`, a direct returned source point at every gate, and
no hidden DLP. The following are charged inside `c,r,s,Delta` as applicable:

- second-eigenline construction and scalar-compatible lifting;
- extension-field and pairing arithmetic;
- return-domain construction and membership;
- cover equations, branch search, ramification, and certificates;
- high-degree circuit coefficients, advice, and table entries;
- all failed full circuits rather than accepted gates only; and
- direct MOV/Frey-Ruck target-field DLP when used.

No current artifact supplies values that pass this gate.

## Controls and falsifiers

### Required positive controls

- A supersingular toy with a public distortion map validates the two pairing directions,
  but remains excluded from generic ordinary promotion.
- An oracle-labeled finite return table validates the multiplication circuit and Cheon
  recovery, but its table and labels receive no mechanism credit.
- A directly injected `[x^D]P` validates Cheon's divisor, table, ambiguity, and final
  scalar checks.

### Required negative controls

- On ordinary distinct-eigenline instances, every geometric endomorphism must preserve
  `V_1`; a claimed distortion lift must fail or identify a non-endomorphism mechanism.
- Rational return formulas on more than `5d` accepted values must either become constant
  or violate the curve equation/denominator policy.
- Complete branch traces must be constant; a useful output must identify one certified
  nonsymmetric branch.
- Direct MOV, target-field DLP, source rho, BSGS, and P1530 exponent-coset controls are
  costed on the same environment.

### Immediate falsifiers for the current formulation

- The second pairing lift is an unconstructed `[a]P -> [a]T` oracle.
- The return reads `log_zeta(z)`, uses a precomputed source-label table, or verifies only
  pairing correspondence membership.
- A rational map from the full torus is claimed nonconstant.
- A degree-`d` univariate return is accepted on more than `5d` points without becoming a
  rational torus-to-`E` map.
- Per-gate density is reported in place of whole-cycle success.
- A pairing value, one returned toy product, injected Cheon input, or supersingular
  result is called a generic-prime Shoup-bound improvement.

## Literature boundary

1. Jung Hee Cheon and Dong Hoon Lee, *A Note on Self-Bilinear Maps*,
   <https://eprint.iacr.org/2002/117>. This supplies the DH-collapse boundary for a full
   pairing return, not an unconditional theorem against partial domains.
2. Dan Boneh and Alice Silverberg, *Applications of Multilinear Forms to Cryptography*,
   <https://eprint.iacr.org/2002/080.pdf>. This is the geometric multilinearity control.
3. Alfred Menezes, Tatsuaki Okamoto, and Scott Vanstone, *Reducing elliptic curve
   logarithms to logarithms in a finite field*,
   <https://doi.org/10.1109/18.259647>. This is the direct pairing-transfer control.
4. Jung Hee Cheon, *Security Analysis of the Strong Diffie-Hellman Problem*,
   <https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf>.
   This supplies the auxiliary-input recovery cost after `[x^D]P` exists.
5. J. S. Milne, *Abelian Varieties*, <https://www.jmilne.org/math/CourseNotes/AV.pdf>.
   The rational-map theorem says a map from a group variety to an abelian variety is a
   homomorphism followed by translation; maps from a torus are therefore constant.
6. Andreas Enge, *Bilinear Pairings on Elliptic Curves*,
   <https://arxiv.org/abs/1301.5520>. This supplies the pairing, eigenspace, and
   distortion-map background.

No source supplies the P1542 compact finite-domain lift-and-return branch. Novelty of
such a future operation remains unverified.

## Producer decision

The IDEA-008 instruction to draft a toy ordinary-versus-oracle contract is premature.
The oracle arm would test plumbing, while the ordinary arm has neither a constructed
cross-eigenline lift nor a return branch. The exact endomorphism and rational-map gates
remove the simplest algebraic implementations; the finite-domain degree theorem rules
out low-degree interpolation at useful density.

P1542 is queued for one independent theorem audit. No contract, implementation,
extension-field fixture, pairing run, return table, or Cheon campaign should be built
until the audit either specifies a compact high-degree or nonsymmetric-cover return with
both lift and whole-cycle costs, or returns the candidate terminal inconclusive.

## Exactly one next action

Independently reconstruct the ordinary Frobenius-eigenline lift gate, torus-to-elliptic
rational-map theorem, `M<=5d` finite-domain degree bound, correspondence-trace boundary,
and whole-cycle cost; then either specify one target-independent compact high-degree or
nonsymmetric-cover lift-and-return operation with complete `lambda,mu<=0.45`, or return
P1542 terminal inconclusive. Do not draft or execute an IDEA-008 contract during review.

