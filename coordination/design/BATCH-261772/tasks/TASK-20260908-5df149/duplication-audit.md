# Duplication audit — `EXP-ECDLP-df24c3`

## Proposed comparator

The supplied handoff identifies `EXP-JINV-606dce` as derived from
`IDEA-20260807-51675e` / `GOAL-ENDO-001`. Its stated purpose is an audit of an
L3 curve-family affected-versus-safe classification, specifically a `j = 0` /
automorphism discount scope within a curve-family table.

`EXP-ECDLP-df24c3` proposes a different object and decision procedure:
ledger-wide selected records with a declared scoped-negative statement and a
run/manifest citation are reconciled field by field against the coverage of the
cited artifact. It emits `clean`, `overbroad`, `unauditable`, or `inconclusive`;
the latter two prevent missing bindings and prose-level generalizations from
being silently treated as scope overstatements.

| Dimension | `EXP-JINV-606dce` | `EXP-ECDLP-df24c3` draft |
| --- | --- | --- |
| Source idea / goal | `IDEA-20260807-51675e` / `GOAL-ENDO-001` | `IDEA-20260815-024cf2` / source-bound ledger corpus |
| Object under audit | L3 curve-family affected-versus-safe classification | Scoped-negative ledger statements and cited run/manifest coverage |
| Domain boundary | `j = 0` / automorphism discount in a curve-family table | Decision/evidence records selected from `ledger/decisions` and `ledger/evidence` |
| Comparison | Classification membership within the L3 table | Typed conclusion-scope vector versus cited-artifact coverage vector |
| Possible disposition | Curve-family classification audit result | `clean`, `overbroad`, `unauditable`, or `inconclusive` record-level disposition |
| Claim boundary | Affected-versus-safe scope of a particular L3 classification | Record-integrity alignment only; no curve, solver, or mathematical result |

## Mechanical non-duplication boundary

The proposals can be called distinct only if the later source-bound corpus index
proves both predicates below:

1. At least one selected statement has no resolved provenance/linkage to
   `GOAL-ENDO-001`, `IDEA-20260807-51675e`, `EXP-JINV-606dce`, or the L3
   curve-family table; and
2. Its verdict is produced by the scope-vector-to-cited-run/manifest comparison
   specified in `EXP-ECDLP-df24c3`, rather than by an affected-versus-safe
   classification lookup.

The implementation must make predicate 1 mechanical by recording, for every
corpus row, its source path, source commit/blob identity, all resolved
goal/idea/experiment linkage fields, and an explicit `l3_curve_family_table`
membership flag. A missing linkage field cannot prove the predicate; it must be
recorded as unresolved. Predicate 2 is mechanical only when the immutable
comparison row includes the two typed vectors, per-field relations, cited
artifact identities, and the comparator version.

## Verdict

**Mechanically unresolved at draft stage; do not call the experiments distinct
yet.** The exact unresolved blocker is that this task has no bound source
commit, no parsed ledger schema/linkage index, and no immutable corpus or
comparison rows. Consequently there is presently no mechanical evidence that
the frozen selector yields a selected negative outside the L3 curve-family
audit, nor that its comparison engine is actually separate from a table
classification lookup.

The semantic distinction above is a testable design boundary, not a completed
duplicate-screen result. If a future source-bound corpus fails either predicate,
the Coordinator must treat this draft as overlapping `EXP-JINV-606dce` and
record the concrete relationship before authorizing work. If it satisfies both,
the evidence supports a control-plane scope-reconciliation audit that is
separate in object, selector, and decision rule.

## Scope and provenance limits

This audit relies exclusively on the parent-supplied internal description of
`EXP-JINV-606dce`, `IDEA-20260807-51675e`, `GOAL-ENDO-001`, and
`TASK-20260908-5df149`. The role independently read none of their source files,
performed no repository traversal, and makes no claim that either proposal has
been run, approved, or reviewed. No external-literature novelty search was
performed; novelty remains unverified.
