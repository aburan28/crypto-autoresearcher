---
name: pr
description: "Prepare, update or review a scoped pull request, inspect CI/review status, synchronize branches and perform an explicitly authorized merge in crypto-autoresearcher. Use for code delivery and repository integrity work. Never add PR creation as an automatic phase of run."
---

# Repository delivery

Read `AGENTS.md` branch/archival rules and inspect the exact working branch, target base, dirty scope and remote PR before changing anything. Consult `tools/check_merge_hygiene.py`, `check_run_immutability.py`, `producer_landing.py` and `sync_open_branches.py` only for their declared scope.

1. Preserve unrelated user changes and immutable records. Fetch/inspect current base for a delivery task; merge upstream into branches carrying pushed evidence, never rebase them.
2. Stage only the scoped implementation/docs/tests. Run required checks and meaningful affected tests. Do not repair unrelated ledger errors or bypass a failed admission/integrity gate.
3. Separate software validation from research evidence and independent scientific review. A green CI run or merged PR does not promote a hypothesis.
4. Write the PR for the final diff: concrete behavior, validation, missing checks and limitations. Use structured arguments or a body file to preserve multiline text.
5. Enable auto-merge as part of opening or refreshing the PR: `gh pr merge <n> --auto --merge`. This is the default for every PR whose base is `main`; never leave a ready PR without it. GitHub offers auto-merge only when the base is the repository's default branch — a PR stacked on a feature branch is retargeted to `main` and auto-merge enabled once its parent lands, or merged bottom-up by hand.
6. Inspect review findings, checks and head SHA before an authorized merge. A pending check is not a passed check; do not silently merge a different revision. If only PR creation was requested, enable auto-merge and then stop after making the result reviewable.
7. Return the PR link, exact delivered scope and current observed checks/review/merge state, including whether auto-merge is enabled. Do not send unrelated messages or make repository access changes.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
