# Implementation and premeasurement freeze — EXP-PFDR-a76b91 (version 1)

Successor execution of the EXP-PFDR-845d33 audit. The scientific protocol (eight fixtures,
four bounded run groups, seeds, budget, prediction, stopping rules) is byte-identical to the
predecessor per the predecessor-equivalence statement in specification.yaml; this freeze
records the execution package of this successor.

## What changed versus the predecessor (and why)

The predecessor's single launch attempt failed before fixture evaluation because the host
(macOS 26.6-arm64) rejects every `RLIMIT_AS`/`RLIMIT_DATA` `setrlimit` call
(`ValueError: current limit exceeds maximum limit`, i.e. kernel EINVAL; reproduced on
2026-09-07 with both available Python 3.13.1 interpreters, outside any sandbox). The
predecessor driver's four reserved run IDs are permanently consumed by their immutable
failure receipts, and the driver creates receipt directories exclusively (`exist_ok=False`),
so the frozen predecessor package is structurally un-runnable on any host. DEC-20260906-280035
requires a separately frozen successor before any rerun; this contract is that successor.

Driver deltas D1-D6 (see specification.yaml `driver_deltas_vs_predecessor`): new run IDs,
contract id, OSError-guarded receipt writes (the container workspace is read-only), dirty
flag computed from actual `git status`, and a final stdout line that carries the run id, the
full certificate dict, and the full driver manifest so the host-side adapter can assemble
the canonical record without re-execution. Fixture evaluation, the checker call, seeds,
limits, and status logic are unchanged.

`checker.py`, `inputs.json`, and `source-audit.md` are byte-identical copies of the
predecessor's frozen files (hashes below match the predecessor freeze).

`adapter.py` (new, this package) is the host-side canonicalizer required by
docs/first-fall-audit-repair.md: it assembles the schema-conforming run record
(schemas/run-manifest.schema.json) from the supervisor receipt plus the driver's stdout
payload, re-verifies the frozen hashes, and validates the canonical manifest before the
group is considered recorded. It never re-classifies driver statuses and never interprets
results.

## Execution environment

Pinned Linux container (digest in specification.yaml `execution_environment`), launched by
`tools/audit_process.py` docker backend: `--network=none --read-only --memory 8589934592
--memory-swap 8589934592 --cpus=1 --pids-limit=64 --cap-drop=ALL
--security-opt=no-new-privileges --tmpfs /tmp:rw,nosuid,nodev`, workspace bind-mounted
read-only at /work, image identity and limit readback asserted before every launch. Inside
the container the driver's own `RLIMIT_AS` 8 GiB call succeeds (verified in the pinned
image), so the frozen memory limit is enforced both by the cgroup and per-process.

Commands (per group, host side, cwd = a clean full clone of this branch):
`python3 tools/audit_process.py --output <supervisor-out>/RUN-PFDR-20260907-<tok> --seconds 900 --memory 8589934592 --backend docker --image sha256:<pinned> -- python3 /work/experiments/EXP-PFDR-a76b91/driver.py --group N --setup-wall-seconds <measured>`
then
`python3 experiments/EXP-PFDR-a76b91/adapter.py --supervisor-output <supervisor-out>/RUN-PFDR-20260907-<tok> --group N --run-id RUN-PFDR-20260907-<tok> --dest experiments/EXP-PFDR-a76b91/runs --prefix experiments/EXP-PFDR-a76b91 --setup-wall-seconds <measured>`

All setup wall time is charged to group 1 (predecessor convention). Limits: 900 s/group
inclusive of setup, 3600 s total, 8 GiB, four groups, one worker. Python standard library
only in the payload; the host interpreter is not the payload interpreter (payload is
CPython 3.10.12 in the container).

No deviations from the stopping rule are anticipated: native arithmetic stops at the
unresolved interface exactly as in the predecessor (groups 1 and 3 unmeasured by design);
no degree estimates are substituted. Fixtures are deterministic, seed 0, zero independent
random samples. Input hashes include complete signature/claim/constant identity.

Frozen files (verified by the driver at launch and by the adapter before canonicalization):
```json
{
  "frozen_at": "2026-09-07T05:15:13.366487+00:00",
  "sha256": {
    "driver.py": "736b7671dfa407f97aa69a25d1102e0c80d8c6bff6e80005ba6f2cbca310f32e",
    "checker.py": "3407c0b95b02579f8653ded5ee52e3740a2e215b34c6373914d2e842624474f8",
    "inputs.json": "5306309f73e8fb3aa54f0e2aed6349243f19add17053b2bedf0d5a6acd268653",
    "source-audit.md": "3af7cb4e7665667ce6082f2c6cae2c10a48683d7a490e26cf8797613fe03883d",
    "specification.yaml": "b7b5cb0a2eb3f8ee46746a8235200b33a5c5a945e10dce9a27e9b0b276fd8fde",
    "adapter.py": "ef88ac344e5d707112062948239d05b54a4cf1eee63511a60955dc0158b7130a"
  }
}
```
