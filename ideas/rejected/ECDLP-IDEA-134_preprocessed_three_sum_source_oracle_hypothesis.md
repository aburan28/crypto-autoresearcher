# ECDLP-IDEA-134 — Preprocessed three-sum source oracle

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_preprocessed_universe_batch_dimension`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: retired `review_required` draft; unapproved; zero runs permitted
- Scale labels: every prospective finite measurement is `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct three-sum query, valid relation, full toy rank, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a public factor base `F` of size `B=N^beta`, the two-versus-three split of a five-source relation admits a group-native preprocessed-universe data structure that, for every target `R`, reports all signed intersections `A_2 intersect (R-A_3)` with exact source labels in total query exponent `alpha<3/2`. Its setup is at most `B^(2+o(1))`, it never materializes `A_3`, a scalar-indexed ambient array, or a dense resultant, and the same frozen structure supports relation collection and blind target descent.

## Mechanism-new operation

The proposed operation is a **source-reporting elliptic three-sum index for a batch of all `B^2` two-sum endpoints**. It would adapt preprocessed-universe 3SUM so equality is tested directly in `E(F_p)`, not through hidden discrete-log coordinates, and return the three factor-base indices for every hit. The operation must exploit the shared public universe across the entire `A_2` batch; calling an ordinary three-sum query independently, sorting a `B^3` list, building a full pair/large-prime table, or applying a generic solver is a duplicate/control.

Unlike rejected IDEA-117, this lane does not instantiate or semijoin P1510 product-circuit leaves: its claimed object is one group-native, target-reusable preprocessed universe built before any three-source leaf list exists. If a construction first emits the IDEA-117 provenance leaves, or merely runs a faster join over them, the distinction fails and this record must merge into IDEA-117.

Independent review nevertheless rejects the specification. The cited `O(n^(3/2))` preprocessed-universe bound is measured in the universe size: using the `B^2` pair-endpoint universe gives `B^3`, not the claimed `B^(3/2)`, while the unmaterialized three-source side is itself `B^3`. Asking for a strict-sub-`B^(3/2)` group-native complete reporter without a construction restates the P1434/IDEA-012/IDEA-120 source-oracle wish and the ledger's frozen cubic generator boundary.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and a target-independent signed factor base `F` of size `B=N^beta`, with the primary arm `beta=1/5`.
2. A group-native equality/hash primitive uses public point encodings and never assumes scalar indices, a discrete-log oracle, or a length-`N` convolution array.
3. Setup emits at most `B^(2+o(1))` words and the complete batched query, including source labels and verification, costs `B^(alpha+o(1))` for fixed `alpha<3/2`.
4. The reporter is complete on signs, repetitions, infinity, collisions, and exceptional projective cases and has no post-hoc selector.
5. Failed targets, output multiplicity, factor-base construction, rank, factor-log linear algebra, blind descent, final scalar verification, and peak bit memory are charged.

## Semantic fingerprint

`elliptic_preprocessed_universe_3SUM | batched_A2_against_R_minus_A3 | group_native_equality | exact_three_source_reporting | strict_alpha_below_three_halves | no_scalar_index`

The load-bearing novelty is a single shared batch operation with strict `alpha<3/2` and exact sources. Independent ordinary queries, FFT over hidden scalar coordinates, explicit `A_3`, large-prime graphs, generic 3SUM substitution, or membership-only output are duplicates or controls.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which freezes the complete five-term query boundary `alpha<3/2`, setup at most `B^2`, exact sources, rank, and descent.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, the exact pair-only/on-demand generator boundary showing cubic per-target work or cubic triple advice.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which asks for a public source-fiber generator and transposed target join; the proposed reporter restates that missing operation.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where explicit forward/backward serial-`S3` state polynomials become too dense; the new index may not materialize those states.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where one subgroup-norm transition is compact but two-transition composition is dense quadratic; the reporter must bypass that composition and still emit sources.

## Closest primary literature

- Golovnev, Guo, Horel, Park, and Vaikuntanathan, [Data Structures Meet Cryptography: 3SUM with Preprocessing](https://arxiv.org/abs/1907.08355), give preprocessing/query tradeoffs but not a source-complete elliptic-group batch with hidden scalar indices forbidden.
- Kasliwal, Polak, and Sharma, [3SUM in Preprocessed Universes: Faster and Simpler](https://arxiv.org/abs/2410.16784), achieve an `O(n^1.5 log n)` subset-query boundary and report participation; they do not give the strict sub-`3/2` group-native operation required here.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation equations but no such data structure.

No checked primary source proves the exact operation or full ECDLP path. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, sign/order conventions, complete projective addition, deterministic preprocessing, and an independent verifier.
2. Build the target-independent `B^(2+o(1))` source-labelled universe from public factor points and pair endpoints; record every byte and group operation.
3. For each known-log target `R_j=[r_j]P`, issue one shared batch for all `A_2` endpoints against `R_j-A_3`; emit every five-source tuple, including multiplicities, without `A_3` materialization.
4. Verify every tuple by direct curve membership and elliptic addition; retain exactly `B+sigma` rows of rank `B`, charging misses and false reports.
5. Solve factor-base logarithms and independently verify every `[log_P(S)]P=S`.
6. For each fresh mask `t`, query `R_t=Q+[t]P`, substitute verified factor logs in every returned tuple, enumerate ambiguity, subtract `t`, and accept only `x` with `[x]P=Q`.
7. Report setup, relation queries, output, rank, linear algebra, blind descent, verification, time, and peak memory against matched rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let setup and setup-memory be `B^s,B^s_m`; one complete target batch be `B^alpha`; query working memory be `B^m_q`; inverse useful-row and target densities be `B^delta,B^delta_t`; source-output and ambiguity exponents be `o,u`; and factor-log linear-algebra time/memory be `B^ell,B^ell_m`. Then

`lambda=max(s*beta,(1+alpha+delta+o)*beta,ell*beta,(alpha+delta_t+o+u)*beta,beta)`

`mu=max(s_m*beta,m_q*beta,(1+o)*beta,ell_m*beta,u*beta)`.

At `beta=1/5`, `s<=2` and `ell<=2` fit below rho, but relation collection requires strict `alpha+delta+o<1.5`; equality is not enough. Every source label, failed batch, and verification is included. Toy slopes are model-bound and cannot establish these exponents.

## Likely fatal obstruction

The best checked preprocessed-universe result reaches, rather than beats, the `3/2` boundary and relies on integer FFT/hash structure absent from a generic prime-order elliptic group without scalar indexing. A data structure can also decide participation while failing to enumerate all signed sources. Translating the full `B^2` endpoint batch may restore `B^3` work, `B^3` traffic, or a scalar-indexed ambient array, exactly the occupied P1434/P1477/P1478 obstruction.

## Proof track

Give a group-native construction, prove exact source completeness for the entire batch, prove setup `s<=2` and a fixed `epsilon>0` with `alpha<=3/2-epsilon`, and derive `lambda,mu<=0.45` through rank and blind descent without an ambient scalar coordinate.

## Disproof track

Reduce the construction to independent 3SUM queries, explicit `A_3`, scalar-indexed convolution, P1477 states, P1478 dense composition, or a known preprocessing/query lower-bound model; alternatively prove `alpha>=3/2`, incomplete source reporting, or `lambda>=1/2` or `mu>=1/2` after output and memory are charged.

## Positive and negative controls

- **Positive control:** integer and small cyclic-group preprocessed-universe fixtures with supplied scalar indices and planted triples, verifying complete labels and multiplicities.
- **Positive control:** exhaustive toy elliptic fixtures where direct enumeration supplies the exact signed five-source set.
- **Negative control:** independently repeated ordinary three-sum queries, explicit `A_3`, scalar-indexed FFT, P1477 materialized states, and P1478 dense resultants.
- **Negative control:** matched random prime-order groups and random factor bases with the same sizes and output multiplicities.
- **End-to-end control:** matched rho and BSGS plus blind known-log and unknown-log targets under the same accounting.

## Quantitative promotion and falsification gates

The present lane is rejected at the input-dimension and missing-oracle boundary. A fresh ID requires a concrete group-native operation that is not a relabelled P1434/IDEA-012/120 reporter and a proof of `s,s_m<=2`, `alpha<=1.25`, and complete `lambda,mu<=0.45`. Falsify the declared mechanism on one missed source, hidden scalar index, `B^3` object/traffic stage, post-hoc label, or a complete exponent at least `0.5`.

## Artifact plan

- Input-dimension and source-oracle merge audit: `ideas/artifacts/ECDLP-IDEA-134/group_native_three_sum_theorem.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-134/fixtures.json`
- Prospective implementation: `ideas/artifacts/ECDLP-IDEA-134/batched_three_sum_oracle.py`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-134/verify_sources.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-134/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-134_preprocessed_three_sum_source_oracle_preflight.yaml`

No successor artifact or run exists; only the retired `review_required` contract exists.

## Interpretation boundary

This is rejected, novelty-unverified algorithm evidence. All finite tests would be toy, and all extrapolated costs remain heuristic and model-bound. A correct query or valid relation proves only scoped functionality, not a generic prime-field ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-134/group_native_three_sum_theorem.md` formalizing the `n=B^2` preprocessed-universe dimension charge and its merge into the existing source-oracle/cubic-generator boundary, without implementing or timing a solver.
