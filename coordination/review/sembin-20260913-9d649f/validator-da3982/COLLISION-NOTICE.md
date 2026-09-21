# READ FIRST — two sessions executed TASK-20260913-da3982 concurrently

**Raised by**: the session whose working files are under `scratch/` (called *session B*
below), at 2026-09-13 15:33 UTC.
**Status**: disclosed, not resolved. Resolution is the Coordinator's; a validator may not
adjudicate its own task's ownership.

## What happened

Two independent sessions were running as the validator for
`TASK-20260913-da3982` at the same time, in the same worktree, both writing to the
same declared `write_scope`
(`coordination/review/sembin-20260913-9d649f/validator-da3982/`). They are
distinguishable by their working directories:

| session | working dir | first write | its scripts |
|---|---|---|---|
| **A** | `work/` | 15:23 | `j1_memory_from_text.py`, `j4_mechanism.py`, `objects.py` |
| **B** | `scratch/` | 15:11 | `j1_memory_model.py`, `j4_mechanism.py`, `proves_too_much.py` |

Neither session claimed the task with `tools/goal_lanes.py claim`, so neither could see
the other. Session B discovered the collision only when validating its own YAML and
finding a `proves-too-much.json` on disk that its script had not written.

**Session B's `proves-too-much.json` was overwritten by session A's** at 15:32:03. No other
loss has been detected. Session B did **not** overwrite anything of session A's on
discovering this, and has not modified `work/` or any file session A wrote.

## Current contents, and whose each file is

| path | written by | note |
|---|---|---|
| `proves-too-much.json` | **A** | overwrote B's at 15:32:03 |
| `report.md` | **A** | overwrote B's at 15:36 |
| `attestation.yaml` | **A** | overwrote B's at 15:36 |
| `proves-too-much.session-b.json` | B | B's own, at a non-colliding name |
| `report.session-b.md` | B | restored from snapshot `1c207023f` after A overwrote `report.md`, plus a concurrency notice |
| `attestation.session-b.yaml` | B | B's own |
| `work/` | A | untouched by B |
| `scratch/` | B | untouched by A |

**End state: all three declared deliverables are session A's, and they are internally
consistent with each other** — A's report, attestation and objects file all cite `work/`
scripts, and A's attestation declares what A read. So the mixture that existed between
15:32 and 15:36 has resolved itself by A completing its set, and a reader consuming the
three declared paths as a unit now gets one coherent review rather than a blend. That is the
best available outcome and it needed no intervention.

Session B's set is at the three `*.session-b.*` paths and, in its original form, inside
snapshot `1c207023f`. Session B did not overwrite any file of A's at any point, and wrote
no attestation on A's behalf: an attestation is a personal statement about what one agent
read. (The snapshot commit records the concurrent `TASK-20260913-ec11c4` pair declining the
same substitution for the same reason.)

One correction session B makes against itself, since a validator that files a spurious
objection has failed at its own job: while diagnosing this, session B read
`attestation.yaml` mid-write and got a YAML parse error at line 108. That was a torn read of
a file A was still writing, **not** a defect in A's file, which parses cleanly. It is
recorded here rather than dropped because it was nearly reported as a finding.

## The two sessions agree on every verdict

Session A's report records J1 **holds**, J4 **holds**, and all four proves-too-much objects
returning the known-false-refuting answer. Session B's records exactly the same three. The
two were produced from different scripts, different memory accountings, and different
object-4 patch points, with no contact between the sessions.



This is the reassuring part, and it is why the collision is a bookkeeping problem rather
than an evidentiary one. On the four `proves_too_much` objects the two independent
executions **concur 4/4**: every object returned the answer that refutes its known-false
statement, and none failed.

- Object 1 (n = 163): both report Semaev losing.
- Object 2 (eq. (4)): both report it catastrophically worse. A additionally ran it under a
  reading more generous to eq. (4) than the producer's.
- Object 3 (free-yield null): both report the crossover moving DOWN in every cell, and both
  therefore rule out an inverted sign convention.
- Object 4 (solving cost exponential in (m − t)): both report t\* dropping below m\* to
  t\* = 2 once the reward rate exceeds the yield-loss rate, and both locate the transition
  at the predicted threshold. The two used different patch points — A rebound
  `log2_solve_cost`, B rebound `stage_costs` — and different rate parameterisations, and
  agree anyway.

Two sessions reaching the same verdict on four controls by different code paths is worth
more than one session's word for it. It is **not** the independent review the plan requires
and must not be counted as a second reviewer: same task, same role, same handoff, same
frozen inputs, and no declared blindness between them. It is one review executed twice.

## The snapshot commit already captured the mixture — and lost nothing

Snapshot `1c207023f`, "Snapshot REVIEW-SEMBIN-20260913-9d649f reviewer reports before
composition", was made at 15:33:46, between the collision and this notice. It contains:

- session B's `report.md` and `attestation.yaml`;
- session A's `proves-too-much.json`;
- **both** sessions' working directories in full, `scratch/` (B) and `work/` (A).

So the mixture described above is now inside a commit — but **no evidence was destroyed**.
Session B's four-object output is committed at `scratch/ptm_out.json`, and it is the
corrected version: object 4 run under both signs, 4/4 objects meeting their signature. What
session B lost was the declared-path *slot*, not the result, and the result is
reconstructible by running `scratch/proves_too_much.py` at that commit.

That commit's own message independently records the same failure mode elsewhere in this
round: two instances of `TASK-20260913-ec11c4` also ran concurrently and reached *different
verdict words on the same facts* (`breaks` versus `incomplete`). This is therefore a
round-wide dispatch defect, not a one-off, and it is the more serious for having produced
divergent verdicts there while producing agreement here.

`COLLISION-NOTICE.md` and the disclosure blocks added to `report.md` and `attestation.yaml`
were written **after** that snapshot and are working-tree changes at the time of writing.
They add disclosure and change no finding, no number and no verdict; a follow-up commit can
carry them without rewriting `1c207023f`.

## What the Coordinator has to decide

1. Which session's `proves-too-much.json` is the record for this task, or whether both are
   archived side by side. Session A's is at the declared path; session B's is at
   `proves-too-much.session-b.json`.
2. Whether `report.md` / `attestation.yaml` at the declared paths (session B's) stand, or
   whether session A produced its own that should supersede or accompany them.
3. Whether session B's `*.session-b.*` files should be renamed onto the declared paths or
   retired, once (1) and (2) are settled.

## What session B did not do, and why

- **Did not overwrite session A's `proves-too-much.json`.** An existing artifact is not
  session B's to replace, and the immutability rule in AGENTS.md points the same way:
  corrections supersede, they do not overwrite.
- **Did not write a bus message.** `coordination/bus/` is outside this task's declared
  `write_scope`, which the handoff states as the *only* permitted write location. Breaking
  scope to report a scope collision would be self-defeating, so the collision is recorded
  here, inside scope, and in session B's final message to the Coordinator.
- **Did not claim or release a lane.** `tools/goal_lanes.py` writes under
  `coordination/`, also outside scope, and a claim taken after the fact would misrepresent
  when it was taken.
- **Did not adjudicate.** Deciding which of two co-equal sessions owns a deliverable is a
  Coordinator act.

## The process defect worth fixing regardless of how this is resolved

Two subagents were dispatched for one `TASK-*` id with one `write_scope` and no lane claim.
`docs/concurrent-goal-lanes.md` exists for exactly this and was not used: a
`tools/goal_lanes.py claim TASK-20260913-da3982 --as validator --publish` before either
launch would have made the second session visible to the first as `running`. The dispatch
plan's `max_concurrent` bounds how many tasks run at once; it does not stop the same task
from being dispatched twice.

Nothing here bears on J1, J4, CLAIM A, CLAIM B, or the security of any curve. It is an
evidence-integrity and coordination finding, and under AGENTS.md an evidence-integrity
failure blocks downstream review until the Coordinator resolves it — it is not a
mathematical result in either direction.
