# Independent check plan (preparation interface, EXP-CRYPTO-6505c6)

Status: proposed responsibilities only. No reviewer is assigned, no review has
occurred, and no result is fabricated. This is not a `review_plan` record
under `templates/research-records.md` — the Coordinator preregisters the
actual round, with an owned joint per load-bearing step, a `coordinator_prior`,
`blindness`, and `proves_too_much`, when a genuine proof-producing audit is
ready for claim-changing review. This document only proposes the shape that
future plan should take, drawn from the specification's fixed structure.

## Why a plan is proposed here, not opened

`DEC-20260907-d42056.next_actions` requires: complete preparation and its
snapshot, then rank and assign the actual proof-producing audit, then, before
claim-changing review, preregister independent joint ownership, source scope,
blindness, and prior. This preparation task precedes all of that. What follows
is a candidate allocation of responsibilities the Coordinator can start from —
not a commitment, not a claim of independence achieved.

## Candidate review responsibilities

1. **Addition charts (O02, the 400-cell `chart-coverage.yaml`).**
   Candidate joint: verify disjointness/exhaustiveness of the five ordered
   chart tags (`P_identity, S_identity, secant, tangent, inverse`) over all 25
   ordered pairs per case, and that every claimed-empty cell carries an actual
   incompatibility certificate rather than an omitted boundary.
   Attack surface: two-torsion and identity boundary overlaps, where a
   misclassified case (e.g. affine two-torsion routed to `tangent` instead of
   `inverse`) would silently corrupt coverage.

2. **Sheaf/trace interface (O01, O03).**
   Candidate joint: verify the Kummer and Legendre family definitions,
   normalization, and zero-boundary conventions against the family's actual
   source (purity, trace normalization, pullback behavior for K; rank,
   lissity, geometric constituents, conductor for L), and verify the
   correlation-to-pushforward trace/dagger/dual/integral-weight conventions
   match the source theorem's conventions exactly, not by analogy.
   Attack surface: an unstated sign, shift, or normalization mismatch between
   the source's convention and this specification's declared convention.

3. **Complexity / moment / stratification (O04, O06, O07, O08).**
   Candidate joint: verify the effective complexity bound `C`, the
   all-extension fourth-moment statement and effective `B(C)`, the
   hypothesis-by-hypothesis match against the source's Theorem 2.4, and the
   exceptional-locus dimension/degree and effective `K(C)`.
   Attack surface: importing a finite observed maximum, an n-dependent
   constant, or an ineffective existence statement as if it discharged the
   effective-bound target (explicitly disallowed by
   `specification.main_transfer_target.effective_B`).

4. **Controls (O09, plus `case-15`/`case-16` and matched nulls `case-07`/
   `case-08`).**
   Candidate joint: verify the matched-null rank/ramification/Swan comparison
   is per translated pullback (never forced to a diagonal tensor, never
   assumed small), and verify the constant-sheaf controls are correctly
   rejected by the same cancellation argument used for the main families.
   Attack surface: an argument that happens to also accept the constant-sheaf
   control is invalid by `specification.falsification_criterion`, regardless
   of what it claims for the main target.

5. **Degeneration-base diagnostics (`case-09`..`case-14`).**
   Candidate joint: verify each of the three excluded strata (`D0`, `D1`,
   `D01`) is correctly, disjointly classified and that a degeneration-only
   failure is not reported as a main-target refutation
   (`specification.obligation_matrix.diagnostic_rule`).

6. **Certificate/dependency soundness (O05, O10).**
   Candidate joint: independently re-check the dependency DAG for cycles or
   unjustified reuse, and confirm every certificate anchor resolves uniquely.
   This is closer to a structural check (see `checker-specification.md`
   Section 2) but the reuse-substitution judgment itself is semantic and
   belongs to an independent reviewer, not the mechanical checker.

## Blindness and prior (not yet fixed)

A real plan will need: a stated `coordinator_prior` (what result is expected
before any reviewer reports), `blindness.mutual: true` unless there is a
recorded reason to lift it, and a `proves_too_much` control naming objects for
which the target conclusion is known false (the constant-sheaf controls are a
natural candidate, already present as `case-15`/`case-16`, but the review
plan's `proves_too_much.objects` is a separate declaration the Coordinator
must make when opening the round). None of this is fixed by this preparation
document.

## What this document is not

- Not a claim that any of the above joints has been reviewed.
- Not a list of assigned reviewers or reviewer verdicts.
- Not a substitute for the mechanical checker in `checker-specification.md`.
- Not authorization to begin claim-changing review; that requires a Coordinator
  `review_plan` per `templates/research-records.md` and a genuinely claimed,
  proof-producing audit to review.
