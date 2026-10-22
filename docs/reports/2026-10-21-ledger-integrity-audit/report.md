# Full corpus ledger and dashboard integrity audit — 2026-10-21

**Scope.** The initial audit is a read-only validation of `crypto-autoresearcher`
main `e20013ae20d2c09019d8ea1b2fed7556c61ad4ba`, followed by a local
static dashboard build at audit commit `46d5a90bcdf1e13f449604eed118b69e9b7071ef`.
That commit has no changes to ledger, experiment, knowledge, validator, or UI
inputs relative to that main revision. A full checkout held **138,890 tracked
files**. No scientific trial, benchmark, claim promotion, or performance
measurement was run. [The chart](error-categories.svg) counts validation
messages; it is not a graph of cryptographic performance.

## Full ledger gate

`tools/validate_ledger.py` exited **1** on the complete main tree with **162
unsuppressed validation errors affecting 49 paths**. It separately reported
**1,210 grandfathered legacy errors** suppressed by the repository's
prune-only baseline and **543 non-failing advisories**. The exact
[validator log](evidence/validate-ledger.log) has SHA-256
`8d970c4cc0ccecadc8b84eaea63bdbac5c59850c3daf46b6897aedd6351bf0ca`.
The [classification source](render.py) regenerates the [count JSON](counts.json)
and chart from those lines.

| Validator error class | Lines | Meaning at this stage |
|:--|--:|:--|
| Prior-art metadata | 66 | Malformed or unresolved prior-art maps and nearest-work entries. |
| Review and handoff fields | 32 | Missing blind-review plan components or two handoff budgets. |
| Citation provenance | 28 | `internal` citations without a named source reader. |
| Run-manifest schema | 19 | Missing required run fields or malformed top-level run records. |
| Broken references | 7 | Findings, evidence, or decisions point to unknown task, run, or experiment IDs. |
| Zero-compute stage artifacts | 5 | One hand-derivation stage has no program-output companion files. |
| Experiment-spec fields | 5 | One successor contract is in an experiment specification path, and one approved experiment lacks required criteria and decision impact. |

These are **validator messages**, not 162 independent bad scientific results.
The old baseline is not a clean pass, and this audit did not add to it. The
proof branch changed none of the checked ledger paths or validator rules, and
the same validator log was reproduced byte-for-byte after switching to main.

The five missing-artifact messages require careful treatment. The archived
[`RUN-QSP-33b442-S0` manifest](../../../experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml)
explicitly records **zero compute** and no program execution. It names the
five absent files and says fabricating stdout, a command capture, or a raw
result would misrepresent the stage. Its own note identifies a classification
problem: a hand derivation was filed under a run-record path whose validator
requires program outputs. A schema or namespace decision is needed; the gate
must not be made green by invented files.

## Dashboard and performance data

- The complete-tree reader suite [passed **145 tests**](evidence/ui-tests.log)
  (`test_ui_index.py`, `test_ui_research_views.py`, and
  `test_ui_benchmarks.py`).
- The local static build [emitted **55,218 files, 520.6 MB**](evidence/site-build-report.json)
  at branch commit `46d5a90bcdf1e13f449604eed118b69e9b7071ef`: 27,535
  indexed records, 2,732 experiment records, and no comparison-payload error.
  The [generated payload check](evidence/site-payload-check.json), from
  [this script](check_static_site.py), found all **nine** primary archived
  benchmark rows and no comparison error.
  This was a local build, not a Pages deployment.
- [Direct snapshot crosscheck](evidence/primary-snapshot-crosscheck.json)
  compared six identity or measured fields on each of the nine rows against
  the pinned cryptanalysis JSONL: **54 comparisons, zero mismatches**. The
  [replay script](check_primary_snapshot.py) checks both source and snapshot
  SHA-256 first. As of the [read-only current-main check](evidence/cryptanalysis-main-archive-check.json),
  the primary archive Git blob on cryptanalysis main was still identical to
  the blob used by the pinned snapshot. Scratch-only
  [negative controls](evidence/negative-controls.json) confirmed that a
  changed source hash and an injected dashboard payload error are rejected.
- The generated reader's integrity payload reports **24 unparseable historical
  source files**. A [source-bound classification](evidence/unparseable-classification.json)
  found **nine** with parseable replacement records already present in the
  schema-supersession registry; both original and replacement SHA-256 values
  match the registry. **Fifteen** have no registered replacement. The reader's
  deep scan still reports the nine originals as unparseable, and its canonical
  detail lookup still reads the original path. The [reader coverage problem](../../../problems/dashboard-unparseable-archive.md)
  records the exact paths and acceptance conditions. The integrity payload also
  displays other reference and ID warnings; those individual warnings were not
  adjudicated here. A successful reader build does not clear the red ledger gate.
- The separate [progress dashboard output](evidence/progress-dashboard.json)
  has zero claims and zero frontiers because this checkout's `claims/` contains
  no claim JSON files. Its fidelity/dashboard unit suite passed **12 tests**.
  An empty progress dashboard is a faithful rendering of that source directory;
  it is not evidence that the historical prose contains no performance claims.
- The [public Pages status check](evidence/live-pages-status.json) found the
  workflow **manually disabled** and the live dashboard still showing commit
  `bb9e9f01f3f9fcdf6e456acd7e01cd9af6c05bc3`, built on 2026-10-11.
  The local October 21 build has **not** been deployed. The
  [Pages freshness problem](../../../problems/pages-workflow-disabled-live-snapshot-stale.md)
  records the hosted acceptance conditions and the unknown reason for the
  manual disable.

The [catalog pin](../../../ui/benchmarks/catalog.json),
[snapshot](../../../ui/benchmarks/cryptanalysis-primary.json), and nine
[receipt pointers](../../../ui/receipts.json) were checked. No canonical
numerical graph or performance dashboard datum was changed: the audited
primary archive bytes are unchanged, and this pass generated no new timing.
Other historical archives, graphics, and performance claims were not
independently replayed by this dashboard check.

## Follow-on reader correction on this audit branch

The later reader change displays a registered, parseable schema copy in a
**separate tab** when the canonical YAML does not parse and both original and
copy bytes match the supersession registry hashes. For the 15 malformed
originals without a registered copy, the detail payload explicitly says
`raw_only`: structured fields remain unverified. The canonical path, raw
source, parse error, and integrity warning remain visible in either case.
A hash match does not establish semantic fidelity or the truth of the
scientific conclusion. Changed-source, changed-copy, and missing-copy
controls show no parsed copy.

After merging main `cf9c9ee46c2afa99213024f6744f9a14a05d8e3b`, the
reader suite [passed **146 tests**](evidence/supersession-ui-tests.log). The
complete local build from reader-code commit
`b5b0b52b7cd13d52ef7840ff6023205427b5073d`
[emitted **55,248 files, 520.9 MB** and **27,550 records**](evidence/supersession-site-build-report.json)
([build log](evidence/supersession-site-build.log)). Its deep scan still counted
**24** unparseable originals. The [generated-detail checker](check_supersession_readback.py)
verified [all 24 detail payloads](evidence/supersession-readback.json): nine
separate copies, 15 raw-only states, 24 retained parse warnings, and 24 exact
canonical source texts. The [current classification](evidence/supersession-unparseable-classification.json)
still has nine hash-verified replacements and 15 without a registered
replacement. The [generated comparison check](evidence/supersession-site-payload-check.json)
found all nine primary benchmark rows with no payload error. The generated
`app.js` exactly matches the reader source. This host has no Node or browser
runtime to exercise the tab interactively. No measured result or numerical
graph changed.

The [source-bound parser inventory](evidence/unregistered-parse-errors.json)
records the 15 original hashes, byte counts, parser locations, and lack of
current schema-supersession route. Fourteen are root-level `ledger/` records;
one is a malformed correction record. Those path classes are outside the
current registry kind policy. A prospective route and independent semantic
review are still needed; the raw-only label is an honest unsupported state,
not a correction.

The full ledger gate was repeated at merged commit `b5b0b52b7c`. The
[new log](evidence/validate-ledger-merged-20261022.log) and
[delta checker](check_gate_delta.py) show the **same 162 unsuppressed error
lines in 49 paths**, with no baseline growth; non-failing advisories rose
from 543 to **545** because two more handoff advisories appeared. The
[machine comparison](evidence/merged-gate-delta.json) records both log hashes.
The [October 22 public-site recheck](evidence/live-pages-status-20261022.json)
still found the Pages workflow manually disabled and the live metadata at
the October 11 commit. This build is local and has not been deployed.

## Consequence and next step

The repository is **not yet clear for an end-to-end integrity claim or a
current public dashboard**. The
[problem record](../../../problems/full-ledger-validation-errors.md) names
the exact repair conditions. Archived records must be preserved; corrections
belong in the existing supersession routes or a prospective schema change
with controls. Unknown references and missing criteria need real source
evidence, not guessed values. Re-run the full gate after each repair and
require **zero unsuppressed errors without growing the baseline**.
The separate [draft-reference correction PR #2454](https://github.com/aburan28/crypto-autoresearcher/pull/2454)
proposes a source-bound repair for five of the seven broken-reference lines;
its full-tree comparison leaves 157 errors and the gate red. The chart above
remains the exact count for the audited main commit.

The separate [four-target Lean PR #2450](https://github.com/aburan28/crypto-autoresearcher/pull/2450)
closed the frozen file-presence queue and machine-verified all 66 targets.
Its receipts still require independent semantic review. Neither those Lean
proofs nor this reader build validates all historical experiments or their
reported attack costs. The [PDF](report.pdf) embeds the count chart and scope.

## Reproduction

```sh
python3.12 tools/sparse_checkout.py disable
/path/to/python-with-pyyaml tools/validate_ledger.py
/path/to/python-with-pytest -m pytest -q \
  tests/test_ui_index.py tests/test_ui_research_views.py tests/test_ui_benchmarks.py
/path/to/python-with-pyyaml -m ui.build --out /var/tmp/current-site \
  --report /var/tmp/current-site-report.json
python3.12 docs/reports/2026-10-21-ledger-integrity-audit/check_supersession_readback.py \
  . /var/tmp/current-site \
  docs/reports/2026-10-21-ledger-integrity-audit/evidence/unparseable-classification.json
python3.12 docs/reports/2026-10-21-ledger-integrity-audit/classify_unregistered.py \
  . docs/reports/2026-10-21-ledger-integrity-audit/evidence/unparseable-classification.json
python3.12 docs/reports/2026-10-21-ledger-integrity-audit/check_primary_snapshot.py \
  /path/to/cryptanalysis-primary.jsonl
python3 docs/reports/2026-10-21-ledger-integrity-audit/check_unparseable.py \
  . /var/tmp/current-site/data/integrity.json
python3 docs/reports/2026-10-21-ledger-integrity-audit/check_gate_delta.py \
  docs/reports/2026-10-21-ledger-integrity-audit/evidence/validate-ledger.log \
  docs/reports/2026-10-21-ledger-integrity-audit/evidence/validate-ledger-merged-20261022.log \
  e20013ae20d2c09019d8ea1b2fed7556c61ad4ba \
  b5b0b52b7cd13d52ef7840ff6023205427b5073d
python3 docs/reports/2026-10-21-ledger-integrity-audit/check_live_pages.py \
  --build-report docs/reports/2026-10-21-ledger-integrity-audit/evidence/supersession-site-build-report.json
python3 -m tools.progress_dashboard claims --json /var/tmp/progress-dashboard.json
```

The validator's nonzero exit is the recorded result, not a reproduction
failure. Use the cryptanalysis archive at snapshot source commit
`5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14` for the direct crosscheck.
Rebuild the chart and PDF with `render.py` from this report directory using
`svglib`, `reportlab`, and `tectonic`; the script classifies every one of the
162 validator lines or fails.
