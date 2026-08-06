# Quantum p^{1/6} Attempt: NOT ACHIEVABLE

**Verdict**: p^{1/6+o(1)} total quantum time is NOT achievable with any known technique.
**Gap [p^{1/6}, p^{2/9}] is likely PERMANENT.**

## The four-way cost-product barrier

| Obstruction | What it blocks | Why |
|-------------|---------------|-----|
| 1. Table-Query Product | Free QRACM | Building p^{1/3} entries costs p^{1/3} classically |
| 2. Oracle-Query Product | Non-smooth Grover | √d oracle cost × p^{1/6} queries = p^{1/3} |
| 3. Claw-Finding Optimality | Tani improvement | Aaronson-Shi proves Ω(N^{2/3}) for black-box |
| 4. Collision Density | Smaller tables | Need p^{1/3} entries to contain the solution |

## 12 routes checked, all fail

All reduce to one of the four obstructions above. The most promising (Route 9:
non-black-box exploitation of modular polynomial structure) is suppressed by
the Ramanujan property: after O(log p) composition steps, outputs are
pseudorandom and carry no exploitable algebraic structure.

## Conditions for p^{1/6} to become achievable

1. Sub-√d isogeny evaluation (breaks Obstruction 2) — OPEN, no candidate
2. Non-black-box quantum claw-finding (breaks Obstruction 3) — OPEN, Ramanujan prevents
3. Sub-N QRACM population (breaks Obstruction 1) — IMPOSSIBLE (classical memory interface)
4. Non-abelian HSP for quaternions (bypasses everything) — 20+ years open

## The honest final state

The quantum gap [p^{1/6}, p^{2/9}] is:
- Real (not an artifact of analysis)
- Likely permanent (Ramanujan + Aaronson-Shi + √élu)
- Irrelevant at NIST-I (even p^{1/6} = 2^{42.7} ≈ infeasible on quantum hardware)
