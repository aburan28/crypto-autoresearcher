# Independent native CPU software review

TASK-20261026-64f987 · Reviewer · owned joint
`cpu-units-coverage-and-failure-retention`

## Scoped verdict

**Holds for the published source-only software claim at owner commit
`86ddd19f67e08160c22a0d8ba9a32a92321d18ad`.** The checked conversion has the
right microsecond units, phase receipts keep worker-self and waited-child usage
separate, per-child receipts are diagnostic rather than additive, failure paths
retain available wait/CPU evidence, unavailable counters stay unavailable, and
the receipts do not label full phase process-tree CPU as measured.

This is the verdict on the one joint assigned by the frozen prospective review
plan. It is not a vote on a scientific goal and does not establish mathematical
correctness, theorem applicability, admission correctness, experiment readiness,
complete process-tree accounting, performance gain, or improvement over a current
index-calculus baseline. The Coordinator owns any composed software decision.

No breaking artifact was found. Five `git diff --check` advisories occur only in
the retained raw fake-helper `.vertices` serializer outputs (`+0 `); the owner
manifest already discloses those artifacts, and this review did not normalize or
discard them.

## Source custody and sealed expectations

The reviewed owner object is immutable locally and was the clean owner HEAD during
review. Its parent is the declared base
`27fca7749299469bd93bad3a1eed8e7e6a3b6a75`. I independently compared the owner
manifest with `git diff --name-only` and `git show` at the reviewed commit:

- 107 manifest entries, 107 unique paths, and 107 owner-diff paths;
- zero path-set differences, missing blobs, SHA-256 mismatches, or byte-count
  mismatches;
- all four producer outputs currently read are byte-identical to programme
  snapshot `b50185b81b7c145f04aae40eb0ef9770b427dc3d`;
- the published expectation, its snapshot copy, the seal's published hash, and
  the JSON embedded in the owner expectation file all hash to
  `1fb61b6c45e4ef9bd0383519d255c0ea7084ca260038a0e0e5963622fcf5d4fe`;
- the complete owner expectation file and the seal both name
  `18f166bff8b94e53d52d3ec8209e135512fa90c65193a15315f4901ae4728df2`.

The published task resolution selects native `gpt-5.6-sol` at `xhigh` for this
fresh `review-adversarial` session. That is the actual parent-managed native
selection recorded here. I made no model-catalogue/API probe, claimed no current
serving attestation, and used no fallback, degradation, or delegated agent.

## Owned-joint attacks

### Exact units and formatter traps

At `src/usage.hpp:19`, checked conversion rejects negative seconds, rejects
microseconds outside `0..999999`, guards signed 64-bit multiplication/addition,
and returns `sec*1000000+usec`. At lines 39–45 the compatibility seconds field
uses exactly six fractional digits. Independent fixture observations were:

| input `(sec,usec)` | integer microseconds | decimal seconds |
| --- | ---: | ---: |
| `(0,1)` | 1 | `0.000001` |
| `(0,10)` | 10 | `0.000010` |
| `(0,999999)` | 999999 | `0.999999` |
| `(1,0)` | 1000000 | `1.000000` |
| `(1,1)` | 1000001 | `1.000001` |

The maximum signed 64-bit microsecond value passed exactly; the next value and
an excessive seconds value were rejected. The known-false `0.1 seconds` reading
of one microsecond is therefore rejected by both the integer and decimal fields.

### Worker-self, waited-child coverage, and double counting

`phase_cpu_snapshot()` reads `RUSAGE_SELF` and `RUSAGE_CHILDREN` into different
members. `phase_cpu_fields()` computes and serializes their user/system deltas
separately. Linux man-pages 6.19 defines `RUSAGE_SELF` as the process summed over
all threads and `RUSAGE_CHILDREN` as terminated and waited children, with further
descendants included only when each intervening descendant waited. The receipt
labels match those definitions and also state that child usage is credited on
reap rather than time-sliced to the phase.

Static inspection found no addition of `WaitUsage` values to a phase delta.
The known-false additive control created a phase waited-child delta of 40 user
and 5 system microseconds beside a distinct child receipt with the same 40/5
values. The phase stayed 40/5, not 80/10, while worker-self stayed 8/4. Both
records identify the child receipt as diagnostic and full tree CPU as unknown.

### Exit, signal, exec, parser, and failure retention

`backend.hpp` and `cdd_ipc.hpp` wait on the exact forked PID with `wait4`, retry
`EINTR`, then write wait status and a versioned CPU receipt before testing exit
status or parsing/consuming output. Independent replay exercised both paths for
exit 0, exit 17, SIGTERM, missing exec (exit 127), and malformed fake output.
All twelve emitted child receipts carried nonnegative integer user/system
microseconds and the correct exit/signal classification before the later failure.

The phase success and standard-exception paths retained separate self/child
fields. The exception path also retained `failure-checkpoint` with
`fake-throw` and `Singular process failure`. An additional pure software probe,
compiled only against the published source, checked cases not required as
separate sealed fixtures:

- `wait_child_usage(99999999)` returned `ECHILD` (errno 10), `reaped=false`,
  unavailable status/user/system values with explicit reasons, and unknown full
  tree CPU;
- a decreasing synthetic counter returned `counter_regression`, not zero;
- a nonstandard integer exception through `Archive::phase` was rethrown after
  retaining the failure phase and `nonstandard_exception` checkpoint.

The guarded supervisor was inspected statically only. Its successful and timeout
reaps construct the worker `WaitUsage` and write `supervisor-cpu-receipt` before
later cgroup artifact reads; its cleanup path reaps and writes the same scoped
receipt when possible. The cgroup supervisor, watchdog, real worker, and process
tree were not launched.

### Unavailable counters and coverage honesty

`getrusage` failure discards the supplied/stale struct and serializes both fields
as unavailable with the saved errno. Invalid timevals and overflow do the same.
Counter regression is unavailable. The sealed failure fixture produced
`stop_getrusage_errno_5` for all four phase fields and retained
`phase_process_tree_cpu=unknown`.

Every inspected phase, child, and supervisor formatter uses
`native-smallroot-cpu-v2`. Phase records state
`phase_process_tree_cpu=unknown`; child and supervisor records state
`full_process_tree_cpu=unknown`. This is required because live or unwaited
descendants are not covered and because `RUSAGE_CHILDREN` assigns usage at reap.

## Independent replay

From `/workspace/crypto-native-smallroot`, with owner HEAD exactly at the review
target:

```sh
make -C experiments/joint-smallroot-native \
  BUILD=/tmp/TASK-20261026-64f987-native-build.qhylOF \
  -j2 cpu-accounting
/tmp/TASK-20261026-64f987-native-build.qhylOF/cpu-accounting \
  /tmp/TASK-20261026-64f987-native-build.qhylOF/fake-child \
  /tmp/TASK-20261026-64f987-native-build.qhylOF/fixtures-review
```

The warnings-as-errors build exited 0. The fixture command exited 0 and printed:

```text
17 sealed native CPU software fixtures passed; no CAS, mathematical helper, panel or supervisor launch
```

The fixture log contains exactly 17 `START`, 17 `PASS`, one `COMPLETE17`, and
the PASS-ID set equals the frozen expected-ID set. The independent binaries are
byte-identical to the producer manifest binaries: CPU fixture
`e9419aaae748cc05d2eaa0dc0d69cb15432c389d0ec9e90f2bef56ab35abae8f`,
fake child
`d4a84a7c0057fa33a31cac95b837bd2f89e0ddc076050696e63108aecc70bb3d`.
The 80-file replay tree's sorted relative-path/content-hash manifest hashes to
`612a6d58187bd972bc3165e94e0e06669624e3ea4a2a911aaba1615db327b641`.

The producer's earlier strict build attempt that exited 2 on two mixed-type
fixture declarations remains preserved among the 107 verified owner blobs,
together with its stdout/stderr/exit record. The producer's corrected attempt
and this independent build both exit 0; no expectation was changed between them.

Exact commands, actual dynamic values, raw selected outputs, and hashes are in
`checks.json`. No Python research, harness, or test execution occurred. No real
Singular/cdd mathematics, ideal, bound, D-sign control, calibration, root or
parameter search, pipeline, scientific panel, or cgroup supervisor was launched.

## Remaining limits

Full phase process-tree CPU remains unknown. Actual cgroup delegation,
watchdog/tree-kill behavior, live or unwaited descendants, and scientific worker
integration are outside this review. This review makes no new performance or IC
claim and cannot establish mathematical/applicability/experiment readiness.

The retained current whole-library Cargo attempt was not rerun. Its exact log
hash is `c5c5cf1a7ee6b111b654532f5e94d28a09453219696205221acd2cdaf935be14`
and records exit 101 for the unchanged upstream unclosed delimiter at
`src/cryptanalysis/binary_semaev_chain_sat.rs:1648`. The older 4862-pass result
belongs to b02 and is not evidence about this source.

The exact read list is recorded in `review-attestation.yaml`. No current-round
sibling report exists or was read, no blindness lift was used, and this reviewer
does not generate concurrence.
