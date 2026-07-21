# P1553 relation-divisor product gate red-team notes

## Terminal verdict

```text
REVISE__REDUCED_RELATION_DIVISOR_INEQUALITY_SURVIVES_FOR_ONE_GLOBAL_SECTION__
GLOBAL_SCALAR_WORDING_INVALID_ON_PROJECTIVE_DECK_SPACE__B5_COORDINATE_WEIGHT_IS_
SECTION_OR_POLE_DEGREE_NOT_CIRCUIT_SIZE__FINITE_DECK_RATIONAL_REPORTER_FAMILY_
FALSE_POSITIVE_AND_SUCCINCT_NORM_INTERFACES_REMAIN_OPEN__OPERATION_LEVEL_MERGE_
WITH_P1512_P1513_P1551_P1539__NO_UNRESTRICTED_LOWER_BOUND__NO_RUN
```

The proposed gate contains a valid geometric lemma, but it does not provide the
claimed computational obstruction. It should be revised, not passed as written
and not failed as wholly invalid.

## Hash-bound review envelope

The exact canonical task card has SHA-256
`22861be0e8eacf0db8fbac1d26dd5dbb54b079f301ac6971ba7ad21bb1e46f13`.
The complete read scope was bound as follows.

| Input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `agents/red-team.md` | `7ae9372d518fba2b9868eccf1d99102cde1ac6dae2d7bb593971d264314893f5` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_determinant_value_channel_gate_v1.md` | `29464dc899b312a27b16828527e58f1fdef8d5f5e38cc4a660dcee9315b8e6bb` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_six_list_incidence_model_gate.md` | `ca79b115a952ac610d8ec18a18e3efd9aeef4c283d79f4d0c293012507136f57` |
| `ideas/artifacts/ECDLP-IDEA-115/ulrich_source_gate.md` | `7b76a37f27cb137d7ef31d95a235984eda0f266171ef8ded6c6680538704202c` |
| `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md` | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/artifacts/ECDLP-IDEA-012/p1539_r1_independent_audit.md` | `634e5a7d2847e849a2e46178f31500f19109e9a9d88a2bf8c70d1f0afe4d467a` |
| `ledger/FINDING-PF-IC-001.md` | `0848e85698683c2f2edf12e2896527f3dba31a3a678efc664a65a68763136681` |
| `focus/current_plan.json` | `64e02060b8a5b6362b9a1504cc338d775f3f57467a8290161e7b91eb9720fd0a` |

No experiment, solver, fixture, timing run, relation campaign, or IDEA-133
verifier was executed.

## 1. Exact universal configuration model

Let

```text
X=E^(6B)
```

with labelled coordinates `A_(i,j)`, where `1<=i<=6` is the deck colour and
`1<=j<=B` is the location in that deck. Let `U` be P1553's checked open stratum
on which admitted actual points are pairwise disjoint. For

```text
alpha=(j_1,...,j_6) in [B]^6,
```

define

```text
mu_alpha:X->E,
mu_alpha(A)=sum_(i=1)^6 A_(i,j_i),
R_alpha=mu_alpha^(-1)(O).
```

The coefficient vector of `mu_alpha` is primitive and contains coefficients
equal to one. Extending it to an integral unimodular matrix gives an
automorphism of `E^(6B)` under which `mu_alpha` is a coordinate projection.
Consequently

```text
R_alpha ~= E^(6B-1)
```

is smooth, irreducible, and Cartier. Distinct labelled tuples give distinct
divisors. No `R_alpha` is contained in the deleted diagonal boundary, so
`R_alpha intersect U` is a dense irreducible open subset.

This closes the irreducibility attack in the universal geometric model.

## 2. What the divisor theorem actually proves

Let `s` be a nonzero global section of a line bundle `L` on `X`. Assume only
the no-false-negative property

```text
R_alpha intersect U subset Z(s) for every alpha.
```

At the generic point of each prime Cartier divisor, regularity gives

```text
ord_(R_alpha)(s)>=1.
```

Taking closures from `U` to `X` yields

```text
div(s) >= sum_(alpha in [B]^6) R_alpha.          (1)
```

Equation (1), rather than literal polynomial divisibility, is the correct
meaning of carrying the reduced product divisor. The reporter may have higher
multiplicity and extra boundary zeros.

Fix one labelled coordinate `A_(i,j)` and all other coordinates generically,
then vary only `A_(i,j)`. This gives a coordinate fibre `C~=E`. A relation
divisor meets `C` with degree one exactly when its tuple uses `(i,j)`. There
are one choice in that colour and `B` choices in each of the other five:

```text
sum_alpha (R_alpha . C)=B^5.                    (2)
```

Therefore

```text
deg(L|C)>=B^5                                   (3)
```

for every labelled deck-point coordinate.

Equations (1)-(3) are exact. They are the narrow statement that survives.

## 3. The scalar wording is not coherent globally

The compact configuration space `X=E^(6B)` is projective and connected. Every
global regular scalar function `X->A^1` is constant. A nontrivial determinant
reporter is instead a section of a positive line bundle. Local row frames turn
that section into scalar formulae, but changing a frame multiplies those
formulae by units and does not create a canonical global scalar.

For the full product, rescaling one labelled row frame multiplies every tuple
factor containing that row. The exponent is exactly `B^5`. This confirms the
coordinate weight while also showing why line-bundle data cannot be omitted.
Frames with zeros or poles add their own divisor terms.

Verdict on gauge: the divisor is invariant; the scalar wording and apparent
numerator are not.

## 4. Localization and rational reporters

Removing diagonals does not make the `R_alpha` reducible or identify distinct
components. It does change the regular-function question. A function regular
on `U` may extend to a rational function

```text
f=g/h
```

on `X`, with poles on `X-U`. If `f` has no false negatives, then its positive
divisor still contains every `R_alpha`. On a generic coordinate fibre,
principal-divisor degree zero gives

```text
degree of zeros >= B^5,
degree of poles >= B^5.                          (4)
```

Thus a rational reporter does not erase divisor traffic; it transfers the
line-bundle class to a denominator or boundary-pole ledger. But (4) says
nothing about arithmetic-circuit size. A high pole order can itself be encoded
by repeated powers. A denominator that merely avoids the finite evaluated deck
points, while having poles elsewhere inside geometric `U`, is not a globally
regular reporter on `U`.

Verdict on localization/rationality: the geometric statement survives only as
zero-pole degree accounting, and the circuit exception remains open.

## 5. Finite decks defeat the geometric inference

The P1553 algorithm receives fixed public finite decks. After specialization,
the deck coordinates are constants and there is no universal deck-parameter
divisor left to divide a reporter. Moreover, equality on the finite set of
`F_p`-rational configurations does not imply geometric vanishing on
`R_alpha` over the algebraic closure. Frobenius equations, Fermat masks, and
interpolation can agree on finite points without supplying the universal
section in Section 2.

The divisor theorem therefore applies only when the producer supplies one
uniform algebraic section over a geometric family, with coefficient and frame
construction independent of the hidden relation. It does not close:

- a reporter specialized to one fixed deck instance;
- a reporter exact only on `F_p` points;
- a special low-dimensional deck family on which relation divisors coalesce;
- target-fitted advice; or
- a finite-domain circuit whose semantics are pointwise.

Those interfaces return to P1551. Their advice, coefficient construction,
source-diagonal aggregation, and exact source output remain charged.

## 6. Reporter families and target specialization

The `B^5` conclusion is for one reporter over all six `B`-point decks. It does
not hold member-by-member for a family.

For a finite OR-family `{s_a}`, exact coverage means

```text
union_alpha R_alpha subset union_a Z(s_a).
```

Because each `R_alpha` is irreducible, it lies in at least one member's zero
divisor. The total covered degree across the family is therefore at least
`B^5` in every coordinate, but that degree may be distributed among many
members. One determinant per tuple is the extreme control: every member has
constant individual degree and the family has `B^6` members.

A target-specialized reporter gives a sharper mutation. Fix the sixth target
point and multiply only over the five factor lists. It has `B^5` tuple factors,
but a fixed factor-deck point occurs in only

```text
B^4
```

of them. Running such a reporter on `B` known targets restores `B^5` aggregate
campaign weight, while one fresh target sees only the `B^4` member. This does
not produce a fast algorithm, but it disproves any memberwise `B^5` assertion
for reporter families.

Adaptive, randomized, prefix-conditioned, and target-specialized families
must state their decision rule, component coverage, number of members, advice,
coefficient build, query schedule, and exact signed source replay. The
single-section lemma supplies none of those costs.

## 7. False positives do not have one answer

If one global reporter has no false negatives but also vanishes on extra
components, equation (1) still applies. Exact verification removes false
positives only after candidates are returned; it cannot remove the relation
components from the reporter's divisor.

Different behavior is possible when a family covers only subsets of relation
components, uses a nonvanishing score to propose candidates, or is randomized.
Then no individual reporter is a union reporter. Completeness moves to the
family or transcript and must be proved there. The charged interface includes:

```text
total false-positive blocks and source rows;
recursive reporter queries;
exact tuple unranking;
complete elliptic verification;
campaign work <= B^(9/4);
fresh-target work <= B^(5/4).
```

Verification is not a free conversion from a one-sided checksum to a locator.

## 8. Section degree is not circuit complexity

This is the fatal computational objection. A degree lower bound gives no
useful arithmetic-circuit size lower bound. With bounded-degree leaves and
binary multiplication it gives only a logarithmic depth observation:

```text
multiplicative depth >= log_2(B^5)=O(log B).
```

The exact finite-field mutation is

```text
z -> z^(p-1).
```

It vanishes exactly when `z=0`, has degree `p-1=Theta(B^5)`, and is evaluated
from a supplied `z` by `O(log p)` repeated-squaring multiplications. It does
not aggregate hidden tuples or return a source, but it decisively separates
degree from circuit size.

Likewise, a norm or resultant can carry a large product divisor while
remaining succinct as syntax. Expanding its coefficients or executing it in
the currently represented quotient may cost `B^3` or `B^4`; that is the P1513
and P1551 standard-route evidence. The divisor degree does not prove every
specialized product circuit must pay those costs.

The missing charged stages remain:

```text
coefficient construction;
circuit size and intermediate state;
denominator and chart handling;
source-index diagonal aggregation;
exact count or nonempty output without cancellation;
exact signed source unranking;
the separate fresh-target recurrence.
```

## 9. Operation-level semantic comparison

### P1512

P1512 already uses Cartier degree and determinant-line multiplicity to charge
a source-labelled scalar-linear Chow/Tate atomizer. Its lower bound becomes a
matrix-size statement only because every source is required to appear as an
independent kernel or cokernel atom and entry degree is charged. The present
union reporter returns at most one bit and has no independent source atoms.
Its divisor lemma is the same degree-accounting operation without P1512's
matrix/source interface.

### P1513

The full relation-divisor product is a product/norm of the determinant
predicate over the split source domain. Standard product, resultant, gcd, and
common-norm representations are exactly P1513's operation class. Its V3 scope
correction leaves specialized elliptic product circuits and global all-strata
source construction open. The divisor degree does not close them.

### P1551

Finite-field repeated squaring and Fermat equality masks are P1551's pointwise
predicate. They are short circuits but do not aggregate or unrank the hidden
source coordinate. A finite-deck version of the proposed reporter therefore
returns to the pointwise-versus-aggregation boundary, not to a geometric
circuit lower bound.

### P1539

Each individual relation divisor is compiled by P1539's singular evaluation
minor. Multiplying all such predicates adds an OR/product layer but no row
locator. The product gate does not change the coloured five/six-sum source
problem.

### Classification

The universal divisor inequality is a clean exact bookkeeping lemma, but as a
research operation it is a semantic merge with P1512's Cartier degree and
P1513's product/norm, with P1539 supplying factors and P1551 supplying the
finite-domain circuit correction. It is not new evidence that closes P1553's
determinant-value exception.

## 10. Baseline and complete-path consequence

At `B=N^(1/5)`:

```text
Pollard rho                      B^(5/2)=N^0.50
P1553 setup/state/campaign cap   B^(9/4)=N^0.45
P1553 one-target query cap       B^(5/4)=N^0.25
section coordinate weight       B^5=N
```

No valid implication turns the final line into time or memory. The current
explicit product/norm/source controls still expose `B^3` or `B^4` traffic and
miss the P1553 rectangle, but that conclusion comes from P1513/P1551's typed
representations, not from section degree. Succinct norm circuits, rational
reporters, finite-deck circuits, and reporter families remain exceptions with
the explicit interfaces above.

Even a passing zero/nonempty reporter would still lack relation rank,
factor-base logarithms, exact signed source rows, the identical scalar-blind
masked-target recurrence, output accounting, bit complexity, and a complete
`lambda,mu<=0.45` proof.

## Narrowest supported statement

On the universal labelled six-deck configuration space, one nonzero global
algebraic section with no false negatives on P1553's checked disjoint stratum
has zero divisor at least the reduced sum of all `B^6` tuple-relation divisors.
Its line bundle has degree at least `B^5` in each labelled deck-point
coordinate. A rational reporter pays the same amount as pole degree on a
compactification.

This is not a finite-deck, reporter-family, arithmetic-circuit, source-recovery,
incidence, cell-probe, ECDLP, or Shoup lower bound.

## Exactly one next action

Preserve P1553's determinant-value residual. Before the divisor gate is used in
any claim, require a versioned reporter interface that states section versus
rational versus finite-domain versus family semantics and either derives a
charged circuit-size consequence from the `B^5` divisor weight or records the
lemma as a P1512/P1513 semantic control. Allocate no P1554 and execute no
experiment or verifier.
