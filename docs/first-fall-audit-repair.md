# First-fall audit launcher repair

The frozen EXP-PFDR-845d33 package remains an incomplete attempt. This engineering
repair does not overwrite it or grant a research rerun. DEC-20260906-280035 still
requires a separately frozen successor contract.

## Resource and receipt boundary

`tools/audit_process.py` writes `launch.json` before resource setup and retains
stdout, stderr and a terminal `receipt.json` for setup errors, command failures
and timeouts. Output directories are exclusive: a repeated invocation cannot
replace an existing attempt. An externally killed supervisor cannot guarantee a
terminal receipt; its launch record remains available for reconciliation.

On Linux the native backend sets and reads back hard RLIMIT_AS and RLIMIT_CPU
limits before executing the payload. It records wait4 child CPU and peak RSS.
This backend is for a single-process payload: address-space limits are per
process and are not an aggregate descendant-memory boundary.

On macOS, use the Docker backend with an existing Linux image addressed by its
full `sha256:` image ID. The launcher never pulls a mutable tag. It creates a
container, verifies its configured memory, memory-plus-swap and CPU bounds, then
starts it. The container has swap disabled, one CPU, no network, a read-only
workspace/root filesystem, and a bounded PID count. Docker setup and execution
share the wall budget, with time reserved for forced container cleanup. Cleanup
failure is retained as infrastructure failure. No existing container is removed.

Docker CLI CPU/RSS is not payload telemetry. Docker receipts explicitly leave
those metrics unavailable; an approved successor must collect payload telemetry
inside the container before claiming complete instrument validity. A successfully
exited payload is a process outcome, not a completed-valid research run.

Example (infrastructure probe only; supply a verified local image ID):

```sh
python3 tools/audit_process.py --output /tmp/unique-audit-probe \
  --backend docker --image sha256:FULL_LOCAL_IMAGE_ID --seconds 30 \
  -- python3 -c 'print("probe")'
```

The native backend deliberately refuses macOS instead of replacing a hard memory
limit with an unenforced RSS limit. Host preflight reproduced the original
RLIMIT_AS error, including outside the execution sandbox.

## Manifest compatibility

The JSON schema accepts anchored random-suffix identifiers, an explicit
certificate-kind declaration, and unavailable resource measurements on failed or
inconclusive runs. Completed-valid runs still require numerical resource values.
A claimed mathematical certificate requires `verified: true`. All four existing
normalized failure views now validate without modifying their bytes. The original
manifests still lack the mandatory certificate declaration; their registered
normalized views are the intended schema input.

The supervisor receipt is intentionally not a research manifest. A successor
adapter must construct the canonical manifest and validate it before measurement;
it must not reuse the frozen driver's incompatible extra fields/status layout.

## Definition interface for a successor

A concrete proposed resolution is to form top forms in the ordinary polynomial
ring first and then map them into the truncated ring, preserving each original
generator degree as the weight of its slot in the graded free module. A zero image
then has an explicitly weighted slot, rather than needing an intrinsic degree
assigned to the zero polynomial. The quotient by the declared trivial syzygy
module must use the same weights. Ordinary last-fall computation remains in the
ordinary ring, without adding field equations.

This is a proposed explicit implementation convention, not a new source theorem
or an approved native measurement. The successor must document its agreement with
Definitions 1.3/1.5 and Examples 4.2/4.4 of Caminata–Gorla,
https://arxiv.org/pdf/2112.05579 (provenance: retrieved in the preceding source audit;
see EXP-PFDR-845d33/source-audit.md and TASK-20260906-46c863's review). In particular,
check the treatment of zero slots against the displayed syzygies before freezing
code. No degree prediction is promoted to an observation by this repair.

## Regression verification

```sh
python3 -m unittest tools.test_audit_process tools.test_audit_manifest_schema -v
```

Tests cover refusal before payload execution, immutable receipts, daemon timeout,
Docker limit readback/cleanup, schema compatibility, and rejection of unsupported
success/certificate claims. Linux integration tests additionally execute a small
successful process, force a wall timeout, and verify an allocation exceeding the
hard address-space limit fails. They are skipped on macOS and run in the dedicated
`audit-runner` GitHub Actions job. These are infrastructure tests, not research
fixture attempts.
