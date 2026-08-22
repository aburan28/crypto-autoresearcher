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
