# Emit Procedure v2: Runtime Host Binding (Sixth-Generation Repair)

## Status and relationship to predecessor

This document is an ADDITIVE sixth-generation successor to
`coordination/goals/GOAL-ENDO-001/batches/BATCH-820ee8/tasks/TASK-20260830-78b00f/emit_procedure.md`
("v1 procedure"). The v1 procedure is not edited, replaced, or
reinterpreted anywhere in this repository; where this document restates a
v1 value it is a literal copy for closure purposes. This procedure repairs
exactly the three objections named in `DEC-20260830-a575a3.bounded_successor_repair_condition`:

- **RT-J2-O1** (PATH manipulation) — repaired in `emit_host_binding_v2.sh`
  (absolute-path command resolution). This document narrows the provenance
  claim accordingly (see "Narrowed provenance declaration" below).
- **RT-J2-O3** (undisclosed paste-from-different-mount attack surface) —
  repaired below with an explicit reviewer verification step.
- **RT-J3-O1** (missing_receipt_field does not fire on empty/null values) —
  repaired in `repair-package-v6.yaml` (`missing_receipt_field_v2`); this
  document does not restate the rule text, it points to the repair map.

**RT-J2-O2 (self-attestation) is explicitly OUT OF SCOPE for this repair.**
It remains a DISCLOSED limitation of the v5 threat model (caller-supplied
bindings), not a malicious-runtime threat model. It is not repaired here
and is not re-litigated.

## Purpose

This document is the procedure any dispatched session follows to emit a
runtime-session-receipt with a REAL, verifiable host binding in the v2
shape, using the repaired `emit_host_binding_v2.sh` harness that resolves
every external command it invokes by absolute path (no PATH lookup).

## Prerequisites

- The session runs on a POSIX-compatible host (macOS or Linux) where the
  absolute paths pinned in `emit_host_binding_v2.sh` exist and are
  executable. The script fails closed (nonzero exit, no stdout) with a
  named diagnostic if a pinned path is missing on the host it is run on;
  see "Narrowed provenance declaration" below for what this does and does
  not mean about trust.
- `emit_host_binding_v2.sh` is available at the task directory path
  declared in the dispatch queue.
- No network access is required or used by the script.
- No repository writes are performed by the script.

## Step 1: Run the emit script

From the session's working directory (the worktree root), run:

```sh
sh coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_host_binding_v2.sh
```

The script reads three host identity surfaces via PINNED ABSOLUTE PATHS
(verified with `command -v` at authoring time on the authoring host; see
`repair-package-v6.yaml` and `runtime-session-receipt.json` for the exact
verification commands and their output):

| Field              | Surface (this host, pinned absolute path) | Normalization (v5 rule, literal copy)                     |
|--------------------|--------------------------------------------|-------------------------------------------------------------|
| `host_id`          | `/bin/hostname`                            | trimmed, case-preserved                                     |
| `filesystem_id`    | `/bin/df -P .` column 1                    | lowercase, trimmed, no trailing slash                        |
| `filesystem_mount` | `/bin/df -P .` trailing column(s)          | absolute POSIX path, trailing slash stripped except "/"       |

The script emits a single JSON object on stdout, in the SAME shape as the
v1 predecessor's output (schema tag, three host_binding fields, UTC
timestamp):

```json
{"schema":"crypto.autoresearch.runtime_session_receipt.v2","host_binding":{"host_id":"...","filesystem_id":"...","filesystem_mount":"..."},"emitted_at":"2026-08-30T18:06:13Z"}
```

### Failure behavior (unchanged from v1, plus one new fail-closed case)

If ANY identity surface is unreadable or empty after normalization, the
script:

1. Writes a diagnostic to stderr naming the unreadable surface(s).
2. Emits NO partial JSON block on stdout.
3. Exits nonzero.

**New in v2:** if a pinned absolute path itself does not exist or is not
executable on the host the script is actually run on (e.g. the script is
carried to a host whose `hostname`/`df`/etc. live at different absolute
paths than the authoring host), the script fails closed the same way —
diagnostic to stderr naming the missing path, no partial JSON, nonzero
exit — rather than silently falling back to a PATH search (which would
reopen RT-J2-O1). Porting this script to a host with different absolute
paths requires re-running `command -v` on that host and updating the
pinned constants; that is a reviewable script edit, never an automatic or
silent fallback.

If the script exits nonzero, the session MUST NOT fabricate or hand-write
a host_binding block, exactly as under v1.

## Step 2: Capture the output

```sh
BINDING=$(sh coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_host_binding_v2.sh)
```

Verify the exit code is zero before proceeding, exactly as under v1.

## Step 3: Merge into the v2 receipt

Unchanged from v1 Step 3: parse the script's JSON output, extract the
`host_binding` object, place it as the `host_binding` field in
`runtime-session-receipt.json`, and set `schema` to
`crypto.autoresearch.runtime_session_receipt.v2`.

## Step 4: Record the command in the session receipt

Unchanged from v1 Step 4: the `commands` list MUST include the exact emit
invocation that produced the binding.

## NARROWED PROVENANCE DECLARATION (repairs RT-J2-O1)

The v1 procedure claimed: "a caller can no longer supply arbitrary
host_binding values THROUGH the emit procedure." The red team
(RT-20260830-d85fdf) showed this was FALSE for v1: a caller controlling
`PATH` could substitute a hostile `hostname`/`df` binary and have the
procedure emit caller-controlled values for all three fields.

This procedure NARROWS the provenance claim to state exactly what remains
trusted, rather than repeating the disproven blanket claim:

- **What is no longer trusted infrastructure, and is no longer an attack
  surface:** the shell's `PATH` environment variable. `emit_host_binding_v2.sh`
  never performs a PATH-based command lookup for any external command
  (`hostname`, `df`, `date`, `sed`, `awk`, `tr`, `tail`); every one is
  invoked by a literal absolute path pinned in the script and verified to
  exist and be executable before use. A caller who prepends a directory of
  hostile binaries to `PATH` cannot influence which binary the script
  executes, because `PATH` is never consulted. This closes RT-J2-O1
  against the exact attack that found it.

- **What REMAINS trusted infrastructure under the v5 threat model, and is
  explicitly NOT defended against by this repair:** the host's own system
  binaries and runtime at the pinned absolute paths themselves — e.g. the
  actual bytes at `/bin/hostname` and `/bin/df` on the host, the dynamic
  linker and shared libraries the shell and these binaries load (dyld on
  macOS, ld.so on Linux, and any `DYLD_*`/`LD_*` environment variables that
  influence library resolution), the `/bin/sh` interpreter executing this
  script, and the filesystem's own reporting of its device/mount identity.
  If the host's own `/bin/hostname` binary has been replaced, or if the
  dynamic linker has been made to load an attacker's shared library into
  it, or if `/bin/sh` itself is compromised, this repair does not detect or
  prevent that — pinning an absolute path removes PATH as a caller-input
  channel, it does not and cannot authenticate the binary found at that
  path. Trusting the host's own binaries and runtime unless a caller can
  reach them is unavoidable for a script running ON that host; the v5
  threat model (caller-supplied bindings via an object the caller submits
  to a validity check) does not include a compromised host runtime, so this
  is an accepted, disclosed scope boundary, not a silent gap. It is the
  same class of residual trust as RT-J2-O2 (self-attestation): both are
  properties of trusting the host and the emitting session rather than
  properties this static repair can eliminate.

- Consequently: **HOST-BINDING-ENFORCEABILITY, against the v5 threat model
  (a caller supplying values through the schema, the procedure, or an
  environment variable such as PATH the caller controls), is now narrowed
  further than the v1 package achieved** — the PATH channel is closed. It
  remains NOT closed against a malicious-runtime threat model (a
  compromised host binary, dynamic linker, or shell interpreter, or a
  compromised emitting session per RT-J2-O2), exactly as disclosed for v1
  and carried forward unrepaired here, per the Coordinator's
  `not_repair_items` scoping of RT-J2-O2.

## PASTE-FROM-DIFFERENT-MOUNT VERIFICATION (repairs RT-J2-O3)

The v1 package did not give a reviewer an explicit, runnable step to detect
the following attack surface: a session runs `emit_host_binding_v2.sh` from
one working directory / mount, and the resulting receipt is presented
(pasted, copied, or reused) as if it described a different working
directory or mount than the one it was actually captured from. The values
in such a receipt are REAL (they were genuinely read from a host's own
identity surfaces) but describe the WRONG filesystem for the claim being
made about it — this is a distinct failure from RT-J2-O2 (a fabricated
value) and from RT-J2-O1 (a caller-substituted value): it is a true value
attached to the wrong claim.

This is disclosed and given an explicit, runnable reviewer verification
step:

**Verification step — independent mount cross-check (human reviewer or
dispatcher performs this, not the emitting session):**

1. Identify the exact working directory the emitting session claims to
   have run `emit_host_binding_v2.sh` from (recorded in the session's
   `runtime-session-receipt.json` `commands` list and in its declared
   worktree path).
2. On the SAME host, independently run:
   ```sh
   df -P <that-exact-worktree-path>
   ```
   (Not from memory, not from the emitting session's own report of what it
   ran — the reviewer runs this command themselves.)
3. Normalize the reviewer's own output using the SAME v5 normalization
   rules the schema declares (`filesystem_id`: lowercase, trimmed, no
   trailing slash; `filesystem_mount`: absolute POSIX path, trailing slash
   stripped except root `/`).
4. Compare the reviewer's independently-derived `filesystem_id` and
   `filesystem_mount` against the values in the receipt's
   `host_binding.filesystem_id` and `host_binding.filesystem_mount`.
5. **Agreement** is evidence the receipt's filesystem values genuinely
   describe the claimed working directory on this host at verification
   time. **Disagreement** means one of: the receipt was captured
   elsewhere and pasted in (the RT-J2-O3 attack), the working directory
   was moved to a different filesystem between capture and verification,
   or the device/mount table changed (e.g. a remount) — the reviewer
   records which, if determinable, and treats an undetermined
   disagreement as a STOP, not a pass.

This verification step does not run automatically as part of
`emit_host_binding_v2.sh` — the script itself has no way to know what claim
a receipt will later be attached to. It is a REQUIRED reviewer action,
named here explicitly rather than left implicit, which is the repair for
RT-J2-O3 ("partially disclosed" in the v1 package becomes fully disclosed
and procedurally actionable here).

## What this binding DOES attest (updated)

- The `emit_host_binding_v2.sh` script captured the host's hostname, the
  filesystem device, and the mount point of the working directory at the
  moment it ran, using binaries at absolute paths pinned and verified at
  authoring time — not binaries resolved through the caller-controlled
  `PATH` environment variable.
- A reviewer or dispatcher can independently verify each value by running
  the same underlying commands (at their own trusted `hostname`/`df`
  paths, or the pinned absolute paths) on the same host and comparing the
  normalized results (see "Paste-from-different-mount verification"
  above for the mount-specific procedure).
- A caller can no longer supply arbitrary `host_binding` values THROUGH the
  emit procedure by manipulating `PATH` or by supplying values through the
  schema. This is the RT-J2-O1 repair.

## What this binding does NOT attest (unchanged in kind, restated for v2)

- **The emitting session's honesty (RT-J2-O2, disclosed, unrepaired).** A
  compromised emitting session can still hand-write a
  `runtime-session-receipt.json` with arbitrary `host_binding` values, or
  run the script on a different host and paste the output into its
  receipt. This is explicitly out of scope for this repair batch per
  `DEC-20260830-a575a3.bounded_successor_repair_condition.not_repair_items`.
- **The integrity of the host's own binaries and runtime** at the pinned
  absolute paths (see "Narrowed provenance declaration" above) — this is
  the newly-explicit residual trust boundary this repair introduces by
  naming it, not a new gap; it existed in v1 too but was not stated.
- **That the host identity surfaces are immutable** (unchanged from v1):
  the hostname can be changed by an administrator, the working directory
  can be moved to a different filesystem, the device mapping can change
  across reboots.
- **That a receipt's filesystem values were captured from the claimed
  working directory** (RT-J2-O3) — this is why the paste-from-different-
  mount verification step above is REQUIRED, not optional, for a reviewer
  who wants that assurance.
- **Automatic enforcement.** Independent verification (a reviewer running
  the verification commands on the same host, from the same claimed
  working directory) detects a misreported or mismatched binding after the
  fact; it is not automatic and must be performed deliberately.

## Scope of what HOST-BINDING-ENFORCEABILITY closes (updated)

Against the v5 threat model (caller-supplied bindings): **narrowed further
than v1.** The PATH-manipulation channel (RT-J2-O1) is closed. The
paste-from-different-mount attack surface (RT-J2-O3) is disclosed with an
explicit, runnable reviewer verification step. The empty/null gap in the
missing_receipt_field rule (RT-J3-O1) is closed by `missing_receipt_field_v2`
in `repair-package-v6.yaml`.

Against a malicious-runtime threat model (a compromised host binary,
dynamic linker, shell interpreter, or a compromised emitting session that
lies about its host): **still not closed, and not attempted by this
batch.** This is the disclosed residual (RT-J2-O2 plus the newly-named host
system binary/runtime trust boundary). Independent reviewer verification
remains the available detection mechanism, not automatic prevention.
