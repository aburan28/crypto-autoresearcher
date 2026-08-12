# Nested source-level norm preflight v1

## Handoff: exact root norm over registered sources

### Claim or task

Instantiate an exact source-level nested norm for
`D2^fin intersect (Q-D3)` using three registered signed source variables, without
constructing distinct D3 or `c_Q mod M_D2`.

### Status

- `RESTRICTED THEOREM`, independently reviewed `GO` for exact norm semantics,
  identity coverage, multiplicity handling, and child factorization.
- `NEGATIVE RESULT`, `MODEL-BOUND`, independently reviewed `GO` for explicitly expanded
  CRT/Sylvester/Macaulay resultants, direct ordered-triple product circuits, and
  standard black-box determinant/Krylov interfaces over the source tensor
  algebra.
- Overall candidate: `REVISE`, `REVIEW_REQUIRED`. A scalar-only transposed
  resultant and compact selector remain open but are not instantiated.

No implementation, experiment, or child operator is authorized.

### Assumptions

- `K=F_p(omega)` is the registered quadratic encoding field.
- Signed source branches are split so each accepted source root has one oriented
  affine point; multiple public identifiers may decorate that point.
- For signed branch `b_i`, `M_i(T_i)=M_(b_i)(T_i)` is monic and squarefree with
  degree `d_i`; the constant branch family has total degree `Theta(B)`.
- Each `M_i` splits over `K` as the product of `T-t` over exactly its registered
  distinct source roots. Monic and squarefree without this split-root condition
  is insufficient for the product-algebra semantics.
- The collision-light balanced specialization has `d_i=Theta(B)` and root node
  degree `n_I=deg(M_I)<=N2=Theta(B^2)`.
- The number of source-branch triples and typed addition patterns is constant in
  `B`.

### Evidence so far

#### Signed source algebras

For each branch define

```text
A_i=K[T_i]/(M_i),             dim_K(A_i)=d_i.
```

Accepted roots are non-poles, so the rational x-coordinate defines

```text
X_i=N_i(T_i)*D_i(T_i)^-1 in A_i.
```

Let `Y_i` be the unique CRT interpolation of the registered oriented
y-coordinate at every source root. It obeys the curve equation in `A_i`. A
source residue supporting both orientations must be split into signed branches;
the curve equation alone would admit unregistered orientations.

The three-source algebra is

```text
A_123=A_1 tensor_K A_2 tensor_K A_3
     isomorphic to product_(r1,r2,r3) K,
dim_K(A_123)=d_1*d_2*d_3.
```

Its components are ordered registered source triples, including repetitions.

#### Exact branch-complete value

On each component compute `S=P_1+P_2+P_3` using the registered exact branch
cover: ordinary, doubling, inverse pair, and intermediate left identity. Then
translate by `Q`, covering `Q=O`, `S=O`, `S=Q`, `S=-Q`, and ordinary `Q-S`.

For one typed component `pi` with finite output, write

```text
enc(Q-S)=A_(pi,Q)/Delta_(pi,Q),
```

where the registered denominator is a unit on that selected component. Define

```text
G_(pi,I,Q)=Delta_(pi,Q)^n_I
           *M_I(A_(pi,Q)/Delta_(pi,Q)).
```

It vanishes exactly when the finite translated point is in node `I`. When
`Q-S=O`, define `G_(pi,I,Q)=1`, since `M_I` contains only finite D2 roots.
Branch idempotents in the split algebra give the exact semantic element

```text
G_(I,Q)=sum_pi e_pi*G_(pi,I,Q) in A_123.
```

Materializing the idempotents or this element is not free. Constant-many explicit
`e_pi`, or global units `e_pi*Delta+(1-e_pi)`, each allocate
`d_1*d_2*d_3=Theta(B^3)` K-coordinates. Stored explicitly, they fail Tier B's
strict `o(B^3)` advice cap; regenerated explicitly, they incur `Theta(B^3)`
work, traffic, or preprocessing workspace. Tier A charges their aggregate
canonical bytes against its exact cap. An executable global circuit cannot
invert a denominator merely because it is a unit on one selected component: it
must construct and charge such a global unit, or remain fraction-free. Compact
selector circuits or complete projective formulas remain possible and are not
ruled out by this explicit-idempotent census.

#### Exact norm and full support

For one signed branch triple `b`, define

```text
R_(I,b)(Q)=Norm_(A_123/K)(G_(I,Q))
          =product_(r1,r2,r3) G_(I,Q)(r1,r2,r3).
```

Across all ordered signed branch triples in the constant branch family,

```text
R_I(Q)=product_b R_(I,b)(Q).
```

Then `R_I(Q)=0` exactly when an ordered registered source triple has finite
`Q-S` equal to a finite D2 point in `I`. If `S=O` and `Q` is finite, its factor
is `M_I(enc(Q))`, so the D3-identity route is included without a D3 sentinel.

The remaining D2-identity route is needed when `o_2` is present. Evaluate it at
the root with the exact charged terminal scan

```text
Member_D3(Q) = OR_(P in signed factors) D2Contains(Q-P)
Hit_root(Q)  iff R_root(Q)=0 or (o_2 and Member_D3(Q)).
```

Charge `Theta(B)` group subtractions, dictionary probes, record reads, bytes,
sign/identity/repetition handling, and independent replay. The same successful
probe returns one signed factor and the stored D2 pair witness, so it both decides
membership and supplies the D3 witness. Every finite child node uses only
`R_I(Q)=0`; otherwise the D2 identity, which belongs to no child, would make
every child spuriously positive.

Ordered-triple multiplicity cannot create or remove a zero. Repeated leaves are
included; duplicate public decorations are expanded after algebraic recovery.

#### Concrete elimination order

Use `T_3`, then `T_2`, then `T_1`. Let `Ghat_(I,Q)` be the unique representative
of `G_(I,Q)` with degree `<d_i` in every source variable. The exact nested norms
are

```text
H_(12,Q) = Res_(T_3)(M_3,Ghat_(I,Q)) mod (M_1,M_2)
         = Norm_(A_123/A_12)(G_(I,Q)) in A_12,

H_(1,Q)  = Res_(T_2)(M_2,H_(12,Q)) mod M_1 in A_1,

R_(I,b)(Q)=Res_(T_1)(M_1,H_(1,Q)) in K,
```

where `A_12=A_1 tensor A_2`. The identities are exact over these product
coefficient rings because the source polynomials are monic and the resultant is
the determinant of multiplication. Division-based fast resultant algorithms
still require proof that every attempted pivot is a unit.

#### Degree and module census

At a collision-light root, `d_i=Theta(B)` and `n_I=Theta(B^2)`. The degree
bounds below are branchwise after fixing one typed translation branch; they do
not include construction of target-dependent selectors distinguishing `S=Q`,
`S=-Q`, and ordinary translation.

| Stage | Coefficient module | Dense target coefficients | Branchwise target-degree upper bound |
|---|---:|---:|---:|
| `G_(I,Q)` | `A_123` | `Theta(B^3)` | `O(n_I)=O(B^2)` |
| `H_(12,Q)` | `A_12` | `Theta(B^2)` | `O(d_3*n_I)=O(B^3)` |
| `H_(1,Q)` | `A_1` | `Theta(B)` | `O(d_2*d_3*n_I)=O(B^4)` |
| final scalar | `K` | `1` | `O(d_1*d_2*d_3*n_I)=O(B^5)` |

```text
selector degree:       UNDEFINED, REVIEW_REQUIRED
selector work:         UNDEFINED, REVIEW_REQUIRED
selector target state: UNDEFINED, REVIEW_REQUIRED
```

A field-indicator selector may have field-size degree. Compact selector circuits
or complete projective addition formulas remain a separate positive obligation.

Reduction bounds each source degree by `d_i`. The frozen dense power-basis
representation allocates every quotient coordinate; it does not prove that each
specific element has full nonzero support. In that representation, the first
norm hits the registered root boundary:

```text
H_(12,Q) in A_12,       dim_K(A_12)=d_1*d_2=Theta(B^2).
```

Every sequential one-variable-at-a-time elimination order that explicitly emits
its penultimate quotient element has an analogous two-source module.
Simultaneous block elimination, reordered D2/source norms, structured tensor
contraction, and scalar-only transposition remain outside this statement.

#### Dense resultant census

After reducing in `T_3`, the first Sylvester matrix is `Theta(B)` square over
`A_12`. Under the frozen dense/worst-case storage census, it has:

- `Theta(B^2)` nonzero block positions;
- `Theta(B)` unique target-dependent `Ghat` coefficients, each containing
  `Theta(B^2)` K-coordinates;
- `Theta(B^3)` unique explicit target coefficients;
- up to `Theta(B^4)` flattened occurrences if shifted blocks are expanded;
- a `Theta(B^2)`-coefficient target output `H_(12,Q)`.

The second Sylvester matrix is `Theta(B)` square over `A_1`, with up to
`Theta(B^3)` flattened occurrences. The final scalar matrix is `Theta(B)`
square over `K`, with `Theta(B^2)` scalar nonzeros. A full quotient-
multiplication determinant acts on `A_123`, giving a `Theta(B^3)` square matrix
and up to `Theta(B^6)` entries.

Thus explicitly expanded CRT, dense Sylvester/Macaulay, or coefficient-output
nested-resultant interfaces fail the root gate before runtime constants matter.
The counts are allocated slots or worst-case nonzeros, not lower bounds on the
actual support of every EC-derived element.

#### Direct and standard black-box routes

A direct pointwise product can retain an `O(1)` accumulator, but performs
`Theta(B^3)` tuple translations. Naive evaluation of degree-`Theta(B^2)` `M_I`
at every output costs `Theta(B^5)` field operations. Explicit fast multipoint
evaluation can approach `soft-O(B^3)` arithmetic only by consuming the full
`Theta(B^3)` multiplicity-expanded translated-point stream.

Standard determinant or Krylov methods do not fix the interface:

- multiplication by `G` uses vectors in `A_123`, with `Theta(B^3)`
  K-coordinates;
- a nested black-box determinant uses `Theta(B)` entries in `A_12`, again
  totaling `Theta(B^3)` K-coordinates;
- componentwise first-norm evaluation emits one result for each source pair,
  namely `Theta(B^2)` target outputs.

These standard product-circuit and black-box interfaces are `REJECTED_SCOPED`.
A different scalar-only arithmetic-circuit resultant that emits no `A_12`
element and uses no `A_123`-sized vector is not disproved.

Exact gate mapping for the frozen interfaces:

| Interface | Charged obstruction | Gate failure |
|---|---:|---|
| Materialized dense `G_(I,Q)` | `Theta(B^3)` target slots and traffic | target-live, online work, and traffic |
| Sequential dense `H_(12,Q)` | `Theta(B^2)` target output; streaming retains `Theta(B^2)` traffic/work | strict `o(B^2)` target/work/traffic |
| Direct or explicit multipoint tuple route | `Theta(B^3)` tuple processing | online work and traffic, not necessarily live state |
| Standard explicit black-box/Krylov route | `Theta(B^3)` vector coordinates | workspace/live-state and traffic |
| Explicit selector/global-unit route | `Theta(B^3)` stored or regenerated coordinates | strict Tier B advice, workspace, work, or traffic |
| Root sentinel and terminal scan | `Theta(B)` work and `O(1)` live state | fits Tier B; not an obstruction |

#### Child factorization and witnesses

For `I=I_L disjoint-union I_R`, denominator clearing gives componentwise

```text
G_(I,Q)=G_(I_L,Q)*G_(I_R,Q),
```

so norm multiplicativity gives

```text
R_I(Q)=R_(I_L)(Q)*R_(I_R)(Q).
```

This is an exact hereditary semantic law. A parent implementation that outputs
only the product does not reveal which child vanishes. The frozen dense and
tuple-stream realizations repeat their root-sized obstruction at the first
split, where both child degrees remain `Theta(B^2)`. A different scalar circuit
may compute and retain both child scalars internally with constant output state;
that route is not ruled out and must disclose its internal boundaries.

After a hypothetical descent returns D2 point `R`, set `S=Q-R`, scan all `B`
signed factors `P`, and probe `S-P` in the charged D2 dictionary. This
`Theta(B)` exact terminal lift returns three signed identifiers; combining them
with the pair witness gives five identifiers and independent replay.

### Narrow scoped conclusion

The source-level norm is an exact scalar formulation and removes distinct-D3
deduplication from the semantics. It does not yet remove D3-scale or D2-scale
interfaces from known algorithms:

- dense sequential resultants emit `Theta(B^2)` target coefficients at their
  first norm;
- direct ordered-triple circuits process `Theta(B^3)` tuples;
- standard black-box determinant vectors contain `Theta(B^3)` coordinates.

These interfaces fail the zero-run gate. No lower bound follows for a scalar-
only transposed resultant, source-composition tower, target-parametric circuit,
or other algorithm whose internal vector spaces and boundaries are genuinely
sub-`B^2`.

### Failure modes

- Calling the final scalar compact while hiding `H_(12,Q)`, a triple branch
  mask, or a black-box vector.
- Treating an ordered-triple stream as removal of D3 traffic because it is not
  deduplicated.
- Applying field-only division algorithms over `A_12` without unit proofs.
- Treating ambient tensor dimension as a lower bound on a structured or
  separable scalar circuit.
- Allowing the curve equation to choose unregistered orientations.
- Losing inverse, identity, doubling, or target-exception branches.
- Claiming parent scalar factorization supplies a child decision.
- Returning zero without the charged terminal lift.

### Next concrete action

Specify a scalar-only transposed norm algorithm by listing every vector space,
oracle interface, and target boundary. Reject it immediately if any has
`Omega(B^2)` target-dependent coordinates; otherwise prove child-modulus
substitution and certificate cost before implementation.

### Artifact paths

- `candidate-review-v1.md`
- `root-operator-preflight-v1.md`
- `../EXP-ECDLP-GENROOT-CIRCUIT-001/theory.md`
- `contract.md`
- `object-dimension-ledger.md`
