# Independent check plan (EXP-CRYPTO-6505c6, preparation only)

This document proposes review **responsibilities** for a future,
Coordinator-preregistered independent review round. It names no reviewers
and reports no review results, because no review has happened yet. It is a
plan, not a receipt.

## Scope split: mechanical vs. semantic

Per `checker-specification.md`, mechanical schema/hash/coverage checks
(section 2 there) can be run by anyone or by a script and establish
structural consistency only. The responsibilities below are all **semantic**
review surfaces: they require genuine mathematical expertise applied to
actual source material and actual proof text, and none of them exist as
completed work at this time.

## Proposed review surfaces

1. **Addition-chart geometry** (25-cell panel per case, 400 cells total)
   - Responsibility: verify the five ordered addition cases (`P_identity`,
     `S_identity`, `secant`, `tangent`, `inverse`) are actually disjoint and
     exhaustive over the declared domain, that empty-cell claims carry an
     actual proof/certificate (not an omission), and that the global
     zero/lisse boundary convention is applied without overlap.
   - Depends on: `symbolic-fixtures.yaml` chart-tag definitions in this
     bundle; future `chart-coverage.yaml`.

2. **Sheaf / trace interface** (families K and L; correlation pushforward)
   - Responsibility: verify the Kummer sheaf `L_chi` and Legendre-derived
     `R^1` definitions, purity, trace normalization, and pullback behavior
     against actually-read primary sources; verify the correlation-to-
     pushforward trace formula, dagger/dual identification, and
     zero-extension convention (`j_!`) are used exactly as the frozen
     specification requires, with no silent substitution.
   - Depends on: future `source-hypothesis-matrix.yaml`,
     `normalization-and-weights.yaml`.

3. **Complexity / moment / stratification claims**
   - Responsibility: verify the embedded-complex complexity bound `C` is
     actually the source-defined quantity (not conflated with curve
     conductor, rank, or a different derived-complex complexity); verify any
     claimed all-extension fourth-moment bound `B(C)*q_n^5` is effective and
     uniform in `n`, not an observed finite maximum or an ineffective
     existence statement; verify every hypothesis of the cited stratification
     theorem (source Theorem 2.4, per the specification) is actually checked
     for this embedded `X` and complex, including the exceptional locus
     dimension/degree bound `D(C)` and off-locus constant `K(C)`.
   - Depends on: future `complexity-ledger.yaml`, `moment-certificates.yaml`,
     `stratification-application.yaml`.

4. **Controls** (matched nulls, constant-rank negative controls, excluded
   base strata)
   - Responsibility: verify each matched-null case's translated-pullback
     comparison (rank, translated ramification support, local
     inertia/tame/Swan data, conductor totals) against its corresponding
     generic-main object, with an explicit certificate for any claimed
     match, and confirm a missing required match is recorded `OPEN` rather
     than silently resolved; verify the two constant-rank controls (`C1`,
     `C2`) actually expose full-parameter-support correlation and are
     actually rejected by the cancellation argument (not merely asserted
     rejected); verify each of the three excluded base strata
     (`D0`, `D1`, `D01`) is classified with an exact disjoint-base
     determination and an explicit chart/shared-geometry outcome or open
     obligation.
   - Depends on: future `control-results.yaml`, `shared-constituents.yaml`.

## What this plan does not do

- It does not name individuals, teams, or model identities as reviewers.
- It does not report any pass/fail/verdict for any surface above.
- It does not authorize a claim-tier or hypothesis-status change; that
  remains a separate Coordinator decision after the review actually runs.
- It does not replace the Coordinator's duty to preregister the actual
  review round (participants, independence from the audit's producer,
  scope, and timing) before that round begins.

## Status

All four surfaces above are **unassigned and unreviewed**. This plan exists
so that a future Coordinator-preregistered review round has a concrete,
scope-complete starting checklist; it carries no evidentiary weight by
itself.
