# SNFS-A3 design audit

## Audit basis

- Idea: `IDEA-20261009-f24f8a`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  official hypothesis or experiment status was changed.
- Closest existing records: `EXP-MODEL-5f5f45`,
  `research/factor_base_lab.md`, and the solver/timeout requirements in
  `EXP-ICPERF-2f2e40`.

## Overlap and genuine delta

The proposal is substantially covered by existing factor-base analysis. The
existing coordinate-model contract already separates coordinate-domain size,
rational factor-base cardinality, membership degree, Bézout/Groebner cost,
and lifting cost. It also treats the attractive isogeny-pullback construction
as a rationality and lifting-cost question rather than counting geometric
points as though they were rational.

The genuine new scope is narrower: compare the `x < p^beta` bounded-coordinate
family across pseudo-Mersenne and matched random primes, and measure SAT and
digit-encoded algebraic backends on identical mathematical instances. That is
a finite measurement adaptation, not a new decomposition mechanism. It should
not create a second broad factor-base experiment without an explicit
instrumentation delta and lineage to the existing contracts.

## Cardinality and mathematical-instance contract

The symbol `|F_beta|` is not yet defined tightly enough for the claimed
scaling law. The implementation must record separately, for every cell:

1. candidate coordinate values satisfying the bound;
2. values surviving field and curve membership tests;
3. liftable rational points, including sign and repetition conventions;
4. points in the selected subgroup and any excluded torsion or exceptional
   points;
5. the realized factor-base cardinality `B` used in the decomposition
   equations; and
6. the natural yield and the count of verified decompositions.

The approximation `p^(m beta - 1) / m!` is admissible only after the relevant
group order, factor-base definition, subgroup, and sampling measure are fixed.
Coordinate-domain cardinality cannot be substituted for the number of points
actually available to a relation. Point-level, `x`-level, and relation-level
counts must never be merged.

The SAT and F4/F5 lines are distinct only as backend or encoding measurements
if they solve exactly the same frozen mathematical instance. The record must
specify arithmetic semantics, auxiliary variables, bound constraints,
homogenization, saturation, variable order, and solution extraction for each
encoding. Pseudo-Mersenne arithmetic must be separated from any claimed
decomposition-structure effect by same-domain controls and matched random
prime controls.

## Runnable experiment requirements

The proposed matrix has 168 nominal cells and 3,360 instance runs before
controls, retries, or censored rows. It is not runnable as filed because it
does not freeze:

- the actual primes and the `2^n-c` schedule;
- the mapping of the 20 instances and campaign seeds to every cell;
- solver build hashes, command lines, and supported versions;
- exact SAT, F4/F5, enumeration, and Coppersmith encodings;
- the dependency and admission condition for the A2 Coppersmith line; or
- the availability of Magma and `msolve` in the execution environment.

Only backends that pass an explicit environment/admission check may enter the
main comparison. A solver name in a proposal is not evidence that the solver
is installed, reproducible, or able to emit the required certificates.

The first runnable successor should be a reduced pilot with an explicit prime
schedule, a small fixed set of `beta` and `m` values, verified available
backends, frozen encodings, and a complete artifact path. The readiness gate
is the repository selector:

```text
python3 tools/newest_experiments.py --experiment <repaired-successor-id>
```

The returned `execution_state` must be `ready` before approval. A design that
still needs implementation or environment work remains `review_required`.

## Controls and charged cost

Planted decompositions and natural random targets are different populations.
Planted instances test conditioned solver behavior and should not be used as
the natural relation-collection rate. The repaired contract needs, at
minimum, natural random targets, planted known-answer targets, matched random
factor bases, random-prime controls, same-shape solver/encoding nulls, and
known-false instances. Each control must state which confounder it isolates.

“Full decomposition cost” must include factor-base construction or expansion,
membership compilation, serialization, solver search, model extraction,
point lifting, exact group verification, failed attempts, and retry cost per
verified natural decomposition. Solver-stage timing alone is not an admissible
decomposition-cost measurement.

First-fall degree and degree of regularity are separate diagnostics. The
contract must freeze the ideal, field equations, homogenization, saturation,
and monomial order for both quantities. A memory-limited or timed-out row is a
censored infrastructure outcome, not a measured degree. The analysis must not
silently turn those rows into negative mathematical evidence.

Replace the proposal's broad six-hour median rule with per-instance wall
limits, resident-memory watchdogs, campaign caps, explicit retry policy, and
an a priori rule for excluding censored cells from scaling fits. Report peak
memory as a primary outcome because memory can terminate Groebner and SAT
lines before elapsed time does.

## Claim ceiling

The strongest admissible result is a measured scaling exponent for
`log(T_full)` against realized `log(B)` for the named solver builds, encodings,
prime families, beta values, m values, and completed cells. A fitted exponent
below 0.9 over three sizes, even with a confidence interval, is evidence only
about that declared finite scope.

The experiment cannot establish a universal lower bound, an asymptotic claim
that no solver beats brute force, or a change in ECDLP complexity. A negative
result would close only the tested encodings, solver implementations, primes,
factor bases, sizes, and stopping rules. A censored solver line is not a
failure of the underlying mathematical hypothesis.

## Disposition and next action

Disposition: **keep proposed; do not approve or execute as filed.** The idea
is a medium/high-priority finite measurement only after substantial contract
repair. It is not a second general factor-base mechanism and should remain
linked to the existing coordinate and decomposition records.

Next action: split the successor into two bounded contracts:

1. a cardinality/oracle contract fixing actual primes, realized factor-base
   point counts, natural-yield baselines, planted versus random populations,
   and exact membership/lift certificates; and
2. a reduced solver-comparison contract using only admitted backends, identical
   mathematical instances, same-domain and random-prime controls, complete
   charged costs, memory watchdogs, and explicit censoring.

Only after both contracts are runnable and the readiness selector reports
`execution_state: ready` should the Coordinator consider approval. No claim of
an ECDLP advantage follows from the proposal or from a future finite scaling
fit alone.
