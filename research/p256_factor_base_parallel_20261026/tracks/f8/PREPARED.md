# F8 second pass: prepared, not executed

The task is `TASK-20261026-7324bb`. Source preparation follows the committed
Phase A card. The runner will create eight public deterministic
representatives without supplied scalar labels, enumerate their signed orbits,
solve eight fixed unplanted target queries and a zero-target query completely,
and check exact quotient ranks and explicit detector/refusal controls.

No second-pass observation is claimed here. Execution requires root's exact
frozen protocol/source release and a successful real S3 checkpoint gate.
`protocol.draft.json` is prospective and is not a frozen preregistration.

After release, run `run.py --out runs/run-01 --seed 2026102608`, then
`analysis.py --run runs/run-01 --out reports/run-01`, and export the same run
using `export.py --run runs/run-01 --protocol protocol.json --out export.json`.
Commands are run from this track directory with the released interpreter.
F6 and F8 run sequentially under their shared one-process/2-GiB worker limit.
