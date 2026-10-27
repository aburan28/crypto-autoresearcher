# Metadata backlog and schema routing repair — 2026-10-27

The requested goal remains every PR merged and latest-main CI passing. This integration preserves the current author heads of #2433, #2536, #2564, #2571 and #2591, alongside the shared CI repair in #2609. It records obstructions and bounded corrections without promoting research outcomes. Exact integrated heads are recorded in integrated-heads.json.

## Conflict and integrity review

Problem-index conflicts retain main’s newer P-256/Prym observations, add each new problem once, and keep the 83/84/87 formal inventories explicitly dated and source-bound. Historical audit counts are not current-head validation claims. The Semaev correction is additive; the frozen target is unchanged. Historical merged #2504 wording is preserved alongside later review findings.

The schema-routing index had two handoff records appended without YAML list markers. PyYAML silently overwrote the preceding decision and first handoff. Separate list records now restore DEC-20261019-624f64, TASK-20261017-2d324f and TASK-20261017-4d744d. The handoff registration dates come from the dated DEC-20261023-5c9671 approval and replacement paths. Both sides of all 238 active bindings match their pinned SHA-256 values. Original and replacement bytes are untouched.

PR #2536’s archived correction for TASK-20261023-e485d9 remains retained, but its proposed active route is obsolete: main commit 30e6dd9e4 already added from/to/role. That current source hashes to be8ba52cc611a58f05e16ab35d7c33fb127612802964e0cc2486129ae3176d0f, while the historical correction names the earlier 466c25ed source. Applying that route would be invalid; its hashes are not rewritten to make it fit.

The registry loader now rejects duplicate YAML keys locally to this mutable index. Other legacy record loaders retain their behavior. Regression controls reject a missing list marker that would replace a preceding record and a repeated registry header.

PR #2564 fixes future run-record string quoting and empty container types. Its three archived malformed manifests remain unchanged and their validity remains unresolved. The formal inventory notes retain claim-fidelity and source-run gaps.

## Validation

- Schema supersession safety tests: 13 passed, including both duplicate-key controls. The CI supersession helper module also imports and passes its available unittest discovery.
- All 238 active schema routes: original and replacement bytes present and SHA-256 matched, no hash errors.
- Future run-record serialization: 3 tests passed, including multiline Git status, string type preservation and empty lists/maps.
- All five named PR heads are ancestors of this integration.

Sources reviewed: AGENTS.md, tools/validate_ledger.py, tools/schema_supersession_registry.yaml, the author PR bodies and exact merge deltas, DEC-20261023-5c9671, CORR-20261024-7c17bf, the current handoff’s Git history, and the existing safe YAML serializer tests. The repair keeps each correction bound to the source it actually describes.

Current-head hosted CI and review remain required. This report does not establish a clean full-corpus ledger, universal theorem fidelity, valid archived S2 results, or completion of the user’s wider backlog request.
