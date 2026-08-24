# Wesolowski Structural Ingredient Transfer Analysis
## TASK-20260804-132, BATCH-096

## The Wesolowski structural theorem

**Theorem 1.5 (Wesolowski 2026)**: For E supersingular over F_{p^2}, the minimal degree
of an isogeny E → E^{(p)} (Frobenius conjugate) satisfies deg ≤ (p/2)^{1/3}.

This theorem enables the p^{1/3} algorithm via the KN-TECH-055 pattern:
1. Structural bound: deg ≤ p^{1/3} (rigorous)
2. Distribution heuristic: the isogeny has B-smooth degree (Dickman probability)
3. MITM: split the smooth degree into two halves
4. Rerandomization: use the supersingular isogeny graph

## Why the proof works for supersingular curves

The key: End(E) for supersingular E is the DEFINITE QUATERNION ALGEBRA B_{p,∞}.
A maximal order in B_{p,∞} has a "LLL-short" basis of norm O(p^{1/2}).
The ideal I ⊂ End(E) corresponding to the isogeny E → E^{(p)} has norm p.
Finding a short element of I via LLL gives an isogeny of degree ≤ (p/2)^{1/3}.
This uses the 4-dimensional lattice structure of the quaternion algebra.

## Can this transfer to ordinary prime-field ECDLP?

**For ordinary curves over F_p**:
- End(E) is an order in Q(sqrt(D)) — COMMUTATIVE (rank 2 over Z)
- The "short element" problem in O_K has no 4-dimensional quaternion structure
- The analogue of the Frobenius ideal is the ideal corresponding to [k]G (the DLP target)
- Finding k via LLL on O_K would require a lattice of dimension 2 with det N ~ p
- The shortest vector in this lattice has norm ~ sqrt(N) ~ sqrt(p) — same as Pollard rho

**The obstruction**: Wesolowski's theorem uses 4D quaternion lattice reduction to find a degree ≤ p^{1/3} isogeny. For ordinary curves, the endomorphism ring is 2D (commutative), and the shortest vector in the 2D lattice has norm sqrt(N) — no improvement.

## The DLP lattice analogy

The ECDLP can be viewed as a 2D lattice problem:
- Lattice L: spanned by (N, 0) and (0, N) with the point [k]G embedded
- The "short vector" is (k, -1) with norm sqrt(k^2 + 1) ~ N^{1/2}
- No quaternion structure; LLL finds vectors of norm ~ sqrt(N) (same as Pollard rho)

For the Wesolowski pattern to improve this to N^{1/3}: we'd need a HIGHER-DIMENSIONAL
embedding of the DLP that gives short vectors of norm N^{1/3}. No such embedding is known.

## The 4D analogy attempt

What if we embed E in a 4-dimensional abelian variety A where End(A) is a quaternion algebra?
- The Weil restriction Res_{F_{p^2}/F_p}(E) is a 2-dimensional abelian variety over F_p
- Its endomorphism algebra is M_2(Q) (2×2 matrices) — still not B_{p,∞}
- For specific CM curves: A = E_1 × E_2 can have End(A) related to a quaternion algebra
- But: the DLP on E(F_p) is a DIFFERENT problem from the isogeny problem on A

## Conclusion

The Wesolowski structural theorem (deg ≤ p^{1/3} for E → E^{(p)}) uses the 4-dimensional
quaternion algebra structure of supersingular endomorphism rings. This structure is:
- PRESENT for supersingular curves (End(E) = B_{p,∞}, quaternion)
- ABSENT for ordinary curves (End(E) = imaginary quadratic order, commutative, 2D)

The analogue for ordinary prime-field ECDLP would require:
- A problem P related to ECDLP
- Such that P embeds in a higher-dimensional lattice with quaternion structure
- And a new structural theorem bounds the solution degree

No such problem P is known. The Wesolowski ingredient is not transferable.

## Impact on H-PSEUDO

The extension-field analysis (BATCH-095) showed H-PSEUDO asks for algebraic-type
Fourier flatness without algebraic mechanism. The Wesolowski analysis confirms:
the structural theorem approach also requires a HIGHER-DIMENSIONAL algebraic structure
(quaternion algebra) that is absent for prime-field ECDLP.

Both independent approaches converge on the same conclusion: prime-field ECDLP
lacks the higher-dimensional algebraic structure that enables sub-rho algorithms
for supersingular (quaternion endomorphisms) and extension-field (algebraic factor base) cases.

H-PSEUDO is the precise formulation of what would be needed to bypass this structural gap.
