# Pre-ID duplicate draft — PinSketch endpoint-syndrome decoder

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O03`; no canonical ID allocated.
- Disposition: `merged_rejected_without_endpoint_to_syndrome_homomorphism`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`, `theorem-gated`.
- Breakthrough claim: none; exact BCH decoding or a valid relation is not an ECDLP result.

## Falsifiable hypothesis

There exists a public target-to-syndrome homomorphism for generic prime-order elliptic
addition such that subtracting a reusable reference sketch yields a bounded BCH syndrome
of the signed factor-base multiset for every restricted relation and fresh masked target.
PinSketch decoding would then return occurrences inside the complete sub-rho caps.

## Mechanism-new operation

PinSketch maps a supplied set to BCH power-sum syndromes and decodes a bounded symmetric
difference relative to a nearby supplied set. It counts only if a target endpoint supplies
the syndrome without source knowledge, with signed multiplicity, subset-stable restrictions,
complete negative semantics, and an occurrence inverse. Sketching a known set is a control.

## Assumptions

1. A nontrivial endpoint-to-syndrome homomorphism exists without encoding discrete logs.
2. Every useful source multiset is within the frozen decoding radius of target-independent reference state.
3. Signs, repeated occurrences, exceptional strata, and restrictions have a unique syndrome representation.
4. Decoding failures and list ambiguity are exact and fully charged.
5. The same reference sketch supports relation targets and 100 fresh scalar-blind targets.

## Semantic fingerprint

`public_elliptic_endpoint | BCH_power_syndrome_homomorphism | bounded_signed_set_difference_decode | occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — aggregate moments require a source-faithful inverse and complete descent.
2. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — syndrome analogies need an endpoint encoding.
3. `ideas/rejected/ECDLP-IDEA-150_moore_syndrome_rank_metric_source_decoder_hypothesis.md` — decoding consumes represented source error state.
4. `ideas/rejected/ECDLP-IDEA-307_slepian_wolf_distributed_source_decoder_hypothesis.md` — reconciliation assumes correlated source-bearing inputs.
5. `ideas/rejected/preallocation/20260718v_ECDLP-IDEA-410_characteristic_polynomial_set_reconciliation_preid_duplicate.md` — set reconciliation cannot sketch a hidden target fibre.

## Closest primary literature

- Dodis et al., [Fuzzy Extractors](https://doi.org/10.1137/060651380), formalizes PinSketch-style BCH secure sketches for supplied nearby sets.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), provides endpoint relations but no BCH syndrome homomorphism.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls hidden generic-group assumptions.

No checked source supplies the endpoint homomorphism. This is a conditional information-flow
idea only; the transplant is novelty-unverified and does not survive without that theorem.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, signed decks, reference family, BCH field/code/radius, endpoint map, restrictions, all strata, randomness, and verifier.
2. Build target-independent reference syndromes/state within `B^(9/4+o(1))`; forbid source tables, scalar residues, target caches, and per-target dense vectors.
3. For each known-log target, derive the syndrome from the endpoint, subtract reference state, decode signed occurrences, and verify their elliptic sum.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log, charging decode failures, list sizes, and dependencies.
5. Reuse byte-identical state for 100 fresh `R=Q+[t]P`, decode, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge syndrome construction, field width, decoding, ambiguity, restrictions, output, densities, rank, factor logs, bit complexity, and live memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. The endpoint map, syndrome
coordinates, retries, and output are included. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

PinSketch linearizes symmetric difference of represented sets, not elliptic addition of an
unknown source multiset. A map informative enough to identify factor occurrences may encode
scalar orientation, while generic relations are not close to one fixed reference under
arbitrary restrictions. Without the map, the sketch is supplied source state.

## Proof track

Construct a gauge-invariant endpoint-to-syndrome map with signed multiplicity, bounded
decoding radius, exact restriction behavior, and no hidden DLP, inside both caps.

## Disproof track

Show the map factors only through trivial group data or scalar orientation; find unbounded
set difference, syndrome collisions with different fibres, list explosion, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied nearby toy sets decoded by BCH syndromes with labelled differences.
- Negative: equal syndromes/different elliptic sums, far sets, repeated signed points, empty fibres, and blind targets.
- Baselines: characteristic-polynomial reconciliation, IDEA-053/150, Query2P1, rho, and BSGS.
- Native decoding correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only after a theorem-level endpoint map, zero collisions over four sizes/all strata, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on scalar-labelled advice, one map collision, radius failure, lost sign/occurrence, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o03_endpoint_syndrome_theorem.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o03_syndrome_collision_search.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o03_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This records a theorem-gated representation test, not a surviving hypothesis or rejection of
PinSketch. All evidence would remain toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Specify the endpoint-to-BCH-syndrome map and prove it is nontrivial, source-invertible, restriction-stable, and independent of scalar labels, or preserve the first failed property.
