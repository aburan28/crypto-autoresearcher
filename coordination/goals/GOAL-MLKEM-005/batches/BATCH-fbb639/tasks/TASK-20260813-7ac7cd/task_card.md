# TASK-20260813-7ac7cd — SNAPSHOT ARCHIVE of the lead producer

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           not_started
    depends_on      TASK-20260813-7b3039
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Make the lead's seven artifacts durable and reviewable, **alone**, before
either review is dispatched. Cross-checks `report_c3lane.md`'s own declared
path list against `dispatch_queue.json`'s `declared_path_set` before staging.
**Additionally confirms no reduction was performed**: `fpylll` does not appear
as an import or install anywhere in the lead's committed artifacts — a
constraint violation here returns the run to the producer rather than
archiving it.

## Completion gate, in one sentence

The commit changes **exactly eight paths** — this task's own receipt plus the
lead's seven artifacts — 0 extra, 0 missing, with validity (run count,
schema-complete manifest, RC-1/RC-2 carried-not-recomputed) checked before
interpretation, exactly as this goal's every prior lead snapshot has required.

## Artifacts — ONE PATH

    archives/TASK-20260813-7ac7cd/snapshot-receipt.json
