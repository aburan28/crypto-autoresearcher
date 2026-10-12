# Cross-family ECDLP index-calculus complexity experiment

Status: **proposal only**; no experimental speedup or hardness separation is claimed.

## Research question

For matched elliptic curves, do summation-polynomial decomposition systems show systematic differences in degree of regularity, relation yield, and end-to-end verified ECDLP solve time across curve families, models, and isogeny classes? Separate *direct IC performance* from *best available ECDLP attack after transfers*.

Jao–Miller–Venkatesan's GRH-conditional random reducibility within suitable ordinary endomorphism-order levels does **not** imply equal per-curve decomposition yield or Gröbner behavior. Conversely, observed direct-IC differences do **not** prove intrinsic hardness differences.

## Families and strata

1. **Binary characteristic-two curves:** Koblitz curves (interpreting the request's “Cobb-Douglas binary” as likely Koblitz; confirm terminology), ordinary non-Koblitz controls, and where valid, same-trace/same-order horizontal isogeny pairs. Pilot degrees 31, 51, 53, 83; reserve 131 for extrapolation, not full ECDLP solves.
2. **Prime-field curves:** ordinary short-Weierstrass curves over small prime fields, same-field/same-order horizontal isogeny pairs, and controls varying j-invariant and conductor. Include different coordinate models of the *same* curve to quantify representation effects.
3. **Prime-field extensions:** ordinary curves over F_(p^k), initially k=2,3,4,5; stratify by fixed total field bit length, base characteristic, extension degree, embedding degree and descent applicability. Avoid treating extension-field results as directly comparable to prime fields unless subgroup size and field bit length are controlled.

Exclude singular curves; record ordinary/supersingular status, group structure, prime-order subgroup, twist security, endomorphism order and conductor where computable. Explicitly label unverified invariants. Pair within a field and same group order when testing JMV-related hypotheses; cross-field comparisons are a separate stratum and **not** covered by that theorem.

## Experimental design

- Generate reproducible curves with seed, field polynomial/modulus, coefficients, cardinality, subgroup generator/order, trace, j-invariant, CM discriminant, conductor and isogeny certificate when available.
- For each curve run matched factor-base strategies: x-coordinate subspaces, trace-defined sets, Frobenius-orbit bases where applicable, random/structured bases. Match factor-base cardinality and subgroup coverage; record construction cost.
- Build Semaev summation-polynomial and/or valid decomposition systems. Record variable counts, equation degrees, monomial counts, field-equation constraints, symmetries, and representation. Apply F4/F5 and SAT variants with identical limits and deterministic seed schedules.
- Track **degree of regularity** only when mathematically justified; otherwise report observed maximal solving degree / Macaulay degree and solver-specific matrix profiles, never silently equate them.
- Sample targets uniformly in the designated subgroup. Log attempts, failed decompositions, timeouts, duplicates, invalid relations, independent verified relations, rank updates, and relation yield per target and per wall-second.
- Finish complete small-parameter DLP solves: factor-base construction + relation collection + sparse linear algebra + individual logarithm + independently verified scalar multiplication. Include unsuccessful trials in total elapsed time.
- Compare to optimized Pollard rho and, for isogenous pairs, measured isogeny discovery/evaluation/transfer overhead. Do not interpret direct-IC advantage as intrinsic hardness separation.
- Use paired seeds and repeated runs (minimum 20 where affordable); report confidence intervals, effect sizes, distributions, and hardware/compiler versions. CPU pinning/NUMA and GPU model must be recorded; normalize within hardware first.

## Primary outcomes

1. Relation probability per attempted target, with Wilson/binomial intervals.
2. Verified **independent** relations per second including preprocessing and failures.
3. Observed maximum solving degree, F4/F5 matrix dimensions/density, peak RAM, timeout fraction.
4. Full end-to-end time per verified solved logarithm (median, p90, confidence interval) and amortized per-target cost where applicable.
5. Transfer-adjusted best-known attack time and construction/evaluation cost, clearly separated from measured direct IC.
6. Dependence on characteristic, extension degree, conductor level, j-invariant, field representation and factor-base choice.

## Statistical controls and falsification

- Primary comparison: same-field, same-order, same-endomorphism-order pairs; secondary: conductor-gap pairs; tertiary: cross-family matched bit sizes.
- Cross curves × factor bases × solvers using fixed preregistered budgets; hold relation rank target and decomposition arity fixed when meaningful.
- Fit hierarchical models with family, curve, factor-base and solver effects; report interaction terms and multiple-testing correction.
- Null: after controlling for representation and solver, no systematic curve-level difference in end-to-end cost.
- A positive result requires replicated out-of-sample effects, not a single exceptional curve; publish negative results and timeout censoring.
- Audit isomorphic models to avoid attributing coordinate-system artifacts to curve hardness.
- No claim of ECDLP hardness separation without a proven lower bound for the harder family in an explicit model.

## Milestones and acceptance criteria

**M0 — Dataset and reproducibility.** Versioned curve manifests, pair certificates, baseline scripts, machine metadata, predeclared statistical protocol. All claimed same-order pairs verified.

**M1 — Pilot (31-bit binary and similarly sized prime/extension cases).** At least three valid curves per family and two factor bases per curve; complete at least one independently verified DLP per feasible stratum. Capture all failed trials.

**M2 — Scaling (51, 53, 83 binary and matched feasible prime/extension sizes).** Record full relation-yield and solver-degree curves even when complete solves exceed budgets. No extrapolated solve labeled completed.

**M3 — Isogeny/conductor analysis.** Compare horizontal same-order pairs and, where constructible, vertical pairs; measure transfers separately. Publish null/positive results with confidence intervals.

**M4 — Theoretical follow-up.** If stable gaps appear, derive structural explanation and a cost bound for an infinite family. Distinguish algorithm-specific upper bounds from optimal-complexity separation.

## Suggested artifact schema

`experiment_id,curve_id,family,field_q,characteristic,extension_degree,group_order,subgroup_order,trace,j_invariant,endomorphism_order,conductor,isogeny_pair_id,representation,factor_base_type,factor_base_size,solver,seed,attempts,successes,timeouts,duplicates,invalid_relations,independent_rank,observed_solving_degree,peak_macaulay_degree,max_matrix_rows,max_matrix_cols,peak_ram_bytes,preprocess_seconds,relation_seconds,linear_algebra_seconds,individual_log_seconds,verification_seconds,total_seconds,verified_dlp,hardware_id,commit_sha`.

## Implementation boundaries

Reuse the repository's existing index-calculus and curve-catalog interfaces where possible. Before implementation, inventory the current binaries and schemas and open separate implementation PRs for generators, solver adapters, metrics, and dashboards. This proposal PR **does not implement experiments**.

## References

- Jao, Miller, Venkatesan, *Do All Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log?* (ASIACRYPT 2005).
- Semaev summation polynomials; Gaudry and Diem index-calculus work on elliptic curves over extension fields.
