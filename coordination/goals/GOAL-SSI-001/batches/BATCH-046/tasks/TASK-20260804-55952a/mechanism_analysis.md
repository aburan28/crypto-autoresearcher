# Sub-p^{1/3} Mechanism Analysis

**Task**: TASK-20260804-55952a (GOAL-SSI-001/BATCH-046)

## The structural barrier

The p^{1/3} exponent in Wesolowski 2026 is NOT accidental. It reflects:

1. The traceless sublattice of a maximal order in B_{p,∞} has rank 3
2. Minkowski for rank-3 gives minimum ~det^{1/3} ~ p^{1/3}
3. ANY algorithm reducing to short-vector-finding in quaternion orders hits this

This means: every direction that looks for "short algebraic objects" in the
quaternion setting will find objects of size ~p^{1/3} and no smaller.

## The only open avenue: dimensional ascent

IDEA-SSI-EXP-002 exploits the observation that PIP (principal ideal problem)
in HIGHER-dimensional matrix rings M_g(O) for g >= 2 is solvable in heuristic
polynomial time. The idea: embed the rank-1 problem into rank-2, solve it there,
and project back.

**Morita equivalence** guarantees an abstract bijection:
- Left O-ideals ↔ Left M_2(O)-ideals (up to isomorphism)
- Principal O-ideals ↔ Principal M_2(O)-ideals
- Generator alpha of O-ideal I ↔ Generator diag(alpha, alpha) of M_2(I)

**The decisive question**: Is this bijection COMPUTATIONALLY EFFECTIVE?
Specifically: given an M_2(O)-ideal (found by the g>=2 algorithm), can you
extract the rank-1 generator without knowing O first?

## What a breakthrough looks like

If IDEA-SSI-EXP-002 works:
- The isogeny problem is solvable in polynomial time
- Every isogeny-based cryptosystem (SQIsign, CSIDH, CGL) is broken
- This would be a result comparable to Shor's algorithm for RSA

If it's circular:
- p^{1/3} is likely a hard structural barrier
- The honest conclusion is: no classical sub-p^{1/3} mechanism is currently available
- The goal should record this as the narrowest supportable claim

## Directions assessed as vacuous

- Spectral/Ramanujan methods: global information, no local pair extraction
- CM lifting / Shimura: Frobenius doesn't lift; no local-global principle
- Jacquet-Langlands / L-functions: global, non-constructive
- Norm-equation sieve: lattice minimum IS p^{1/3}; sieving doesn't go below
- Index calculus: relation-finding circular with the full problem

## Next action

READ KN-LIT-7641. This is zero-compute, decisive, and maximal-payoff.
