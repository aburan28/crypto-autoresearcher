# P1533 R1 independent collision-resultant audit

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1533`
- Producer artifact:
  `ideas/artifacts/ECDLP-IDEA-003/p1533_collision_multiset_resultant_spec.md`
- Artifact class: independent theorem-only reconstruction and scoped no-candidate audit
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__NO_SUBRHO_COLLISION_RESULTANT`
- Evidence scale: symbolic interface, identity, representation, and cost audit; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

The producer's corrected Gallant interface, affine-compression bound, balanced-CRT
normalization, and exponent target reconstruct. This audit supplies an exact
cross-resultant derivative identity that recovers the common compressed label without
ordered rows. It then writes that attempt through the balanced quotient, split
coordinate algebra, source-localization recursion, and union-gcd control. Every
explicit realization tested either constructs the row values, materializes a dense
invariant representation, or performs a rho-scale intersection. No tested operation
has both `c_C,b_C<1/2`.

This is a scoped no-candidate result for the admitted constructions, not a lower bound
for every arithmetic circuit or every future use of elliptic resultants.

## Reconstructed balanced collision

Retain

```text
ell-1=A*D,                 |H|=D,
A=A_1*A_2,                gcd(A_1,A_2)=1,
J_1=<a^(A_2)>,            |J_1|=A_1,
J_2=<a^(A_1)>,            |J_2|=A_2,
A_1,A_2=K=ell^((1-alpha)/2+o(1)).
```

All subgroup notation here is in `F_ell^*/H`; representatives in `F_ell^*` are used
when multiplying points. Because `J_1 x J_2` maps bijectively to the quotient, write

```text
xH=x_1*x_2,                x_i in J_i.
```

The two label sets are

```text
U={z_eta([j_1]P): j_1 in J_1},
V={z_eta([j_2]Q): j_2 in J_2}.
```

Since `Q=[x]P` and the label identifies an `H` orbit, equality occurs exactly when

```text
j_1 H = j_2*xH,
j_1=x_1,                  j_2=x_2^(-1).
```

Thus there is one true cross equality. Conditioned on pole-free setup and no false
affine-hash collision, it is the unique cross equality. The producer's union bound

```text
Pr[false cross equality] <= K^2/p = ell^(-alpha+o(1))
```

is correct. Balanced factorization is still a restricted order-family condition and
its generation and density costs remain mandatory.

## The full scalar resultant is tautological

Enumerate the two compressed-label sets as `U={u_i}` and `V={v_j}` and define

```text
C_U(Z)=product_i (Z-u_i),
C_V(Z)=product_j (Z-v_j).
```

Their scalar resultant is

```text
Res_Z(C_U,C_V)=product_(i,j) (u_i-v_j).
```

For every valid challenge `Q=[x]P`, the balanced CRT proof above supplies one common
label, so this resultant is zero for every `x`. It is therefore an identically true
predicate on the valid challenge family. It neither reveals the common root nor
localizes its source. A useful direct construction must return more information than
the full-set zero bit or must support proper-subset calls.

This is an exact obstruction to the producer's weakest scalar-predicate
interpretation. It is not an obstruction to a witness-bearing resultant.

## Exact derivative witness

There is a simple witness-bearing deformation. Define

```text
R(t,s)=product_(i,j) ((1+s)*u_i-v_j+t).
```

Let the unique common pair be `(i_0,j_0)` and let its value be
`z=u_(i_0)=v_(j_0)`. At `(t,s)=(0,0)`, the corresponding factor is zero and every
other factor is nonzero. Therefore

```text
dR/dt (0,0) = product_((i,j)!=(i_0,j_0)) (u_i-v_j),
dR/ds (0,0) = z*product_((i,j)!=(i_0,j_0)) (u_i-v_j),
z = (dR/ds (0,0))/(dR/dt (0,0)).
```

The denominator is nonzero under the unique-cross-equality condition. The identity
also handles `z=0`. If a false compressed collision creates another zero factor, the
simple derivative vanishes or becomes ambiguous; that branch is covered by the
`K^2/p` error bound and mandatory final scalar verification.

This identity is an exact direct cross-resultant attempt and a genuine output of the
audit. It recovers the common compressed label without ordered row materialization.
It does not by itself evaluate the two derivatives or recover `(i_0,j_0)` below rho.

## Direct evaluation and localization costs

From explicit row values, the derivatives require `K^2` pair differences after the
`2K` labels are available. Each H-invariant label has the producer's most favorable
known square-root-orbit cost `D^(1/2+o(1))`. Hence

```text
row construction: K*sqrt(D) = sqrt(K^2*D) = ell^(1/2+o(1)),
pair arithmetic:   K^2       = ell^(1-alpha+o(1)).
```

At the balanced choice `alpha=1/2`, both terms have exponent `1/2`. For
`alpha<1/2`, pair arithmetic is worse; for `alpha>1/2`, row construction remains
exactly rho.

One can instead ask whether the entire pair grid can be treated as one elliptic
product. The grid has `K^2=A` quotient pairs, and every comparison contains an
H-orbit label. Even granting a single favorable square-root product over the resulting
`A*D=ell` scalar-orbit terms gives

```text
sqrt(A*D)=sqrt(ell).
```

The known square-root elliptic-product formulas apply to special addition-law
products; they do not supply this nested difference-of-orbit-label evaluator. The
rho estimate is therefore a generous control, not an implemented algorithm or a
universal lower bound.

After `z` is recovered, deterministic source recovery asks which subsets satisfy

```text
product_(i in I) (z-u_i)=0,
product_(j in J) (z-v_j)=0.
```

In the balanced direct product, a subgroup/coset subdivision tests membership in a
set of `Theta(ell)` scalar terms once the inner `H` action is included. A favorable
square-root orbit evaluation costs `ell^(1/2+o(1))` for the first informative bit.
Arbitrary interval halves have no stronger complete-subgroup structure. Evaluating
singleton labels through the bisection tree returns to `K*sqrt(D)=sqrt(ell)`.
Thus the derivative witness does not remove the producer's missing outer composition.

## Relative norm in the split coordinate algebra

Let `B` be the reduced coordinate algebra of the nonzero rational prime subgroup
modulo sign. Because all scalar points are rational and separable,

```text
B is isomorphic to Map(G/{+1,-1},F_p),
B^H is isomorphic to F_p^A.
```

The H-invariant compressed label is an element `f` of `B^H`. A characteristic
polynomial for a `J_i` slice is the evaluation at the challenge point of the relative
norm

```text
Norm_(J_i)(Z-f)=product_(j in J_i) (Z-j(f)).
```

This is the requested relative-norm formulation. Two standard representations do
not compress its payload:

1. In the orbit-coordinate basis, multiplication by `f` is diagonal. The relevant
   diagonal contains the `K` independent H-orbit labels. Constructing it with the
   favorable orbit evaluator costs `K*sqrt(D)=sqrt(ell)`.
2. In the cyclic Fourier basis, multiplication is circulant. The P1532 disjoint-pole
   argument proves that no quotient Fourier mode vanishes identically. A full
   orientation-free representation is dense, while selecting or normalizing one mode
   reintroduces the hidden-scalar character orientation.

The full invariant algebra has dimension `A`; a generic determinant or multiplication
matrix is worse than the slice table. Universal elliptic Gauss sums provide
character-weighted torsion information, but no audited formula constructs this
challenge-oriented partial norm without the dense modes or hidden orientation.

Applying a square-root Velu formula externally to
`g(R)=Z-z_eta(R)` is also unsupported. The fast product formulas exploit the specific
low-degree addition relation of the point-coordinate factor. They do not make an
arbitrary already-aggregated, high-degree H-invariant function into a unit-cost input.
Assuming nested costs `sqrt(K)*sqrt(D)` would erase the coefficient and degree traffic
that this audit is required to count.

These are representation-specific no-pass results. They do not prove that no compact
relative-norm circuit exists.

## Union-gcd control

An exact alternative avoids compressed labels. Form the coordinate polynomials of the
two point unions

```text
U_P(X)=product_(h in H,j_1 in J_1) (X-x([h*j_1]P)),
U_Q(X)=product_(h in H,j_2 in J_2) (X-x([h*j_2]Q)).
```

With the sign duplication removed, their gcd is the coordinate polynomial of the one
common `H` orbit. This proves that the set intersection can be represented exactly in
base-field polynomial algebra. It does not meet the cost gate:

- each union polynomial has degree `Theta(DK)`;
- the complete gcd has degree `Theta(D)`, so merely emitting it costs `D` words;
- materializing either union costs at least its `DK` output size;
- generic sampling from two size-`DK` sets with `D` matching points needs
  `DK/sqrt(D)=K*sqrt(D)=sqrt(ell)` samples for constant collision probability.

At `alpha=1/2`, union materialization has exponent `3/4`, the gcd output has exponent
`1/2`, and witness sampling has exponent `1/2`. Extracting only one common point
avoids the degree-`D` output but not the rho-scale collision search.

## Pole, probability, and recovery receipt

All affine-hash statements above are conditioned on the producer's pole-free setup.
An implementation would have to carry projective numerator/denominator data or emit an
aggregate bad-setup bit, resample, and charge the replay. Clearing denominators in
`R(t,s)` must preserve the denominator-zero branch; an unchecked sentinel is invalid.

On the admitted good branch:

1. the balanced batches have one true common H orbit;
2. false compressed cross equality has probability at most `K^2/p` per hash;
3. the derivative ratio returns its compressed label if the derivatives are supplied;
4. subdivision certificates must recover `j_1` and `j_2`;
5. an inner H search recovers the remaining multiplier; and
6. `[x]P=Q` verifies the final scalar.

The audited failure is at steps 3 and 4: no explicit derivative, norm, or subdivision
evaluator performs them with both base and challenge exponents below `1/2`.

## Complete route accounting

| Route | Time exponent at `alpha=1/2` | Peak-state exponent | Independent disposition |
|---|---:|---:|---|
| Explicit labels plus derivative witness | `1/2` | `1/4` if rows retained | Exact witness identity; row construction and pair arithmetic are rho |
| Single pair-grid elliptic product | at best credited `1/2` | no passing bound supplied | Required nested evaluator is absent; even the favorable term-count control is rho |
| Characteristic polynomial from slice labels | `1/2` | `1/4` | Degree-`K` output is admissible, but constructing its roots is rho |
| Split-algebra orbit coordinates | `1/2` or worse | `1/4` for one slice, `1/2` for the full invariant table | Diagonal entries are the missing labels |
| Split-algebra Fourier coordinates | at least dense-output `1/2` | at least dense-output `1/2` | Every mode is present; target orientation remains hidden |
| Subgroup/coset source bisection | `1/2` for the first informative structured test | no passing bound supplied | Membership orbit has `Theta(ell)` scalar terms |
| Union polynomial plus gcd | `3/4` | up to `3/4` | Exact but materializes degree `DK` unions |
| Union witness sampling | `1/2` | implementation-dependent | `D` common points conserve the rho collision cost |

For every explicit admitted route,

```text
lambda_C=max(c_C,b_C,(1-alpha)/2,alpha/2)=1/2
```

at its best balanced setting, or is larger. The hypothetical
`sqrt(KD)=ell^(3/8+o(1))` subset primitive remains a target only; none of the audited
representations constructs it. The promotion caps `c_C,b_C<=0.45` are therefore not
met. Memory can be kept below `0.30` only on some rho-time row-table routes; dense
coordinate and Fourier realizations fail the state cap as well.

## Route dispositions

| Route | Independent disposition |
|---|---|
| Full scalar resultant bit | Identically zero on every valid balanced challenge; no information |
| Deformed resultant derivatives | Exact common-root formula, but no sub-rho evaluator or localizer |
| Relative norm in orbit coordinates | Re-expresses the `K` independent H labels |
| Relative norm in Fourier coordinates | Dense modes or hidden character orientation |
| Nested square-root Velu | Invalid unit-cost composition for a high-degree H-invariant input |
| Direct structured subdivisions | First informative membership test is rho in the tested subgroup realization |
| Arbitrary interval subdivisions | No complete-action evaluator; singleton fallback is rho |
| Union polynomial gcd | Exact witness family with degree-`DK` materialization |
| High-multiplicity union collision | One-point recovery still costs `K*sqrt(D)=sqrt(ell)` generically |
| Universal elliptic Gauss sums | No challenge-oriented partial norm; orientation route already controlled |

## Full-path decision

P1533's interface is mathematically sound, and the derivative deformation gives an
exact witness-bearing direct resultant. No audited way to evaluate that witness and
localize its source has `c_C,b_C<1/2`. The independently audited disposition is

```text
INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__NO_SUBRHO_COLLISION_RESULTANT
```

P1533 is terminal `inconclusive` in this scope. Do not authorize a contract, solver,
or toy fixture from this result. The next theorem lane must use an operation that is
semantically distinct from ordered orbit rows, characteristic-polynomial roots,
relative norms in the split coordinate algebra, hidden-orientation Fourier or Gauss
modes, and union-set collision sampling. It must include a complete descent and cost
path before entering the focus queue.

This audit is not an ECDLP algorithm, a generic-order result, a Shoup-bound
improvement, or a breakthrough.
