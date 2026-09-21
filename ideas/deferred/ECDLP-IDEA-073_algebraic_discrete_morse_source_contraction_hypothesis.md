# ECDLP-IDEA-073 — Algebraic discrete-Morse source contraction

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `deferred_theorem_required`
- Evidence scale: `toy` chain-complex preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid chain contraction or recovered relation is not an ECDLP break.

## Falsifiable hypothesis

For fixed relation arity `m`, partial factor-base decompositions ending at a public target `R` form an implicitly evaluable chain complex `C_R`. A target-independent acyclic matching cancels nonwitness cells while preserving a critical subcomplex of `N^(gamma+o(1))` cells, `gamma<1/2`; the chain homotopy lifts each target-critical cell to exact factor-base point sources. Complete relation collection, rank, linear algebra, blind target descent, verification, and peak memory remain below the rho/BSGS boundary.

## Mechanism-new operation

The operation is **witness-preserving algebraic discrete-Morse cancellation with an explicit chain-homotopy source lift**. It changes the combinatorial state object before relation certificates exist. A generic complex reduction, sparse solver, post-hoc row selector, source-free homology class, or explicit enumeration of all `B^m` cells is a control. Credit requires an implicit matching rule, sub-rho critical-cell count, and exact source ancestry.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, with `Q=[x]P`.
2. A target-independent factor base `F` has size `B=N^beta` and complete point/sign labels.
3. Boundary maps for partial sums are computable without enumerating the full complex.
4. One public acyclic matching works for known and blind targets and preserves every valid decomposition.
5. Chain-homotopy data recovers exact sources, multiplicities, and exceptional branches.
6. Matching construction, critical output, failed targets, rank, factor-log solving, descent, and memory are fully charged.

## Semantic fingerprint

`partial_elliptic_decomposition_chain_complex | target_independent_acyclic_matching | critical_witness_cells | chain_homotopy_exact_source_lift | full_rank_and_blind_descent`

The new operation attacks the state-space/output obstruction rather than swapping the polynomial solver. If the matching is obtained by first finding witnesses, it is circular and receives no credit.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the closest exact sparse primitive whose composition becomes dense.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, the exact one-transition positive control that a contraction must compose.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the complete higher-arity exponent boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, where exact source-fiber generation and joins remain cubic.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H629`, the nearest pre-certificate source-split lane.

## Closest primary literature

- Jöllenbeck and Welker, [Resolution of the residue class field via algebraic discrete Morse theory](https://arxiv.org/abs/math/0501179), extends discrete Morse theory to free-module chain complexes but supplies no elliptic witness complex.
- Sköldberg, [Morse theory from an algebraic viewpoint](https://doi.org/10.1090/S0002-9947-05-04079-1), develops algebraic Morse complexes without a source-preserving ECDLP matching.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the nearby elliptic decomposition equations, not the proposed contraction.

No checked paper supplies this matching or descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, cell encoding, boundary signs, matching order, and exhaustive reference enumerator.
2. Build implicit cells for partial signed sums and prove `boundary^2=0` on complete charts.
3. Apply the frozen matching and verify acyclicity, witness preservation, and critical-cell/source bijection exhaustively on tiny curves.
4. Lift each critical target cell through the chain homotopy to exact factor-base indices and verify its elliptic sum.
5. Collect `B+sigma` independent rows for `R=[a]P+[b]Q`, retaining every matched/cancelled/critical state and `a,b`.
6. Solve and independently verify factor logs modulo `N`.
7. Contract complexes for masked blind targets `Q+[t]P`, lift a full factor-base decomposition, recover `x+t`, subtract `t`, and retain all candidates.
8. Verify the accepted scalar by `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let implicit setup exponent be `s`, critical-cell exponent `gamma`, per-cell matching/lift exponent `k`, reciprocal relation/target densities `N^delta,N^delta_t`, factor-base exponent `beta`, output exponent `o`, linear algebra `ell>=2beta` absent proved structure, and memory exponent `mu`. The full exponent is

`lambda=max(s, beta+delta+gamma+k+o, ell, delta_t+gamma+k+o, beta)`.

The full complex size, matching proof, chain-homotopy ancestry, rejected cells, and `N^beta` required rows cannot be amortized away.

## Likely fatal obstruction

The natural complex has `Theta(B^m)` cells. For every complete tuple there is some target equal to its sum, so a universal target-independent matching that preserves every target witness may have to retain every tuple cell. A matching that instead queries reachability to the current target can be the missing source oracle. Homology preservation also does not preserve individual source ancestry: one critical class can aggregate exponentially many paths, and lifting it can branch through the entire cancelled complex.

## Proof track

Define the implicit complex and local matching; prove acyclicity, witness preservation, exact source lift, and bounds `gamma,k,o,mu<1/2`; then prove complete relation, rank, descent, and verification costs below rho.

## Disproof track

Show target-independent matchings leave `N^(1/2)` critical/lift states, that witness preservation requires a target oracle, or that chain-homotopy lifting loses sources or expands to the enumerated complex.

## Positive and negative controls

- Published monomial-resolution complexes with known Morse reductions.
- Planted small decomposition complexes with unique and multiple witnesses.
- Random acyclic matchings matched for cell count.
- Witness-blind local matchings and a forbidden oracle matching.
- Exhaustive tuple/source truth on ordinary toy curves.
- Blind masked targets and matched rho/BSGS runs.

## Quantitative promotion and falsification gates

Phase 1 requires zero boundary, acyclicity, witness, or source-lift errors over all cells on 20 curves at each of three toy sizes. Phase 2 requires at least 1,000 independent verified rows and 100 blind descents at each of two largest sizes. Promotion requires upper 95% `gamma<=0.20`, `lambda<=0.45`, `mu<=0.45`, and stable leave-largest-size-out fits. Falsify after an independently reproduced source error or lower 95% `lambda>=0.50` for every complete arm.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-073_discrete_morse_preflight.yaml`
- Complex specification: `ideas/artifacts/ECDLP-IDEA-073/chain_complex.md`
- Implementation: `ideas/artifacts/ECDLP-IDEA-073/morse_contraction.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-073/verify_chain_sources.py`
- Runs: `ideas/artifacts/ECDLP-IDEA-073/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-073/analysis.md`

## Interpretation boundary

This proposal is toy, heuristic, model-bound, and novelty-unverified. Small homology, a valid critical cell, or a recovered toy relation is not a performance result or breakthrough.

## Exactly one next executable action

1. Derive `ideas/artifacts/ECDLP-IDEA-073/universal_matching_theorem.md` defining the chain groups and boundary and either proving a target-independent source-preserving acyclic matching with sub-rho critical/output bounds or proving the universal-target obstruction.
