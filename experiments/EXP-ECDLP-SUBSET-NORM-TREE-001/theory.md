# Theory preflight: exact subset-norm self-reduction

## Claim boundary

The self-reduction below is an exact conditional theorem. It does not make the
node predicate cheap. The first companion-displacement/direct-approximant root
family is now `REJECTED_SCOPED`; alternate implicit coordinate operators remain
`CONJECTURE`, `UNTESTED`, and `REVIEW_REQUIRED`.

## Exact intersection encoding

Let `E(F_p)` have odd prime order. Register a nonsquare `delta in F_p` and let

```text
K=F_p[omega]/(omega^2-delta)
```

with canonical serialization as the base-field pair `(c_0,c_1)` for
`c_0+omega*c_1`. Every extension operation is charged by its exact base-field
addition, multiplication, inversion, serialization, and traffic vector. Encode
every finite point by

```text
enc(x,y) = x + omega*y in K.
```

This encoding is injective on oriented affine points. Handle the identity as a
separate sentinel.

Let `D2` be the distinct finite two-sum points, retaining one exact pair of
signed factor identifiers for each point. Let `D3` be the distinct finite
three-sum points, again with one exact triple witness per point. For target `Q`,
define the conceptual translated set

```text
T_Q = { enc(Q-S) : S in D3 and Q-S is finite }.
```

For any subset `I` of distinct oriented finite D2 points, define

```text
M_I(Z) = product over R in I of (Z-enc(R))
C_Q(Z) = product over z in T_Q of (Z-z).
```

If no finite translated root remains, define the empty product `C_Q=1`. If
`Q in D3`, omitting the translated identity lowers `deg(C_Q)` by one; exact
specialization must account for this without an undisclosed D3 membership
oracle. These definitions specify semantics only. Materializing `C_Q`, all of `T_Q`,
or one target bit per D2 leaf is forbidden on the candidate positive path.

## Exact node predicate

**Lemma.** For nonempty `I`, the following are equivalent:

1. some `R in I` and `S in D3` satisfy `R+S=Q`;
2. `M_I` and `C_Q` have a common root in `K`;
3. `gcd(M_I,C_Q)` has positive degree;
4. `Res_Z(M_I,C_Q)=0`.

**Proof.** Both polynomials split into distinct linear factors indexed by their
sets. They share a root exactly when `enc(R)=enc(Q-S)` for some `R,S`.
Injectivity of `enc` gives `R=Q-S`, which is equivalent to `R+S=Q`. The standard
gcd and resultant characterizations give the remaining equivalences.

Let `o_2` and `o_3` denote identity support in D2 and D3, with registered
witnesses, and let `Hit_ff(Q)` be the finite-finite predicate above. Full support
is

```text
Hit(Q) = Hit_ff(Q)
         or (o_2 and Q in D3)
         or (o_3 and Q in D2).
```

Membership includes the identity sentinel. When routes overlap, including
`Q=O` with both identity supports, deterministic priority returns one witness
and audit counters retain every multiplicity.

## Witness self-reduction

Build a balanced binary tree whose leaves are the distinct finite D2 points and
whose node polynomial is `M_I`. Suppose an oracle returns the exact node
predicate above.

If the root is negative, no finite D2+D3 witness exists. If it is positive,
query the left child; descend left when positive and right otherwise. Exactness
guarantees that the selected child remains positive. After
`ceil(log2(|D2|))` levels, the leaf gives a point `R` and its two-factor witness.
An exact terminal lift must then return one deterministically selected
registered three-factor witness for `S=Q-R`. Equal D2 or D3 sums are one
polynomial root but may carry many source witnesses; audit multiplicity is
separate from the one required output. Concatenation gives five signed public
identifiers, and independent affine addition verifies the target.

This proves logarithmic *oracle-call count*, not logarithmic time. The complete
cost is the sum of node-oracle specialization and evaluation along the path,
plus terminal witness lift.

## Exact terminal-lift baseline

Once the leaf gives `R`, set `S=Q-R`. Scan every signed factor `P` and probe
`S-P` in the already charged D2 dictionary. A hit returns `P` and the stored
deterministic pair witness, hence a three-factor witness for `S`. This takes
`Theta(B)` group subtractions and probes, handles repetition and identity through
the registry and D2 sentinel, and needs no explicit D3 advice. It is the Tier B
terminal-lift baseline; any faster lift must beat its complete operation and
traffic vector.

## Coordinate translation cover

The abstract map `S -> Q-S` is exact, but a rational-coordinate operator must
separate `Q=O`, `S=O`, `S=Q` with output `O`, `S=-Q` with doubling output, and
ordinary translation. Every branch needs exact guards, denominator inverses or
saturation, target-dependent degree semantics, and positive and negative
certificates. An exhaustive oracle may verify these branches but may not supply
the candidate's branch bit or path.

## Two claim tiers

### Tier A: online-only fixed-curve compiler

An explicit D3 dictionary may provide terminal membership and witness lift.
Its `Theta(B^3)` construction, advice bytes, and bandwidth are charged. A
passing Tier A result may improve fixed-curve online work, but it is not a
single-instance exponent result and does not satisfy compressed-advice Tier B.

### Tier B: compressed-advice compiler

The node operator and terminal lift must use total target-independent advice
`o(B^3)` while preserving exact membership and a three-factor witness. Moving
the D3 dictionary into pointers, seeds that regenerate it per query, a target
table, or an unreported auxiliary index does not satisfy Tier B.

## The actual open operator problem

For each tree node `I`, derive a target-independent representation `A_I` and an
exact specialization algorithm such that

```text
Node(A_I,Q) = 1 iff Res_Z(M_I,C_Q)=0.
```

The candidate lead is a transposed subset-norm computation whose linearized
maps have block-Hankel, approximant-basis, or bounded-displacement generators.
A valid derivation must state:

- the input and output modules;
- the matrix or polynomial operator before and after target specialization;
- the displacement equation and exact generator rank;
- all preprocessing and advice used to build every `A_I`;
- the sum of ranks, nonzeros, and operations on a root-to-leaf path;
- how a positive terminal predicate yields a D3 witness.
- how one chosen child is decided at each known-zero parent without rebuilding
  a D2-length target object, or how a direct root locator bypasses descent;
- exact certificates for both zero and nonzero node decisions, including
  identity and target-dependent degree-drop cases.

The previously proved full-rank convolution/profile results do not rule out a
compact full-rank structured operator: a circulant matrix can be full rank and
still have a short description. They do rule out claiming that an exact
low-dimensional image follows merely from rank loss.

## Scoped companion-displacement negative

`root-operator-preflight-v1.md` derives the exact identity-complete translated
polynomial `c_Q`, including ordinary translation, `S=Q` degree drop, `S=-Q`
doubling, `Q=O` conjugation, and both identity sentinels. In the quotient

```text
A_root=K[Z]/(M_root),
```

let `J` be multiplication by `Z` and let `T_Q` be multiplication by
`r_Q=c_Q mod M_root`. Then

```text
det(T_Q)=Res(M_root,c_Q)
Delta_J(T_Q)=J*T_Q-T_Q*J=0.
```

The rank-zero commutator is exact but non-identifying. Since `J` is cyclic,
`ker(Delta_J)=Cent(J)=K[J]` has dimension `N2`. In the frozen companion
interface, the boundary data identifying `T_Q` is its first column, exactly the
`N2` power-basis coefficients of `r_Q`. The frozen direct-factor interface
instead processes `N3` translated factors. These interfaces therefore fail the
root zero-run gate in the collision-light regime.

This is not a lower bound on the target family. A target-parametric matrix such
as `J-a(Q)I` shows that zero displacement can coexist with a one-scalar
description. Implicit scalar norms, nested source resultants, alternate
displacement operators, source-recursive circuits, batch specialization, and
hereditary child restrictions remain open and need new ledgers.

## Scoped nested-source norm negative

`nested-source-norm-preflight-v1.md` replaces distinct D3 by three ordered signed
source algebras `A_i=K[T_i]/(M_i)` and defines the exact scalar norm of the
denominator-cleared node membership value over

```text
A_123=A_1 tensor A_2 tensor A_3.
```

The norm vanishes exactly when one registered ordered triple completes a finite
D2 point in the node. D3 identity is included componentwise; the D2 identity is
checked only at the root by the charged `Theta(B)` factor scan. For finite
children, `M_I=M_L*M_R` gives exact norm factorization `R_I=R_L*R_R`.

This scalar semantics is exact, but known explicit interfaces recreate the
obstruction. In the balanced collision-light regime:

- a sequential dense first norm emits an `A_12` element with `Theta(B^2)`
  allocated target slots;
- direct ordered-triple evaluation processes `Theta(B^3)` tuples;
- standard product-basis determinant or Krylov vectors expose `Theta(B^3)`
  scalar coordinates;
- explicit branch idempotents or global units allocate `Theta(B^3)` coordinates.

These are `REJECTED_SCOPED` interface results, not lower bounds on the scalar
function. A separable tensor is a counterexample to any ambient-dimension lower
bound. Compact selectors, simultaneous or reordered elimination, structured
tensor contraction, scalar-only transposition, source-composition towers, and
parent circuits producing one chosen-child decision remain open.

## Scoped coordinate-moment and canonical-separation negative

`bounded-separation-preflight-v3.md` works in the actual split source algebra.
For `U_Q=A_Q/Delta_Q`, the minimal-polynomial degree equals the number `t_Q` of
distinct component values, so

```text
dim_K span{A_Q^k*Delta_Q^(n-k):0<=k<=n}=min(n+1,t_Q).
```

On the complete collision-light support, `t_Q=Theta(B^3)` and
`n=N2=Theta(B^2)`. A node-oblivious coefficient-linear interface that recovers
the complete algebra element therefore has width `n+1`. This is a restricted
linear-interface theorem, not a lower bound on one fixed nonlinear predicate.

For explicit CP descriptions of `A_Q` and `Delta_Q`, the uncollected canonical
symmetric-power slot count is

```text
sum_(k in supp(M_I))
  binom(k+r_A-1,r_A-1)*binom(n-k+r_D-1,r_D-1).
```

The global EC coordinate is not rank-one separable: its zero and pole divisors
are nonvertical addition fibers in `E^3`. Hence one global base rank is at least
two, although finite quotient reduction may still collapse active terms. The
explicit trace resolvent has recurrence order `t_Q` and recreates the
translated D3 polynomial. These explicit interfaces are `REJECTED_SCOPED`;
minimal quotient CP/TT rank and fixed-node nonlinear circuits remain open.

At a known-zero finite parent, first-witness descent evaluates one chosen child.
If its field norm is nonzero, the sibling norm must be zero. Both child values
are necessary only for all-root enumeration. Root-to-leaf work and traffic are
cumulative gates.

## Historical three-source TT zero-locator sketch

Status: `SUPERSEDED PAPER DRAFT` by the direct five-source construction in
`experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`. The paragraph
below is preserved as provenance, not as the current accounting surface.

The 2026 arbitrary-field TT normal form suggests a direct locator. For the
finite-branch membership tensor `G_Q`, define componentwise

```text
Z_Q=1-G_Q^(|K|-1).
```

Then `Z_Q[x]=1` exactly at source components where `G_Q[x]=0`. An exact leading
nonzero TT index would return the three signed source factors; one D2 lookup
returns the other two. This bypasses the subset tree and scalar norm.

The historical candidate was `OPEN`, `NOVELTY-UNVERIFIED`. Constructing `G_Q`
by dense Horner, D2 factor multiplication, or canonical CP enumeration already
hits the B2 boundary. The successor removes this unspecified three-source
object: it binds a complete five-source RCB circuit, an exact projective
equality scalar `g_Q`, and `1-g_Q^(p^2-1)`. Its exact final ranks are now known,
but its intermediate Hadamard/normalization ranks remain the fatal obligation.

## Immediate obstruction

Naively constructing `C_Q` costs at least its `Theta(B^3)` output size. Naively
evaluating membership at every D2 leaf emits `Theta(B^2)` target values. The
frozen companion interface also shows why displacement rank alone is
insufficient: its rank is zero while its standard boundary data is D2-sized. A
product tree by itself changes none of these facts. A successor begins only when
a coordinate-specific exact operator avoids both outputs and exposes a complete
sublinear representation including its kernel boundary data.

## Next concrete action

Use `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md` as the current
paper contract. Derive or refute the gate-by-gate central-rank certificate for
the bound RCB-plus-norm-indicator circuit. Source remains unauthorized if a
central rank reaches `Omega(B)`, any cumulative Tier-B target resource reaches
`Omega(B^2)`, or fixed advice/workspace reaches `Omega(B^3)`.
