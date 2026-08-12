# Implementation — Autolab task/result migration

`tools/migrate_autolab_archive.py` performs deterministic enumeration, atomic
copy, source/destination SHA-256 comparison, task cataloging, and harness receipt
generation. It does not execute any migrated benchmark or interpret historical
results.

The source Git repository is dirty. Its commit identifies the tracked base only;
the per-file manifest is the byte-level provenance record for tracked and
untracked files alike.

The first enumeration omitted three symlink-to-directory fixture aliases because
`os.walk` exposes them through `dirnames`. `CORR-ALMIG-001` preserves that
observation. The corrected enumerator binds those aliases without traversing
their targets and produced the canonical successor run
`RUN-ALMIG-001-import-r1`.
