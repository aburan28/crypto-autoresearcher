# TT Runtime Boundary Decision V1

## Decision

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Source producer/verifier stage provenance status: `GO` within the exact model
below.

Full experiment status: `REVISE`.

This decision freezes the development runtime model for the source and target
staging supervisors. It does not freeze source advice, authorize an artifact or
campaign, establish index calculus, produce a locator, improve Pollard rho, or
establish an ECDLP breakthrough. The experiment still has no `execution_plan`.

## Trusted boundary

The development result trusts:

- the exact reviewed parent supervisors and static auditors bound by their
  current source and harness hashes;
- the pinned Python executable and the parent-snapshotted Python and NumPy
  runtime files;
- the macOS kernel, Seatbelt enforcement, kqueue vnode delivery, filesystem,
  loader, and hashing implementation;
- the parent process that retains approved bytes, constructs the stage,
  controls the child command and environment, observes direct child time and
  rusage, validates child output, and publishes the result and receipt;
- absence of a concurrent malicious same-UID process that can alter and restore
  approved runtime files between the parent's pre-run and post-run snapshots.

Within that model, the parent:

- retains every approved stage payload before publication;
- requires the first stage manifest to equal the retained-byte manifest;
- binds each staged path to an open device/inode/type/size identity;
- monitors the stage directory and every allowed file for setup and run-time
  vnode events;
- denies file-data reads by default and admits only literal stage paths plus
  parent-snapshotted runtime filters;
- denies child file writes, networking, and process forks;
- rehashes stage content and runtime closure after the child exits;
- treats child audit-hook read rows as diagnostic telemetry rather than
  authority;
- validates exact result, backend, runtime-receipt, claim-boundary, and resource
  schemas from parent-derived expectations.

## V22 source-specific authority

V22 adds three required controls:

1. The parent retains the exact six static-policy inputs, requires their hashes
   to equal the audit policy rows, regenerates the complete static audit, and
   requires exact structural equality with the supplied canonical report. It
   then rechecks that all six retained inputs remained unchanged.
2. Verifier stderr is bounded to 4 MiB and must be exactly one framed canonical
   runtime receipt. Leading, trailing, duplicate, whitespace-only, malformed,
   or oversized bytes fail closed.
3. Output is published before its receipt using same-directory temporary files
   and individual atomic replacement. Both files are reopened with
   `O_NOFOLLOW`, checked as regular files with exact bytes, and required to have
   distinct final device/inode identities. The receipt is the publication
   commit marker for a successful parent return.

The V21 fabricated-policy and hardlink-alias counterexamples are preserved as
negative evidence. Deterministic V22 regressions reject both, and an independent
recheck returned `GO` for these three scoped findings.

## Explicit exclusions

This model does not establish:

- protection against concurrent same-UID mutation and restoration of Python or
  NumPy runtime trees between parent snapshots;
- a cryptographic identity for code served from the macOS shared cache;
- protection against a malicious parent supervisor, trusted host, kernel,
  filesystem, loader, or hash implementation;
- pair-atomic crash recovery for the output and receipt; each replacement is
  atomic and a successful receipt is published last;
- durable authority for numeric inode values on the exFAT artifact volume;
  they are publication-time observations, while bytes and hashes remain the
  artifact identity;
- immutability of development files after the parent returns;
- provenance from a development producer receipt to a later verifier merely
  because a raw-result path was supplied.

The last two exclusions are campaign gates. An immutable campaign must use the
repository runner's clean-tree approval lock and Git-committed predecessor
transition, bind the verifier to the committed predecessor raw-result hash and
runner receipt, and verify the predecessor again after the verifier exits.

## Authorization consequence

The runtime and shared-cache limitations are accepted only for development
preflight on the pinned local backend. V22 may be used to design the campaign
artifact format and the frozen 29-mutation harness. It may not be cited as an
immutable run or used to create an approval lock until the producer output,
parent receipt, verifier input, and repository predecessor transition are one
reviewed end-to-end protocol.

## Next concrete action

Design a runner-compatible source artifact envelope that carries the supervised
child result and parent receipt into the Git-committed predecessor transition,
then prove that the verifier consumes exactly that committed envelope before
implementing the 29-mutation execution plan.
