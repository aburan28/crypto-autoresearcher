# ECDLP-IDEA-189 — Garside braid-lift source normal form

## Status and claim labels

- Class: `combinatorial_representation`
- Risk band: `high_risk`
- Top lane: `none`
- State: `scoped_negative_no_public_canonical_braid_lift`
- Cohort: `20260718-d`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: rejected at the endpoint-to-braid lift and leaf-return gates; no contract or run is authorized
- Scale labels: every future finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a canonical braid word, valid normal form, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a public, target-uniform lift from an elliptic endpoint and its addition correspondence to a braid element such that the Garside left-greedy normal form canonically returns every ordered signed factor-base leaf, rather than only the induced permutation or monodromy class. Running that lift on known-log endpoints and blind masked targets would yield a complete factor-base descent below rho and BSGS without enumerating the source fiber.

## Mechanism-new operation

The operation is **endpoint-derived braid-monodromy lifting followed by Garside left-normal-form source extraction**. It is mechanism-new only if the braid lift is canonical, coordinate-only, scalar-blind, compact, and biconditional with exact factor-point leaves. Choosing a braid after seeing a source tuple, retaining an explicit strand-to-factor dictionary, enumerating Hurwitz lifts, or applying a generic solver is a control.

The scoped review is negative: an endpoint determines at most a symmetric quotient or permutation/monodromy class unless a path, branch system, and labeled lifts are added. Garside normal form canonicalizes a supplied braid element; it does not canonically lift the public endpoint to that braid or reconstruct the identities of its leaves. The missing lift is the existing source-fiber problem.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, branch locus, base path system, Garside structure, masks, and verifier are frozen.
2. A canonical braid lift is computed from endpoint coordinates without scalar labels, source tuples, or post-hoc path choices.
3. Left-greedy normal form preserves enough information to identify exact signed factor points, repeats, multiplicities, and exceptional branches.
4. The lift and normal form return all and only source tuples with sub-rho ambiguity and without materializing a `B^m` strand deck.
5. Branch tracking, braid length, normalization, source output, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`public_endpoint_braid_monodromy_lift | Garside_left_greedy_normal_form | exact_signed_leaf_return | no_strand_source_dictionary | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless edge/source-deck boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the path-state representation boundary.
4. `inputs/ledger_inventory.json` — imported `P1477`, the nearest canonical transition normal-form proposal.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge materialization boundary.

## Closest primary literature

- Garside, [The braid group and other groups](https://doi.org/10.1093/qmath/20.1.235), proves normal-form and lattice structure for supplied braid elements.
- Dehornoy and Paris, [Gaussian groups and Garside groups, two generalisations of Artin groups](https://doi.org/10.1112/S0024611599012071), generalizes normal-form machinery for a supplied group element but does not provide an elliptic endpoint lift.

Neither checked primary source gives a public finite-field braid lift whose normal form returns exact factor-base leaves; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta,m`, the factor base, addition correspondence, branch system, braid generators, Garside element, masks, strata, and verifier.
2. Prove a compact scalar-blind algorithm that lifts each public endpoint to all relevant braid elements without choosing or enumerating its source tuples.
3. For known-log endpoints `R_j=[r_j]P`, compute the canonical lift and Garside left normal form, then decode every normal-form output to an exact signed factor-base tuple.
4. Verify every decoded sum and preserve Hurwitz-equivalent lifts, repeated factors, cancellations, infinity, branch collisions, misses, multiplicities, and full output.
5. Collect at least `B+sigma` verified independent relation rows of rank `B`, solve factor logs, and independently verify every recovered logarithm.
6. Apply the identical frozen lift and normalization to fresh masked targets `Q+[t]P` chosen independently after setup.
7. Substitute verified factor logs, remove masks, retain every braid/source ambiguity candidate, and accept only `x` with `[x]P=Q`.
8. Charge branch construction, path continuation, braid length, normalization, leaf output, failed endpoints, rank, logs, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant-sized state; BSGS costs `N^(1/2+o(1))` time and memory. Let canonical braid-lift setup have time and memory exponents `a,a_m`; let reciprocal relation and masked-target densities be `N^delta,N^delta_t`; let one lift plus Garside normalization cost `N^q,N^q_m`; let decoded leaf output and target ambiguity have exponents `o,u`; and let factor-log algebra have exponents `ell,ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All path choices, braid words, simple factors, Hurwitz branches, leaf dictionaries, failed lifts, and verification are charged.

## Likely fatal obstruction

There is no canonical public braid lift from a symmetric elliptic endpoint: a braid records how labeled branches move along a chosen path, so it requires branch labels and path data absent from the endpoint. Different source tuples can induce the same permutation or monodromy class, and Garside normal form retains that supplied braid class rather than recovering factor-point leaves. Listing all compatible lifts reinstates the original source fiber and its output.

## Proof track

Construct an endpoint-only finite-field braid lift, prove independence from auxiliary paths and branch labeling, prove a biconditional between left-normal factors and every exact signed source tuple on all strata, and derive complete `lambda,mu<=0.45` blind descent.

## Disproof track

Exhibit two source-distinct fibers with the same endpoint monodromy or permutation class, prove any separating lift requires labeled branches or source continuation, force exhaustive Hurwitz lifting, lose an exceptional stratum, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: supplied braid words with published Garside normal forms and independently known strand labels.
- Positive control: toy elliptic paths for which sources and branch continuation are deliberately supplied.
- Negative control: erase, permute, or change branch labels and paths while holding the endpoint and permutation class fixed.
- Negative control: exhaustive Hurwitz lifts, explicit source decks, dense resultants, rho, BSGS, known-log endpoints, and blind masked targets.

## Quantitative promotion and falsification gates

The current operation is a scoped negative. Reopening under a new ID requires path-independent public lifting, 100% source/multiplicity recall on preregistered toy strata, zero false leaves, no strand/source dictionary, and formal `lambda,mu<=0.45`. If `0.45<max(lambda,mu)<0.50`, the result is inconclusive; any auxiliary source lift, path-dependent answer, lost tuple, false tuple, or `max(lambda,mu)>=0.50` falsifies the successor.

## Artifact plan

- Prospective public-lift theorem: `ideas/artifacts/ECDLP-IDEA-189/public_braid_lift_theorem.md`
- Prospective normal-form/source biconditional: `ideas/artifacts/ECDLP-IDEA-189/garside_source_biconditional.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-189/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-189/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-189/cost_analysis.md`

All paths are prospective. No artifact root, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is rejected, novelty-unverified evidence about a braid-lift gate. Any finite check would be toy, and cost projections are heuristic and model-bound. A correct Garside normal form, a valid relation, or known-log recovery is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-189/public_braid_lift_theorem.md` and prove or refute the existence of a path-independent endpoint-to-braid lift that distinguishes exact factor-point leaves without labeled source continuation.
