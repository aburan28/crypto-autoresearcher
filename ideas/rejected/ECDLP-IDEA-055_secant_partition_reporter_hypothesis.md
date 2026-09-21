# ECDLP-IDEA-055 — Secant partition reporter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_merged`
- Evidence scale: `toy` reasoning and preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: exact merge with existing secant-pencil and
  point-hyperplane incidence reporters; candidate generation is not the surviving
  obstruction in the closest ledger lane.
- Breakthrough claim: **none**; an exact partition tree, reported incidence, valid
  relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a factor base `F` of size `B=N^beta` on an ordinary prime-field curve, the rejected
proposal asserted that finite-field polynomial partitioning of the secant parameter
space gives a complete reporter for pairs `(A,B)` whose sum lies on a target-conditioned
complement surface. The reporter would emit all atom sources with preprocessing,
relation collection, rank, separate target descent, output, and bit-memory exponents
below `1/2`.

The closest ledger experiments already compile secant-origin root pencils and exact
point-hyperplane incidence reporters. They show that exact candidate incidence can be
made cheap enough that relation density, independent rank, and source/descent cost—not
the reporter data structure—become the bottleneck. Polynomial partitioning therefore
does not constitute a new mechanism under the recorded scope.

## Mechanism-new operation

The proposed operation was to embed each factor-base pair or secant into a bounded-
degree affine/projective parameter space, recursively partition that space by public
polynomials, and answer a target complement query by visiting only crossed cells and
reporting exact secant witnesses.

After audit, this is a query-engine substitution for the ledger's exact Plucker,
root-pencil, and transposed-incidence formulations. It neither changes the relation
support law nor guarantees reusable factor rank. It could justify a new ID only if a
partition polynomial follows from elliptic addition geometry and proves polynomial
support concentration or rank augmentation absent from matched random incidence data.

## Assumptions

- The curve, factor base, secant parameterization, exceptional tangent/vertical cases,
  partition polynomial, recursion depth, and query rule are frozen before targets.
- Every pair represented in multiple charts is canonicalized without losing source
  multiplicity or sign information.
- Partition construction, finite-field roots, boundary cells, report output, false
  positives, relation verification, rank, descent, and memory are charged.
- A point-hyperplane incidence is not counted as an ECDLP relation until its atoms and
  sum verify independently.
- Finite tests and fitted slopes are toy, heuristic, model-bound, and
  novelty-unverified.

## Semantic fingerprint

`elliptic_factor_base_secants | finite_field_polynomial_partition | complete_target_incidence_reporter | source_witness_output | relation_rank_and_descent`

Collision fingerprint:
`secant_root_pencil | Plucker_point_hyperplane_incidence | exact_reporter | unchanged_density_and_rank_obstruction`

## Five closest ledger entries

1. `ledger/H-FB-001.yaml` — requires factor-base geometry to change scaling rather than only reorganize the same pair set.
2. `ledger/EV-FB-001.yaml` — supplies matched structure/yield controls for any claimed incidence concentration.
3. `ledger/H-REP-001.yaml` — prevents a new incidence representation from receiving exponent credit by itself.
4. `ledger/FINDING-PF-IC-001.md` — charges complete relation generation, linear algebra, and descent against rho.
5. `ledger/SYNTHESIS-20260716.md` — preserves the scoped-negative and toy-versus-cryptographic boundaries.

## Closest primary literature

- Guth and Katz, [On the Erdős distinct distances problem in the
  plane](https://doi.org/10.4007/annals.2015.181.1.6), supplies the primary polynomial-
  partitioning paradigm; its real-incidence setting does not provide this finite-field
  source reporter.
- Stevens and de Zeeuw, [An improved point-line incidence bound over arbitrary
  fields](https://arxiv.org/abs/1609.06284), gives a primary finite-field incidence
  boundary relevant to secant queries.
- Semaev, [Summation polynomials and the discrete logarithm
  problem](https://eprint.iacr.org/2004/031), supplies the elliptic relation variety to
  which the reporter would have to connect.

These works do not establish that polynomial partitioning changes elliptic relation
density, source rank, or descent cost. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `F`, its known point labels, pair canonicalization, secant/tangent charts,
  partition degrees, recursion, boundary handling, and report order.
- Build the partition/reporting structure over all factor-base secants while charging
  every pair or implicit construction operation and retained bit.
- For known-scalar random shifts `R=[r]P`, formulate the exact complement incidence
  query and report every candidate secant source, including boundary and exceptional
  cells.
- Recover explicit factor-base atoms, independently verify their sum to `R`, and retain
  every miss and false report.
- Collect enough independent verified rows to solve all factor-base logarithms; do not
  credit repeated secants or rank-duplicate rows.
- Query the unchanged structure on `Q+[t]P`, recover and verify explicit atoms,
  substitute factor logs, remove `t`, and verify `[x]P=Q`.
- Compare the complete pipeline with the exact root-pencil/point-hyperplane reporter and
  matched random incidence controls.

## Full rho/BSGS cost model

Let `B=N^beta`; partition preprocessing cost `N^(a+o(1))` and memory
`N^(s+o(1))`; one complete incidence query including report output cost
`N^(q+o(1))`; reciprocal verified relation density be `N^(delta+o(1))`; average
reported candidates be `N^r`; and masked-target density/query exponents be
`delta_t,q_t`. Explicit pair materialization has control exponent `2*beta`.

- Pollard rho: `N^(1/2+o(1))` group operations and negligible asymptotic memory.
- BSGS: `N^(1/2+o(1))` time and `N^(1/2+o(1))` memory.
- Partition construction: `N^(a+o(1))`, with `a>=2*beta` if all secants are
  materialized.
- Relation collection: `N^(beta+delta+max(q,r)+o(1))` to obtain `Theta(B)` usable
  independent rows.
- Sparse linear algebra: `N^(2*beta+o(1))` time and `N^(beta+o(1))` memory; dense
  fallback exponent is `3*beta`.
- Target descent, complete output, and verification: `N^(delta_t+max(q_t,r)+o(1))`.

The complete time exponent is
`lambda=max(a,beta+delta+max(q,r),2*beta,delta_t+max(q_t,r))` and bit-memory exponent
is `mu=max(s,beta)`. Promotion requires upper 95% bounds `lambda<1/2` and `mu<1/2`
against both rho and BSGS. A sublinear query bound cannot compensate if relation density
or independent-rank yield retains the generic support exponent.

## Likely fatal obstruction

Over finite fields, partition cells need not have the real-topological separation used
by polynomial partitioning, and boundary varieties can contain a large fraction of the
points. More decisively, the ledger's exact incidence generators already make candidate
generation non-dominant in the closest cover/secant lane. Faster reporting leaves the
generic relation probability, fresh-column rank deficit, and individual descent
unchanged; report output itself can be quadratic.

## Proof track

Prove a finite-field partition theorem for the exact secant set with complete source
reporting, boundary control, and query/output exponent below the existing reporter.
Then prove that the same geometry increases verified independent-rank yield or reduces
relation/descent exponents so the complete `lambda,mu` bounds are below `1/2`.

## Disproof track

Show that the partition reporter enumerates the same incidence set at the same output
size; boundary cells contain generic-scale mass; relation/rank yield matches randomized
secants; or complete collection/descent retains exponent at least `1/2`. Equivalence to
the existing root-pencil or Plucker reporter confirms the merge.

## Positive and negative controls

- Positive reporter control: planted low-degree point-line incidences with known complete
  reports and small boundary sets.
- Positive elliptic control: exhaustive secant/tangent truth on tiny curves, including
  vertical, repeated-point, and exceptional branches.
- Negative geometry control: randomized point/hyperplane sets with matched dimensions
  and density.
- Mechanism control: the exact root-pencil/Plucker reporter on identical inputs.
- Rank control: shuffle row coefficients while preserving relation count and support.
- Leakage control: forbid target-conditioned partition polynomials, recursion, or report
  truncation.

## Quantitative promotion and falsification gates

A counterfactual preflight would cover at least 24 ordinary curves per 10--20-bit size,
factor bases `B=16..512`, three frozen partition-degree schedules, exhaustive pair and
incidence truth through 16 bits, at least 1,000 verified relations, and 100 masked
descents per largest cell. Reconsideration requires zero missed incidences or invalid
sources, at least 99% planted-report recall, full factor rank, independent-rank yield at
least `1.5x` the matched random/control reporter on both largest sizes, and upper 95%
bounds `lambda,mu<=0.45`. Falsify if the reporter is incidence-equivalent without a
rank/density change, boundary/output exponent is at least `0.50`, or any lower 95%
complete-pipeline exponent reaches `0.50`.

## Artifact plan

- Equivalence report: `ideas/artifacts/ECDLP-IDEA-055/reporter_equivalence.md`
- Frozen partitions: `ideas/artifacts/ECDLP-IDEA-055/partitions.jsonl`
- Complete reports: `ideas/artifacts/ECDLP-IDEA-055/incidences.jsonl`
- Source/rank replay: `ideas/artifacts/ECDLP-IDEA-055/relation_rank.jsonl`
- Planned audit runs: `ideas/artifacts/ECDLP-IDEA-055/runs/<run-id>/`
- Cost analysis: `ideas/artifacts/ECDLP-IDEA-055/cost_model.json`
- Required retained data: factor-base points, secants, partition polynomials, boundary
  cells, all reports, sources, ranks, descents, seeds, commands, environment, resources,
  stdout, stderr, and checksums.

## Interpretation boundary

This record is rejected and merged. It is toy, heuristic, model-bound, and
novelty-unverified. An incidence theorem, exact reporter, valid relation, or toy scalar
does not establish a speedup. A new ID requires a mathematical operation that changes
relation support or reusable rank, not another reporter for the same secant incidences.

## Exactly one next executable action

1. Replay exhaustive 8--14-bit secant instances through both the proposed partition reporter and the existing exact root-pencil/point-hyperplane reporter, and record a merge certificate if their source incidence multisets are identical.
