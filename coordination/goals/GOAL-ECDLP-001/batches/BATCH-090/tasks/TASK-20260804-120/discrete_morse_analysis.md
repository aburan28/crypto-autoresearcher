# Discrete Morse Analysis: ECDLP-IDEA-073
## TASK-20260804-120 / BATCH-090 / GOAL-ECDLP-001
**Analyst:** Mathematical analyst (BATCH-090)  
**Reviewed against:** DEC-20260804-2158f1 (BATCH-089 decision), ECDLP-IDEA-073

---

## 1. Chain Complex Definition

For fixed m and target R, two formulations appear in the literature. We analyze both and identify which applies to ECDLP-IDEA-073.

### Formulation A — "all m-tuples" complex

- **C_m**: ordered m-tuples (P_1,...,P_m) ∈ F^m with P_1+...+P_m = R. Count: r_m(R) ≈ B^m/N^{m-1}.
- **C_{m-1}**: ALL unconstrained ordered (m-1)-tuples from F. Count: B^{m-1}.
- ...
- **C_1**: all elements of F. Count: B.
- **Boundary**: ∂_j(P_1,...,P_j) = Σ_{i=1}^{j} (−1)^{i−1} (P_1,...,P̂_i,...,P_j).

Only the top group C_m is constrained to sum to R; lower groups are unconstrained. This is a well-defined chain complex (∂^2 = 0).

For m=2 (the task-brief case):

| Group | Generators | Count |
|-------|-----------|-------|
| C_2 | pairs (P_1,P_2) ∈ F^2, P_1+P_2=R | r_2(R) ≈ B^2/N |
| C_1 | elements P ∈ F | B |
| C_0 | (absent or augmented) | — |

### Formulation B — "partial sums toward R" complex

- **C_j** (j < m): j-tuples (P_1,...,P_j) ∈ F^j such that there exist (P_{j+1},...,P_m) ∈ F^{m-j} with P_1+...+P_m = R (i.e., the partial sum can be extended to a complete decomposition of R).
- Cells at every level are "witnesses en route to R."
- Count at level j ≈ B^j × (B^{m-j}/N^{m-j-...}) ≈ B^m/N^{m-1} ≈ r_m(R) for all j ≥ 1.

For m=2:
- |C_2| ≈ B^2/N, |C_1| ≈ B^2/N (each element P ∈ F that appears in any 2-decomposition).
- Euler characteristic: χ = (B^2/N) - (B^2/N) + 1 = 1.

ECDLP-IDEA-073 (lines 3–4, "partial factor-base decompositions...with sum running toward the target") uses **Formulation B**. The task brief's count |C_2| ≈ B^2/N is consistent with this.

---

## 2. Betti Numbers and Morse Inequality Lower Bound

### Formulation B (the correct one for the IDEA)

The m=2 Formulation B complex is **contractible**:
- Every cell is "connected" to R via a chain of partial sums.
- H_0 = Z, H_j = 0 for j ≥ 1.
- Proof: the complex is the "nerve of a cover" of the single point R; contractibility follows from the cone structure at C_0 = {R}.

By the discrete Morse inequality c_j ≥ β_j:
- **Minimum total critical cells: 1** (just the 0-cell {R}).

A perfect Morse function on Formulation B cancels all 1-cells and 2-cells in matched pairs, leaving the single cone point. The critical complex is trivial.

However, this triviality is vacuous: the single critical cell {R} carries no factor-base source information. The chain homotopy that cancelled all other cells encodes the ancestry of every path from R to decompositions, but extracting any one path requires traversing O(r_2(R)) chain-homotopy data — exactly reproducing the cost of direct search.

**The Formulation B complex is contractible by construction. Discrete Morse theory cannot reduce below 1 critical cell, but that cell is useless without the homotopy data.**

### Formulation A (the task-brief's implicit model)

For m=2, ∂_2: C_2 → C_1 sends (P_1,P_2) ↦ P_2 − P_1.

Rank-nullity:
- rank(im ∂_2) = min(r_2(R), B). In the regime r_2(R) ≤ B (which holds whenever B ≥ N^{1/2}, since r_2(R) ≈ B^2/N ≤ B ⟺ B ≤ N), the map is generically injective, so rank(im ∂_2) = r_2(R).

Betti numbers:
```
β_2 = rank(ker ∂_2) = r_2(R) − rank(im ∂_2) = 0  (injective map)
β_1 = rank(C_1) − rank(im ∂_2)  = B − r_2(R)
```

Morse inequality lower bound:
```
c_1 ≥ β_1 = B − r_2(R) ≈ B          (since r_2(R) ≈ B^2/N << B for B < N)
```

**In Formulation A, any acyclic matching must leave at least B − r_2(R) ≈ B critical 1-cells.** Since B ≥ N^{1/2} is required for any decompositions to exist, the critical complex always contains ≥ N^{1/2} cells. Not sub-rho.

---

## 3. Arithmetic Correction: Task Brief Error

The task brief states:

> "For the standard index calculus parameter B = N^{1/2}/log(N) (near-optimal): B^2/N ≈ N/log^2(N) >> sqrt(N)"

This is **arithmetically wrong**. The correct computation:

```
B = N^{1/2}/log N
B^2 = N / log^2 N
B^2 / N = 1 / log^2 N  → 0  as N → ∞
```

Numerical verification (B = N^{1/2}/ln N):

| log_2(N) | B^2/N        | sqrt(N)    |
|----------|-------------|------------|
| 20       | 5.2 × 10^{-3} | 1.0 × 10^3 |
| 40       | 1.3 × 10^{-3} | 1.0 × 10^6 |
| 60       | 5.8 × 10^{-4} | 1.1 × 10^9 |
| 80       | 3.3 × 10^{-4} | 1.1 × 10^{12} |

Far from N/log^2(N): B^2/N = 1/log^2(N) ≪ 1. **With B = N^{1/2}/log N, typical targets have essentially no 2-decomposition.**

The task brief's conclusion that "critical cells ≈ N/log^2 N >> N^{1/2}" rests on this error. The conclusion (approach does not give sub-rho) is **still correct**, but for a different reason.

**Correct analysis by parameter regime (m=2, Formulation A):**

| β | B = N^β | r_2(R) ≈ N^{2β−1} | Critical 1-cells ≈ B | Sub-rho B? | Sub-rho r_2(R)? |
|---|---------|-------------------|---------------------|-----------|----------------|
| 0.50 | N^{1/2} | N^0 ≈ 1 | N^{1/2} | No (boundary) | Yes |
| 0.60 | N^{0.6} | N^{0.2} | N^{0.6} | No | Yes |
| 0.70 | N^{0.7} | N^{0.4} | N^{0.7} | No | Yes |
| 0.75 | N^{0.75} | N^{0.5} | N^{0.75} | No | Boundary |
| 0.80 | N^{0.8} | N^{0.6} | N^{0.8} | No | No |

The critical 1-cell count ≈ B always exceeds N^{1/2} when B > N^{1/2}. The 2-cell count r_2(R) is sub-rho for β < 3/4, but the dominant term in the Morse inequality is β_1 = B − r_2(R) ≈ B.

---

## 4. Does ECDLP-IDEA-073 Avoid the H-PSEUDO/DL Circularity?

**Short answer: Yes — but the avoidance is real yet insufficient.**

### The H-PSEUDO/DL circularity

The H-PSEUDO/DL circularity (as documented in DEC-20260804-2158f1 and prior ledger records) applies to approaches that:
1. Try to exploit structural clustering in the set {R : r(R) > threshold}, and
2. Require knowledge of discrete log values to identify or exploit that clustering.

The circularity: the structure is determined by dlog(F), but finding dlog(F) is the goal.

### Discrete Morse is combinatorial — no dlog used

The Morse matching for C_R is defined using:
- The set F (EC points, no dlog needed)
- The EC group law (computing P_1 + P_2, which is dlog-free)
- A total ordering on F (e.g., by coordinate, dlog-free)

A valid target-independent rule: match (P_1, P_2) ↔ P_1 whenever P_1 precedes P_2 in the fixed ordering on F. This rule is defined entirely without knowledge of any discrete log value.

**Conclusion: The discrete Morse matching genuinely avoids H-PSEUDO/DL circularity.** This is a real and non-trivial distinction from character-sum-based approaches.

### But avoidance does not confer sub-rho complexity

The obstruction to sub-rho is NOT the DL circularity. It is the Betti number floor derived in §2:
- Any acyclic matching on C_R (Formulation A) must leave ≥ β_1 = B − r_2(R) ≈ B critical cells.
- B ≥ N^{1/2} is a necessary condition for any relations to exist (r_2(R) ≥ 1 requires B ≥ N^{1/2}).
- Therefore the critical complex always has ≥ N^{1/2} critical cells.

This obstruction is **topological, not algebraic**. It does not depend on H-PSEUDO, DL circularity, or character sums. It is a consequence of the Morse inequality c_1 ≥ β_1 applied to a complex where C_1 = F has size B.

---

## 5. The Actual Obstructions

Two distinct obstructions block ECDLP-IDEA-073, neither of which is the DL circularity:

### Obstruction 1: Betti number floor (Formulation A)

The dimension-1 Betti number β_1 = B − r_2(R) ≈ B imposes a floor of ≈ B critical 1-cells for any acyclic matching. Since B > N^{1/2} whenever decompositions exist, the critical complex is always super-rho. The matching is not at fault; the complex's topology requires it.

No target-independent matching can reduce C_1 below β_1. The only way to reduce β_1 is to either (a) reduce B below N^{1/2}, which eliminates all decompositions, or (b) increase r_2(R) to near B, which requires B^2/N ≈ B, i.e., B ≈ N — making the factor base the entire group, which is trivially absurd.

### Obstruction 2: Chain homotopy lift cost (Formulation B)

In Formulation B the complex is contractible: perfect Morse reduction yields 1 critical cell. But the chain homotopy data has size Θ(r_m(R)) and recovering one factor-base decomposition requires traversing it fully. The "compression" is illusory: the lifted path through cancelled cells requires traversing as many cells as there are decompositions. Total work per decomposition is still O(r_m(R)) cell operations, which is no better than direct search.

The IDEA itself (line 73–74) identifies a version of Obstruction 2: "one critical class can aggregate exponentially many paths, and lifting it can branch through the entire cancelled complex."

### Obstruction 3: Parameter ceiling (both formulations)

The claim "gamma < 1/2" in the IDEA's hypothesis requires critical-cell count < N^{1/2}. From Obstructions 1 and 2:
- Formulation A: critical cells ≥ B ≥ N^{1/2} (never strictly sub-rho).
- Formulation B: critical cells = 1, but lift cost ≥ r_2(R) (no net gain over direct search).

There is no parameter choice of B and m that gives both sub-rho critical cells AND non-trivial chain homotopy lift at sub-rho cost.

---

## 6. Target-Independence: A Concrete Matching and Its Limitations

To confirm that a target-independent matching can be defined (for thoroughness), consider m=2 with Formulation A:

**Rule**: for each pair (P_1, P_2) ∈ C_2 with P_1 + P_2 = R, match (P_1, P_2) ↔ P_1 if P_1 < P_2 in the fixed ordering on F. The rule uses only the ordering of F — no knowledge of R, no knowledge of dlogs.

- Critical 2-cells: pairs (P_1, P_2) with P_1 ≥ P_2. Count ≈ r_2(R)/2.
- Critical 1-cells: elements P ∈ F that never appear as the smaller element of any decomposition pair. Count ≈ B − r_2(R)/2 ≈ B.

Acyclicity: Each matched pair (P_1, P_2) ↔ P_1 has no directed Morse path back to itself because the matching rule is lexicographic (strict decrease in ordering along any path). This matching is acyclic.

**Result**: This is a valid, computable, target-independent acyclic matching. It achieves approximately β_1 = B − r_2(R) critical 1-cells — the Betti-number minimum. So the matching is optimal. And it still has ≈ B ≥ N^{1/2} critical cells.

**The target-independence of the matching is achievable; the sub-rho claim is not.**

---

## 7. Formal Assessment of the IDEA's Claims

| Claim | Status | Justification |
|-------|--------|---------------|
| Target-independent acyclic matching exists | **Plausible, possibly provable** | Lexicographic rule works; acyclicity argument above. |
| Matching achieves N^{gamma} critical cells, gamma < 1/2 | **False (Formulation A)** | Morse inequality: c_1 ≥ β_1 ≈ B ≥ N^{1/2}. |
| Matching achieves N^{gamma} critical cells, gamma < 1/2 | **Vacuously true but useless (Formulation B)** | Complex is contractible; 1 critical cell; lift cost O(r_m(R)). |
| Chain homotopy lifts critical cells to exact sources at sub-rho cost | **False (both formulations)** | Lift traversal costs O(r_m(R)) per cell (Obstruction 2). |
| Approach avoids H-PSEUDO/DL circularity | **True** | Matching is purely combinatorial, no dlog required. |
| Complete ECDLP solution below rho/BSGS boundary | **False** | Total complexity is ≥ max(B, B^2) = O(B^2) > N^{1/2} for all viable B. |

---

## 8. Verdict

**ECDLP-IDEA-073 genuinely avoids the H-PSEUDO/DL circularity obstruction.** This distinguishes it from prior character-sum-based approaches and is a non-trivial structural observation.

**However, it does not provide a viable path to sub-rho complexity.** Two independent obstructions apply:

1. In the "all m-tuples" (Formulation A) complex: the Betti number floor β_1 ≈ B requires any acyclic matching to leave ≥ B ≥ N^{1/2} critical 1-cells. This is a hard topological lower bound independent of DL circularity or H-PSEUDO.

2. In the "partial sums toward R" (Formulation B) complex: the complex is contractible, giving trivially few critical cells (1), but the chain homotopy lift required to extract a factor-base decomposition from the single critical cell traverses O(r_m(R)) data — no better than direct search.

**No parameter choice of B, m, or matching rule can simultaneously achieve (a) sub-rho critical cells and (b) sub-rho lift cost, in either formulation.**

The IDEA correctly identifies Obstruction 2 in its "Likely fatal obstruction" section (line 73–74). Obstruction 1 (Betti number floor in Formulation A) is an additional, independent reason to reject the approach.

**Recommended action**: Mark ECDLP-IDEA-073 as **disproved on current formulation** with the following forward guidance:
- A new formulation would need to define a chain complex with β_1 = O(N^{1/2−ε}) AND non-trivial source-encoding critical cells. No such construction is evident.
- The observation that combinatorial matchings avoid DL circularity is worth preserving as a positive technique note — it may inform future proposals.
- Do not pursue further implementation until a sub-rho Betti number bound is proved on a concrete complex definition.

---

## 9. Note on the Task Brief's Arithmetic

The task brief claims: "B = N^{1/2}/log N → B^2/N ≈ N/log^2(N) >> sqrt(N)."

This is an error. Correctly: B^2/N = 1/log^2(N) → 0. The task brief's numerical conclusion (approach not sub-rho) is correct, but the arithmetic supporting it is wrong. The correct obstruction argument uses the Betti number floor β_1 ≈ B (§2 and §5 above), not an inflated yield count.

---

*Analysis completed: TASK-20260804-120, BATCH-090.*
