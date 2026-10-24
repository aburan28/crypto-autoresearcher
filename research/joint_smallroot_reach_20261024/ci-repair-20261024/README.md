# CI compatibility repair for audit PR #2547

Archival task: TASK-20261024-e7a060. This is software validation, not a
scientific experiment or an ECDLP performance measurement.

The hosted artifact job at run 40127333405 failed on an abbreviated blob ID
(`6ee9ea2a`) outside its blobless sparse checkout. Its `git cat-file -s` call
cannot resolve an abbreviated name for a blob the promisor has not fetched.
The full object ID enables ordinary Git lazy fetching. The checker now requests
`git diff --raw --no-abbrev`; artifact thresholds and enforcement are unchanged.

The regression creates an actual local file-transport filtered clone without
checking out its blobs. Before the fix it exits 2 with `Not a valid object name`;
after the fix it fetches the missing blob and exits 1 for the deliberately
oversized data file. A small-file control is not reported as an offender. This
tests policy enforcement, not just the formatting of a Git argument.

Hosted CI-tier run 40127333431 also found the artifact workflow outside the
repository's existing draft-tier contract. The repository's own
`draft_tier_gate.py --apply` changes that workflow only: add `ready_for_review`
and combine the nondraft condition with its existing PR-event condition. It
still runs on this ready PR. No check is disabled or moved into the fast-tier
exception list, and no large-file exemption is applied.

Recorded local checks in [checks.json](checks.json) and adjacent stdout/stderr:

- All 10 artifact tests pass, including the new filtered-clone regression.
- The draft-tier validator reports zero uncovered PR workflows.
- Artifact policy check reports no data files committed in the audit diff.
- Artifact workflow hydration checks pass.

The unrelated pre-existing `.tmp/` gitlink cleanup warning was not changed.
Current-head hosted checks and review remain required before merge. The user
has now explicitly authorized merging; this does not waive those gates.
