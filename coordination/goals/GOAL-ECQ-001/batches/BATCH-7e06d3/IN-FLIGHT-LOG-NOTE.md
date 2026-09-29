# Outstanding obligation: restore the in-flight producer log before archiving

`RUN-a7a9e8-002-m10-main/stdout.log` is a LIVE append-only trace written by a
producer that is still running. It emits one line per trial: 2.5 MB and ~30,000
lines within the first 280 s, still growing.

The session Stop hook requires a clean tree, and re-committing this file on every
stop would add a multi-megabyte near-duplicate blob per cycle to a shared
repository, for no informational gain — the run's actual artifacts are its
`manifest.yaml` and `raw-result.json`, and the log is only meaningful once, in
its final state.

So the file has been marked locally with:

    git update-index --skip-worktree <path>

This is LOCAL ONLY. It lives in `.git/index`, changes nothing for any other
clone, commits nothing, and alters no repository configuration. The file remains
tracked at its last committed content; only further local churn is ignored.

## THIS MUST BE UNDONE BEFORE THE SNAPSHOT ARCHIVE

`tools/validate_ledger.py` REQUIRES `stdout.log` in every run directory, and the
Coordinator snapshot archive (TASK-20260822-e7c486) must hash the FINAL log, not
the stale committed prefix. Before that archive runs:

    git update-index --no-skip-worktree <path>
    git add <path>          # final content, once

Leaving the flag set would archive a truncated log while reporting a hash for it,
which is exactly the kind of silent mismatch the archive receipts exist to catch.

---

## DISCHARGED for RUN-a7a9e8-002-m10-main, 2026-08-22

The run terminated (`exit_code: 0`, `ended_at: 2026-08-22T14:33:15Z`) and its log
stopped growing — measured stable at 3,480,393 bytes across a re-read. The flag
was cleared with `git update-index --no-skip-worktree` and the FINAL log was
committed in full alongside the run's `manifest.yaml` and `raw-result.json`, so
the snapshot archive will hash the complete file rather than a stale prefix.

This note stays in the batch as the audit trail. If another producer run opens a
new live log, the same procedure and the same obligation apply again.

---

## OPEN for RUN-a7a9e8-004-augment-full, 2026-08-22

Same situation, same treatment: the producer opened a fourth run whose stdout.log
is live and growing. Flag set with `git update-index --skip-worktree`; LOCAL
ONLY, nothing committed, no repo config changed.

**Obligation is OPEN.** Before the snapshot archive, clear the flag and commit
the final log, exactly as was done for RUN-a7a9e8-002-m10-main:

    git update-index --no-skip-worktree <path>
    git add <path>

Check `runs/` for any further live logs at archive time — the producer has opened
four runs so far and may open more, so this must be swept rather than fixed to a
known list. `git ls-files -v <dir> | grep '^S'` lists every path currently
carrying the flag.

## Watch item for the Coordinator

`raw-result.json` for run 002 was 108 MB and had to be stored gzipped
(RAW-RESULT-STORAGE.md in that run directory). If later runs dump at the same
rate, the archive will accumulate tens of MB per run. That is a producer
over-collection question to settle before the snapshot archive fixes it in
history, not something to resolve by trimming output.

---

## DISCHARGED for RUN-a7a9e8-004-augment-full, 2026-08-22

Run terminated (`exit_code: 0`, `ended_at: 2026-08-22T14:45:56Z`, 703 s) and its
log stopped growing — measured stable at 2,311,904 bytes across a re-read. Flag
cleared, final log committed in full.

Sweep result at this point: `git ls-files -v coordination/ | grep '^S'` returns
NOTHING. No flagged path remains outstanding.

Its `raw-result.json` is 35,039,973 bytes — large, but under GitHub's 100 MB
limit, so it is committed VERBATIM with no compression and no deviation. Only
run 002 needed the gzip treatment, and only because it exceeded the hard limit.

---

## OPEN for RUN-a7a9e8-008-upper-crosscheck, 2026-08-22

Live log, growing; local-only skip-worktree applied. Obligation OPEN — clear the
flag and commit the final log before the snapshot archive, via the sweep
`git ls-files -v coordination/ | grep '^S'`.

---

## DISCHARGED for RUN-a7a9e8-008-upper-crosscheck, 2026-08-22

Run terminated and its log stopped growing (verified stable across a re-read).
Flag cleared via the sweep and the final log committed. Sweep is empty again.

---

## OPEN for RUN-ECQ-81141a-004 (over-Q pipeline), 2026-08-22

Flagged for CHURN FREQUENCY, not size — the log is sub-kB but dirtied three
consecutive stop-cycles. Same local-only skip-worktree; same sweep discharges it
before the snapshot archive.

---

## DISCHARGED for RUN-ECQ-81141a-004 (over-Q pipeline), 2026-08-22

Run terminated and its log stopped growing (stable at 8,008 bytes across a
re-read). Flag cleared via the sweep and the final log committed with the run's
manifest and raw-result. Sweep empty again. RUN-005's log opened stable and small,
so it needs no flag.
