# ECDLP-IDEA-057 — Algebraic correction-map birthday descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_exact_composable_bucket_and_kummer_trace_norm_resultant_scoped_negative_list_specific_correction_open`
- Evidence scale: `toy` proof preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: rejected as an explicit generalized-birthday/large-prime
  variant unless a support-law-changing algebraic correction identity is proved first.
- Breakthrough claim: **none**; a bucket collision, repaired tuple, graph cycle, valid
  relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Let a factor base have size `B=N^beta` and an auxiliary large-prime deck have size
`L=N^ell`. The rejected proposal asserted that a frozen algebraic correction map
`C(u,v)` repairs near-collisions produced by a Wagner-style generalized-birthday tree so
that corrected endpoints land on the valid elliptic relation surface with polynomial
enrichment `N^delta`, `delta>1/4`, or admit an implicit query oracle with setup below
`L` and query below `sqrt(L)`. Complete relations, large-prime closure, factor logs, and
target descent would then beat rho and BSGS.

Without a proved correction identity that changes support rather than reorders explicit
buckets, this is the ledger's two-large-prime occupancy mechanism. The explicit
hash-like model has a restricted minimum exponent `2/3`; tuning levels, bucket widths,
or repair schedules cannot promote.

## Mechanism-new operation

The proposed operation was to split an `m`-term elliptic sum into birthday buckets,
merge partial states under truncated public labels, and apply an algebraic correction
map to a failed merge so it becomes a valid factor-base-plus-large-prime relation while
preserving source witnesses. Repaired endpoints would be joined into a signed/incidence
cycle graph and solved by sparse linear algebra.

The operation is mechanism-new only if `C` obeys an exact elliptic identity that
provably changes the corrected support distribution or gives a non-materializing
endpoint oracle. If `C` merely changes bucket representatives, adds explicit correction
tables, or retries nearby labels, it is an explicit Wagner/large-prime table and is
rejected under the recorded obstruction.

The theorem-only producer receipt now closes every exact globally composable bucket
label on the prime-order subgroup. Equality fibers of such a label form a group
congruence, hence cosets of a subgroup; prime order makes the label constant or
injective. A constant label does not filter, while an injective label retains the full
point and supplies no quotient collisions. Only a genuinely nonhomomorphic,
field-specific correction identity or list-restricted support operation remains open.

The first concrete nonhomomorphic candidate is now also screened. For short
Weierstrass curves, the trace and norm of `{x(P+Q),x(P-Q)}` are exactly the two
normalized coefficients of `S3(x(P),x(Q),Z)`. Aggregating them over a source deck is
`Res_U(F(U),S3(U,v,Z))`; source-complete composition is the P1478/P1513 recursive
norm/resultant backend. This removes raw Kummer trace/norm as a mechanism-new
correction, while preserving a list-specific support-changing identity or implicit
source router as open.

## Assumptions

- `E`, `P`, `Q`, factor and large-prime decks, bucket maps, truncation bits, correction
  map, merge tree, and stopping rules are frozen before outcomes.
- Every bucket entry, correction attempt, failed merge, duplicate endpoint, edge,
  source witness, graph solve, relation verification, and retained bit is charged.
- Corrected relations preserve exact signed elliptic sums and source identities; a graph
  cycle without a verified group relation has zero evidentiary weight.
- Enrichment is measured against independent hash, shuffled-coordinate, and synthetic
  occupancy controls on held-out instances.
- All finite evidence is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`Wagner_generalized_birthday_tree | algebraic_failed_merge_correction | factor_plus_large_prime_relations | implicit_or_enriched_cycle_closure | target_descent`

Collision fingerprint:
`explicit_bucket_tables | hash_like_two_large_prime_occupancy | parameter_tuning | exponent_two_thirds_floor`

## Five closest ledger entries

1. `ledger/H-FB-001.yaml` — rules out credit for a factor-base or bucket shape without a scaling-changing support operation.
2. `ledger/EV-FB-001.yaml` — supplies matched random/structured yield and solving controls for claimed enrichment.
3. `ledger/FINDING-PF-IC-001.md` — requires complete relation, rank, target descent, and memory below rho.
4. `ledger/H-REP-001.yaml` — distinguishes a correction-map representation from a changed mathematical support law.
5. `ledger/SYNTHESIS-20260716.md` — enforces fresh-instance scaling, independent verification, and toy claim boundaries.

## Closest primary literature

- Wagner, [A generalized birthday problem](https://doi.org/10.1007/3-540-45708-9_19),
  supplies the primary merge-tree algorithm whose explicit bucket costs must be charged.
- Gaudry, Thomé, Thériault, and Diem, [A double large prime variation for small genus
  hyperelliptic index calculus](https://doi.org/10.1090/S0025-5718-06-01863-3), gives
  the closest primary large-prime graph/cycle framework.
- Semaev, [Summation polynomials and the discrete logarithm
  problem](https://eprint.iacr.org/2004/031), supplies the exact elliptic relation law a
  correction identity must preserve.

None proves the proposed support-law-changing correction identity for generic
prime-field elliptic curves. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze the factor base `F`, large-prime deck `L`, arity, merge tree, bucket labels,
  correction formula, canonical signs, duplicate policy, and cost ledger.
- Build only the setup structures authorized by the proved correction identity; record
  whether any structure materializes `Theta(L^2)` pairs or an equivalent table.
- Generate known-scalar shifted targets and execute every birthday merge and correction,
  retaining failed buckets and all endpoint/source multiplicities.
- Independently verify each small/large-prime elliptic relation and insert its signed
  edge/hyperedge into the closure graph.
- Extract verified cycles, eliminate large primes, collect at least `B` independent
  factor rows, and solve all factor-base logarithms.
- Apply the identical bucket/correction/closure process to `Q+[t]P`, recover explicit
  atoms, substitute factor and resolved large-prime logs, remove `t`, and verify
  `[x]P=Q`.
- Compare the full process with ordinary Wagner buckets, explicit hash-like 2LP advice,
  and rho/BSGS; do not credit a correction that only relocates attempts.

## Full rho/BSGS cost model

Let `B=N^beta`, `L=N^ell`, correction setup exponent `a`, one corrected membership
query exponent `q`, measured support enrichment `N^delta`, and stored state exponent
`s`. In the explicit hash-like two-large-prime control, pair advice costs `N^(2*ell)`,
miss/search work costs `N^(1-ell)`, and obtaining `B` useful rows from pair support costs
`N^(1+beta-2*ell)` before sparse factor linear algebra and descent.

- Pollard rho: `N^(1/2+o(1))` time and negligible asymptotic memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Explicit bucket/pair setup: exponent `2*ell`; any correction table is added to `a`.
- Relation search and closure control:
  `max(1-ell-delta,1+beta-2*ell-delta,q+beta)`.
- Sparse factor linear algebra: exponent `2*beta` time and `beta` memory.
- Target descent uses the same corrected query/closure backend and its complete attempt
  and candidate-output exponent `d_t`.

The full time exponent is
`lambda=max(a,2*ell,1-ell-delta,1+beta-2*ell-delta,q+beta,2*beta,d_t)` and bit-memory
exponent is `mu=max(s,ell,beta)`. With `beta=1/5`, explicit hash-like advice and
`delta=0` minimize at exponent `2/3`, not `1/2`. A survivor needs proved/measured
`delta>1/4` or an implicit deck with setup `o(L)` and query `o(sqrt(L))`, followed by
upper 95% complete-pipeline bounds `lambda,mu<1/2`.

## Likely fatal obstruction

An algebraic correction that maps many failed bucket pairs to valid relations usually
creates equal preimage multiplicity on successes and trials, duplicates existing
endpoints, or requires an explicit table as large as the avoided pair surface. Wagner
truncation discards information needed for exact elliptic source recovery. After signs,
duplicate columns, graph rank, correction verification, and target descent are restored,
the explicit occupancy floor remains. The exact composable-label arm is now additionally
closed by the prime-order congruence theorem; any survivor must be nonhomomorphic and
prove its correction/support law rather than inherit it from bucket composition.

## Proof track

Before implementation, prove an exact correction identity, source-replay theorem, and
support distribution theorem showing either enrichment `delta>1/4` or an implicit
setup/query bound that crosses the ledger threshold. Then prove large-prime graph rank,
factor-log recovery, masked descent, and complete `lambda,mu<1/2` accounting.

## Disproof track

Show the correction is a permutation/many-to-one relabeling with no support enrichment;
its table or preimages cost `Theta(L^2)`; corrected edges duplicate columns; source
recovery requires enumerating discarded bucket states; or the optimized complete cost
has exponent at least `1/2`. Failure to prove the identity leaves this record rejected
without an experiment.

## Positive and negative controls

- Positive correction control: a synthetic group relation with a planted algebraic
  correction identity and known enrichment.
- Positive graph control: planted signed cycles with known factor and large-prime logs.
- Negative occupancy control: independent hash decks with identical sizes and merge
  schedules.
- Negative geometry control: shuffled coordinate decks preserving marginal bucket
  counts.
- Baseline control: ordinary Wagner, explicit 2LP, rho, and BSGS under the same cost
  ledger.
- Leakage control: forbid post-hoc correction formulas, bucket widths, target-dependent
  retries, and uncharged oracle tables.

## Quantitative promotion and falsification gates

The identity-only gate precedes collection: symbolic proof plus exhaustive verification
on every ordinary curve through 16 bits, all inputs, signs, exceptional branches, and
source witnesses. Only after that gate may a scaling preflight use at least 24 curves per
16--24-bit size, `B=N^(1/5)` controls, at least four `L` exponents, 1,000 verified
relations, and 100 masked descents per largest cell. Reconsideration requires zero
identity/source failures, held-out lower 95% `delta>0.25` or certified implicit bounds,
full factor rank, at least 95% descent recovery, and upper 95% `lambda,mu<=0.45`.
Falsify if the identity is absent, enrichment lower bound is at most `0.25`, setup/query
fails the implicit thresholds, or any lower 95% complete-cost exponent reaches `0.50`.

## Artifact plan

- Identity proof: `ideas/artifacts/ECDLP-IDEA-057/correction_identity.md`
- Existing exact-label theorem gate: `ideas/artifacts/ECDLP-IDEA-057/prime_order_composable_bucket_theorem.md`
- Kummer trace/norm removal gate: `ideas/artifacts/ECDLP-IDEA-057/kummer_trace_norm_correction_gate.md`
- Symbolic checker: `ideas/artifacts/ECDLP-IDEA-057/check_identity.sage`
- Exhaustive truth: `ideas/artifacts/ECDLP-IDEA-057/exhaustive_identity.jsonl`
- Occupancy/cycle ledger: `ideas/artifacts/ECDLP-IDEA-057/occupancy.jsonl`
- Planned audit runs: `ideas/artifacts/ECDLP-IDEA-057/runs/<run-id>/`
- Cost analysis: `ideas/artifacts/ECDLP-IDEA-057/cost_model.json`
- Required retained data: formulas, branches, buckets, corrections, failures, endpoints,
  witnesses, edges, cycles, ranks, descents, commands, environment, resources, stdout,
  stderr, and checksums.

## Interpretation boundary

This record is rejected unless the support-law-changing correction identity is proved
first. It is toy, heuristic, model-bound, and novelty-unverified. An exact bucket merge,
cycle, relation, or toy scalar is not a breakthrough. Parameter tuning, explicit tables,
and post-hoc repairs remain duplicates of the recorded large-prime family.

## Exactly one next executable action

1. Independently review both IDEA-057 theorem receipts, then either preserve the two scoped rejections or freeze one explicit list-specific support-law-changing identity or implicit source router with all inputs, exceptional branches, exact replay, and complete sub-rho relation/rank/descent costs before implementing any checker or bucket tree.
