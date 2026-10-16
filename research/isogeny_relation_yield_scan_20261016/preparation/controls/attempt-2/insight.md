# Censored all-point dual replay — 2026-10-16

The second local implementation-control attempt ran `transport_two_edges.py` under Sage and was manually interrupted after several minutes during the all-point dual replay. Its `result.json` is empty and `stderr.log` retains the interrupt traceback. The exact duration and number of completed dual checks were not instrumented. This is a censored implementation attempt, with no inference about isogeny correctness or relation yield.

The next attempt computes every forward image once, checks the dual on a fixed sample of 21 points per edge, and retains stage progress plus a ten-minute watchdog. Its source and outcome are preserved separately in `../attempt-3/`.
