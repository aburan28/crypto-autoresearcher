# TASK-20260802-964 task report

Determination: **APPROVE** the bounded, session-scoped adapter extension
protocol in `coordinator_protocol.yaml`.

The observed Codex 0.144.6 probe is a credible feasibility proof: one named
thread produced `PROBE_OK`; its state row reports `gpt-5.6-sol`, `xhigh`,
provider `openai`, source `exec`, and CLI 0.144.6; that model and effort agree
with the thread-local rollout `turn_context`, and the rollout contains matching
`session_meta`. This is enough to specify an implementation. It is not itself
a compliant adapter receipt and makes no model, backend, or research claim.

The approved command is `python3 -m orchestration.adapter
probe-codex-session`. It must receive explicit Codex binary, state database,
workdir, model, effort, policy, role, task ID, and receipt path; create exactly
one new non-ephemeral read-only `codex exec` thread; parse exactly one
`thread.started` ID; and query only that ID. It verifies exact agreement among
the request, the single state row, `session_meta`, and the single probe
`turn_context`. Unknown or ambiguous metadata fails closed.

Privacy is structural rather than advisory: no thread enumeration, rollout
globbing, prompts, environment dumps, credentials, tokens, raw events, or full
base instructions may enter the receipt. The receipt retains only allowlisted
values, safe argv, timestamps, byte counts, and source hashes. It is immutable
and scoped to one independent session ID.

A receipt may set `runtime_resolution_verified: true` only after the probe and
`tools/check_runtime_bindings.py` both pass. It must simultaneously state
`verification_scope: exact_codex_session_only`,
`global_backend_verified: false`, and `model_bindings_mutated: false`. No
change to `orchestration/model-bindings.yaml` is authorized.

Implementation is not authorized to dispatch reviewers. Code, fixture-only
tests, documentation, and a representative receipt must first be snapshot-
committed and independently validated. R3 and R4 then need separate new
verified sessions and must execute in or resume their exact receipt-bound
thread IDs.

No code was implemented, no live probe was run, no review was dispatched, and
no merge, stage, commit, inference amendment, or research-state change was
performed. Only the two TASK-964 deliverables were written.

Inference provenance remains unresolved for this Coordinator session: the
requested policy was `coordinator-orchestration-code` at `high`, but no exact
probe-verified runtime model identifier was exposed, so `model_verified` is
`false`.
