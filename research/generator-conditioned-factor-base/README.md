# Generator-conditioned factor bases: proposed ECDLP experiments (2026-10-19)

**Status:** research proposal and executable toy control; not an approved frozen protocol, not an attack claim. Coordinator approval required before promotion to canonical experiment ledger.

## Question
Can joint selection of generator P and a coordinate-restricted factor base F enforce an algebraic property of the Semaev relation system that persists for *arbitrary unknown* Q=[x]P, reducing total relation-finding cost?

## Hypotheses
- **H1 (planted relation):** selecting P=A+B+C with A,B,C in F guarantees f4(x_A,x_B,x_C,x_P)=0. This is a construction identity, not evidence of ECDLP speedup.
- **H2 (persistent algebraic reduction):** a selected P causes a measurable reduction in elimination complexity of f4(x_1,x_2,x_3,x_R) for independently sampled R=[a]P+[b]Q, b nonzero, compared to random generators, with F held fixed. **Unproven**. A single special x_P cannot generally imply special behavior at arbitrary x_R.
- **H3 (equivariant base):** for an efficiently computable endomorphism phi, a phi-stable F allows orbit reuse/quotienting and lowers *total* independent-relation cost. Must count dependence of orbit-related rows and setup costs.

## Mathematical controls and invariance
For a fixed prime-order subgroup G and fixed F subset G, any generator P'=[u]P, u != 0 mod n, induces the same uniform distribution R=[a]P+[b]Q when a is uniform. Thus decomposition existence probability over F is generator-invariant. Any reported difference in hit rates requires scrutiny of sampling, changing F, or nonuniform target selection. A conditioned F(P) changes the set itself and must be separately matched by size and construction cost.

When Q=[x]P and b != 0, a successful relation [a]P+[b]Q=sum_i F_i yields a linear equation in x and unknown factor-base logs. If the logs of all F_i were deliberately known from P, finding the target-dependent relation is itself the hard step.

For short Weierstrass E: y^2=x^3+Ax+B in odd characteristic, f3(x1,x2,x3)=(x1-x2)^2*x3^2 - 2*((x1+x2)*(x1*x2+A)+2*B)*x3 + (x1*x2-A)^2 - 4*B*(x1+x2). f4 is the resultant of two f3 polynomials over their shared coordinate. Polynomial roots require lift/sign and group-equation verification.

## Discriminating experimental plan
1. **Exact combinatorial control:** enumerate a small prime-order subgroup G and a fixed coordinate-restricted F. Construct conditioned P as a 3-sum in F and compare against other generators. Enumerate all R in G and exact 3-sum decomposition counts. Expect identical histograms for fixed F; compare sampling with seeded a,b as an additional check.
2. **Joint selection control:** choose F(P) by a preregistered generator-dependent coordinate rule. Match |F| and subgroup coverage to a generator-independent F; measure construction cost and hit rates for uniform R. Reject planted-target sampling.
3. **Semaev solver benchmark:** for multiple primes/curves and seeds, instantiate f4(x_A,x_B,x_C,x_R), measure solving degree, Gröbner basis wall time, memory, root count, sign-lift validation, and independent relation rank for random R, not only R=P or known multiples. Use exact same solver settings, warm-up and resource instrumentation; account for failures and timeouts.
4. **Equivariance benchmark:** where an explicit endomorphism exists, close F under phi, quotient by orbits, count unique independent equations, and compare full relation collection plus linear algebra time with matched non-equivariant controls.
5. **Scale gate:** report end-to-end work including generator search, factor-base construction, polynomial solving, relation filtering, linear algebra, and amortization. Compare to best verified matched index-calculus baseline and Pollard rho; do not extrapolate toy gains to P-192/P-224 without a justified complexity model.

## Acceptance and falsification
- **Null:** exact uniform-target decomposition counts are invariant for fixed F. This is expected and is a correctness control.
- **Promising:** persistent, independently replicated lower *total* cost per independent relation at matched success probability, with setup included and valid unknown-target inputs.
- **Falsified (specific mechanism):** conditioning only helps R=P or seeded known multiples; no advantage for independent uniform R, or any speed gain disappears after setup/rank accounting.
- **Unresolved:** solver timeouts or resource limits. Preserve raw outputs and do not infer impossibility.

## Artifacts and governance
- Toy control script: `research/generator-conditioned-factor-base/toy_control.py`.
- This document is a proposal, not a frozen `experiments/EXP-*/specification.yaml` or immutable `RUN-*` record.
- Follow `AGENTS.md`, `docs/task-lifecycle.md`, and Coordinator approval before allocating canonical experiment IDs or changing hypothesis status.
- No large-scale computation or Sage polynomial-system benchmark has been run by this PR.
