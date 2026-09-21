# PIP Bypass Analysis: Can g≥2 Prescribed-Kernel Methods Solve OneEnd Without End(E)?

**Task**: TASK-20260804-55952a (GOAL-SSI-001/BATCH-046)  
**Verdict**: BYPASS_BLOCKED  
**Named obstruction**: Deuring-Page-Wesolowski input-dependence barrier

## Three independent structural barriers

### Barrier 1: Input barrier
The PIP problem in M_2(O) requires O as explicit input. Without O, you don't
know what M_2(O) is and cannot formulate the problem.

### Barrier 2: Selection barrier
Choosing valid endomorphism kernels K ⊂ E^2[N] requires knowing O mod N
(which subgroups of E[N] are endomorphism kernels is encoded by the Galois
representation ρ_N(O) ⊂ M_2(Z/NZ)). Computing this IS computing End(E) mod N.

### Barrier 3: Output barrier (Page-Wesolowski)
Any non-trivial endomorphism of E^2 (outside M_2(Z)) has at least one entry
α ∈ O \ Z. Extracting α gives a non-scalar endomorphism of E. By the
Page-Wesolowski equivalence: OneEnd ≡ EndRing. So any polynomial-time method
to find non-trivial endomorphisms of E^2 constitutes a polynomial-time
algorithm for the full endomorphism ring problem.

## The computable subring of End(E^2) without O

Given E only as a Weierstrass equation (no endomorphism ring knowledge):

**R_comp = M_2(Z) ⊂ M_2(O) = End(E^2)**

This has rank 4 out of 16. The missing 12 dimensions encode End(E).
No polynomial-time computation on E^2 can escape M_2(Z) without solving OneEnd.

## Why exhaustive kernel search doesn't help

The set of K ⊂ E^2[N] with |K| = N^2 has size ~N^4. Valid endomorphism kernels
are ~N^3. Density ~1/N. Search cost: N^3 isomorphism checks.

For the Wesolowski-relevant scale N ~ p^{1/3}: cost is p (no improvement).
For sub-p^{1/3} performance, you'd need N ~ p^{1/9}, but at that degree you
get only O(p^{1/3}) information bits — requiring ~p^{2/3}/p^{1/3} = p^{1/3}
iterations to determine O. The p^{1/3} barrier re-emerges from information theory.

## Conclusion

The dimensional-ascent avenue (IDEA-SSI-EXP-002) is closed by circularity:
- Morita equivalence is algebraically correct but computationally circular
- The g≥2 algorithm is powerful within its setting but requires the ring as input
- Any method that finds non-trivial endomorphisms of E^2 without End(E) would
  break all isogeny-based cryptography (polynomial-time OneEnd)

**p^{1/3+o(1)} is the standing classical barrier. No known technique bypasses it.**
