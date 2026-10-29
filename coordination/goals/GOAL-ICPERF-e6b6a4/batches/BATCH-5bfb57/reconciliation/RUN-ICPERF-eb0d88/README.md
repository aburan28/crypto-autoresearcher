# Prepared custody package for RUN-ICPERF-eb0d88

This directory is a **prepared, unarchived** custody candidate. It has no scientific or research-state effect. The frozen queue, failed release, run, and trial plan retain their original bytes.

`custody.json` records SHA-256, size, and source Git blob for all 25 existing files in the run directory and the failed executor release. `source-bundle.tar.gz` contains exact copies of those 26 files in deterministic USTAR entries. The manifest also binds the 15 members of the diagnostic raw archive, the frozen queue, claim, plan, and published run report files. It explicitly records the absence of the two top-level supervisor outputs, `manifest.yaml` and `raw-result.json`.

Replay from the repository root:

```sh
python3 coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/reconciliation/RUN-ICPERF-eb0d88/verify_custody.py
```

The replay compares each bundle member with the working file and the recorded source commit, recomputes all raw archive member hashes against the diagnostic receipt, checks historical anchors, and confirms the two required outputs are absent. It preserves the distinction between the supervisor's `invalid_output` and the narrower raw checker's `integrity_pass`.

A fresh Coordinator decision, additive terminal queue disposition, task handoffs, content-bound snapshot, and independent review are still required before this candidate can support a ledger evidence decision. The three capped positive solver calls remain censored observations; this package does not rank factor bases or measure a complete index-calculus pipeline.
