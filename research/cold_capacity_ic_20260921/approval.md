# DEC-20260921-6837e5 — conditional approval of RUN-KIC-8b5038

**Decision:** conditionally approve the frozen design in `protocol.json`. This
does not authorize preflight or scientific execution unless the parent-review
and all source/admission gates have been committed as satisfied.

The successor isolates one implementation factor. For the common-ARM,
allocation-only K=75 / eta=1/256 signed-expanded IC configuration, it doubles
only `CompactPairTable` capacity when `x_only=true`: 16,777,216 active slots to
33,554,432. Bloom bits remain computed from the original `expected` value; the
mathematical method, factor-base density, field arithmetic, target generation,
witness policy, threads, CLI/dataflow, and unchanged rho implementation remain
fixed. The additional table capacity is not free: wall, CPU, and RSS are all
required outcomes, and exact byte/RSS delta is not inferred from slot count.

The run fixes 24 fresh deterministic public known-answer targets and 72 serial
fresh processes. Every target receives baseline direct, capacity-candidate
direct, and unchanged rho once. The six lexicographic three-arm orders cycle
four times, so each arm occurs eight times in every process position. There is
no calibration, selection, old-target reuse, best-of timing, shared log/state,
hidden rho weakening, or scientific retry. The RUN-KIC-e3dbed records remain
unchanged and are not pooled into this experiment.

The primary candidate/rho whole-process-wall predicate requires all 24 valid
pairs, median ratio below 0.95, and a paired-bootstrap 95% upper endpoint below
1.00. Candidate/baseline wall, CPU, and RSS are secondary and cannot replace
this predicate. Even a pass is only a finite public-synthetic observation until
the independent review; it cannot establish an asymptotic, SOTA, security, or
cryptanalytic result.

Before the three untimed N=13 controls, the parent review
`TASK-20260921-6ae79e` must validate the parent source/correctness/cold-accounting
evidence. Exact source/binary/runner/analyzer/case closure and the one-factor
diff then require hashes. The controls require equal base, points/labels, active
pair domain, and bounded lookup semantics between IC capacities, full known
answer/group checks, and actual ARM PMULL backend reports. They do not demand
equal hash-sensitive witness order, first-hit transcript, relation transcript,
or rank-prefix trajectory.

The one-thread serial cold boundary, 240-second watchdog, per-PID `wait4`
telemetry, cooperative 8 GiB Darwin resource boundary, no-retry rule, and
anomaly stop rule bind exactly as written in the protocol. Failures are
preserved implementation/instrumentation outcomes, never mathematical evidence.

The executor binding is `executor-implementation` with explicitly requested
`gpt-5.6-sol` at `high` effort, no fallback and no degradation. The dispatcher
must record the actual resolved identity and verification result. Earlier terra
implementation failures remain immutable parent evidence and do not alter this
task.

Reserved progression after all gates are satisfied:

- `TASK-20260921-0a3002` — executor implementation, admission, and frozen run;
- `TASK-20260921-c8973d` — Coordinator hash-pinned snapshot;
- `TASK-20260921-571c77` — independent adversarial review;
- `TASK-20260921-154dd3` — archive and disposition under `DEC-20260921-a15c3b`.

The high-occupancy observation motivating this conditional design is `internal`.
The limited source search makes no novelty or literature-completeness claim.
