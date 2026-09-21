# ECDLP-IDEA-340 — Balog–Szemerédi–Gowers energy source chart

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_small_doubling_chart_is_trivial_or_requires_source_collision_deck`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; excess additive energy or a small-doubling subset is not an ECDLP break.

## Falsifiable hypothesis

If a public elliptic factor deck has reproducible collision energy above matched random controls, a constructive Balog–Szemerédi–Gowers extraction yields a target-independent small-doubling subdeck with a public chart that increases exact decomposition density enough for complete sub-rho relation collection and blind descent.

## Mechanism-new operation

The screened operation is **convert excess additive energy into a large small-doubling subdeck, then coordinatize that subdeck for reusable exact source decomposition**. The BSG operation is known; only this ECDLP adaptation is novelty-unverified. It is not merely measuring collisions. On a prime-order elliptic subgroup, Freiman-type structure is the direct owner: without a new curve-visible chart, the subset is progression-like only in the hidden scalar coordinate and merges directly with IDEA-027 plus the occupancy/birthday controls.

## Assumptions

1. Excess energy is target-independent, survives held-out curves, and is not caused by duplicate or sign symmetries.
2. The extraction is constructive from public point operations without pair-table enumeration.
3. The small-doubling chart is evaluable and invertible without discrete logarithms.
4. The extracted subdeck improves relation and target density after its reduced size and rank are charged.
5. Energy measurement, extraction, charting, output, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`public_factor_deck_collision_energy | BSG_small_doubling_extraction | public_Freiman_source_chart | enriched_exact_decomposition | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H673`, the prospective additive-energy enrichment hypothesis.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`, the measured negative that found no prospective high-energy promotion.
3. `inputs/ledger_inventory.json` — imported `P1472`, the exact two-large-prime exponent boundary.
4. `inputs/ledger_inventory.json` — imported `P1476`, the conditional m-ary support/query gate.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-043`, where natural Abel–Jacobi completion labels match random controls.

## Closest primary literature

- Balog and Szemerédi, [A statistical theorem of set addition](https://doi.org/10.1007/BF01212974), converts dense additive relations into structured subsets but presumes access to the relation graph.
- Gowers, [A new proof of Szemerédi's theorem for arithmetic progressions of length four](https://doi.org/10.1007/s000390050065), provides the quantitative BSG form used as a structural control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide a public small-doubling chart or exact source locator.

No checked source produces the required prime-field elliptic chart and full descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve family, factor deck, energy statistic, extraction rule, chart, masks, and verifier.
2. Measure energy on known-log public points against sign, duplicate, random, and relabelled controls.
3. Extract and chart a target-independent subdeck without enumerating its collision graph.
4. Recover and verify exact known-log relations, then collect at least the subdeck rank and solve all needed logs.
5. Apply the same chart to fresh scalar-blind masked targets and preserve every miss.
6. Substitute logs, remove masks, map sources back to the original curve, and verify `[x]P=Q`.
7. Charge discarded points, density, rank, output, preprocessing, verification, time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, define ordinary additive energy `E(A)=|{(a,b,c,d) in A^4:a+b=c+d}|`, so `E(A)<=B^3`. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, chart query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Energy sampling, relation-graph access, extraction, chart evaluation, lost rank, and output are charged; `0<=r<=o`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires all complete exponents at most `0.45`; `B^2` one-time work is not independently fatal if the complete gates still hold.

## Likely fatal obstruction

In a prime-order cyclic group, a genuine small-doubling subset is controlled by scalar progressions, but exposing that chart publicly is the DLP orientation problem. Constructive BSG also consumes the dense relation graph that the ECDLP algorithm is trying to avoid. Measured elliptic collision energy to date is hash-like after matched controls, and shrinking the deck can erase any density gain.

## Proof track

For a preregistered `epsilon>0`, prove held-out `E(A)>=B^(2+epsilon)` or an equivalent stated `B^3/K` enrichment against matched controls, give a public extraction and DLP-free exact chart, and show the charged density/rank/log/descent model has `lambda,mu<=0.45`.

## Disproof track

Match energy with random controls, reduce any public chart to a hidden scalar progression, exceed `B^(9/4)` setup or `B^(5/4)` fresh-query work after graph access, or show the reduced deck restores exponent at least `0.50`.

## Positive and negative controls

- Positive: known-coordinate cyclic progressions with planted energy must be extracted and inverted.
- Negative: random, sign-closed, duplicated, and source-permuted decks must not show chart advantage.
- Baselines: IDEA-027, IDEAS 057/104/134/200, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with preregistered held-out ordinary energy at least `B^(2+epsilon)` for a fixed stated `epsilon>0` (or a stated equivalent `B^3/K` gate), a public chart with zero source errors, 1,000 ranked rows, 100 blind descents, and complete exponents at most `0.45`.
- Falsify if matched controls explain the energy, charting needs scalar labels, charged setup exceeds `B^(9/4)`, fresh query exceeds `B^(5/4)`, rank loss cancels enrichment, or either exponent reaches `0.50`.
- Energy alone is a measurement control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-340/energy_control_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-340/public_chart_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-340/extraction_cost_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-340/cost_analysis.md`

## Interpretation boundary

This rejects the unsupplied public BSG chart, not the BSG theorem or all structured factor bases. All finite evidence would be toy, heuristic, model-bound, and novelty-unverified. Excess energy or correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-340/energy_control_receipt.md` specifying the public energy oracle and matched controls while charging every accessed collision edge.
