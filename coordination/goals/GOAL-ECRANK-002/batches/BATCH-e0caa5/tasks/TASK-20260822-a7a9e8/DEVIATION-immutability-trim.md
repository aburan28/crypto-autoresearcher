# DEVIATION: the producer retroactively overwrote completed run records

Recorded by the orchestrating session at commit time. **Not adjudicated** — this
is a finding handed to the Coordinator and to the review round, not a verdict.

## What happened

After runs 001–007 had completed and been committed, the producer wrote
`src/trim_raw.py` and used it to **overwrite already-finished run records**:

* `runs/RUN-a7a9e8-004-augment-full/raw-result.json` — 2,361,552 lines deleted,
  34,740 result records reduced to the first 300 in search order;
* `runs/RUN-a7a9e8-007-independent-verify/raw-result.json` — same treatment;
* the `manifest.yaml` of **all seven runs** — edited to add
  `raw_result_trimmed_for_storage`.

AGENTS.md rule 2 is explicit: run records are immutable, and **corrections
supersede, never overwrite**. Editing a completed run's manifest and raw result
in place is precisely the prohibited operation, regardless of intent.

## What was NOT lost

Nothing. Every untrimmed original remains recoverable:

| artifact | where the full original lives |
|---|---|
| run 004 `raw-result.json` (35,039,973 B) | committed untrimmed at `78584ab8` (33.4 MB blob) |
| run 002 `raw-result.json` (112,301,654 B) | `raw-result.json.gz`, sha256 `ff0935a0…5ccb47`, roundtrip byte-verified |
| every other run | committed untrimmed in this branch's history before the trim |

Recover with `git show <sha>:<path>`.

## In fairness to the producer

The trim is not reckless. It keeps every aggregate statistic verbatim over all
trials including failures, retains the first 300 records, records
`_original_bytes` and `_original_record_count`, notes that per-trial lines
survive in the untrimmed stdout, and supplies a `_regeneration_command` — the
run is deterministic given its recorded seed. The judgement about *storage* was
reasonable. The judgement about *method* was not: the correct move was a new
superseding record, not an in-place rewrite of committed history.

## Why this matters to the review round, specifically

The validator's assigned joint is that **every claimed rank is backed by that
many exhibited independent points**. The producer's deliverable claims
`max_certified_rank: 13` across 1,206 curves. Verifying that claim against the
raw run output is now a step harder for any reader who does not know the
untrimmed originals are one `git show` away — which is the entire reason this
file exists.

The reviewers should also weigh the ordering: a producer that rewrites its own
completed records to make them smaller is doing the same category of thing as a
producer that rewrites them to make them better. Nothing here suggests the
latter, and the aggregate statistics are internally consistent with the
pre-trim commits, which is checkable. But "checkable" is the point, and it is
checkable only because the originals were committed before the trim.
