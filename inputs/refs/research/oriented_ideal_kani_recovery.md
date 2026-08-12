# Balanced Oriented-Ideal Kani Recovery

Date: 2026-07-18

Status: `RESTRICTED THEOREM / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / NOVELTY-UNVERIFIED`

## Result

A nonprincipal ideal can replace the integer auxiliary in a balanced Kani
recovery diamond.  Let an unknown `R`-oriented isogeny have known degree `d`.
If a publicly computable invertible `R`-ideal `a` has norm `s` and

```text
n^2 = d + s,
```

then applying `a` to both public endpoints reveals all four corners of a Kani
diamond.  In the coprime case, the resulting `n^2`-similitude can be approached
from both sides by dimension-two `n`-isogenies using candidate action only on
`n`-torsion.  More generally, coprimality can be replaced by an exact
restricted-kernel cardinality test.  This evades the sharp principal-element
norm floor in a tall volcano because an ideal of small norm need not have a
small principal generator.

For interpolation-style recovery rather than only the Kani representation,
one must additionally require `n^2>4d`.

The block construction and ideal functoriality are standard Kani/module-action
theory.  The potentially new contribution is narrower: use the same
nonprincipal oriented ideal on both endpoints, search for the balanced shifted
norm equation, and treat its existence as a weak-instance condition for
vertical isogeny recovery.  Novelty is not yet established.

## Balanced ideal-diamond theorem

Let `R` be an imaginary quadratic order and let

```text
phi : E0 -> E1
```

be a separable `R`-oriented isogeny of degree `d`.  Let `a` be an integral,
proper, invertible `R`-ideal of norm `s`, prime to the characteristic and to
the conductor.  Apply the ideal action to both endpoints:

```text
E0  --phi-->  E1
 |             |
psi0          psi1
 |             |
F0 --phi'-->  F1.
```

Functoriality gives the exact square

```text
psi1 phi = phi' psi0.
```

Assume `n^2=d+s`, the characteristic does not divide `n`, and
`gcd(d,s)=1`.  Then

```text
M = [ phi    hat(psi1) ] : E0 x F1 -> E1 x F0
    [ -psi0  hat(phi')  ]
```

satisfies

```text
M^dagger M = [n^2] I_2.
```

Two maximal isotropic order-`n^2` half-kernels are

```text
K_left  = {(hat(phi)(Q), psi1(Q)) : Q in E1[n]},
K_right = {(phi(P), -psi0(P))     : P in E0[n]}.
```

The quotient of `E0 x F1` by `K_left` and the quotient of `E1 x F0` by
`K_right` are the two sides of the same intermediate principally polarized
abelian surface.  Thus candidate action for `phi` on `E0[n]` determines both
halves: on `n`-torsion, `hat(phi)` is the symplectic adjoint, equivalently
`[d] phi^(-1)` when the candidate is invertible.

### Proof sketch

The exact square and its dual cancel the off-diagonal blocks in
`M^dagger M`; the diagonal blocks are `[d]+[s]=[n^2]`.  The left kernel is
`M^dagger(E1[n],0)` and the right kernel is `M(E0[n],0)`.  Multiplication by
`M` or `M^dagger` kills these groups because `[n^2]` kills `n`-torsion.
The coprimality hypothesis makes both graph maps injective, hence each image
has order `n^2` and is maximal isotropic.  Standard Kani factorization then
identifies the two quotients as the middle surface.

This is a specialization of the standard Kani isogeny diamond, not a new
identity.

## Non-coprime transversality theorem

Let `A` and `B` be principally polarized abelian surfaces over a field whose
characteristic does not divide `N`.  Let `M:A->B` be a separable isogeny with

```text
M^dagger M = [N^2].
```

Define `H_A=ker(M) intersect A[N]`.  If `#H_A=N^2`, then:

1. `ker(M)` has group type `(Z/N^2 Z)^2`;
2. `H_A` is maximal isotropic in `A[N]`;
3. the quotient `alpha:A->C=A/H_A` is a polarized `N`-isogeny and `M`
   factors as `M=beta alpha`, where `beta:C->B` is another polarized
   `N`-isogeny; and
4. `H_B=ker(M^dagger) intersect B[N]` automatically has order `N^2`, equals
   `ker(beta^dagger)`, and gives the same middle principally polarized surface
   `C` from the `B` side.

No coprimality assumption on the degrees of the blocks of `M` is required.
The cardinality is geometric group-scheme rank; rational-point counts are not
a substitute.

### Proof

The polarization identity gives `M^*lambda_B=N^2 lambda_A`, so `M` is a
polarized `N^2`-isogeny, `deg(M)=N^4`, and `ker(M)` lies in `A[N^2]`.  For
`ell^e || N`, write its elementary-divisor valuations as
`0<=a_i<=2e`, with `sum_i a_i=4e`.  Then

```text
log_ell #H_A[ell^infinity] = sum_i min(a_i,e).
```

Since `min(a_i,e)>=a_i/2`, this sum is at least `2e`.  Equality holds only
when every `a_i` is `0` or `2e`; the total sum then forces the Smith type
`(0,0,2e,2e)`.  Hence globally

```text
ker(M) = (Z/N^2 Z)^2,     H_A = [N]ker(M) = (Z/N Z)^2.
```

The full kernel is maximal isotropic at level `N^2`, so Weil-pairing
compatibility makes `H_A` isotropic at level `N`; its order makes it maximal.
Polarization descent gives a principal polarization on `C=A/H_A` with
`alpha^*lambda_C=N lambda_A`.  Since `H_A` lies in `ker(M)`, write
`M=beta alpha`.  Pulling back polarizations and using injectivity of pullback
by an isogeny gives `beta^*lambda_B=N lambda_C`.

Finally, `M` and its Rosati adjoint have the same Smith invariants because
their Tate-module matrices differ from transposes by unimodular symplectic
changes of basis.  Thus the `B`-side kernel also has order `N^2`.
The inclusion `ker(beta^dagger) subset H_B` is therefore an equality, proving
the two-sided statement.

Candidate action on `A[N]` determines `M` modulo `N`, so this transversality
gate is computable before either quotient is evaluated.  The theorem is a
general polarization/Smith-type criterion; its use as a same-ideal recovery
screen remains narrow and novelty-unverified.

## Recovery algorithm

```text
BALANCED-IDEAL-KANI(E0,E1,R,d, candidate ideals, torsion candidates):
    for each computable ideal a:
        s := Norm(a)
        reject unless d+s is a square n^2
        reject unless n is powersmooth and its torsion field is accessible
        compute psi0:E0->F0 and psi1:E1->F1

        for each candidate A for phi on E0[n]:
            derive the adjoint candidate A^dagger on E1[n]
            build K_left from A^dagger and psi1
            build K_right from A and psi0
            reject unless both kernels are maximal isotropic
            compute the two dimension-two n-isogeny halves
            if their intermediate PPAVs match:
                split/normalize the Kani representation and return phi
    return failure
```

The public ideal does **not** reduce torsion uncertainty.  Since `gcd(s,n)=1`,
`psi1` is invertible on `n`-torsion, so knowing `psi1 phi` is equivalent to
knowing `phi` there.  Self-pairings or another leakage source must still
supply the candidate list.

## Honest cost model

Let

- `T` be the number of candidate secret actions on `E0[n]`;
- `B` be the largest prime dividing `n`;
- `r_n` be the smooth-chain length, including exponents;
- `U_n` be the relevant torsion/compositum field degree;
- `C_a(Ei)` be the fully charged ideal action on endpoint `Ei`;
- `C_search` include balanced-witness search and factoring;
- `C_split` include theta conversion, middle-surface recognition, and map
  extraction.

The conditional dimension-two cost is

```text
C_search + C_a(E0) + C_a(E1) + C_torsion
+ T * O~(r_n U_n B^2 log q) + C_split.
```

If a full candidate list for the action on `E0[n]` is already available, the
ideal auxiliary changes only the higher-dimensional backend term; it does not
reduce `T` or `U_n`.  This statement does **not** directly apply to the cyclic
self-pairing branch of GGR: that branch first composes the secret isogeny with
an `m`-isogeny in order to turn cyclic torsion information into full torsion
information.

The same integer Kani architecture costs `B^4` when `n^2-d` is two squares
and `B^8` in the four-square worst case.  These are backend comparisons.  An
end-to-end improvement follows only when ideal search/action and the unchanged
`T` term do not dominate a direct class-group or isogeny-recovery baseline.

### Failed direct transfer to cyclic self-pairing recovery

An earlier draft claimed that the dimension-two auxiliary immediately changed
the supersingular GGR backend from `T sqrt(Delta0) B^10` to
`T sqrt(Delta0) B^4`.  That transfer is **not proved** and is withdrawn.

The obstruction is structural.  Let `f` be the original ascending degree and
let `m|Delta0` be the cyclic self-pairing factor.  GGR composes the unknown
isogeny with an `m`-isogeny, producing an isogeny of degree

```text
D = m f
```

and reconstructs it with modulus `N=n1*m`, where `n1^2*m>4f`.  A balanced
ideal auxiliary for this actual Kani instance would therefore need

```text
Norm(a) = N^2-D = m(n1^2*m-f).
```

Both `D` and `Norm(a)` are divisible by `m`.  This violates the coprimality
hypothesis used above to make the two graph maps injective and to prove that
the displayed order-`N^2` half-kernels are maximal isotropic.  The verified
`F_29` experiment has `gcd(d,Norm(a))=1` and therefore does not test this case.

The non-coprime transversality theorem does not rescue the natural cyclic
self-pairing block.  Let `ell^r || m` in the usual regime
`gcd(ell,n1*f)=1`, and work at a maximal ramified oriented local order with
uniformizer `varpi` satisfying `varpi*bar(varpi)=ell`.  Both the degree-`D`
map and an invertible auxiliary of norm `N^2-D` have local factor
`varpi^r`.  The block therefore has local Smith type

```text
(varpi^r, varpi^(3r)).
```

As a rank-four `Z_ell` map its elementary-divisor valuations are

```text
floor(r/2), ceil(r/2), floor(3r/2), ceil(3r/2).
```

It follows that

```text
#ker(M|A[ell^r]) = ell^(3r),
```

not the required `ell^(2r)`.  For `r=1`, the restricted kernel has rank three
over `F_ell` and cannot be maximal isotropic.  Thus the transversality gate
rejects the standard same-ideal cyclic composition at every such shared
ramified prime.

There is also no canonical oriented half hidden inside this oversized kernel.
For `r=1`, write the ramified residue order as
`F_ell[epsilon]/(epsilon^2)`.  In a local basis the block is
`epsilon*C`, where `C` has rank one modulo `epsilon`.  If `L=ker(C)` then

```text
K = ker(M|A[ell]) = L direct_sum F_ell^2
```

has dimension three.  Its restricted alternating form has one-dimensional
radical `Rad(K)`, and `K/Rad(K)` is a symplectic plane.  Maximal-isotropic
planes inside `K` are therefore in bijection with the lines of
`K/Rad(K)`, so there are exactly

```text
ell + 1
```

of them.  Multiplication by `epsilon` maps all of `K` into `Rad(K)`, hence
every one of these planes is stable under the local oriented order.  The
orientation does not distinguish a preferred choice.

For squarefree `m`, Chinese remaindering gives at least
`product_(ell|m)(ell+1) > m` globally oriented half-kernel choices.  Thus
enumerating internal maximal-isotropic subgroups erases the hoped-for
self-pairing saving before middle-surface recognition.  This is a restricted
local obstruction for the natural same-ideal block; extra public structure or
a different auxiliary could still select a branch without enumeration.

Consequently, the synthetic `258/390/160/24`-bit screen and its claimed
`9.5`-bit margin are retained only as a diagnostic for the now-falsified
coprime substitution.  They are not a SCALLOP complexity result.  A valid
cryptographic corollary requires one of the following new ingredients:

1. a rule selecting and transporting a maximal-isotropic order-`N^2`
   subgroup strictly inside the oversized restricted kernel;
2. a way to convert the cyclic self-pairing information to full torsion action
   without introducing the shared factor `m`; or
3. an independent leakage source that supplies the full candidate action for
   a coprime balanced modulus.

This is now a scoped negative result for the direct same-ideal transfer, not
merely a missing proof.  Until one of the escape routes is established, there
is no claimed improvement to the published SCALLOP or PEARL-SCALLOP attack
complexities.

The frozen unbalanced cost diagnostic charged both endpoint chains and both
torsion basis images under linear and quadratic chain proxies.  All twelve
proxy rows favored dimension two even at `T=1`, but this is not a field-
operation benchmark and its arbitrary `N=d+s` census uses full `N`-torsion.
It is implementation guidance, not recovery evidence.

## Experimental evidence

### Non-coprime finite-module transversality

An exact producer tested the transversality theorem on the standard rank-four
symplectic module for composite `N=4,6,12` and three deterministic basis seeds
per modulus.  All nine positive maps satisfy `M^dagger M=[N^2]`, have Smith
diagonal `(1,1,N^2,N^2)`, and have order-`N^2` maximal-isotropic restricted
kernels on both sides.  Explicit polarized factors `M=beta alpha` match those
kernels exactly.  Nine controls of the form `M=N*S` retain the global
similitude identity but have restricted-kernel order `N^4` and reject.

Producer and independent-verifier payloads are

```text
e6796d600bfd1ec38eb1f554b3d5aa851d8ea14224c0270eba061fd5a19aae3f
f45e11c311b31f54a10431cf482fe5976bd8b236f7fb3f3ddea5315880642d14
```

The verifier passes 27 assertions and rejects four semantic mutations.  This
is exact finite-module evidence.  It does not test an abelian-variety block
matrix, middle-surface recognition, recovery, or SCALLOP parameters.

### Ramified local branching census

The local obstruction was instantiated exactly for
`(b,ell)=(2,5),(4,17),(6,37)` in the ramified model
`varpi^2=-ell`, `ell=b^2+1`, with block

```text
M = varpi * [[1,b],[-b,1]].
```

All three blocks satisfy `M^dagger M=[ell^2]`, have integer Smith diagonal
`(1,ell,ell,ell^2)`, restricted-kernel dimension three, pairing rank two, and
radical dimension one.  Complete enumeration of every two-plane gives
`6,18,38` oriented maximal-isotropic planes, exactly `ell+1`.  Producer and
independent-verifier payloads are

```text
f03a541ac07db04a72c47cd6a5879b78378b29451a17e712bfebafb3bf5e794e
bd9a8c76407b7bf84bc33dc7b02a6d88068e80d1235b5d3ff3ee79e6f0feecd0
```

The verifier passes 11 assertions and rejects three semantic mutations.  A
V1 predecessor failed before arithmetic on an obsolete Sage constructor
signature and remains preserved with contract/source hashes
`974937a0...afb5` / `306ca88f...b89f`.

### Exact ideal diamond

Over `F_29`, trace `6`, the floor/crater discriminants are `-80` and `-20`.
The degree-2 ascent and matching nonprincipal norm-7 ideal give

```text
3^2 = 2 + 7.
```

The independently replayed fixture verifies all four block equations,
maximal isotropy on 9-torsion, two matching ideal directions, two rejected
mismatches, and a strict integer-dimension `8 -> 2` drop.  Producer/verifier
payloads are

```text
658a56c89c90100a24bc7347713c682a378b6041e9fc6e55507606dc2e3343cd
07963cc06be9e02815446a8eafadaa407c26fa685f1d0efa79c4d74e7fd8ab64
```

This is an algebraic full-kernel certificate, not a two-half theta recovery.

### Full-degree theta companion

Over `F_61`, trace `8`, a degree-3 ascent and nonprincipal norm-5 ideal give
`8=3+5`.  The existing product-theta backend launches all six compatible
basis transforms, kills both graph generators, and reaches exactly the public
factor multiset.  The strict drop is `4 -> 2`; graph and payload mutations
reject.  Producer/verifier payloads are

```text
91577a747c24b135fcfdb748814f4a11a76bba4871fa73f7663cfb331d927246
34d21216645910ed3bfbedad2b1b30c69da984c39e867bc0c665d3c7609c1453
```

This uses full 8-torsion and is not the balanced square-root information
model.

### Exact balanced two-half split below the recovery threshold

Over `F_881`, trace `12`, a degree-13 ascent and matching nonprincipal
norm-3 ideal give

```text
4^2 = 13 + 3.
```

The exact target-separated implementation constructs both order-16,
rank-two maximal-isotropic half-kernels from 4-torsion candidate action.
Each half is evaluated as two `(2,2)` theta stages of polarized degree 4.
For all three frozen seeds, the two halves reach the same normalized genus-2
midpoint, with normalized-codomain and absolute-Igusa hashes

```text
30f2b196ef11b42eb3e7f1ade169761cdfbf2427dba6fc56e1ede2db2ae8c9de
0217d3911065f3f2f40d845ba141c494ccbece6ad6fa95c4a47a0770754cc0f3
```

Both matching ideal directions pass and both mismatched directions reject.
The full block independently satisfies `M^dagger M=[16]`, and the strict
integer-auxiliary comparison is dimension `8 -> 2`.  The producer and
independent-verifier payloads are

```text
cd10b489313477dcd14b06d7e740f49dc06784cfcbf5b2e879349e5165ca8d2e
f21de13e7caae5f9b4516549ce29d9debcd3e4b8b469a9cba0be2428569373fc
```

This closes the balanced split-plumbing obligation, but it is deliberately
not a recovery result: `16<4*13`, so the interpolation uniqueness condition
fails.  Equality is certified at the normalized genus-2 moduli level; an
explicit theta-coordinate isomorphism between the two presentations is not
serialized.

### Recovery-admissible odd-degree split

The strict `F_29` fixture has trace `6`, degree `d=2`, nonprincipal ideal norm
`s=7`, and

```text
3^2 = 2 + 7 > 4*2.
```

The implementation translates the published BHLS degree-3 gluing formulas,
constructs the two `(3,3)` quotient dictionaries independently, and binds
each genus-2 curve to its exact graph anti-isometry using all nine 3-torsion
points and Mumford pullbacks.  Full 3-torsion lives over `F_(29^2)`; the older
degree-6 field was needed only for full 9-torsion.

For each of three symplectic-basis seeds, the raw determinant-2 action census
contains 24 matrices.  Exact Frobenius commutation admits only the true action
and its target-sign mate.  Both candidates meet at the unique exact absolute-
Igusa class

```text
6b2a60370e6880d9fbb4b2f4a64c2e4205c8cc65e0b3d46da612ac4946d0bd75
```

and no other raw action reaches the base-field gluing backend.  Each side has
one inequivalent BHLS gluing, two sign-related graph matrices, and one Igusa
class.  The strict integer comparison is again dimension `8 -> 2`.

The producer payload is

```text
d334bc53a1f367a5124d5d4bbb898d2998b65b3d6407051af2913428cb506560
```

and a separate source/process replays 46 assertions with payload

```text
3ea3856b5a5505ca6bcba0870a6824e5e0b9b58ddfe46a101a68f64495b30a5e
```

Two failed predecessors remain preserved.  V1 confused the least full
3-torsion field with the older full-9-torsion field; V2 completed both BHLS
dictionaries and then failed on a missing nested serialization key.  Neither
failure was overwritten.

This closes a recovery-admissible split-plumbing gate on a toy fixture.
Frobenius already isolates the sign orbit before Kani matching, so the fixture
does not demonstrate candidate recovery, map extraction, a large candidate
search, or a practical speedup.

### Auxiliary availability

An initial smooth-`N`-first unbalanced search tested 12,000 candidates and
found 47 smooth differences but zero valid ideal norms.  Reversing direction
and generating valid ideal norms first found `10,15,12` smooth Kani degrees at
32, 48, and 64 bits.  These results establish search-direction sensitivity,
but neither is balanced recovery evidence.

The balanced successor sampled powersmooth `n` and factored `n^2-d` with
`B=d^(1/4)` in the fixed order of fundamental discriminant `-20`:

| Size | Prime-smooth `n` | Smooth differences | Strict ideal hits |
|---:|---:|---:|---:|
| 32 | 8,000 | 16 | 1 |
| 48 | 8,000 | 23 | 2 |
| 64 | 8,000 | 34 | 0 |
| 64 holdout | 40,000 | 143 | 1 |

The 8,000-candidate campaign is a `NEGATIVE RESULT` under its all-size
criterion.  The disjoint 64-bit holdout passes and its sole strict hit is

```text
difference = 44246718550921610787
             = 3 * 7^2 * 23 * 229 * 18587 * 48781 * 63029,
n          = 7312324568
             = 2^3 * 83 * 443 * 24859.
```

All but one of the holdout's 143 smooth differences fail inert-prime parity.
This is sparse availability evidence, not a stable density law.  The V2 and
V3 independent verifier payloads are

```text
c68c32e1e7d92e1f154caa4eb64c119762091091c373461a20af152f73f5decc
ca5a0d6daf21f36016e66b321d11e344e67c2407090695408f8e5ab61851e913
```

The candidate generators admitted `P+(n)<=B` (largest prime bounded), not the
stricter prime-power condition `P*(n)=max(p^e)<=B`.  The ineligible counts are
828, 131, 22, and 97 in the four rows above.  Every strict ideal hit remains
eligible under the stricter condition; its corrected rank is 5,205, 450, and
20,029 for the successful 32-, 48-, and 64-bit streams.  These are sorted
ranks after the candidate pools were generated, not streaming discovery
costs.

## Principal-norm contrast

For an order of discriminant `D`, the least non-scalar principal norm is
`ceil(|D|/4)`.  On a floor with `D=Delta0*d^2`, no non-scalar principal
element can satisfy `n^2-d=O(d)`.  A nonprincipal ideal of norm `O(d)` escapes
that theorem.  The price is two genuine ideal actions; an effective principal
orientation element would have been much cheaper to evaluate.

## Cryptographic implications

The coprime result suggests a concrete parameter-screen condition.  Given a public
orientation order, known recovery degree `d`, and a basis of efficiently
computable ideal actions, reject or audit parameters admitting a short witness

```text
(a,n):  Norm(a)=n^2-d,
```

where `a` has a cheap action chain, `n` is powersmooth, and `E[n]` has an
accessible field of definition.  A parameter generator can scan bounded-weight
products of its action primes and test the square condition exactly.

Conversely, a malicious parameter generator could deliberately choose
`d=n^2-Norm(a)` and then construct a compatible isogeny class.  This would
plant a dimension-two recovery backend.  It is not by itself a trapdoor break:
the attacker still needs a small torsion-candidate set and an end-to-end cost
below direct recovery.  Current SCALLOP/PEARL-SCALLOP parameters have not been
shown to admit such a witness and are not claimed broken.

For the cyclic self-pairing architecture, the corresponding screen must use
the composed degree and modulus

```text
D=mf,  N=n1*m,  Norm(a)=N^2-D,
```

and then evaluate the transversality gate on the actual block matrix.  The
local calculation above shows that the natural same-ideal block fails this
gate at the shared ramified primes.  This gives a concrete defensive audit:
the simple planted coprime witness does not silently transfer into GGR's
cyclic recovery architecture.  It does not prove that every different
non-coprime auxiliary or internal isotropic-subgroup selection must fail.

The internal-subgroup fallback is also unattractive without a new selector:
for squarefree `m` it presents more than `m` oriented branches.  This branch
factor would dominate the self-pairing gain that motivated the substitution.

For the published 256-bit PEARL-SCALLOP shape quoted in GGR,
`log2 Delta0` is about `258`, `log2 f` about `390`, and the known
`2^16`-smooth factor has only about `33` bits.  Even the dimension-two backend
cannot repair the unchanged requirement `m>T^2 sqrt(Delta0)`, whose right
side already exceeds 129 bits before the `T^2` factor.  The public parameter
set therefore remains outside this conditional attack for a stronger reason
than backend smoothness alone.

The inverse generator was tested at conductor sizes 32, 48, 64, 96, and 128
bits.  It used only primes below `2^16` for both the torsion modulus and ideal
norm, set prime `d=n^2-s`, and then found a prime
`q=k^2+5d^2` with Frobenius discriminant `-20d^2`.  All five independently
verified tuples passed.  The 128-bit tuple required 1,004 outer attempts and
one field-prime trial; its field has 257 bits.  Producer/verifier payloads are

```text
a571a72607b7cf12527e823617bbae3bc7f3fbcd394e996d396b41088d47f79b
637d40f030d11a53d2f3586741e277097ef6b9604a709db43987cfcd9970e7ed
```

This is constructive evidence that weak parameters are easy to plant.  It
does not show that the planted `n` is hidden: the forward interval has about
`d^(1/2)` integers, but specialized shifted-smooth or parameter-provenance
attacks have not been ruled out.  Transparent, seed-verifiable parameter
generation is therefore a stronger mitigation than relying only on a bounded
witness scan.

A versioned cryptographic-size arithmetic replication at 192, 256, and 390
conductor bits also passed with the same `2^16` factor cap.  The 390-bit tuple
used 1,611 outer attempts, a torsion chain of length 16, an ideal chain of
length 27, and 3,681 field-prime trials; the resulting prime field has 782
bits.  Its public forward square interval has about `2^195` integers.  The
producer/verifier payloads are

```text
e35bf8bde8e9bdea0476e7625b2a59c8e0c9ad277b2946415f8705d596beeaac
51600772420bd8b4c33e21e826d84cd79baf7f568f110e36f4771d2b3bcf72e8
```

These figures show an asymmetry between planting and naive public scanning;
they do not prove witness concealment against specialized algorithms.

This construction does not break ECDLP.  Isogeny recovery transports a
discrete logarithm but does not solve it unless the target curve has an
independent weakness.

## Novelty and limitations

- The Kani matrix, orthogonal half-kernels, and ideal module action are known.
- GGR Section 4.3 already gives known-degree, candidate-torsion-action,
  balanced two-half Kani recovery.  Robert's module-action Propositions
  4.32--4.33 already act a compatible ideal/module functorially on an
  isogeny.  Clapoti and KLaPoTi already use nonprincipal ideal classes in
  dimension-two Kani computations, while SQIsign2D and Orient Express already
  search shifted auxiliary norm equations.
- Backdoored isogeny curves and smooth-witness-first parameter generation are
  also prior art, including Seta, torsion-point backdoors, SCALLOP, and
  PEARL-SCALLOP.  The broad trapdoor narrative is not novel.
- The audited primary literature already contains broad balanced Kani
  recovery, nonprincipal ideal Kani auxiliaries, shifted norm selection, and
  malicious isogeny-parameter generation separately.  It did not reveal the
  exact single-ideal recovery specialization or shifted-witness screen.  The
  defensible position is narrow application/selection novelty, stated as "to
  our knowledge," not a new Kani theorem.
- GGR already gives a different favorable `B^4` SCALLOP scenario.  Ray's
  correct-degree auxiliary-isogeny work is a particularly close comparison;
  transparent generation needs a transcript-security model; and current
  direct-recovery comparisons must include newer oriented-isogeny algorithms.
  These comparisons further narrow the novelty claim.
- The balanced census omits actual torsion-field degrees and uses synthetic
  32--64-bit degrees.
- Its accepted-candidate counts use largest-prime smoothness; only the strict
  hits were post-audited for the stronger prime-power condition.
- Its action bound `d^(1/4)` grows too large for naive Velu evaluation at
  cryptographic sizes.  Compact class-action machinery or much smoother ideals
  would be required.
- Candidate multiplicity `T`, two endpoint actions, middle recognition, and
  direct MITM/rho baselines remain mandatory costs.
- The exact power-of-two split passes below the recovery threshold, and the
  odd-degree BHLS split passes above it only on one toy fixture whose public
  Frobenius gate leaves two sign-equivalent candidates.

## Next concrete action

Search for extra public structure that selects one of the `ell+1` local
maximal-isotropic planes without enumerating them, or construct a different
auxiliary whose shared-prime restricted kernel passes transversality.  The
next experiment must use a geometric `m>1` block, compare every selected
dual-side quotient, and charge the branch selector.  Do not run a
cryptographic parameter census or claim a SCALLOP improvement unless that
selector beats the `product(ell+1)` branch barrier.
