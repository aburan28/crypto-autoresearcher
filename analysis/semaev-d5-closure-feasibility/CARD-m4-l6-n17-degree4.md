# Frozen card (proposed, not approved): degree-4 closure of the m=4, l=6, n=17 instance

Instance: `raw-20261026/unsat_m4_n17_l6.jsonl` (draw 57, seed 20261016, exact solution count 0). Numbers: `m4-l6-search-20261026.md` (derived, extrapolated 2.5x past the largest completed cell).
- Question: does the degree-4 closure refute it (d_F = 4 at m*l = 24 for m = 4)? A "not refuted" result is d_F >= 5 for this instance and, as in the C19 case, would not by itself show the degree is unbounded.
- Command, from the crypto checkout at commit 981f80710b7efd7513ff6f3f70296a1148688b41 (`raw-20261026/crypto-commit.txt`): `RAYON_NUM_THREADS=4 hky_par ladder unsat_m4_n17_l6.jsonl --m 4 --cmax 4` (the stock `ladder` subcommand; no scratch tool is needed to run it).
- Host (planning, unvalidated): 32 GB RAM, 4+ cores, no address-space cap. Memory 13-21 GB expected, time 1-3 h by extrapolation.
- Done here: degree <= 3 not refuted (dim 3,299 of 32,568); degree 4 aborted at the 14.5 GB cap after 1,973 s.
- Not covered: degree 5 (5,038,954 columns at N = 58, out of reach), certificate production (`hky_par` produces none; a "no" is a measurement).
