# ECDLP-IDEA-046 — Shioda intersection-coordinate descent

## Status and claim labels

- Class: `representation`
- Risk band: `high_risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` theorem-first preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a surface, section, height, or valid
  specialization relation is not a break.

## Falsifiable hypothesis

For a declared generic family of ordinary prime-field ECDLP inputs, there is a
target-independent elliptic surface `S_(E,P) -> P^1_(F_p)` with a computable
specialization homomorphism

`sp_0: MW(S/F_p(t)) -> E(F_p)`

and a deterministic bounded-description lift `R -> S_R` for enough public
`R in <P>`. Shioda intersection coordinates of `S_R` permit a certified
factor-base decomposition in the Mordell--Weil lattice, whose specialization is a valid
relation on `E`. Relation collection, lattice-coordinate recovery, base-log solving,
target descent, ambiguity, construction, and bit memory all have exponents below
`1/2` in `N=#<P>=p^(1+o(1))`.

The lift is not assumed additive into a torsion-free group. Every useful equality must be
proved upstairs as a section identity and then pushed back by `sp_0`. The falsifiable
claim is that intersection data discovers enough such identities below rho, not that
elliptic surfaces or Shioda heights exist.

## Mechanism-new operation

Build one surface from `(E,P,N)`, freeze a good fiber identified with `E`, and
lift geometrically selected points and randomized known-scalar points to sections using
one public grammar. Compute each section's intersections with the zero section, fiber,
and resolved components. Use the resulting Shioda coordinate vector to recover an exact
short expression in a factor-base section lattice. Verify the equality as rational
sections before specializing it to an elliptic relation.

The proposed new operation is **intersection-coordinate recovery with an explicit
section-equality inverse witness and specialization back to the source curve**. It is not
a number-field point lift, a short Mordell--Weil relation guessed after favorable lifts,
a same-field isogeny, a toric transfer, a different lattice solver, or a relation-only
height certificate. If only numerical heights agree, if the surface depends on `Q`, or
if the section expression is not verified in `MW(S/F_p(t))`, the mechanism is invalid.

## Assumptions

1. `E/F_p` has a public prime subgroup `<P>` of order
   `N=p^(1+o(1))` and `Q=[x]P`.
2. A deterministic grammar constructs `S_(E,P)`, its minimal regular model, a declared
   good fiber at `t=0`, and the identification of that fiber with `E`.
3. The section-lift rule is defined from public point coordinates, not scalar labels,
   and its failures and height/degree growth are charged.
4. Singular fibers, component intersections, torsion sections, saturation indices, and
   the Shioda height pairing are computed exactly.
5. A recovered coordinate expression is accepted only after symbolic section equality
   and specialization on `E` both verify.
6. Factor-base selection and relation collection are target-independent; `Q` appears
   only during individual descent.
7. Any finite observation remains toy, heuristic, model-bound, and
   novelty-unverified.

## Semantic fingerprint

`fixed_elliptic_surface_over_Fp_t | public_point_to_section_lift | exact_Shioda_intersection_coordinates | verified_MW_section_decomposition | specialization_back_to_source_E`

The indispensable operation is exact coordinate recovery with a section-level inverse
witness. A lift without that witness merges into the global-lift obstruction; a
specialization relation found by an ordinary solver is only a control.

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — the closest representation boundary: a new model alone
   does not change ECDLP scaling.
2. `ledger/EV-REP-001.yaml` — supplies evidence that relation-preserving
   representation changes can leave the original search cost intact.
3. `ledger/EV-REP-002.yaml` — requires construction and inverse-map costs to remain
   visible when a representation appears compressed.
4. `ledger/RQ-REP-001.yaml` — asks for a representation that removes, rather than
   renames, the dominant obstruction.
5. `ledger/SYNTHESIS-20260716.md` — requires a complete factor-base, linear-algebra,
   individual-descent, and verification path against rho.

## Closest primary literature

- Shioda, [Mordell-Weil Lattices and Galois Representation.
  I](https://doi.org/10.3792/pjaa.65.268), develops the section-lattice and height
  framework used by the proposed coordinates.
- Silverman, [Heights and the Specialization Map for Families of Abelian
  Varieties](https://doi.org/10.1515/crll.1983.342.197), gives the nearby
  specialization/height boundary; it does not provide cheap lifts of arbitrary
  finite-field points.
- Tate, [Algorithm for Determining the Type of a Singular Fiber in an Elliptic
  Pencil](https://wstein.org/Tables/antwerp/tate/tate.pdf), is the primary
  computational boundary for the singular-fiber data that must be fully charged.

None of these sources gives a scalar-separating point-to-section lift with a sub-rho
inverse witness. This proximity check is not a novelty proof.

## Complete factor-base-to-target-descent path

1. Construct and minimize `S_(E,P) -> P^1`, resolve every singular fiber, and certify
   `sp_0` and the fiber identification `S_0 ~= E`.
2. Choose a deterministic target-independent elliptic factor base
   `F={F_1,...,F_B} subset <P>` of size `B=N^beta` by public point predicates;
   the logs of the `F_i` are initially unknown. Lift every `F_i` to `S_(F_i)`
   and retain failures.
3. For a frozen stream of known scalars `a`, form `R=[a]P`, lift `R`, and use
   exact Shioda coordinates to seek
   `S_R = sum_i e_i S_(F_i) + T`, where `T` is an explicitly enumerated torsion
   section. Verify the equality as rational sections.
4. Specialize the equality at `t=0` to certify
   `R=sum_i e_i F_i+sp_0(T)` on `E`. Collect every success, miss, coefficient,
   torsion adjustment, and dependency until at least `B` independent rows exist.
5. Solve the sparse system modulo `N` for `log_P(F_i)` and independently verify
   each recovered base logarithm on `E`.
6. Apply the same frozen lift and coordinate reducer to randomized target representatives
   `Q+[u]P` until a verified section decomposition is obtained. Substitute base logs
   and the public `u` to recover `x mod N`.
7. Accept only if `[x]P=Q` on the original curve; retain every failed or ambiguous
   target descent in the cost.

## Full rho/BSGS cost model

Let `B=N^(beta+o(1))`; surface construction/minimization cost
`N^(c+o(1))`; total singular-fiber and Neron--Severi setup cost
`N^(i+o(1))`; and stored surface/section state use `N^(s+o(1))` bits.
Let one complete point lift plus exact intersection-coordinate reduction cost
`N^(q+o(1))`. Let reciprocal relation and target-decomposition densities be
`N^(delta+o(1))` and `N^(delta_t+o(1))`. Let sparse base-log algebra have
time `N^(omega_s*beta+o(1))` and bit memory `N^(m_LA+o(1))`. Coefficient,
section-equality, and specialization verification costs are included in `q`.

- Pollard rho: `N^(1/2+o(1))` expected group operations with constant state.
- BSGS: `N^(1/2+o(1))` group operations and stored points.
- Surface setup: `T_setup=N^(max(c,i)+o(1))`.
- Factor-base lift: `T_FB=N^(beta+q+o(1))`.
- Complete relation collection:
  `T_rel=N^(beta+delta+q+o(1))` for all successes and misses needed for
  `Theta(B)` independent rows.
- Sparse linear algebra: `T_LA=N^(omega_s*beta+o(1))`.
- Individual descent: `T_desc=N^(delta_t+q+o(1))`.

Thus `lambda=max(c,i,beta+delta+q,omega_s*beta,delta_t+q)` and
`mu=max(s,beta,m_LA)`. Degrees in `t`, coefficient bit lengths, singular-fiber
output, saturation data, section expressions, and cached coordinates are part of these
exponents. Promotion requires `lambda<1/2` and `mu<1/2` against both rho and
BSGS.

## Likely fatal obstruction

A bounded-description elliptic surface is unlikely to contain cheaply constructible
sections specializing to a positive-density subset of a cryptographic prime subgroup.
Specialization can collapse high-height sections, so a lift of a generic finite-field
point may require degree or canonical height `N^(1/2-o(1))` or worse. Exact Shioda
coordinates locate a section only after the Mordell--Weil lattice and saturation are
known; constructing that lattice or solving the coordinate problem may be the original
DLP in another form. Matching numerical heights can also create false relations, while a
surface large enough to separate `N` specializations may have discriminant, rank, or
fiber output of order `N`.

## Proof track

Construct the surface and lift grammar uniformly, prove exact specialization, and bound
surface degree, singular fibers, section heights, lift density, coefficient size, and
Mordell--Weil saturation. Prove that the Shioda coordinate algorithm emits verified
section equalities at the claimed relation and target densities. Then prove all seven
descent steps and derive `lambda<1/2` and `mu<1/2`.

## Disproof track

Establish any one of: no fixed surface supports the required lift rule; lift density or
height forces `beta+delta+q>=1/2`; exact lattice construction or saturation costs
`N^(1/2-o(1))`; intersection vectors collide without section equality; every useful
relation is found only after a generic group search; or target descent lacks a verified
specialization witness.

## Positive and negative controls

- Positive geometry control: a rational elliptic surface with a fully known
  Mordell--Weil basis, exact Shioda matrix, and planted section decompositions.
- Positive specialization control: every symbolic section equality is checked in the
  function field and at every nonsingular toy fiber.
- Negative mechanism control: arbitrary interpolation sections through `R` with their
  full degree/height charged.
- Negative relation control: pairs of sections with equal height but unequal rational
  functions.
- Negative representation control: lift the same points to unrelated surfaces, where
  apparent short vectors must not be pooled.
- Leakage control: a section chosen using `log_P(R)` is an invalid oracle arm.

## Quantitative promotion and falsification gates

Before any scaling experiment, a theorem/preflight gate must produce one explicit public
surface and lift grammar with exact section-equality verification. The toy matrix then
uses every ordinary prime-order curve over primes `p<=251` supported by the grammar,
degree-at-most-four pencils, exhaustive known scalars, and blinded target labels.
Escalation requires:

- exact agreement of all fiber types, intersection numbers, Shioda pairings, section
  equalities, and specializations under independent implementations;
- lift applicability at least 25% on each of the two largest completed size strata;
- at least `B+8` independent verified relations and 100 verified target descents per
  largest-size curve family;
- zero accepted false section or source-curve relations;
- upper 95% bounds `lambda<=0.45` and `mu<=0.45` with height, degree,
  saturation, misses, and output charged;
- a statistically significant advantage over arbitrary-section interpolation and
  generic lattice-search controls.

Falsify this scoped claim if the theorem-first grammar cannot be defined, exact section
equality fails, lower 95% lift-density/cost bounds force `lambda>=0.50`, all
intersection profiles collide without valid decompositions, or the required
Neron--Severi/Mordell--Weil data reaches square-root scale. A timeout is not mathematical
evidence.

## Artifact plan

- Planned grammar: `ideas/artifacts/ECDLP-IDEA-046/surface_grammar.md`
- Planned symbolic derivation: `ideas/artifacts/ECDLP-IDEA-046/section_lift_derivation.sage`
- Planned theorem audit: `ideas/artifacts/ECDLP-IDEA-046/theorem_preflight.md`
- Planned manifests: `ideas/artifacts/ECDLP-IDEA-046/runs/<run-id>/manifest.yaml`
- Planned section data: `ideas/artifacts/ECDLP-IDEA-046/runs/<run-id>/sections.jsonl`
- Planned relation data: `ideas/artifacts/ECDLP-IDEA-046/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-046/analysis.md`
- Required retained data: exact models, resolutions, fiber types, section functions,
  intersection matrices, saturation proofs, every miss and ambiguity, resource metrics,
  commands, environment, seeds, commit, dirty-tree state, stdout, stderr, and checksums.

## Interpretation boundary

An elliptic surface, correct Shioda pairing, short section, or valid toy relation is not
an ECDLP breakthrough. Equality of heights is not equality of sections, and
specialization correctness is separate from performance. Only independently verified
end-to-end scalar recovery below rho/BSGS can justify escalation; it remains heuristic,
model-bound, toy-scoped, and novelty-unverified.

## Exactly one next executable action

1. Symbolically enumerate the frozen degree-at-most-four pencil grammar on the lexicographically first supported ordinary prime-order curve over each `p<=251` and either produce or disprove a target-independent point-to-section lift with exact section-equality and specialization witnesses.
