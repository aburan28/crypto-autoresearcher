# Time-Memory Tradeoff: Wesolowski at SQIsign NIST-I

## The tradeoff curve

| log₂(B) | Memory (log₂M) | Time (log₂T) | Practical? |
|----------|----------------|---------------|------------|
| 4        | 50.5           | 152.7         | M feasible, T way above 128 |
| 5        | 61.6           | 140.3         | M borderline, T above 128 |
| 6        | 69.0           | 133.0         | M impractical, T above 128 |
| 7        | 74.4           | 128.7         | M impractical, T ≈ 128 (break-even) |
| 8        | 78.5           | 126.0         | M impractical, T < 128 |
| 10       | 84.6           | 123.8         | M impossible, T < 128 |
| 12       | 89.1           | 123.9         | M impossible, T < 128 |
| 14       | 92.9           | 125.2         | M impossible, T < 128 |
| 16       | 96.1           | 127.2         | M impossible, T ≈ 128 |
| 20       | 101.7          | 132.6         | M impossible, T > 128 |

## Break-even point

**Memory ≈ 2^{75}** (≈ 30 zettabytes = 30× all data on Earth)

Above this memory: Wesolowski beats VW (time < 2^128)
Below this memory: VW at 2^128 remains tighter

## At practical memory budgets

| Memory budget | Physical scale | Attack time | Meets NIST-I? |
|---------------|----------------|-------------|---------------|
| 2^40 (1 TB)  | Consumer       | 2^{164.8}   | YES (secure) |
| 2^50 (1 PB)  | Data center    | 2^{151.1}   | YES (secure) |
| 2^60 (1 EB)  | Nation-state   | 2^{140.3}   | YES (secure) |
| 2^70 (1 ZB)  | All Earth data | 2^{130.6}   | YES (secure) |
| 2^75 (30 ZB) | Impossible     | 2^{128}     | BREAK-EVEN |
| 2^80          | Fantasy        | 2^{124.6}   | NO (theoretical) |
| 2^93 (optimal)| Fantasy       | 2^{118.5}   | NO (theoretical) |

## Conclusion

**The concrete-cost finding (2^{118.5}) is PURELY THEORETICAL.**

At any practically achievable memory (≤ 2^{70}), Wesolowski's algorithm costs
MORE than 2^{128} — the VW collision-search baseline. The theoretical advantage
only materializes at memory ≥ 2^{75}, which exceeds all storage ever built by
a factor of 30.

**For the GOAL completion criterion** ("fully charged attack estimate that
materially improves a matched baseline"): when memory is HONESTLY CHARGED
(as AGENTS.md requires), the attack does NOT improve the practical baseline
at any achievable parameter regime. The VW collision search at 2^{128} time
with negligible memory remains the tightest PRACTICAL attack.

## Implication for GOAL-SSI-001

The goal's completion criterion is NOT met by this finding because:
1. "Fully charged" includes memory cost — and charging 2^{92.5} memory makes
   the attack impractical
2. At practical memory, the attack cost EXCEEDS the previous baseline
3. The "material improvement" exists only in an infinite-memory model

The honest state: SQIsign NIST-I has ≈128-bit practical security (VW-limited),
with a theoretical security gap in the infinite-memory model (≈119 bits).
This is a CHARACTERIZATION, not a break.
