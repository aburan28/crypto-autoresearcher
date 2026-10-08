# Candidate A: UTTK (unoriented torsion-transport kernel interface)

## Disposition

`UTTK` is a **typed obstruction**, not a PKE and not a security claim. It is
the most direct curve/transcript-level interface found here whose forward map
is public from a bare supersingular curve. The earliest failed arrow is a
polynomial, basis-independent inverse: no algorithm is supplied that turns
**every** complete evaluable basis of `End(E)` into an endomorphism satisfying
the torsion-attack preconditions. Moreover, if such an endomorphism `theta`
were produced, inversion appears to factor through `(theta, AttackTT)` rather
than require the complete ring.

## Exact candidate interface

Let `p > 3`. The EndRing challenge distribution is fixed to the endpoint
distribution of a declared-length uniform nonbacktracking small-degree walk
from a public supersingular `E0/F_{p^2}` with Frobenius `[-p]`; only the
canonical endpoint curve `E` is returned and the walk is erased. This is a
candidate distribution definition, not an assertion that an EndRing theorem
covers it. Public parameters contain factored, coprime smooth integers
`n,N | (p+1)`, with bounded prime factors.

`X_E` contains `(R,P,Q)`, where `R` has exact order `n`, `(P,Q)` is an exact
`N`-torsion basis, and `phi_R` is the normalized cyclic isogeny with kernel
`<R>`. Generators `R` and `[u]R`, `u in (Z/nZ)^*`, are equivalent. The public
map is

```text
Trap_E(R,P,Q) = (E', P, Q, phi_R(P), phi_R(Q)),  E' = E/<R>.
```

`Sample` obtains exact-order points by public rejection sampling and checks
the basis with the Weil pairing. `Eval` evaluates the smooth isogeny as a
deterministically ordered chain of small-degree Velu steps. These algorithms
need only `E`, public parameters, and fresh coins; the torsion basis is sampled
and disclosed, not supplied by a hidden orientation.

The desired inverse receives a complete evaluable rank-four `Z`-basis `B` of
`End(E)` and the transcript and must return any generator of `<R>`, for every
valid `B`. A Seta-like torsion-attack outline would first derive a suitable
non-scalar `theta` from `B`, then use `theta` and the transported torsion basis
to recover the kernel. The repository pointer `KN-LIT-6572` reports this broad
trapdoor family from an abstract-level read, but neither its primary text nor
a theorem with this distribution and every-basis quantifier was read here.
Consequently both stages remain unavailable, and `Inv` returns the typed
failure `INV_ANY_BASIS_COMPILER_UNDEFINED`.

## Four cheap audits

1. **CEST/RWCT regression.** Replacing `B` by one attack-suitable `theta` and
   an `AttackTT` implementation would leave all inverse outputs unchanged.
   Thus syntactic provenance in a rank-four basis does not establish complete-
   ring necessity; this reproduces the finite-witness factorization pattern.
2. **Collisions and smaller witnesses.** Unit multiples of `R` are an admitted
   input equivalence. Distinct-kernel collisions yielding isomorphic pointed
   outputs were not ruled out. The smallest known conditional reusable witness
   is one attack-suitable evaluable endomorphism `theta` plus the torsion-attack
   procedure, not a complete basis. No reconstruction of `End(E)` from this
   witness was supplied.
3. **Quantifier order.** The obligation is `for every E` in the declared
   endpoint distribution, `for every valid complete basis B`, and every valid
   transcript. Enumerating short combinations in one planted basis does not
   meet it. The candidate fails at this quantifier.
4. **Known-false control and ceiling.** If `R` is appended to the output,
   inversion is public while the implication “an EndRing solver can invert”
   remains true. Hence that forward implication cannot prove security. Static
   analysis can type the public map and identify missing arrows; it cannot
   establish a family-level impossibility or an EndRing reduction.

## Reduction and PKE boundary

The first definable target is only one-way inversion of a random UTTK
transcript. No `KeyGen/Enc/Dec` wrapper is proposed. In particular, there is
no selected-message attacker-to-UTTK embedding, no simulator, and no
UTTK-inverter-to-complete-ring extractor. The only visible route is the wrong
direction:

```text
complete ring basis -> suitable theta (missing) -> kernel recovery (unverified)
```

Accordingly O1--O6 all remain open. O2/T2 has the earliest typed break, T3
has a conditional smaller-witness factorization, and T4 has no correctly
directed reduction.

## Scope controls and next useful lemma

`P=O` and lower-order points are parser controls obtained by weakening the
exact-order premises; they are not attacks on valid inputs. No `x(X)`-only
normalization or digit-loop assertion is used. The smallest useful future
lemma would be an explicit polynomial algorithm which, from every complete
evaluable basis on every curve in the distribution, produces an
attack-suitable `theta` with quantified success and cost. Even such a lemma
would leave the smaller-witness reconstruction and attacker-to-EndRing arrows
open.

