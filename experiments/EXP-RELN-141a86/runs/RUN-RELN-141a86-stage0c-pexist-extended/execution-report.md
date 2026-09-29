# RUN-RELN-141a86-stage0c-pexist-extended: execution report

Handoff: TASK-20260907-8e0165. Decision: DEC-20260907-bc69ee. This run
extends the SOLE remaining Stage-0c recovery control -- INV-7 p_exist
(canonical complexity 11, pack `enum_xclass_signed_m2`) -- through level 9
(and, if reached, level 10) of the same targeted-minimality method already
validated in RUN-RELN-141a86-stage0c-minimality.

**This task does NOT wait for the job to finish.** It starts a detached,
durable background process, verifies it is alive and genuinely progressing
for a few minutes, and reports. The job is expected to run for many hours
after this turn ends.

## 1. Hash re-verification (Stage 0a)

Recomputed `sha256(candidate-list.yaml || grammar.yaml || environment.lock.json)`
from `RUN-RELN-141a86-stage0a/` directly:

```
f1aec620f8cb19318e6d6459174bd79b80daf6dd46fdacf6afdf2468c7cac7f2
```

This matches the value recorded in `RUN-RELN-141a86-stage0a/candidate-list-hash.txt`
exactly, and matches the three individually-hashed input files recorded
there. **Result: MATCH.** (One transcription artifact was noticed and
resolved: the task instruction text carried a stray trailing character
making the quoted hash 65 hex characters; the archived file's hash and my
independent recomputation both agree on the 64-character value above, so
this is a prompt-transcription artifact, not a real discrepancy -- disclosed
for completeness.)

## 2. Resume vs. restart decision

I read `checkpoint-INV-7_p_exist.json` from `RUN-RELN-141a86-stage0c-minimality`
in full, plus `grammar_engine_checkpoint.py` (the enumerator that wrote it).

**Finding:** the checkpoint file's `levels_completed` array stores only
per-level *summary statistics* -- `new_registered`, `cumulative_registered`,
timings, `rss_bytes`, a timestamp -- never the actual in-memory
`by_complexity: Dict[int, List[Expr]]` dict of canonical expression trees,
nor the `seen_string_hashes` / `seen_fp_hashes` dedup sets those counts were
computed from. Those three structures are exactly what building level 9
from a level-8 state requires (level 9's binary-operator step iterates over
`by_complexity[c_left]` x `by_complexity[c_right]` for all `c_left + c_right
= 8`, and every candidate is deduplicated against the accumulated hash
sets). None of that is serialized anywhere in this run's or the prior run's
artifacts.

**Decision: restart from level 1, not a true resume.** Reconstructing the
missing state from the summary counts alone is not possible (the counts are
lossy -- they record *how many* new forms appeared, never *which*
fingerprints). A genuine resume would require extending the checkpoint
writer to serialize millions of canonical expression trees (3,314,145 forms
by level 8) plus two large hash sets on every level-boundary write -- a real
engineering cost, and one that would only be repaid by skipping levels 1-8,
which the prior run's own checkpoint shows cost just **~1800 seconds**
total, against an estimated **12-14+ hours** for level 9 alone. That
ratio (a few minutes of accepted rework against many hours of new work)
did not justify the engineering effort, so I restarted instead.

To get some value out of the resume attempt rather than none, I added a
`--resume-from-checkpoint <path>` flag to
`target_enumerate_worker_checkpoint.py` (additive; `grammar_engine.py`,
`grammar_engine_lean.py`, and `grammar_engine_checkpoint.py` are untouched).
It loads the prior checkpoint and, if this run reaches a clean exit, embeds
a level-by-level cross-check of `cumulative_registered` counts in
`worker-result-INV-7_p_exist.json`'s `resume_cross_check` field --
verifying the restart reproduces the same enumeration rather than silently
diverging. I unit-tested this flag on a 3-level toy run before the real
launch (confirmed levels 1-3 cross-checked as `matched_exactly`).

During the live 2-5 minute post-launch verification (below), I directly
observed the new run's checkpoint file reach levels 1-6 with
`cumulative_registered` = 6, 20, 179, 949, 8087, 54078 -- **identical** to
the prior run's checkpoint at the same levels. This is a strong live
determinism confirmation, obtained before the formal cross-check field is
even written (that field only gets written on a clean exit, which for this
job is many hours away).

## 3. Launch command and PID

```
cd /home/user/crypto-autoresearcher/experiments/EXP-RELN-141a86/source && \
RUNDIR=/home/user/crypto-autoresearcher/experiments/EXP-RELN-141a86/runs/RUN-RELN-141a86-stage0c-pexist-extended && \
setsid nohup python3 run_stage0c_pexist_extended_monitor.py \
  > "$RUNDIR/stdout.log" 2> "$RUNDIR/stderr.log" < /dev/null &
disown
```

- **Monitor PID: 10969** -- confirmed its own session leader
  (`SID=10969, PGID=10969`, i.e. detached from the launching shell) via
  `ps -o pid,ppid,pgid,sid,stat,cmd -p 10969,10971`.
- **Worker PID at launch: 10971** (child of 10969, running
  `target_enumerate_worker_checkpoint.py --pack enum_xclass_signed_m2
  --max-complexity 10 ...`).
- `--max-complexity 10` = canonical_complexity(11) - 1, so **one invocation
  covers both level 9 and level 10** (they build sequentially; the run does
  not stop after level 9 unless a cap intervenes first).
- Launched at `2026-09-07T18:57:26Z`.

Full command detail (including the exact worker sub-invocation with all
flags) is in `command.txt`.

## 4. Post-launch verification (2-5 minute check)

Checked repeatedly over the following ~4 minutes (real wall clock,
confirmed via `date +%s` deltas around each `sleep`):

| t (elapsed) | process state | checkpoint | memory-timeseries |
|---|---|---|---|
| ~50s  | both PIDs alive (R/Ss) | levels 1-6 in `checkpoint-INV-7_p_exist.json`, matches prior run's counts exactly | 13 samples, RSS 0.063 GB |
| ~81s  | both PIDs alive | level 6 still latest (level 7 building) | growing, 0.13 GB |
| 3:00  | both PIDs alive, RSS 198 MB | level 6 latest | -- |
| 3:51  | both PIDs alive, RSS 198-203 MB | level 6 latest (level 7 in progress) | **43 samples**, latest at t=210s, RSS 0.2033 GB, `still_running: true` |

- **(a) Process alive:** `ps -p 10969,10971` confirmed both PIDs alive at
  every check, `ELAPSED` climbing monotonically (00:31 -> 03:51), no zombie
  or defunct state.
- **(b) Memory-timeseries fresh:** `memory-timeseries-INV-7_p_exist.json`
  grew from 7 to 43 samples over the check window, each new sample carrying
  an advancing `t_elapsed_s` and `timestamp_utc`, and `still_running: true`
  at the last write.
- **(c) Checkpoint progress:** `checkpoint-INV-7_p_exist.json` shows levels
  1-6 exhaustively completed (`cumulative_registered` 6, 20, 179, 949, 8087,
  54078 -- byte-for-byte identical to the prior interrupted run's checkpoint
  at the same levels), `stopped_reason: "in_progress"`, and level 7 visibly
  under construction (RSS climbing from ~87 MB to ~203 MB across the check
  window, consistent with the prior run's own ~376-second duration for this
  level; level 7 had not yet completed by the end of my ~4-minute check
  window, which is expected and not a problem).

I did not wait for level 7 (or 8, or 9) to actually complete -- per the
handoff, that would require hours, not minutes.

## 5. Run directory and current artifact set (incomplete, job still running)

`experiments/EXP-RELN-141a86/runs/RUN-RELN-141a86-stage0c-pexist-extended/`:

- `manifest.yaml` -- status `running`; `result.certificate.kind: none`
- `command.txt` -- exact launch command and PID
- `environment.json` -- host capacity disclosure, resume-decision disclosure, source hashes
- `execution-report.md` -- this file
- `stdout.log`, `stderr.log` -- monitor's own logs (stderr carries the
  `worker_started` event JSON and, on eventual completion, a `summary` JSON
  line)
- `checkpoint-INV-7_p_exist.json` -- **live, growing** (per-level
  checkpoint, updated after every completed complexity level)
- `memory-timeseries-INV-7_p_exist.json` -- **live, growing** (RSS samples
  every 5s, written to disk every 30s while running)
- `worker-result-INV-7_p_exist.json` -- **does not exist yet**; only
  written by `target_enumerate_worker_checkpoint.py` on a clean exit
- `pexist-extended-search-raw-result.json` -- **does not exist yet**; only
  written by the monitor after the worker subprocess exits (clean, capped,
  or killed)

## 6. How a future task should check on, wait for, or resume this job

1. **Check if alive:** `ps -p 10969` (monitor) and, if that PID is gone,
   look for a `target_enumerate_worker_checkpoint.py --target-id
   INV-7_p_exist` process directly (`pgrep -f target_enumerate_worker_checkpoint`)
   in case the monitor exited but somehow left an orphan (should not happen
   under normal operation, since the monitor waits on the worker via
   `subprocess.Popen`/`.poll()`, but disclosed as a possibility).
2. **Check live progress without waiting:** read
   `checkpoint-INV-7_p_exist.json`'s `levels_completed` (highest
   `complexity` reached, its `cumulative_registered` and `timestamp_utc`)
   and `memory-timeseries-INV-7_p_exist.json`'s last sample and
   `still_running` flag. A `stopped_reason` other than `"in_progress"` in
   the checkpoint (i.e. `"completed"`, `"target_found_early"`,
   `"memory_cap"`, or `"wall_clock_cap"`) means the **worker's own internal
   loop** exited that way (distinct from the external monitor's own harder
   kill, which the worker cannot record about itself).
3. **If the process is dead AND `pexist-extended-search-raw-result.json`
   exists:** the job reached a terminal state cleanly (from the monitor's
   point of view). Read that file's `monitor_killed` /`monitor_kill_reason`
   /`returncode` /`worker_result` fields to determine PASS (no match
   through level 10, or a match found) vs. `resource_exhaustion` (killed by
   either cap) vs. some other failure. Then update `manifest.yaml`'s
   `status`, `timing.finished_at`, and `result` fields accordingly (this is
   the one in-place edit this manifest explicitly anticipates and
   authorizes, per its own `status_note`), and hand the result back to the
   Coordinator per the handoff's `review_reservation` -- **do not** dispatch
   Stage 1 regardless of outcome; that remains a Coordinator act.
4. **If the process is dead and NO `pexist-extended-search-raw-result.json`
   exists:** the job was killed by something external to its own two
   layers of caps (e.g. a container restart, an OOM-killer strike that
   pre-empted the monitor's own 12.5 GB cap, or the host being torn down).
   In that case: read `checkpoint-INV-7_p_exist.json`'s last completed
   level for how far it got, and re-launch a NEW run (new RUN-ID; do not
   overwrite this one) that, per the same resume-vs-restart reasoning
   above, most likely restarts from level 1 again UNLESS a future task
   judges it worthwhile to implement genuine state serialization by then
   (e.g. if repeated interruptions make re-deriving levels 1-8 a recurring,
   non-negligible cost). Use `--resume-from-checkpoint` pointed at
   whichever checkpoint file is most recent for the cross-check.
5. **If still running and you want to wait:** this is a genuinely long job
   (hours). Per the handoff and DEC-20260907-bc69ee, the intended check-in
   is roughly 15 hours after launch (`2026-09-08T~09:57Z`), not a live poll
   loop. A later task can simply read the checkpoint/memory-timeseries
   files at that time without needing to attach to or wait on the process.

## Disclosed deviations and risks

- **Host capacity below the specification's sizing assumption.** This host
  has ~15 GiB RAM / 4 cores, not the >=32 GB / >=8 cores the
  `budget.sizing_note` assumes. I lowered the external monitor's hard
  memory-kill threshold from the handoff's advisory 16 GB to **12.5 GB**
  (worker internal soft cap 10.0 GB) to leave headroom below actual
  physical RAM and ensure a clean, checkpoint-preserving kill rather than
  risking the OS OOM-killer acting first and possibly killing more than
  just this process. **This means the job may hit the memory cap before
  finishing level 9**, based on the prior run's own measured level-7-to-8
  growth factor (~7.5x in cumulative forms and in RSS): level 8 peaked at
  1.86 GB, so level 9 could plausibly approach or exceed the 12.5 GB cap
  before completing. If that happens, this is `resource_exhaustion`
  (an infrastructure limit of this particular host), never a negative or
  positive result on the control itself -- consistent with the frozen
  contract's own `invalidation_rules` ("Timeout, out-of-memory, solver or
  tool crash ... is failed_infrastructure for that stage or arm, never a
  negative or positive result").
- **Restart, not resume**, disclosed in full in section 2 above and in
  `environment.json`'s `resume_vs_restart_disclosure`.
- **Per-level-only checkpoint granularity is unchanged** from the
  validated prior design: if this job is killed mid-level-9 (which, given
  the ~12-14 hour estimate for that single level, is a real possibility
  under a 20-hour external cap or an external interruption), NO partial
  level-9 progress is preserved -- the checkpoint will still show level 8
  as the last complete level. This is a known limitation carried forward
  unchanged, not something this dispatch introduced.

## Not done in this dispatch (per explicit constraint)

- Did not touch any of the four prior immutable run directories under
  `experiments/EXP-RELN-141a86/runs/`.
- Did not edit `ledger/`, did not commit anything.
- Did not touch `experiments/EXP-RELN-f202be/` or `experiments/EXP-RELN-82f487/`.
- Did not proceed to Stage 1, and will not, regardless of how this job
  eventually terminates.
