# Pre-ID duplicate draft — Hough accumulator source voting

## Status and claim labels

- Prospect: 20260720-b-F04; no canonical ECDLP idea ID was allocated
- Class / risk / lane: parameter_space_voting / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_source_points_and_aggregate_vote_ambiguity
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; an accumulator peak or valid relation is not scalar recovery.

## Falsifiable hypothesis

Map each public partial endpoint to a curve in a target-parameter space and accumulate intersections. A Hough peak would mark an exact five-source decomposition, with vote provenance replaying factor occurrences for relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

The Hough transform makes each supplied observation vote along a parameter locus; peaks aggregate observations consistent with a model. It counts only if endpoint loci are generated without source tuples, exact empty-versus-singleton support survives discretization/cancellation, and a peak returns compatible occurrence labels. Voting after enumerating partial sources is a control.

## Assumptions

1. Public endpoint loci cover all signed and exceptional strata with exact finite-field semantics.
2. Locus construction, accumulator bins or symbolic cells, every vote, restrictions, peak search, provenance, replay, rank, logs, descent, time, and memory are charged.
3. A peak is biconditional with exact source existence and not merely high aggregate density.
4. Vote provenance preserves mutually compatible occurrence labels under arbitrary restrictions.
5. One target-independent accumulator serves fresh blind targets without target-specific voting.

## Semantic fingerprint

public_endpoint_parameter_loci | Hough_vote_accumulation | exact_restricted_peak_nonemptiness | peak_votes_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted nonemptiness and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source resolver.
3. ideas/rejected/ECDLP-IDEA-155_finite_radon_source_tomography_hypothesis.md — projection aggregates do not create labelled sources.
4. ideas/rejected/ECDLP-IDEA-347_countsketch_heavy_endpoint_source_decoder_hypothesis.md — heavy aggregate buckets lose rare-source exactness.
5. ideas/rejected/ECDLP-IDEA-359_kakeya_nikodym_directional_source_focusing_hypothesis.md — directional focusing still requires source incidence.

## Closest primary literature

- Duda and Hart, [Use of the Hough transformation to detect lines and curves in pictures](https://doi.org/10.1145/361237.361242), accumulates votes from supplied image points and does not invert an implicit elliptic source fiber.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations, not a source-free vote generator.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies exact endpoint votes, rare-source provenance, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, parameter space, locus/vote rule, precision, restrictions, peak rule, and verifier.
2. Build target-independent accumulator state within B^(9/4+o(1)) without enumerating source tuples.
3. For R=[kappa]P, use exact restricted peaks to replay labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P before recording sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve false peaks/dependencies, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge locus generation, all votes/bins/symbolic intersections, peak search, restrictions, provenance, replay, rank, logs, descent, checks, bit time, and peak memory.

## Full rho/BSGS cost model

Let n be observation/locus count, v votes or exact cells per locus, A accumulator cells, Q_R restrictions, and C_inv inversion. A standard discrete transform costs Theta(nv) vote work and Theta(A) state; exact symbolic intersections charge their represented complexity instead. Set a=log_N(T_loci+nv), a_m=log_N(A+M_prov), q=log_N(Q_R(T_restrict+T_peak+C_inv)+T_replay), and q_m=log_N(A+M_peak+M_inv). With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

Votes originate from supplied observations, so faithful endpoint loci materialize partial sources. Coarse bins can create false peaks or erase singleton support; exact symbolic cells restore source-scale incidence. A peak mixes votes that need not form one compatible tuple, and arbitrary restrictions demand provenance-aware rebuilding. This merges with IDEAS 155/347/359.

## Proof track

Construct endpoint-only exact loci and prove peak/source biconditional, point-faithful provenance, restriction stability, and complete costs.

## Disproof track

Produce equal accumulator states with different singleton support or show exact bins/provenance enumerate source tuples.

## Positive and negative controls

- Positive: supplied toy points with a unique planted line and labelled vote provenance.
- Negative: equal peaks from incompatible colors, empty/singleton bins, discretization shifts, exceptional and blind targets.
- Baselines: IDEAS 155/347/359, explicit source accumulators, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only votes, zero-error restricted peak/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing vote stream, false/missing peak, incompatible provenance, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f04_vote_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f04_peak_ambiguity_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f04_cost_analysis.md

## Interpretation boundary

This rejects the elliptic voting representation, not Hough transforms. A visible peak or one valid relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f04_vote_provenance.md; do not create it under this retired pre-ID screen.
