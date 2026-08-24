# Formal Group Linearization: FAILS

**Verdict**: FORMAL_GROUP_FAILS — four independent fatal obstructions.

## The idea

The formal group logarithm linearizes the group law: log([k]P) = k·log(P).
This makes kernel points form an ARITHMETIC PROGRESSION in log-coordinates.
Could this yield sub-√ℓ kernel sum evaluation?

## Four fatal obstructions

### 1. Domain mismatch
log_Ê converges over p-adic rings (Z_p, Q_p). The computation lives over F_q.
No bridge exists. The anomalous case (KN-TECH-033, trace = 1) is the unique
exception; it doesn't apply to supersingular curves.

### 2. Torsion locality (Néron-Ogg-Shafarevich)
For ℓ ≠ p: the ℓ-torsion injects into the reduction mod p. The kernel points
have v_p(t) = 0 — they are NOT in the formal group's convergence disk.
The linearization literally cannot reach them.

### 3. Finite-field summation barrier
Even granting the arithmetic progression: Σ_{k=1}^N 1/(k²-d) mod p has NO
known sub-linear evaluation. The digamma closed form is characteristic-0 only.
Over F_p: this requires Θ(N) operations.

### 4. Nonlinearity persistence
The composition x = X(k·h) = 1/(kh)² + c₀ + c₁(kh) + ... is transcendental.
The linearization moves complexity from the ITERATION to the EVALUATION
without reducing total cost. A sum of a transcendental function at equally
spaced points is not cheaper than N evaluations.

## Universality theorem (Silverman IV.5.5)

Every homomorphism from Ê to a commutative formal group factors through log_Ê.
There is NO alternative linearization. The formal group IS the universal one,
and it fails for the reasons above.

## What would falsify this

1. A finite-field digamma: O(log N) algorithm for Σ 1/(k²-d) mod p
2. A global formal-group coordinate: ℓ-torsion in the convergence disk (impossible by NOS)
3. A bounded-degree algebraic identity for Σ ℘(k·z₀) (believed not to exist)
4. A non-formal-group linearization over F_q (no candidate known)

## Conclusion

The last crack in the wall is sealed. Sub-√ℓ isogeny computation is blocked
by the group law's degree-2 nature propagating through every representation.
The formal group — the one mathematical object designed to linearize the
group law — cannot bridge from its p-adic domain to the finite-field setting.
