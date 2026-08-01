# ECDLP-IDEA-307 — Slepian–Wolf distributed source decoder

## Status and claim labels

- Class: `distributed_coding_representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_distributed_decoder_requires_hidden_source_encoders_or_side_information`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a rate-region calculation, successful supplied-source decoder, valid relation, or toy recovery is not an ECDLP break.

## Falsifiable hypothesis

The hidden factor coordinates of a summation-polynomial relation behave as correlated distributed sources whose separately computed Slepian–Wolf syndromes, together with the public endpoint as decoder side information, identify one exact signed factor tuple with total charged rate and work below rho and BSGS for reusable relations and blind descent.

## Mechanism-new operation

The screened operation is **assign one encoder to each factor coordinate, compress it to a syndrome at a Slepian–Wolf corner point, and jointly decode exact factor points using the elliptic endpoint as correlated side information**. This differs from a generic sparse solver because the proposed gain is a distributed source-coding rate region. The coding theorem presumes that each encoder observes its realized source symbol. Here those hidden symbols are precisely the unknown tuple; computing their syndromes therefore requires first finding the tuple, enumerating candidate source decks, or supplying equivalent source incidence. Endpoint-only binning leaves the exponentially large source fiber. The proposal merges with IDEAs 014, 130, 150, 226, and 281.

## Assumptions

1. A target-uniform joint distribution for factor coordinates and endpoints is available without sampling hidden tuples at source-enumeration cost.
2. Each syndrome can be computed from public curve, factor-base, and endpoint data even though its encoder does not receive the hidden factor coordinate.
3. The endpoint supplies enough correlation for a canonical all-strata decoder returning exact signed points rather than a list or distribution.
4. Code construction, syndrome production, lists, side information, failures, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`hidden_factor_distributed_sources | Slepian_Wolf_syndrome_bins | endpoint_decoder_side_information | exact_joint_source_decode | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1472`, the two-large-prime occupancy-exponent boundary.
2. `inputs/ledger_inventory.json` — imported `P1476`, the m-ary sparse-deck conditional-exponent boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, where pair-only generation avoids advice only through cubic work.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`, the compact membership-polynomial versus translated-query tradeoff.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator and transposed join.

## Closest primary literature

- Slepian and Wolf, [Noiseless coding of correlated information sources](https://doi.org/10.1109/TIT.1973.1055037), derives distributed rate regions when separate encoders observe their actual source sequences; it does not manufacture syndromes of unobserved factors.
- Korner and Marton, [How to encode the modulo-two sum of binary sources](https://doi.org/10.1109/TIT.1979.1056022), shows structured functional compression for supplied correlated binary sources, not endpoint-only inversion of a hidden finite-field tuple.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the endpoint constraint but no distributed encoders or sub-rho joint decoder.

No checked source provides public syndromes of unobserved factor coordinates, an exact all-strata source decoder, blind descent, or the complete sub-rho cost path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, joint source model, encoder matrices, decoder, side-information map, masks, and independent verifier.
2. For random known-log endpoints, compute every coordinate syndrome without first discovering, enumerating, or receiving the hidden factor tuple.
3. Jointly decode all candidate signed factor tuples from the syndromes and endpoint, output every list entry, and independently verify each relation.
4. Collect independent verified rows, solve the complete factor-log system, and verify each recovered factor logarithm.
5. Reuse the identical encoders and decoder on fresh masked targets `Q+[t]P` without target-trained bins, codebooks, or source advice.
6. Substitute factor logs, remove masks, retain every decoder-list and sign ambiguity, and return all scalar candidates.
7. Accept only exact `[x]P=Q`, charging training samples, codebooks, syndrome production, endpoint queries, lists, failures, rows, logs, descent, verification, time, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one public-syndrome/joint-decode/verify attempt `N^q,N^q_m`, independent-rank gain `N^r`, list output `N^o`, target ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes public syndrome computation, every decoder query, exact inverse, and independent verification; `o` includes all bins, lists, and tuples returned. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Slepian–Wolf compression saves communication after encoders see correlated source samples; it is not a search algorithm for samples absent from every encoder. In the proposed ECDLP use, no public party knows the hidden factor coordinates before descent succeeds. Giving the encoders those coordinates assumes the answer, while generating all possible syndrome messages materializes the factor decks or tuple fiber. With only the elliptic sum as side information, many source tuples occupy the same endpoint bin, so exact decoding requires source-sized advice, list output, or generic search.

## Proof track

Specify public encoders that do not observe hidden factors, prove their syndromes plus the endpoint uniquely and biconditionally identify exact signed tuples on every stratum, then prove sufficient independent relations, reusable factor logs, blind descent, and `lambda,mu<=0.45` with all code and list costs charged.

## Disproof track

Prove a source-access circularity or conditional-entropy/list-size lower bound: either an encoder must observe the unknown factor, or endpoint-compatible messages leave `N^0.50`-or-larger construction, query, state, or output on the preregistered regime.

## Positive and negative controls

- Positive: supplied correlated source sequences with frozen encoders must decode at an admissible Slepian–Wolf rate and recover their exact labelled symbols.
- Negative: withholding the realized source symbols while retaining only the endpoint must not be credited with zero-cost syndrome production or exact decoding.
- Baselines: explicit factor-deck binning, sparse-list decoding, IDEAs 014/130/150/226/281, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with source-unobserving public encoders, an independent all-strata biconditional, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if syndrome production consumes a hidden factor, endpoint bins retain nontrivial source lists, or charged encoder/codebook/list cost reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-307/distributed_source_decoder_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-307/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-307/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-307/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of Slepian–Wolf decoding when the proposed encoders do not possess the hidden factor sources, not a rejection of distributed coding for supplied data. A valid rate region or successful labelled control does not yield factor relations, blind scalar descent, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-307/distributed_source_decoder_theorem.md` proving either public syndrome computation without source access and exact endpoint-conditioned decoding or the source-access/list-size obstruction before any coding experiment.
