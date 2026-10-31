# Independent mathematical refinement: four designated points

Task: `TASK-20261029-912498`  
Joint: `J1`  
Archival task: `TASK-20261029-4cdb4c`  
Policy: `review-adversarial`, manual mathematical review  
Verdict: **holds**.

The sole source read for this refinement was
`/home/ec2-user/scratch/stark-affine-proof-20261029/TASK-20261029-912498/four-probe-refinement/blind-four-probes.md`.
Its SHA256 was checked and matches the supplied expected value:
`5de718cd2f7c8e9d8b9b335fbf038ba07a65b538e1bd0aab2825ade42f01dfa6`.
The input was preserved. This report and its accompanying attestation are new
refinement artifacts; the original review report and attestation were not read
or modified during this refinement.

## Exact assertion and manual derivation

Let `R` be a commutative ring with identity, allowing the zero ring, and let

\[
E_{a,b,c}(x,y)=ax+by+c.
\]

For a fixed triple `(a,b,c)`, define `C(a,b,c)` to be exactly the conjunction
in the input:

\[
\begin{aligned}
E_{a,b,c}(0,0)&=0\cdot0,\\
E_{a,b,c}(1,0)&=1\cdot0,\\
E_{a,b,c}(0,1)&=0\cdot1,\\
E_{a,b,c}(1,1)&=1\cdot1.
\end{aligned}
\]

Ring identities reduce these four equalities to

\[
c=0,\qquad a+c=0,\qquad b+c=0,\qquad a+b+c=1.
\]

The first equality gives `c=0`. Substituting it into the second and third
gives `a=0` and `b=0`. Substituting all three into the fourth gives `0=1`.
Therefore, when `R` is nontrivial, meaning `0 != 1`, the conjunction is false
for every triple:

\[
\forall a,b,c\in R,\quad \neg C(a,b,c).
\]

This is a direct proof of the exact finite assertion. It does not assert that
each of the four equations fails. For example, the zero triple satisfies the
first three equations and fails only the fourth in a nontrivial ring.

In ordinary classical terms, the result also supplies a disagreement somewhere
in the fixed set

\[
S=\{(0,0),(1,0),(0,1),(1,1)\}.
\]

A manual case description locates such a point: if `c != 0`, use `(0,0)`;
otherwise, if `a != 0`, use `(1,0)`; otherwise, if `b != 0`, use `(0,1)`;
otherwise use `(1,1)`. This describes the mathematical cases and makes no
claim of an implemented decision procedure for equality in an arbitrary ring.

There is also a single identity that records the same obstruction:

\[
E_{a,b,c}(1,1)-E_{a,b,c}(1,0)-E_{a,b,c}(0,1)+E_{a,b,c}(0,0)=0.
\]

For the four multiplication values, the corresponding expression is
`1-0-0+0=1`. Agreement at all four points would thus imply `0=1`.

## Necessary assumptions and the zero ring

Nontriviality is necessary for the stated universal denial of the conjunction.
In the zero ring, `0=1` and every element equals zero: for any `r`,
`r=r·1=r·0=0`. There is a single coefficient triple and all four displayed
equations are true. The four designated pairs also coincide.

More precisely, for any ring allowed by the input and any fixed coefficient
triple, the exact characterization is

\[
C(a,b,c)\quad\Longleftrightarrow\quad 0=1\text{ in }R.
\]

The forward implication is the manual derivation above. For the reverse
implication, `0=1` makes all elements, coefficients, and evaluated values zero.
Thus the zero ring is the exact exception, rather than just one possible
counterexample after removing nontriviality.

The proof uses multiplication by `0` and `1`, together with additive identities.
It uses no division, multiplicative cancellation, finiteness, absence of zero
divisors, or restriction on characteristic. In particular:

- In characteristic two, additive cancellation remains valid, and `0 != 1`
  still supplies the contradiction for a nontrivial ring. No division by two
  appears.
- In a composite-modulus ring such as `Z/4Z` or `Z/6Z`, zero divisors do not
  affect any substitution. Both rings have `0 != 1`, so the conjunction is
  impossible there as well.
- Commutativity is sufficient but is not needed for this particular proof;
  the same substitutions work in a ring with identity whose multiplication
  need not be commutative. The claim as supplied assumes commutativity and is
  established within that scope.
- The identity element is part of the supplied setting and specifies the
  probes and the value `1·1=1`. Removing the identity assumption would leave
  these formulas without the stipulated meaning of `1`.

## Relationship to global agreement

For a fixed triple, write

\[
G(a,b,c):\quad
\forall x,y\in R,\ E_{a,b,c}(x,y)=xy.
\]

Instantiation at the four designated points gives `G(a,b,c) ⇒ C(a,b,c)`.
Consequently, the finite obstruction `¬C(a,b,c)` immediately proves
`¬G(a,b,c)`. With the outer quantifiers over coefficients, the reviewed
assertion therefore proves that no affine expression agrees with
multiplication everywhere.

The four-point conclusion adds a precise localization of the disagreement:
one of the same four predetermined points works for every affine candidate.
Merely saying that a candidate fails somewhere does not state that
localization. In this sense, the finite assertion is a sharper certificate
of the global obstruction.

It would, however, be incorrect to claim a strict logical separation between
four-point agreement and global agreement within this exact family of
functions and rings. The derivation of `C(a,b,c) ⇒ 0=1`, followed by the zero-ring
calculation, gives `C(a,b,c) ⇒ G(a,b,c)` as well. Thus, throughout the input's
class of commutative rings with identity, for every fixed triple,

\[
C(a,b,c)\quad\Longleftrightarrow\quad
G(a,b,c)\quad\Longleftrightarrow\quad
0=1\text{ in }R.
\]

Their negations are likewise equivalent. The finite formulation strengthens
the explicit information about a witness location, but it does not define a
strictly stronger obstruction on these rings. Nontriviality is the exact
condition for both nonexistence statements.

This equivalence is specific to the asserted affine candidate and the target
multiplication function. It is not an interpolation rule saying that arbitrary
functions agreeing at these four points agree everywhere. For instance, over
the integers the non-affine polynomial function

\[
h(x,y)=xy+x(x-1)
\]

agrees with `xy` at all four designated points, since `x` is then `0` or `1`.
At `(2,0)`, it takes the value `2`, while multiplication takes the value `0`.
This example is a manual calculation illustrating the limitation of any
generalization beyond the supplied affine family.

## Scope, blind compliance, and limits

The derivations above use only the sealed mathematical input and elementary
ring identities. No producer repository, review plan, implementation, proof,
source notes, native outputs, sibling reports, histories, or memory were
consulted for this refinement. No builds, experiments, network access, or
package installations were performed. The file checksum records the actual
reviewed source; it is not native mathematical verification.

The verdict concerns the exact finite conjunction, its zero-ring exception,
and the logical relationship described above. It is manual mathematics only.
It does not verify Lean elaboration, Lean kernel acceptance, a theorem's
implementation-level statement, executable behavior, or scientific promotion.
