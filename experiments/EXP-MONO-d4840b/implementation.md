# EXP-MONO-d4840b implementation notes

## What this is

A third attempt to find a curve satisfying Z=3, h_+>=1, h_->=1,
max(h_+,h_-)>=2, after `EXP-MONO-8ec0e5`'s own two resource_exhaustions
(an unmodified O(p) root-scan, then a verified-correct but only
1.55x-faster O(log p) splitting test — both still fundamentally O(p^3)
overall since neither reduced the *number* of (A,B) candidates enumerated).

## The algorithm

A short-Weierstrass cubic f(X)=X^3+AX+B has no X^2 term, so its three
roots always sum to zero. Every curve with Z=3 (three distinct rational
roots) can therefore be generated *directly*: choose r1 < r2 in F_p, set
r3 = -(r1+r2) mod p, skip if r3 ∈ {r1,r2} (a repeated root — not 3
distinct roots), else compute A = r1·r2+r1·r3+r2·r3 mod p and
B = -r1·r2·r3 mod p. This (A,B) is *guaranteed* to split with roots
exactly {r1,r2,r3} — no per-candidate root-scan needed at all. This is a
genuine O(p^2) total algorithm per prime, not merely a cheaper O(p^3) one.

Declared search order (frozen before execution, per specification.yaml):
primes ascending in [101,2000]; within a prime, r1 ascending 0..p-1
(outer), r2 ascending r1+1..p-1 (inner); first (A,B) satisfying the
qualifying filter is taken.

## Verification performed

- **Construction audit** (500 candidates): confirmed f(r1)=f(r2)=f(r3)=0
  mod p for every audited (r1,r2,r3,A,B) tuple — the root-pair-to-(A,B)
  construction is correct.
- **Filter audit** (250 candidates): the fast character-based h_+/h_-
  method agrees with brute-force 4-torsion counting on every audited
  candidate, consistent with every prior experiment in this sub-thread.
- **Per-prime pair counts**: every prime's own `pairs_examined` in
  `raw-result.json` matches C(p,2) exactly (e.g. 5050 at p=101, 187578 at
  p=613) — independently confirms the enumeration visits every unordered
  pair exactly once, in the declared order, with no double-counting or
  skips beyond the declared degenerate case.

## Result

`resource_exhaustion`, again: 6,179,235 root pairs (6,149,265 genuine,
non-degenerate candidates) examined across 87 primes (101..613) of the
declared 278, in 861.2s wall — no qualifying curve found. See
`execution_report.yaml` for the full measured-throughput comparison
against the two prior attempts (a real 1.71x genuine-candidate-per-second
improvement over the fast-splitting-test attempt) and the extrapolation
showing even this faster algorithm would need ~7 hours to cover the full
declared range — see the Coordinator's own decision record for the
recommended path forward.

## Files

- `implementation/run_root_pair_search.py` — the script.
- `runs/RUN-MONO-d4840b-1/` — the run package.

## Reused, read-only

- `experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`
- `experiments/EXP-MONO-815525/implementation/run_census.py` and its
  monomial/coefficient JSON tables
- `experiments/EXP-MONO-8ec0e5/implementation/run_amended_bivariate_test.py`
  (structural template for M6/Stage-1/Stage-2, not reached this run)
