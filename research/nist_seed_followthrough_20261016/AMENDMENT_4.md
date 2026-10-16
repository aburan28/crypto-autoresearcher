# Completion-order receipt collection

Recorded before rerun `modalfull2`. Attempt `modalfull1` used ordered result
delivery with P-521's long first shard; other returned shards could be held
in the client and lost on interruption. The run was stopped early after this
recovery flaw was observed, and its plan, empty local event stream and client
observation are retained. No candidate conclusion is drawn from it.

The 221 planned shards, inputs, arithmetic, acceptance criteria, per-count
and per-shard watchdogs, twelve-container limit, and 12-hour client guard are
unchanged. The runner now receives outputs in completion order, verifies each
returned item's identity against the frozen plan, and writes each raw shard
and event before waiting for another. Duplicate, missing, failed and
unidentified responses keep the run partial. The summary binds events by item
identity, not event order. A new attempt suffix prevents overwriting any
earlier artifact.
