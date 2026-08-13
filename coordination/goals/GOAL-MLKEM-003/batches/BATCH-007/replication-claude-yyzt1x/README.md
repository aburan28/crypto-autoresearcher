# BATCH-007 — independent replication (branch claude/harness-findings-repo-yyzt1x)

These are the artifacts of the SECOND, independent execution of GOAL-MLKEM-003
BATCH-007. They are **not** the authoritative batch record.

`origin/main` carries the authoritative execution at the canonical paths
(`../tasks/…`, `../archives/…`), with `EV-MLKEM-017` and `DEC-20260802-15cadd`.
Both executions ran from the same launch decision `DEC-20260802-002` and used
the same task identifiers, because neither session knew the other existed. The
duplication and its resolution are recorded in `CORR-20260802-d8ba0e`.

They are preserved here, at a distinct path, for one reason: the canonical paths
now hold the other execution's bytes, so an evidence record citing them would be
citing someone else's artifacts. `EV-MLKEM-5a8ec5` — this branch's replication
record — points at the files in this directory, which are the ones its
observations were actually derived from.

## What replicated

- **Q1** returned `confirmed_in_current_source` in both executions, against the
  same vendored artifact (`sha256 083b1422…b8005`), with the same declared
  limitation: ePrint-hosted PDF bytes were never retrieved (HTTP 403,
  Cloudflare challenge, path-class-wide), so the HAL-object/ePrint-revision-3
  identity is inferred from metadata rather than byte-proven.
- Both executions' **red teams independently derived** the counting-resolution
  identity `log2(4000 · 241³) = 35.7045` against `KN-FIND-012`'s recorded
  Pwrong floor of `−35.70`. Two adversarial passes converging on it separately
  is materially stronger than either derivation alone.

## What diverged

Knowledge promotion, and this branch was wrong. This execution promoted the
identity as `KN-FIND-031`; the authoritative execution declined, because the
result supersedes coverage statistics carried by `KN-FIND-012` and
`KN-FIND-014` and is therefore a contradiction between validated evidence
records, which AGENTS.md rule 12 gates behind an independent
`review-breakthrough` review at `max` effort. `KN-FIND-031` is withdrawn.

## Path mapping

Files under `inputs-MLKEM-DUAL-SOURCES-20260802/` were produced at
`inputs/MLKEM-DUAL-SOURCES-20260802/` and are copied here because that
directory's canonical files now hold the other execution's content. The
`extracts/` subdirectory there was unique to this execution and remains at its
original path.
