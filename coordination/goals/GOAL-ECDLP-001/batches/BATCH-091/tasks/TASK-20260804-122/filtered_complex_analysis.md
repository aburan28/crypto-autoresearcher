# Filtered / Alternative Complex Analysis
## TASK-20260804-122 | BATCH-091 | GOAL-ECDLP-001

**Role:** Mathematical Analyst  
**Input decision:** DEC-20260804-b8d7be (BATCH-090 closure of Discrete Morse / ECDLP-IDEA-073)  
**Date:** 2026-08-04

---

## 1. Starting Point

DEC-20260804-b8d7be identified two independent obstructions to ECDLP-IDEA-073 (Algebraic
Discrete Morse), but also flagged a positive structural observation:

> The discrete Morse approach is the FIRST mechanism studied that genuinely avoids DL
> circularity — it operates purely combinatorially on the EC group law without algebraic
> characters.

The BATCH-091 mandate is therefore: can a filtered or alternative complex structure
circumvent the Betti number floor while retaining the combinatorial (non-DL) character?

---

## 2. The Betti Number Floor — Precise Statement

Let E be an elliptic curve over F_p, N = |E(F_p)|, F ⊂ E(F_p) a factor base with |F| = B.
Fix a target R ∈ E(F_p).

Define the "all 2-tuples" chain complex C_R:
- C_0 = {R} (one vertex)
- C_1 = F (1-cell per factor-base element, boundary ∂P = R − P − P = ... see below)
- C_2 = {(P_1, P_2) ∈ F × F : P_1 + P_2 = R} (2-cells)

The boundary map ∂: C_2 → C_1 sends (P_1, P_2) ↦ P_1 − P_2 (the "difference" 1-chain).
By the rank-nullity theorem:

    β_1 = dim ker(∂_1: C_1 → C_0) − rank(∂_2: C_2 → C_1)
         ≥ B − rank(∂_2)
         ≥ B − |C_2|
         = B − r_2(R)

where r_2(R) = |{(P_1,P_2) ∈ F×F : P_1+P_2=R}|. For generic R and a random factor base,
r_2(R) ≈ B²/N, so:

    β_1 ≥ B − B²/N

For the index-calculus regime B = Θ(√N): B²/N = Θ(1), and β_1 = Θ(B) = Θ(√N).
For B >> √N: β_1 ≈ B >> √N. In either case β_1 ≥ Ω(√N).

The Discrete Morse inequality gives: #{critical 1-cells} ≥ β_1 ≥ Ω(√N). Not sub-rho.

---

## 3. Analysis of Alternative Complex Structures

### 3.1 Quotient Complex (negation orbits)

Replace F with the quotient F/{±1}, so the 1-skeleton has size ⌈B/2⌉. A 2-cell
(P, Q) with P + Q = R becomes a 2-cell ({P}, {Q}) in the quotient.

Effect on Betti number: the quotient has B' = B/2 vertices and r'_2(R) ≈ B²/(2N) edges.

    β_1(quotient) ≥ B/2 − B²/(2N)

This is B/2 in the index-calculus regime — exactly half the original bound. The order of
magnitude is unchanged: β_1 = Θ(√N). The factor-of-2 saving is not asymptotically meaningful.

**Verdict: No improvement.**

### 3.2 Symmetric Product Complex

Replace ordered pairs (P_1, P_2) with unordered multisets {P_1, P_2}.

    |Sym²(F)| = B(B+1)/2

r²_sym(R) = #{unordered pairs} ≈ B²/(4N) for generic R (half the ordered count, ignoring
P_1 = P_2 = R/2 cases, which require char ≠ 2 and contribute at most one extra cell).

The Betti number analysis is the same (the chain complex is isomorphic to the quotient by
ℤ/2 acting on C_2), so β_1(Sym²) ≈ B/2 in the same regime. **No asymptotic improvement.**

### 3.3 Nerve of a Cover by Cosets

If N = |E(F_p)| has a small prime factor q | N, we can cover E by cosets of the unique
subgroup H of order N/q. Each coset has size q and there are N/q cosets. The nerve of this
cover is a simplicial complex whose Betti numbers reflect how factor-base elements distribute
across cosets.

For N prime (the standard cryptographic case), E has no proper non-trivial subgroups
(by Lagrange). The only subgroups are {O} and E itself, so no useful coset cover exists.

**Verdict: Fails for prime-order curves, which are the cryptographically relevant case.**

### 3.4 Filtered Complex / Persistent Homology

Introduce a filtration by a function f: E(F_p) → ℝ measuring "distance" or "progress"
toward R (e.g., a discrete height function or a ranking by affine x-coordinate).

Define F_t = {P ∈ F : f(P) ≤ t} and let C_R(t) be the sub-complex of C_R with 1-cells
from F_t and 2-cells from F_t × F_t. This yields a filtered complex

    C_R(t_0) ⊆ C_R(t_1) ⊆ ⋯ ⊆ C_R = C_R(t_max).

**Persistent β_1:** A 1-homology class born at level t and dying at level t' contributes
to bar (t, t'). We would like: few bars of long persistence (those born early and dying late).

However:

(a) **The total β_1 bound is unchanged.** Persistent homology can redistribute β_1 across
filtration levels but cannot reduce the total rank of H_1(C_R). The total count of bars
(of any length) equals β_1(C_R) ≥ Ω(√N). Persistence does not annihilate homology.

(b) **Long-persistence bars correspond to "essential" obstructions.** If we threshold on
bars with persistence > Δ, we discard only short-lived bars. But the number of long
bars depends on the structure of F under f — a priori it could still be Ω(√N).

(c) **f itself cannot be chosen adversarially to collapse β_1.** Any function f that
concentrates many decompositions of R at low levels will also create many 1-cycles early
(since r_2(R) births are accompanied by births of potential 1-cycles). The tension is
intrinsic: more decompositions → more 2-cells → more potential cancellations of 1-cycles,
but only rank(∂_2) of them are cancelled, and rank(∂_2) ≤ r_2(R) ≈ B²/N.

**Verdict: Persistence redistributes but does not reduce the β_1 floor. Same asymptotic.**

### 3.5 Non-Uniform / Selected Sub-complex

Replace F with a carefully chosen subset S ⊂ F with |S| = N^γ for some γ < 1/2.

The Betti number of C_R restricted to S satisfies:

    β_1(C_R|_S) ≥ |S| − r_2^S(R)

where r_2^S(R) = |{(P_1,P_2) ∈ S×S : P_1+P_2=R}|.

For β_1 < √N we need |S| − r_2^S(R) < √N, i.e., r_2^S(R) > |S| − √N ≈ |S|.

So we need r_2^S(R) = Θ(|S|), meaning almost every element of S participates in a
decomposition of R. This requires |S|²/N = Θ(|S|/1), i.e., |S| = Θ(N). But we
assumed |S| = N^γ < √N = N^{1/2}. Contradiction.

**Unless S has highly structured additive density.** The yield is

    yield(S, R) = r_2^S(R) / |S|.

For a random set S with |S| = N^γ, yield ≈ |S|/N = N^{γ−1} → 0. For yield = Θ(1)
we need the additive energy E(S, S) = Σ_R r_2^S(R)² to be >> |S|³/N. By the
Cauchy-Schwarz bound:

    E(S,S) ≥ |S|^4 / N   (trivial lower bound from averaging)

For E(S,S) >> |S|³, we need |S|^4/N >> |S|³, i.e., |S| >> N. This contradicts |S| = N^γ < N.

**Conclusion:** A random or typical set S with |S| = N^γ < √N cannot have yield = Θ(1).
A set with yield = Θ(1) at sub-√N size must possess **extraordinary additive structure**:
E(S,S) = Ω(|S|^3), which is the maximum possible (achieved only by arithmetic progressions
or structured cosets — structures not known to exist in EC point sets without DL).

---

## 4. The Fundamental Tension: Formal Statement

**Claim (Betti–Yield Duality):** For any chain complex C_R built from a subset S ⊂ E(F_p)
as 1-skeleton, exactly one of the following holds:

(A) β_1(C_R) ≥ Ω(√N) for generic R (complex is NOT sub-rho), OR  
(B) r_2^S(R) = 0 for generic R (most targets have NO decomposition — complex is USELESS).

**Proof sketch:** The boundary map ∂_2: C_2(S,R) → C_1(S) satisfies rank(∂_2) ≤ r_2^S(R).
So β_1 ≥ |S| − r_2^S(R). If β_1 < √N then r_2^S(R) > |S| − √N. For this to hold for
generic R, we need the average of r_2^S(R) over R to satisfy

    ⟨r_2^S⟩ = |S|²/N > |S| − √N.

This forces |S|²/N > |S| − √N, i.e., |S|(|S|/N − 1) > −√N, i.e., |S|(1 − |S|/N) < √N.

For |S| ≤ N/2: 1 − |S|/N ≥ 1/2, so |S|/2 < √N → |S| < 2√N. Thus ANY set of size
|S| = Ω(√N) satisfies β_1 = Ω(√N) by this argument.

The regime |S| = o(√N) escapes this bound but then ⟨r_2^S⟩ = |S|²/N → 0, so generic R
has no S-decomposition. □

**Corollary:** Sub-rho complex utility requires |S| = o(√N) AND concentrated decompositions,
i.e., structured additive density in S — precisely the H-PSEUDO hypothesis.

---

## 5. Reduction to H-PSEUDO

H-PSEUDO asks: Does there exist a set S ⊂ E(F_p) with |S| = N^γ (γ < 1/2) such that
the fraction of targets R ∈ E(F_p) with r_2^S(R) ≥ 1 is ω(N^{γ−1/2})? Equivalently,
does there exist a sub-√N factor base that yields decompositions for a super-random fraction
of targets?

The analysis of §3–4 shows:

**Every filtered or alternative complex approach that:**
1. Avoids DL circularity (uses only the group law combinatorially), AND
2. Claims β_1 < √N for generic R,

**must implicitly use a factor base S with yield exceeding the random-set baseline** —
which is exactly what H-PSEUDO posits. In other words:

> Any combinatorial complex that breaks the Betti floor must be built from a factor base
> that witnesses H-PSEUDO. If H-PSEUDO is false (no such structured sets exist), the
> Betti floor is insurmountable for all combinatorial complexes.

The converse also holds: **if H-PSEUDO is true**, then there exists S with r_2^S(R) = Θ(|S|)
for a sub-rho set of targets, and one can build a complex with β_1 < √N for those targets.
The complex approach is then not vacuous — but the hard step is finding/constructing S.

---

## 6. What Would Bypass Both Obstructions?

To simultaneously avoid DL circularity AND achieve β_1 < √N, one would need:

**Option A:** Prove H-PSEUDO true, construct S explicitly, and build the complex over S.
The Discrete Morse argument then gives a sub-rho critical complex — for targets that have
S-decompositions. This is a conditional sub-rho algorithm, conditioned on H-PSEUDO.

**Option B:** Find a NEW chain complex structure for ECDLP where the chain groups are not
"decompositions of R" but some algebraically distinct relation, such that:
- The boundary map has a different null-space structure (rank closer to dim C_1), AND
- The complex still encodes useful information about DL(R).

No such complex is currently known. Candidates would need to connect E(F_p) topology to
DL structure through a non-decomposition encoding.

**Option C:** A structural theorem showing EC point sets necessarily contain structured
subsets — i.e., proving H-PSEUDO from first principles using EC arithmetic. This would
constitute a genuine breakthrough: it would give both the sub-rho complex AND the
combinatorial DL algorithm simultaneously.

---

## 7. Conclusion

**The Betti number floor reduces exactly to H-PSEUDO.**

Specifically:

1. Every alternative complex structure examined (quotient, symmetric product, coset nerve,
   filtered/persistence, non-uniform sub-complex) either:
   (a) leaves β_1 = Ω(√N) unchanged, or
   (b) requires a factor base with structured additive density — which is the H-PSEUDO
       conjecture.

2. The Betti–Yield Duality (§4) shows this reduction is sharp: no combinatorial complex
   over a "generic" sub-√N factor base achieves β_1 < √N while remaining useful (yield > 0).

3. Therefore: **the Discrete Morse avenue is not blocked by an ad-hoc obstruction; it is
   blocked by the same structured-density question that gates all sub-rho approaches.**
   The positive observation from BATCH-090 (avoidance of DL circularity) is preserved —
   combinatorial approaches remain strictly cleaner than character-sum approaches — but
   the Betti obstruction is a hard wall unless H-PSEUDO holds.

4. **Recommended research state:** The filtered/alternative complex analysis closes the
   "workaround" question for ECDLP-IDEA-073. The combinatorial lane reduces cleanly to
   H-PSEUDO. Future work should either:
   (a) Make progress on H-PSEUDO directly (structural theorems about EC additive energy),
   (b) Search for a non-decomposition chain complex encoding ECDLP that avoids the Betti
       floor by a genuinely different mechanism, or
   (c) Treat a conditional algorithm (assuming H-PSEUDO) as the deliverable, with an
       explicit falsification plan.

**The filtered complex approach does not close the gap between "avoids DL circularity" and
"achieves sub-rho." It confirms that the gap IS the H-PSEUDO question, stated in its
sharpest combinatorial form.**

---

## References to Prior Records

- **DEC-20260804-b8d7be**: BATCH-090 closure decision for ECDLP-IDEA-073 (Discrete Morse)
- **BATCH-090**: Two obstructions: Betti number floor + chain homotopy lift cost
- **H-PSEUDO**: Standing open hypothesis on structured density in EC factor bases

---

*Analysis completed: 2026-08-04. Author: Mathematical Analyst, TASK-20260804-122.*
