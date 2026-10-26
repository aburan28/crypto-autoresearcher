# Actual code-only image build

The committed source snapshot `fe01ccd832832488c58abeef17548b0a8db6035f`
was built on 2026-10-26 using the digest-pinned Debian base recorded in
`image-observation.json`. The container's production executable passed all
783 fixed correctness checks with its network disabled and root filesystem
read-only. No confirmation instances or scientific comparison were run.

The executable SHA-256 is
`0eb981311b4dd0de7da9faf51178d1d97759d48a54e4c143f2f9d44ef31d8c48`.
It differs from the earlier development-host build; the actual container
compiler and package versions are retained in `build-info.json`.

The local Docker image ID is a configuration digest, not a published registry
manifest digest. No registry publication or isolated worker readiness is
asserted. The prospective protocol remains a draft. The next runtime binding
must use the actual published private-registry digest and observed executable
hash, followed by protocol freeze, committed input lock, fresh cohort and
final admission through the source-capable isolated route.

`manifest.json` records exact build arguments and hashes. The failed first
attempt is preserved in `build.log`; it failed before compilation because
buildx tried to write to the read-only home directory. The successful attempt
used writable workspace buildx state while preserving configured proxy and
registry authentication. Its complete output is `build-attempt-02.log`.
The required base argument was supplied; the retained Docker warning about
its empty default does not mean an unpinned base was used.

The source archive is independently checked with the unchanged repository
`GitRepositoryVerifier.verify_archive`: exact commit, first parent, 277 changed
paths, hashes and task/experiment IDs. That verifies custody, not execution
or scientific claims. See the source snapshot receipt under
`coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-15eb64/archives/TASK-20261026-fe6662/`.

The local resume note is complete. Automatic approval review rejected the
attempted S3 checkpoint upload before it executed because authorization for
the destination bucket and private source payload was unestablished. It was
not retried. No checkpoint upload acknowledgment or S3 pointer is fabricated.
Both the isolated execution route and checkpoint authorization remain explicit
infrastructure gaps, with no implication about algorithm performance.
