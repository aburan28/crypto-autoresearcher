# P-192 weighted-CM Role-1 interface addendum

This directory is an additive, non-executing interface overlay for Role 1
(`P192-WCM-PREFLIGHT`) of `EXP-SCURVE-1a8daf` protocol v2. It does not modify or
replace the checksum- and receipt-bound v2 archive.

- `../../experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml`
  is the authoritative interface addendum. It freezes the previously missing
  JSON schemas, REF-0 binary files and literal order, Role-1 control subset,
  source bindings, independent agreement, and supervisor receipt.
- `run-family.role1-interface.yaml` repeats the exact immutable Role-1 argv and
  nine top-level outputs, then names the four addendum-owned child artifacts.
- `schemas/role1-artifacts.schema.json` is the closed-key Draft 2020-12 schema
  bundle for the eight newly specified JSON document types. The already-frozen
  `factor-base.json` schema remains in `specification.v2.yaml`.
- `check_role1_interface.py` verifies immutable base hashes, exact argv/output
  arrays, pending state, schema closure, REF-0 count/order/bytes, control
  staging (including exact mutation target pointers and the at-`L` endpoint
  mutation), and source-binding rules without executing either native binary.
- `SHA256SUMS` binds this additive payload and its mutation test while excluding
  itself. It is separate from, and does not rewrite, the archived v2 manifest.

The addendum keeps `execution_authorized: false`. It records no scientific run,
relation, factorization result, timing, or weakness claim. A later dispatch
requires a fresh Coordinator decision binding final clean protocol, producer,
and verifier commits plus exact executable hashes and resolved argv arrays.

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
