# C-star bounded projection search

Task `TASK-20261005-47d13a` examined exactly three public projections of the
prior Route-C cyclic-kernel map. None is retained as a C-star finalist. The
single-image projection leaves both message separation and the connecting
module unresolved; the fresh mask quotient introduces mask recovery that is
not supplied by `End(E)`; and the determinant/Weil-pairing invariant is
constant on every valid encryption. This is a scoped failure of these three
definitions, not an impossibility result for EndRing-based PKE.

No experiment, implementation, security claim, novelty claim, parameter
recommendation, or deployment claim is made.

## Common typed scaffold

Fix a prime `p>5`, a finite represented extension `F/F_(p^2)`, and public
certificates for a supersingular curve `E_star/F_(p^2)` and an evaluable
integral basis of `End(E_star)`. Fix integers `L,a,k,b` with `1<=k<a`,
`D=2^a`, `N=5^b`, `gcd(D,Np)=1`, and `N^2>4D`. The field `F` must contain the
declared `D`- and `N`-torsion. Its degree, construction, point encodings, and
arithmetic costs are explicit input costs; no bounded-degree claim is made.

`KeyGen` samples a length-`L` chain of independent uniform cyclic degree-3
kernels from `E_star`, obtains `tau:E_star->E`, forms
`R=Z*1+tau End(E_star) dual(tau)`, and performs the finite saturation procedure
from the prior packet to obtain four evaluable maps forming `O=End(E)` with a
multiplication table and rational coordinate data. It rejects any failed
certificate or map-integrality check. It erases `tau`, its kernels, connecting
ideals, orientations, and the walk transcript. The procedure is a finite
specification; a uniform polynomial time/output bound is still the separate
`K0` obligation.

The public key contains `E`, canonical public bases `(U,V)` of `E[D]` and
`(P,Q)` of `E[N]`, the represented field and all parameters. The secret key is
only the evaluable basis/table/coordinates of `O`. The public distribution is
the stated walk pushforward with deterministic level selection, not a claimed
uniform distribution. For message `m in M={0,...,2^k-1}` and uniform
`r in R={0,...,2^(a-k)-1}`, set

```
s = m + 2^k r in Z/DZ,
K_s = <U+sV>,
phi_s:E -> C_s=E/K_s.
```

The sender computes the normalized degree-`D` quotient as `a` public
degree-2 steps. Curves and all retained points are normalized simultaneously;
malformed or noncanonical encodings return `bottom`. A candidate-list is not
a plaintext.

## Family P1: one-column action

The projection is

```
Pi_1(phi_s) = (C_s, phi_s(P)).
```

`Encrypt_1(pk,m;r)` is public: construct `phi_s` and output `Pi_1(phi_s)`.
The only fully specified lift is `LiftEnum_1`: enumerate every `t in Z/DZ`,
recompute `phi_t`, and retain those whose normalized endpoint and image of `P`
equal the ciphertext. `Decode_1` returns `t mod 2^k` only if all retained
values have one common low-`k` value, and returns `bottom` otherwise.

This gives no quantified all-message correctness equation. The previous
`N^2>4D` proof needs equality on a full `E[N]` basis; equality on `P` alone
only makes `phi_s-phi_t` vanish on one cyclic order-`N` subgroup. Neither
`N^2 | deg(phi_s-phi_t)` nor unique kernel/message recovery follows. Thus the
exact failed arrow is

```
(C_s,phi_s(P)) -/-> unique degree-D map -/-> unique s -/-> m.
```

`LiftEnum_1` costs `D` public encryptions, ignores `End(E)`, and is exponential
in `a`. An End(E)-only polynomial replacement would have to output the missing
second action value or an equivalent evaluated connecting map without a path,
ideal, orientation, retained `tau`, or other secret. No such algorithm is
defined here. The single-point shape also meets the PIKE/POKE comparison
boundary and is not claimed as a new interface.

## Family P2: fresh public-orbit mask quotient

Let `G_N=SL_2(Z/NZ)` with its canonical matrix encoding. Extend encryption
randomness to `(r,A)`, where `A` is uniform in a declared finite sampler for
`G_N`. For the ordered row of public action images
`Y_s=(phi_s(P),phi_s(Q))`, define

```
Pi_mask(phi_s,A) = (C_s, Y_s A).
```

The sender can compute this using only public values. The ciphertext omits
`A`. `LiftEnum_mask` enumerates all `(t,B)` in `(Z/DZ) x G_N`, reenacts the
masked ciphertext, and returns the compatible pairs. `Decode_mask` returns a
message only when every compatible pair has the same `t mod 2^k`; otherwise it
returns `bottom`.

For every valid pair `(s,A)` and every `B in G_N`, the same ordered target
basis can be written as `Y_t B` whenever a compatible full-action basis is
chosen; the mask deliberately discards the source-basis labeling needed by the
Route-C kernel coefficient. More basically, the receiver has no input related
to the sender's fresh `A`. `End(E)` contains endomorphisms of the source curve,
not this independent ciphertext randomness. The failed arrow is

```
End(E), (C_s,Y_s A) -/-> A or unmasked Y_s -/-> s -/-> m.
```

Including `A` in the ciphertext makes unmasking public and restores the
audited full-action/Robert recovery route. Giving `A` to the receiver adds a
per-ciphertext secret not present in `KeyGen`. Replacing it by a long-term
secret matrix or a connecting isogeny changes the construction and introduces
the FESTA/LIT-style masking structure and its own assumption. The exhaustive
algorithm costs `D*|G_N|` reenactments, is exponential in the bit length, and
is public. Consequently this family has neither a polynomial End(E)-only
`SecretLift` nor established all-message correctness.

## Family P3: determinant/Weil-pairing invariant

The projection is

```
Pi_det(phi_s) = e_N(phi_s(P),phi_s(Q)) in mu_N(F).
```

`Encrypt_det` publicly computes the quotient and this pairing value; the
ciphertext does not retain the codomain or either image point. By Weil-pairing
functoriality,

```
Pi_det(phi_s) = e_N(P,Q)^D
```

for every `s`. Hence every message/randomness pair has exactly the same
ciphertext. `SecretLift_det` validates that the input is this constant and
returns the singleton invariant; it uses the evaluable ring only vacuously.
`Decode_det` returns `bottom` because the observation fiber contains every
message. For every generated key and every `m,r`,

```
Dec_det(sk,Enc_det(pk,m;r)) = bottom != m.
```

No amount of End(E), Hom, path, ideal, or orientation data can recover which
encryption preimage produced a constant observation. This is the required
constant-projection control, not a candidate.

## First security game and reduction directions

The first target, had a finalist existed, would be IND-CPA for the exact PKE:
the challenger runs `Setup,KeyGen`, gives `pk`, receives equal-length
`m_0,m_1`, samples `beta` and declared encryption randomness, returns
`Enc(pk,m_beta;r)`, and receives a guess. Malformed-ciphertext behavior is
outside this first game but remains part of syntax.

Let `EndRingEval` take a curve from the exact bare `D_curve` distribution and
return an evaluable integral basis of its full endomorphism ring, modulo the
declared basis/model equivalence. If a correct polynomial `SecretLift` and
`Decode` were supplied, the direct arrow would be

```
EndRingEval solver -> recover sk representation -> SecretLift -> Decode
                    -> IND-CPA break.
```

That is an attack or upper-bound direction: the scheme is no harder to break
than the stated EndRing problem under the necessary distribution/auxiliary-data
matching. It does not prove security from EndRing. Such a claim would require
the opposite construction

```
IND-CPA adversary -> EndRingEval solver,
```

or a named intermediate assumption plus explicit reductions on both sides.
No such reduction is supplied for P1, P2, or P3. Augmented level data are not
silently erased from the distribution. A generic ElGamal, LWE, KEM, hash, or
other PKE layer would remain controlled by its own assumption and is excluded.

## Cost and honest accounting

There is no finalist, so no finalist efficiency table exists. For the failed
definitions, common `KeyGen` has unresolved finite saturation, field, torsion,
and evaluated-map output costs (`K0`). Public encryption performs `a`
degree-2 quotient steps plus the stated projection. P1 exhaustive lift/decode
uses `D=2^a` reenactments; P2 uses `D*|SL_2(Z/NZ)|`; P3 is constant-size after
field encoding but fails correctness. Public keys contain one curve, four
torsion points, parameters, field/model certificates, and no connecting data.
Ciphertext sizes are respectively one curve plus one `N`-torsion point, one
curve plus two masked `N`-torsion points, and one `mu_N` element. All sizes
must charge `[F:F_p]`, coordinate encodings, canonicalization, factorization,
preprocessing, and validation.

The exact remaining mathematical obligation is singular:

> Construct and prove a uniform polynomial-time **one-column completion
> algorithm** `Complete_2(O,E,C,X,P,Q,D,N)` that, on every valid P1 ciphertext
> `(C,X=phi_s(P))` in the stated KeyGen/Encrypt support, outputs the exact
> second image `phi_s(Q)` (or an equivalent evaluable degree-`D` map), using
> only the evaluable basis/table of `O=End(E)` and the public inputs, with
> polynomial-size output, explicit failure probability, and no retained path,
> connecting ideal, orientation, `tau`, setup trapdoor, or extra secret; then
> prove that the same output is not computable from the public inputs under the
> audited Robert, finite-torsion linear-algebra, fixed-rank-lattice, public-Hom,
> public-reencryption, and public-inverse controls.

Passing the constructive half would only define a conditional recipient
decoder; the non-publicity and adversary-to-EndRing reduction would remain
separate obligations. Failure to construct it leaves P1 failed and says
nothing universal about EndRing-PKE.

