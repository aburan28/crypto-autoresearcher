# Legacy adapter output preservation and timing validation

- **Status:** `investigating`
- **Kind:** implementation gap; prospective source-binding requirement
- **Affected work:** [PR 2397 qualification](../docs/reviews/pr2397/qualification.md), the five frozen plans binding `tools/legacy_trial_manifest.py`, and the two plans binding `tools/legacy_stage0_manifest.py`.
- **Next action owner:** Coordinator for prospective source binding; Executor only after native admission.
- **Last updated:** 2026-10-20

## Problem

The original two-output adapter can discard undeclared child output and accept inconsistent timing; both original temporary-directory adapters can delete scratch output when preservation fails with an I/O error. Existing approved plans remain bound to those original sources. The corrected prospective versions have no execution authorization under those plans.

## Evidence and uncertainty

- **Observed:** synthetic controls reproduce deletion of an extra binary file and acceptance of negative wall time/reversed timestamps in the original two-output adapter. The original sources and their SHA256 bindings are recorded in the [two-output proposal](../docs/reviews/pr2397/proposed-source-binding.json) and [three-output proposal](../docs/reviews/pr2397/proposed-stage0-source-binding.json).
- **Derived:** explicit cleanup after output and receipt persistence retains scratch on injected read/copy/receipt-write failure. The two prospective suites pass 48 tests and 29 subtests; they use synthetic metadata producers and temporary repositories.
- **Uncertainty:** these counterexamples do not show that any retained historical run lost undeclared bytes or contains inconsistent timing. No historical result is reclassified on that basis.
- **Missing capability:** prospective Coordinator source bindings and approval for the new adapter paths; exact-head CI remains separate.
- **Scope:** schema completion for six retained invalid manifests preserves their invalid status, native receipts, unknown fields and null scientific conclusions. It does not retrospectively accept those attempts.

## What would unblock it

- [x] Supply versioned adapters and independent regression review without editing approved source or frozen plans.
- [x] Preserve scratch when copying or receipt persistence fails; reject inconsistent timing and undeclared outputs in the two-output successor.
- [ ] Bind the exact successor source hashes in a new complete, approvable packet through the Coordinator, retaining `execution_authorized: false` in these proposals until that separate authority exists.
- [ ] Pass applicable checks for the resulting source revision and native admission before any future execution.

These conditions address adapter integrity. They establish no mathematical certificate, performance improvement or scientific transition.

## Next discriminating step

The Coordinator can inspect the two proposed bindings, their retained-original hashes and synthetic tests, then prepare a prospective packet if justified. A source/hash or admission mismatch keeps execution refused. This PR review runs software fixtures only and does not launch either research adapter against an experiment.

## Resolution and history

Unresolved pending prospective binding. On 2026-10-20 independent review approved the additive adapter and schema corrections. Frozen inputs, original run evidence and scientific status remain unchanged. The existing scientific graph edges and claim sources were checked for impact; this operational integrity correction changes none of them, so no scientific graph is regenerated.
