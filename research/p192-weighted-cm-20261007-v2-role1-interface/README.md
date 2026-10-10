# P-192 weighted-CM Role-1 interface addendum

This directory is an additive, non-executing interface overlay for Role 1
(`P192-WCM-PREFLIGHT`) of `EXP-SCURVE-1a8daf` protocol v2. It does not modify or
replace the checksum- and receipt-bound v2 archive.

- `../../experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml`
  is the authoritative interface addendum. It freezes the previously missing
  JSON schemas, REF-0 binary files and literal order, Role-1 control subset,
  source bindings, independent agreement, and supervisor receipt.
- `run-family.role1-interface.yaml` repeats the exact immutable Role-1 child
  argv, the exact supervisor argv, nine immutable outputs, five addendum-owned
  children, and six canonical v2 custody outputs.
- `schemas/role1-artifacts.schema.json` is the closed-key Draft 2020-12 schema
  bundle for the Role-1 output documents. Its filename-specific
  `factor-base.json` definition mirrors and enforces the schema already frozen
  in `specification.v2.yaml`; it does not replace that authority.
- `schemas/role1-dispatch-decision.schema.json` is the closed, versioned schema
  for a later fresh Coordinator decision. No decision is created by this
  package.
- `check_role1_interface.py` verifies immutable base hashes, exact argv/output
  arrays, pending state, schema closure, REF-0 count/order/bytes, control
  staging (including exact mutation target pointers and the at-`L` endpoint
  mutation), source bindings, decision admission, source-clone screening, and
  post-run custody without executing a native binary.
- `SHA256SUMS` binds this additive payload and its mutation test while excluding
  itself. It is separate from, and does not rewrite, the archived v2 manifest.

The addendum keeps `execution_authorized: false`. It records no scientific run,
relation, factorization result, timing, or weakness claim. A later decision is
stored only at `ledger/decisions/DEC-YYYYMMDD-<six-lower-hex>.yaml`, and its run
is a newly allocated `RUN-SCURVE-<six-lower-hex>` under this experiment. The
decision authorizes one composite non-scientific `P192-WCM-PREFLIGHT` invocation
only; retry, resume, later roles, scientific execution, and scientific result
recording remain false.

Let P be the clean commit containing this complete package, and D the later
commit adding the decision. P must be a strict Git ancestor of D. Every protected
protocol path must have the same Git mode and blob at P and D, while the working
tree used for pre-dispatch must be clean with `HEAD == D`. The decision binds
normalized absolute binary paths, exact binary lengths and SHA-256 values, and
both the clean Git `repository_path` and exact descendant crate `package_path`
for supervisor, producer, and verifier. The full twenty-three-string supervisor
argv uses the producer/verifier crate roots, the exact protocol checkout and
decision paths, and keeps the dependency audit at
`RUN_DIR/dependency-audit.json`.

The decision cannot contain its own commit or byte hash without becoming
self-referential. Instead, immediately before it creates the run directory, the
supervisor requires a clean protocol checkout, derives D from its HEAD, verifies
the exact committed decision blob and all P-protected blobs, and records the
decision path, D, raw decision SHA-256, and checkout facts in the closed receipt
`decision_binding`. `raw-result.json` hashes that receipt and the final manifest
hashes both, so post-run evidence cannot be silently paired with another
decision.

The three closed `authorization.executables` records are the sole minimal build
receipts. They bind clean release source commits, crate roots, executable bytes,
and embedded commit metadata; no separate unnamed build-receipt artifact is
required. They intentionally do not claim a fully serialized compiler/toolchain
identity. The dependency audit separately binds Cargo/source bytes and a
deterministic structural clone screen, which the checker recomputes from both
decision-bound `src` roots before dispatch and again against the retained audit
during post-run admission.

The supervisor owns `independent-agreement.json`,
`independent-verifier-receipt.json`, `dependency-audit.json`, and the six v2
custody files. `command.txt` is canonical JSON for the resolved supervisor argv;
`stdout.log` and `stderr.log` are domain-separated framed child streams, not
captures of the supervisor process; `raw-result.json` is a non-scientific
summary; and `manifest.yaml` is canonical JSON/YAML written last with an exact
inventory excluding itself. All writes stay below the fresh RUN_DIR.

Role 1 has no mid-shard checkpoint or resume artifact. Its determinism control
performs two independent complete in-memory REF-0 regenerations inside each
implementation and compares all three streams, four roots, and seven counters.
It claims no external two-directory build or crash recovery; the interrupted
resume obligation remains with Roles 2 through 4.

Validate from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_p192_wcm_role1_interface.py
```

After clean release binaries and a fresh committed decision exist, the only two
additional accepted invocations are:

```text
PYTHONDONTWRITEBYTECODE=1 python3 research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py --decision ledger/decisions/DEC-YYYYMMDD-xxxxxx.yaml --decision-commit DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD --pre-dispatch
PYTHONDONTWRITEBYTECODE=1 python3 research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py --decision ledger/decisions/DEC-YYYYMMDD-xxxxxx.yaml --decision-commit DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD --run-dir /absolute/repository/experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-xxxxxx --post-run
```

The default invocation is static validation. `--run-dir` without the complete
post-run decision tuple is rejected, and the checker never launches the
supervisor, producer, or verifier.
