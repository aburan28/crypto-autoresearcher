# ECDLP-IDEA-195 — Non-Cartesian S3 intertwiner source router

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `deferred_needs_noncanonical_intertwiner_and_exact_source_inverse_theorem`
- Cohort: `20260718-d`
- Evidence scale: literature and theorem preflight only; no experiment ran
- Contract posture: relative top-lane draft is retired, `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite test is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a branch identity or compressed pair map is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent rational map `psi` outside the canonical ECFFT family and a non-Cartesian recursive support `Sigma_F` on which both coefficients of the complete Kummer `S3` branch polynomial descend through `psi`, with bounded exact inverse fibers. Iterating that support-changing intertwiner yields exact signed five-source rows and blind descents below rho and BSGS.

## Mechanism-new operation

The operation is **simultaneous trace/norm descent on a non-Cartesian recursively constrained support**, followed by an exact branch-to-point inverse. It is not a same-field isogeny, a global quotient label, the canonical `x+c+1/x` ECFFT map, or a trace-only filter. P1526 closes target-isogeny and unrelated auxiliary-tree routing; P1527 closes the canonical map on `y^2=x^3+1` except deck-fixed and bounded residual loci; P1528 proves that same-field rational isogeny kernels on the near-prime-order target are only `N^o(1)` and give duplicate factor-log columns. This successor survives only for a genuinely different non-group map/target family, an explicitly charged extension-field return, or a later-stage non-Cartesian support component not visible at the Cartesian pair gate.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, `F` of size `B=N^beta`, and target `Q=[x]P` are frozen.
2. `psi` and `Sigma_F` are generated target-independently from public curve/factor-base data with no pair table.
3. Both transformed trace and norm descend, so the complete unordered Kummer branches are transported.
4. Every transported branch lifts to all exact signed point sources on exceptional and nonreduced strata.
5. Setup, support tests, inverse lists, failed targets, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`noncanonical_rational_map | non_Cartesian_recursive_support | simultaneous_S3_trace_norm_intertwiner | bounded_exact_branch_inverse | blind_masked_descent`

Global isogenies, canonical ECFFT maps, trace-only invariants, explicit pair tables, and dense resultants fail the fingerprint.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1399`, the rational-map factor-base predicate frontier.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, a support-changing source-router hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H686`, the target-conditioned algebraic support frontier.
4. `inputs/ledger_inventory.json` — imported `P1473`, the exact sparse-subgroup one-step membership control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, where endomorphism-stable transitions are nonfunctional and dense.

## Closest primary literature

- Ben-Sasson, Carmon, Kopparty, and Levit, [ECFFT Part I](https://arxiv.org/abs/2107.08473), supplies auxiliary isogeny evaluation trees but no target-curve addition intertwiner.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the complete branch relation.
- Chalcraft and Fryers, [Kummer structures](https://arxiv.org/abs/0806.0409), formalizes two-valued Kummer addition but not the proposed restricted-support source inverse.

No checked primary source supplies the complete non-Cartesian operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve family, `psi`, support equations, branch charts, inverse rule, masks, and verifier.
2. Prove simultaneous trace/norm descent and positive-dimensional nonfixed support before any finite search.
3. Build the support/intertwiner inside the frozen setup bound and route known-log endpoints to exact sources.
4. Verify every source and preserve all failures, lists, signs, repeats, poles, infinity, and multiplicities.
5. Collect `B+sigma` independent rows, solve factor-base logs, and verify them.
6. Route fresh masked targets `Q+[r]P` under the identical support and inverse.
7. Substitute factor logs, subtract masks, preserve ambiguity, and accept only `[x]P=Q`.
8. Serialize construction, queries, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one support query plus inverse cost `N^q,N^q_m`; independently ranked rows per query be `N^r`; output and inverse ambiguity exponents be `o,u`; and factor-log linear algebra cost `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

The P1515 router gate additionally asks for setup at most `B^2.25` and one-row query at most `B^1.25`; promotion still requires both complete exponents at most `0.45`.

## Likely fatal obstruction

Simultaneous branch transport imposes `Theta(B^2)` pair constraints. For a generic support these force degree growing with `B`, an explicit correction table, or only deck-fixed/constant residual components. A global composable map is constant/injective on the prime-order group; P1528 further bounds target-isogeny rational branching by the subpolynomial cofactor and removes its duplicate log columns. Later non-Cartesian or extension-field constraints may simply hide the same `B^3` transition deck or its descent cost.

## Proof track

Exhibit an explicit map and support family; prove a positive-dimensional nonfixed simultaneous trace/norm component across the claimed curve family; prove exact all-strata inverse lists; and derive complete `lambda,mu<=0.45` with the P1515 setup/query rectangle.

## Disproof track

Prove the compatibility ideal has only deck-fixed or bounded residual components, show map degree/table size grows at least `B`, reduce recursive support to `B^3` provenance, find one lost branch, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: supplied two-valued Kummer maps with known exact branch inverses.
- Positive control: symbolic compatibility ideals on preregistered toy targets, roots withheld from the constructor.
- Negative control: P1526 global/isogeny routes, the P1527 canonical `x+c+1/x` branch locus, and P1528 same-field rational-kernel multiplicity.
- Negative control: trace-only filters, explicit pair tables, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

Remain theorem-deferred and do not run the retired contract. Reopening requires an explicit noncanonical map/support theorem, an exact inverse with 100% source/multiplicity recall and zero false tuples, no explicit pair table, setup at most `B^2.25`, query at most `B^1.25`, and `lambda,mu<=0.45`. Deck-fixed-only support, bounded residue, a `B^2` correction table, one lost source, or exponent at least `0.50` falsifies that successor.

## Artifact plan

- Prospective compatibility theorem: `ideas/artifacts/ECDLP-IDEA-195/noncartesian_intertwiner_theorem.md`
- Prospective exact inverse specification: `ideas/artifacts/ECDLP-IDEA-195/branch_source_inverse_spec.md`
- Prospective fixtures and verifier: `ideas/artifacts/ECDLP-IDEA-195/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-195/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-195/cost_analysis.md`
- Retired contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-195_noncartesian_intertwiner_preflight.yaml`

All paths are prospective; no artifact root or run exists.

## Interpretation boundary

This is novelty-unverified theorem-deferred representation work, not positive ECDLP evidence. Finite checks would be toy and asymptotics heuristic and model-bound. A branch identity, valid source, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-195/noncartesian_intertwiner_theorem.md` giving one explicit noncanonical map/target family and positive-dimensional nonfixed simultaneous trace/norm support with exact all-strata inverse, or a symbolic elimination proving that the proposed family has only deck-fixed or bounded residue; do not run the retired contract.
