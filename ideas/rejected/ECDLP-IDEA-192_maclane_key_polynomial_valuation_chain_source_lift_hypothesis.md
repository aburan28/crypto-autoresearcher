# ECDLP-IDEA-192 — MacLane key-polynomial valuation-chain source lift

## Status and claim labels

- Class: `valuation_theoretic_representation`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_valuation_elimination_backend`
- Cohort: `20260718-d`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: selected for a retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs are permitted
- Scale labels: any future finite check is `toy`; all cost projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid augmented valuation, key polynomial, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For the endpoint-specialized elliptic summation fiber, a compact target-uniform MacLane chain of augmented valuations and key polynomials separates every relevant source branch, and its residual data lifts biconditionally to the exact signed factor-base points on that branch. The same construction on known-log endpoints and fresh masked targets would then provide complete relations and blind target descent with time and memory exponents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **endpoint-specialized MacLane key-polynomial valuation-chain construction followed by residual branch-to-exact-source lifting**. It is mechanism-new only if a bounded chain is built directly from public coordinates, separates all relevant branches uniformly, and returns exact point identities without factoring a dense eliminant or enumerating roots/sources. A chain constructed from already isolated roots, source-indexed valuations, a full resultant, parameter tuning, or a generic solver is a control.

The current sketch is merged/rejected as a valuation/elimination backend: primary theory constructs augmented valuations from valued polynomial data but supplies neither a compact endpoint-derived key chain nor an all-strata exact source biconditional. The only reopen condition is a theorem proving a **compact target-uniform separating MacLane key chain plus exact source lift**. Current evidence suggests generic smooth source branches share coarse valuations and that separating keys grow with total eliminant degree/output or require source-indexed choices.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, a sparse summation-fiber presentation, base valuation, key-selection rule, masks, strata, and verifier are frozen.
2. Endpoint specialization yields a compact polynomial/valuation input without constructing the dense source eliminant or enumerating its roots.
3. One target-uniform MacLane chain separates every exact signed factor-base branch, including repeats, cancellations, infinity, singularities, and residue-field extensions.
4. Residual polynomials and augmentation data lift canonically and biconditionally to exact factor-point coordinates with sub-rho ambiguity.
5. Polynomial construction, key search, augmentation length, residue extensions, output, rank, factor logs, target descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`endpoint_specialized_summation_fiber | compact_target_uniform_MacLane_key_chain | valuation_branch_separation | residual_exact_factor_source_lift | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate preprocessing barrier relevant to a purported compact key-chain coordinate.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`, the canonical root-product/output boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-structure boundary.
4. `inputs/ledger_inventory.json` — imported `P1478`, the nearest transition/resultant branch proposal.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.

## Closest primary literature

- MacLane, [A construction for absolute values in polynomial rings](https://doi.org/10.2307/1989629), constructs inductive valuations by successive key-polynomial augmentation.
- MacLane, [A construction for prime ideals as absolute values of an algebraic field](https://doi.org/10.1215/S0012-7094-36-00243-0), develops valuation extensions and key data for supplied algebraic inputs.

Neither primary source proves a bounded endpoint-uniform chain that separates a high-degree elliptic source fiber or lifts its residual branches to exact point identities; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta,m`, the factor base, sparse summation-fiber presentation, base valuation, key-selection rule, residue conventions, masks, exceptional strata, and verifier.
2. From public endpoint coordinates, construct a compact specialized polynomial/valuation input without dense elimination, root enumeration, scalar labels, or source advice.
3. For known-log endpoints `R_j=[r_j]P`, build the target-uniform MacLane chain, enumerate its relevant residual branches, and lift each branch to every exact signed factor-base tuple.
4. Verify every lifted tuple sum and preserve repeated factors, cancellations, infinity, equal-valuation branches, residue extensions, misses, multiplicities, and full output.
5. Collect at least `B+sigma` verified independent relation rows of rank `B`, solve all factor-base logarithms, and independently verify each recovered log.
6. Apply the identical frozen polynomial, valuation-chain, and source-lift rules to fresh masked targets `Q+[t]P` selected independently after setup.
7. Substitute verified factor logs, remove masks, retain every valuation/residual ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Charge sparse input construction, any elimination, key search, all augmentations, residual factorization, exact source output, failed endpoints, rank, descent, total time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant-sized state; BSGS costs `N^(1/2+o(1))` time and memory. Let compact polynomial and key-chain setup have time and memory exponents `a,a_m`; let reciprocal relation and masked-target densities be `N^delta,N^delta_t`; let one valuation-chain evaluation plus residual lift cost `N^q,N^q_m`; let exact source output and residual target ambiguity have exponents `o,u`; and let factor-log algebra have exponents `ell,ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every eliminant coefficient, key candidate, augmentation, residue extension, branch factor, lifted source, failed endpoint, and verification is charged; total key degree and output cannot be hidden in an oracle.

## Likely fatal obstruction

Generic smooth source branches can have identical coarse valuations and residual degrees. Separating them forces additional keys whose cumulative degree or residual output approaches the full endpoint eliminant/source fiber, or it requires choosing augmentations from already known roots and is therefore source-indexed. Constructing the valued polynomial itself may also be the dense elimination already recorded as nonpromoting. The remaining uncertainty is whether a special nonhomomorphic elliptic structure yields a uniformly bounded separating chain and exact lift.

## Proof track

Prove a uniform theorem bounding chain length, total key degree, residue degree, construction time, and memory; prove all-strata biconditionality between residual branches and exact signed factor tuples; exclude dense elimination and source advice; then derive complete `lambda,mu<=0.45` blind descent.

## Disproof track

Construct an infinite family of endpoint fibers with source-distinct branches sharing every bounded key invariant, prove total separating key degree or output is `Omega(B^m)`, reduce key selection to root/source isolation, find a lost stratum, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: published MacLane chains for supplied low-degree valued polynomials with independently known branches.
- Positive control: preregistered toy summation fibers whose full roots are withheld from the chain constructor and revealed only to the verifier.
- Negative control: chains seeded with known roots, dense resultants, full factorization, source-indexed augmentations, and bounded chains on deliberately valuation-colliding branches.
- Negative control: parameter-only key changes, rho, BSGS, known-log endpoints, and fresh blind masked targets.

## Quantitative promotion and falsification gates

This version remains merged/rejected, and the selected retired preflight must not run. Reopening under a new ID requires the compact target-uniform separating-key-chain plus exact-source-lift theorem, 100% source/multiplicity recall and zero false tuples on preregistered toy strata, no root/source advice, and formal `lambda,mu<=0.45`. If `0.45<max(lambda,mu)<0.50`, evidence is inconclusive; a dense eliminant, source-indexed key, lost branch, false tuple, unbounded chain/output, or `max(lambda,mu)>=0.50` falsifies a successor.

## Artifact plan

- Prospective bounded-chain theorem: `ideas/artifacts/ECDLP-IDEA-192/compact_key_chain_theorem.md`
- Prospective residual source-lift specification: `ideas/artifacts/ECDLP-IDEA-192/source_biconditional_spec.md`
- Prospective collision family: `ideas/artifacts/ECDLP-IDEA-192/valuation_collision_family.md`
- Prospective fixtures, independent verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-192/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-192/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-192/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-192_maclane_key_preflight.yaml`

All research-artifact paths are prospective; no artifact root or run exists. The retired contract is review-required, unapproved, and zero-run.

## Interpretation boundary

This is merged/rejected, novelty-unverified valuation-theoretic evidence, not positive ECDLP evidence. Any finite check would be toy, and projections are heuristic and model-bound. A correct key chain, isolated branch, relation, or known-log result is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-192/compact_key_chain_theorem.md` proving a target-uniform bound and exact all-strata source lift or recording an explicit family that forces total key degree/output `Omega(B^m)`; do not execute the retired contract.
