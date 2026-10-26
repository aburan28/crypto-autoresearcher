# F6 second pass: prepared, not executed

The task is `TASK-20261026-2746d0`. Source preparation follows the committed
Phase A card. The runner will screen twelve total-degree staircase families
at five fixed widths, inspect a root-independent public-target 8-by-8 box,
and reduce two fixed small matrices, including a labelled known-root control.

No second-pass observation is claimed here. Execution requires root's exact
frozen protocol/source release and a successful real S3 checkpoint gate.
The source accepts `--help` without collecting data. `protocol.draft.json`
is prospective and must not be presented as a frozen preregistration.

After release, run `run.py --out runs/run-01 --seed 2026102606`, then
`analysis.py --run runs/run-01 --out reports/run-01`, and export the same run
using `export.py --run runs/run-01 --protocol protocol.json --out export.json`.
Commands are run from this track directory with the released interpreter.
