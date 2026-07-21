# ECDLP-IDEA-349 — Constructive vector-discrepancy source rounding

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_real_discrepancy_rounding_has_no_exact_finite_field_correction`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired review_required preflight; execution prohibited`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; low real discrepancy or a correct rounded toy relation is not an ECDLP break.

## Falsifiable hypothesis

A public fractional decomposition of endpoint contributions can be constructively rounded by vector-discrepancy methods to a sparse integral source selection, after which a bounded exact finite-field correction returns every relation tuple within the P1553 bounds.

## Mechanism-new operation

The screened operation is **embed fractional endpoint contributions as a supplied set-system/vector instance, apply a Bansal-style SDP-guided constructive coloring, and correct the bounded residual exactly in the curve group**. It is distinct only if the public encoding preserves source provenance and the exact correction is sub-gate. Otherwise it is approximate real balancing followed by the original hidden completion problem.

## Assumptions

1. Fractional endpoint weights and low-dimensional real vectors are computed without enumerating source tuples or knowing scalar labels.
2. Small discrepancy in the public vectors implies a bounded exact residual in every finite-field and curve-group constraint.
3. The correction returns replayable factor-base sources without rho, BSGS, or a supplied DLP oracle.
4. Rounding covers signs, multiplicities, overlaps, singularities, infinity, ambiguity, and target updates.
5. Encoding, rounding, correction, output, rank, logs, blind descent, precision, and memory are charged.

## Semantic fingerprint

`fractional_endpoint_decomposition | public_low_dimensional_evaluation_vectors | Bansal_vector_discrepancy_rounding | bounded_exact_residual_correction | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the target-independent public encoding requirement.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the exact correction and source-replay obligation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the unresolved nonlinear full-phase composition boundary.
5. `inputs/ledger_inventory.json` — imported `P1479`, where approximate public features do not recover exact hidden witnesses.

## Closest primary literature

- Bansal, [Constructive algorithms for discrepancy minimization](https://doi.org/10.1109/FOCS.2010.7), gives an SDP-guided constructive discrepancy algorithm for supplied set systems; it is not a general rounding theorem for arbitrary public vector encodings and does not make approximate real balance into exact finite-field equality with sources.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides exact finite-field endpoint equations but no compatible low-dimensional real encoding or correction oracle.

No checked source supplies the exact public bridge and correction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, fractional decomposition, vector encoding, rounding seed, exact correction, and verifier.
2. Construct public fractional systems for known-log relation collection without enumerating source tuples.
3. Round, exactly correct the residual, replay every recovered tuple, and verify each relation.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the identical encoding, rounding, and correction to fresh scalar-blind masked targets.
6. Substitute factor logs, remove masks, retain all correction alternatives, and verify `[x]P=Q`.
7. Charge vector construction, numerical precision, rounding, correction, output, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, rounding and correction excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every vector coordinate, precision bit, rounding branch, residual candidate, output tuple, and bit of state is charged; `0<=r<=o`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires complete exponents at most `0.45`.

## Likely fatal obstruction

Vector discrepancy bounds an approximate real norm. Elliptic relation equations are exact over a finite field and the curve group, with no known public homomorphic low-dimensional real encoding. A small real residual need not correspond to a small finite-field correction. Solving that exact correction is the hidden completion problem and can restore tuple enumeration, rho, or DLP-scale work.

## Proof track

Construct the public homomorphic encoding, prove a discrepancy-to-exact-correction theorem for every stratum, give a source-replaying correction algorithm, and derive complete `lambda,mu<=0.45`.

## Disproof track

Exhibit equal public vectors with different exact group residuals, prove correction solves a generic completion or DLP instance, find a precision or wraparound failure, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: explicit integer lattices with supplied homomorphic embeddings and planted bounded corrections must round and replay correctly.
- Negative: finite-field instances with identical real embeddings but different exact residues, wraparound pairs, and source-permuted fractional systems must not yield preferred sources.
- Baselines: direct owners IDEAs 332/335/328/143/057, randomized rounding, lattice correction, P1553 contractions, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an exact public encoding theorem, zero all-strata correction errors, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one equal-embedding/different-residual pair, one rho/DLP correction, source-sized precision or state, or either exponent at least `0.50`.
- Low discrepancy, numerical agreement, or a valid toy relation is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-349/vector_encoding_and_correction_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-349/wraparound_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-349/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-349/cost_analysis.md`

## Interpretation boundary

This rejects the proposed exact discrepancy bridge, not constructive discrepancy theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Low discrepancy or correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-349/vector_encoding_and_correction_obligations.md` and test whether any proposed public coordinate map preserves exact addition modulo the curve order.
