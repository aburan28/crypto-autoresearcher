# P1530 orbit-distinguisher literature correction and operation audit

## Record status

- Candidate: `ECDLP-IDEA-003`
- Focus experiment: `P1530`
- Artifact class: append-only literature correction and theorem-only operation screen
- Decision: `LITERATURE_CORRECTION_PASS__REDISCOVERY__NO_EXPLICIT_EC_TESTER`
- Evidence scale: primary-source reconstruction and asymptotic identities; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

This record preserves the producer receipt unchanged and corrects its novelty boundary.
The constant-output exponent-coset normal form is a restatement of the type-1 set-orbit
distinguisher studied by Gallant in 2010. The reduction from such a distinguisher to a
sub-rho DLP algorithm is therefore prior art. An explicit, sign-complete, sub-rho
elliptic-coordinate implementation of the distinguisher remains open; none is supplied
here.

## Bound producer receipt

- `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`
  - SHA-256: `7ad6ee0d5a038dbb086eb32d65e40cda79cba20bf2288c0bee473e9e96c2fc0f`
  - Producer decision: `SCOPED_NO_PASS__OPEN_COMPACT_EXPONENT_COSET_TESTER`

The affine-map, symmetric-trace, failed-branch verification, and materialized-section
gates in the producer receipt are not withdrawn. The correction is that its canonical
survivor is not a new reduction. It is the established orbit-indicator primitive.

## Exact identification with Gallant's type-1 orbit

Let `G=<P>` have prime order `ell`. Write

```text
ell - 1 = A*B,            gcd(A,B)=1,
alpha0 in F_ell^*         of order A,
beta0  in F_ell^*         of order B.
```

Gallant's fixed orbit, translated to additive elliptic notation, is

```text
O_a = { [alpha0^a * beta0^j]P : 0 <= j < B }.
```

This exact parameter identification is on the order families satisfying Gallant's
coprimality hypothesis. For an arbitrary `D | ell-1`, the producer set is still one
orbit under the order-`D` scalar subgroup, but applying Gallant's stated recovery
algorithm verbatim may require splitting the factors. That distinction does not turn
the orbit-membership primitive into a new operation.

Set

```text
D = B,                    theta = (alpha0^a)^B.
```

Every scalar in the orbit satisfies

```text
(alpha0^a * beta0^j)^D = theta,
```

because `beta0` has order `B`. Conversely, `u^D=theta` has exactly `D=B`
solutions and already contains all `B` orbit scalars. Hence

```text
O_a = S_(D,theta)
    = { [u]P : u^D=theta }.
```

The producer predicate

```text
1[log_P(R)^D = theta]
```

is therefore exactly Gallant's type-1 indicator for one exponentiation orbit, up to
notation and the additive presentation of the elliptic-curve group. Gallant explicitly
states that the DLP reduction applies to arbitrary groups and includes elliptic-curve
groups in its discussion.

The producer's post-acceptance route differs: after accepting `Q_s=[s*x]P`, it derives
`[x^D]P` from the constant `[theta]P` and invokes Cheon. Gallant instead moves public
generator and challenge powers into the same orbit and performs BSGS inside that orbit.
This difference does not make the orbit predicate or its sub-rho consequence novel.

## Cost identity

Gallant's type-1 algorithm with one orbit indicator of query cost `c(ell)` has, ignoring
polylogarithmic factors,

```text
T_G = A + sqrt(B) + A*c(ell),        A=(ell-1)/B.
```

Parameterize

```text
B=ell^(alpha+o(1)),       c(ell)=ell^(q+o(1)).
```

Then

```text
lambda_G = max(1-alpha, alpha/2, 1-alpha+q).
```

The producer's randomized constant-output route has

```text
lambda_P = max(1-alpha+q, chi(alpha)),
chi(alpha)=max(alpha/2, (1-alpha)/2).
```

For a polynomial-time indicator (`q=0`), both routes attain exponent `1/3` at
`alpha=2/3`, subject to the required factorization of `ell-1`. Thus the producer's
best exponent profile is the known type-1 orbit-distinguisher profile.

For generic orbit membership, `q=alpha/2`. Both profiles then contain

```text
1-alpha+q = 1-alpha/2 > 1/2       for every fixed alpha<1.
```

Letting `alpha` approach one only approaches rho from above; it gives no fixed strict
sub-rho exponent. A full orbit table has setup/state exponent `alpha` and retry exponent
`1-alpha`, so `max(alpha,1-alpha)>=1/2`. These controls agree with the producer receipt.

## Structured-generic density check

The orbit occupies fraction

```text
delta_orbit = B/ell = ell^(alpha-1+o(1))
```

of the prime-order group. Corrigan-Gibbs, Henzinger, and Wu prove in their structured
generic-group model that exploiting structure constrained to a `delta` fraction of
labels requires

```text
Omega(min(sqrt(ell), 1/delta))
```

group-oracle queries. Modeling a free orbit indicator as structure available exactly on
this orbit gives the density sanity check

```text
Omega(ell^min(1/2, 1-alpha)).
```

At `alpha=2/3`, this is `ell^(1/3)`, matching the known orbit-indicator upper bound.
This is a model-bound comparison, not a theorem that their partial binary-operation
model exactly equals an arbitrary coordinate predicate. It neither constructs nor
rules out a concrete elliptic-coordinate tester.

## Operation screen for an elliptic-coordinate type-1 distinguisher

A successor may not claim the orbit reduction as its positive mechanism. Its positive
must be an explicit evaluator for

```text
D_(D,theta)(R) = 1 iff log_P(R)^D=theta
```

on a stated ordinary prime-field curve family. It must charge target-independent setup,
amortized query time, state, sign handling, exceptional points, divisor applicability,
and final DLP recovery.

| Route | Exact contribution | Current obstruction |
|---|---|---|
| Dense point ideal or point table | Exact sign-complete membership after enumerating the orbit | `B` setup or state; combining with orbit density has exponent at least `1/2` |
| Generic orbit BSGS | Exact membership using the known scalar action `[beta0]` | `sqrt(B)` per independent query; retries cost `ell^(1-alpha/2)` |
| `x`-only vanishing polynomial | Can vanish on all orbit abscissas | Also accepts negatives unless the scalar orbit is sign-stable; a sign-complete second condition is mandatory |
| Summation-polynomial elimination | Can encode point addition and eliminate hidden ordinates | Re-encodes the membership variety unless it supplies a target-independent compact circuit, all branch signs, and query cost `q<alpha-1/2` |
| Extension-field / FFE lift | May expose Frobenius, norm, trace, or fast field arithmetic | No stated lift turns multiplicative scalar cosets into additive subspaces; descent, all conjugate branches, and return cost remain uncharged |
| ECFFT or multipoint evaluation | Can accelerate evaluation once coefficients, samples, and an evaluation domain are available | Does not supply the missing point-to-orbit-index intertwiner; materializing `B` orbit values or coefficients restores the setup/state floor |
| Division polynomial or isogeny kernel | Gives compact tests for additive torsion or kernel sets | The desired set is a multiplicative coset in the hidden scalar, not a nontrivial additive subgroup of prime-order `G` |
| Pairing transport | Preserves exponentiation orbits under a nondegenerate homomorphic image | Merely moves the same type-1 distinguisher to a target group; `z^D` tests `D*u`, not `u^D`, and MOV/target-group work must be charged |
| Sparse indicator polynomial or short SLP | Would be a genuine non-generic coordinate mechanism | This is already the open class isolated by Gallant; no explicit sign-complete EC circuit or sufficient sparsity bound is supplied |

### Summation-polynomial acceptance gate

A summation-polynomial proposal passes only if it publishes all of:

1. A finite arithmetic circuit whose constants depend on `(E,P,D,theta)` but not on
   the challenge scalar.
2. A proof that its accepted affine points are exactly `S_(D,theta)`, including both
   ordinate signs, points at infinity, poles, repeated roots, and exceptional fibers.
3. Setup exponent `c<1/2`, query exponent `q<alpha-1/2`, and memory exponent below the
   stated campaign cap, without first enumerating the `D` orbit points.
4. A complete recovery path and the family density for usable `D | ell-1`.

Writing a Semaev polynomial whose roots include a decomposition, computing a resultant
that has the orbit points among its zeros, or evaluating a dense product faster does not
meet items 2 and 3. The source labels and false branches must be recoverable and charged.

### FFE and ECFFT acceptance gate

An extension-field or ECFFT proposal passes only if it supplies an explicit
intertwining identity

```text
Phi([u]P) in K  belongs to L_(D,theta)  iff  u^D=theta,
```

where membership in `L_(D,theta)` is evaluated at the required cost and every map,
inverse image, conjugate, sign, and descent branch is public. Fast multiplication,
Frobenius evaluation, multipoint evaluation, or an isogeny tree is a backend after this
identity is proved; it is not the missing identity.

No screened route supplies such an intertwiner. This is a scoped no-candidate result,
not a lower bound against all arithmetic circuits or all concrete elliptic curves.

## Source checks

- Gallant, *Finding discrete logarithms with a set orbit distinguisher*:
  <https://eprint.iacr.org/2010/370.pdf>
  defines type-1 membership in one exponentiation orbit, gives the
  `A + sqrt(B) + A*c` DLP algorithm, identifies the `ell^(1/3)` parameter point, and
  leaves short straight-line indicator polynomials as an open route.
- Corrigan-Gibbs, Henzinger, and Wu, *The Structured Generic-Group Model*:
  <https://eprint.iacr.org/2026/384>
  proves the `Omega(min(sqrt(q),1/delta))` structured-generic query lower bound. The
  comparison above is explicitly model-bound.
- Cheon, *Discrete Logarithm Problems with Auxiliary Inputs*:
  <https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf>
  supplies the producer route's recovery term after a valid `[x^D]P` is obtained.

These sources establish prior art for the reduction and a model boundary. They do not
establish that no concrete coordinate distinguisher exists. No checked source supplies
the required generic ordinary-prime-field EC tester; this statement is not a novelty
proof.

## Decision

The producer's canonical reduction is a rediscovery of Gallant's type-1 orbit
distinguisher. It must not be promoted as a novel ECDLP mechanism.

- The producer's scoped affine and retry-cost negatives remain usable.
- The `ell^(1/3)` oracle consequence is prior art.
- Dense ideals, full tables, generic orbit BSGS, additive-kernel tests, and backend-only
  summation-polynomial, FFE, and ECFFT formulations do not pass.
- A compact sign-complete elliptic-coordinate type-1 orbit distinguisher remains an
  explicit open operation class, with novelty unverified and no candidate supplied.

The scoped disposition is
`LITERATURE_CORRECTION_PASS__REDISCOVERY__NO_EXPLICIT_EC_TESTER`. This is not an ECDLP
solution, a generic-prime Shoup-bound improvement, an experiment, or a breakthrough.

## Exactly one next action

Independently audit the producer receipt and this correction as one hash-bound package;
only a passing audit may freeze a successor whose sole positive is an explicit
sign-complete EC-coordinate Gallant type-1 distinguisher, potentially using
summation-polynomial, FFE, or ECFFT machinery, with complete setup, query, state,
applicability, and recovery costs below the stated gates.
