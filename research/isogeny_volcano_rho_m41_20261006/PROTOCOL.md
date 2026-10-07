# Protocol: the full isogeny volcano at m = 41 (replication of the m = 37 study)

Frozen 2026-10-06, before any rho data for this study existed. Same question,
same method, same analysis as `../isogeny_volcano_rho_20261005` (m = 37),
repeated at a larger field and a different conductor. Lessons from m = 37 are
built in from the start, not added as amendments: the idle-machine timing test
is part of the plan, and nothing else runs during timed phases.

## Object
Koblitz curve E0: y² + xy = x³ + 1 over F_2^41 = F_2[x]/(x^41 + x^3 + 1).
#E = 4 · l, l = 549756390943 (prime, ≈ 2^39). Trace −2308219.
[O_K : Z[π]] = 409 · 1721, K = Q(√−7), h(O_K) = 1; both primes are inert.

| level | conductor f | curves | ord[𝔩₂₃] | ord[𝔩₁₁] | ord[𝔩₂₉] |
|---|---|---|---|---|---|
| crater | 1 | 1 | 1 | 1 | 1 |
| 409-floor | 409 | 410 | 205 | 82 | 410 |
| 1721-floor | 1721 | 1,722 | 574 | 861 | 1722 |
| bottom | 703889 | 706,020 | 2870 | 1722 | 8610 |

Total: 708,153 curves.

## Finding curves
- **Floors:** one explicit vertical isogeny per floor from E0 (`vert.gp`).
  Kernel x-coordinates come from x-only arithmetic over F_2^(41·204) (409, on
  the quadratic twist, since c^204 = −1) and F_2^(41·215) (1721, on E, since
  c^215 = 1). The image curve comes from char-2 Vélu (b′ = 1 + v + v², with
  v the sum of the kernel x-coordinates; checked against PARI `ellisogeny` on
  6 random 73-isogenies at m = 37, 6/6 exact). Then the horizontal 29-isogeny
  cycle from that curve, whose length equals the class number, enumerates the
  whole floor.
- **Bottom:** random scan with the C sieve (`search.c`, [N]P = O for two
  points), each hit re-verified by PARI `ellcard`.
- **Level (exact, two independent invariants):** the horizontal 23-cycle
  length (1 / 205 / 574 / 2870) and the 11-cycle length (1 / 82 / 861 /
  1722). Both are measured on every sampled curve and must agree with the
  assigned level. Every sampled curve also has #E = N confirmed by `ellcard`.

## Rho sample (selection rule fixed now)
- crater: n = 3000 negation only, n = 3000 negation + Frobenius.
- 409-floor: 30 curves, the first 30 visited along the 29-cycle from the
  vertical-isogeny image; n = 200 each.
- 1721-floor: 30 curves, the first 30 *distinct Galois orbits* visited along
  its 29-cycle; n = 200 each.
- bottom: 30 scan hits with distinct Galois orbits, in ascending b; n = 200 each.
Every non-crater curve runs with negation only, its full automorphism group.

Solver: `rho.c` parametrised by `params.h`. It is otherwise the m = 37 solver,
with two changes made and tested before this protocol: Itoh–Tsujii inversion
generalised to any M, and the `Q2[]` table enlarged from 32 to 64 entries (at
M = 41 the old size overflowed, and 40/40 test solves were rejected by the
verifier as wrong answers; no m = 37 run was affected, since there QPOW = 28).
Every solve is verified against the secret and by recomputing [k]P = Q.

## Phases (no other user process during phases 2 and 3)
1. Solves: shuffled jobs on 4 pinned cores.
2. Per-step benchmark: sequential on CPU 0, 3 reps of 2^20 steps per curve,
   shuffled order.
3. Idle timing test: crater (both modes) + curves 1 and 2 of each lower level,
   300 solves each, 15 interleaved rounds of 20, sequential on CPU 0.

## Pre-declared analysis (alpha = 0.05)
Identical to m = 37 (`analyze_volcano.py`):
- 0. validity: every solve verified.
- H1: any curve faster than crater + Frobenius (one-sided Mann–Whitney per
  curve, Holm correction).
- H2-steps: Kruskal–Wallis over levels, ANOVA on curve means, and TOST of each
  level vs the crater (negation only) with margin ±3% (90% bootstrap CI).
- Within-level Kruskal–Wallis.
- Per-step ns: Kruskal–Wallis, and TOST ±3%.
- H2-time from phase 3: TOST ±3%.
- Frobenius speedup in steps and time, against √41 = 6.40.
- Spearman correlation of per-curve mean steps with the traits.

Plus the same trait computations: `traits.py` and `smooth_endos.py` rerun at
m = 41, and GHS m(b).

## Scope
m = 41, this solver, this machine. Precision is lower than at m = 37 (200
solves per curve against 1000), because each solve costs about 46× more. If
the 90% CIs exceed ±3%, the verdict is reported as inconclusive, not
equivalent.
