# ECDLP-IDEA-257 — Rado matroid-intersection colourful-circuit extraction

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_independence_optimizer_does_not_locate_rare_circuit`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic, live-ledger, and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; matroid-intersection correctness, a fundamental circuit, a valid relation, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Intersecting the one-row-per-colour partition matroid with a truncation or dual of the
linear matroid represented by P1539's evaluation rows exposes a target-valid dependent
transversal as a fundamental circuit and returns its five row labels below rho and BSGS.

## Mechanism-new operation

The screened operation is **apply Rado/matroid intersection to the coloured evaluation
rows, then convert the exchange certificate of a maximal common independent set into the
rare colourful dependent transversal**.  This differs from representative-family
compression, but ordinary matroid intersection optimizes independence, not the desired
dependence predicate.  Adding a target-circuit oracle merges the proposal with
IDEA-137/157/170/212/223/235 and P1539.  Solver substitutions, parameter changes,
same-field isogenies, explicit source tables, post-hoc selectors, dense resultants, and
relation-only certificates are controls.

## Assumptions

1. A polynomial-size matroid construction converts existence of a target-valid colourful five-circuit into a common-independent-set optimum or deficiency.
2. The construction distinguishes the rare endpoint circuit even though many full-rank colourful transversals exist.
3. Its exchange/fundamental-circuit certificate maps biconditionally to exact signed factor rows without a circuit oracle.
4. Oracle queries, representation, output, rank, factor logs, blind descent, verification, and peak memory are charged.

## Semantic fingerprint

`partition_matroid_colours | endpoint_linear_matroid | Rado_intersection_deficiency | fundamental_colourful_circuit | exact_row_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-term implicit-membership requirement.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the materialized five-term state negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry boundary.
5. `inputs/ledger_inventory.json` — imported `P1480`, the bit-vector membership control.

P1539 supplies the exact linear-matroid rows and determinant predicate; it does not turn
the rare dependent transversal into an independence optimum.

## Closest primary literature

- Rado, [A theorem on independence relations](https://doi.org/10.1093/qmath/os-13.1.83), characterizes independent transversals in a supplied matroid.
- Frank, [A weighted matroid intersection algorithm](https://doi.org/10.1016/0196-6774(81)90032-8), optimizes common independent sets in supplied matroids.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), is the elliptic-relation control and supplies no matroidal dependence reduction.

These sources do not characterize a rare target-conditioned dependent transversal by an
independence optimum, construct its support, or provide factor logs and blind descent.
Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E/F_p`, prime-order `G=<P>` of size `N`, five signed colour decks of scale `B=N^beta`, matroid representations, truncation/duality rule, masks, tie rules, and verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct P1539's evaluation-row linear matroid and the alleged common-independent-set reduction without enumerating target-valid circuits.
3. Run intersection, convert the optimum/exchange certificate to every exact signed row source, replay the elliptic sum, and preserve oracle failures, multiple fundamental circuits, repeats, infinity charts, and rejected candidates.
4. Collect independently verified rows to rank `B`, charge rank loss/output, solve all factor logs, and independently verify each factor logarithm.
5. Apply the identical frozen reduction and inverse to fresh masks `Q+[t]P`, with no known-log-only basis or target-selected exchange path.
6. Substitute factor logs, subtract `t`, retain every ambiguity candidate, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents
`1/2`.  Let setup time/memory be `N^a,N^a_m`, reciprocal relation/target densities be
`N^delta,N^delta_t`, one intersection plus exact circuit inverse cost `N^q,N^q_m`,
independent-rank gain be `N^r`, source output/ambiguity be `N^o,N^u`, and factor-log
completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every rank-oracle call, exchange edge, circuit candidate, source output, rank defect,
factor log, masked descent, verifier call, bit operation, and live byte is charged.
Promotion requires both complete exponents at most `0.45`.

## Likely fatal obstruction

Rado's theorem and matroid intersection find an independent colourful transversal.  For
generic P1539 rows, many size-five colourful transversals are independent even when one
rare target-valid transversal is dependent.  Hence the optimum remains five in both the
positive and negative ECDLP cases.  A fundamental circuit appears only after a dependent
extension element and basis are selected; choosing the extension that yields the target
circuit is the original source-locator problem.  The family of desired transversals is
not itself a matroid because fixed-target dependence lacks exchange closure.

## Proof track

Give an explicit matroid lift/dual whose optimum is biconditional with the target circuit,
prove exact all-strata certificate-to-row inversion, and establish complete exponents at
most `0.45` through rank, factor logs, and blind descent.

## Disproof track

Exhibit positive and negative endpoints with identical common-independence optimum and
exchange ranks, prove the target-circuit family violates matroid exchange, or establish
that the circuit oracle/output or either complete exponent is at least `0.50`.

## Positive and negative controls

- Positive control: supplied partition and linear matroids where an independently known rank deficiency characterizes the desired transversal.
- Negative controls: generic full-rank colourful transversals plus one planted circuit, source permutations, IDEA-137, IDEA-157, IDEA-170, IDEA-212, IDEA-223, IDEA-235, P1539, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires setup/state at most `B^2.25`, intersection plus exact source output at
most `B^1.25`, a biconditional optimum with zero false sources, full factor-log rank,
blind descent, and complete lambda and mu at most `0.45`.  Identical optima across
relation/no-relation controls, a supplied circuit oracle, or an exponent at least `0.50`
falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-257/rado_colourful_circuit_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-257/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-257/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-257/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Finite checks would be
toy and extrapolations heuristic and model-bound.  A correct intersection optimum,
fundamental circuit, valid relation, recovered tuple, or toy scalar is not a generic
ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-257/rado_colourful_circuit_theorem.md` deriving a biconditional matroid reduction or proving that independence optima cannot distinguish the rare target circuit.
