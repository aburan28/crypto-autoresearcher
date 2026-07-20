# ECDLP-IDEA-005 — Height-compressing global lift

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a finite-field relation that reduces correctly is not a break.

## Falsifiable hypothesis

There is a deterministic global lift of a generic `E/F_p`, a factor base, and randomized
targets to a curve over a number field such that useful lifted divisor/Mordell–Weil
relations have coefficient and logarithmic-height exponent `h<1/2`, occur at sufficient
density, and can be recovered and descended with total time and memory exponents below
`1/2` in the prime subgroup order.

The new prediction is a uniform **height-compression theorem and algorithm**. Replacing
LLL, changing an arbitrary lift, or observing a toy short vector is not the mechanism.

## Mechanism-new operation

Choose a canonical global model and coupled point-lift rule whose denominator ideals share
controlled support, turning finite-field point relations into provably short global
relations. Recover those relations by ideal/height factorization and lattice reduction,
then reduce them back modulo the original prime. The claimed operation is the coupled
height compression that the known Xedni-style route lacks.

## Assumptions

1. `E(F_p)` contains `<P>` of prime order `N=ell=p^(1+o(1))` and `Q=[x]P`.
2. The global curve, reduction prime, and lifts of points are deterministic and computable
   without knowing their discrete logarithms.
3. Reduction maps every accepted global relation to the claimed finite-field relation;
   spurious reduction collisions are detected.
4. The number-field degree, discriminant, coefficient sizes, denominators, and unit/class
   group work are included in the height and cost exponents.
5. Lattice success is measured over all preregistered instances, not selected short vectors.
6. Toy-to-crypto extrapolation is heuristic and model-bound.

## Semantic fingerprint

`canonical_global_curve_and_point_lift | shared_denominator_ideal_support | sub_sqrt_height_relations | reduction_back_to_E | removes_xedni_coefficient_growth`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field relation-cost obstruction to be bypassed.
2. `ledger/H-FB-001.yaml` — prevents ordinary small-coordinate bases from being relabeled as height compression.
3. `ledger/EV-FB-001.yaml` — supplies the uniform-yield control.
4. `ledger/H-REP-001.yaml` — distinguishes a cross-characteristic lift from a coordinate-model swap.
5. `ledger/SYNTHESIS-20260716.md` — supplies scaling and target-descent requirements.

## Closest primary literature

- Jacobson, Koblitz, Silverman, Stein, and Teske, [Analysis of the Xedni calculus attack](https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf), gives the closest negative height/coefficient analysis.
- Lauter and Stange, [ECDLP and equivalent hard problems for elliptic divisibility sequences](https://arxiv.org/abs/0803.0728), blocks a mere EDS renaming.
- Borger and Gurney, [Canonical lifts of families of elliptic curves](https://arxiv.org/abs/1608.05912), provides canonical-lift geometry but not global point-relation compression.
- Bisson and Sutherland, [Computing the endomorphism ring of an ordinary elliptic curve](https://arxiv.org/abs/0902.4670), is nearby computational CM/lift infrastructure.

The checked works do not establish the coupled sub-square-root height property. Absence in
this search is not a novelty proof; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze a global model `E_tilde/K`, a prime over `p`, and a deterministic lift rule for
   curve points, including failure and ambiguity semantics.
2. Select a finite-field factor base `F={F_j}` of size `B=N^beta`; lift each point and build
   the shared denominator/ideal factor base with checksums.
3. For random known scalars `a`, set `R=[a]P`, lift `R`, and construct the global relation
   lattice from coordinates, denominator ideals, and local height constraints. Keep `Q`
   out of the base-log phase.
4. Recover a short candidate relation, verify it over `K`, reduce it modulo the original
   prime, and accept only if it yields `R=sum e_j F_j` on `E/F_p`.
5. Collect `B+margin` independent rows and solve for finite-field factor-base logarithms.
6. Apply the same lift/lattice to randomized `Q+[t]P`, descend it over the solved base,
   recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Let `B=N^beta`; global model/base construction cost `N^c`; relation-lattice cost per trial
`N^kappa`; reciprocal success density `N^delta`; coefficient/height bound `N^h`;
individual descent `N^tau`; bit memory `N^s`, including coefficient and ideal encodings;
and **total charged bit-operation exponent**
`chi` for number-field degree, discriminant, coefficient, denominator, ideal, unit/class-
group, and precision arithmetic. `chi` is measured independently rather than inferred
from the symbolic height label.

- Pollard rho: `N^(1/2+o(1))` time, constant memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Lift/base construction: `N^(c+o(1))`.
- Relation collection: `N^(beta+kappa+delta+o(1))`.
- Sparse finite-field linear algebra: `N^(2*beta+o(1))` time, `N^(beta+o(1))` memory.
- Individual descent: `N^(tau+o(1))`.
- Integer/number-field arithmetic is reported as `N^(chi+o(1))` total bit operations,
  with operand lengths and operation counts retained separately; it may not be folded
  into an unnamed polynomial-time term.

The full time exponent is
`lambda=max(c,beta+kappa+delta,2*beta,tau,chi)` and memory is
`mu=max(s,beta)`. A relation of height `N^h` with `h>=1/2`, or a lift table of that size,
cannot support a sub-rho claim.

## Likely fatal obstruction

There is no canonical lift of arbitrary finite-field points that preserves their unknown
group relation as a short Mordell–Weil relation. Reduction collapses many high-height
global points, and coefficient/denominator growth in the known Xedni analysis cancels the
apparent information. The number field or its discriminant may also grow with `p`. A short
vector found after choosing favorable lifts is selection bias, not a mechanism.

## Proof track

Prove the lift rule is target-independent, bound number-field degree/discriminant and
relation heights by `N^(h+o(1))` with `h<1/2`, lower-bound usable-relation density, and
derive an end-to-end descent with `lambda<1/2`.

## Disproof track

Prove any relation-preserving lift has coefficient, denominator, field-degree, or lattice
dimension exponent at least `1/2`; demonstrate lift dependence; or show recovered global
relations reduce to tautologies that do not determine factor-base logs.

## Positive and negative controls

- Positive control: a planted global curve and rational points with deliberately short
  integral relations before reduction.
- Positive instrumentation control: exhaustive toy reduction verifies every accepted relation.
- Negative control: arbitrary coefficient lifts and the published Xedni-style construction.
- Negative statistical control: random lattices with identical dimension/determinant/height.
- Leakage control: permute toy logs before lift construction and audit every dependency.

## Quantitative promotion and falsification gates

Use primes of 12–40 bits, at least 100 curves per size, `beta in {0.10,0.15,0.20}`, and
three independent global models/lift controls. Promotion requires:

- zero incorrect global or reduced relations;
- a height-slope upper 95% bound `h<=0.35` at the two largest sizes;
- at least one preregistered configuration with `kappa+delta<=0.20`, `tau<=0.45`,
  `c<=0.20`, `chi<=0.45`, and upper 95% `lambda<=0.45`;
- relation-matrix rank at least `0.98*B` before oversampling;
- upper 95% memory exponent `mu<=0.45` including number-field tables.

Falsify the scoped prediction if the height-slope lower 95% bound is `>=0.50`, accepted
relations depend on arbitrary lift choices, matrices remain rank deficient, or every
complete-cost fit has lower 95% `lambda>=0.50`. Number-field construction failure is not
negative mathematical evidence.

## Artifact plan

- Planned specification: `ideas/artifacts/ECDLP-IDEA-005/preflight_spec.yaml`
- Planned lift catalog: `ideas/artifacts/ECDLP-IDEA-005/global_lifts.jsonl`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-005/height_lift_preflight.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-005/runs/<run-id>/`
- Planned raw lattices: `ideas/artifacts/ECDLP-IDEA-005/runs/<run-id>/lattice/`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-005/analysis.md`

## Interpretation boundary

This hypothesis is toy, heuristic, model-bound, high-risk, and novelty-unverified. A short
toy vector or a relation that reduces correctly is not a speedup. Promotion requires a
uniform height bound, complete relation system, target descent, full cost below rho/BSGS,
and independent replication.

## Exactly one next executable action

1. Implement the deterministic lift-rule comparison and measure coefficient, denominator, field-degree, and shortest-relation height slopes on the preregistered 12–24-bit matrix.
