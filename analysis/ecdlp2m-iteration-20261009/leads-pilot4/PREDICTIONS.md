# Predictions recorded before the runs that test them

Written 2026-10-18T03:52Z, before the m=6 instances exist and before any m=6 closure ran.

## P-M6 (m=6, n=9, k=3, chained S_3, same curve, basis and target list as pilot #3's m5-n9k3 cell)

Data seen when writing this:
- pilot #3: L1 refutes 0/10 and L2 refutes 5/5 at m=5, n=9, k=3;
- this pilot's u-degree caps, for which the smallest cap that refutes rises with m:
  2 (m=3), 2 (m=4, n=7), 3 (m=4, n=9), and 4 = no cap (m=5, n=9, k=3: L2u3 refutes 0/5);
- the target-independent solution counts (zfree_fast.py) against the closure's column count.

Prediction: the locality-2 degree-4 closure (L2, 105,040 columns) refutes **at most 1 of 5**
UNSAT instances at m=6, n=9, k=3. Sample status: out of sample (no m=6 data exists).

Mechanism behind it (two readings that agree here):
- the u-degree requirement reaches the degree cap at m=5, so m=6 would need degree 5;
- the z-free subsystem has about 2.4e5 solutions (estimate 0.9 |V|^6) against 1.05e5 columns,
  and at m >= 4 no refutation in any pilot so far used fewer columns than z-free solutions
  (at m = 3 this fails: pilot #1 refuted 8/8 at n=15, k=5 with 31,931 columns against 32,032
  z-free solutions; corrected at 03:5xZ before any m=6 run, see P-SEMBIN).

Falsified if L2 refutes >= 3 of 5 UNSAT instances. A refutation of any SAT instance voids the run.
A failure does not show that full W_4 fails (L2 is a subspace of W_4; full W_4 is out of reach here).

## P-SEMBIN (pointer only; EXP-SEMBIN-d9767f is running and its UNSAT outcomes have NOT been read)

Exact z-free counts (zfree_fast.py) put pilot #1's n=13, k=5 cell at log2(cols4 / zfree) = -0.43 and
the n=15, k=5 cell at 0.00. Pilot #1 recorded 8/8 W_4 refutations at n=15, k=5, and an unrecorded single
probe refuted at n=13. So "cols >= zfree solutions" is NOT treated as a necessary condition at m=3; it
is a reading to test, not a prediction, and EXP-SEMBIN-d9767f's m=3 cells are not used to tune it.
