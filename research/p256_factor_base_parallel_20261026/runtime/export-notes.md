# Second-pass protocol and export integration

These are source-preparation notes, not experiment output. Read the canonical
`docs/experiment-protocol.md`, schema and checker. Root owns this directory;
workers own their assigned track directories. No pilot or experiment runs are
authorized until the committed source/protocol and actual S3 checkpoint gate
are released by root.

- `tools/experiment_protocol.py seeds` addresses instances as strings `0`,
  `1`, ... and requires the full arms x instances x replicates grid. Keep the
  human-readable case name as additional native raw metadata. Explicit-list
  seeds are repeated cyclically across the grid; `harness_drawn` requires the
  actual frozen deterministic rule in its note. Choose before any data.
- The current schema requires at least two genuine arms and one declared
  comparison even for an exact-computation panel. A producer traversal and
  an independently implemented reference traversal can each export the same
  entire fixed panel as one execution, with an absolute equality criterion.
  Retain their actual work/counters and shared setup; do not invent a second
  run or turn an exact correctness comparison into a performance claim.
- `from-rows` creates the row/flow structure but leaves producer, observed
  instrument, host and analysis metadata empty. Complete these from actual
  execution receipts. Never copy a planned binary/commit into a missing
  observation merely to satisfy the checker. Root will hash the actual
  interpreter/entry points and verify the selected source bytes against their
  pinned committed objects before execution. Distinguish runtime HEAD from
  the pinned implementation commit when protocol-only commits intervene.
- Protocol drafts remain drafts during engineering. Root pins instrument and
  analysis hashes only after source is committed, validates, writes a fresh
  `protocol.json`, freezes it and commits it before affected data. Later
  source/analysis changes need a prospective protocol amendment/version.
- The shared host earns no isolated-clock result. Record available diagnostic
  clocks with `wall_valid=false`; exact integer counts and checked witnesses
  carry the specified scope. Restored rows retain counts and lose clocks.
- Preserve partial/failed rows. A process timeout is `not_completed` and
  cannot be converted to a zero-result mathematical observation. Each attempt
  needs a fresh directory and command/stdout/stderr/source receipt.
- An export needs actual source, host, interpreter/entrypoint, raw artifact
  hashes and frozen analysis source/outputs. End with `check-export
  --protocol ... --verify-files` and retain the printed flow. A passing schema
  checker does not certify mathematical correctness or official review.

Literature: internal sources actually read are the canonical document,
`schemas/experiment-protocol.v1.json`, `schemas/experiment-export.v1.json`,
and `tools/experiment_protocol.py` (`seeds_table`, `lint_export`, `from_rows`
and `export_skeleton`). The integration notes reuse those requirements;
no new research method or outcome is inferred here.
