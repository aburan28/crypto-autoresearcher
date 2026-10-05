# Curve catalog and provenance delivery

Implementation scope: presentation and read-only adapters only. No research
program, solver, experiment dispatch, research-state transition or deployment.

## Source selection

- Degree 13: existing `ui/benchmarks/cryptanalysis-primary.json`, pinned by
  `ui/benchmarks/catalog.json`. Preserve its existing EC1/full SHA-256 identity.
- Degree 19: exact `field`, `curve` and two endomorphism metadata values copied
  from cryptanalysis commit `f7945bd68b5269c760640bce0adf064789f08c14`, candidate
  `IC1N19Ckb1fb108PDP2xlRCsampleLAgaussTDpdpISO0h990cb5d5d404.json`.
  The capsule records the original source file hash and immutable source link.
  No executable configuration or implementation is imported. Endomorphism
  values are source-reported, not independently proved by the dashboard.
- Comparison: all nine pre-existing primary archive rows, including their exact
  source references and recorded quantities. No fabricated benchmark pair.

The capsule catalog has twelve trait slots. Missing j-invariant/CM fields are
visible unknowns; no algebra is performed to fill them. The two curve records
are distinct representations, not an assertion of equivalence or security.

## Deliberate limits

- The first provenance pass is a citation trail over indexed records, not a
  validation of coordinator archival receipts. It names that coverage limit.
- Only an experiment's explicit `archived` status yields `declared_archived`.
  A completed run or a decision mentioning it does not imply archival or review.
- Benchmark host details and complete cost exclusions are unavailable in the
  existing snapshot. Comparisons therefore remain descriptive with warnings.
- Runtime telemetry production and Pages deployment remain separate operations.

## Review boundaries

1. `ui/curves.py`, pinned capsules and Curves route: exact identity, source
   attribution, unknowns, conflict handling and responsive side-by-side display.
2. `ui/provenance.py`, run path metadata and Provenance route: bounded citations,
   honest archive state, source links and Home follow-up summary.
3. `ui/comparisons.py` benchmark adapter and receipt registration: no loss of
   failures/zero/missing data, explicit units/boundaries, filters and sources.

Validation covers corrupted pins, identity conflicts, conflicting traits, unsafe
paths, invalid numeric metadata, missing receipts, failed rows, zero durations,
static/shared-payload equality, deterministic output and browser interactions.
Full-repository CI remains the integration gate; local work used a focused
source checkout through the authorized GitHub connector.

## Local validation, 2026-10-05

- 128 Python tests passed, including actual HTTP/static parity. One corpus
  calibration test skipped because this checkout contains only selected records.
  One pre-existing telemetry-export test was excluded after its missing
  `orchestration.campaign` dependency prevented execution in the partial checkout.
- 18 DOM tests passed, including curve comparison, filters/deep links, provenance
  gaps, source escaping, failure/unknown/zero handling and missing-curve filtering.
- Chromium/Playwright checks at 390px and 1280px: Curves, Compare and Provenance
  rendered without page-level overflow or JavaScript errors; immutable comparison
  source links rendered. Screenshots were inspected locally.
- Full repository CI and production Pages deployment have not been verified.
