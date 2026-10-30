# Follow-up selected by the user

The user accepted the three next actions in the preceding report: compare equivalent quartic, curve-membership and quadratic-lift encodings; integrate shared divisor coefficients with certified SAT and complete chart handling; require a structural change before expanding the existing matrix/backdoor sweeps. The last item is a constraint on this work, not an additional sweep.

Reconciliation: previous RUN-PFIVE-e793f3 is output_validated and its executor released completed. No related producer remains active. Preserve both previous runs and all reports. Continue PR2679 and its branch. Fresh origin/main 862fea464c was fetched (a refetch repaired an unresolved-delta transport error) and merged before design. Full ledger/backlog checks refuse this sparse checkout; no bypass or portfolio-wide pass is claimed.

Sources inspected on 2026-10-29:

- Kosters and Yeo, https://arxiv.org/html/1503.08001, Proposition 2.1 and the discussion distinguishing first fall degree from regularity. Retrieved primary text. The summation-polynomial property concerns geometric lifts; the two-summand rational-lift argument has explicit non-two-torsion and characteristic assumptions.
- Hader et al., https://arxiv.org/html/2402.17927v1, Sections 4 and 5. Retrieved primary text. The finite-field engine tracks feasible values and explains conflicts with polynomial consequences. This motivates a certificate-producing univariate residual test, not a claim to implement Yices or reproduce its benchmarks.
- Prior source, checked run, and exact lift identities: research/prime_sat_five_tests_20261029/ and experiments/EXP-PFIVE-e26798/reports/run-20261029T0454Z/. Internal evidence. Earlier partial-matrix and fixed two-bit backdoor outcomes motivate the user's deferral; no global closure follows.

Prospective implementation boundary (not yet a frozen protocol):

1. Same complete projected coordinate sets, same certified polynomial-calculus learner and search limits; quartic, membership-augmented, quadratic lift, and quadratic A/A order control. Canonical lambda field encoding, all range constraints explicit. Independent full model-set and group-law checking. Costs separated into construction, search, certificate checking, witness reconstruction, and independent oracle work. No timing/regularity/attack claim.
2. Shared coefficient membership coupled to SAT. Prefer exact univariate residual gcd/Bezout certificates after fixing three of four field coefficients; retain all learned clauses and charge the polynomial construction, gcd, certificate checks, root extraction, and chart fallback. Compare with exhaustive coefficient evaluation and a matched SAT leaf-only arm. Require complete relation coverage for the declared predicate, including explicit exceptional-chart fallback and its cost. No use of post-solve oracle/model sets to select prefixes or clauses.

Scientific fixtures may run only after the complete native protocol is frozen, committed, admitted and owned. Integrity checks of arithmetic/certificates may run before freeze; their evidence is software validation only. Final field/target inventory and caps belong in the new config and protocol, not this sketch.
