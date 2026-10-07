# P-192 weighted-CM Role-2 BOX-0 interface

This package is an additive, non-executing interface amendment for Role 2 of
`EXP-SCURVE-1a8daf`. It closes the native producer, isolated verifier,
checkpoint/restart control, predecessor provenance, and supervisor custody
boundaries that the immutable v2 protocol left open.

It does **not** authorize a run and contains no curve-search result. Both the
addendum and run-family overlay set `execution_authorized: false`; a later,
canonical, committed Coordinator decision conforming to
`schemas/role2-dispatch-decision.schema.json` is mandatory.

## Frozen execution shape

- The producer enumerates exactly 262,148 BOX-0 records in `(v,x)` order and
  emits one logical shard. The 4,194,368 candidate bytes are virtual.
- The isolated verifier receives both `RUN_DIR` and `PREDECESSOR_DIR`, rebuilds
  the factor base and every BOX-0 disposition independently, and shares no
  producer implementation component.
- The predecessor's `factor_base_source_commit` is explicit input provenance
  and must equal the Role-2 `producer_commit`, preserving the immutable v2
  checkpoint contract. The independently implemented `verifier_commit`
  remains separately bound; no identity is silently relabeled as another.
- The supervisor owns process launch, source/binary/dependency hashes, immutable
  input snapshots, restart-control mutation, comparison, agreement, and the
  final receipt. It contains no curve arithmetic.
- The protocol checkout is part of the evidence. Its clean HEAD is the decision
  commit, the admitted protocol commit is a strict ancestor, the decision is an
  exact committed regular blob, and every protected interface blob is identical
  at both commits and in the checkout. The protected list includes every
  Role-2 payload named by `SHA256SUMS`, not just the manifest itself. Producer,
  verifier, and supervisor each
  bind an exact repository top level and package root rather than an ambiguous
  source directory.

BOX-0 is shorter than one logical shard. The restart control therefore stops
after the sole checkpoint but before final manifests, appends a fixed non-NUL
ASCII string plus one zero byte to each committed append file, and resumes.
The resumed producer must truncate only those uncommitted suffixes and produce
all eight producer-owned final artifacts byte-for-byte equal to the clean run.
This tests durable-prefix recovery; it does not claim mid-shard recovery.

## Canonical bytes and schemas

JSON is UTF-8 RFC-8785 canonical JSON without a trailing LF. JSONL is one such
object plus exactly one LF per record, with records strictly increasing by
`candidate_index`. Binary disposition records and their variable certificate
hash suffixes are fixed in the addendum. Unknown keys, reordered check IDs,
reordered artifact inventories, path aliases, symlinks, implicit defaults, and
unresolved placeholders are invalid.

`schemas/role2-artifacts.schema.json` closes every Role-2 scientific or
supervision JSON/JSONL record. `schemas/role2-dispatch-decision.schema.json`
closes the future authorization object. JSON Schema handles shape and types;
`check_role2_box0_interface.py` handles duplicate-key rejection, Git decision
custody, normalized/non-symlink paths, exact argv, ordering, conservation,
canonical bytes, disposition streams, and post-run cross-document rules. It
also independently enumerates each role's complete Rust-source inventory,
rehashes the package Cargo.toml and repository Cargo.lock, and recomputes the
frozen structural clone screen rather than trusting dependency-audit claims.
Failure custody carries both invalid and unresolved counts and excludes
malformed or partial files from its completed-artifact inventory.

## Resource envelope

The protocol-wide dispatch ceiling remains 32 producer workers, 128 GiB RAM,
512 GiB disk, and 259,200 seconds. The candidate stream itself is 4.20 MB
virtual and `disposition.bin` is exactly
`2,621,480 + 64 * retained_count` bytes (2.62--13.44 MB). Certificate and
relation JSONL sizes are data-dependent and therefore are not guessed here;
the 512 GiB bound is the hard admission check. No wall-clock estimate is an
evidence claim until a release-build pre-dispatch benchmark records it.

## Native implementation sequence (not performed here)

1. Extend `tools/p192-weighted-cm/src/producer/mod.rs` with the exact `sieve`
   and `--resume` parsers, then add shell-neutral candidate/disposition code
   plus BOX-0 writers and checkpoint recovery. Producer-local arithmetic,
   certificate, digest, and factor-base code may be reused. The current
   `producer/ref0.rs::build_reference_segmented` is a REF-0 control, not an
   acceptable BOX-0 kernel: its prime-major full rescans must be replaced by
   bounded shard-local residue marking without changing record order.
2. Add `verify-shell` in `tools/p192-weighted-cm-verify/src/main.rs` and new
   verifier-owned BOX-0/replay modules. Its existing `encoding.rs`,
   `factor_base.rs`, and `ideal.rs` are useful only as independently authored
   verifier components. The verifier must not import or text-include producer
   modules, link `crypto_lib`, or delegate a check to producer self-check code.
3. Generalize `tools/p192-weighted-cm-supervisor/src/main.rs` into the frozen
   BOX-0 argv/custody path. It may reuse process, filesystem, Git, and hashing
   mechanisms, but no curve, ideal, norm, factorization, or certificate
   arithmetic.
4. First pass golden iterator/root/encoding fixtures and mutation tests; then
   pass crash-before-checkpoint genesis recovery, the frozen post-checkpoint
   suffix control, symlink/path/inventory rejection, source mutation, wrong
   predecessor, wrong commit, and producer/verifier disagreement tests.
5. Only after independent review, create clean release builds, record their
   commits/hashes, rerun or validate Role 1 at the same clean producer commit
   used by Role 2, and author a fresh decision at its frozen path in a clean
   protocol descendant commit. Validate both `--pre-dispatch` and `--post-run`;
   until then the execution gate remains closed.

## Validation

From the repository root:

```text
python research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py
python research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py --decision /absolute/protocol/ledger/decisions/DEC-YYYYMMDD-xxxxxx.json --pre-dispatch
python research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py --decision /absolute/protocol/ledger/decisions/DEC-YYYYMMDD-xxxxxx.json --post-run --run-dir /absolute/runs/RUN-SCURVE-xxxxxx
pytest -q tests/test_p192_wcm_role2_interface.py
sha256sum -c research/p192-weighted-cm-20261007-v2-role2-box0-interface/SHA256SUMS
```

These commands validate the interface only. They do not invoke the native
producer or verifier and do not perform a scientific run.
