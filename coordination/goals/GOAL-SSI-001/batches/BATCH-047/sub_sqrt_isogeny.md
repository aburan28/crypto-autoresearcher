# Sub-√ℓ Isogeny Computation: Deep Analysis

**Date**: 2026-08-05  
**Role**: Idea Generator  
**Question**: Can we compute an ℓ-isogeny in fewer than O(√ℓ) field operations?  
**Verdict**: NO known algorithm achieves sub-√ℓ. NO proven lower bound exists. The structural barrier is the QUADRATIC NONLINEARITY of the elliptic curve group law, which prevents all known algebraic acceleration techniques from breaking the baby-step/giant-step threshold.

---

## 1. Problem Statement

**Input**: An elliptic curve E/F_q in short Weierstrass form y² = x³ + ax + b, and a point P ∈ E(F_q) of prime order ℓ.

**Output**: The j-invariant j(E/⟨P⟩) of the codomain curve (or equivalently, its Weierstrass coefficients).

**Current best**: √élu [KN-LIT-764, Bernstein-De Feo-Leroux-Smith 2020] achieves O(√ℓ · (log ℓ)²) field operations in F_q.

**Target**: O(ℓ^α) for some α < 1/2.

---

## 2. What √élu Actually Does (Precise Description)

The codomain computation reduces (via Vélu's formulas) to computing:

```
t = Σ_{k=1}^{(ℓ-1)/2} (3x_k² + 6a₂x_k + a₂² - a₄)
w = Σ_{k=1}^{(ℓ-1)/2} (5x_k³ + ...)
```

where x_k = x([k]P). Equivalently: compute the power sums p_j = Σ x_k^j for j = 1, 2, 3 (and a few related sums involving y_k for the isogeny map evaluation).

**√élu's BSGS decomposition**:

1. Choose b ≈ √ℓ. Write k = ib + j for i ∈ {0,...,g-1}, j ∈ {1,...,b} where g ≈ √ℓ.
2. **Baby steps**: Compute {[j]P : j = 1,...,b}. Cost: O(b) = O(√ℓ) group operations.
3. **Giant steps**: Compute {[ib]P : i = 0,...,g-1}. Cost: O(g) = O(√ℓ) group operations.
4. **Polynomial construction**: Build the degree-b baby-step polynomial
   F(T) = ∏_{j=1}^{b} (T - x([j]P)) from its roots. Cost: O(b log b) via subproduct tree.
5. **Multi-point evaluation**: Evaluate certain rational functions derived from F at the g giant-step x-coordinates. Cost: O(g log² g) via fast multi-point evaluation.
6. **Combination**: Sum the results. Cost: O(g).

**Total**: O(√ℓ · (log ℓ)²) field operations.

The key algebraic identity: the Vélu sum decomposes as

```
Σ_{k=1}^{(ℓ-1)/2} f(x_k, y_k) = Σ_{i=0}^{g-1} [evaluation of a degree-b rational function at (X_i, Y_i)]
```

where (X_i, Y_i) = [ib]P and the rational function encodes all baby-step information. Each evaluation costs O(b log b / g) amortized via batch multi-point evaluation.

---

## 3. Direction-by-Direction Analysis

### Direction 1: Multi-point Evaluation Tricks

**Question**: Can we evaluate F(T) at g points faster than O(g log² g)?

**Answer**: No, in the algebraic computation tree model. Multi-point evaluation of a degree-n polynomial at m arbitrary points requires Ω(n + m) operations (trivially: the output has n + m size). The subproduct-tree method achieves O((n + m) log² (n + m)), which is essentially optimal.

The g evaluation points {x([ib]P)} are in GENERAL POSITION — they are not in arithmetic or geometric progression, they do not satisfy any known polynomial relation of bounded degree, and they have no FFT-friendly structure. The reason: x([ib]P) is determined by iterating a degree-2 rational map (the multiplication-by-b map on the x-line), whose iterates generate an orbit with no algebraic structure exploitable for batch evaluation beyond what BSGS already uses.

**Sub-direction**: What if we need K(x₀) at a SINGLE specific point x₀?

Then we need ∏_{k=1}^{d} (x₀ - x_k) for d = (ℓ-1)/2. This is a single field element. Could it be computed faster than O(√ℓ)?

The BSGS approach gives:
```
K(x₀) = ∏_i ∏_j (x₀ - x([ib+j]P))
       = ∏_i [F_i(x₀)]
```
where F_i(T) = ∏_j (T - x([ib+j]P)) is a degree-b polynomial depending on both the giant step i and all baby steps relative to it.

Each F_i requires knowing x([ib+j]P) for all j, which requires the ADDITION of [ib]P and [j]P. Since addition on E is quadratic, the x-coordinate of [ib]P + [j]P cannot be expressed as a polynomial of bounded degree in x([ib]P) and x([j]P) alone without y-coordinates.

√élu handles this by working with the RESULTANT:
```
K(x₀) = Res_T(baby_poly(T), giant_function(x₀, T))
```
where the resultant structure separates baby and giant variables. This gives exactly O(√ℓ log² ℓ).

**Verdict**: No improvement beyond √élu possible via multi-point evaluation on arbitrary points. The evaluation points lack exploitable structure.

---

### Direction 2: Division Polynomial Recursion

**The recursion** (EDS/division polynomial values at P):

```
ψ_{m+n} · ψ_{m-n} = ψ_{m+1} · ψ_{m-1} · ψ_n² - ψ_{n+1} · ψ_{n-1} · ψ_m²
```

where ψ_k := ψ_k(P) ∈ F_q (division polynomial evaluated at the specific point P).

**What this gives**: Computing a SINGLE ψ_k(P) costs O(log k) field operations via a double-and-add ladder on the recurrence. This is how scalar multiplication is done efficiently.

**What we need**: The kernel x-coordinates satisfy
```
x([k]P) = x_P - ψ_{k-1}(P) · ψ_{k+1}(P) / ψ_k(P)²
```

So computing ALL x_k for k = 1,...,(ℓ-1)/2 requires ALL ψ_k values for k = 0,...,(ℓ+1)/2.

**Can we compute ALL ψ_k values faster than O(ℓ)?**

The doubling ladder gives: ψ_1, ψ_2, ψ_4, ψ_8, ..., ψ_{2^t} in O(t) = O(log ℓ) steps.

Filling in ALL values from 1 to d = (ℓ-1)/2 requires O(d) = O(ℓ) sequential steps of the recursion (there is no "FFT on the EDS" because the recurrence is bilinear, not linear).

**Could we compute the SUM Σ x_k without all individual x_k?**

```
p_1 = Σ_{k=1}^{(ℓ-1)/2} x([k]P) = ((ℓ-1)/2) · x_P - Σ_{k=1}^{(ℓ-1)/2} ψ_{k-1}·ψ_{k+1}/ψ_k²
```

This reduces to: S = Σ_{k=1}^{(ℓ-1)/2} ψ_{k-1}·ψ_{k+1}/ψ_k²

**Can S be computed via a telescoping identity?**

Note: ψ_{k+1}·ψ_{k-1}/ψ_k² = x_P - x([k]P) by definition. So S = (ℓ-1)/2 · x_P - p_1. This is CIRCULAR — it's the definition of p_1, not a shortcut.

**Can S be computed via cumulative-sum augmentation of the state vector?**

For a LINEAR recurrence a_k = Σ c_i a_{k-i}, we can compute Σ_{k=1}^N a_k in O(w³ log N) by augmenting the w-dimensional state vector with a "running sum" component and using matrix exponentiation.

For the EDS recurrence: the state is (ψ_k, ψ_{k-1}, ψ_{k+1}, ...) but the transition map is BILINEAR (products of state components), not linear. This means:
- The state space is NOT a vector space under the transition.
- Matrix exponentiation does not apply.
- The cumulative sum cannot be folded into a finite augmented state.

**This is the critical structural barrier for Direction 2.**

**Could a "logarithmic" change of variables linearize the EDS?**

Define u_k = log ψ_k (in some formal sense). Then the bilinear recurrence ψ_{m+n}·ψ_{m-n} = ... becomes additive: u_{m+n} + u_{m-n} = ... This is related to the formal group logarithm. But:
- Over a finite field, "log" doesn't exist in general.
- The sigma-function/theta-function analogue works over C or p-adically, but evaluating it requires O(ℓ) terms of a q-expansion.
- No known finite-field shortcut for the formal-group approach gives sub-√ℓ.

**Verdict**: The division polynomial recursion gives O(log ℓ) for INDIVIDUAL terms, but the nonlinear (bilinear) nature prevents sub-linear SUMMATION. √élu's O(√ℓ) already exploits the group structure optimally via polynomial BSGS.

---

### Direction 3: Power Sums via Algebraic Relations

**Setup**: p_j = Σ_{k=1}^{(ℓ-1)/2} x([k]P)^j for j = 1, 2, 3.

**Newton's identities**: relate p_j to the elementary symmetric polynomials e_i (coefficients of K(x)), but require BOTH sets — they don't give p_j from nothing.

**Question**: Is there a recursion for p_j as a function of j (for fixed P)?

Define: p_j(P) = Σ_{k=1}^{(ℓ-1)/2} x([k]P)^j.

As j varies, p_j is the j-th moment of the "empirical distribution" of kernel x-coordinates. There is NO known polynomial recurrence relating p_j to p_{j-1}, p_{j-2}, ... that has depth less than (ℓ-1)/2.

**Why not?** The values x_1, ..., x_d are d DISTINCT elements of F_q. Their power sums determine them uniquely (via Newton's identities → elementary symmetric polynomials → roots). So computing p_1, ..., p_d contains the same information as computing all x_k. There is no "compression": the first few power sums (p_1, p_2, p_3) carry only O(1) bits of the O(ℓ · log q) bits needed to specify the kernel.

However, for the CODOMAIN COMPUTATION, we only NEED p_1, p_2, p_3 (and a few y-sums). This is O(1) field elements of output. The question is: can these O(1) outputs be computed from the input (E, P) in sub-√ℓ time?

**The trace/norm approach**: p_1 = Σ x_k is the TRACE of x in the "function field" of the kernel polynomial. Could it be computed via a trace formula?

The trace of x mod K(x) is Tr_{F_q[x]/K(x) / F_q}(x) = -(coefficient of x^{d-1} in K(x)).

But K(x) is not a MINIMAL POLYNOMIAL (its roots are all in F_q, not in an extension). It's a completely split polynomial. Its coefficients encode all d roots. There is no trace-formula shortcut.

**Hecke operator interpretation**: The sum Σ_{C ⊂ E[ℓ], C cyclic} j(E/C) = T_ℓ(j)(E) is a Hecke eigenvalue computation — summing over ALL ℓ+1 subgroups. This can be computed from the modular polynomial Φ_ℓ. But we want the sum for a SINGLE specific subgroup, not all of them. Restricting to one subgroup IS the isogeny computation problem.

**Verdict**: No algebraic shortcut for computing p_j for a SPECIFIC cyclic subgroup. The power sums of kernel x-coordinates are not accessible via trace formulas, Hecke operators, or recurrences that bypass enumeration of kernel elements.

---

### Direction 4: Endomorphism-Ring Shortcuts

For special curves (j = 0 with Z[ζ₃]-action, j = 1728 with Z[i]-action):

The kernel ⟨P⟩ may be stable under the extra endomorphism α, giving:
```
{x([k]P) : k = 1,...,(ℓ-1)/2} = {x(α·[k]P) : k = 1,...,(ℓ-1)/2}
```

This PERMUTES the kernel points (doesn't reduce their count). The saving: for degree-4 endomorphisms, we can use 4-dimensional GLV/GLS decomposition to compute scalar multiples faster. But this gives a CONSTANT factor (≤ 4×) improvement, not a sub-√ℓ EXPONENT change.

**For generic curves** (End(E) = Z): no extra endomorphisms exist. No shortcut.

**Verdict**: Constant-factor improvement only. Does not change the exponent.

---

### Direction 5: Transform Methods (DFT/FFT)

**The fantasy**: if x([k]P) = g(k) where g has a FOURIER-FRIENDLY structure, then
```
S(x₀) = Σ_{k=1}^{(ℓ-1)/2} 1/(x₀ - g(k))
```
could be computed via number-theoretic transform (NTT) in O(ℓ^ε) time.

**Reality**: The map k ↦ x([k]P) is a map Z/ℓZ → F_q defined by iterating a degree-2 rational map (the multiplication-by-1 map on the x-line: x([k+1]P) = R(x([k]P), x([k-1]P), x(P)) where R is a rational function of total degree 4).

This map is:
- **Bijective** on {1,...,ℓ-1}/{k ∼ ℓ-k} (onto (ℓ-1)/2 distinct values)
- **Non-polynomial**: it cannot be expressed as a polynomial of bounded degree in k
- **Non-periodic**: the orbit visits each x-value exactly once (before repetition at period ℓ)
- **Pseudorandom**: from a cryptographic standpoint, the sequence (x([k]P))_k is computationally indistinguishable from random (this IS the ECDLP hardness assumption)

If the map k ↦ x([k]P) were efficiently computable as a "simple" function of k (polynomial, rational, exponential sum), then ECDLP itself would be easy. The difficulty of ECDLP is PRECISELY the difficulty of "de-indexing" this map.

**Consequence**: The Vélu sum cannot be rewritten as a DFT, NTT, or any convolution-type operation because the "sample points" g(k) have no transform-compatible structure. Any such structure would break ECDLP.

**A more precise formulation**: The discrete Fourier transform computes Σ_k f(k)·ω^{jk} in O(n log n) because ω^{jk} factors as a MULTIPLICATIVE function of (j,k). The Vélu sum Σ_k 1/(x₀ - x([k]P)) does NOT factor this way: the summand 1/(x₀ - x_k) depends on x_k = x([k]P), which is a QUADRATIC iteration in k, not a multiplicative/additive character.

**Could we work in the "formal group" Fourier basis?** Over the complex numbers, the Weierstrass ℘-function gives x([k]P) = ℘(kz₀) where z₀ is the elliptic logarithm of P. The sum becomes:

```
p_1 = Σ_{k=1}^{(ℓ-1)/2} ℘(kz₀) where ℓz₀ ∈ Λ
```

This is a sum of ℘ at arithmetic-progression arguments, all of which are ℓ-division points. There IS a classical identity (Eisenstein series / Hecke operator):

```
Σ_{k=0}^{ℓ-1} ℘(z + kω/ℓ) = ℓ² · ℘(ℓz) + (ℓ²-1) · G₂(Λ)/... 
```

But this sums over ALL ℓ division points of ω (i.e., ℘ at an arithmetic sequence with spacing ω/ℓ), not over multiples of a fixed z₀. The distinction: {kz₀ : k = 0,...,ℓ-1} is a cyclic subgroup of C/Λ, NOT a coset of the ℓ-torsion lattice (unless z₀ is itself a lattice direction divided by ℓ).

When z₀ = ω₁/ℓ (a specific ℓ-torsion point), then {kz₀ : k = 0,...,ℓ-1} = {kω₁/ℓ : k = 0,...,ℓ-1}, and the classical identity DOES apply:

```
Σ_{k=1}^{ℓ-1} ℘(kω₁/ℓ) = (ℓ²-1)/6 · (π²/ω₁²) · E₂(τ) + corrections
```

But this identity involves:
- E₂(τ) = the WEIGHT-2 EISENSTEIN SERIES of the lattice
- Computing E₂(τ) over F_q (via its p-adic analogue or via counting points) costs... O(√p) via Schoof or O(p^{1/4+ε}) via SEA.

For the isogeny problem, p is fixed (it's the characteristic) and ℓ varies. If ℓ ≪ p, then the "Eisenstein series" quantities are FIXED for the given curve E. Computing them once in O(poly(log p)) via Schoof/SEA, then using the identity to get p_1 for any ℓ-torsion subgroup in O(log ℓ), would be a breakthrough.

**BUT**: the identity Σ_{k=1}^{ℓ-1} ℘(kω₁/ℓ) = f(E₂, E₄, E₆, ℓ) gives the sum over ALL points in the cyclic subgroup generated by ω₁/ℓ. Which subgroup this is depends on the CHOICE of lattice basis, which corresponds to a CHOICE of symplectic basis for E[ℓ]. Over F_q, this choice is what distinguishes the different ℓ-isogenies — so the identity would need to "know" which basis element corresponds to P, which is the isogeny computation problem itself.

More concretely: the identity gives Σ x_k over a subgroup specified by a LATTICE DIRECTION, but converting from "torsion point P" to "lattice direction" IS the discrete logarithm in E[ℓ] (finding the Weil pairing coordinates of P relative to a basis). This costs O(ℓ) naively, or O(√ℓ) via BSGS in the ℓ-torsion group.

**Verdict**: Transform methods fail because the map k ↦ x([k]P) has no Fourier structure. Complex-analytic identities (Eisenstein series) exist but their evaluation over F_q either reduces to computing the isogeny (circular) or requires DLP-type computation in E[ℓ] that costs ≥ √ℓ.

---

### Direction 6: Resultant Approach

**Setup**: The codomain j-invariant j' satisfies Φ_ℓ(j(E), j') = 0 where Φ_ℓ is the ℓ-th modular polynomial. This has ℓ+1 roots (one per cyclic subgroup of E[ℓ]).

**Costs**:
- Writing down Φ_ℓ: O(ℓ³ log ℓ) bits (its coefficients are integers of size O(ℓ log ℓ))
- Evaluating Φ_ℓ(j, Y) ∈ F_q[Y]: O(ℓ) operations if Φ_ℓ is precomputed
- Finding all ℓ+1 roots of Φ_ℓ(j, Y): O(ℓ log² ℓ) via fast root-finding

**The matching problem**: Given P ∈ E[ℓ], identify WHICH root j'_i corresponds to E/⟨P⟩.

This requires computing SOME invariant of the pair (E, ⟨P⟩) that distinguishes it from other subgroups. The cheapest known invariant: compute x([2]P) or a small number of multiples of P and match against a list. But distinguishing among ℓ+1 subgroups generically requires information of Ω(log ℓ) bits, and computing this information from P costs Ω(1) group operations (trivially available). The problem is that COMPUTING the distinguishing information from the ROOTS of Φ_ℓ(j, Y) = 0 still requires some form of kernel computation.

**Alternative**: Use the ISOGENY VOLCANO structure. If E is ordinary with CM discriminant D, the volcano structure of the ℓ-isogeny graph gives:
- 0, 1, or 2 "ascending" directions (toward lower level)
- ℓ-1 or ℓ "horizontal/descending" directions

Distinguishing the level can be done in O(poly(log p)) via Frobenius computations. But distinguishing AMONG horizontal neighbors still requires kernel information.

**Key obstruction**: Even with Φ_ℓ precomputed, identifying the correct root requires Ω(√ℓ) computation to match P to a specific isogeny class representative.

**Could a "modular unit" approach help?** A modular unit on X₀(ℓ) is a rational function u that separates the ℓ+1 sheets. If u can be evaluated at (E, ⟨P⟩) in O(log ℓ) operations, then matching the root costs O(log ℓ). But:
- Modular units on X₀(ℓ) are products of SIEGEL UNITS, which involve values of the Weierstrass σ-function at torsion points
- Evaluating a Siegel unit at (E, ⟨P⟩) requires computing σ-values at kernel points, which costs O(ℓ) naively or O(√ℓ) via BSGS
- No sub-√ℓ evaluation of modular units at CM points is known

**Verdict**: The resultant/modular polynomial approach gives O(ℓ³) precomputation, O(ℓ) online computation for root-finding, and O(√ℓ) for matching. The matching step is the bottleneck and cannot obviously be made sub-√ℓ.

---

## 4. The Fundamental Structural Barrier

All six directions fail for the SAME underlying reason:

> **The elliptic curve group law is a degree-2 (quadratic) algebraic map, and no known algebraic technique computes cumulative sums/products along a quadratic orbit in sub-√N time.**

Formally:

Let φ: V → V be a degree-2 rational self-map of a variety V, and let f: V → F_q be a rational function. Define:
```
S_N = Σ_{k=1}^{N} f(φ^{(k)}(P₀))
```
where φ^{(k)} denotes k-fold iteration.

**If φ were LINEAR** (degree 1): then (f(φ^k(P₀)))_k satisfies a linear recurrence of bounded width w, and S_N can be computed in O(w³ log N) via matrix exponentiation of the augmented state (state + running sum).

**If φ is QUADRATIC** (degree 2): the sequence (f(φ^k(P₀)))_k satisfies NO linear recurrence of bounded width. The "state" grows with k (or the recurrence width equals N). No matrix-exponential trick applies.

**Best known for quadratic maps**: BSGS decomposition gives O(√N). Write k = ib + j with b ≈ √N. Precompute {φ^j(P₀) : j = 1,...,b} (cost O(b) = O(√N)). For each giant step i, compute the relevant function via polynomial methods at cost O(b log b) amortized. Total: O(√N · poly(log N)).

**This is a META-THEOREM**: for ANY problem requiring a sum over the orbit of a degree-2 map, BSGS gives √N, and no better algebraic method is known.

### Why is this NOT a proven lower bound?

Because algebraic complexity lower bounds are notoriously hard to prove. We cannot rule out:

1. An algebraic IDENTITY that expresses S_N as a CLOSED FORM in terms of (E, P, N) using only O(log N) operations. Such an identity would need to "shortcut" the quadratic iteration via some unknown structural property.

2. A NUMBER-THEORETIC shortcut specific to elliptic curves that uses the special geometry of the curve (e.g., its connection to modular forms, L-functions, Galois representations).

3. A QUANTUM algorithm that exploits superposition over the kernel.

None of these is known to exist, but none is PROVEN impossible.

---

## 5. The One Speculative Path: Closed-Form Codomain via Modular Forms

### The conjecture (speculative, status: unverified)

**H_closed**: There exists a closed-form expression for j(E/⟨P⟩) in terms of j(E), x(P), and the first O(1) DERIVATIVES of the j-function at E, computable in O(poly(log ℓ)) field operations.

**Why it might be true**: Over C, the codomain j-invariant j' = j(E/⟨P⟩) is a VALUE of a modular function. Specifically:

j' = j(τ/ℓ) where τ = elliptic logarithm of the lattice direction corresponding to ⟨P⟩.

The q-expansion j(τ/ℓ) = 1/q^{1/ℓ} + 744 + ... involves ℓ-th roots of q = e^{2πiτ}. If the first few terms of this expansion suffice (they don't — it's an infinite series), or if a MODULAR EQUATION gives j' as an algebraic function of j and some "invariant of P" computable in O(log ℓ) time, then sub-√ℓ would follow.

**Why it's almost certainly false**: The modular equation relating j and j' IS Φ_ℓ(j, j') = 0, which has degree ℓ+1. Resolving which branch requires information about P that encodes Ω(log ℓ) bits. Extracting this information from P naively costs Ω(log ℓ) group operations (trivially achievable), but MATCHING it to the correct root of Φ_ℓ requires the isogeny computation (circular).

More critically: if H_closed were true, then we could compute ALL ℓ+1 isogenous j-invariants from j in O(ℓ · poly(log ℓ)) total. But computing them via root-finding on Φ_ℓ already costs O(ℓ log² ℓ) — so H_closed would only improve the INDIVIDUAL isogeny case (given a specific kernel generator), not the batch case.

**Known progress in this direction**: NONE. The Weber/Schläfli modular functions reduce the coefficient size of Φ_ℓ (giving smaller modular polynomials [KN-LIT-7613]) but do not change the degree (still ℓ+1). No closed-form evaluation of a single ℓ-isogeny below O(√ℓ) is known.

---

## 6. Implications for the Wesolowski/SSI Program

From `b1_3_test.md` in this batch, the isogeny computation cost directly controls:

| Isogeny cost exponent κ | Wesolowski total at NIST-I | Improvement over VW 2^128? |
|--------------------------|---------------------------|----------------------------|
| κ = 1 (Vélu)            | 2^{128.5}                 | None                       |
| κ = 1/2 (√élu)          | 2^{107.1}                 | Yes (≈20 bits)             |
| κ = 1/3 (hypothetical)  | 2^{95.0} (estimate)       | Yes (≈33 bits)             |
| κ = 1/4 (hypothetical)  | 2^{90.3} (estimate)       | Yes (≈38 bits)             |
| κ = 0 (free oracle)     | 2^{85.8}                  | Yes (≈42 bits)             |

**The cascade effect**: In Wesolowski's algorithm with smoothness bound B, the total cost is approximately:
```
Total ≈ p^{1/3} × B^κ × u^u (where u = log X / log B, X = (p/2)^{1/6})
```

Any reduction in κ below 1/2 gives a DIRECT improvement in the total attack cost. At κ = 1/3, the attack cost drops by ~12 bits. At κ = 1/4, by ~17 bits.

**For the quantum (Grover) setting**:
- Oracle cost per query: ℓ^κ
- Grover queries: O(1/√(success_prob))
- At κ < 1/2: the quantum oracle becomes cheaper, improving the total
- At κ = 0: the quantum attack reaches p^{1/6} (the lower bound)

---

## 7. What Would Constitute a Genuine Breakthrough

A sub-√ℓ algorithm would require ONE of:

### 7A. A linear-algebraic encoding of the kernel sum
Find a matrix M ∈ F_q^{w×w} of bounded dimension w = O(poly(log ℓ)) such that:
```
p_j = [initial vector] · M^ℓ · [extraction vector]
```
This would give O(w³ log ℓ) = O(poly(log ℓ)) computation. It requires "linearizing" the degree-2 group law into a bounded-width linear recursion — essentially finding a finite-dimensional representation of the Vélu sum. No such representation is known.

### 7B. A number-field identity
An identity expressing j(E/⟨P⟩) as a RATIONAL FUNCTION of j(E), x(P), y(P), and a bounded number of "modular invariants" computable from E alone (like a_p, the trace of Frobenius, or higher-weight modular forms).

### 7C. A p-adic/crystalline shortcut  
Computing the kernel sum via p-adic analysis (Kedlaya-style) or crystalline cohomology. The kernel sum Σ x_k is a "period" of the isogenous curve, and periods are sometimes computable via cohomological methods in O(p^{1/2+ε}) — but this depends on p, not ℓ. For ℓ ≪ p, this gives no improvement.

### 7D. Amortized sub-√ℓ over many isogenies
If we need to compute MANY ℓ-isogenies from the SAME curve E (to different subgroups), precomputation on E might amortize the cost. Example: precompute the full ℓ-torsion E[ℓ] in O(ℓ²) time, then each individual isogeny from E costs O(ℓ) via Vélu or O(√ℓ) via √élu. No amortized sub-√ℓ is known even in this batch setting.

### 7E. A randomized algorithm with expected sub-√ℓ
Allow randomization: pick random elements and check if they help. Example: the birthday paradox in a sum of random contributions. But the kernel sum is DETERMINISTIC (given E and P), not probabilistic. Randomization might help with the polynomial arithmetic (e.g., Monte Carlo multi-point evaluation) but known randomized algorithms still cost Ω(√ℓ).

---

## 8. Formal Status and Open Questions

### What is PROVEN:
- √élu achieves O(√ℓ · poly(log ℓ)): **proven** [KN-LIT-764]
- Classical Vélu is O(ℓ): **proven** (Vélu 1971)
- The modular polynomial Φ_ℓ requires Ω(ℓ²) bits to write down: **proven** (coefficient growth)
- Radical isogenies give O(ℓ) per isogeny with small constant: **proven** [KN-LIT-1291]
- Theta-based methods give O(ℓ log ℓ) for g=1: **proven** [KN-LIT-3789]

### What is NOT proven (open questions):
1. **Is there an Ω(√ℓ) lower bound** for computing j(E/⟨P⟩) given (E, P) in the algebraic computation tree model? **OPEN.**
2. **Does a sub-√ℓ algorithm exist** for computing the codomain j-invariant? **OPEN.**
3. **Is there a closed-form expression** for j(E/⟨P⟩) of bounded algebraic complexity? **OPEN (conjectured NO).**
4. **Can the Lubicz-Robert theta-function approach** be made sub-linear for g=1? **OPEN (believed NO for g=1, their advance is for g≥2).**

### Lower bound evidence (not proof):
- The generic group model (GGM) does not directly apply here (we're computing a function, not solving a search problem), but the GGM philosophy suggests that exploiting the group law requires "touching" Ω(√N) elements.
- The ECDLP hardness assumption IMPLIES that the map k ↦ x([k]P) cannot be "inverted" or "summarized" efficiently. If Σ x([k]P) could be computed in sub-√ℓ, it's not immediately clear this breaks ECDLP — the sum is a LOSSY compression of the orbit. But it IS a non-trivial function of the orbit that "sees" all elements.
- Information-theoretic: the output j' has O(log q) bits, which is independent of ℓ. So there's no OUTPUT-SIZE lower bound preventing O(log ℓ). The barrier must be COMPUTATIONAL, not information-theoretic.

---

## 9. Conclusion

**Is sub-√ℓ POSSIBLE with a concrete algorithm?**

NO concrete algorithm achieving sub-√ℓ is known. Every approach I have analyzed (six directions plus variants) hits the same structural wall: the quadratic nonlinearity of the group law prevents algebraic acceleration beyond BSGS.

**Is √ℓ provably optimal?**

NO. There is no proven Ω(√ℓ) lower bound. The question is formally OPEN. The absence of a lower bound means sub-√ℓ is not ruled out — merely that no one has found a way past the barrier in 5 years since √élu, despite strong incentives (it would improve every isogeny-based cryptosystem's parameter estimates).

**Strongest statement I can make**: √ℓ is optimal WITHIN the class of algorithms that:
1. Decompose the kernel sum via BSGS on the cyclic group structure, AND
2. Use polynomial arithmetic (multi-point evaluation, subproduct trees) to batch the computation.

Beating √ℓ requires escaping BOTH (1) and (2) simultaneously — either finding a non-BSGS decomposition of the kernel sum, or finding a non-polynomial-arithmetic batch method. No known mathematical object provides either escape.

**Research priority assessment**: A genuine sub-√ℓ algorithm would be a MAJOR result in computational algebraic geometry (comparable to Schoof's algorithm for point-counting). It would cascade into improved isogeny path-finding (via Wesolowski), improved CSIDH parameters, and potentially affect post-quantum security estimates. Given the difficulty and the absence of even partial progress in 5 years, the recommended approach is:

1. **Document the barrier formally** as an open conjecture: "Conjecture: computing j(E/⟨P⟩) from (E, P) requires Ω(√ℓ) algebraic operations in F_q for generic E."
2. **Monitor for external ingredients** (new identities in modular form theory, new algebraic complexity results for quadratic iterations, advances in p-adic cohomology for elliptic curves).
3. **Do NOT invest significant compute** in empirical approaches — this is a STRUCTURAL question about algebraic complexity, not an experimental one.
4. **The Wesolowski algorithm's performance ceiling** at the current κ = 1/2 (√élu) should be treated as FIXED for security estimation purposes.

---

## 10. Pareto Position and SOTA Delta

| Attribute | This analysis | SOTA |
|-----------|--------------|------|
| Best known single-ℓ-isogeny | O(√ℓ · poly log) | √élu [KN-LIT-764] |
| Lower bound | Ω(1) (trivial) | No non-trivial lower bound known |
| Impact of sub-√ℓ on SSI | κ < 1/2 → attack costs drop ~10-40 bits | κ = 1/2 is current ceiling |

**dominated_by**: null (this is the frontier — no algorithm dominates √élu for single large-prime isogenies)  
**sota_delta**: 0 (no improvement proposed; analysis concludes the barrier is structural)  

---

## References

- [KN-LIT-764] Bernstein, De Feo, Leroux, Smith. "Faster computation of isogenies of large prime degree." 2020.
- [KN-LIT-780] Adj, Chi-Domínguez. "Karatsuba-based square-root Vélu's formulas." 2020.
- [KN-LIT-1237] Cai, Chen. "Faster algorithms for isogeny computations over extensions." 2024.
- [KN-LIT-1291] Decru. "Radical √N élu isogeny formulae." 2024.
- [KN-LIT-3789] Lubicz, Robert. "Fast change of level and applications to isogenies."
- [KN-LIT-129] Chavez-Saab et al. "The SQALE of CSIDH." 2022.
- [KN-LIT-1378] Stange. "Division polynomials for arbitrary isogenies." 2025.
- [KN-TECH-009] Elliptic nets and EDS (program knowledge entry).
- [KN-TECH-057] Full-cost matched baselines for classical supersingular path-finding.
