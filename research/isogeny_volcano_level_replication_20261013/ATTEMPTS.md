# Attempt log

This file existed before launch. Append-only run facts are recorded after the
frozen protocol commit. No solve had been launched when this initial entry was
written.

- 2026-10-13: audited the immutable historical launchers. They overwrite fixed
  paths and do not propagate thread failures, so they were not executed.
- 2026-10-13: selected a fresh output root, disjoint seed namespaces, atomic
  per-job publication, and exact fail-closed validation. Resume was removed
  after pre-launch review; any later attempt must use a new empty output root.
