# Pre-ID duplicate draft — Davis–Putnam source-resolution elimination

## Status and claim labels

- Prospect: `20260722-a-N02`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / conservative / secondary screen.
- State: `merged_rejected_supplied_cnf_resolution_and_model_reconstruction`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a resolution certificate or valid tuple is not an ECDLP result.

## Falsifiable hypothesis

Public elliptic endpoints admit a compact CNF whose models are exactly signed five-source relations. Davis–Putnam variable elimination can resolve away internal variables under arbitrary restrictions, decide target-fibre nonemptiness, and reconstruct one occurrence-labelled model often enough for full factor logs and 100 fresh blind descents below rho and BSGS.

## Mechanism-new operation

The screened operation eliminates a Boolean variable by resolving every positive clause against every negative clause and deleting clauses containing that variable, while retaining enough parent data to reconstruct a model. It counts only if the CNF is endpoint-derived and compact, resolvent growth stays sub-rho, and reconstruction returns signed source occurrences.

## Assumptions

1. The all-strata elliptic relation has a uniform endpoint-only CNF within the setup cap.
2. Variable elimination order keeps width and resolvent count inside the online caps for every restriction.
3. Satisfiability is exact over the finite field and cannot be changed by encoding collisions.
4. Model-reconstruction pointers preserve occurrence labels and signs at charged cost.
5. Target-independent clauses and elimination order are reusable for masked targets.

## Semantic fingerprint

`public_endpoint_relation_CNF | Davis_Putnam_resolution_elimination | exact_restricted_SAT | labelled_model_reconstruction | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact decision plus source replay is the controlling interface.
2. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — bounded symbolic states can hide completion/source distinctions.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — compilation width and source inversion are already charged.
4. `ideas/rejected/ECDLP-IDEA-141_unambiguous_rectangle_source_factorization_hypothesis.md` — compact Boolean rectangles do not arise for free from endpoints.
5. `inputs/idea_generation_20260719_batch11.md` — an adjacent proof-complexity control records resolution-width barriers for a large-prime enrichment CNF; it does not directly own model-reconstructing Davis-Putnam elimination.

## Closest primary literature

- Davis and Putnam, [A Computing Procedure for Quantification Theory](https://doi.org/10.1145/321033.321034), supplies resolution-based elimination for a supplied logical formula, not an elliptic CNF compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint polynomials but no bounded-width source-faithful CNF.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic-cost control.

No checked primary source constructs the required ECDLP encoding or model inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base, signed decks, exceptional strata, Boolean encoding, elimination order, restriction variables, reconstruction log, and independent verifier.
2. Compile only target-independent clauses/state within `B^(9/4+o(1))`; forbid source enumeration, target-fitted encodings, discrete-log labels, dense resultants, and Query2P1 calls.
3. For known-log `R`, instantiate endpoint clauses, perform exact restricted elimination, reconstruct actual `(A_i,epsilon_i)`, and verify `sum epsilon_i A_i=R` before retaining a row.
4. Collect at least `max(d_FB+32,1000)` verified rows for actual `d_FB`, retain failures/dependencies, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical target-independent clauses for fresh `R=Q+[t]P`, reconstruct and verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 targets.
6. Charge clause compilation, all resolvents, tautology/subsumption checks, restrictions, reconstruction pointers, failed runs, verification, rank, linear algebra, blind descent, bit complexity, and peak live memory.

## Full rho/BSGS cost model

Freeze `beta=1/5` for `B=N^beta`. With setup/state `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, ambiguity/amplification `N^u`, and factor-log costs `N^ell,N^ell_m`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain exponent `0.50`. Every literal occurrence, resolvent, parent pointer, and bit operation is charged.

## Likely fatal obstruction

Davis–Putnam starts after a complete CNF is supplied. A faithful CNF has occurrence variables or clauses encoding the source catalogue, while eliminating them creates resolvents exponential in induced width. A satisfiability certificate alone does not replay a tuple; retaining reconstruction parents restores the source traffic. This is a solver substitution for the existing endpoint predicate, not a new mathematical operation removing it.

## Proof track

Construct a target-uniform bounded-width CNF directly from public endpoints and prove bounded resolvent growth, exact all-strata semantics, occurrence reconstruction, and complete sub-rho costs.

## Disproof track

Trace one clause to explicit source incidence, prove width/resolvent/state cap failure, give equal residual formulas with different occurrence models, or show model reconstruction/complete descent reaches exponent `0.50`.

## Positive and negative controls

- Positive: a supplied bounded-treewidth toy CNF with a unique labelled model.
- Negative: empty/singleton fibres, formulas with resolvent explosion, equisatisfiable encodings with different source models, repeated occurrences, and blind targets.
- Baselines: the five anchors, direct SAT/DPLL, dense elimination, P1553 R4, rho, and BSGS.
- Controls are toy and model-bound; resolution validity is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only on zero errors at four frozen sizes, exact restriction semantics, charged labelled reconstruction, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied clause catalogue, encoding collision, missing model source, width/cap breach, or complete exponent at least `0.50`.
- Correct clauses, a SAT answer, or validator success never establishes a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n02_cnf_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n02_resolution_width_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n02_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This is a scoped rejection of the transplant, not Davis–Putnam resolution. Claims remain toy, heuristic, model-bound, and novelty-unverified. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the CNF-origin audit and measure the first unavoidable source-incidence clause or width explosion symbolically.
