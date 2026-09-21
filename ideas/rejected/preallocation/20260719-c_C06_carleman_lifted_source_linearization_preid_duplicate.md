# Pre-ID duplicate draft — Carleman-lifted source linearization

## Status and claim labels

- Prospect: `20260719-c-C06`; no canonical ID allocated
- Class / risk / lane: `lifted_linear_representation` / `representation-changing` / representation-changing pre-ID screen
- State: `merged_rejected_infinite_monomial_lift_or_uncontrolled_truncation`
- Evidence: complete-corpus and primary-literature review only; no experiment
- Contract posture: retired zero-run text snapshot
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Embed the nonlinear elliptic partial-addition recurrence into a sparse Carleman monomial lift, truncate at endpoint-independent degree while preserving exact zero structure, and use linear reachability/Krylov state to recover signed source tuples, factor logs, and fresh blind descents below rho/BSGS.

## Mechanism-new operation

Carleman linearization replaces nonlinear monomials by coordinates of an infinite-dimensional linear system. It counts only if a finite exact invariant section preserves all relation zeros and source ancestry; ordinary truncation or a solver change is a representation control.

## Assumptions

1. Elliptic addition and membership admit a target-independent polynomial recurrence whose finite Carleman section is exact on every chart.
2. Lift construction, monomial count, truncation error, linear algebra, restrictions, source inverse, rank, logs, descent, and memory are charged.
3. The exact source inverse does not require one monomial per tuple or scalar-labelled state.
4. One frozen lifted operator serves known-log and fresh `Q+[t]P` targets.
5. No approximate zero, dense monomial basis, post-hoc selector, or uncharged nonlinear evaluation is admitted.

## Semantic fingerprint

`elliptic_nonlinear_endpoint_recurrence | Carleman_monomial_lift | finite_exact_invariant_section | linear_state_to_signed_sources | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted common-factor existence remains open.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-MX-1478`: exact one-transition linearization becomes dense on composition.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1477`: dense forward/backward states miss the complete boundary.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: tested public feature spaces do not recover factor logs.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a compact exact endpoint-to-source circuit is still required.

## Closest primary literature

- Carleman, [Application de la théorie des équations intégrales linéaires aux systèmes d'équations différentielles non linéaires](https://doi.org/10.1007/BF02546499), gives the infinite linear embedding.
- Amini, Zheng, Sun, and Motee, [Carleman Linearization of Nonlinear Systems and Its Finite-Section Approximations](https://arxiv.org/abs/2207.07755), treats finite sections with approximation bounds, not exact finite-field zero preservation.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) remains the baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, polynomial recurrence, lift order, restrictions, and verifier.
2. Build a target-independent exact lifted operator/state within `B^(9/4+o(1))`.
3. For known-log targets, answer exact restricted existence and invert one accepting lifted state to five verified occurrences.
4. Collect at least `B` independent rows, retain failures/dependencies, and solve factor logs.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover/verify a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge lift size, composition, negative queries, inverse output, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, fresh work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho time and BSGS time/memory are `0.50` controls.

## Likely fatal obstruction

The exact lift is infinite; finite truncation is approximate unless an invariant finite closure is proved. Degree and monomial count grow under repeated elliptic composition, while a source-faithful basis approaches one coordinate per partial source state. This merges with IDEAs `056/267/329/330/387` and the dense-state ledger receipts.

## Proof track

Prove a bounded exact invariant Carleman section, all-chart zero biconditional, source inverse, and full sub-rho descent costs.

## Disproof track

Show a truncated false zero, monomial degree/dimension growth, source ambiguity, or any complete exponent outside the gates.

## Positive and negative controls

- Positive: polynomial recurrences with a known finite invariant monomial closure.
- Negative: same low-degree truncation with different higher-degree zeros, exceptional charts, restrictions, blind targets.
- Baselines: IDEAs `056/267/329/330/387`, exact untruncated lift, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with an exact finite-section theorem, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one truncation mismatch, source-labelled monomial, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-c/c06_finite_section_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-c/c06_truncation_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260719-c/c06_cost_analysis.md`

## Interpretation boundary

This rejects the screened finite lift, not all Carleman methods. A correct lift identity or toy trajectory is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-c/c06_finite_section_obligations.md` and enumerate the monomials forced by two composed elliptic-addition transitions.
