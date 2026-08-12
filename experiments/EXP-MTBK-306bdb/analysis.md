# EXP-MTBK-306bdb — Corrected cell-grid analysis (protocol v1, AMEND-001)

Run: RUN-MTBK-306bdb-cellgrid
Date: 2026-08-06
Author: coordinator (executor subagent returned empty; disclosed in receipt)

## 1. Why this analysis exists

The frozen v0 objective contained a rescue-window prediction (regime (ii)): at
cells with `t = T_desc/sqrt(N)` in `[1, (m+1)/2)` the BKK sparse check was
claimed to give a FINITE multi-target crossover `K*(BKK)` where the standard
factor-base descent had `K*(std) = inf`. AMEND-001 (approved this batch)
records that this regime is structurally unreachable at any planned curve size
and replaces the falsifiable content with the measured full-check ratio vs the
sweep-theorem factor `2^(m-1)`.

## 2. Corridor emptiness (analytical + numeric)

- Decomposability: `B >= N^(1/m)`.
- Sweep-cost rescue window: `1 <= B^(m-1)/sqrt(N)` and
  `beta*(B/2)^(m-1) < sqrt(N)`, `beta = 2/(m+1)`.
- Combining: `N^(1/m) < B < 2*((m+1)/2*sqrt(N))^(2/(m-1))`, satisfiable only
  if `N < ((m+1)/2)^(2m/(m-2))`:
  - m=3: N < 64
  - m=4: N < 39
  - m=5: N < 39
- Numeric scan confirms EMPTY for N in {64, 10^3, 1e5, 5.2e4, 1e9} and every
  planned (p, b) cell. Under the geometric model `T ~ N/B`, both K* collapse
  to ~1-2 targets (ratio ~1.0-1.1) or both are infinite; again no rescue cell.

## 3. Measured evidence (p=1009 family, 36 cells)

Grid: curve seeds {1,5}, b in {0.4,0.5,0.6}, m in {3,4,5}, target seeds {1,2}.

| channel | m=3 | m=4 | m=5 | theorem (2^(m-1)) |
|---|---|---|---|---|
| descent ratio mean | 1.170 | 1.037 | 0.957 | 4 / 8 / 16 |
| relation ratio mean | 1.822 | 0.968 | 1.427 | 4 / 8 / 16 |

- The descent channel is flat at ~1.0 for all m: BKK finds a first-success
  decomposition in the same ~N/B geometric number of checks as std.
- The relation channel shows 1.5-2x on average; the only cells approaching the
  sweep factor 4x are m=3, b=0.4 (B=13,16; ratio 3.35-4.00) — the smallest
  bases, where the (B/2)^2 enumeration completes nearly exhaustively.
- No cell reaches 0.9 x 2^(m-1) for m in {4,5}; the m=3 b=0.4 cells reach the
  sweep bound for relation collection only.

## 4. Interpretation

1. The BKK sparse check does NOT deliver a per-target descent speedup at toy
   scale: the descent channel is dominated by first-success geometry (~N/B),
   and the domain restriction halves the tuple set but not the geometric rate.
2. Relation collection does benefit where the half-domain enumeration is
   small enough to run near-exhaustive (m=3, tiny B); this is a finite-base
   effect, not the announced (m+1)/2 net speedup.
3. The rescue-window claim is therefore UNFALSIFIABLE at toy scale (empty
   corridor) and, in the measured regime, the channel ratios stay at ~1.0-1.8,
   far below the sweep theorem's 2^(m-1). Per AMEND-001's corrected
   falsification criteria: measured descent ratio < 0.9 x 2^(m-1) at m in
   {3,4} — H-MTBK-001's BKK-rescue mechanism is WEAKENED scoped to the toy
   enumeration model.

## 5. Scope honesty

- This weakens the multi-target BKK rescue as implemented (naive ordered
  enumeration, first-success stopping, toy p~1000). It does NOT touch the
  combinatorial theorem KN-FIND-982fdf (C_t-minimality) nor the H-PSEUDO
  orientation work; those are separate claims with separate evidence.
- A full-sweep implementation (memorizing the entire relation table) might
  recover part of the announced factor; that would be a NEW experiment with a
  new contract, not a repair of this one (rule 4: corrections create new
  records).
- Toy evidence never speaks to crypto-scale validation (rule 7). The
  geometric model is the operative cost model at this scale.

## 6. Raw artifacts

- runs/RUN-MTBK-306bdb-cellgrid/result.json (36 cells, checks per channel)
- runs/RUN-MTBK-306bdb-cellgrid/manifest.yaml
- amendment AMEND-001.yaml (corridor derivation + probes)
