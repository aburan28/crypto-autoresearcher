# ECDLP-IDEA-256 — Algebraic-matroid circuit-polynomial source lift

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_circuit_polynomial_requires_unknown_source_support`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic, live-ledger, and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a circuit polynomial, derivative, source tuple, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The algebraic matroid of P1539's coloured elliptic-normal-curve evaluation rows admits an
endpoint-derived circuit polynomial whose support and partial derivatives expose one
target-valid colourful five-row circuit without enumerating candidate supports, enabling
complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **derive the minimal algebraic circuit polynomial of the
endpoint row matroid and use its variable derivatives to identify the exact five source
rows**.  Circuit polynomials are more structured than a generic determinant call, but
known algorithms begin with the circuit support and ideal.  Once unknown-support search
and source variables are charged, the proposal merges with IDEA-052/137/156/201/215 and
P1539.  Solver swaps, parameter changes, same-field isogenies, explicit source tables,
post-hoc selectors, dense resultants, and relation-only certificates are controls.

## Assumptions

1. The endpoint row family has a compact algebraic-matroid presentation whose target-valid five-circuits are distinguished from all other dependencies.
2. One circuit polynomial is computable without first choosing its five row variables or constructing the full relation ideal.
3. Its derivatives recover exact signed rows on simple and nonreduced strata without a source-labelled polynomial dictionary.
4. Polynomial construction, support recovery, output, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`elliptic_evaluation_algebraic_matroid | unknown_colourful_circuit_polynomial | derivative_support_recovery | exact_signed_rows | factor_logs | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the coordinate-predicate source-resolution hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic source-fibre generator hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact identity/dense-composition control.

P1539 is the closer live control: its five-row determinant is already the circuit
predicate once a support is supplied; the missing operation is support location.

## Closest primary literature

- Király, Rosen, and Theran, [Algebraic matroids with graph symmetry](https://arxiv.org/abs/1312.3777), defines circuit polynomials for supplied algebraic-matroid circuits.
- Malić and Streinu, [Computing Circuit Polynomials in the Algebraic Rigidity Matroid](https://arxiv.org/abs/2304.12435), computes such polynomials from known supports and construction trees using elimination.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the elliptic relation equations but no unknown-circuit locator.

These sources do not derive a circuit support from one elliptic endpoint, compress all
candidate supports, or supply factor-log and blind-target descent.  Novelty remains
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E/F_p`, prime-order `G=<P>` of size `N`, five signed colour decks of scale `B=N^beta`, row variables, matroid presentation, masks, tie rules, and verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the compact endpoint algebraic matroid and its circuit-polynomial interface without listing five-row supports or materializing the source-fibre ideal.
3. Compute the unknown circuit polynomial, use derivatives to recover every exact signed row, replay its elliptic sum, and preserve support collisions, multiplicities, derivative zeros, repeats, infinity charts, and rejected candidates.
4. Collect independently verified rows to rank `B`, charge rank loss and output, solve all factor logs, and independently verify each factor logarithm.
5. Apply the identical frozen matroid and circuit procedure to fresh masks `Q+[t]P`, with no known-log-only support hint or target-selected variable set.
6. Substitute factor logs, subtract `t`, retain every ambiguity candidate, and accept only `x` satisfying `[x]P=Q`; record complete time and peak memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents
`1/2`.  Let setup time/memory be `N^a,N^a_m`, reciprocal relation/target densities be
`N^delta,N^delta_t`, one circuit construction plus exact support inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, output/ambiguity be `N^o,N^u`, and
factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every circuit variable, elimination node, factor, derivative, support candidate, rank
defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.
Promotion requires both complete exponents at most `0.45`.

## Likely fatal obstruction

A circuit polynomial is attached to a specified minimal dependent coordinate set.  Its
variables already name that support, and derivative recovery returns information about
those supplied variables.  P1539 already provides the determinant polynomial for any
supplied five rows.  Searching the algebraic matroid for the rare colourful target-valid
circuit, or constructing a global polynomial containing every such circuit, reinstates
the `B^5` support deck or a dense elimination object.

## Proof track

Give an endpoint-only circuit-polynomial constructor that never receives the support,
prove exact all-strata row recovery, and establish full rank, blind descent, and complete
exponents at most `0.45`.

## Disproof track

Reduce every circuit-polynomial call to a support/ideal oracle, prove global coefficient
traffic is source-deck sized, exhibit different supports with indistinguishable aggregate
derivatives, or establish either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied rigidity circuit with independently known ideal, support, circuit polynomial, and derivative labels.
- Negative controls: hidden support permutations, unions of circuits, IDEA-052, IDEA-137, IDEA-156, IDEA-201, IDEA-215, P1539, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires support-blind setup/state at most `B^2.25`, circuit construction plus
exact source output at most `B^1.25`, zero false rows, full rank, blind descent, and
complete lambda and mu at most `0.45`.  Receiving the support or full fibre ideal,
enumerating `B^3` partial supports, or an exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-256/circuit_polynomial_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-256/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-256/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-256/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Finite checks would be
toy and extrapolations heuristic and model-bound.  A correct circuit polynomial,
derivative, source tuple, valid relation, or toy scalar is not a generic ECDLP algorithm,
crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-256/circuit_polynomial_source_theorem.md` deriving a support-blind circuit constructor or proving that circuit variables and coefficients materialize the missing source deck.
