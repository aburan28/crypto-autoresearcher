# Candidate relation-matrix solve path

`solve.py` is a candidate for the later complete-solve stage and runs with
`sage -python`. It consumes a prepared curve input, exact triple collector
output, independent ordered-count output, and public generator/Q coordinates.
It receives no target scalar or seed reveal. It first replays the existing
independent relation/count/rank verifier, constructs the modular equations
for useful triples with the known-generator orbit eliminated and Q merged
when Q is in the base, and computes rank over `GF(r)` with Sage/FLINT.

When rank reaches every unknown column, it solves for the factor-base logs
and Q scalar, checks every matrix equation, and verifies all base logs and
`[scalar]G=Q` with Sage point arithmetic. An incomplete rank returns
`censored_insufficient_rank` with no scalar. `check.py` separately replays
the original relation verifier and Sage point/log equations for every base
orbit, target, and reported triple. Its verification is a software control;
formal independent review of full-width scientific receipts remains required.

The fixed public 19-point controls under `controls/attempt-1/` exercise both
Q-in-base (two unknown columns) and Q-outside-base (three unknown columns),
plus a one-target rank-censored input and a changed-scalar rejection. These
are implementation controls on an exhaustively enumerable group. They do
not measure P29/P37 full solve feasibility, complete ECDLP cost, or matched
rho.

`controls/attempt-2/` replays those small controls with source hashes and
captured solver/checker logs. `controls/attempt-3/` runs a bounded P37
eight-target public input through the existing 8 GiB graph wrapper, then
through this candidate solver and checker. It exercises the 1,601-column
layout and records a valid rank-censored outcome; it cannot establish
full-quota rank or complete solve feasibility. The consolidated report,
diagram and PDF in this directory cover both later attempts.
