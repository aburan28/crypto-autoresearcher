# ECDLP-IDEA-246 — Kostant adjoint-quotient sheet section

## Status and claim labels

- Class: `invariant_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_adjoint_quotient_forgets_orbit_point_labels`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A coregular Lie-algebra representation encodes each factor tuple as a regular element whose Chevalley invariants equal the public endpoint.  A Kostant section and simultaneous-resolution sheet would then choose a canonical representative and return exact factor points below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode the relation fiber in an adjoint quotient, apply a Kostant section, and lift through simultaneous resolution to point-labelled eigenvalue sheets**.  This is more structured than an arbitrary invariant ring, but it collides with IDEA-075's coregular-orbit section and IDEA-214's Jordan/Peirce atomization.  A Kostant section chooses one regular orbit representative for supplied invariant values; it does not invert a many-source elliptic fiber to its original point labels.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. The representation, invariant map, and endpoint embedding are public and compact without one weight/eigenvalue per source tuple.
2. Regular and singular fibers admit a canonical rational simultaneous-resolution sheet over the prime field.
3. The sheet coordinates invert biconditionally to every signed factor point with bounded ambiguity.
4. Embedding, invariant evaluation, section, Weyl sheets, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_relation_invariants | chevalley_adjoint_quotient | kostant_section | simultaneous_resolution_sheet | exact_factor_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H396`, the nonlinear representation-constraint frontier.
2. `inputs/ledger_inventory.json` — imported `ECFG-H397`, the quotient-module invariant frontier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H465`, the quotient/rational identity source-generator frontier.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full nonlinear-feature rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1479`, the public feature/factor-log compression control.

## Closest primary literature

- Kostant, Lie group representations on polynomial rings, [https://doi.org/10.2307/2373130](https://doi.org/10.2307/2373130), constructs the adjoint quotient and section for supplied Lie-algebra invariants.
- Donagi, Spectral covers, [https://arxiv.org/abs/alg-geom/9505009](https://arxiv.org/abs/alg-geom/9505009), develops cameral and spectral sheets for supplied invariant data but retains Weyl ambiguity.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies neighboring elliptic equations, not the claimed coregular embedding.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the endpoint-conditioned regular element or invariant vector without enumerating the source orbit or attaching point-labelled weights.
3. Apply the frozen section, enumerate rational simultaneous-resolution sheets, map every sheet coordinate to signed factor points, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and source inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected parameter, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by source ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every constructor coefficient, represented state, preprocessing query, failed target, branch,
source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation,
and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness
or relation validity alone has no performance meaning.

## Likely fatal obstruction

Adjoint invariants identify conjugacy classes and the Kostant section selects a canonical representative, not the original eigenbasis or labelled eigenvalues.  Encoding factor points as weights/eigenlines supplies the source dictionary; removing labels leaves Weyl ambiguity and aggregate invariants, while singular resolution fibers can grow.

## Proof track

Give a compact elliptic-to-coregular embedding, prove a canonical all-strata rational sheet-to-point inverse, and derive complete exponents at most 0.45.

## Disproof track

Exhibit distinct factor tuples with the same invariant/section data, reduce the embedding to a source-labelled eigenvalue table, or prove Weyl-sheet/output/state or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied regular semisimple matrices with known invariants, Kostant representatives, and independently labelled eigenvalues.
- Negative controls: Weyl permutations, singular equal-invariant fibers, IDEA-075, IDEA-099, IDEA-214, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only coregular embedding and canonical exact point-sheet inverse, zero label leakage, all-strata recall, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  Supplied eigenvalues, Weyl ambiguity, orbit-only correctness, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-246/kostant_source_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-246/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-246/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-246/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-246/kostant_source_section_theorem.md` proving a canonical endpoint-invariant-to-point sheet section or an orbit-invariant/source-label obstruction.
