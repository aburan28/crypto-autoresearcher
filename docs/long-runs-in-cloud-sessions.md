# Long experiment runs in Claude Code cloud sessions

Observed 2026-10-15 to 2026-10-19 (EXP-ECDLP-f49f75, -502ae2, -20a588, -8c41d7): **background
processes do not survive idle gaps between turns of a cloud session.** Three times, when the
user returned after a gap, `/proc/uptime` was under a minute and every run process was gone while
the disk (repository, run directories, installed packages) was intact. Separately, a single
background command is stopped after 2 hours (`timeout` max 7 200 000 ms), which killed two runs
that were still going.

What that means for a run:

- A run only progresses while the session is actively working (tool calls in flight). Ending a turn
  with a run in the background risks losing it; `setsid nohup` did not help against the recycle.
- Rows written at the **end of a cell** are lost with the cell. A launcher that appends after every
  instance and skips instances already in its output file loses at most one instance per recycle.
- Do not write `finished_at` or a manifest for a run you did not see finish. Record the loss
  (`termination.txt`, last write time, what completed) and resume the unexecuted cells under a
  protocol amendment whose `filed` field is the commit time, never a hand-typed time.
- A chained runner that waits on another run's `finished_at` waits forever if that run was killed
  without writing it; write the marker deliberately (with a note) or rerun.

Practices that worked here:

1. Freeze the protocol and commit it before the first data (`filed_before_affected_data`).
2. Resume with an amendment that changes only the cell list and output path, same launcher commit,
   seeds, arms, timeout and stopping rule (see `experiments/EXP-ECDLP-8c41d7/amendments/`).
3. Never run two timed experiments on the same cores; chain them.
4. Keep CPU-light work (tests, analysis, reports, theory notes) for the time a run is going.

For future experiments use `tools/resumable_grid.py`: it appends each finished instance (flush +
fsync), skips instances already in the output file on restart, drops a half-written last line, and
rebuilds the stopping rule from the stored rows, so a recycle loses at most the instances in flight
(`tools/test_resumable_grid.py`). It reads the same plan format and per-instance seeds as
`block_order_grid.py`. The four EXP-ECDLP launchers above are frozen and still write per cell, as their
protocols were committed that way.
