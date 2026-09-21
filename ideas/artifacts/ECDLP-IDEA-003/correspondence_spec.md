# P1530 partial scalar-power correspondence theorem gate

## Record status

- Candidate: `ECDLP-IDEA-003`
- Focus experiment: `P1530`
- Artifact class: theorem-only specification and scoped operation screen
- Decision: `SCOPED_NO_PASS__OPEN_COMPACT_EXPONENT_COSET_TESTER`
- Evidence scale: theorem controls and cost identities; no experiment
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

This record does not construct `[x^D]P`, solve an ECDLP, or prove a lower bound
against every algebraic correspondence. It freezes the exact public interface, removes
the single-valued and rational-section classes, corrects the failed-branch cost, and
reduces the surviving mechanism to one explicit hidden-scalar coset predicate.

## Bound inputs

- `ideas/ECDLP-IDEA-003_partial_scalar_power_correspondence_hypothesis.md`
  - SHA-256: `64041ee5f8652c997041b193bd451ccb6e06d8ebfc1e21d986d393109b20013d`
- `ideas/ECDLP-IDEA-008_partial_pairing_return_cycle_hypothesis.md`
  - SHA-256: `0566ffabe87b88f3c92500dbeeee3ebe6a6a561c482ca1eaa40e48226d403142`
- `inputs/h100_session/HYPOTHESES_100.md`
  - SHA-256: `7c884bc75fe73cc85df363bf7f1413d8b5b943af958f7f831fc06d9e0746abff`
- `ledger/REVIEW-H100-20260717.md`
  - SHA-256: `18f7982e3810c88703244ca22c512682ab60d05fd33bddaaf6eba1701c0d9f12`

The H047 statement that auxiliary-free Cheon is an exponent-DH problem is retained as a
semantic warning, not as an unconditional impossibility theorem. Constructing the
missing exponent-DH operation below rho would be the mechanism under investigation.

## Public interface

Let `E/F_p` be an ordinary elliptic curve and let

```text
G = <P> <= E(F_p),   |G| = ell prime,   Q = [x]P,
D | (ell - 1),       D = ell^(alpha+o(1)),   0 < alpha < 1.
```

A passing operation must publish all of the following.

1. Target-independent equations or an arithmetic circuit `C(E,P,D)`.
2. A deterministic public enumerator producing every candidate branch for input `Q_s`.
3. A public acceptance predicate or certificate verifier `V_D(P,Q_s,Z_s)`.
4. A proof that every accepted output satisfies `Z_s=[(s*x)^D]P`.
5. Construction, branch, failed-query, verification, normalization, Cheon-recovery,
   final `[x]P=Q`, and peak-memory costs.
6. A subgroup-order family for which the divisor `D` is available without replacing an
   arbitrary fixed ECDLP input by a searched-for curve.

Algebraic membership in a multivalued correspondence is not item 4 unless the equations
and public branch rule imply the scalar-power identity. Verification with a known toy
`x` is only a development control.

## Cheon interface and corrected retry cost

Cheon's `ell-1` algorithm takes `P`, `[x]P`, and `[x^D]P` in the same order-`ell`
group. Its direct time and table exponents are

```text
chi(alpha) = max(alpha/2, (1-alpha)/2).
```

Let one correspondence attempt cost `ell^(kappa+o(1))`, enumerate
`ell^(beta+o(1))` candidate branches, and succeed with probability
`ell^(-delta+o(1))`.

If `V_D` rejects every false branch before Cheon, the acquisition and recovery terms are

```text
lambda_cert = max(kappa + delta, chi(alpha), verification and setup terms).
```

If correspondence membership does not certify the scalar-power branch, Cheon plus the
final equality `[x]P=Q` is the verifier. It must run on failed candidates as well. The
retry term is then

```text
lambda_uncert = delta + max(kappa, beta + chi(alpha), other per-attempt terms).
```

This is an append-only correction to the original hypothesis's optimistic `max` formula.
It does not reject a construction that supplies a sound cheaper verifier; it requires
that verifier to be the explicit mechanism rather than an assumption.

## Gate R1: single-valued rational maps are affine

Every rational map `phi:E -> E` extends to a morphism. Writing `T=phi(O)`, the map
`tau_(-T) o phi` preserves the identity and is a group homomorphism. Hence

```text
phi(R) = psi(R) + T
```

for an elliptic-curve homomorphism `psi`. On the rational prime-order subgroup `G`,
`psi` acts as a scalar `[a]`. If `phi([u]P)` lies in `G` for any `u`, then the relevant
translation also lies in `G`, so

```text
phi([u]P) = [a*u+t]P.
```

For `1 < D < ell`, equality with `[u^D]P` implies

```text
u^D - a*u - t = 0 mod ell,
```

which has at most `D` roots. Coordinate nonlinearities in a Lattes map, an isogeny, an
endomorphism, Frobenius, or a translated morphism therefore remain scalar-affine on
`G`. They do not supply the requested nonlinear scalar action.

Scope: this gate applies to single-valued rational maps and explicit rational sections.
It does not apply to an irreducible higher-genus correspondence with a nonalgebraic
public branch selector.

## Gate R2: symmetric branch aggregation is affine

Let `C` be the normalization of a finite correspondence with maps

```text
pi:C -> E,   psi:C -> E.
```

For generic `R`, sum the `psi` images of the points in `pi^(-1)(R)`, with
multiplicity, using the elliptic group law. The induced divisor push-pull map on
`Pic^0(E)` is a homomorphism, up to the fixed base-fiber translation. Thus the complete
group-sum trace of all branches is scalar-affine on `G`.

Consequently a trace, norm-to-group conversion, complete deck aggregate, or other
symmetric branch sum cannot be credited as `[x^D]P`. A surviving construction must
select an individual nonsymmetric branch or expose a different certified nonlinear
readout. This is not a claim that every coordinate norm is itself a point-valued trace.

## Gate R3: materialized rational sections plus Cheon-only verification

Suppose one attempt materializes
`B=ell^(beta+o(1))` explicit rational-section outputs. Each section is affine by R1, and
their union can agree with `[u^D]P` on at most `B*D` scalar inputs. Therefore

```text
delta >= max(0, 1-alpha-beta).
```

Without a cheaper sound scalar-power verifier, every enumerated section pays Cheon.
Hence

```text
lambda_uncert >= beta + delta + chi(alpha)
              >= 1-alpha + chi(alpha).
```

For `alpha <= 1/2`, the right side is at least `3(1-alpha)/2 >= 3/4`. For
`1/2 < alpha < 1`, it equals `1-alpha/2 > 1/2`. Thus no materialized family of rational
sections with Cheon-only verification gives a strict sub-rho algorithm, regardless of
how the enumerated branch count is split from the retry density.

This is a scoped cost theorem, not an unconditional lower bound against a public
exponent-DH decision predicate. A compact implicit selector that does not materialize its
algebraic branches is outside R3; its selection circuit and soundness proof are the
candidate operation and must be charged directly.

## Canonical surviving normal form

The cheapest possible output correspondence is constant. Fix public
`theta in F_ell^*` and define

```text
U_(D,theta) = {u in F_ell^* : u^D = theta},
S_(D,theta) = {[u]P : u in U_(D,theta)},
T = [theta]P.
```

Because `D | ell-1`, a nonempty `U_(D,theta)` has exactly `D` elements. For a public
nonzero randomizer `s`, set `Q_s=[s]Q`. If a public predicate proves

```text
Q_s in S_(D,theta),
```

then the constant output `T` is exactly `[(s*x)^D]P`, and

```text
Z = [s^(-D)]T = [x^D]P.
```

The success density is exactly `D/(ell-1)=ell^(-(1-alpha)+o(1))`. Therefore a compact
target-independent tester for `S_(D,theta)` with setup exponent `c`, amortized query
exponent `q`, and memory exponent `m` would have

```text
lambda = max(c, q + 1-alpha, chi(alpha), final verification),
mu     = max(m, chi(alpha)).
```

At `alpha>1/2`, this would be a genuine sub-rho route if `c<1/2`,
`q<alpha-1/2`, and memory also passes. The missing operation is therefore not an
unspecified output branch. It is the explicit coordinate-level predicate

```text
EXPONENT-COSET-MEMBERSHIP:
decide whether log_P(R)^D = theta without recovering log_P(R).
```

This normal form is target-independent and branch-complete. It also exposes exactly
where a summation-polynomial, finite-field-extension, ECFFT, or other algebraic proposal
would have to act: construct and evaluate this predicate below the dense/orbit floors.

## Explicit dense equation control

The set has an exact public vanishing ideal in the coordinate ring of `E`:

```text
I_(D,theta) = intersection over u^D=theta of
              (X-x([u]P), Y-y([u]P)).
```

This is a valid algebraic membership specification. It is not a passing algorithm.
Enumerating the `D` roots and points, storing the ideal or a point hash table, or
evaluating a direct product representation costs `ell^(alpha+o(1))` setup or state.
With randomization, a full table has

```text
lambda_table >= max(alpha, 1-alpha, chi(alpha)) >= 1/2.
```

An `x`-only product needs a separate sign proof: it also vanishes at `-[u]P`, which may
not satisfy the same scalar equation. Dropping this distinction creates false
auxiliary points.

## Orbit and algebraic controls

Choose `rho in F_ell^*` of order `D`. Then `S_(D,theta)` is one orbit under the known
scalar map `[rho]`. The following controls do not pass.

| Control | Exact result | Charged obstruction |
|---|---|---|
| Full point table or dense vanishing ideal | Exact membership | `D` setup/state, giving no strict sub-rho rectangle |
| Baby-step/giant-step orbit membership | Exact generic membership | `D^(1/2)` work per independent query; retries give exponent `1-alpha+alpha/2>1/2` |
| Division polynomials or isogeny kernels | Compact additive-torsion tests | A prime-order `G` has no nontrivial additive subgroup of size `D`; the intersection is trivial or all of `G` |
| Single rational function with the prescribed zeros | Exact only after all zeros and poles are controlled | Its zero divisor has degree at least `D`; degree alone is not a circuit lower bound, so a compact SLP remains open |
| Pairing test for a fixed quadratic power | Possible only with a nondegenerate second direction and exact orientation | Fixed `D` leaves Cheon at exponent `1/2`; iterated growing-degree return belongs to IDEA-008 and must charge MOV and return density |
| Generic-group affine operations | Every computed point has known affine scalar in `x` until a collision | Cannot realize or certify the multiplicative coset predicate below the generic boundary |
| Summation-polynomial or FFE encoding without a tester | Re-encodes point equations | No credit unless it gives an exact sign-complete membership circuit with the stated setup/query costs |

The division-polynomial row is a structural control, not an arithmetic-circuit lower
bound. Compact high-degree functions exist; their torsion zero sets simply have the
wrong additive structure for this multiplicative scalar coset.

## Source checks

- Cheon, *Discrete Logarithm Problems with Auxiliary Inputs*:
  <https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf>
  gives `O(sqrt((ell-1)/D)+sqrt(D))` group exponentiations after the valid auxiliary
  input is supplied.
- Cheon and Lee, *Diffie-Hellman Problems and Bilinear Maps*:
  <https://eprint.iacr.org/2002/117>
  shows that a bilinear map plus an injective return to the source collapses DH; it does
  not rule out every partial predicate.
- Boneh and Silverberg, *Applications of Multilinear Forms to Cryptography*:
  <https://eprint.iacr.org/2002/080.pdf>
  supplies the geometric multilinearity boundary, not a construction of the surviving
  predicate.
- Galbraith, *Mathematics of Public Key Cryptography*, Chapter 9:
  <https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch9.pdf>
  states that a rational map between elliptic curves is a homomorphism followed by a
  translation.
- Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>
  remains the generic comparison when only affine generic-group expressions are used.

No checked source constructs a compact coordinate tester for
`S_(D,theta)` on generic ordinary prime-field curves. This is not a novelty proof.

## Decision

No supplied IDEA-003 operation passes the theorem gate.

- Single-valued rational maps and rational sections are scalar-affine.
- Symmetric branch traces are scalar-affine.
- Cheon-only branch verification restores an exponent strictly above `1/2` for every
  materialized family of rational-section outputs.
- The dense exact exponent-coset ideal and point-table implementations meet or exceed
  the rho boundary.
- A compact coordinate-level exponent-coset membership circuit remains logically open,
  but no summation-polynomial, FFE, ECFFT, pairing, isogeny, or arithmetic-circuit
  recurrence is supplied.

The scoped disposition is
`SCOPED_NO_PASS__OPEN_COMPACT_EXPONENT_COSET_TESTER`. This is not a rejection of every
multivalued correspondence, not a generic-prime ECDLP algorithm, not a Shoup-bound
improvement, and not a breakthrough.

## Exactly one next action

Independently audit this theorem receipt and, only if it passes, freeze a successor gate
whose sole admitted positive is an explicit sign-complete arithmetic circuit for
`I_(D,theta)` with target-independent setup exponent below `1/2`, amortized query
exponent below `alpha-1/2`, complete Cheon recovery, and no point table, orbit BSGS,
pairing-return oracle, or hidden discrete-log selector.
