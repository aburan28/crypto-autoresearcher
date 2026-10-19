# Frozen card: degree-5 closure of C19a/b (host requirement)

Status: **proposed, not approved, not run.** Only the Coordinator approves. Written 2026-10-19.
Source of every number: `calib.json` (measured) and `estimate-output.txt` (derived from it).

## Task
Decide whether 1 ∈ W_5 for C19a and C19b (`../semaev-m2-last-fall-degree/results/instances_t3.json`; m=3, ℓ=7, N = n+3k = 40).
A "no" is only accepted with a closure certificate checked by `../semaev-m2-last-fall-degree/verify/cert_check.py` (Prop. 1.5, D=5).

## Command (engine = #2410's `lfdclose2.c`, unmodified)
```
gcc -O3 -march=native lfdclose2.c -lm4ri -lm -o lfdclose2
./lfdclose2 5 1 <chunk_rows> <cert_path> < C19a.sys      # then cert_check.py with --t3, D=5
```

## Host requirement (derived and CONDITIONAL; extrapolation is 6.2x past the largest measured point)
Dense storage by phase of `lfdclose2.c` (`estimate.py phases_gb`; rho = final rank / ncols, unknown until run;
the generated-row count 218,918 is exact for C19a, from `mksys3.py` + the degree-5 Macaulay count):
| phase | allocation (code) | dense GB at rho = 0.5 / 0.92 / 1.0 |
|---|---|---|
| P1 initial matrix | `macaulay(D)`: rows_gen x ncols, rows_gen = 218,918 | 20.8 / 20.8 / 20.8 (not the 72 GB square) |
| P2 chunk rebuild | old A (>= rank rows) and new B (rank + chunk rows) both live, plus Lw (nnew rows, unbounded here) | 78 / 139 / 150, plus Lw |
| P3 certificate | A (rank rows) + R = ncols * ceil(nq/64) * 8 B, nq = ncols - rank; B is A by then, so not concurrent with two matrices | 72 / 72 / 72 |
- Other columns: 760,099 columns; ncols^2/8 = 72.2 GB is a unit, not an allocation.
- rho = 0.92 is the engine-reported W_4 dimension of C19a at degree 4 (92,838 of 102,091 columns; engine output, not what the certificate proves, see ../../semaev-m2-last-fall-degree/results/verification-correction-20261019.md). The three calibration systems are satisfiable with rho ~ 1.
- Measured peak RSS exceeded 2*ncols^2/8 by 2.0x, 1.65x, 1.46x at N = 24, 26, 28 (allocator, M4RI tables, Lw); the ratio fell with N, so its value at N = 40 is unknown.
- The log-log RSS fit (98 GB at C19) is an extrapolation of three points and is not a bound in either direction.
- **Host size: 256 GB RAM is an unvalidated planning choice** (P2 at rho ~ 1 is 150 GB before Lw and overhead). It is not a proved lower or upper bound.
- cores: 1 effective (m4ri echelonize is single-threaded as built here; measured user ~= wall).
- wall time: 2.7 d from the fit (exponent 2.43), up to ~7 d if iterations are as many as at D=4 (C19a/b took 7-8; the calibration runs 3). Not validated.
- disk: certificate R <= ~36 GB if nq <= 380k; ~6 GB at rho = 0.92. Plan 40 GB.

768 GB is **not** needed for this test; 256 GB is. 768 GB is the figure for sizes beyond C21 (C21 at D=5: 975k columns, 119 GB per matrix; m=4, ℓ=5 at N~46: 1.55M columns, 300 GB per matrix).

## Not covered
- `hky_par` (crypto #2214) was not built or run (build was denied in this session), so its memory/time on these instances is unmeasured. Its row storage is triangular, so expect roughly half the dense footprint, not less.
- m=4, ℓ=5 needs a four-chain system generator that #2410 does not have.
- This card tests W_5 only. It does not test W_6.
