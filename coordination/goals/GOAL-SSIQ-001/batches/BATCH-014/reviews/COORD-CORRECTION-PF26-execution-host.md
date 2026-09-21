# COORD-CORRECTION-PF26 — the Coordinator's own load figures described the
# wrong machine, and this record says so

GOAL-SSIQ-001 BATCH-014. Correction record under AGENTS.md rule 4
(corrections create new records) and rule 8 (unexpected observations are
recorded, not discarded). Issued by the Coordinator against its **own**
contribution to this batch.

## What I got wrong

In dispatching the round-1 pre-freeze review (`TASK-20260807-43d16f`) I
handed the reviewer this, under the heading "MEASURED FACTS I HAVE
INDEPENDENTLY VERIFIED":

> THE EXECUTION ENVIRONMENT IS CURRENTLY HEAVILY OVERSUBSCRIBED.
> `sysctl -n hw.ncpu` = 14 cores; successive `uptime` readings this session
> gave 1-minute load averages of 19.45, then 24.15.

Those numbers are real, and they are **not about the execution
environment**. They are about the *orchestration* host — the arm64 Darwin
machine this Coordinator session runs on. Every run in this experiment's
lineage executed somewhere else.

Verified directly from the committed run artifacts
(`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-*/environment.json`),
all ten runs `-a` through `-j`:

| field | value, identical across all ten runs |
|---|---|
| `platform` | `Linux-6.18.5-fc-v18-x86_64-with-glibc2.39` |
| `cpus_available` | `4` (where recorded; `None` in `-e`, `-f`, `-g`) |
| load average | **never logged, in any run** |

So the 1.149932861328125 s natural-completion floor, and the whole archived
timing curve every prediction in this amendment rests on, were measured on a
**4-CPU x86_64 Linux** host. My oversubscription figures (19.45 / 24.15 /
33.78 against 14 arm64 Darwin cores) describe a machine that has never run
this experiment.

Found by the round-3 Red Team review
(`RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3.md`, PF-26), not by me.

## What it damaged

The error propagated into frozen draft text across two rounds, because I
supplied it with a confident label and neither round-1 nor round-2 review
opened `environment.json` to check it:

1. **The caveat is misnamed.** The draft's "**SAME-HARDWARE** CONTENTION
   CAVEAT" is not same-hardware at all. It is a cross-hardware comparison
   wearing the opposite label — and PF-14 introduced that section
   specifically to distinguish same-hardware contention from the
   cross-hardware case v11 already covered. The section inverted the very
   distinction it exists to draw.
2. **A required field is unimplementable on the platform that runs it.**
   PF-14(c), my own prescription, requires `hw.ncpu` in `environment.json`.
   `hw.ncpu` is a macOS/BSD `sysctl` key. It does not exist on Linux, which
   is the only platform this lineage has ever executed on. As frozen, that
   requirement could not be satisfied by a conforming run.
3. **The deferral prediction is unfounded as stated.** The draft's
   operational note — that at ~2.4× load `F_cal` would land near 2.8 s and
   trip `G-1 DEFER` — extrapolates from host load to execution-host
   behaviour with no measured link between them. The *gate* is sound and
   should stay; the *prediction attached to it* is not evidence and must not
   be read as one.

## What it did not damage

Stated precisely, so this correction is not read as wider than it is:

- **No archived measurement is affected.** RUN-a..RUN-j were executed and
  recorded before this session and are untouched by my error.
- **No number in the prediction curve is affected.** 115 / 36 / 20 / 79, the
  `{5:20,6:4,7:6,8:6}` and `{2:28,3:43,4:8}` histograms, the 1.3924050331115723 s
  minimum over `delta_E >= 5`, the 80-member population, and the calibration
  coordinates all derive from the archived artifact alone. They were
  recomputed independently by this Coordinator and again by the round-3
  reviewer, and they stand.
- **PF-14's underlying concern was correct and remains correct.** A
  wall-clock-gated search whose measured variable is natural completion
  within a ~50 ms margin is genuinely vulnerable to contention, and PF-8's
  well-formed empty histogram genuinely would make a contention-induced null
  indistinguishable from a finding. The calibration + defer gate that
  concern produced (CAL-1/CAL-2, G-0/G-0b/G-1/G-2/G-2b) is the right
  instrument and survives this correction intact. What was wrong was the
  *host attribution*, not the *mechanism*.
- **PF-17 is unaffected.** Its argument is about the archived timing curve
  and the `delta_E = 5` class, and touches no host figure.

## Required repairs, carried into the round-4 draft

- Rename the caveat to reflect what it actually is, and restore the
  same-hardware / cross-hardware distinction PF-14 was raised to draw.
- Replace `hw.ncpu` with a portable capture that works on the Linux
  execution host (e.g. `os.cpu_count()` plus `os.getloadavg()`), and require
  `platform` and `cpus_available` to be read from the run's own environment
  rather than assumed.
- Re-label every 14-core Darwin load figure in the draft as an
  **orchestration-host observation**, explicitly not an execution-host
  measurement, and withdraw the `F_cal ≈ 2.8 s` deferral prediction as
  unfounded while keeping the gate.
- Add the round-3 reviewer's proposed `G-0c` branch: refuse to proceed if
  the execution host's recorded `platform` / `cpus_available` differ
  materially from the archived runs' (`Linux ... x86_64`, 4 CPUs), since the
  entire prediction curve is only transferable across matched hosts.

## The process lesson, recorded because this lineage records them

This is a first-principles failure of the kind the goal record's standing
BATCH-011 obligation names: *check whether the instrument can discriminate
the hypothesis at all before spending effort on it*. I asserted an
environmental fact about the execution host without opening the artifact
that records the execution host — an artifact already committed, in the same
directory as the timing curve I did open and recompute twice. The check
that would have caught it cost one file read.

It also shows the review chain doing exactly what it is for, in the
direction that matters most: the Coordinator's own input, delivered with
authority and a "verified" label, was the thing that was wrong, and an
independent reviewer overturned it at round 3. That is worth more than the
three rounds cost. **A Coordinator-supplied "measured fact" is not evidence
until it is bound to a committed artifact**, and reviewers in this lineage
should treat one as a claim to check rather than a premise to build on.

```yaml
provenance:
  role: coordinator
  batch: BATCH-014
  goal: GOAL-SSIQ-001
  corrects: >-
    This Coordinator's own dispatch input to TASK-20260807-43d16f, and the
    draft text it propagated into across rounds 1-3.
  found_by: RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3.md (PF-26)
  verified_against:
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-{a,b,c,d,e,f,g,h,i,j}/environment.json
  changes_no_measurement: true
  changes_no_hypothesis_status: true
  recorded_at: '2026-08-07'
```
