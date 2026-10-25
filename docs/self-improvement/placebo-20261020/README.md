# Placebo calibration, 2026-10-20

Raw output behind the calibration table in `docs/self-improvement-loop.md`.
These measure the harness, not ECDLP.

- Base commit and interpreter: `base_commit.txt` (ledger state the run read).
- Commands, at the commit that adds this directory:

  ```sh
  python3 tools/self_improve.py --today 2026-10-20 placebo --target propose-ideas \
      --from 2026-07-01 --to 2026-09-30 --step-days 3 > propose-ideas.json
  python3 tools/self_improve.py --today 2026-10-20 placebo --target design-experiment \
      --from 2026-07-01 --to 2026-09-30 --step-days 3 > design-experiment.json
  python3 tools/self_improve.py --today 2026-10-20 plan --json > plan.json
  ```

- Result: propose-ideas has 17 measurable dates of 31, with 2 false positives
  (`regressed` on 2026-09-26 and 2026-09-29, one episode). design-experiment has
  0 measurable dates of 31. Adjacent dates share most items, so they are not
  independent trials.
- Absent: the two development rows of the table (item bootstrap, and cluster
  bootstrap without the 4-cluster minimum) ran on uncommitted code; their raw
  output was not kept.
