# ECDLP-IDEA-001 — Ambient spectral incidence oracle

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected_exact_linear_one_witness_spectral_factor__nonlinear_implicit_batch_router_requires_new_id`
- Producer theorem status: `scoped_negative_exact_linear_target_uniform_spectral_factor_with_one_witness__nonlinear_multirow_router_open`; independently reviewed
- Evidence scale: exact theorem-only scoped negative; any future finite preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low-rank or correctness observation is not a break.

## Falsifiable hypothesis

For generic ordinary prime-field curves, the target-conditioned three-point addition
incidence tensor, after lifting point membership to additive characters of `F_p`, has a
uniformly constructible compressed rank `r = N^(rho+o(1))` with `rho < 1/2`. Moreover,
the factorization can return complete factor-base decompositions with total relation,
linear-algebra, and individual-descent exponent below `1/2`, once construction, failed
queries, memory, and verification are charged.

This is stronger than observing spectral bias. It predicts an executable batched
decomposition oracle whose complete ECDLP cost beats matched rho/BSGS in the model.

## Mechanism-new operation

Define the complete incidence relation for `U + V + W = R` on curve points, but access it
through an implicit additive-character formula whose construction and storage are both
sublinear in `p`; materializing the full curve indicator, character table, or target
operator is forbidden. Factor the target-indexed formula without enumerating the `B^3`
triples or solving a membership-quotient polynomial system. The claimed new operation is
a **target-uniform low-rank character factorization with batched witness recovery**, not
a new factor-base shape, solver, resultant, full-size lookup table, or post-hoc selector.

## Assumptions

1. `E(F_p)` contains a prime subgroup `<P>` of order `N = ell = p^(1+o(1))` and `Q=[x]P`.
2. Point membership, curve addition, and additive Fourier transforms are represented with
   all exceptional denominators and sign branches explicit.
3. The rank proxy used in the preflight converges to the rank needed for witness recovery,
   rather than merely compressing a count.
4. Relation samples are target-independent before the target-descent phase.
5. Sparse arithmetic and memory costs are charged in base-field operations/words.
6. Any extrapolation from toy fields is heuristic and model-bound.

## Semantic fingerprint

`ambient_character_transform | target_conditioned_addition_incidence | low_rank_batched_witness_recovery | removes_membership_quotient_enumeration | density_and_rank_charged`

The obstruction it tries to remove is the ledger's factor-base membership solve cost. It
also has to remove, rather than hide, the relation-count and target-descent costs.

The producer theorem receipt now closes the exact linear-rank arm as stated. Flattening
the target-uniform incidence tensor against source tuples has rank exactly `|mF|`.
Writing `S=|mF|`, explicit retained-component memory satisfies `M>=S`, while obtaining
one useful row per supported known-log target has favorable attempt work `T>=B*N/S`.
Therefore `max(T,M)>=sqrt(B*N)=N^((1+beta)/2)`, which is `N^0.6` at
`beta=1/5`. This is a time/memory resource tradeoff, not a standalone time or
Shoup-style lower bound. A nonlinear operation that consumes a succinct target batch and
emits many independent exact source rows remains outside this scoped negative.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the direct obstruction: prime-field PDP membership and
   relation/linear-algebra costs remain above rho.
2. `ledger/H-FB-001.yaml` — rules out elementary factor-base shape as the explanation.
3. `ledger/EV-FB-001.yaml` — supplies the matched random-base yield law.
4. `ledger/H-REP-001.yaml` — rules out presenting another equation formulation as a new
   scaling mechanism.
5. `ledger/SYNTHESIS-20260716.md` — requires a representation-level operation and full
   Phase-5 accounting.

## Closest primary literature

- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), establishes the point-decomposition route.
- McGuire and Mueller, [A New Index Calculus Algorithm for the ECDLP](https://eprint.iacr.org/2017/1262.pdf), already explores solver-free summation evaluation; therefore “no Gröbner basis” is not novel.
- Corrigan-Gibbs, Henzinger, and Wu, [The Structured Generic-Group Model](https://eprint.iacr.org/2026/384), charges algorithms whose exploitable structure covers only a small fraction of points.
- Shoup, [Lower Bounds for Discrete Logarithms](https://www.shoup.net/papers/dlbounds1.pdf), is the generic `Omega(sqrt(N))` boundary the encoding-specific operation must escape.

The checked sources do not establish the proposed target-uniform low-rank witness oracle.
That is not proof of novelty; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Fix a deterministic factor base `F subset <P>` of size `B=N^beta` and a reversible
   point-to-coordinate encoding; freeze exceptional-point handling.
2. Derive implicit additive-character evaluators for the curve indicator, factor-base
   indicator, and rational addition graph. Record the expanded table size as a negative
   control, but do not construct it or charge it as a sublinear object.
3. Factor the target-parameterized incidence operator into `r=N^rho` components and retain
   enough data to recover actual signed points, not just a relation count.
4. Freeze a target-independent batch of random known scalars `a` and query
   `R=[a]P`; recover and verify `R=F_i+F_j+F_k`. Reject invalid or duplicate
   witnesses without resampling invisibly. The batch contains every failed scalar needed
   to pay the generic three-sum density.
5. Collect at least `B+security_margin` independent rows and solve the sparse system for
   the logarithms of all factor-base points.
6. Query the same frozen oracle on randomized target representatives `Q+[t]P` until a
   verified factor-base decomposition is obtained; substitute known factor-base logs.
7. Recover `x mod N` and verify `[x]P=Q` on the original instance.

## Full rho/BSGS cost model

Let `B=N^beta`; compressed-state bit memory be `N^s`; factorization construction cost be
`N^a`; reciprocal relation success density be `N^delta`; and reciprocal individual-
descent density be `N^delta_t`. Obtaining `B` rows requires a frozen batch of
`L_rel=N^(beta+delta+o(1))` known-scalar targets. Let `N^q_rel` be the **total** cost of
processing that complete batch, including misses and witness output, and let `N^q_t` be
the total cost of processing `N^(delta_t+o(1))` randomized individual-descent targets.
These are batch costs, not per-query costs with density silently omitted.

- Pollard rho baseline: expected `sqrt(pi*N/2)=N^(1/2+o(1))` group operations and `O(1)`
  state, before only constant-factor automorphism gains.
- BSGS baseline: `N^(1/2+o(1))` group operations and `N^(1/2+o(1))` stored points.
- Oracle construction: `T_build=N^(a+o(1))`.
- Relation collection: `T_rel=N^(q_rel+o(1))` for all `L_rel` candidates and
  `Theta(B)` accepted rows. An ordinary per-query implementation has
  `q_rel>=beta+delta` before its query cost and is an explicit negative control.
- Sparse linear algebra: conservatively `T_LA=N^(2*beta+o(1))`, memory `N^(beta+o(1))`.
- Individual descent: `T_desc=N^(q_t+o(1))` for the complete randomized target batch.
- Verification is linear in emitted witnesses and is included in `q_rel` and `q_t`.

Thus the claimed time exponent is
`lambda=max(a, q_rel, 2*beta, q_t)` and the memory exponent is
`mu=max(s,beta)`, with every stored field element charged by its bit representation. A count-only transform, an `a>=1/2` build, or a density omitted from
the explicit batch sizes does not beat rho. Under the generic three-sum heuristic,
`delta=max(0,1-3*beta)`; at `beta=0.20`, an ordinary scan pays
`beta+delta=0.60`, so this candidate survives only if the target-uniform factorization
processes that batch in exponent at most `0.45`.

## Likely fatal obstruction

For generic curves the addition incidence is expected to have square-root-scale spectral
complexity, while any useful low-rank portion may cover only a negligible fraction of
points. Then `rho`, `a`, `q_rel`, or `q_t` restores a `>=1/2` exponent. The structured-generic
lower bound makes sparse post-hoc structure especially dangerous: rank compression of
counts can coexist with rho-hard witness recovery.

The exact producer gate strengthens this for the declared linear one-witness interface:
rank gives explicit memory `M>=S`, while shrinking endpoint support increases favorable
known-target attempt work to `T>=B*N/S`. Thus `max(T,M)` has floor `N^0.6` at the
campaign factor-base exponent; `T` alone is not asserted to have that floor. The
statement is not an arithmetic-circuit or Shoup-style lower bound; implicit nonlinear
target batching and multirow source generation remain open only under a new successor ID.

## Proof track

Prove an explicit factorization identity over additive characters, a uniform upper bound
on its witness-recovery rank, and an algorithm that processes the full
`N^(beta+delta)` known-scalar batch and the full `N^delta_t` target batch at the claimed
total costs. Then prove the seven-step descent and derive `lambda<1/2` with all transforms
and memory charged.

## Disproof track

Establish any one of: rank `N^(1/2-o(1))`; construction or complete-batch witness recovery
`N^(1/2-o(1))`; generic density forces `q_rel>=1/2`; factorization recovers counts but not
witnesses; or the measured total exponent confidence interval intersects `1/2`.

## Positive and negative controls

- Positive control: an additive cyclic group with a planted convolutional factor base,
  where FFT factorization and witness recovery are known to be low rank.
- Positive instrumentation control: tiny curves exhaustively enumerate all triples and
  compare every spectral count and recovered witness.
- Negative control: random tensors with the same dimensions and marginal density.
- Negative mechanism control: the ledger's random/interval/AP bases processed by ordinary
  enumeration; they must not acquire a claimed exponent win from relabeling.
- Adversarial control: permute point encodings while preserving the abstract group law; any
  surviving benefit must be traced to a stated coordinate operation.

## Quantitative promotion and falsification gates

Toy preflight fields are `13, 14, 15, 16, 18` bits, at least 20 independent ordinary
curves per size, three deterministic bases per curve, with exhaustive truth through 16
bits. Promotion to a larger scaling study requires all of:

- upper 95% confidence bound `rho <= 0.35` for witness-recovery rank;
- upper 95% bounds `a <= 0.45`, `q_rel <= 0.45`, and `q_t <= 0.45`, with all
  `N^(beta+delta)` and `N^delta_t` candidates represented in the measured batches;
- some preregistered `beta <= 0.20` giving upper 95% bound `lambda <= 0.45`;
- zero incorrect accepted witnesses and exact agreement with every exhaustive count;
- memory exponent upper bound `mu <= 0.45`.

Falsify this scoped prediction if any exhaustive mismatch occurs, witness recovery is not
available, the rank-slope lower 95% bound is `>=0.49`, or every fitted full-cost
configuration has lower 95% bound `lambda>=0.50`. A timeout is infrastructure failure.

## Artifact plan

- Planned contract draft: `ideas/artifacts/ECDLP-IDEA-001/contract.yaml`
- Exact linear-rank theorem gate: `ideas/artifacts/ECDLP-IDEA-001/exact_spectral_rank_density_gate.md`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-001/spectral_incidence.py`
- Planned manifests: `ideas/artifacts/ECDLP-IDEA-001/runs/<run-id>/manifest.yaml`
- Planned raw data: `ideas/artifacts/ECDLP-IDEA-001/runs/<run-id>/raw.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-001/analysis.md`
- Required retained data: matrices or sketches, ranks, witnesses, failed queries, timings,
  peak memory, exact seeds, commit, dirty-tree state, stdout, and stderr.

## Interpretation boundary

A toy low-rank observation is heuristic and model-bound. Correct relation counts or valid
decompositions do not establish an ECDLP improvement. Only a verified end-to-end cost
exponent below rho/BSGS can support escalation, and it still would not be a breakthrough
without crypto-scale replication and independent review.

## Exactly one next executable action

1. Write a new successor hypothesis only after freezing one explicit nonlinear implicit-batch/multirow source recurrence with complete rank, factor-log, blind-descent, and sub-rho costs; do not draft or execute the closed linear-character contract.
