# Emit Procedure: Runtime Host Binding for v2 Receipts

## Purpose

This document is the procedure any dispatched session follows to emit a
runtime-session-receipt with a REAL, verifiable host binding in the v2
shape. It closes the disclosed limitation HOST-BINDING-ENFORCEABILITY by
attaching a runnable harness (`emit_host_binding.sh`) that reads the host's
own identity surfaces and produces a `host_binding` block any reviewer or
dispatcher can independently verify.

## Prerequisites

- The session runs on a POSIX-compatible host (macOS or Linux).
- `emit_host_binding.sh` is available at the task directory path declared
  in the dispatch queue.
- The session has shell access to run `hostname`, `df`, and `date`.
- No network access is required or used by the script.
- No repository writes are performed by the script.

## Step 1: Run the emit script

From the session's working directory (the worktree root), run:

```sh
sh <task-dir>/emit_host_binding.sh
```

For this batch, the task directory is:

```
coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/
```

So the exact invocation is:

```sh
sh coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/emit_host_binding.sh
```

The script reads three host identity surfaces:

| Field             | Surface (macOS)           | Surface (Linux)                    | Normalization (v5 rule)                          |
|-------------------|---------------------------|------------------------------------|--------------------------------------------------|
| `host_id`         | `hostname`                | `hostname`                         | trimmed, case-preserved                          |
| `filesystem_id`   | `df -P .` column 1        | `df -P .` column 1 / `findmnt`     | lowercase, trimmed, no trailing slash            |
| `filesystem_mount`| `df -P .` trailing column | `df -P .` trailing column / `findmnt` | absolute POSIX path, trailing slash stripped except "/" |

The script emits a single JSON object on stdout:

```json
{"schema":"crypto.autoresearch.runtime_session_receipt.v2","host_binding":{"host_id":"...","filesystem_id":"...","filesystem_mount":"..."},"emitted_at":"2026-08-30T02:35:47Z"}
```

### Failure behavior

If ANY identity surface is unreadable or empty after normalization, the
script:

1. Writes a diagnostic to stderr naming the unreadable surface(s).
2. Emits NO partial JSON block on stdout.
3. Exits nonzero.

If the script exits nonzero, the session MUST NOT fabricate or hand-write a
host_binding block. The receipt is emitted WITHOUT the v2 host_binding
fields (a v1-shaped `host_binding.note` recording the failure), and the v5
`missing_receipt_field: STOP` rule applies by absence. The session records
the failure in its `commands` list and `protocol_deviations`.

## Step 2: Capture the output

Capture stdout to a file or shell variable:

```sh
BINDING=$(sh coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/emit_host_binding.sh)
```

Verify the exit code is zero before proceeding:

```sh
if [ $? -ne 0 ]; then
  # surface unreadable; do not emit a v2 host_binding block
  # record the failure and proceed with a v1-shaped absence note
fi
```

## Step 3: Merge into the v2 receipt

The session's `runtime-session-receipt.json` carries a `host_binding`
block. Under v2, this block is populated from the script's output:

1. Parse the script's JSON output.
2. Extract the `host_binding` object (containing `host_id`,
   `filesystem_id`, `filesystem_mount`).
3. Place it as the `host_binding` field in the session's
   `runtime-session-receipt.json`.
4. Set the receipt's `schema` field to
   `crypto.autoresearch.runtime_session_receipt.v2`.

The resulting `host_binding` block in the receipt looks like:

```json
"host_binding": {
  "host_id": "Adams-MacBook-Pro.local",
  "filesystem_id": "/dev/disk5s1",
  "filesystem_mount": "/Volumes/SSD990"
}
```

Do NOT include the `emitted_at` or `schema` fields from the script output
inside the receipt's `host_binding` block — those are script-output
metadata. The `emitted_at` timestamp may be recorded in the session's
`commands` list as evidence of when the binding was captured.

## Step 4: Record the command in the session receipt

The session's `runtime-session-receipt.json` `commands` list MUST include
the exact emit invocation that produced the binding, for example:

```
sh coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/emit_host_binding.sh > demo-receipt.json
```

This makes the binding reproducible: a reviewer can re-run the same command
on the same host and compare.

## What this binding DOES attest

- The `emit_host_binding.sh` script captured the host's hostname, the
  filesystem device, and the mount point of the working directory at the
  moment it ran.
- The values were read from the host's own identity surfaces (`hostname`,
  `df`), not from caller input, environment variables the caller controls,
  or repository state.
- A reviewer or dispatcher can independently verify each value by running
  the same commands (`hostname`, `df -P .`) on the same host and comparing
  the normalized results.
- A caller can no longer supply arbitrary `host_binding` values THROUGH the
  emit procedure: the script reads the host's surfaces and accepts no
  arguments.

## What this binding does NOT attest

- **The emitting session's honesty.** A compromised emitting session can
  still hand-write a `runtime-session-receipt.json` with arbitrary
  `host_binding` values, or run the script on a different host and paste
  the output into its receipt. Nothing in this package INDEPENDENTLY
  cross-checks the capture at emission time. The v5 closure's threat model
  assumed caller-supplied bindings were the attack; this procedure narrows
  that gap (a caller cannot supply values through the schema or the
  procedure) but does not fully close it (a compromised emitting session
  can still misreport its host).

- **That the host identity surfaces are immutable.** The hostname can be
  changed by an administrator; the working directory can be moved to a
  different filesystem; the device mapping can change across reboots. The
  binding is a point-in-time capture, not a permanent attestation. A
  reviewer verifying the binding must run the verification commands at
  review time and account for legitimate changes.

- **That the host itself is trusted.** The binding attests which host the
  session ran on; it does not attest that the host is free of compromise,
  that the filesystem is untampered, or that the hostname is not spoofed.
  These are properties of the host environment, not of the binding
  procedure.

- **Automatic enforcement.** Independent verification (a reviewer running
  the verification commands on the same host) detects a misreported binding
  after the fact, but it is not automatic and must be performed
  deliberately. The v5 `binding_rule_v2` enforces that the receipt's
  `host_binding.*` must match the `host_observation.*` at evaluation time;
  it does not enforce that the receipt's values were honestly captured.

## Scope of what HOST-BINDING-ENFORCEABILITY closes

Against the v5 threat model (caller-supplied bindings): **narrowed, not
fully closed.** The emit procedure removes the caller's ability to supply
arbitrary values through the schema or the procedure. The residual gap is
self-attestation by the emitting session, which is disclosed here and in
the schema document, not hidden.

Against a malicious-runtime threat model (a compromised emitting session
that lies about its host): **not closed.** This package does not address
that threat model. Independent reviewer verification is the available
detection mechanism, not automatic prevention.
