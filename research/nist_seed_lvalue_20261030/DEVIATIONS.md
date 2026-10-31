# Deviations from PROTOCOL.md

- **D1 (2026-10-30).** The first launch was killed by the agent harness's
  600 s background-task limit while the estimator control was running
  (after the per-curve pass and the Monte Carlo nulls). It wrote no
  `lvalues.json` or `controls.json`. Its logs are kept in
  `runs/attempt1-killed/`; they contain no study statistic. The identical
  command was relaunched with a longer limit. Script and inputs are unchanged.
