G4 prospective schema/accounting preparation, 2026-10-17

Scope: EXP-ECDLP-ad27ad / RUN-ECDLP-a5281a / trial full-grid.
This initial preparation was written while the scientific run was live.
Only the frozen plan, specification and implementation were read. No live
run data was interpreted, no terminal outcome was assumed, and no original
artifact hashes, schema envelope or registry fragment were finalized.

The delegated task waits for the primary's terminal published archive SHA.
At that point the exact command is:
  python3 coordination/design/SNFS-RUN-SCHEMA-G4-20261017/prepare.py --archive-ref <PRIMARY_TERMINAL_ARCHIVE_SHA>
The script first requires the archived receipt to equal the terminal original
and requires producer/checker rc0 plus invalid_output. A different status is
returned as a named preparation blocker, never silently changed. The generator
makes a one-entry registry fragment only; primary owns the shared registry.
No trial, claim, approval, git mutation or scientific transition is performed.

Final verification, only after terminal preparation:
  python3 coordination/design/SNFS-RUN-SCHEMA-G4-20261017/verify.py
It checks the one fragment and immutable source bundle, source/input hashes at
actual launch commit 82cc1338b982c401002f77dc4c19cb2c10a04989, exact argv/trial
identity, retained supervisor outcome, and four refusal controls. Producer
end-of-run HEAD is kept separately; unrelated publication during execution
must not be confused with the execution source revision.

Static implementation limitations carried by the prospective envelope:
- Controls have the same nominal m, but actual density/cardinality matching is
  not established and is not asserted. Rotation membership unions cyclic
  rotations; hash uses threshold 2^(64-m); size uses p>>m. Literal frozen
  control descriptions remain historical protocol text with this caveat.
- random_point samples finite affine points with y!=0 and excludes O. Exact
  enumeration includes y=0 but excludes O. Derived finite sums with y=0 still
  use the x-coordinate membership rule; O is excluded by explicit checks.
These are static scope/accounting notes, not interpretation of scientific
results or permission to change the frozen protocol after observing them.

Actual preparing runtime: Codex; system-reported model family GPT-6; exact
serving identifier unavailable. No unverified anthropic binding was claimed
as executed and no probe or substitution approval was fabricated.

Terminal preparation completed against primary archive
ba753d2521c9fedacf9f35148f60da5da29cf7e1. See terminal-summary.json, checks.json
and verification.json. Correction CORR-20261017-447c0e. The initial
preparation-state.json above remains a historical prospective-stage receipt.
All original outcomes are retained; this packet is not yet published by its
preparer and the shared registry remains primary-owned.
