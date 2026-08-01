# ECDLP-IDEA-304 — Fourier–Deligne stationary-source transform

## Status and claim labels

- Class: `sheaf_representation`
- Risk band: `representation-changing`
- Top lane: `representation_changing`
- State: `merged_rejected_transform_preserves_supplied_incidence_and_aggregates_stalks`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid sheaf transform, trace identity, stationary-phase component, relation, or toy tuple is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-conditioned elliptic relation sheaf admits a compact Fourier–Deligne transform whose local stationary-phase or singular-support stalks are canonically and biconditionally indexed by exact signed factor tuples, yielding full relations and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the endpoint fiber as an `ell`-adic perverse sheaf on a coefficient vector space, apply Fourier–Deligne, isolate stationary/singular-support contributions, and invert each contribution to exact factor points**. This is narrower than a sparse Fourier restatement of IDEA-001: promotion requires a new singular-support-to-point inverse computed from endpoint coefficients. Laumon's transform is invertible and acts on a supplied sheaf; its trace and stalk summaries aggregate critical points unless the source incidence is already encoded. The operation therefore merges with IDEAs 001, 048, 080, 139, and 155.

## Assumptions

1. A target-uniform compact sheaf compiler exists without a source-labelled incidence table.
2. Fourier–Deligne stationary components separate all rational signed source strata over the benchmark finite fields.
3. Each component has a canonical exact point inverse with sub-rho output and ambiguity.
4. Sheaf construction, conductor/rank, transform, stalks, output, relation rank, logs, descent, verification, time, and memory are charged.

## Semantic fingerprint

`endpoint_relation_sheaf | Fourier_Deligne_transform | stationary_singular_support_split | exact_factor_stalk_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H664`, the character/spectral relation control.
3. `inputs/ledger_inventory.json` — imported `ECFG-P1422-EXACT-CHARACTER-FILTER-CONTROL`, the exact aggregate character-filter control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the character-validity/no-source-promotion boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the unresolved phase-to-source gap.

## Closest primary literature

- Laumon, [Transformation de Fourier, constantes d'equations fonctionnelles et conjecture de Weil](https://doi.org/10.1007/BF02698937), develops the geometric Fourier transform and local stationary-phase machinery for supplied sheaves.
- Deligne, [La conjecture de Weil II](https://doi.org/10.1007/BF02698791), supplies the weight/trace framework, not a source-point inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations without signed source stalk labels.

No checked source constructs the required compact relation sheaf and exact stalk-to-point inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, factor base, sheaf compiler, additive character, transform conventions, masks, and verifier.
2. Compile random known-log endpoints without source tuples, transform, and enumerate every accepted stationary component.
3. Invert components to exact signed factor points and independently verify relations.
4. Collect independent rows, solve and verify the full factor-log system.
5. Apply the identical compiler/transform/inverse to fresh masked targets `Q+[t]P`.
6. Substitute factor logs, remove masks, retain all ambiguity, and return scalar candidates.
7. Accept only exact `[x]P=Q`, charging conductors, ranks, transforms, stalks, outputs, failures, rows, logs, descent, verification, and live bytes.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one compile/transform/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes exact inverse and independent verification; `o` includes all stalk/branch outputs. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Fourier–Deligne is an equivalence on a supplied derived category, not a compression theorem that creates missing incidence. Trace functions and stationary contributions sum over critical points; separating individual point stalks requires a point-faithful sheaf or microlocal deck whose rank, conductor, or construction already carries the source fiber.

## Proof track

Construct the endpoint-only sheaf, prove bounded conductor/rank, a stationary-component/exact-point biconditional for all strata, sufficient row rank, verified factor logs, identical blind descent, and `lambda,mu<=0.45`.

## Disproof track

Prove transform equivalence conserves source-length rank/state, or exhibit two source configurations with identical checked transform data but different point tuples; charge any point-separating refinement and its output.

## Positive and negative controls

- Positive: supplied skyscraper sheaves at labelled toy points must transform and invert exactly.
- Negative: equal-trace nonisomorphic sheaves and shuffled point labels must not pass exact source recovery.
- Baselines: direct finite Fourier transforms, IDEAs 001/048/080/139/155, dense sheaf incidence, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only after independent all-strata proofs, 1,000 verified rows and 100 blind descents at each large size, with complete `lambda,mu<=0.45`.
- Falsify if compiler/transform rank, stalk output, or ambiguity reaches `N^0.50`; if a point-labelled sheaf is required; or if one valid stratum is lost.
- Exponents strictly between `0.45` and `0.50` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-304/fourier_deligne_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-304/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-304/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-304/cost_analysis.md`

## Interpretation boundary

This rejects the declared transform/inverse path only. It does not claim a lower bound for every sheaf-theoretic representation. Correct traces, stalks, or relations do not constitute a generic ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-304/fourier_deligne_source_theorem.md` proving a compact endpoint-only singular-support-to-point biconditional or the scoped rank/incidence conservation obstruction before any run.
