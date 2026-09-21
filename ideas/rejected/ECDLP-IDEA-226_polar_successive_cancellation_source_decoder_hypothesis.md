# ECDLP-IDEA-226 — Polar successive-cancellation source decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_bit_channels_require_the_missing_source_marginals`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; channel polarization, a decoded planted word, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

The signed source variables of an endpoint relation define public synthetic bit channels that polarize under a fixed transform. Exact endpoint likelihoods on the reliable channels would allow successive cancellation to recover every factor point, producing relation rows and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **elliptic source-channel synthesis followed by successive-cancellation point decoding**. It merges/rejects because polarization reorganizes supplied channel observations; it does not create likelihoods or syndromes. Computing an endpoint-conditioned bit likelihood marginalizes the same exponential source fiber, and a decoder trained on known sources is a selector/backend control.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, source encoding, kernel, and frozen-bit rule are target-independent.
2. Exact bit-channel likelihoods are computable without source enumeration, oracle labels, post-hoc training, or dense summation-polynomial elimination.
3. Successive cancellation returns every exact signed point, including repeats and ambiguous branches, with no hidden side information.
4. Channel construction, likelihoods, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_source_variables | endpoint_conditioned_synthetic_channels | polar_transform | successive_cancellation_exact_points | factor_logs | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the endpoint source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact-source predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the source-generator boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the dense serial source-state negative.
5. `inputs/ledger_inventory.json` — imported `P1480`, the structured bit-vector membership control.

## Closest primary literature

- Arıkan, [Channel polarization](https://arxiv.org/abs/0807.3917), constructs reliable synthetic channels from repeated uses of a supplied memoryless channel.
- Şaşoğlu, Telatar, and Arıkan, [Polarization for arbitrary discrete memoryless channels](https://arxiv.org/abs/0908.0302), extends the method to finite input alphabets.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint constraints but not cheaply evaluable source marginals.

No checked source derives the required elliptic channel observations. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the source encoding, polar kernel, bit-channel order, likelihood evaluator, masks, and verifier.
2. For known endpoints, synthesize exact channel observations without enumerating sources and decode all candidate signed tuples.
3. Independently verify every elliptic relation and retain all ambiguous SC paths rather than only a best guess.
4. Collect full rank, solve and verify factor-base logarithms.
5. Apply the same channel/decoder to fresh `Q+[t]P`, substitute factor logs, and subtract `t`.
6. Accept only `[x]P=Q`, charging likelihood evaluation, list size, output, rank, descent, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, likelihood plus complete SC inverse `N^q,N^q_m`, rank gain `N^r`, list output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All marginal sums, frozen-channel design, lists, and source outputs are charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

There is no natural independent memoryless channel emitting noisy views of the hidden factor tuple. Exact endpoint-conditioned likelihoods are partition functions over source completions, so their computation is the original point-decomposition task. Approximate/trained likelihoods can miss rare branches and cannot support exact all-source relation accounting or blind descent.

## Proof track

Derive algebraic bit-channel likelihood recurrences with exact all-source SC/list decoding and complete `lambda,mu<=0.45`.

## Disproof track

Reduce a likelihood to source-fiber summation, show polarization reliability is absent or target-dependent, exhibit a missed source branch, or derive list/state exponent at least `0.50`.

## Positive and negative controls

- Positive control: a genuine memoryless channel with planted polar codewords and exact likelihoods.
- Negative controls: shuffled likelihoods, endpoint-blind random channels, IDEA-130/132/146/149/150/158, P1480, post-hoc classifiers, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a proved source-free likelihood recurrence, 100% all-list source recall, zero false tuples, no target-trained frozen set, and `lambda,mu<=0.45`. Source marginal enumeration, a missed branch, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-226/polar_likelihood_recurrence.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-226/channel_source_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-226/independent_polar_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-226/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected algorithm analysis. Finite checks would be toy and projections heuristic and model-bound. Polarization, successful decoding on supplied likelihoods, a relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-226/polar_likelihood_recurrence.md` deriving endpoint likelihoods without source marginalization or proving that one synthetic channel already requires the occupied decomposition oracle.
