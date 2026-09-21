# ECDLP-IDEA-002 — Split-Jacobian projected smoothness

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a cover or valid conorm relation is not a break.

## Falsifiable hypothesis

There exists a bounded-degree cover `pi:C->E` over `F_p`, with `J(C)` isogenous to
`E x A`, for which divisor classes in the conorm image of the cryptographic subgroup have
an asymptotically higher **E-projected smoothness** over a split-prime divisor base than
matched random classes in `J(C)`. The gain is large enough that relation collection,
projection, sparse linear algebra, and individual descent all have exponent below `1/2`
in `N=ell≈p`.

The prediction is not that a split Jacobian exists. It is that the conorm image has a
constructible, target-compatible smooth-divisor distribution whose complete projected
descent is sub-rho.

## Mechanism-new operation

Use conorm to move `E(F_p)[ell]` into a higher-dimensional Jacobian, reduce conorm-image
classes to divisors supported on places whose pushforwards land in a small E-factor base,
and project relations back with the norm. The new operation is **projected-smoothness
compression on the E isogeny factor**. This differs from walking to another same-field
elliptic curve and testing the same PDP.

## Assumptions

1. `E(F_p)` has prime subgroup `<P>` of order `N=ell=p^(1+o(1))`.
2. The cover degree `d` is coprime to `ell`, so `pi_* pi^*=[d]` is invertible on the target subgroup.
3. Equations for `C`, conorm, norm, divisor reduction, and the `E x A` projector are explicit
   in time charged by the model. Every failed target-independent cover-family attempt is
   retained, and reciprocal admissible-cover density is charged rather than conditioned away.
4. A deterministic divisor atom base of size `B=N^beta` maps to a known E-factor base and
   supports verifiable decompositions.
5. Smoothness samples are generated before observing success and censored runs are retained.
6. Extrapolation from fixed-genus toy curves is heuristic and model-bound.

## Semantic fingerprint

`bounded_degree_cover_conorm | E_subgroup_to_split_Jacobian | projected_smooth_divisor_atoms | norm_back_to_E | removes_prime_field_factor_base_membership_cost`

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — closest object-level comparison, but it tests E-to-E neighbors
   rather than a cover/Jacobian conorm and projection.
2. `ledger/EV-ISO-001.yaml` — establishes the coefficient-variance control required here.
3. `ledger/FINDING-PF-IC-001.md` — states the factor-base/relation obstruction this
   representation must actually remove.
4. `ledger/H-FB-001.yaml` — prevents ordinary split-point selection from being called new.
5. `ledger/SYNTHESIS-20260716.md` — requires matched controls, scaling, and explicit rho cost.

## Closest primary literature

- Shaska, [Curves of genus 2 with elliptic subcovers](https://arxiv.org/abs/math/0312285), develops split-Jacobian/elliptic-subcover geometry.
- Gaudry, [Index calculus for abelian varieties](https://doi.org/10.1016/j.jsc.2008.08.005), gives the nearby full-abelian-variety index-calculus framework.
- Diem, [Computing discrete logarithms with special linear systems](https://www.math.uni-leipzig.de/~diem/preprints/small-degree-exact.pdf), quantifies curve/Jacobian factor-base costs.
- Gaudry, Hess, and Smart, [Constructive and Destructive Facets of Weil Descent](https://doi.org/10.1007/s00145-001-0011-x), is the closest established curve-transfer attack family.

These works make “use a cover” known. The proposed projected-smoothness distribution on a
generic prime-field E factor was not established in the checked sources; novelty remains
unverified.

## Complete factor-base-to-target-descent path

1. Construct `pi:C->E`, explicit conorm `i=pi^*`, norm `n=pi_*`, and an isogeny projector
   onto the E factor; verify `n(i(R))=[d]R` on all toy points.
2. Choose divisor atoms `D_j` on `C` whose norms `F_j=n(D_j)` form a deterministic E-factor
   base of size `B`; record fibers and all multiplicities.
3. For random known scalars `a`, set `R=[a]P`, lift `i(R)`, add preregistered
   kernel/A-factor dithers only when their later projection is exactly known, and reduce
   the class. No target point enters this base-log collection phase.
4. Accept only verified decompositions `i(R)=sum_j e_j D_j+K` with a certified projected-zero
   `K`; apply `n` to obtain `[d]R=sum_j e_j F_j` in `E`.
5. Collect `B+margin` independent projected rows and solve for `log_P(F_j)`.
6. Lift and decompose randomized representatives `Q+[t]P` using the identical frozen base;
   apply norm, substitute factor-base logs, and multiply by `d^(-1) mod ell`.
7. Recover `x mod ell` and verify `[x]P=Q` on E, independently of the Jacobian code.

## Full rho/BSGS cost model

Let one cover construction/projector attempt cost `N^c`, reciprocal admissible-cover
density be `N^zeta`, base size `B=N^beta`; per-trial divisor
reduction/factor test `N^r`; reciprocal projected-smoothness probability `N^delta`;
individual-descent cost `N^tau`; and stored divisor data using `N^s` bits, including
extension coordinates and coefficient sizes.

- Pollard rho: `N^(1/2+o(1))` group operations, constant memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Cover/base construction: `N^(c+zeta+o(1))` across the frozen target-independent family.
  For a fixed input with no admissible cover, the method is inapplicable; it may not
  replace the target curve and call that search an attack.
- Projected relation collection: `N^(beta+delta+r+o(1))`.
- Sparse linear algebra on `B` unknowns: `N^(2*beta+o(1))` time and `N^(beta+o(1))` memory.
- Individual target descent: `N^(tau+o(1))`, including branch search, norm, and verification.

The total time exponent is
`lambda=max(c+zeta, beta+delta+r, 2*beta, tau)` and memory exponent
`mu=max(s,beta)`. For comparison, unconditioned fixed-genus Jacobian index calculus has
cost at least `p^(2-2/g)` for genus `g>=2` in the nearby model, already worse than
`p^1/2`; only a measured projected-smoothness collapse can change that conclusion.

## Likely fatal obstruction

The conorm image is an elliptic isogeny factor, so its reduced divisors may be no smoother
than random classes subject to that factor. Generic factor-base relations then solve a
full Jacobian problem, and projection does not reduce the number of atoms or the descent
cost. Fixed-degree covers yield only constants; growing degree raises genus and destroys
the cost. Existence of `C`, a split `J(C)`, or valid norm identities alone is therefore
irrelevant to promotion.

## Proof track

Prove an explicit family of covers, an applicability-density bound, and a lower bound on projected smoothness for conorm
classes, including a constructive witness algorithm. Prove that kernel/A-factor dithers
project to zero and derive an end-to-end `lambda<1/2` bound.

## Disproof track

Show the projected smoothness exponent matches random-Jacobian or random-E controls;
show atom norms span `Theta(N)` unknowns; show individual descent costs `N^(1/2-o(1))`;
or prove any useful cover family needs genus/degree growing enough that `lambda>=1/2`.

## Positive and negative controls

- Positive control: a deliberately split small-genus Jacobian with planted low-degree
  divisor decompositions and an explicit E projection.
- Positive instrumentation control: exhaustive toy verification of conorm, norm, kernel,
  and every accepted divisor equality.
- Negative control: same-genus random curves/Jacobians with matched factor-base size.
- Negative mechanism control: the ledger's small E-to-E isogeny neighbors evaluated under
  the same projected metric.
- Null projection control: use divisor atoms with the same smoothness but random E images;
  this must not pass the logarithm/descent gate.

## Quantitative promotion and falsification gates

The preflight uses ordinary curves at `p` bit sizes `11,13,15,17,19`, at least 30 base
curves per size, every constructible cover of preregistered degrees `2,3,4`, and matched
random-Jacobian controls. Promotion requires all of:

- exhaustive conorm/norm correctness with zero unexplained kernel terms;
- a projected-smoothness exponent advantage of at least `0.20` over controls, with a 95%
  confidence interval excluding zero at every two largest sizes;
- a preregistered `beta<=0.20` with upper 95% bounds `delta+r<=0.20`, `tau<=0.45`,
  `c+zeta<=0.20`, and hence `lambda<=0.45`;
- at least 100 independently verified target descents at the two largest toy sizes;
- `mu<=0.45` after storing all cover and divisor tables.

Falsify the scoped prediction if conorm is noninjective on the tested prime subgroup,
projected relations do not determine E-factor-base logs, the advantage slope is at most
`0.05`, or the lower 95% full-cost bound is `lambda>=0.50`. Construction failures are
infrastructure/coverage results, not mathematical negatives.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-002_split_jacobian_projection_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-002/split_cover_preflight.sage`
- Planned cover catalog: `ideas/artifacts/ECDLP-IDEA-002/covers.jsonl`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-002/runs/<run-id>/`
- Planned raw relations: `ideas/artifacts/ECDLP-IDEA-002/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-002/analysis.md`

## Interpretation boundary

All preflight evidence is toy, heuristic, and model-bound. A split Jacobian, a correct
conorm, or a valid projected relation is not an attack. Promotion requires a complete
factor-base-to-target descent whose measured, uncertainty-bounded exponent beats rho and
BSGS; crypto-scale claims require independent replication.

## Exactly one next executable action

1. After coordinator approval, execute the frozen cover-construction and projected-smoothness matrix in `ideas/contracts/ECDLP-EXP-CONTRACT-002_split_jacobian_projection_preflight.yaml`.
