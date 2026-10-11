# Runtime admission — P9 pair-reuse protocol

**Decision:** Admit the native authenticated Codex runtime binding for the
P9 design under `TASK-20260922-3a1ca7`, archived by protocol snapshot
`TASK-20260922-01282b`. This is a bounded runtime approval only. It changes no
protocol field, scientific count, criterion, source, result, or research state.

## Approved bindings

| Role | Requested native binding | Effort | Session requirement |
| --- | --- | --- | --- |
| Executor | `gpt-5.6-terra` under `executor-implementation` | `high` | Native authenticated Codex session with the declared implementation tool surface. |
| Coordinator | `gpt-5.6-terra` under `coordinator-orchestration-code` | `high` | Coordinator session. |
| Source and permanent-blind reviewers | `gpt-5.6-sol` under `review-adversarial` | `xhigh` | Distinct fresh sessions. |

The checked-in `executor-implementation` policy default is medium, while its
model card explicitly permits high. This admission selects the requested
`gpt-5.6-terra`/high Executor binding for P9. Earlier summaries that named an
Executor `gpt-5.6-sol` binding do not govern this protocol.

No fallback, degraded substitution, or Bedrock provider is permitted. Native
authenticated collaboration sessions supply the declared tools. Adapter metadata
is operator-supplied and last probed on 2026-08-02; no fresh API serving probe or
model-identity verification is claimed by this admission.

## Scope and gate

P9 protocol SHA remains
`3de8d70ae219cd2aad2c6ccf67156fdc3d1c6591729efad9e9822224a4d844de`.
The binding authorizes **Stage A implementation and compile work only**. Native
control, independent checker, benchmark jobs, and all scientific measurements
remain subject to the protocol's committed staged admissions and Coordinator
decisions.

W9's own checked-in preflight returned READY. A prior canonical skill-path
mismatch came from running a newer primary-checkout preflight against W9; it was
resolved by using W9's checked-in preflight and its `WORKFLOW.md` rename, with no
code edit or scientific interpretation.

Root retains orchestration, Git, and launch ownership. This admission carries
zero runs, 2 GiB memory, and null wall-clock budget. It asserts no runtime,
scientific, performance, or result outcome.

**Citation provenance:** all configuration and preflight facts are `internal`.
