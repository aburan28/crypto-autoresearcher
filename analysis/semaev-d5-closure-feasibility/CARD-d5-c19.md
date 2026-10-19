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

## Host requirement (derived; extrapolation is 6.2x past the largest measured point)
| quantity | value | basis |
|---|---|---|
| columns | 760,099 | sum_{d<=5} C(40,d), exact |
| one dense matrix | 72.2 GB | ncols^2/8, exact |
| peak RAM, lower bound | **>= 145 GB** | lfdclose2 rebuilds A into a larger B each chunk (two live copies) |
| peak RAM, fit | 98 GB (ncols^1.59) | fit of 3 points; **understates**, ignores the copy and the certificate map |
| certificate map pi | ncols * ceil(nq/64) * 8 B, ~10 GB at nq = 100k | nq unknown until run |
| **RAM to request** | **>= 256 GB** | covers 2 x 72 GB + pi + slack |
| cores | 1 effective (m4ri echelonize is single-threaded as built here) | measured user ~= wall |
| wall time | 2.7 d (fit) up to ~7 d if iteration count is 8 as at D=4 | fit exponent 2.43; calibration runs had 3 iterations, C19a/b at D=4 had 7-8 |
| disk | >= 25 GB (certificate + inputs) | derived |

768 GB is **not** needed for this test; 256 GB is. 768 GB is the figure for sizes beyond C21 (C21 at D=5: 975k columns, 119 GB per matrix; m=4, ℓ=5 at N~46: 1.55M columns, 300 GB per matrix).

## Not covered
- `hky_par` (crypto #2214) was not built or run (build was denied in this session), so its memory/time on these instances is unmeasured. Its row storage is triangular, so expect roughly half the dense footprint, not less.
- m=4, ℓ=5 needs a four-chain system generator that #2410 does not have.
- This card tests W_5 only. It does not test W_6.
