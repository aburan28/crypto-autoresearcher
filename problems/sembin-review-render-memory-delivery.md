# SEMBIN source-custody review renderer stopped with MemError

- **Status:** `open`
- **Kind:** independent source-review delivery obstruction; no scientific finding
- **Affected work:** `GOAL-SEMBIN-5078bc`, `BATCH-c8105a`, reviewer `TASK-20261030-d34252`; dependent archive `TASK-20261030-459b12` remains ineligible
- **Next action owner:** Coordinator
- **Last updated:** 2026-10-30

## Observed failure

The independently admitted reviewer produced three declared UTF-8 review bodies and a Typst source under its exact task session. The pinned Typst 0.15.0 helper set a 2 GiB address-space limit and stopped with a `zlib-rs` 0.6.3 `MemError` panic while rendering the fourth declared output. There is no PDF, same-reviewer four-output completion check, producer landing, or completed release. The original owner published epoch-1 release `failed` at 2026-10-30T22:10:32Z, before the unchanged 22:44:25Z deadline, with an empty artifact hash map. The task is blocked against accidental reoffer; the archive dependency is unchanged.

## Evidence and limits

- The sanitized [epoch-1 incomplete custody manifest](../coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-c8105a/admission/DEC-20261030-99f3aa/epoch-1-incomplete-custody.json) binds the exact private text/source sizes and SHA256 hashes, reviewer turn, render-error digest, and remotely verified failed release. It publishes no partial reviewer body, raw native events or failed-render material.
- The pinned helper uses `RLIMIT_AS=2147483648`. The observed allocation error does not identify whether virtual address reservation, renderer concurrency, or resident memory caused the failure. The prior neutral one-page render did not predict this report's memory demand.
- Reviewer-authored partial text is incomplete administrative custody. It cannot supply a source-review verdict, completed four-output artifact set, scientific claim, or eligibility for `TASK-20261030-459b12`.
- The original reviewer task, epoch and deadline remain historical. No in-place retry, output overwrite, budget reset, or interpretation of the partial text as a completed review is authorized.

## Exit criteria

- [ ] Coordinator separately authorizes a bounded renderer diagnostic on an immutable copy of the reviewer-authored Typst source. Retain a 2 GiB resident-memory ceiling and zero swap, pin exact renderer/font/source hashes, measure peak RSS, and compare settings such as thread count or address-space limit only under an explicit scope. A proposed setting is not a demonstrated fix.
- [ ] Demonstrate one compliant PDF under native artifact policy and the frozen repository size/storage route, with parse, text extraction, page-render and visual checks. Preserve unchanged reviewer content and source provenance; record any renderer warnings and failure cost.
- [ ] If completion remains useful, define a **new disjoint** four-output Validator successor with finite budget, exact source scope, fresh independent task-session admission, accountable writer and claim. The existing archive binds the failed reviewer and needs a separately justified successor archive contract. No automatic retry or old-record rewrite.
