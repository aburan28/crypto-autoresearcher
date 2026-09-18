# GLV-aware index-calculus experiment matrix

Date: 2026-09-18
Scope: j = 0 prime-field curves with the order-3 GLV automorphism, with secp256k1 as the motivating deployed curve.
Status: design only. This file adds no result, approval, run, evidence record, or hypothesis transition.

## Why this batch exists

For a j = 0 curve E: y^2 = x^3 + b over F_p with p = 1 mod 3, let beta be a nontrivial cube root of unity and phi(x,y) = (beta*x,y). On a prime-order phi-stable subgroup G = <P>, phi acts as multiplication by a public eigenvalue lambda with lambda^2 + lambda + 1 = 0 mod N.

The repository already contains the exact informative-rank folding predecessor EXP-EQLA-164b34 and literature intake showing that endomorphism-invariant factor bases, orbit representatives, and eigenvalue-weighted relation coefficients are prior art. The new experiments below therefore do not claim novelty for orbit quotienting itself. They measure four narrower deltas that are still useful to the current harness.

## Experiments

| experiment | question | treatment | primary comparison |
|---|---|---|---|
| EXP-GLVFB-5f287d | Does a GLV-closed factor base reduce end-to-end relation plus sparse-LA cost after the density tradeoff is charged? | store one log unknown per phi-orbit and encode orientation by 1, lambda, lambda^2 | full GLV base vs same-size generic base vs generic quotient-size base |
| EXP-GLVCAN-468fb2 | How much repeated solver and storage work is eliminated by canonicalizing target and relation GLV orbits? | solve/store one canonical representative and carry orientation metadata | raw orbit-expanded pipeline vs canonical pipeline |
| EXP-GLVF-8dee36 | Can the C3 grading of the orbit-lifted j=0 Semaev system reduce actual F4/Macaulay work? | character-grade monomials by total GLV weight mod 3 and eliminate blockwise | identical system through vanilla F4, plus wrong-grading and generic-j controls |
| EXP-GLVINV-94a550 | Does quotienting the diagonal C3 action into invariant coordinates reduce PDP solver cost after degree/syzygy overhead? | derive and solve an exact quotient ideal; rational chart u_i=x_i/t, v=t^3 is only a candidate representation | raw orbit-lifted system vs quotient system with exact solution bijection checks |

## Shared rules

1. No experiment may count phi-transforms of one relation as independent relations. After orbit folding, transported rows are scalar multiples.
2. Semaev x-coordinate systems already quotient point negation. The additional symmetry under study is the order-3 GLV action, not a fresh factor six.
3. Every end-to-end comparison includes the relation-density cost, canonicalization/preprocessing cost, solver cost, sparse-linear-algebra cost, and memory.
4. Every comparison reports the applicable automorphism-adjusted Pollard-rho baseline from KN-TECH-018. None of these constant-order symmetries is treated as an exponent improvement.
5. Solver experiments also report against the maintained ICPERF boundary RQ-ICPERF-94c86e where the instance family is comparable. A smaller polynomial, matrix, or factor base is not a win unless charged cost per verified relation or charged solve cost improves.
6. Toy runs use j = 0 curves with p = 1 mod 3 and a prime-order phi-stable subgroup. secp256k1 constants may be used for exact algebraic sanity checks, but no cryptographic-scale relation-collection claim follows from toy data.
7. Every relation accepted by an experiment is independently re-added on the curve and checked against its scalar/right-hand side.

## Existing records this batch must not duplicate

- EXP-EQLA-164b34: exact informative-rank folding and the B/3 unknown space.
- EXP-JINV-dd60d3: j = 0 has smaller S3 monomial support at toy scale, but the measured Groebner time did not improve because factor-base constraints dominated.
- RQ-EQJ-001 / KN-LIT-031: generic character/isotypic decomposition of equivariant polynomial systems.
- coordination/intake/cm-factor-base-20260905/source-context.md: retrieved prior art on endomorphism-invariant factor bases and orbit representatives.
- KN-TECH-018: automorphism-adjusted rho baseline.
- RQ-ICPERF-94c86e and EXP-ICPERF-66fd51: maintained point-decomposition performance boundary.

## Recommended execution order

Run EXP-GLVFB-5f287d and EXP-GLVCAN-468fb2 first because they require no new algebraic formulation. Run EXP-GLVF-8dee36 next. Run EXP-GLVINV-94a550 only after its exact quotient map and inverse checks pass exhaustive toy truth; otherwise a favorable solver timing could merely reflect solving a different system.
