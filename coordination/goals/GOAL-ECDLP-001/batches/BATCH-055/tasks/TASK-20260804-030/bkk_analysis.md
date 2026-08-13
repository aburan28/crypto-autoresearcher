# BKK Analysis: Newton Polytope & Mixed Volume for Semaev S\_3

**Task:** TASK-20260804-030  
**Batch:** BATCH-055  
**Goal:** GOAL-ECDLP-001  
**Executor:** amazon-bedrock/us.anthropic.claude-sonnet-4-6  
**Date:** 2026-08-04  
**Git commit at execution:** cf6ef1cb57899bced9dbac5c41fa28c061d1057f  
**Computation runtime:** SageMath 10.9 (Python 3.14)

---

## 1. Setup

Elliptic curve **E**: y² = x³ + x + 1 over **GF(101)** (and over ℚ for symbolic work).

- Group order: 105 = 3 × 5 × 7
- Valid x-coordinates on E(GF(101)): 52 (the x-values where x³+x+1 is a quadratic residue)

---

## 2. Degree Correction (Task Description Error)

The task description stated:

> S\_m has degree 2^(m−1) in each variable. For m=3: degree 4.

**This is incorrect.** Semaev (2004) proves:

> S\_m(x₁,…,xₘ) has degree **2^(m−2)** in each variable, for m ≥ 2.

| m | Degree per variable | = 2^(m−2) |
|---|---|---|
| 2 | 1 | 2^0 = 1 ✓ (S₂ = x₁ − x₂) |
| 3 | 2 | 2^1 = 2 ✓ (computed below) |
| 4 | 4 | 2^2 = 4 |
| 7 | 32 | 2^5 = 32 |

---

## 3. Explicit S\_3 for y² = x³ + x + 1

**Derivation.** From the Weierstrass addition law, P₁+P₂+P₃ = O requires
(y₂−y₁)² = (x₃+x₁+x₂)(x₂−x₁)². Eliminating y₁,y₂ via y_i² = x_i³+x_i+1 and squaring yields a candidate polynomial; factoring over ℚ gives:

```
S₃_candidate = −(x₁−x₂)² · S₃(x₁,x₂,x₃)
```

where **S₃** is the true irreducible summation polynomial.

### Closed Form (a=1, b=1)

Setting e₁ = x₁+x₂+x₃, e₂ = x₁x₂+x₁x₃+x₂x₃, e₃ = x₁x₂x₃:

```
S₃(x₁,x₂,x₃) = e₂² − 4·e₃·e₁ − 2·e₂ − 4·e₁ + 1
```

**Fully expanded:**

```
S₃ = x₁²x₂² + x₁²x₃² + x₂²x₃²
   − 2·x₁²x₂x₃ − 2·x₁x₂²x₃ − 2·x₁x₂x₃²
   − 2·x₁x₂ − 2·x₁x₃ − 2·x₂x₃
   − 4·x₁ − 4·x₂ − 4·x₃
   + 1
```

**Properties:**
- Degree in each variable: **2** (not 4)
- Total degree: **4** (from x₁²x₂² term)
- Number of monomials: **13** (out of 27 in the [0,2]³ box)
- Symmetric: yes (in x₁, x₂, x₃)
- Coefficients: ±1, ±2, −4 (all over ℤ, independent of p)

---

## 4. Newton Polytope of S\_3 (3D)

The **3D Newton polytope** is the convex hull of the 13 exponent vectors:

```
{(0,0,0), (0,0,1), (0,1,0), (0,1,1), (0,2,2),
 (1,0,0), (1,0,1), (1,1,0), (1,1,2), (1,2,1),
 (2,0,2), (2,1,1), (2,2,0)}
```

**Vertices of the Newton polytope (extreme points):**

```
(0,0,0), (0,0,1), (0,1,0), (0,2,2),
(1,0,0), (2,0,2), (2,2,0)
```

- Dimension: 3
- Number of vertices: 7
- Euclidean volume: 14/3 ≈ 4.67
- Normalized volume (3! × Vol): **28**

The polytope does **not** equal the full [0,2]³ cube (which would have 27 lattice points and volume 8); S₃ has 13/27 ≈ 48% of the monomials in the bounding box.

---

## 5. Newton Polytope after Specialization (2D)

Specializing x₃ = c (a constant, representing the target x-coordinate in the index calculus):

```
S₃(x₁,x₂,c) = x₁²x₂²
             − 2c·x₁²x₂ − 2c·x₁x₂²
             + c²·x₁² + c²·x₂²
             − (2c²+2)·x₁x₂
             − (2c+4)·x₁ − (2c+4)·x₂
             + (−4c+1)
```

**Properties of S₃(x₁,x₂,c) for generic c:**
- Degree in x₁: **2**
- Degree in x₂: **2**
- Total degree: **4** (from x₁²x₂² term)
- Number of monomials: **9** (all of (0…2)² = full 2D box)

**2D Newton polytope:**

```
NP₂D = conv{(0,0),(2,0),(0,2),(2,2)} = [0,2]²
```

| Property | Value |
|---|---|
| Dimension | 2 |
| Vertices | (0,0), (2,0), (0,2), (2,2) |
| Lattice points | 9 |
| Euclidean area | 4 |
| Normalized area (2! × Area) | **8** |
| Equals full [0,2]² box? | **YES** |

After specialization, the Newton polytope fills the entire degree-2-per-variable box.

---

## 6. Bezout Bound vs. BKK Bound

The index calculus system for ECDLP relation collection involves the 2-variable system:

```
{S₃(x₁, x₂, c₁) = 0,  S₃(x₁, x₂, c₂) = 0}
```

(find pairs (x₁,x₂) such that, for two distinct target x-coordinates c₁,c₂, appropriate point combinations over E satisfy the group law).

### Bezout Bound (total degree)

Both polynomials have total degree 4:

```
Bezout = d₁ × d₂ = 4 × 4 = 16
```

### BKK Bound (Bernstein–Kushnirenko–Khovanskii)

By the Bernstein theorem, the BKK bound equals the **mixed volume** of the two Newton polytopes. Since both specializations give the same polytope P = [0,2]²:

```
MV(P, P) = Area(P+P) − Area(P) − Area(P)
         = Area([0,4]²) − Area([0,2]²) − Area([0,2]²)
         = 16 − 4 − 4
         = 8
```

Equivalently: MV(P,P) = 2! × Vol(P) = 2 × 4 = **8**.

### Comparison

| Bound | Value | Reference |
|---|---|---|
| Bezout (total degree d=4) | **16** | Bézout's theorem |
| Multi-graded Bezout (deg 2 in each var) | 4 | Not directly applicable here |
| BKK / Mixed Volume | **8** | Bernstein theorem, Newton polytope |

**BKK provides a factor-2 improvement over total-degree Bezout.**

The gain arises because S₃(x₁,x₂,c) is a *bihomogeneous* polynomial (degree 2 in each variable separately), so its Newton polytope is the box [0,2]² rather than the Bézout simplex associated with total degree 4.

---

## 7. Empirical Verification over GF(101)

Brute-force counting of common roots of {S₃(x₁,x₂,c₁)=0, S₃(x₁,x₂,c₂)=0} over GF(101)²:

| c₁ | c₂ | Affine joint roots | Roots with x₁,x₂ on E |
|---|---|---|---|
| 0 | 3 | **2** | **2** |

Sample root: (x₁, x₂) = (5, 74) and its symmetric partner (74, 5).

**Random sampling (20 random valid (c₁,c₂) pairs, seed=42):**
- All 20 pairs produced exactly **2** affine joint roots
- Min = Max = Average = **2**
- All ≤ BKK bound 8? **YES**

### Observations

1. **Actual count (2) ≪ BKK bound (8) ≪ Bezout bound (16).** The BKK bound is not tight for this polynomial system.

2. **Consistent count of 2.** The pair (x₁,x₂) and its symmetric partner (x₂,x₁) always appear together (since S₃ is symmetric). This suggests the affine intersection always consists of exactly one unordered pair {x₁,x₂}. This may follow from the genus-0 structure of the S₃ variety or from the fact that 4 possible point-sums from (x₁,±y₁)+(x₂,±y₂) cover at most 4 distinct target x-values, and generically only 1 pair of targets matches any given (c₁,c₂).

3. **Projective solutions.** There may be additional projective solutions (points at infinity) not counted by the affine brute force; these could bring the total closer to 8. However, the affine count of 2 is the operationally relevant quantity for index calculus over GF(p).

---

## 8. Implications for ECDLP Index Calculus

### Scale-up (from S₃ to S₇)

For the Gaudry (2009) / Faugère–Perret–Spaenlehauer index calculus approach using S_m:

| m | Degree per var | Total deg (after spec.) | Bezout (2-var sys.) | BKK estimate |
|---|---|---|---|---|
| 3 | 2 | 4 | 16 | **8** |
| 4 | 4 | 8 | 64 | **32** |
| 5 | 8 | 16 | 256 | **128** |
| 7 | 32 | 64 | 4096 | **2048** |

The BKK bound is consistently half the total-degree Bezout. For larger systems (m > 3 variables after specialization), the Newton polytope structure may give additional improvement if further sparsity emerges.

### Relation to S₇ for ECDLP over F_p

For p ≈ 2^128, the standard approach uses S_7 (6 unknowns after specializing x₇). The S₇ polynomial has degree 32 in each of 6 variables; the 6-variable system {S₇(x₁,...,x₆,c)=0} defines a (5-dimensional) variety, not a finite point set. The actual complexity is dominated by the Gröbner basis computation of a related system.

The BKK analysis here (for m=3) establishes:
1. The degree formula 2^(m-2) (not 2^(m-1))
2. The Newton polytope fills the full box after specialization (no additional sparsity beyond the bihomogeneous structure)
3. A factor-2 gain over total-degree Bezout from Newton polytope analysis

Whether the same bihomogeneous structure persists for S_7 (giving a factor-2 gain there) requires separate computation.

---

## 9. Summary of Key Findings

| Finding | Value |
|---|---|
| Degree of S₃ in each variable | **2** (formula: 2^(m−2)) |
| Number of monomials of S₃ | **13** (out of 27 in [0,2]³ box) |
| Monomials after x₃-specialization | **9** (full [0,2]² box) |
| Bezout bound for 2-var system | **16** (total degree d=4 each) |
| BKK mixed volume bound | **8** |
| BKK / Bezout ratio | **0.5 (factor-2 improvement)** |
| Empirical affine root count (GF(101)) | **2** (consistent across 20 random samples) |
| BKK bound is tight? | **No** (actual count 2 ≪ BKK = 8) |

**The Newton polytope of S₃(x₁,x₂,c) is the full [0,2]² box.** The BKK bound (8) halves the Bezout bound (16), but the actual solution count over GF(101) is consistently 2, indicating the BKK bound is not tight for this system.

---

## Appendix: Computation Artifacts

**Scripts run:**
- `/Volumes/SSD990/llm/tmp/opencode/bkk_compute.sage` — factorization and degree analysis
- `/Volumes/SSD990/llm/tmp/opencode/bkk_compute2.sage` — Newton polytope and mixed volume
- `/Volumes/SSD990/llm/tmp/opencode/bkk_verify.sage` — empirical root count over GF(101)

**Environment:**
- SageMath 10.9 (2026-05-04), Python 3.14
- Platform: macOS (darwin), aarch64

**Key SageMath computation (factorization):**

```python
# S3_candidate = ((x3+x1+x2)*(x2-x1)^2 - f(x1) - f(x2))^2 - 4*f(x1)*f(x2)
# Factor over QQ:
S3_candidate.factor()
# = -(x1-x2)^2 * (x1^2*x2^2 - 2*x1^2*x2*x3 - 2*x1*x2^2*x3 + x1^2*x3^2
#                  - 2*x1*x2*x3^2 + x2^2*x3^2 - 2*x1*x2 - 2*x1*x3
#                  - 2*x2*x3 - 4*x1 - 4*x2 - 4*x3 + 1)
```

The second factor is S₃. ∎
