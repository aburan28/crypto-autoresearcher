# Research progress and receipt comparison UI

Implementation scope: read-only UI and measurement presentation. No experiments
are launched, no research state is changed, and fixture results are not scientific
evidence. The September 28 development brief's three actions are implemented in
one reviewable change:

- [x] Home progress panel with observed time window, stale/unavailable states,
  aggregate actions, validated-output delta, handoff latency, cost and coverage.
- [x] Two-receipt comparison with source pins, scope/accounting labels, incomplete
  and incompatible states, and URL-preserved selections.
- [x] Zero-duration accounting in experiment totals and client rendering.
- [x] Python, HTTP/static parity, and browser-DOM regression checks.
- [ ] Supply an operational progress snapshot to the production Pages build.
- [ ] Register a real archived comparison package after its immutable sources
  are available in this repository. The checked-in catalog is intentionally empty.

## Supplying progress

The UI does not read a supervisor's private state directory. An explicit,
read-only exporter reuses `orchestration.campaign.autopilot.report()` and prints a
small allowlisted JSON object. It neither starts a supervisor nor writes its state.

```sh
python -m ui.progress --state-dir .git/autoresearch-autopilot > /tmp/progress.json
python -m ui --progress-snapshot /tmp/progress.json
python -m ui.build --progress-snapshot /tmp/progress.json --out site
```

Both hosts also accept `ui/progress.json` by default (gitignored). For a long-lived
local server, refresh the supplied file atomically; opening Home again reads it.
For Pages, provide a reviewed snapshot file to the build job and pass
`--progress-snapshot`. Transport from the worker host is deployment configuration,
not implemented by this UI change. No new cloud credentials or services are needed
by the reader itself. Do not copy raw state/log directories into the site.

The exporter retains only numeric aggregate fields, numeric coverage fractions,
and observation timestamps. The consumer applies the same allowlist again. No
prompts, worker output, environment paths, errors, or credentials are published.
Malformed or absent input produces `available: false` with null metrics. A cost
or trial delta with no observed coverage stays null. A measured zero stays zero.

The window is the 24 hours ending at `generated_at`, not the viewer's current
24 hours. The latest event time is shown separately. A snapshot/event older than
one hour is marked stale by both the payload and the browser; rebuilding the site
does not make old observations fresh. Missing files do not mean zero activity.
Verified discoveries and independent relations stay null until a scientific
receipt joiner exists; this change does not implement that joiner.

## Registering receipts

`ui/receipts.json` is a schema-1 catalog with at most 100 explicitly selected
receipts. Each entry names the existing `groebner_compare` schema-1 backend
summary and frozen manifest. Every source has a repository-relative path and a
SHA-256 of its **exact file bytes**:

```json
{
  "schema": 1,
  "receipts": [
    {
      "id": "unique-reader-id",
      "label": "Archived backend measurement",
      "summary": {"path": "path/to/backend-0/summary.json", "sha256": "64 lowercase hex characters"},
      "manifest": {"path": "path/to/manifest.json", "sha256": "64 lowercase hex characters"},
      "events": {"path": "path/to/backend-0/events.jsonl", "sha256": "64 lowercase hex characters"},
      "host": {"path": "path/to/host.json", "sha256": "64 lowercase hex characters"}
    }
  ]
}
```

The example is a shape, not an actual catalog entry. Compute pins from the
archived files, then commit the catalog and sources together so commit-pinned
GitHub source links resolve. Never overwrite a historical receipt to fit this
adapter. Synthetic UI controls belong in tests; set `fixture: true` if one is
explicitly registered for a separate demo.

`summary` and `manifest` are required. `events` supplies worker-attempt outcome
counts (including failures and timeouts); without it those counts say *Not
supplied*, not zero. `host` supplies recorded Python/platform and a digest of the
harness source-hash map; without it the view flags missing provenance. Command
arrays, host cwd, raw responses, and equations are not copied into the payload.
The dashboard does not execute a command from any receipt.

The adapter checks each byte pin, the summary's canonical manifest digest,
backend membership, result identity/order and counts. Missing sources, altered
bytes, paths outside the repository, or inconsistent rows are reported and
excluded. Incomplete summaries remain visible as incomplete. A hash match proves
binding to the selected bytes, not that the measurements or verification claims
are scientifically correct. The view explicitly labels verification as recorded
in the receipt.

Selections live in `#/compare?a=<id>&b=<id>`. A comparison requires the same full
manifest (a deliberately conservative rule), scope, accounting boundary and
recorded environment to display a matched label. Different/absent metadata,
unknown verification, incomplete inputs and fixtures produce visible cautions.
No winner, speedup ratio, hypothesis transition or full-algorithm claim is inferred.
Current host receipts do not attest identical physical hardware; the matched
label is only about the metadata actually displayed.

The comparison table works offline from bundled `data/comparisons.json`. Its
original-source links require GitHub access, as do existing committed-source
links elsewhere in the dashboard. All displayed measurements and source pins
remain available offline. No synthetic measurements are bundled into production.

## Contract and validation

- `data/progress.json`: allowlisted snapshot or explicit unavailable state.
- `data/comparisons.json`: normalized, pinned receipts and sanitized read errors.
- `ui/payloads.py`: shared entry points for the local server and static builder.
- Existing experiment payloads: zero seconds counts as a measured run and remains
  distinct from a missing duration in totals and in the UI.

```sh
python -m pytest tests/test_ui_index.py tests/test_ui_ops.py -q
npm ci --prefix ui --ignore-scripts
npm test --prefix ui
```

Tests include raw-log exclusion, stale and missing telemetry, zero costs and
zero durations, receipt hash/identity mismatches, path escapes, incomplete
results, absent journals, actual HTTP/static payload parity, deep links, source
links, escaped rendering, and network retry. The Pages build checks both new
payload files exist. Real-corpus scanner calibration requires a full ledger
checkout and runs in the existing Pages CI job.

## Validation recorded for this change

- Local targeted suite: 116 Python tests passed; two real-ledger calibration
  checks skipped because this checkout is sparse.
- Client suite: 12 DOM tests passed.
- Headless Chromium: Home, Compare and Experiments checked at 1440, 390 and
  320 pixels; no JavaScript errors or whole-page horizontal overflow. The
  comparison table scrolls within its own region. Screens used synthetic test
  fixtures, not production telemetry or research measurements.
- Base inspected: `0e8e8c5eb00ad8d32aedf5be43cf87e569b3e4f8` on `origin/main`;
  no UI overlap was present when preparing the PR. Full corpus/build validation
  remains the Pages CI job's responsibility.
