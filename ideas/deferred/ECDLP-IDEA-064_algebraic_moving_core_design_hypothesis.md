# ECDLP-IDEA-064 — Algebraic moving-core design

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `deferred_missing_realization_theorem`
- Evidence scale: `toy` combinatorial derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low-overlap block design or full-rank toy matrix is not an ECDLP break.

## Falsifiable hypothesis

There is an explicit finite-geometry design of Hesse/cover parameter cores with bounded
pairwise overlap and a nonzero universal rank minor such that every design block creates
actual source rows before certificate materialization. The resulting relation family has
linear fresh-rank growth, source/query cost below the ledger's moving-core floor, complete
factor-log calibration and masked target descent, and full exponents below `1/2`.

## Mechanism-new operation

The proposed operation is an **algebraically realized limited-intersection core design**.
Polynomial-evaluation blocks would be mapped into cover pencils so their combinatorial
intersection bound becomes a theorem about source-divisor overlap and a specified matrix
minor. It is a generator, not a scheduler over observed rows.

A learned ordering, fixed-core retuning, deletion of dependent rows, or an abstract block
design with no cover/source realization is a duplicate/control.

## Assumptions

1. `E/F_p` has a prime-order subgroup `<P>` of order `N` and a public target-independent cover/factor base.
2. Design blocks are fixed from public curve data before any relation or target outcome.
3. Each block maps to valid cover parameters and returns complete source witnesses.
4. Bounded set intersection implies a proved nonzero rank minor over the actual coefficient field.
5. Block generation, misses, output, large-prime state, rank, calibration, descent, verification, and memory are charged.
6. No post-event feature, target-specific design, or explicit relation table is permitted.
7. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`finite_geometry_limited_intersection_design | algebraic_cover_core_realization | pre_event_source_rows | universal_nonzero_rank_minor | bounded_overlap_fresh_rank | blind_descent`

The missing operation is the realization theorem connecting design incidence to actual
cover sources and rank. Without it, this is only another schedule.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-18`, the closest targeted low-term source-form generator question.
2. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-20`, the closest public motif generator question.
3. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-21`, which requires constructive source algebra rather than selector correlations.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-041`, the verified moving-core source/rank transfer cost boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H633`, the closest fresh-rank/density control for structured blocks.

## Closest primary literature

- Guruswami and Kopparty, [Explicit subspace designs](https://doi.org/10.1007/s00493-014-3169-1), proves limited-intersection subspace families but no elliptic source realization.
- Dvir and Lovett, [Subspace evasive sets](https://arxiv.org/abs/1110.5696), supplies nearby algebraic limited-intersection constructions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the nearby relation variety but not a design-to-source theorem.

No source connects these designs to Hesse/cover relation rank or ECDLP descent; novelty
and applicability remain unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, cover/Hesse pencil, factor base, and polynomial-evaluation design.
2. Map every design block to public cover parameters before relation generation.
3. Produce all source rows from each block and verify them independently.
4. Check the universal minor and measure fresh rank without deleting failed blocks.
5. Continue until the factor-base/large-prime matrix calibrates all required logs.
6. Verify every calibrated log on the curve.
7. Apply the same design to randomized `Q+[t]P` and complete source-resolving descent.
8. Remove `t` and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let block count `N^b`, per-block source cost `N^kappa`,
usable-row density `N^-delta`, independent-rank fraction `N^-r`, factor-base size
`N^beta`, target density `N^-delta_t`, and memory `N^mu`. Then relation exponent is
`max(b,beta)+kappa+delta+r` unless blocks stream and stop after emitting the required
`N^beta` accepted rows under a preregistered rule; the complete exponent is
`lambda=max(max(b,beta)+kappa+delta+r,2beta,delta_t+kappa,mu)`. Design
construction and coefficient output are included. A constant-factor rank improvement is
not an exponent improvement.

## Likely fatal obstruction

Combinatorial block overlap need not control rank of elliptic relation coefficients.
Realizable cover cores may occupy a tiny subfamily, and enforcing the design can lower
hit density by exactly the fresh-rank gain. A universal nonzero minor can also certify
only relation rank while large-prime state and target descent remain dominant.

## Proof track

Construct the explicit design, prove every block has a source-realizing cover section,
derive a nonzero rank minor and density law, and bound all relation/descent costs below rho.

## Disproof track

Show the design cannot be realized by the cover pencil, the universal minor vanishes,
fresh-rank and hit density cancel, or complete `lambda>=1/2`.

## Positive and negative controls

- Positive design control: verify intersection parameters of the abstract construction.
- Positive source control: a planted cover family realizing all blocks on tiny curves.
- Negative structure control: random blocks with matched size and coverage.
- Negative scheduler control: reorder a fixed row pool without changing its contents.
- Leakage control: forbid scored outcomes, target-specific blocks, and post-hoc row deletion.

## Quantitative promotion and falsification gates

Deferral lifts only after a symbolic realization theorem proves every block/source map and
a generically nonzero rank minor. A future preflight would require zero source errors,
fresh rank at least `0.8` per accepted row, 1,000 relations, 100 blind descents, and upper
95% `lambda,mu<=0.45`. Falsify if the minor is identically zero, realized-block density
falls with lower 95% exponent canceling rank, or lower 95% `lambda>=0.50`.

## Artifact plan

- Missing theorem: `ideas/artifacts/ECDLP-IDEA-064/core_realization_theorem.md`
- Design data: `ideas/artifacts/ECDLP-IDEA-064/design.yaml`
- Symbolic mapper: `ideas/artifacts/ECDLP-IDEA-064/core_mapper.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-064/verify_sources_and_rank.sage`
- Future runs: `ideas/artifacts/ECDLP-IDEA-064/runs/<run-id>/`
- Retain all blocks, maps, sources, misses, minors, ranks, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This deferred record is toy, heuristic, model-bound, and novelty-unverified. A correct
design or full-rank toy matrix is not a breakthrough and cannot bypass complete descent.

## Exactly one next executable action

1. Derive the block-to-cover source realization and universal-minor proof in `ideas/artifacts/ECDLP-IDEA-064/core_realization_theorem.md` before creating a contract.
