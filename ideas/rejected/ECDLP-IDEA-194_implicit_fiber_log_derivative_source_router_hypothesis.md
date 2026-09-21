# ECDLP-IDEA-194 — Implicit fiber log-derivative source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_implicit_eliminant_restores_dense_provenance`
- Cohort: `20260718-d`
- Evidence scale: literature and symbolic cost audit only; no experiment ran
- Contract posture: relative top-lane draft is retired, `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite test is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a gcd, log derivative, source tuple, or relation is not an ECDLP break.

## Falsifiable hypothesis

A target-batch gcd and logarithmic derivative of a succinct recursive-`S3` fiber circuit can be reverse-differentiated through Hasse jets to emit exact signed five-point factor-base sources without expanding the `B^3` middle-state deck. The same operation would provide enough independently ranked known-log rows and masked target descents with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The proposed operation is `FiberJet(C_F,H)`: retain a target-independent circuit `C_F` for the five-source fiber, intersect it with a batch polynomial `H`, compute a logarithmic derivative only on common target factors, and reverse automatic-differentiation/Hasse-jet data to the five labelled leaves. This differs syntactically from a dense resultant and from P1428 union-root reporting because the claimed output is exact leaf ancestry. The audit finds that the required reverse ancestry is precisely the missing operation: without a proved compressed reverse map, `C_F` is a dense eliminant or a source-labelled `B^3` transition object.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, factor base `F` of size `B=N^beta`, and target `Q=[x]P` are fixed.
2. `C_F` is built without enumerating pair/triple states, source tuples, or a dense resultant.
3. The log derivative distinguishes multiplicities, signs, repeats, vertical pairs, infinity, and nonreduced fibers.
4. Reverse Hasse jets return every exact labelled source and no false source without post-hoc root matching.
5. Setup, failed batches, output, rank, factor logs, blind descent, verification, and bit memory are charged.

## Semantic fingerprint

`implicit_recursive_S3_fiber_circuit | target_batch_gcd_log_derivative | reverse_Hasse_jet_leaf_ancestry | exact_signed_sources | blind_masked_descent`

The fingerprint fails its novelty gate if the circuit materializes transition states, if the derivative returns only target roots, or if source labels are joined after factorization.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1478`, the sparse-`S3` norm primitive whose composition becomes dense.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where shared union roots lose row/source identity.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the zero/common-root output boundary.
4. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
5. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-`S3` state-compression control.

## Closest primary literature

- Baur and Strassen, [The complexity of partial derivatives](https://doi.org/10.1016/0304-3975(83)90110-X), gives reverse arithmetic-circuit differentiation, not source recovery from an implicit elliptic fiber.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the recursive relation polynomial but no compressed leaf inverse.
- Kedlaya and Umans, [Fast polynomial factorization and modular composition](https://doi.org/10.1137/08073408X), is a polynomial-arithmetic control; it does not remove represented degree or provenance.

No checked primary source supplies `FiberJet` with exact source replay; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `F`, charts, signs, masks, circuit grammar, batch schedule, and independent verifier.
2. Build the target-independent circuit and its reverse-Hasse interface without explicit source states.
3. Batch known-log endpoints `[a_j]P`, compute supported common factors, and emit all exact signed five-source tuples.
4. Independently verify each tuple and preserve multiplicity, collision, infinity, and failed-batch data.
5. Collect at least `B+sigma` independent rows, solve and verify all factor-base logarithms.
6. Apply the identical frozen operation to fresh masks `Q+[r]P`.
7. Substitute verified factor logs, subtract `r`, retain every ambiguity candidate, and accept only `[x]P=Q`.
8. Serialize setup, attempts, output, rank, linear algebra, descent, verification, wall time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one batch/query plus reverse lift cost `N^q,N^q_m`; independently ranked rows per batch be `N^r`; output and target ambiguity exponents be `o,u`; and factor-log linear algebra cost `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Promotion would require both at most `0.45`; an implicit target polynomial alone has no performance meaning.

## Likely fatal obstruction

The log derivative is defined only after a polynomial carrying the common target factors exists. Preserving which five leaves produced each factor requires source tags through `Theta(B^3)` middle states, while dropping those tags gives the source-losing P1428 union. Expanding the implicit gcd or reverse Jacobian recreates a dense `B^2/B^3` eliminant and exceeds the promotion gate.

## Proof track

Construct a sub-`B^2.25` circuit directly from endpoint and factor-base data; prove a target-uniform reverse-Hasse source biconditional on every stratum; prove multirow independence; and derive `lambda,mu<=0.45` without represented-degree or source traffic.

## Disproof track

Reduce reverse ancestry to explicit transition tags, prove circuit/derivative degree or state at least `B^3`, exhibit two source fibers with identical retained jets, find one missed multiplicity, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: reverse differentiation of a supplied small source-labelled product circuit.
- Positive control: exhaustive toy fibers withheld from the router and revealed only to the verifier.
- Negative control: P1428 union-root gcd, dense resultants, source-labelled transition tables, and post-hoc root joins.
- Negative control: rho, BSGS, known-log endpoints, and fresh blind masks.

## Quantitative promotion and falsification gates

This version is merged/rejected and its retired contract must not run. A successor requires 100% source and multiplicity recall, zero false tuples, no source-labelled intermediate object, independently ranked multirow output, and formal `lambda,mu<=0.45`. A `B^3` state/degree term, one source collision, or `max(lambda,mu)>=0.50` falsifies it; values strictly between `0.45` and `0.50` are inconclusive and non-promoting.

## Artifact plan

- Prospective circuit theorem: `ideas/artifacts/ECDLP-IDEA-194/implicit_fiber_circuit_theorem.md`
- Prospective reverse-source specification: `ideas/artifacts/ECDLP-IDEA-194/reverse_hasse_source_spec.md`
- Prospective collision family: `ideas/artifacts/ECDLP-IDEA-194/jet_collision_family.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-194/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-194/cost_analysis.md`
- Retired contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-194_fiberjet_preflight.yaml`

All paths are prospective; no artifact root or run exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified algorithmic evidence. Any finite check would be toy, and every asymptotic projection is heuristic and model-bound. A correct derivative, common factor, exact relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-194/implicit_fiber_circuit_theorem.md` proving a sub-`B^2.25` endpoint circuit with exact reverse-Hasse source replay or proving that reverse ancestry forces `Omega(B^3)` represented state; do not execute the retired contract.
