# Emit procedure v3: bounded administrative successor

This procedure belongs to TASK-20260909-2ba74d / BATCH-e59907, approved by
DEC-20260909-8f6b19. It uses the unchanged v2 emitter, SHA-256
`63240dc0df515a9757e8ae763443000421e25e172b8a843a570be63400393b24`.
The emitter is not extended with the new presence rule; consumers apply the
separate checker after JSON parsing. Zero scientific runs are authorized.

Before invocation, independently establish that /bin/sh, /bin/hostname,
/bin/df, /bin/date, /usr/bin/sed, /usr/bin/awk, /usr/bin/tr and /usr/bin/tail
are the intended trusted host executables. Record their literal path, realpath,
SHA-256, uid/gid, permission bits, executable/regular-file status and ancestor
ownership/permissions. Require root ownership and no group/world write access
for the system executable chain. A metadata mismatch STOPs; a missing executable
STOPs without fallback. Metadata and hashing disclose identity and ownership;
they do not establish binary authenticity or cure a compromised operating system.
The local battery records these checks before calling the emitter. Its Python
interpreter is an explicitly recorded absolute path and remains a trusted local
dependency; record its ownership and runtime identity too. Do not select an
executable through modified PATH or reuse historical bare-name examples.

From the exact claimed worktree, the emit command is:

```sh
/bin/sh coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_host_binding_v2.sh
```

For capture, preserve the command status as well as stdout and stderr:

```sh
BINDING=$(/bin/sh coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_host_binding_v2.sh)
EMIT_STATUS=$?
```

Proceed only for status zero and valid JSON. Store the exact command, cwd and
unmodified outputs in the immutable runtime receipt. A failure STOPs; do not
hand-write substitute bindings. Parse host_binding and apply receipt-rules-v3.json
and check_receipt_v3.py to all three fields. Then perform all predecessor
binding_rule_v2 requirements: use only this task's own immutable v2 runtime
receipt, STOP on absent receipt/fields or v1 receipt, reject caller-supplied
active-binding substitutions, and require normalized equality of the observation
and receipt fields. A presence PASS alone cannot authorize a receipt or execution.

An independent reviewer on the same host must inspect the actual claimed
working directory and run, with the same trusted path verification:

```sh
/bin/df -P /Volumes/SSD990/crypto-autoresearcher/.tmp/cm-factor-base-ideas-20260905-01ed89
/bin/hostname
```

Compare independently normalized host/device/mount values with the captured
receipt. STOP on mismatch or inability to verify. Recheck for later receipts;
a prior same-host observation does not bind future captures or changed mounts.

Normalization trims only leading/trailing U+0020, U+0009, U+000A, U+000D,
U+200B, U+200C, U+200D, U+2060 and U+FEFF. Reject absence, JSON null and
non-string first. Preserve host case; lowercase filesystem_id and strip trailing
slashes; strip mount trailing slashes while retaining root /. Finally STOP on
empty or case-insensitive literal null. A legitimate null/NULL/Null identifier
is deliberately rejected: this false positive is part of the rule itself.
Interior characters, including interior zero-width characters, are preserved
apart from the stated case conversion. Other invisible Unicode is outside the
finite set. This is neither all Default_Ignorable_Code_Point coverage nor
hostname/mount syntax validation. Self-attestation, malicious runtimes, dynamic
linkers, environment-driven loader behavior and filesystem truth remain trusted.

The one deterministic local battery uses a harmless task-local alternate sh
sentinel only against this repaired absolute invocation. It writes a marker and
exits if invoked; it never emits or forges a receipt. Historical vulnerable
invocations are never executed. Temporary files are removed after the check and
their source and observations are retained in control-results.json. The battery
is reproducible by passing the absolute test_repair.py path to the recorded
absolute Python interpreter with -B; output files are exclusive-create, so a
reviewer must redirect output with --output-dir to its own declared write scope.

Historical custody: the v1 emitter live bytes differ from its original archive
(f71fe9f2059428888394b0cb6cd031a397879a8519044db70a1776878d54599f versus
8e2e9a1918f9051789d979b76c97ac8fccde7887af66d1bf074303b83cee8f1c).
This known drift remains disclosed. Verify all five original blobs specified by
predecessor-custody.json against their original commits. BATCH-bde652's legacy
archive verification remains defective. No historical files or hashes change.

Sources: batch.json, predecessor-custody.json, predecessor receipt-schema-v2.yaml,
and emit_procedure_v2.md, provenance internal, read by TASK-20260909-2ba74d.
All outcomes remain producer observations pending Coordinator snapshot and fresh
independent reviews. They assert no scientific, cryptanalytic or performance result.
