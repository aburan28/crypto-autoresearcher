# ECDLP-IDEA-170 — Violator-space source basis

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_completion_oracle_backend`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: every future finite check is `toy`; all projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid violator basis, source tuple, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For each public endpoint, the signed factor-base constraints admit a target-uniform violator mapping of combinatorial dimension `m` whose bases are biconditional with exact signed `m`-source tuples. A cheap endpoint-derived violation oracle lets Clarkson sampling find every required basis without enumerating decompositions, enabling complete relations, factor-base logs, and blind masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **violator-space basis extraction using an endpoint-only violation oracle**. The removal theorem must prove consistency and locality, the basis/source biconditional on every stratum, and cheap violation from public endpoint data. A membership or decomposition oracle, supplied sources, a post-hoc basis, solver substitution, or explicit tuple table is a control.

Independent operation-level review found that the stated removal test is not met: the
violation predicate is the completion oracle already occupied by IDEA-137/168, and
Clarkson sampling begins only after that oracle is supplied. P1516's missing target-router
gate strengthens the same objection. The record is therefore retained as a merged
backend, not an active proposal.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, constraint encoding, masks, random seeds, and verifier are frozen.
2. One target-uniform violator map satisfies consistency and locality for known and masked unknown endpoints.
3. Its inclusion-minimal bases correspond exactly to all signed source tuples, including repeats, infinity, and exceptional charts.
4. Violation tests use only public constraint and endpoint data, not scalar labels, completion queries, or source ancestry.
5. Sampling, oracle calls, retries, output, rank, factor logs, descent, verification, and peak memory are charged.

## Semantic fingerprint

`endpoint_factor_constraints | target_uniform_violator_map | bounded_combinatorial_dimension | Clarkson_basis_extraction | exact_source_biconditional | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source query, rank, and descent gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, the staged generator and `B^3` boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where exact ancestry remains source-distinct.
5. `inputs/ledger_inventory.json` — imported `P1480`, the solver-change control that leaves source generation unresolved.

## Closest primary literature

- Gartner, Matousek, Rust, and Skovron, [Violator Spaces: Structure and Algorithms](https://arxiv.org/abs/cs/0606087), give the consistency/locality framework and bounded-basis sampling, not an elliptic violation oracle.
- Clarkson, [Las Vegas algorithms for linear and integer programming when the dimension is small](https://doi.org/10.1145/201019.201036), gives the randomized sampling control once a valid low-dimensional oracle exists.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives nearby endpoint relation equations but no violator/source biconditional.

No checked primary source supplies the proposed elliptic violator map and complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor constraints, violator axioms, tie-breaking, masks, sampling distribution, and complete verifier.
2. Prove consistency, locality, dimension at most `m`, and exact basis/source correspondence without enumerating tuples.
3. For known `R_j=[r_j]P`, run Clarkson sampling using only the frozen endpoint-derived violation oracle.
4. Decode every returned basis to signed factor points; preserve misses, duplicate bases, multiplicities, failures, and all output.
5. Verify tuples by elliptic addition, collect `B+sigma` independent rows of rank `B`, solve logs, and verify each factor log.
6. Apply the identical mapping and sampler to fresh `Q+[t]P` masks with no known target scalar.
7. Substitute verified factor logs, remove masks, retain every ambiguity candidate, and accept only `x` with `[x]P=Q`.
8. Charge map construction, all oracle calls, resampling, output, rank, linear algebra, descent, time, and bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal useful-relation and target densities be `N^delta,N^delta_t`; Clarkson makes `N^c` calls costing `N^v` each with basis decoding exponent `s`, so `q=max(c+v,s)`. Let `q_m` be the peak bit-memory exponent for the violation-oracle state, sampled constraint sets, and decoded bases; output and target ambiguity exponents are `o,u`; factor-log algebra costs `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every scanned constraint, oracle bit, sampled subproblem, returned basis, source tuple, and failed endpoint is included.

## Likely fatal obstruction

Testing whether a new factor constraint violates a partial set for endpoint `R` appears to ask whether that set extends to an exact decomposition of `R`, which is the original constrained source problem. Moreover, multiple unrelated decompositions of the same endpoint can make the natural extension predicate violate locality, so Clarkson's theorem may not apply even with an expensive oracle.

## Proof track

Define the ground set and violator map explicitly; prove consistency, locality, bounded dimension, an all-strata basis/source biconditional, endpoint-only oracle cost, and complete `lambda,mu<=0.45` blind descent.

## Disproof track

Reduce one violation query to source completion, exhibit `F subset G` violating locality, find a basis that loses or merges a source, expose tuple enumeration, or prove either complete exponent at least `0.5`.

## Positive and negative controls

- Published low-dimensional violator spaces with independently checkable bases and violation oracles.
- Planted toy elliptic tuples with supplied extension answers as an explicit oracle control.
- Direct source enumeration, materialized `B^2/B^3` decks, P1480 solver swaps, rho, and BSGS.
- Known-log and blind-target fixtures covering repeats, signs, infinity, collisions, and no-decomposition endpoints.

## Quantitative promotion and falsification gates

This version is merged/rejected at the missing-oracle gate. Reopening under a new ID requires a proved endpoint-only violation operation distinct from source completion, 100% all-strata source recall, zero false bases, no supplied completion bit, upper 95% `q,q_m<=0.20`, and formal `lambda,mu<=0.45`. One locality failure, lost source, oracle circularity, or exponent at least `0.5` remains falsifying.

## Artifact plan

- Prospective axiom theorem: `ideas/artifacts/ECDLP-IDEA-170/violator_axiom_theorem.md`
- Prospective oracle and source-basis specification: `ideas/artifacts/ECDLP-IDEA-170/violation_oracle_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-170/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-170/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-170/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-170_violator_space_preflight.yaml`

All research-artifact paths are prospective; the retired contract is unapproved and permits zero runs. No experiment artifact or run exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified evidence. Every finite check would be toy and every complexity claim remains heuristic and model-bound. Correct violator axioms or relation validity is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-170/violator_axiom_theorem.md` defining the endpoint extension violator map and either proving consistency/locality plus the exact source-basis biconditional or recording the first counterexample; do not implement sampling.
