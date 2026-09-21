# ECDLP-IDEA-039 — Noether-Lefschetz Kummer relation lift

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` theorem-first preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Picard-rank jump, rational curve, or lifted incidence certificate is not a break.

## Falsifiable hypothesis

For a generic ordinary prime-field `E` and marked pair `(P,R)`, an explicit deformation
of the Kummer surface `Km(E x E)` admits a Picard-rank-jump fiber with an extra effective
divisor class. A target-independent obstruction-and-lifting procedure can carry a useful
marked incidence of that class back to the original Kummer surface. Pulling the lifted
curve to `E x E` and intersecting it with fixed factor-base slices yields verified
relations for `R`; enough relations and a separate descent for `Q` have total time and
bit-memory exponents below `1/2`.

The hypothesis does not treat special-fiber Picard rank as information by itself. The
extra class must lift with explicit equations or a certified formal/algebraic deformation,
retain nonconstant marked intersections, and return relation coefficients without using
the hidden scalar.

## Mechanism-new operation

Embed the relation problem in a Kummer-surface family, deliberately specialize to a
Noether-Lefschetz fiber where additional divisor classes can be constructed, and solve
the exact deformation obstruction for a selected class together with marked incidence
conditions. The proposed operation is **Picard-jump divisor construction followed by
marked class lifting and intersection descent**.

This is not a lift of point coordinates to search for short Mordell-Weil vectors, a toric
specialization, same-field isogeny, quaternion-module orientation, product-Kummer
addition-law rewrite, or relation-only support certificate. The special class is useful
only if its lifted intersection data algorithmically produces factor-base coefficients.

## Assumptions

1. `E/F_p` is ordinary with a known prime subgroup `<P>` of order `N=p^(1+o(1))`, and
   `Q=[x]P`; characteristics `2` and `3` are excluded in the first preflight.
2. `Km(E x E)`, its resolution of the sixteen nodes, the relevant Neron-Severi lattices,
   intersection forms, and pullback to `E x E` are computed exactly.
3. The deformation family, special-fiber selection rule, candidate divisor enumeration,
   and marked incidence conditions are target-independent during base-log collection.
4. A class counts as lifted only with an explicit equation or independently checkable
   formal deformation through the required order and an algebraization certificate.
5. Every intersection multiplicity, exceptional component, sign, field extension,
   coefficient height, failed class, and ambiguity is charged.
6. Toy behavior is heuristic and model-bound; all novelty and asymptotic claims remain
   novelty-unverified.

## Semantic fingerprint

`Kummer_surface_deformation | Noether_Lefschetz_Picard_jump | extra_effective_divisor | marked_obstruction_lifting | pullback_intersection_relation | factor_logs_and_separate_target_descent`

A special-fiber class that does not lift is a negative control. A lifted generic diagonal,
factor, node, or trope is a correctness control. If the only surviving action on `Pic^0(E)`
is a known scalar, or relation coefficients still require factor-base support search, the
proposal merges with existing correspondence or support controls.

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — excludes same-field isogeny-neighbor structure as the claimed
   source of easier relations.
2. `ledger/EV-ISO-001.yaml` — supplies the matched coefficient-variance control for special
   auxiliary geometry.
3. `ledger/H-REP-001.yaml` — requires a new mathematical operation rather than a Kummer
   coordinate or equation change.
4. `ledger/FINDING-PF-IC-001.md` — fixes the factor-base membership and end-to-end exponent
   obstruction that lifted incidences must remove.
5. `ledger/SYNTHESIS-20260716.md` — requires exact negative scope, full target descent, and
   rho/BSGS accounting.

## Closest primary literature

- Kuwata and Shioda, [Elliptic parameters and defining equations for elliptic fibrations on a Kummer surface](https://arxiv.org/abs/math/0609473), gives explicit Kummer-surface geometry and elliptic fibrations near the proposed construction.
- van Luijk, [K3 surfaces with Picard number one and infinitely many rational points](https://arxiv.org/abs/math/0506416), demonstrates exact specialization/Picard-rank methods that constrain any claimed lift.
- Bogomolov, Hassett, and Tschinkel, [Constructing rational curves on K3 surfaces](https://arxiv.org/abs/0907.3527), studies deformation and specialization of rational curves on K3 surfaces.

None gives a marked divisor-lifting decoder for prime-field ECDLP. These are nearby
primary boundaries, not evidence of novelty or feasibility.

## Complete factor-base-to-target-descent path

1. Freeze `(E,P,N)`, a one-parameter Kummer deformation, its original and Picard-jump
   fibers, exact lattice bases, the class-enumeration order, and marked-slice conventions.
2. Choose `B=N^beta` target-independent factor-base points `F_i` and their fixed horizontal,
   vertical, or graph slices on `E x E`; publish all pullback and quotient conventions.
3. For known `R=[a]P`, impose only the preregistered marked incidence conditions involving
   `(P,R)` and the fixed slices; enumerate candidate extra special-fiber classes in order.
4. Run the exact obstruction calculation. Accept only a class with a certified lift and an
   explicit pulled-back curve whose complete intersection cycle gives
   `c_R R + sum_i e_i F_i + c_P P=O`, with known nonzero `c_R mod N`.
5. Independently verify the intersection cycle and the projected group relation on `E`;
   collect enough independent rows to solve all required factor-base logs.
6. Freeze the family, accepted class rule, and base logs. Apply the identical construction
   to `(P,Q+[t]P)` for preregistered randomizers `t`, retaining every failed lift and class.
7. Divide by `c_R`, substitute base logs, remove `t`, enumerate all sign/exceptional
   ambiguities, recover `x`, and accept only if `[x]P=Q`.

## Full rho/BSGS cost model

Let factor-base size be `B=N^beta`; surface/family setup `N^(s+o(1))`; Neron-Severi,
equation-degree, field-extension, and coefficient-height charge `N^(nu+h+o(1))`; one
candidate obstruction/lift/intersection attempt `N^(kappa+o(1))`; reciprocal useful-lift
density `N^(delta+o(1))`; target parameters `kappa_t,delta_t`; and verification exponent
`v`.

- Pollard rho: `T_rho=N^(1/2+o(1))` and `N^o(1)` state bits.
- BSGS: `T_BSGS=N^(1/2+o(1))` and `M_BSGS=N^(1/2+o(1))` stored-point bits.
- Family and lattice setup: `T_setup=N^(max(s,nu+h)+o(1))`.
- Relation collection: `T_rel=N^(beta+delta+kappa+o(1))`, including every special class
  rejected by obstruction or incidence checks.
- Sparse linear algebra: `T_LA=N^(2*beta+o(1))`, `M_LA=N^(beta+o(1))` bits.
- Target descent: `T_desc=N^(delta_t+kappa_t+o(1))`.
- Independent equation, intersection, and group verification: `N^(v+o(1))`.
- Total bit memory is `M=N^(max(beta,nu,h,m_eq,m_class)+o(1))` bits, including all
  polynomial coefficients, lattice matrices, class panels, and caches.

The complete time exponent is
`lambda=max(s,nu+h,beta+delta+kappa,2*beta,delta_t+kappa_t,v)`; memory exponent is
`m=max(beta,nu,h,m_eq,m_class)`. Both upper confidence bounds must be below `1/2` to beat
rho and BSGS. A free special-fiber oracle is never included in the promoted arm.

## Likely fatal obstruction

Picard rank is upper-semicontinuous under specialization: the useful extra divisor is
expected to exist only on the jump fiber and fail the first obstruction to lifting. On a
generic non-CM `E x E`, surviving correspondences are generated by factors and the
diagonal and act by known scalars on `Pic^0(E)`. Forcing an extra class to lift together
with marked order-`N` incidence may require level-`N` degree or coefficient height, or may
reinsert the original support/DLP problem. Thus a lattice/deformation theorem may close
the lane before relation experiments.

## Proof track

Exhibit a uniform family, an extra effective class, and an obstruction calculation that
proves a non-generic marked lift with bounded degree and height. Derive the exact
intersection-to-group relation and prove useful-lift density, relation rank, separate
target descent, and `lambda,m<1/2` without target-selected specialization.

## Disproof track

Show that every non-generic class fails first-order lifting, that every liftable class lies
in the generic factor/diagonal lattice and induces only a known scalar correspondence, or
that marked lifting has degree/height or reciprocal density exponent at least `1/2`.
Failure of a software backend is not such a proof.

## Positive and negative controls

- Positive lift controls: factor, diagonal, node, and trope classes known to persist in
  the frozen family must pass every equation, lattice, and intersection verifier.
- Positive extra-class control: a planted CM Kummer family with a known extra endomorphism
  checks detection and lifting without counting its special-family DLP as a generic win.
- Negative class control: an extra class certified to exist only on the jump fiber must be
  rejected by the lift gate.
- Incidence control: random marked points and matched random divisor classes measure
  accidental intersections.
- Scalar-correspondence control: remove every relation generated by factors, diagonal,
  negation, or known endomorphisms before rank and cost estimates.
- Oracle control: supplying a lifted equation tests downstream intersection plumbing only
  and cannot promote the construction mechanism.

## Quantitative promotion and falsification gates

The frozen theorem-first preflight is specified in
`ideas/contracts/ECDLP-EXP-CONTRACT-039_noether_lefschetz_kummer_preflight.yaml`. It uses a
deterministic finite toy curve panel, exact first- and second-order obstruction checks,
known-lift and known-nonlift controls, and no experiment before coordinator approval.
Promotion only to a larger study requires zero verifier failures, detection of every
control class, rejection of every certified nonlift, at least one non-generic class with
an explicit independently verified lift on at least three unrelated ordinary curves, at
least 100 scalar-blind useful relations total, no known-scalar explanation, and upper
bounds `nu+h<=0.20`, `lambda<=0.45`, `m<=0.45`.

Falsify the frozen scope if the exact obstruction rejects every non-generic class, every
survivor lies in the known generic lattice, any accepted lifted equation or intersection
fails verification, or the lower full-cost bound is `lambda>=0.50`. Correctness of a
control or a Picard jump alone is non-promotion evidence.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-039_noether_lefschetz_kummer_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-039/kummer_lift_preflight.sage`
- Planned class panel: `ideas/artifacts/ECDLP-IDEA-039/class_panel.json`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-039/runs/<run-id>/`
- Planned obstruction traces: `ideas/artifacts/ECDLP-IDEA-039/runs/<run-id>/obstructions.jsonl`
- Planned intersection certificates: `ideas/artifacts/ECDLP-IDEA-039/runs/<run-id>/intersections.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-039/analysis.md`
- Retain equations, lattice bases, discriminants, class coordinates, deformation orders,
  all failures, costs, peak bit memory, commands, seeds, environment, stdout, stderr, and checksums.

## Interpretation boundary

All assertions remain toy, heuristic, model-bound, and novelty-unverified. Special Picard
rank, a rational curve, a correct lifted control, a valid intersection relation, or toy
factor-log recovery does not establish a breakthrough. Promotion requires a non-oracle
mechanism-new lift and complete base-to-target recovery below rho/BSGS, followed by
independent review and replication.

## Exactly one next executable action

1. After coordinator approval, execute the frozen theorem-first class-lifting preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-039_noether_lefschetz_kummer_preflight.yaml` without running any target-recovery arm unless the non-generic lift gate passes.
