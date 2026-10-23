# Source-bound non-execution stage classification — 2026-10-22

## Result

`RUN-QSP-33b442-S0` is a hand derivation filed in the run namespace. Its
frozen [experiment specification](../../../experiments/EXP-QSP-33b442/specification.yaml)
states `compute: ZERO. No program is run in this stage.` The superseding
[manifest](../../../experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml)
records `execution: none_occurred` and names its
[derivation note](../../../experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/derivation-note.md).
No command, environment, stdout, stderr, or raw-result file ever existed for
this stage. The earlier validator correctly reported a category error under
its rule for execution runs; the historical [correction](../../../ledger/corrections/CORR-20260917-8b80cc.yaml)
and its original five-error disclosure remain unchanged.

This branch adds a repository-level **non-execution hand-derivation category**
to `tools/validate_ledger.py`. Admission requires the existing hash-pinned run
supersession plus exact hashes of the frozen specification and derivation note,
the declared stage/status/command/certificate and absence of all five capture
files. The validator emits a visible advisory that no measurement is credited.
Any failed admission keeps a forced declaration error and the ordinary
capture-file checks. The [source-binding receipt](evidence/source-binding.json)
lists all four hashes and confirms the five absences. No original file or
prune-only baseline entry changed.

The complete-tree validator still exits **1**. Its unsuppressed count fell
from **147 in 41 paths** on the parent audit branch to **142 in 40 paths**.
The [exact delta](counts.json) shows only the five QSP Stage 0 missing-artifact
messages removed and zero added messages. Advisories rose from 545 to 546
because the new classification is disclosed. The [before/after chart](error-delta.svg)
counts validator messages, not scientific results or performance data.

## Negative controls and limits

The run-supersession suite passes **87 tests**, including a hash drift of each
of the two manifests and the two new source bindings; a changed `compute`,
`execution`, stage, or terminal status; a captured `command.txt`; and an
unregistered terminal record that still owes all five files. A rejected
registered declaration produces a forced error plus the missing-artifact
errors. The category does not apply to Stage 5, whose report program actually
ran and whose capture was recovered by a separately documented re-execution.

This classification does **not** prove the hand derivation, the QSP bound, or
any attack claim. Stage 1's numerical cross-check and later independent
mathematical review remain separate evidence. The other 142 ledger errors,
24 historical reader parse warnings, and stale public Pages snapshot remain
open under their existing problem records. The
[ledger problem](../../../problems/full-ledger-validation-errors.md) records
the new gate count and the [dashboard problem](../../../problems/pages-workflow-disabled-live-snapshot-stale.md)
retains the hosted-publication condition.

## Reproduce

```sh
python3 docs/reports/2026-10-22-zero-compute-category/check_sources.py
python3 -m unittest tools.test_run_supersession
python3 tools/validate_ledger.py > docs/reports/2026-10-22-zero-compute-category/evidence/validate-ledger.log 2>&1
python3 docs/reports/2026-10-22-zero-compute-category/render.py
```

The validator's nonzero exit is the recorded outcome. `render.py` requires the
exact five deletions, zero additions, and 142 remaining messages.
