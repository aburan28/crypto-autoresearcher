# Modal counted-study engine implementation

This is source preparation and fixed software conformance, dated 2026-10-27.
It draws no confirmation inputs, invokes no native EC solver, performs no
provider API call, and asserts no study result or clock qualification.

The native source remains `fe01ccd832832488c58abeef17548b0a8db6035f` (source A).
`engine.py` imports the existing public input reader, cell writer, schedule,
`os.wait4` child launcher, output-shape check and lossless stream splitter by
reference. Their source-A byte hashes are checked before execution. The
Isolab entry point, its admission guard, native implementation, verifier,
analysis, vendor files and historical manifests are unchanged.

The new module supplies its own frozen-protocol admission for canonical backend
`modal`, runtime `vm`, blocked workload network, one attempt and no restore. It
checks the controller-provided actual SDK App, Sandbox and Image identifiers
using their distinct field names. A Modal Image ID is not an OCI digest. These
identities are labeled controller-supplied; guest code cannot independently
attest the provider control plane. Build-info, its complete code-file hash map,
the adapter manifest and native executable are read back and checked against
launch pins. Actual execution requires Linux `wait4` and observed UID/EUID and
GID/EGID 1000 with no other supplementary group.

All 128 cells and six arms remain in the exact original interleaving, making
768 fresh native child attempts when uninterrupted. Every child record retains
its 64 ordered public target IDs even when it is never attempted. Existing
counter/trace bytes are preserved without transformation, including partial
streams. Nonzero exit, timeout, incomplete output, infrastructure failure and
interruption remain records. Every clock has `wall_valid:false`. Host facts
come from the guest's actual `/proc`, cgroups, affinity and process identity;
physical isolation and native L2 remain unestablished.

`planned` counts schedule slots. `attempted` counts confirmed native children
returned by the unchanged `wait4` helper. A helper exception can occur before
or after process creation, so those records have `attempts:null`, an unresolved
spawn observation, and contribute to `attempts_unresolved`; they are never
credited as completed executions or silently counted as a known zero. A slot
never handed to the helper has `attempts:0` and no native rusage.
An unresolved child stops all subsequent native starts, leaving the remaining
slots unattempted. This prevents overlap with a child whose PID is hidden by
the unchanged helper's exception; the controller retains and closes the same
Sandbox rather than retrying the ambiguous invocation.

The eleven conformance tests use fixed dimension-only text fixtures and
a fake child. They compare the entire invocation order to the original helper,
compare generated TSV bytes, retain 8,192 distinct software-only IDs, check
unchanged counter streams and reconstructed parts, retain all failure classes,
and verify source/binary/context tamper refusals. They do not validate provider
capacity, account admission, privileged bootstrap, real execution, numerical EC
correctness, independent equations, scientific adherence or performance.

Sources checked before implementation:

- `AGENTS.md`, `docs/agent-contract-extended.md` literature-first and
  observation-first rules; `docs/experiment-protocol.md`, especially frozen
  identities, counted metrics, failed outcomes and unqualified clocks.
- `harness/classical_ecdlp_endpoint_reuse/README.md`, execution README,
  `execution/run_experiment.py`, `execution/worker.py`,
  `execution/image_build.py`, `execution/test_adapter.py`,
  `cohort/public_inputs.py` and `protocol/seed_rules.py`.
- `docs/reports/classical-ecdlp-endpoint-reuse-20261026/report.md`, which checks
  prior endpoint-recycling work and states the invariant and complete-cost
  boundary. No mechanism, novelty or inference change is introduced here.
- Official Modal Sandbox, networking/security and existing-image documentation,
  retrieved 2026-10-27 and retained under
  `/workspace/classical-ecdlp-endpoint-reuse/modal-route-feasibility/docs/`.
  Its retrieval manifest binds URLs and bytes. The documented `runtime="vm"`,
  `block_network=True` and ignored Dockerfile `USER` motivate separate runtime,
  controller option recording and an actual UID check. The documentation does
  not establish physical-host exclusivity or L2.
- The root agent's actual software-only VM receipt
  `/workspace/classical-ecdlp-endpoint-reuse/modal-vm-software-probe-20261027-02.json`
  reports a successful basic Sandbox and actual SDK IDs, with UID 0. It does
  not establish UID 1000 bootstrap, scientific artifacts or a measurement run.

No new literature retrieval was made by this implementation task. The retained
official source text and linked prior audit are its bounded source review;
there is no new mathematical claim or canonical graph change to support.
