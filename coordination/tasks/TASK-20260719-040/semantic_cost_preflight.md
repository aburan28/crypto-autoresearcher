# TASK-20260719-040 independent semantic and cost preflight

## Record boundary

- Role: independent red team.
- Candidate roots: the weakest sufficient `P1553/Query2P1` decision interface
  under `ECDLP-IDEA-012`, and the stronger optional direct-decoder branch under
  `ECDLP-IDEA-133`.
- Source snapshot: validated `ECDLP-IDEA-001..409`, 409 records, canonical
  aggregate `b98794f4af83369e07b8ad7c09df442b84052c25564976d7f3df4b0f0eb122bf`.
- Independence: the original preflight did not read `TASK-20260719-039` or any
  artifact in its write scope. This scoped correction binds the independently
  reviewed P1553 R3 interface without importing a producer conclusion.
- Evidence: theorem and representation audit only. No experiment, solver,
  fixture, proposal, contract, or status transition was created.
- Decision:
  `NO_SURVIVOR_IN_THE_LITERAL_CUMMINGS_HAUENSTEIN_GRAMMAR__LOCAL_DUAL_REQUIRES_A_CENTRE__HOMOGENEOUS_MULTIGRADED_DUAL_GIVES_A_REAL_COEFFICIENT_TO_HILBERT_COMPONENT_RECURSION_BUT_NO_THEOREM_FIXED_SATURATED_REGULARITY_GRADE_FINITE_FIELD_RESTRICTION_STABLE_EXISTENCE_BIT_OR_COMPLETE_COST__NATURAL_FIVE_BLOCK_COMPONENT_HAS_B5_AMBIENT_COORDINATES__SPARSE_ADAPTIVE_EXCEPTION_PRESERVED`.
- Claim boundary: this is a scoped input/type and natural-representation result,
  not a lower bound for arbitrary sparse, black-box, multihomogeneous, or
  elliptic-specific algorithms.

All nine original owner files and all four IDEA-133 receipts matched the
SHA-256 bindings in the BATCH-008 prerequisite manifest. The corrected weak
interface is bound to
`ideas/artifacts/ECDLP-IDEA-012/p1553_query2p1_indexing_gate_r3.md`, SHA-256
`b2ee5934e295ab1f0d6b43452898e520d0cb18e718a8f5865694b25909b0df5e`:
an exact all-restriction existence bit plus charged `O(log B)` self-reduction
and singleton verification is sufficient. Counts, a distinguished functional,
multiplication operators, and a direct source reporter are stronger optional
interfaces.

## 1. What the multigraded-dual construction actually consumes and returns

The primary source is Cummings and Hauenstein,
[Multi-graded Macaulay Dual Spaces](https://arxiv.org/abs/2310.11587v1).
It exposes two interfaces which must not be conflated.

### 1.1 Affine local interface

For an ideal `I` and a supplied point `y`, Definition 2.9 forms

```text
D_y(I) = { differential evaluations centred at y that annihilate I }.
```

Its finite dimension is the multiplicity of the already selected isolated
point `y`. Proposition 2.11 recursively imposes generator annihilation and
closedness under the anti-differentiation maps. In the ECDLP application, a
centre containing the five factor coordinates and recursive-S3 intermediate
states is already a source tuple, or at least a supplied local component.
Computing its local multiplicity does not locate that centre.

Therefore the affine interface is an exact positive control for multiplicity
after a source is known. Enumerating centres restores the direct `B^5` source
deck; a `2+3` locator restores the existing `B^3` control.

### 1.2 Homogeneous multigraded interface

Theorem 3.2 concerns an `M`-graded ideal and the dual space at the homogeneous
origin `D_0(I)`. Its graded piece is the annihilator

```text
D_0^m(I) = (R_m / (I intersect R_m))^*.
```

The paper's `DualSpace` procedure consumes:

1. a homogeneous generating set for `I`;
2. the grading matrix `A`;
3. a half-space description of a saturated pointed weight cone;
4. a requested grade `m`.

It enumerates every grade `s <= m`, constructs a closedness subspace by
intersecting inverse images under the coordinate anti-differentiation maps,
and imposes generator evaluations as linear nullspace conditions. Its output
is a basis of a graded annihilator space. The paper explicitly leaves the
complexity of these computations for future work.

This output is not a distinguished relation-weighted functional `Lambda_R`.
A vector-space basis may be changed arbitrarily, and the source gives no
multiplication operators, point section, or reduced/nonreduced direct source
inverse. Those omissions are fatal only for the stronger IDEA-133 reporter
branch, not for the weakest P1553 interface.

Indeed, Proposition 3.4 identifies
`dim D_0^m(I)=H_(R/I)(m)`. For a saturated finite restricted-fiber ideal and a
grade in a proved uniform multigraded regularity region, that Hilbert value is
the scheme length. Its nonzero bit would therefore decide exact restricted
nonemptiness, including a nonreduced nonempty fiber, without selecting a
functional or decomposing points. The paper supplies no theorem-fixed such
grade, saturation-to-fiber biconditional, or restriction-uniform construction.
At an arbitrary or transient grade, a nonzero component can persist even when
the multiprojective source fiber is empty.

Theorem 4.8 obtains the dual of an ideal quotient by applying `Phi_g` to an
already computed higher-degree dual space. Its right inverse is a right
inverse to that linear operator. It can express a restriction after the
needed higher components exist, but it supplies neither a compact arbitrary-
dyadic update nor an exact target-fiber nonemptiness and cost theorem.

The article is stated over `C`. A divided-power or bounded-degree finite-field
port may be possible, but the cited paper proves neither the required
`F_p` exceptional-characteristic semantics nor base-field/bit complexity.

## 2. Exact natural five-colour grading dimension

Homogenize each size-`B` colour deck in its own projective block:

```text
R = k[X_1,Z_1,...,X_5,Z_5],
deg(X_i) = deg(Z_i) = e_i in Z^5,
F_i^h(X_i,Z_i) = product_(a in F_i) (X_i-a Z_i),
deg(F_i^h) = B e_i.
```

For `m=(m_1,...,m_5)`, the exact ambient component dimension is

```text
dim_k R_m = product_(i=1)^5 (m_i+1).
```

A single component in which all five degree-`B` deck equations can be imposed
has `m_i >= B` for every colour. At the first natural coupled grade,

```text
m=(B,B,B,B,B),
dim_k R_m = (B+1)^5 = Theta(B^5).
```

For the saturated positive-orthant grading, the grade interval sorted by the
literal procedure also has the exact cardinality

```text
|{s in Z^5 : 0 <= s_i <= B}| = (B+1)^5.
```

Thus the literal dense monomial realization exposes `Theta(B^5)` grade labels
and a terminal coefficient vector of `Theta(B^5)` entries before the
target-specific nullspace or nonemptiness decision. Optional multiplication-
algebra and direct-source stages can only add work. Extra recursive-S3 and
projective blocks and exceptional charts do not reduce this deck-only control.

This agrees in exponent with P1514's separate total-degree safe-cutoff control

```text
binomial(5B+2,5) = Theta(B^5),
```

but neither count is a compulsory cutoff for every construction. A target
fiber may have constant scheme length and a constant eventual Hilbert value.
An elliptic-specific theorem could conceivably reach that small quotient via
sparse bases, black-box nullspaces, early multigraded stabilization, or a
different grading without materializing the ambient component. The paper
supplies no such theorem, and this review does not rule one out.

## 3. Restrictions and source recovery

For a squarefree deck factorization `F_i^h=G_i H_i`, selecting the roots of
`G_i` can be expressed by the ideal quotient `(F_i^h):H_i=(G_i)` in the
one-block control. Theorem 4.8 can transport this restriction only from an
already constructed dual space of the required higher grade. It gives no
compact arbitrary-dyadic restriction update. Rebuilding after each bisection
or retaining all restriction duals must be charged.

P1553 does not require a direct point section. If every canonical restricted
ideal has an exact nonemptiness bit, deterministic positive-parent/negative-
child bisection over the five labelled decks uses `O(log B)` charged queries
to reach one singleton tuple, which direct group addition then verifies. The
entire query sequence, negative children, grade certification, saturation,
and singleton verification must fit the online cap.

For the stronger optional IDEA-133 branch, a reduced zero-dimensional fiber
would still need coordinate multiplication matrices and joint eigenspaces,
while exact nonreduced multiplicity would still need primary decomposition
and nilpotent local algebras. A local dual at a supplied centre remains only a
positive control after a source is known. These direct-decoder obligations
must not be imposed on a correct restriction-stable existence oracle.

## 4. Semantic ownership and controls

The weakest sufficient information flow is the existing P1553/Query2P1
residual under IDEA-012/P1513/P1551/P1516; it receives no new ID:

```text
compact signed and chart-complete restricted target ideal
  -> theorem-fixed saturated regularity grade
  -> exact finite-field bit: dim D_0^m(I) != 0
  -> O(log B) restriction self-reduction and singleton verification
  -> rows, factor logs, and unchanged masked descent.
```

IDEA-156 is the closest canonical information-flow control for conditional
nonvanishing and source self-reduction. IDEA-138 owns only the proof/transcript
wrapper after a decision oracle exists. The legacy P1551 artifact under
IDEA-195 is an endpoint-aggregation/source-unranking control; current canonical
IDEA-195's non-Cartesian S3 intertwiner is not this mechanism.

IDEA-133 remains the exact owner of the stronger optional path:

```text
compact target ideal
  -> source-blind nonlinear dual functional
  -> flat multiplication algebra
  -> exact reduced/nonreduced occurrence inverse.
```

The multigraded-dual route is therefore a proposed Query2P1 decision backend
and, only if extended to direct atomization, an IDEA-133 backend. Bound
adjacent controls are:

| Record | Exact overlap/control |
|---|---|
| P1553 / IDEA-012 | exact all-restriction nonemptiness plus charged bisection |
| IDEA-156 | stronger conditional-coefficient nonvanishing and self-reduction |
| IDEA-138 | search-to-decision after the exact conditional predicate exists |
| P1551 / IDEA-195 | endpoint aggregation and source-unranking control |
| IDEA-133 | optional faithful functional and direct algebraic source inverse |
| IDEA-053 | sparse decoding after an implicit moment oracle |
| IDEA-152 | multigraded source module plus missing canonical atomization |
| IDEA-259 | source atomization after a hidden moment tensor is supplied |
| IDEA-372 | Macaulay/syzygy backend without a quotient/source section |
| IDEA-373 | adaptive reconstruction after exact entry/fiber queries |
| IDEA-378 | target atlas after parametric ideal construction |
| IDEA-408 | family regularity without an exact restriction-stable bit |
| IDEA-409 | transform and inverse after the relation functional is supplied |

The exact positive controls are: `D_y(I)` at a supplied isolated point;
coefficient-derived graded Hilbert/annihilator computation from a supplied
homogeneous ideal;
Theorem 4.8 ideal-quotient transport from a supplied dual space; Laurent--
Mourrain flat extension from supplied moments; and multiplication/primary
decomposition after a faithful finite algebra is supplied. The homogeneous
component recursion is a genuine coefficient-derived arrow, but it becomes a
P1553 oracle only after the missing exact regularity, saturation, finite-field,
restriction-update, and cost theorem is proved.

## 5. Complete cost cases at `B=N^(1/5)`

Grant constant relation density, constant source output per successful target,
and full independent row gain; these are favorable model-bound assumptions.

| Route | Setup/state | One target | `B`-row campaign | Fresh masked target | Result |
|---|---:|---:|---:|---:|---|
| supplied centre/local dual | source supplied | local | source supplied | source supplied | circular constructor |
| supplied moments/dual algebra | omitted | decoder-only | omitted | omitted | positive backend only |
| literal natural multigraded dense route | `B^5` | `B^5` | `B^6` | `B^5` | `lambda>=6/5`, `mu>=1` |
| reusable `2+3` control | `B^3` | `B^2` | `B^3` | `B^2` | `lambda>=3/5`, `mu>=3/5` |
| streamed `2+3` control | `B^2` memory | `B^3` | `B^4` | `B^3` | `lambda>=4/5`; memory alone `>=2/5` |

The literal multigraded exponents charge only ambient/component traffic and
therefore favor the route; nullspace arithmetic, coefficient bits, saturation,
regularity certification, all restriction updates, and singleton verification
can add work. A stronger direct reporter additionally pays for multiplication
matrices, primary splitting, and source output. These costs are scoped to the
displayed representation. The charged `O(log B)` bisection does not change the
displayed exponents, but it is not free.

After verified five-sparse rows exist, grant sparse factor-log linear algebra
`B^(2+o(1))=N^(0.4+o(1))` time and `B^(1+o(1))` memory, plus independent log
verification. This is dominated in every explicit constructor case. No rank
theorem is supplied. The identical construction must be applied to fresh
`Q+[t]P`; known scalar labels may verify relation rows but cannot provide a
regularity grade, exact nonemptiness bit, or restriction result unavailable
for the scalar-blind masked target.

## 6. Fatal obstruction and preserved exception

The local Cummings--Hauenstein recursion remains circular as a locator because
it consumes a source centre. The homogeneous recursion is genuinely source-
blind, but the cited grammar does not give a theorem-fixed saturated
multigraded regularity grade whose nonzero component is biconditional with the
exact signed finite-deck fiber over `F_p`. It also gives no finite-field and
exceptional-characteristic port, compact arbitrary-dyadic restriction update,
or complete query/campaign complexity. In the literal natural five-block
realization, the first component seeing all five degree-`B` deck equations
already exposes `B^5` ambient coordinates.

No exact survivor is present. The preserved exception is a theorem-fixed
sparse/adaptive multigraded construction that derives an exact all-strata
restricted-nonemptiness bit directly from coefficients, never materializes the
natural component, and supports the full charged bisection sequence. A faithful
functional and direct source inverse are permitted stronger realizations, not
requirements. P1514's scope correction requires that this exception remain
open.

## Exactly one theorem obligation

Prove, for every signed and chart-complete canonical restriction of the
homogenized five-colour recursive-S3 ideal over `F_p`, one source-blind
coefficient-to-Hilbert theorem that specifies a theorem-fixed saturated
regularity grade and makes `dim D_0^m(I_R) != 0` biconditional with exact
restricted source existence; construct or update all components needed for the
charged `O(log B)` bisection and singleton verification with setup/state plus
the full verified-rank-`B` row campaign at most `B^(9/4+o(1))`, the total
restricted sequence for each relation or fresh `Q+[t]P` target at most
`B^(5/4+o(1))`, and charged factor logs and scalar verification. A faithful
functional and direct primary/nilpotent source inverse may instantiate this
obligation but are not required; otherwise classify the literal recursion as
the `Theta(B^5)` natural-component control.
