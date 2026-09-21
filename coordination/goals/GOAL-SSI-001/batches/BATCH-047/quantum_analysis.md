# Quantum Analysis: Supersingular Isogeny Path-Finding

**Best achievable quantum exponent: p^{2/9+o(1)} (Tani claw-finding on Wesolowski tables)**
**Lower bound: Ω(p^{1/6}) (oracle model)**
**Gap: [p^{1/6}, p^{2/9}] — OPEN**

## The quantum landscape

| Algorithm | Time | Qubits | QRACM |
|-----------|------|--------|-------|
| Grover on VW | p^{1/4} | poly(log p) | 0 |
| **Tani on Wesolowski** | **p^{2/9}** | **p^{2/9}** | **0** |
| BHT + full QRACM | p^{1/3} total, p^{1/6} depth | O(log p) | p^{1/3} |
| Lower bound | p^{1/6} | — | — |

## Why p^{2/9} cannot be beaten (6 approaches checked)

| Approach | Obstruction |
|----------|-------------|
| A: Tighter structural bound | Lattice geometry: p^{1/3} is tight (Minkowski) |
| B: Better quantum claw-finding | Aaronson-Shi: N^{2/3} is optimal (proven) |
| C: Quantum walk on isogeny graph | Ramanujan: gives only p^{1/2} (same as Grover) |
| D: Exploit isogeny structure | Ramanujan kills local→global |
| E: Non-abelian HSP | 20+ years open, no progress |
| F: Unbalanced/multi-target | Unique collision prevents amplification |

## Critical knowledge-base correction

KN-TECH-029 records "quantum Õ(p^{1/4})" as the quantum baseline. This is STALE:
- **Old**: p^{1/4} (Biasse-Jao-Sankar 2014)
- **New**: p^{2/9} (Tani on Wesolowski, 2026)
- **Improvement**: factor p^{1/36} ≈ 2^7 at NIST-I

## At NIST-I (p ≈ 2^256)

Tani quantum attack:
- Time: 2^{56.9+o(1)} quantum operations
- Qubits: ~2^{57} logical (with surface code: ~2^{67} physical)
- At 1μs/T-gate: ~4500 years
- Verdict: COMPLETELY INFEASIBLE with current or projected hardware

## Conclusion

The quantum route (p^{2/9}) is:
1. The tightest known QUANTUM exponent
2. Infeasible at NIST-I (~2^{57} logical qubits × 4500 years)
3. Cannot be improved without breakthroughs in claw-finding, lattice geometry, or non-abelian HSP
4. An AUTOMATIC consequence of applying Tani to Wesolowski (not a new algorithm)
