# Cross-check: crypto #2214 `hky_par` closure vs #2410 `lfdclose2`, and an m=4, l=5 cell

Write-once record, 2026-10-20. Observations first, derivations labelled, limits last. Raw outputs, hashes and the scratch diff are in `raw-20261020/`. The earlier record `report.md` and `CARD-d5-c19.md` are unchanged.

## What was run
- Engine under test: `closure_par` / `refute` from `examples/hky_par.rs` of aburan28/crypto at commit `981f80710b7efd7513ff6f3f70296a1148688b41` (the head of #2214's branch), release build, 4 threads. The build was allowed by the user in this session.
- **Scratch wrapper.** `hky_par` builds its own descent with the curve coefficient b fixed to 1, so it cannot generate #2410's C19a/b. A scratch copy `hky_sys.rs` adds one subcommand that reads an `lfdclose2` `.sys` file (equations from `mksys3.py`) and calls the same `refute`. The diff is `raw-20261020/hky_sys-vs-hky_par.diff` (26 lines, an added match arm only). It was not committed to crypto.
- This tests the two **closure engines on identical equations**. It does not test that the two descents (equation builders) agree.

## Observations (measured)
Degree-4 closure, `--cmax 4`, 4 threads:
| instance | N | columns | hky_par result | hky_par wall | #2410 record (`certificates.txt`) | #2410 closure wall |
|---|--:|--:|---|--:|---|--:|
| C17a (control, refutes) | 35 | 59,536 | closure 59,536/59,536 at degree 4, d_F = 4 | 70 s | `W4_one 1` (instances_t3.json), ncols 59,536 | 281 s |
| C19a | 40 | 102,091 | closure 92,838 of 102,091 at degree 4, not refuted, d_F >= 5 | 157 s | W4 dim 92,838, `W4_one 0`, certificate VALID | 3,964 s |
| C19b | 40 | 102,091 | closure 95,274 of 102,091 at degree 4, not refuted, d_F >= 5 | 189 s | W4 dim 95,274, `W4_one 0`, certificate VALID | 3,368 s |
- The two engines return the same closure dimensions on C19a and C19b, and the same verdict on all three instances. No disagreement arose, so `cert_check.py` was not needed.

Degree-5 closure on three satisfiable (saturating) m=3 systems, both engines, same files:
| N | columns | hky_par wall / peak RSS | lfdclose2 wall / peak RSS |
|--:|--:|--:|--:|
| 24 | 55,455 | 204.7 s / 1.10 GB | 412.1 s / 1.55 GB |
| 26 | 83,682 | 287.4 s / 1.58 GB | 1,081.8 s / 2.88 GB |
| 28 | 122,438 | 609.4 s / 2.43 GB | 2,825.6 s / 5.46 GB |
(`hky_par` runs cover degrees 2 to 5 in sequence, `lfdclose2` degree 5 only; `lfdclose2` is single-threaded.)

m=4, l=5 cell (new): `hky_par newcells --cells 4:13:5 --seed 20261016 --keep 1 --cmax 4`. The m=4 variable count in crypto's cells is N = 2n + 4l, so n=13, l=5 gives N=46 (m*l = 20). One unsatisfiable draw (draw index 18) was kept. It reached closure 179,447 of 179,447 at degree 4 in 11 rounds, so d_F = 4. Wall 613 s, peak RSS 3.26 GB.

## Derived (extrapolation, not measured; 6.2x past the largest degree-5 point)
- C19, N=40, D=5: 760,099 columns. For `hky_par`, from the N=28 point (609 s): wall on 4 cores is 6.3 h / 14.3 h / 40.5 h for scaling exponents 1.98 / 2.43 / 3.0 (53 CPU-hours at 2.43). The 3-point fit exponent (1.37) and the RSS fit (exponent 0.99) are not used: a row-triangular store cannot scale linearly in memory.
- Peak RSS: at least 33 GB (rank 0.92 x ncols, triangular rows, no overhead) and about 93 GB if peak memory scales quadratically from the N=28 point. The rank ratio at D=5 is unknown.
- Host planning figure for C19 at D=5 with `hky_par`: 128 GB RAM, >= 16 cores. Unvalidated planning choice, not a bound. The 256 GB figure in `CARD-d5-c19.md` is for `lfdclose2` and is unchanged by this record.

## Limits
- One m=4, l=5 draw, one degree-5 point per N, one run per instance, no variance estimate.
- Identical closure dimensions on two instances do not prove the engines agree everywhere. Dimension equality is a strong check on these two.
- The descent-agreement check, a degree-5 run on C19, and an l=6 (m*l = 24) m=4 cell were not done.
- The calibration systems are satisfiable with rank ratio near 1. C19a/b are not.
