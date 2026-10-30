# Native CPU receipt correction

TASK-20261026-dc4016 · Executor implementation · software accounting only

The bounded correction is implemented and its **17 sealed native software fixtures
pass**. Main source and dedicated tests compile with C++17/O2 and
`-Wall -Wextra -Wpedantic -Werror` in a fresh explicit build directory.
No real Singular computation, cdd mathematical construction, ideal, bound,
mathematical control, calibration, root/parameter search, panel or cgroup supervisor
was invoked. No performance, scientific readiness or IC improvement is claimed.

The exact published expectations were sealed before checks. Published JSON SHA256:
`1fb61b6c45e4ef9bd0383519d255c0ea7084ca260038a0e0e5963622fcf5d4fe`.
Owner expectation SHA256:
`18f166bff8b94e53d52d3ec8209e135512fa90c65193a15315f4901ae4728df2`.
See [expected-fixture-seal.json](expected-fixture-seal.json).

## Changes and evidence boundary

Shared `src/usage.hpp` converts seconds/microseconds to checked signed64-bit
integer microseconds and explicitly rejects negative, invalid-range or overflowed
values. Receipts carry `native-smallroot-cpu-v2`. Legacy decimal seconds use six
fractional digits:1us is0.000001s, not0.1s. Old receipts are preserved unchanged.

Backend and cdd IPC now use wait4, retry EINTR and retain status/usage before
checking exit/signal status or parsing/returning output. Exit0, exit17, SIGTERM,
missing-exec127 and malformed-output records survive failure. The native fake
child never opens/interprets the generated inputs; it emits fixed software codec
strings selected by its executable basename. The cdd malformed case is a pure
consumer-codec rejection after raw IPC return, not a native hull construction.

Phase records separately label RUSAGE_SELF worker user/system deltas and
RUSAGE_CHILDREN waited-child deltas on success and exceptions. SELF includes all
worker threads; CHILDREN includes terminated waited children and only propagated
descendant usage. CPU is credited on reap, not time-sliced to the phase. Individual
wait4 receipts are diagnostics and are never added again to phase child deltas.
Failed reads and counter regressions are unavailable, never fabricated zero.
Full phase process-tree CPU remains unknown; no complete exclusive phase-cost
claim follows from these fields. Supervisor formatting uses the shared checked
integer and six-digit decimal functions; no supervisor launch tested its guard.

| Requirement | Outcome |
| --- | --- |
| Checked conversion and correct legacy scaling | Five exact conversions plus negative/range/overflow cases pass. |
| Child status/usage failure retention | Both fake backend and fake helper IPC paths retain success/exit17/SIGTERM/127 records; malformed-codec evidence remains after receipt creation. |
| Phase success/exception and unavailable counters | Separate self/child fields, exception checkpoint and pure failed-counter-return fixture pass. |
| No double counting / coverage honesty | Synthetic phase delta remains40us when a separate40us child diagnostic exists; no extra addend or complete-tree label. |
| Native strict build and formatting | Corrected build and exact-file clang-format check pass. |
| Scientific / performance evidence | None produced or inferred. |
| Source publication and independent review | Pending parent commit/push/binding and the separately assigned owned-joint review. |

## Exact commands and retained failures

From `/workspace/crypto-native-smallroot`:

```sh
make -C experiments/joint-smallroot-native \
  BUILD=/workspace/native-smallroot-cpu-build-dc4016-1 -j2 all cpu-accounting
/workspace/native-smallroot-cpu-build-dc4016-1/cpu-accounting \
  /workspace/native-smallroot-cpu-build-dc4016-1/fake-child \
  experiments/joint-smallroot-native/spec/checks/TASK-20261026-dc4016/fixtures-attempt1
/workspace/native-smallroot-tools/clang_format/data/bin/clang-format --dry-run --Werror \
  experiments/joint-smallroot-native/src/{usage,backend,cdd_ipc,pipeline,supervisor}.hpp \
  experiments/joint-smallroot-native/tests/{cpu_accounting,fake_child}.cpp
```

The first build exited2 on two mixed-type auto declarations in the new fixture
file; its stdout/stderr/exit are preserved. After splitting those declarations,
build-attempt2 and fixtures-attempt1 exit0. No expectation changed. Exact raw
records and all per-child/phase receipts are in owner
`experiments/joint-smallroot-native/spec/checks/TASK-20261026-dc4016/` and are
individually hashed by [owner-source-manifest.json](owner-source-manifest.json).
A metadata-only Node child-process Git helper returned EPERM; the retained
reproduction log records it. Thin shell Git listings and Node file reads completed
metadata generation without changing tests or source semantics.

Current root Cargo validation remains failed: parent attempt7 at owner27fca
exits101 for an unchanged upstream unclosed delimiter in
`src/cryptanalysis/binary_semaev_chain_sat.rs`, blob
`3803524139ef5382d85f835107339d66d5909a6d`. Its actual log SHA256 is
`c5c5cf1a7ee6b111b654532f5e94d28a09453219696205221acd2cdaf935be14`.
This producer did not repair unrelated Rust or rerun that suite. Earlier4862-pass
results belong to b02, not this source. Hosted Actions availability and normal
publication gates are not bypassed.

## Source, scope and provenance

Owner base: `27fca7749299469bd93bad3a1eed8e7e6a3b6a75`, branch
`research/joint-smallroot-native-20261026`. Only the published exact source/test/
Makefile/new spec/check paths, the README's stale CPU paragraph and an additive
today log entry change. Mathematical/admission source, old receipts, locks,
queues and frozen plans remain unchanged. Actual local Conductor T-2/id
`14d784d6-1043-4bcc-b6a2-4d0925815fa0` reserves native directory and today's log at
epoch1. A fresh sanitized live observation was read before edits; parent manages
its heartbeat and release. No cross-host exclusivity is asserted.

The source commit/publication fields remain null until the parent publishes and
verifies actual owner bytes. Local hashes do not establish durable publication;
independent review waits for that binding. [validation.json](validation.json)
records commands, all17 outcomes, coverage and remaining gates.

Literature/source review used current owner instructions/log, frozen continuation,
prior CPU source, installed resource/wait declarations and the Linux primary
[getrusage](https://man7.org/linux/man-pages/man2/getrusage.2.html) and
[wait4](https://man7.org/linux/man-pages/man2/wait4.2.html) documentation. They
establish units, reaping and counter scope, not a cryptanalytic result. No new
mathematical theorem or visual scientific result is claimed; canonical research
graphs remain unchanged.

Actual managed native invocation: `/root/native_smallroot_implementation_20261026`,
parent-selected `gpt-6.1-sol/high`, policy `executor-implementation`, published
explicit task-local overlay, Executor authority. No alternate model API/CLI,
API catalogue probe, serving attestation, fallback, degradation or delegation.
The original reach-cost tradeoff and verified improvement over the current
prime-field IC baseline remain unresolved.

## Parent publication update

The producer text above records its pre-publication release. The parent control
plane has now published owner commit `86ddd19f67e08160c22a0d8ba9a32a92321d18ad` in
[PR2642](https://github.com/isogeny-labs/crypto/pull/2642), verified its actual
parent and all107 changed Git-blob hashes, and filled the manifest publication
fields before programme snapshot/release binding. Original producer manifest
SHA153daf28effed893eb7354ffaa933bb71820dafe6f4ea1c9fc963759b57da4a6 is
retained in validation provenance. Five raw fake-helper vertex files retain
serializer whitespace advisories; no raw records were normalized. Independent
review remains pending; no scientific or complete-tree-CPU assertion follows.
