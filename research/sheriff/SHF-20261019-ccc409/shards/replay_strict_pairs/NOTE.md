# Incomplete for EV-MONO-d90e9c (found in review of PR 2425)

This directory was written with basename-only paths, so for EV-MONO-d90e9c the p211 files
(`preregistration.json`, `timings.json`) overwrote the p101 ones. The retained MONO files here are
p211 only; the p101 regenerated files from that first strict run were not retained and the scratch
worktree was removed, so that first comparison is **partial** for p101 (its diffs are listed in
`../replay_strict_discovery.jsonl`, not retained as files). Left as written. The five other records
have unique basenames and are complete. A fresh MONO re-run with collision-free full paths and its own
receipt is in `../replay_strict_pairs_v2/` and `../replay_strict_out_mono_v2.jsonl`
(re-check with `scripts/verify_pairs.py`).
