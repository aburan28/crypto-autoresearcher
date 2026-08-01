# ECDLP-IDEA-012 — Aggregate complement-divisor compression

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid smooth divisor or low-cost toy query is not a break.

## Falsifiable hypothesis

For generic ordinary prime-field curves, the intersection of the Abel-Jacobi fiber over
`R` with degree-`m` effective divisors supported on a factor base `F` of size `B=N^beta`
can be queried, with witness recovery, in `B^(kappa+o(1))` operations for sufficiently
small `kappa`. Encoding the whole divisor as one section and manipulating its complement
avoids constructing the degree-`B` membership quotient. For some frozen `(m,beta)`, the
complete relation, linear-algebra, and target-descent exponent is below `1/2` after build,
failed-query, memory, and verification costs are charged.

The claim is not that smooth divisors exist or that principal-divisor relations are valid.
It predicts a target-uniform, quotient-free **witness oracle** whose end-to-end cost beats
rho/BSGS in the stated heuristic model.

## Mechanism-new operation

Represent an unordered factor-base decomposition `D=P_1+...+P_m` by a single section of
the degree-`m` line bundle whose zero divisor is `D`, and represent the target condition by
the Abel-Jacobi fiber `sum(P_i)=R`. Push the factor-base product tree through this
aggregate section/complement representation so a query returns the supported divisor
without adjoining `m` separate roots of the factor-base locator polynomial.

The claimed new operation is **aggregate divisor-support intersection with witness
recovery**. It is not a new curve model, simple factor-base shape, Gröbner solver,
dense resultant, explicit large-prime table, post-hoc selector, or relation-only certificate.

## Assumptions

1. `E(F_p)` contains a known prime subgroup `<P>` of order `N=ell=p^(1+o(1))`, and
   `Q=[x]P`.
2. A deterministic factor base `F subset <P>` of size `B=N^beta` has an auditable point-ideal
   product tree and no target-dependent selection.
3. Degree-`m` effective divisors, their line-bundle sections, Abel-Jacobi images, signs,
   multiplicities, and exceptional tangencies are represented exactly.
4. The aggregate query recovers actual points in `F`, not only a smoothness count or a
   relation-validity certificate.
5. Relation probability follows the charged heuristic `pi_rel=N^(-delta+o(1))`, with
   `delta=max(0,1-m*beta)` unless measured data justify a worse value.
6. Toy scaling is heuristic and model-bound; novelty is unverified.

## Semantic fingerprint

`symmetric_effective_divisor | Abel_Jacobi_target_fiber | aggregate_section_complement | quotient_free_factor_base_support | target_uniform_witness_recovery`

The operation attacks the ledger's measured membership-quotient cost directly. Merely
symmetrizing Semaev variables, changing elimination order, or evaluating another dense
resultant does not satisfy this fingerprint.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — identifies the degree-`B` membership-quotient arithmetic
   as the dominant prime-field PDP obstruction.
2. `ledger/H-FB-001.yaml` — prevents a different factor-base shape from being called the
   mechanism.
3. `ledger/EV-FB-001.yaml` — supplies the matched yield law and structure-invariance control.
4. `ledger/H-REP-001.yaml` — prevents a coordinate or equation reformulation at unchanged
   solve cost from passing as an exponent change.
5. `ledger/SYNTHESIS-20260716.md` — requires full relation-to-target accounting and
   independent scaling evidence.

## Closest primary literature

- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), establishes the point-decomposition condition that the aggregate divisor query must solve.
- Petit, Kosters, and Messeng, [Algebraic approaches for the ECDLP over prime fields](https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf), studies composed rational-map factor bases and makes low-degree constraint replacement by itself non-novel.
- McGuire and Mueller, [A New Index Calculus Algorithm for the ECDLP](https://eprint.iacr.org/2017/1262.pdf), explores solver-free summation evaluation, so avoiding a Gröbner basis alone is not a novelty claim.
- Gaudry, [Index calculus for abelian varieties of small dimension](https://doi.org/10.1016/j.jsc.2008.08.005), gives the nearby divisor/factor-base framework and its full relation-cost accounting.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, [3SUM with preprocessing](https://arxiv.org/abs/1907.08355), gives nearby preprocessing/query tradeoffs; it is a required baseline, not evidence that elliptic-coordinate witness recovery is easy.

The checked literature does not establish the proposed target-uniform aggregate-support
witness oracle with sublinear dependence on `B`. That is not a novelty proof; novelty
remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `m`, `beta`, a deterministic factor base `F`, its point-ideal product tree, and
   exact encodings for degree-`m` effective divisors and Abel-Jacobi fibers.
2. Build the target-independent aggregate section/complement data structure without
   materializing `F_p[z]/f_F(z)`, an explicit `B^m` tuple table, or target-specific successes.
3. For random known scalars `a`, form `R=[a]P` and query the fiber over `R`; retain every
   miss, ambiguity, repeated point, exceptional divisor, and censored query. Keep `Q`
   out of this base-log collection phase.
4. Accept only a recovered divisor `D=P_1+...+P_m`, with every `P_i in F`, after independently
   verifying `sum_i P_i=R` and the aggregate section identity.
5. Collect at least `B+security_margin` independent rows and solve the sparse linear system
   for all `log_P(P_i)` represented in the accepted divisors.
6. Query the identical frozen structure on randomized target representatives
   `Q+[t]P` until a verified factor-base divisor is recovered; substitute known logs and
   remove `t`.
7. Recover `x mod N` and independently verify `[x]P=Q` on the original instance.

## Full rho/BSGS cost model

Let `B=N^beta`; arity be fixed `m`; target-independent build cost `N^(a+o(1))`; one
aggregate query cost `B^(kappa+o(1))=N^(beta*kappa+o(1))`; reciprocal relation density
`N^(delta+o(1))`; reciprocal target-descent density `N^(delta_t+o(1))`; sparse linear
algebra exponent in `B` be `omega_s`; and stored structure be `N^(s+o(1))` bits,
including every cached field element and product-tree coefficient.

- Pollard rho baseline: expected `sqrt(pi*N/2)=N^(1/2+o(1))` group operations and `O(1)`
  state, apart from constant-factor automorphism gains.
- BSGS baseline: `N^(1/2+o(1))` group operations and `N^(1/2+o(1))` stored points.
- Aggregate build: `T_build=N^(a+o(1))`.
- Relation collection: `T_rel=N^(beta+delta+beta*kappa+o(1))` for `Theta(B)` accepted rows.
- Under the uniform-sum heuristic, `delta=max(0,1-m*beta)`; it is measured, not assumed
  away.
- Sparse linear algebra: `T_LA=N^(omega_s*beta+o(1))`; conservatively `omega_s=2`, with
  memory `N^(beta+o(1))`.
- Individual descent: `T_desc=N^(delta_t+beta*kappa+o(1))`, including all misses and
  witness verification.
- Total bit memory: `M=N^(max(s,beta)+o(1))`.

The complete time exponent is
`lambda=max(a, beta+delta+beta*kappa, omega_s*beta, delta_t+beta*kappa)` and memory exponent
is `mu=max(s,beta)`. For the focal `m=4`, `beta=0.20` arm, the heuristic gives
`delta=delta_t=0.20`, relation exponent `0.40+0.20*kappa`, and linear-algebra exponent
`0.40`; promotion therefore requires approximately `kappa<=0.25`, not merely a solver
faster than the ledger's measured `B^gamma` baseline.

## Likely fatal obstruction

Computing the Abel-Jacobi pushforward of a factor-base indicator is group convolution on
`E(F_p)`, whose useful indexing is the unknown discrete logarithm. Any exact coordinate
implementation may therefore reconstruct the same degree-`B` membership quotient, touch
`Omega(B)` factor-base data per query, or return only a count. Then `kappa>=1`, giving
relation exponent at least `0.60` in the focal arm, before build and memory, so rho wins.

## Proof track

Give an explicit aggregate section/complement identity, prove target-uniform support
intersection and complete witness recovery, and bound build, query, storage, relation
density, sparse solve, and individual descent. Combine the bounds to prove
`lambda<1/2` without an implicit tuple table or quotient algebra.

## Disproof track

Show that exact support intersection requires `B^(1-o(1))` work, that witness recovery is
rho-hard despite cheap counts, that relation density is lower than `B^m/N`, that the data
structure has `N^(1/2-o(1))` build or memory, or that every full-cost parameter choice has
`lambda>=1/2`.

## Positive and negative controls

- Positive control: a cyclic additive group with known scalar coordinates, where the
  factor-base indicator can be convolved by FFT and witnesses can be recovered.
- Positive instrumentation control: exhaustive `Sym^m(E)` enumeration on tiny curves must
  match every aggregate count, miss, multiplicity, and recovered divisor.
- Negative control: random point sets of the same size and matched relation density.
- Negative mechanism control: the ledger's ordinary membership-quotient Semaev solve on
  the identical curve, target, factor base, and arity.
- Count-only control: an implementation allowed to return the number of decompositions but
  not points; it must fail the witness and end-to-end gates.
- Hidden-table control: charge and reject any product tree or cache whose retained size is
  an explicit `B^m`, `N^(1/2)`, or target-indexed decomposition table.
- Preprocessing control: compare build, storage, and online query costs with the applicable
  generic 3SUM/kSUM-with-preprocessing tradeoff at the same base size, while forbidding
  scalar coordinates unavailable in the ECDLP instance.

## Quantitative promotion and falsification gates

The toy preflight uses ordinary prime-field curves at 13, 14, 15, 16, 18, 20, and 22 bits,
at least 20 independent curves per size, `m in {3,4,5}`, and preregistered
`beta in {0.16,0.18,0.20,0.22}`. Exhaustive divisor truth is required through 16 bits.
Promotion requires all of:

- zero incorrect accepted divisors and at least `99.9%` agreement with exhaustive counts
  and misses where truth is available;
- at least 1,000 independently verified relation witnesses and 100 independently verified
  target descents at each of the two largest feasible sizes;
- upper 95% fitted bound `kappa<=0.25` in the focal `m=4,beta=0.20` arm;
- upper 95% bounds `a<=0.45`, `delta<=0.22`, `delta_t<=0.22`,
  `omega_s*beta<=0.45`, and hence full `lambda<=0.45`;
- memory exponent upper bound `mu<=0.45`, with every cache and product-tree node charged.
- the claimed build/query point lies beyond the matched generic preprocessing baseline
  because of an explicit elliptic-coordinate operation, not uncharged advice.

Falsify the scoped prediction if any accepted divisor is wrong, the oracle cannot recover
witnesses, a count/result depends on post-hoc target selection, the lower 95% bound is
`kappa>=0.50` in the focal arm, or every fitted full-cost configuration has lower 95%
bound `lambda>=0.50`. A timeout, implementation error, or unsupported divisor case is not
mathematical evidence against the mechanism.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-012_aggregate_divisor_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-012/aggregate_divisor_query.sage`
- Planned exhaustive oracle: `ideas/artifacts/ECDLP-IDEA-012/exhaustive_symm_power.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-012/runs/<run-id>/`
- Planned raw queries: `ideas/artifacts/ECDLP-IDEA-012/runs/<run-id>/queries.jsonl`
- Planned raw relations: `ideas/artifacts/ECDLP-IDEA-012/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-012/analysis.md`
- Required retained data: recovered divisors, misses, multiplicities, operation counts,
  timings, peak memory, caches, exact seeds, commit, dirty-tree state, stdout, and stderr.

## Interpretation boundary

Every proposed or measured claim is toy, heuristic, model-bound, and novelty-unverified.
A correct section identity, low-cost count, valid relation, or toy decomposition does not
establish an ECDLP improvement. Only verified factor-base-to-target recovery with all
build, density, memory, linear-algebra, and descent costs below rho/BSGS can justify
escalation; crypto-scale claims still require independent replication and review.

## Exactly one next executable action

1. After coordinator approval, execute the frozen aggregate-divisor witness preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-012_aggregate_divisor_preflight.yaml` over its complete preregistered toy matrix.
