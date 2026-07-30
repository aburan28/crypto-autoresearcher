# TASK-20260723-203 independent stage-zero review

## Review boundary and provenance

This is a zero-compute review of non-operational academic mathematics. It
does not design or execute key-recovery software, use a standardized
cryptographic curve, target a real key or deployed system, or provide
operational cryptanalytic instructions.

The reviewed producer artifacts are the immutable `TASK-20260723-201`
snapshot archived by `TASK-20260723-202` at commit
`c5e1975c48a1b4489c9177e7c2d17a34873ca50a`, with parent
`91d42e9222abaee777440c1684da6d29bbf598c6`. The BATCH-002 task card records
post-commit verification at
`09c75692ed390e186c3c4590a81a177b48fff38a`. The receipt file itself is the
provisional `pending_post_commit` form, but the verified task card binds the
producer paths to SHA-256 values
`3a6b059d73fd902098342fb611ef36da4a5cd5496cd19c21e3eb126b7b4eb606`
and
`247d2aeb890fd64acd5027eb401a6198aa9a9fedb8f43abaa434a40de8370c74`;
the files reviewed at HEAD match them.

## Independent scores

| Requirement | Score | Independent reason |
|---|---|---|
| 1. Exact `r_R`/`z_R` definition and support proof | PASS | The occurrence-labelled objects, injective cubic-extension point key, component resultants, interpolant, and monic gcd are defined. The resultant product formula and squarefree label polynomial prove the exact fifth-label support biconditional. |
| 2. Explicit compact fresh-target update identity or recurrence | FAIL | The displayed point translation is exact but applies separately to `Theta(B^3)` target-dependent leaves. Whole-divisor translation and direct `r_R` updates are unexpanded payload macros, not compact recurrences. |
| 3. Dimensions and target dependence | PASS | The explicit semantic route and failed update attempt are dimensioned: `m=Theta(B)`, pair families of size `Theta(B^2)`, translated components of size `Theta(B^3)`, outputs of size `O(B)`, and streamed live state of size `Theta(B^2)`. No compact state exists to dimension. |
| 4. Generic-encoding erasure and a non-generic operation | FAIL | The only explicit update survives erasure as ordinary pointwise group translation. Coordinate reads, field branches, inversions, and `kappa` occur only in the expensive represented route; they are not a non-generic witness for a compact recurrence. |
| 5. Initial time and live-memory recurrences without forbidden payload | FAIL | The honestly charged route takes `B^(3+o(1))` online work and `B^(2+o(1))` live state, exceeding both `B^(5/4+o(1))` online caps. Smaller recurrences begin only after supplying a forbidden coefficient, resultant, factor, source, or scalar. |

The producer's first-failure ordering is correct: requirement 1 passes, and
requirement 2 is the first failure. The overall producer verdict
`NO_ADMISSIBLE_CONSTRUCTION` is confirmed for this snapshot.

## Requirement 1: exact semantics — PASS

For each fifth occurrence `a`, the sheet defines

```text
rho_(R,a) = Res_U(H_12(U), H_34^(R,a)(U))
```

over the cubic extension `K`, interpolates these values at distinct labels
`t_a` to obtain `r_R`, and takes

```text
z_R = monic-gcd(g_I, r_R).
```

The key `kappa([x:y:1])=x+theta*y`, with `kappa(O)=theta^2`, is injective
because `1, theta, theta^2` form an `F_p` basis of `K`. The resultant product
is zero exactly when some pair endpoint equals `R-A_a-v_e`, and the
squarefree `g_I` converts those zero evaluations into the exact set of
extendible fifth-occurrence labels. Repeated pair endpoints only repeat
factors and do not alter support. The intrinsic elliptic-curve group law
covers identity, infinity, tangent, vertical, repeated-point, and order-two
cases.

One wording correction is needed. `admission_report.yaml` says the companion
sheet defines “complete group-law component polynomials,” but the sheet uses
the intrinsic everywhere-defined group operation instead. That operation is
enough for the semantic proof, so the score remains PASS. A future
coordinate-level constructor could not treat unspecified complete formulas or
branch handling as free input.

This score certifies only the support definition. `z_R` does not encode row
multiplicity or the other four source labels, and defining it through
resultants does not construct those resultants.

## Requirement 2: compact update — FAIL

The only fresh-target identity is

```text
q_(a,e)(R+Delta) = q_(a,e)(R) + Delta.
```

It is mathematically exact, but there are
`m*n_34=Theta(B^3)` such leaves. Writing
`D_(R+Delta)=tau_Delta(D_R)` does not reduce their representation or update
cost; it declares translation of an entire represented divisor as one
operation. Likewise, an update of `r_R` that starts from translated
coefficients or component resultants begins after the construction obligation
has already been supplied.

The observation that `kappa` is not a group homomorphism correctly rules out
the simplest scalar polynomial shift. It does not rule out all nonlinear or
rational aggregate transforms. The valid conclusion is therefore that this
snapshot exhibits none, not that none can exist.

The cheapest decisive control is symbolic: require a typed compact state
`sigma_R`, an update equation `sigma_(R+Delta)=F(sigma_R,Delta)`, and an exact
output map to `z_(R+Delta)`. Expand every gate in `F` that consumes a divisor,
coefficient vector, resultant, common factor, successful source, or scalar.
The current sheet has no such recurrence, so no larger theorem audit or toy
run is warranted.

## Requirement 3: dimensions — PASS

Within the explicit route actually presented, the dimensional ledger is
coherent:

- fifth-label count `m=Theta(B)`;
- each pair-occurrence family has `n_12,n_34=Theta(B^2)` entries;
- a represented `H_12` has `Theta(B^2)` extension-field coefficients and is
  target independent;
- the translated family across all fifth labels has
  `m*n_34=Theta(B^3)` target-dependent point/key entries;
- represented `r_R mod g_I` and `z_R` have `O(B)` coefficients; and
- component streaming avoids `B^3` simultaneous storage but retains a
  degree-`Theta(B^2)` translated polynomial, hence `B^(2+o(1))` live state.

This is a pass “as an audit,” not evidence for a compact representation. The
sheet cannot dimension a compact constructor state because it presents none.
Exact replay would add restricted constructor calls and remains deferred after
requirement 2 fails.

## Requirement 4: generic erasure — FAIL

Replace concrete point coordinates and key values by random encodings, while
retaining only group operation and equality. The leaf update still typechecks:
each encoded point is translated by the encoded `Delta`. It remains an
ordinary generic group operation repeated over `Theta(B^3)` leaves.

The standard represented route does name non-generic work: reading
coordinates, evaluating finite-field branch masks and inversions, and forming
the key `kappa`. Those operations disappear under erasure, but in the
presented route they are applied only after exposing the full translated
component family. They do not identify a coordinate-sensitive compact
aggregate update.

The BATCH-001 record gives the generic preprocessing control

```text
S*T^2 = Omega_tilde(N).
```

At `N=B^5`, `S=B^(9/4)` and `T=B^(5/4)` would give
`S*T^2=B^(19/4)<B^5`. This control applies only if the claimed constructor is
generic-group simulable. It is not a lower bound against an unclassified
coordinate-sensitive representation. Here it reinforces the admission
failure because the only explicit update remains generic and no compact
non-generic witness exists.

## Requirement 5: resource recurrences — FAIL

Let `n=Theta(B^2)` and let fast polynomial operations cost
`n^(1+o(1))`. For each of `m=Theta(B)` fifth labels, constructing the
translated root polynomial and taking the represented resultant gives

```text
Q(m,n) = m*n^(1+o(1)) = B^(3+o(1)).
```

Streaming one component gives peak target-dependent live state

```text
W(m,n) = Theta(n^(1+o(1)) + m) = B^(2+o(1)).
```

These are honest recurrences and do not hide a supplied payload, but they miss
the required `B^(5/4+o(1))` fresh-target time and workspace caps by polynomial
factors. The final gcd is quasi-linear only once `r_R mod g_I` has already
been supplied, so it is an extraction control rather than the missing
constructor.

## Baselines and complete-path objections

For `N=B^5`, Pollard rho remains the correct generic work baseline at
`B^(5/2+o(1))=N^(1/2+o(1))`, with small serial memory or a distinguished-point
tradeoff. Baby-step/giant-step has the same square-root work exponent and
`B^(5/2+o(1))` memory. The reviewed component route is not an admitted
algorithm: its per-target `B^3` work is already worse than the square-root
exponent, while its claimed purpose was a `B^(5/4)` query inside a larger
conditional campaign.

The closest checked specialized control is source-reporting five-sum, or
six-list indexing when known targets form a sixth list. Explicit splits have
state/query pairs `(B^2,B^3)`, `(B^3,B^2)`, and `(B^4,B)`. The first fits the
`B^(9/4)` retained-state cap but misses the query cap; the latter two exceed
the setup cap. The BATCH-001 indexed controls also miss the desired rectangle
by polynomial factors. These are comparisons with known positive routes, not
lower bounds on every nonlinear finite-field representation.

Even a future exact support constructor would leave source recovery, target
hit probability, independent relation rank, factor-log completion, and
scalar-blind target descent unproved. Exact `z_R` gives fifth-label support
only. These downstream obligations should not consume review or experiment
capacity until a compact constructor passes stage zero.

## Verdict and next action

`NO_ADMISSIBLE_CONSTRUCTION` is independently confirmed, with requirement 2
failing first. The snapshot supplies an exact semantic support object and an
honest dimensional/cost audit of a standard represented route, but it supplies
no compact fresh-target recurrence, no compact candidate-specific
non-generic operation, and no recurrence inside the online rectangle. This is
a scoped negative about the reviewed constructor material, not an
impossibility theorem, ECDLP result, or claim about cryptographic hardness.
The one next action is to archive this review through `TASK-20260723-204` and
rerank the remaining academic directions without opening a full theorem audit
or toy run for this sheet.
