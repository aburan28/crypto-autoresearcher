# P-192 weighted-CM Role-2 BOX-0 interface

This package is an additive, non-executing interface amendment for Role 2 of
`EXP-SCURVE-1a8daf`. Interface revision 4 supersedes the unexecuted interface
revision 3 before any Role-2 dispatch; the historical filename retains the v2
protocol-version label. Revision 4 preserves the independently audited custody
closure while making the resource-terminalization boundary explicit, without
changing the immutable scientific protocol. It closes the native producer, isolated verifier,
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
- The complete twenty-file Role-1 run is validated by the protected Role-1
  checker, including replay of its raw bound post-run decision. The Role-2
  decision copies the exact Role-1 receipt and inventory/tree digest and binds
  its decision path, bytes, hash, commit ancestry, child sequence and argv,
  executable identities, commits, artifact identities, and dependency audit.
  A shallow or independently fabricated predecessor PASS document is invalid.
- The supervisor owns process launch, source/binary/dependency hashes, immutable
  input snapshots, restart-control mutation, comparison, agreement, and the
  final receipt. It contains no curve arithmetic.
- The protocol checkout is part of the evidence. Pre-dispatch, its clean HEAD
  is decision commit `D2`, whose sole direct parent is the admitted protocol
  commit. Post-run, HEAD is either `D2` or the sole-direct-child archive commit
  `A2`. The decision is an exact committed regular blob, and every protected
  interface blob is identical at the protocol and decision commits and in the
  checkout. The protected list includes every
  Role-2 payload named by `SHA256SUMS` and the full Role-1 checker/schema
  package, not just either manifest. Producer, verifier, and supervisor each
  bind an exact repository top level and package root rather than an ambiguous
  source directory.
- `RUN_DIR` is exactly
  `PROTOCOL_REPOSITORY_PATH/experiments/EXP-SCURVE-1a8daf/runs/RUN_ID`;
  `CONTROL_DIR` is exactly the sibling controls path ending
  `RUN_ID-restart`; and `AUDIT_FILE` is exactly the run's
  `dependency-audit.json`. Pre-dispatch Git state is clean. Post-run state is
  either both complete, wholly untracked trees or both complete trees committed
  by one archive commit whose sole parent is the decision commit. Every
  filesystem leaf is enumerated directly, independently of committed
  `.gitignore` rules. Local exclude/configuration routes, mixed
  committed/untracked trees, index flags outside the exact `H`/`S` profile,
  multiple archive commits,
  merges, transient/reverted history, or any unrelated
  decision-to-archive-HEAD tree change are invalid.
- Linux execution assumes a trusted local host and exclusive workspace. The
  supervisor attests raw argv0/current_exe/`/proc/self/exe`; producer and
  verifier are distinct once-opened nofollow files copied to four-seal memfds
  and launched by `execve` through retained `/proc/self/fd/N` paths with logical
  argv0 unchanged; fd-only `execveat` is not the attested method. The executable
  ABI is frozen: producer `/proc/self/fd/40`,
  verifier `/proc/self/fd/41`. The three producer invocations reuse one sealed
  image.
- Every predecessor file is likewise copied into its own sealed snapshot;
  every child parses only the fixed inherited snapshot FDs `/proc/self/fd/50`
  through `/proc/self/fd/55` in the exact predecessor inventory order while
  the original six paths are identity/hash checked before launches and
  terminally.
- Role 1 and Role 2 use distinct sealed protocol repositories on two direct
  forks of the same base object: `P -> D1 -> A1` for the predecessor and
  `P -> D2` for Role 2. The checker compares raw `P` commit bytes, complete
  canonical topology, and a SHA-256 custody map for the union of both
  execution-relevant selected/protected blobs plus every committed
  `.gitattributes` policy blob. `A1` is not an ancestor of `D2`.
- Immediately before Role-1 launch, the admitted Role-2 checker emits a sealed
  `D1` repository receipt to a distinct, current-user-owned 0700 directory
  outside the repository. The operator retains that same file, path, inode,
  and bytes unchanged through Role-2 admission and terminal validation; after
  Role 1 finishes, the bytes are copied, not moved, to
  `controls/RUN_ID-pre-execution-repository-custody.json` and committed with
  the exact twenty Role-1 run leaves in `A1`. The committed copy must be
  byte-equal to, but inode-distinct from, the retained outside-repository copy.
  A terminal `A1` receipt is then generated; `D2` embeds and hash-binds both
  the pre-`D1` and terminal-`A1` receipts.
  The `D2` predecessor-repository custody binding records and Role 2 rechecks
  the staging parent's absolute path, device, inode, numeric owner UID, and
  mode. The pre-receipt-to-launch timing is a
  trusted-exclusive operator procedure, not a signature, append-only log, or
  proof that this Python checker held a descriptor through launch.
- The retained directory ABI is experiment parent `/proc/self/fd/60`, runs
  parent `/proc/self/fd/61`, controls parent `/proc/self/fd/62`, `RUN_DIR`
  `/proc/self/fd/63`, and `CONTROL_DIR` `/proc/self/fd/64`. Original descriptors
  retain `FD_CLOEXEC`; immediately before each `exec`, only fixed child-target
  duplicates 40/41, 50--55, and 60--64 clear it. Parents are retained first,
  output roots are created with `mkdirat`, and children perform all leaf I/O
  through inherited descriptors with `openat`-style operations. Logical argv
  paths are identity labels and are never reopened.

BOX-0 is shorter than one logical shard. The restart control therefore stops
after the sole checkpoint but before final manifests, appends a fixed non-NUL
ASCII string plus one zero byte to each committed append file, and resumes.
The resumed producer must truncate only those uncommitted suffixes and produce
all eight producer-owned final artifacts byte-for-byte equal to the clean run.
`CONTROL_DIR` remains intact through terminal validation and archival custody;
only later out-of-band archival cleanup may remove it. This tests durable-prefix
recovery; it does not claim mid-shard recovery.

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
binds every regular package-root file (not just Rust) plus repository
Cargo/workspace/toolchain configuration by raw commit mode and bytes, rejects
rogue empty directories, multi-link inputs, and local-filter evasions by
comparing opened bytes directly with self-hashed raw commit blobs. Each
checkout is a sealed selective worktree backed by a complete v3 stage-zero
index: every selected regular leaf is uppercase `H`, every omitted HEAD leaf
(including inert symlink and gitlink entries) is uppercase `S` and physically
absent, and the index has no cache/state extensions, intent-to-add,
assume-valid, fsmonitor-valid, split-index, sparse-index, or resolve-undo
state. The nofollow worktree inventory contains exactly selected leaves and
their implied parents, plus only the output topology admitted by that exact
phase profile. Source `target/`
roots must contain no tracked HEAD/index leaf before they are excluded as
mutable build output.

The trusted object closure is deliberately narrower than a multi-gigabyte
full clone: the checker self-hashes the admitted commits, every recursively
traversed tree, every selected/protected/decision/output/source-build blob,
and every committed `.gitattributes` policy blob. Ordinary omitted leaf blobs
and gitlink target objects are inert, are never consulted, and need not be
present locally. The store nevertheless has no remote, promisor, alternate,
lazy-fetch, or shallow-history route. Committed attribute declarations may
remain in omitted policy blobs; exact minimal configuration provides no
filter/diff/merge driver, global/system and info attributes are disabled,
selected worktree bytes equal raw blobs, and no checkout or merge occurs after
sealing, so those declarations cannot transform an admitted byte. After every
subprocess for a repository is complete, one final same-repository mixed
commit/tree/blob stream replays its whole admitted closure. Only no-process
identity seals of administration, HEAD/direct ref, index, config, and worktree
paths may follow that stream.

The checkout must be standalone: `.git`, its required object store, index,
configuration, refs, loose objects, and packs are local nofollow regular files
or directories; linked/auxiliary worktrees, alternates, symlinks, special
files, multi-link Git administration files, locks, or in-progress operation
state fail before the first Git process and again at the terminal seal. Walks
have frozen depth, entry-count, aggregate-path-byte, and per-file caps. It
recomputes the whole-package Rust structural
clone screen rather than trusting dependency-audit claims. It rejects
`crypto-lib`, the production `crypto` package/lib target, and producer
dependencies through aliases, recursive wrappers, paths, git, workspace,
build/dev/target-specific tables, patch/replace/source overrides, alternate
registries, and Cargo.lock. The verifier is a literal empty standalone
workspace and every non-root lock package is exact-crates.io and
checksum-bound. The separately bound active lock is each package-root
`Cargo.lock`; a repository-root lock cannot stand in for a divergent
standalone-workspace lock.

The dispatch decision also carries a fail-closed verifier build admission. Its
explicit scientific trust base is hash-bound Cargo/Rustc plus checksum-locked
crates.io packages, proc macros, and build scripts; it does not claim a hostile
compiler or whole-filesystem proof. The checker binds an env-cleared offline,
frozen release build and metadata command, exact argv/CWD/selected bin/features,
one-member workspace, resolved graph and root target set, and opened single-link
tool identities. All ancestor and `CARGO_HOME` configuration candidates must be
absent through retained nofollow directory custody. Cargo target/build paths
must remain inside the package. Token-aware scanning rejects direct, aliased,
imported, reexported, or macro-forwarded `include!`, `include_bytes!`, and
`include_str!` identifiers plus `#[path]`, `cfg_attr(path)`, `OUT_DIR`, and
generated local-code routes. The selected binary's opened dep-info bytes and
hash are bound, and every listed local input must be a single-link committed
file in the verifier package inventory. A committed in-package `build.rs` is source-bound
and its observed directives are allowlisted and must embed the exact clean
release/protocol/verifier tuple. The identical build-custody object appears in
the dependency audit, supervisor receipt, and terminal seal.
Checker-valid failure custody carries both invalid and unresolved counts. Its claimed phase
must match the exact completed-artifact prefix, and every completed filename is
bound to its own schema and cardinality (including the one-row BOX-0 checkpoint
chain). Wrong-schema, empty, malformed, or partial files are excluded while a
separate exact custody inventory retains them as evidence. Every prior phase
must also satisfy its complete PASS semantics and cross-document bindings; a
schema-valid producer, restart, verifier, agreement, audit, or receipt FAIL
cannot be shifted to a later claimed phase. Failure inventories are flat and
hash every top-level regular leaf; directories, symlinks, special or multi-link
leaves, duplicate inodes, and immutable-input aliases are rejected, closing
mutable nested state. `RUN_DIR` and `CONTROL_DIR` are created before the first
child; every checker-valid terminal failure retains and identity-binds `CONTROL_DIR`.
Every checker-valid post-directory failure also retains `stdout.log` and `stderr.log` under
failure-specific domain prefixes with zero through four chronological role
frames. The two logs carry the same role prefix and exact captured bytes; they
are custody-only and never count as completed artifacts, so a failure after
the fourth child cannot be misclassified as completed final custody. Frame
counts are phase-bound: canonical producer 0--1, restart control 1--3,
independent verifier 3--4, and agreement or final custody exactly 4. Thus a
failure record cannot discard streams from children that necessarily finished
before its claimed phase.
Canonical-producer failure requires its retained control inventory to be
exactly empty. Stale PASS-manifest fields record `not_reached` with null/false state
for every pre-manifest failure. Only a bound final-custody post-manifest
transition may record the provisional manifest/raw hashes and true/true removal
state; supervised cleanup never removes the control tree. Failure custody, like
the PASS seal, explicitly scopes device/inode claims to the original supervised
workspace.

On PASS, `terminal-custody.json` is an outer admission seal written only after
the manifest and RUN directory are fsynced and every source, sealed image,
predecessor snapshot/original path, decision/protected blob, RUN, and retained
CONTROL artifact is rechecked. The receipt carries before/after binary
identities and source/build-tree digests; the outer seal additionally records
the terminal decision path/hash, runtime protocol HEAD, and source-build commit
bindings plus exact verifier build custody. A post-manifest failure removes the unpublished
PASS manifest and finalizes deterministic failure custody; no stale PASS seal
is admitted. The seal always records the historical execution mode as
`exact_untracked_output_trees`. Archival replay in that same supervised
workspace may independently observe the one permitted archive commit with the
exact two-tree delta, but cannot rewrite that field. Full `--post-run`
admission is intentionally limited to the original supervised workspace: it
rechecks absolute paths plus device/inode identities and therefore cannot PASS
in a relocated clone. A relocated archive can support a separately described
byte/mode audit, but this package currently exposes no portable-admission mode;
such an audit is not a full protocol PASS.

## Standalone execution-checkout preparation

Dispatch checkouts are deliberately stricter than development clones. Prepare
five pairwise-distinct, non-nested repositories: the Role-1 predecessor
protocol repository, the Role-2 protocol repository, and separate producer,
verifier, and supervisor implementation repositories. Each has its own local
object store. A linked worktree, shared or alternate store, hardlinked object,
remote, promisor, partial-clone marker, lazy-fetch route, shallow boundary, or
external Git administration path is invalid.

A conforming repository may contain the narrow required-object closure instead
of every blob reachable from HEAD. The finite commit domain is exactly `P`,
`D2`, and `A2` iff the Role-2 current HEAD is the permitted archive commit;
`P`, `D1`, and `A1` in the predecessor protocol repository; and the one bound
HEAD in each native repository. Retain each raw commit and every tree reached
recursively from those commits. Retain blob payloads only for
selected/protected/decision/source-build/output leaves and every committed
`.gitattributes` policy leaf. Ordinary omitted blob payloads and gitlink target
objects are inert and may be absent. Object preparation must copy bytes into the
new store rather than hardlink them. Remove every remote/branch/include entry
and rewrite `.git/config` to the bytes represented below; each `\t` represents
one literal TAB byte (`0x09`), not the two bytes backslash-plus-`t`:

```text
[core]
\trepositoryformatversion = 0
\tfilemode = true
\tbare = false
\tlogallrefupdates = true
\thooksPath = /dev/null
```

The final newline is required. Detached HEAD bytes are exactly one lowercase
`[0-9a-f]{40}\n` line. Symbolic HEAD bytes are exactly
`ref: refs/heads/<canonical-name>\n`, and that direct loose ref contains exactly
one lowercase `[0-9a-f]{40}\n` line; chained symbolic refs are invalid. `.git/objects`,
`objects/info`, `objects/pack`, and `refs` are real local directories. Nothing
below `.git` is a symlink, special file, or multi-link regular file.

Use this exact temporary non-cone preparation phase before pruning inert blob
payloads. From the admitted selective profile, write a sorted, duplicate-free
`.git/info/sparse-checkout`: each exact selected leaf is the root-anchored line
`/<exact-path>` with no trailing slash, and each selected subtree is the
root-anchored line `/<prefix>/` with one trailing slash. Reject paths containing
LF, CR, NUL, backslash, Git pattern metacharacters, an empty component, `.` or
`..`; do not quote, glob, negate, or add parent wildcard patterns. Temporarily
set `core.sparseCheckout=true`, `core.sparseCheckoutCone=false`, and
`index.sparse=false`, then run `git read-tree -mu HEAD` with hooks disabled.

Canonicalize the resulting index to a complete version-3, stage-zero index over
every HEAD leaf. Tag each selected regular leaf uppercase `H` with normal flags.
Tag every omitted leaf uppercase `S` with exactly the extended skip-worktree
policy and keep it physically absent; omitted symlink and gitlink entries are
inert `S` entries as well. Reject every flag or tag outside that exact `H`/`S`
profile and remove all index extensions. Materialize selected regular leaves
from raw self-hashed blob bytes with their committed 100644 or 100755 mode,
create only their implied parent directories, and leave no rogue empty
directory. Before Role-2 dispatch, `RUN_DIR` and `CONTROL_DIR` are absent; the
supervisor creates them only after admission. A native package's `target/` may
exist only as excluded mutable build output and may contain no tracked HEAD or
index leaf. In the terminal predecessor `A1` profile, the Role-1 output roots
are already selected committed content rather than newly authorized roots.

Finally unset the three temporary sparse configuration keys and remove all
preparation state, including `.git/info/sparse-checkout`,
`.git/info/exclude`, `.git/info/attributes`, split-index/shared-index files,
locks, and operation state. The checker disables global/system configuration
and attributes. Committed attribute declarations are admitted policy bytes,
but the exact local configuration supplies no driver and no checkout or merge
occurs after sealing; selected files are compared directly with raw blobs.
Run pre-dispatch validation only after this terminal state is reached. An
ordinary clone retaining `remote.origin`, a sparse-checkout configuration, or
an incomplete index is not an execution checkout.

## Resource envelope

The protocol-wide dispatch ceiling remains 32 producer workers, 128 GiB RAM,
512 GiB (549,755,813,888 bytes) of session disk, and 259,200 seconds. The disk
ceiling is an external host/quota or bounded-filesystem requirement; it is not
an evidence-file admission check and the checker does not claim to sandbox a
hostile child.

Independent logical evidence gates apply before whole-file reads and writes:

- every evidence file is at most 536,870,912 bytes (512 MiB);
- `candidate-stream.json`, `disposition-schema.json`,
  `checkpoint-chain.jsonl`, and `verification.json` are each at most 65,536
  bytes;
- each eight-file producer tree is at most 884,998,144 bytes (844 MiB);
- non-producer RUN metadata is at most 67,108,864 bytes (64 MiB);
- RUN and CONTROL are each at most 939,524,096 bytes (896 MiB), and their
  path-weighted logical sum is at most 1,879,048,192 bytes (1,792 MiB); and
- committed selected evidence blobs have a separate 1,073,741,824-byte
  distinct-object payload cap. The same object at two paths counts once for
  this object-store cap but twice in the logical tree totals.

The virtual candidate stream is exactly 4,194,368 bytes and
`disposition.bin` is exactly `2,621,480 + 64 * retained_count` bytes
(2.62--13.44 MB). Data-dependent JSONL files remain subject to the per-file and
aggregate gates. A cap, allocation, quota, disk, or time failure is schema-valid
`INCOMPLETE` only when both retained trees remain within every frozen checker
size, topology, and schema-custody bound, their exact completed-artifact and
terminal custody can still be established, and the failure streams, raw result,
and required fsyncs can finish durably. If any of those conditions fails, the
directories remain retained without in-transaction cleanup, but the outcome is
hard resource custody requiring operator remediation rather than a claimed
terminal record. It emits no PASS terminal seal or scientific result. Both
outcomes are infrastructure only, never weak/no-weak evidence; truncation and
sampling remain forbidden. No wall-clock estimate is an evidence claim until a
release-build pre-dispatch benchmark records it.

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
   protocol direct-child commit whose sole parent is the admitted protocol
   commit. Validate both `--pre-dispatch` and `--post-run`;
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
