# Dashboard cannot parse 24 archived source files

- **Status:** `open`
- **Kind:** historical YAML and reader-correction coverage gap
- **Affected work:** [2026-10-21 dashboard audit](../docs/reports/2026-10-21-ledger-integrity-audit/report.md), [`ui/index.py`](../ui/index.py), and claims that every archived ledger item is readable in the dashboard
- **Next action owner:** dashboard maintainer and ledger correction owners
- **Last updated:** 2026-10-21

## Problem

The complete local static build succeeds, but its deep scan reports **24
unparseable original YAML files**. Nine of those have registered schema
supersessions whose original and replacement SHA-256 values match and whose
replacement YAML parses. The reader's integrity scan still counts the
originals as unparseable, and canonical detail lookup reads the original
path, so a valid replacement is not automatically shown to a reader. The
remaining **15** have no registered replacement: 14 old root-level ledger
records and `ledger/corrections/CORR-20260727-004.yaml`.

## Evidence and uncertainty

- **Observed:** The [classification result](../docs/reports/2026-10-21-ledger-integrity-audit/evidence/unparseable-classification.json)
  lists all 24 source paths, the nine replacement paths, and the 15 uncovered
  paths. The [checker](../docs/reports/2026-10-21-ledger-integrity-audit/check_unparseable.py)
  refuses an incomplete deep scan, missing replacement, changed original or
  replacement hash, or unparseable replacement. The input `integrity.json`
  has SHA-256 `ae7bb867d5f6a3b6ce9d49599b0a1c2b00fd3afb556d654c96c1b105d6e24fd2`.
- **Derived or proved:** Nine parse failures concern original files whose
  exact bytes are already source-bound to valid replacements. Fifteen have
  no entry in the current supersession registry. Neither count says the
  underlying scientific conclusion is true or false.
- **Missing evidence:** The 15 uncovered files need individually reviewed
  content corrections or a documented reason they must remain raw. A
  correction route for the malformed correction record itself needs design.
- **What this does not establish:** It does not demonstrate that the nine
  replacements are semantically faithful, nor that every dashboard reference
  and graph is correct. The separate ledger gate and hosted Pages state remain
  open.

## What would unblock it

- [ ] Preserve all archived originals and independently review each proposed
  replacement against its source intent; bind source and replacement hashes.
- [ ] Make the detail reader expose a verified replacement together with the
  original path and parse error, without silently relabeling the replacement
  as the original or erasing the integrity warning.
- [ ] Route the 15 uncovered paths through an appropriate additive correction
  mechanism, or explicitly mark them unsupported with an honest reader state.
- [ ] Rebuild the complete static site and verify detail readback, parse
  classification, source links, and benchmark payload without changing
  numerical performance data absent a new measurement.

## Next discriminating step

- **Action:** Prototype replacement-aware detail readback for one of the nine
  already registered records, with changed-hash and missing-replacement
  controls. Keep the original parse warning visible.
- **Inputs:** Registry paths and SHA-256, original and replacement YAML, and
  the 24-path static integrity payload.
- **Stop condition:** If source/replacement hashes or schema disagree, show
  the original error and do not present the replacement as verified.
- **Recheck trigger:** A reader change, a new registered supersession, or a
  fresh full static build.

## Resolution and history

- 2026-10-21: Opened from the complete local dashboard build and source-bound
  supersession classification. No archived source, numerical result, or
  dashboard deployment changed. Unresolved.
