# ECDLP-IDEA-053 — Aggregate-moment large-prime decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `deferred_missing_moment_oracle`
- Evidence scale: `toy` identity derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; decoding an explicit endpoint table or a valid cycle is not a break.

## Falsifiable hypothesis

For partial elliptic relations with at most `k=N^(sigma+o(1))` distinct large-prime
endpoints per batch, complete addition-law resultants admit target-independent aggregate
power sums of the unknown endpoint keys in `N^(u+o(1))` time, `u<1/2`, without first
enumerating edges. Exact sparse interpolation then recovers endpoints, source relations,
and cycles with complete ECDLP cost below rho/BSGS.

## Mechanism-new operation

The operation is an **implicit elliptic endpoint-moment oracle**: traces/norms of a
factored addition-law algebra return power sums of all successful large-prime endpoints,
after which Prony-style decoding recovers keys and source tags. IBLTs, explicit
large-prime tables, generic sparse interpolation after edge enumeration, hash buckets,
and post-hoc cycle selectors are duplicates or controls.

## Assumptions

1. `E(F_p)` has prime subgroup `<P>` of order `N=p^(1+o(1))` and `Q=[x]P`.
2. The small factor base and large-prime domain are fixed and target-independent.
3. The batch support is sparse and its upper bound is preregistered, not learned from successes.
4. Aggregate moments are computed without listing candidate endpoints or edges.
5. Decoding returns endpoint keys plus source relation coefficients and exact cycle witnesses.
6. Scaling remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`partial_elliptic_relations | implicit_endpoint_power_sums | table_free_sparse_interpolation | source_tag_recovery | exact_large_prime_cycles`

## Five closest ledger entries

1. `ledger/H-FB-001.yaml` — constrains factor-base and yield comparisons.
2. `ledger/EV-FB-001.yaml` — supplies matched relation-density evidence.
3. `ledger/FINDING-PF-IC-001.md` — identifies the membership arithmetic baseline.
4. `ledger/H-REP-001.yaml` — blocks a result encoding with unchanged enumeration cost.
5. `ledger/SYNTHESIS-20260716.md` — requires cycle, rank, descent, and memory accounting.

## Closest primary literature

- Goodrich and Mitzenmacher, [Invertible Bloom Lookup Tables](https://arxiv.org/abs/1101.2245), gives an explicit sparse key-recovery baseline that must be beaten without enumerated insertions.
- Ben-Or and Tiwari, [A deterministic algorithm for sparse multivariate polynomial interpolation](https://doi.org/10.1145/62212.62237), gives the power-sum/sparse interpolation backend.
- Gaudry, Thome, Theriault, and Diem, [A double large prime variation for small genus hyperelliptic index calculus](https://doi.org/10.1090/S0025-5718-06-01863-3), supplies the primary large-prime graph, cycle, and rank baseline.
- Wagner, [A generalized birthday problem](https://www.iacr.org/archive/crypto2002/24420288/24420288.pdf), supplies the nearby list-merging cost floor.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the elliptic relation predicate.

None supplies an endpoint-moment oracle that avoids generating the partial-relation edge
stream; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze small-base size, large-prime domain, batch construction, support cap, and exact addition charts.
2. For known `R=[a]P` batches, compute endpoint power sums directly from the factored relation algebra.
3. Decode endpoint keys and source tags; independently reconstruct and verify every partial relation.
4. Join repeated endpoints into exact cycles, project them to small-factor-base relation rows, and retain all misses/collisions.
5. Collect full-rank rows and solve small-base logarithms with all batch and decoder costs charged.
6. Run identical batches on `Q+[t]P` until a verified target cycle/descent appears.
7. Substitute logs, remove `t`, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let small base `B=N^beta`, implicit moment cost
`N^u`, support `N^sigma`, decoder exponent `d>=sigma`, batch success/cycle reciprocal
exponents `delta,chi`, target exponent `delta_t`, and build/storage `a,s`. Then
`q=max(u,d)`,
`lambda=max(a,beta+delta+chi+q,2beta,delta_t+q)`, and
`mu=max(s,beta,sigma)`. If endpoints are enumerated first, their generation exponent is
inserted into `q` and the mechanism fails its definition.

## Likely fatal obstruction

Computing even the first nontrivial endpoint moment may require the same dense resultant
or explicit edge stream as ordinary relation generation. Source tags can disappear under
aggregation, and cycle density may impose the known `2/3`-style large-prime floor.

## Proof track

Derive exact moment identities and source tags, prove sparse decoding and cycle
completeness, and bound build, support, density, rank, descent, verification, and memory
to obtain `lambda,mu<1/2` without explicit endpoints.

## Disproof track

Reduce moment computation to endpoint enumeration, show two source streams share all
available moments, prove cycle density restores `lambda>=1/2`, or find a verified
missing/false decoded edge.

## Positive and negative controls

- Positive control: planted sparse endpoint polynomials with exact moment access.
- Positive correctness control: explicit endpoint enumeration on tiny curves.
- Negative control: random edge streams with matched support and degree.
- Mechanism control: IBLT and explicit hash-table cycle closure including insertion cost.
- Leakage control: forbid post-hoc support caps, target-specific batches, endpoint tables, and dropped collisions.

## Quantitative promotion and falsification gates

Deferral lifts only after a symbolic first-through-`2k` moment construction whose cost
does not touch candidate endpoints and whose source tags decode exactly. A later study
requires zero false/missed exhaustive edges, at least 20 curves per size, 1,000 verified
cycles and 100 target descents, and upper 95% `u<=0.20`, `lambda<=0.45`, and
`mu<=0.45`. Reject if moment construction enumerates endpoints, source tags collide,
support has lower 95% `sigma>=0.50`, or every complete arm has lower 95%
`lambda>=0.50`.

## Artifact plan

- Derivation: `ideas/artifacts/ECDLP-IDEA-053/endpoint_moment_identity.md`
- Oracle checker: `ideas/artifacts/ECDLP-IDEA-053/check_moments.sage`
- Analysis: `ideas/artifacts/ECDLP-IDEA-053/analysis.md`
- Decoder: `ideas/artifacts/ECDLP-IDEA-053/moment_decoder.sage`
- Retain decoded support, cycles, failures, operation counts, seeds, commands, environment, and commit.

## Interpretation boundary

This deferred claim is toy, heuristic, model-bound, and novelty-unverified. Sparse
decoding, a closed cycle, or a valid relation does not establish an ECDLP improvement.

## Exactly one next executable action

1. Derive the first four exact endpoint power-sum identities from a two-large-prime elliptic relation stream without enumerating the endpoints.
