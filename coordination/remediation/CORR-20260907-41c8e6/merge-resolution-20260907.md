# Merge resolution against main after PR #873 / #874

While merging `origin/main` into this branch, the run and schema supersession
registries each listed the same superseded paths twice: once from already-merged
PR #873 (`CORR-20260907-e6f0f7`, `*_v2` / `*_integrity_v2` replacements) and once
from this repair (`CORR-20260907-41c8e6`, `*.integrity-20260907.yaml`).

`tools/validate_ledger.py` refuses duplicate `superseded_path` entries. Resolution:

1. Keep the #873 registry bindings as the live canonical supersessions.
2. Drop the 16 overlapping run-registry rows and 2 overlapping schema-registry
   rows from this repair. The corresponding `*.integrity-20260907.yaml` /
   companion files remain in the tree as non-registered archival artifacts under
   this correction package; they are not rewritten.
3. Take main's `RUN-MLKEM-980909-a/environment.json` (hash
   `d66fa290…`), which `integrity-recovery.json` from #873 already pins.
4. Add the missing `registered: '2026-09-07'` field on main's
   `EV-ECRANK-76a70d-285d90` schema supersession entry (load-blocking defect
   already present on main).

This branch still contributes the `provenance_quarantine` validator path, its
regression tests, the documentation section in
`docs/evidence-and-reproducibility.md`, and the administrative
`DEC-20260907-44b7d9` / `CORR-20260907-41c8e6` / task records. Activating the
stricter `completed_invalid` disposition for `RUN-ECDLP-5cad48-S2` would require
a later Coordinator registry amendment that replaces the #873 binding; it is
not done in this conflict merge.

5. Publish `ledger/evidence/EV-ECRANK-469594.yaml` as a byte-identical live copy of
   this repair's schema replacement so `DEC-20260907-44b7d9` target_ids still
   resolve after the overlapping schema-registry row was dropped in favor of
   PR #873's `EV-ECRANK-9cadd9` binding. Both evidence IDs remain; neither
   original byte is rewritten.
