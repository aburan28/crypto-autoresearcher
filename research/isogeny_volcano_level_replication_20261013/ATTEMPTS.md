# Attempt log

This file existed before launch. Append-only run facts are recorded after the
frozen protocol commit. No solve had been launched when this initial entry was
written.

- 2026-10-13: audited the immutable historical launchers. They overwrite fixed
  paths and do not propagate thread failures, so they were not executed.
- 2026-10-13: selected a fresh output root, disjoint seed namespaces, atomic
  per-job publication, and exact fail-closed validation. Resume was removed
  after pre-launch review; any later attempt must use a new empty output root.
- 2026-10-13: launched attempt 1 from clean revision
  `f10e03e3d8b0e584d23202deb391c5e7b06026cf` at
  `2026-10-13T06:10:25.597160+00:00`, using four workers pinned to CPUs
  0--3 and output root
  `/tmp/isogeny-volcano-level-replication-20261013-run1`.
- 2026-10-13: attempt 1 completed at
  `2026-10-13T06:53:06.059611+00:00` after 2,560.46 seconds. All 392/392
  jobs and 160,000/160,000 planted solves completed; the runner reported no
  error. The sealed analyzer accepted the exact file sets, session metadata,
  shuffled plan, job receipts, source and binary hashes, counter schema, and
  every `ok=1` certificate.
- 2026-10-13: archived the complete attempt as `run1.tar.zst`, SHA-256
  `37d8abf2d12d51eed53ef013f05bbf8a17028ee51c60355cf1e2f2994fa63eb7`.
  A clean-room extraction compared byte-for-byte equal to the live run tree.
  Reanalysis of a relocated extraction intentionally failed the receipt-path
  gate because absolute output paths are part of the frozen manifest; replay
  therefore must use the recorded output root as documented in `ARCHIVE.md`.
