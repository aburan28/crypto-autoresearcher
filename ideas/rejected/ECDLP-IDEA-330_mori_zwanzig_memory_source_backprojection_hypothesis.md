# ECDLP-IDEA-330 — Mori–Zwanzig memory-kernel source backprojection

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_projection_kernel_requires_microscopic_source_dynamics`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact generalized Langevin identity, memory kernel, valid relation, or toy reconstruction is not an ECDLP break.

## Falsifiable hypothesis

Projecting serial elliptic source dynamics onto endpoint observables yields a compact Mori–Zwanzig memory kernel whose finite convolution can be backprojected to every exact factor trajectory inside the P1553 bounds.

## Mechanism-new operation

The screened operation is **choose resolved endpoint observables, project the full addition dynamics, compute the orthogonal-dynamics memory kernel, and invert its history term to exact source points**. This differs formally from a Koopman delay embedding but merges with IDEAs 069, 073, 176, 302, 308, and 329: the exact kernel is defined using the unresolved microscopic dynamics and projection. Estimating it from source trajectories imports the source; discarding orthogonal dynamics loses the ancestry needed for replay.

## Assumptions

1. A target-independent projection onto compact endpoint observables is constructible without enumerating source states.
2. The orthogonal-dynamics memory kernel has bounded length and rank for all source strata.
3. Endpoint plus memory data invert canonically to exact signed factor trajectories.
4. Projection, kernel construction, history convolution, inversion, output, rank, logs, descent, verification, and memory are charged.
5. The same kernel applies to fresh masked targets without trajectory-trained coefficients.

## Semantic fingerprint

`serial_source_dynamics | endpoint_observable_projection | Mori_Zwanzig_memory_kernel | exact_history_backprojection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1477`, the serial forward/backward endpoint-state control.
2. `inputs/ledger_inventory.json` — imported `P1478`, the compact transition and dense composition boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H680`, the recursive source-resolving circuit proposal.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-history boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the differential-state noncompression control.

## Closest primary literature

- Zwanzig, [Memory effects in irreversible thermodynamics](https://doi.org/10.1103/PhysRev.124.983), derives a memory equation after a projection of supplied microscopic dynamics.
- Mori, [Transport, collective motion, and Brownian motion](https://doi.org/10.1143/PTP.33.423), develops the projection-operator generalized Langevin formalism.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies an endpoint relation equation, not microscopic source trajectories or a memory inverse.

No checked source supplies the compact kernel from endpoint data or a complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor decks, resolved observables, projection, kernel convention, source policy, masks, and verifier.
2. Construct one source-free kernel, apply it to known-log endpoints, backproject all exact factor trajectories, and verify every relation.
3. Collect at least `B=N^(1/5)` independent rows, solve all factor logs, and independently verify them.
4. Reuse the identical kernel on fresh scalar-blind masked targets without microscopic histories.
5. Substitute logs, remove masks, retain ambiguity, and accept only exact `[x]P=Q`.

## Full rho/BSGS cost model

Let setup and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, projection/kernel evaluation excluding emission `N^q,N^q_m`, verified rank credit `N^r`, trajectory output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

The microscopic generator, orthogonal propagator, kernel coefficients, history length, branches, output, and verification are charged, with `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The exact Mori–Zwanzig kernel is a re-expression of the unresolved microscopic dynamics, not a method for inferring that dynamics from one terminal observation. Computing the orthogonal propagator requires the hidden source state space; a learned kernel consumes source trajectories and may reproduce only aggregates.

## Proof track

Construct a compact endpoint-only projection/kernel, prove finite memory and exact all-strata backprojection, then establish full relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show two source histories have identical resolved endpoint memory data, or prove any exact kernel evaluator contains the source transition matrix or a `B^3` history table.

## Positive and negative controls

- Positive: supplied finite linear systems with known microscopic generators must satisfy exact memory identities and backprojection where observable.
- Negative: source-history permutations with equal resolved dynamics must not yield preferred factor points.
- Baselines: IDEAs 069/073/176/302/308/329, explicit history enumeration, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only kernel theorem, exact all-strata replay, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if the microscopic generator/history is supplied, kernel state reaches `B^3`, one source history collides, or either exponent reaches `0.50`.
- A correct identity using supplied dynamics is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-330/microscopic_kernel_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-330/history_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-330/independent_memory_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-330/cost_analysis.md`

## Interpretation boundary

This rejects only the declared endpoint-only memory backprojection. It does not reject projection methods generally. A valid memory identity or toy relation is not source-complete ECDLP evidence or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-330/microscopic_kernel_input_receipt.md` expanding the exact orthogonal propagator and identifying the first coefficient that requires hidden source dynamics.
