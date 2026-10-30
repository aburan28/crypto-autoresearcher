# Legacy ledger YAML parse debt remains in 15 records

- **Status:** `open`
- **Kind:** implementation gap; validation gap
- **Affected work:** exact-main ledger validation, the static dashboard integrity panel, and any downstream audit relying on the 15 baselined ledger records
- **Next action owner:** Coordinator and ledger maintainer
- **Last updated:** 2026-10-26

## Problem

We cannot establish that every archived ledger record is parseable and
semantically reviewable because 15 malformed ledger YAML originals remain in
the repository's legacy parse baseline at main
`6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad`.

The repository requires immutable records and new correction records rather
than edits to archived originals. Its absolute merge-hygiene gate permits a
fixed, shrink-only legacy baseline and hash-verified schema supersessions.
Neither mechanism turns a malformed original into a validated claim. The
dashboard's exact parse sweep lists 24 malformed ledger originals: nine have
verified schema replacements and 15 are still baselined. This blocks an
unqualified statement that the historical ledger is fully parseable or that
all downstream research results have been validated.

## Evidence and uncertainty

- **Observed:** The [2026-10-26 read-only audit](../docs/reports/2026-10-26-ledger-parse-audit/report.md) at exact main SHA `6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad` independently parsed every `ledger/**/*.yaml`, checked source/replacement hashes, replacement parse and ID, and agreed with the merge gate. Its [per-path evidence](../docs/reports/2026-10-26-ledger-parse-audit/evidence.json) records nine verified schema routes, 15 baselined ledger syntax defects, and zero other malformed ledger YAML in scope. The local dashboard build reported the same 24 original paths.
- **Derived or proved:** The classification is a finite, source-bound syntax and registry check. No theorem about the records' research content is established.
- **Suspected explanation:** The defects are historical serialization errors; the baseline names them as pre-existing defects. Their intended exact field semantics require record-by-record review.
- **Missing capability:** Immutable parseable successor records with semantic-fidelity review for each of the 15 baseline entries.
- **What this evidence does not establish:** It does not show that any experiment result is false, that the nine replacement copies preserve scientific meaning, or that the rest of the corpus has complete Lean proof coverage. It does not classify malformed experiment specifications outside `ledger/`.

## What would unblock it

- [ ] For each of the 15 ledger paths in the audit evidence, preserve the original bytes and add a parseable schema-supersession copy with both SHA-256 pins, an exact record-ID check, and independently reviewed semantic fidelity.
- [ ] Remove each successfully superseded path from `tools/merge_hygiene_baseline.txt`; run the absolute merge-hygiene sweep and ledger validator with zero new failures.
- [ ] Rebuild the dashboard at the resulting commit and verify the audit has zero `legacy_parse_baseline` and zero `unresolved` ledger paths. Retired malformed originals may remain visible as archived syntax history.

These conditions establish parseable current routing for the affected ledger
records, not the truth of their scientific claims or completion of the wider
experiment and Lean proof audit.

## Next discriminating step

- **Action or proof obligation:** Supersede one representative baselined ledger YAML file with a minimally changed parseable copy and an independently reviewed text/meaning comparison.
- **Inputs and controls:** The original path and SHA in `evidence.json`, the repository registry and shrink-only baseline, and the already merged schema-supersession pattern in PR #2293. Keep the original untouched; compare the copy to it and use a deliberately mismatched hash as a fail-closed control.
- **Execution limits and stop condition:** One record first; no scientific trial, new instance or spending. Stop if syntax repair would require guessing a field's meaning.
- **Outcomes and next actions:** A passing copy and gates justify repeating the method for the remaining 14 with independent review. Ambiguous semantics keep that record open for source-owner review. A tool or CI failure is infrastructure, not a research verdict.
- **Recheck trigger:** A committed successor, baseline change, or new source evidence for any of the 15 paths.

## Resolution and history

- 2026-10-26: Opened from the exact-main parse and registry audit. No archived ledger record was edited. Unresolved.

Completing this record or merging its PR does not resolve the parse debt or
establish a research result.
