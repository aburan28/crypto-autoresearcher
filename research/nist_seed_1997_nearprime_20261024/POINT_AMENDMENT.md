# Correct the coefficient-root binding before point-certificate rerun

**2026-10-24 UTC.** The first point run,
`runs/points-20261024T022651Z/`, stopped after 17 certificates at P-256
block 81. The archived candidate file stores the two `b_roots` in **numeric
sorted order**, whereas the census `n` column uses the root computed by
exponentiation `(-27/r)^((p+1)/4) mod p` when `p ≡ 3 (mod 4)` and `nt` is its
quadratic-twist order. At P-256 block 81, the sorted first root is the `nt`
branch, so the first point launcher erroneously paired `nt` with the sorted
second root and found no order-`nt` point. A direct Sage point count of both
roots confirmed the inversion; that diagnostic was read-only and did not
modify the failed run. The exact first launcher is retained as
`verify_points_v1.py`.

The corrected launcher computes the exponentiation root from the frozen seed
and field arithmetic, uses that root for a `canonical` row and its negation
for an `other` row, and checks membership in the archived two-root set. For
P-224 (`p ≡ 1 mod 4`), its two signs are isomorphic and the corrected
near-prime run uses only the canonical order; either archived root represents
it, so the smaller numeric root is chosen deterministically. Keep the
existing 99-position list, first-x search 1..32, point and Hasse controls,
10-second per-position and 120-second overall watchdogs. Write a fresh
point-run directory. The failed run is not a negative mathematical result.
