# Quantum Implications of H-PSEUDO + Literature Search

**Task:** TASK-20260804-126  
**Batch:** BATCH-093  
**Goal:** GOAL-ECDLP-001  
**Date:** 2026-08-04  
**Analyst model:** amazon-bedrock/us.anthropic.claude-sonnet-4-6  

---

## Analysis A: Quantum implications

### Setup

H-PSEUDO (the DL pseudorandomness conjecture) asserts that for all k in
[1, p-1], the character sum sum_{j=1}^{B} chi(k * x([j]G)) is bounded by
C * sqrt(B) with C ~ p^{0.079}.  The classical ECDLP lower bound is
Omega(sqrt(p)) generic group operations (KN-TECH-005).  Shor's algorithm
(KN-TECH-037) solves ECDLP quantumly in O(n^3) Toffoli gates for an n-bit
prime field — polynomial time, exponentially faster than classical.

### A1. If H-PSEUDO is FALSE

Suppose there exists k such that |sum_{j=1}^{B} chi(k * x([j]G))| > C * sqrt(B).
This means the sequence x([j]G) mod k is non-uniformly distributed and
displays detectable bias.

**Does this yield a quantum speedup over Shor?**

No. Shor's algorithm already solves ECDLP in polynomial time O(n^3).  A
false H-PSEUDO would be a statement about the Fourier structure of the
x-coordinate sequence, which is a *classical* algebraic property.  Even if
exploitable classically (sub-rho complexity), it does not compose with
quantum amplitude amplification to beat Shor, because:

1. Shor uses the quantum Fourier transform over Z/ord(G)Z directly on the
   group structure — it does not depend on the classical pseudorandomness
   of x-coordinates.
2. A false H-PSEUDO is a classical bias that could in principle be amplified
   classically (yielding a classical sub-rho algorithm).  Quantumly, one
   already has an exponential speedup via Shor; stacking a polynomial
   classical improvement on top of a quantum algorithm does not improve the
   quantum gate complexity below O(n^3).
3. The quantum model already subsumes the classical model.  Any classical
   algorithm running in time T gives a quantum algorithm running in T
   (trivially, by simulating it), so a false H-PSEUDO gives a quantum
   algorithm of time at most O(sqrt(p)) — still dominated by Shor.

**Conclusion:** H-PSEUDO = FALSE gives no new quantum algorithm.  Shor
already provides the optimal quantum attack.

### A2. If H-PSEUDO is TRUE (empirically confirmed, C ~ p^{0.079})

**Quantum query complexity context.**

The standard quantum lower bound for ECDLP (and DLP generally in the generic
group model) is Omega(sqrt(N)) quantum queries, where N = ord(G) ~ p.
This follows from the quantum generic group model (QGGM): even with
superposition oracle access to the group law, any quantum algorithm requires
Omega(sqrt(N)) group-operation queries.  The relevant technique is
KN-LIT-7581 (Foxman-Lombardi-Ma-Nehoran-Wright, 2026), which constructs a
path-recording oracle for arbitrary closed subgroups of U(N), directly
generalising classical lazy-sampling to the quantum setting.

**Does C ~ p^{0.079} tighten the quantum lower bound?**

No, for a structural reason.  H-PSEUDO is a statement about the *classical
Fourier transform* of the indicator function 1_F of the x-coordinate factor
base F = {x([j]G) : j <= B} in F_p.  Specifically:

  hat{1_F}(k) = sum_{x in F} chi_k(x) = sum_{j=1}^{B} chi(k * x([j]G))

The quantum lower bound for ECDLP operates in a completely different model:
it bounds algorithms with *superposition oracle access to the group
operation* (the abstract group oracle), and the bound is proved by showing
the oracle is simulable by a compressed/path-recording oracle.

These are **orthogonal concerns**:

- H-PSEUDO lives in the Fourier analysis of a CLASSICAL sequence in F_p.
  It is a number-theoretic statement about multiplicative characters.
- The quantum lower bound lives in quantum query complexity over an
  ABSTRACT GROUP.  It counts group-law queries, not character sum queries.

A tightening of the quantum lower bound would require showing that the
compressed quantum oracle for E(F_p) learns LESS from each query than a
generic group oracle, due to the concrete F_p structure.  H-PSEUDO says
the opposite: the x-coordinates LOOK pseudorandom (i.e., the group's
concrete representation provides no exploitable bias), which is consistent
with the generic group bound being tight, not looser.

**Does the Fourier structure of 1_F relate to quantum query complexity?**

There is a formal connection in principle: the polynomial method for quantum
query complexity (Beals-Buhrman-Cleve-Mosca-de Wolf) bounds the minimum
degree of a polynomial approximating the Boolean function being computed.
The quantum adversary method (Ambainis) bounds query complexity via a weight
matrix.  Both techniques apply to functions of query answers.

However:

1. ECDLP in the quantum oracle model is formalized as: given oracle access
   to the group law and a target point T, find k such that [k]G = T.  The
   "function being computed" depends on the group structure, not on the
   Fourier expansion of 1_F.
2. The polynomial method lower bounds for ECDLP have not been connected to
   character sums in the literature (per corpus knowledge).  The polynomial
   method applies to Boolean functions on {0,1}^n; adapting it to continuous
   group-law queries requires additional machinery.
3. The measured C ~ p^{0.079} (the L-infinity norm of the DFT of 1_F)
   captures the maximum bias of the x-coordinate sequence modulo p.
   Quantum query complexity lower bounds are about distinguishing oracles,
   not about bias in specific Fourier modes.

**The most one can say:** H-PSEUDO TRUE implies that 1_F is Fourier-flat
(no mode has more than C * sqrt(B) / B amplitude relative to |F|).  In the
quantum polynomial method, if an algorithm must compute a function that
depends on the Fourier coefficient hat{1_F}(k) for some k, then the
polynomial approximation to that function has degree at least
Omega(1 / max_k |hat{1_F}(k)|) = Omega(B / (C * sqrt(B))) = Omega(sqrt(B)/C).
This gives a lower bound of Omega(sqrt(B) / C) queries to the x-coordinate
oracle — but this is not the standard quantum DL oracle, and this bound
is far weaker than the Omega(sqrt(p)) QGGM bound for large B.

**Conclusion:** H-PSEUDO TRUE does not tighten the Omega(sqrt(N)) quantum
lower bound for ECDLP.  The two statements live in separate models
(character-sum Fourier analysis vs. quantum oracle query complexity).

### A3. Summary of quantum implications

| Scenario | Classical implication | Quantum implication |
|---|---|---|
| H-PSEUDO FALSE | Sub-rho classical algorithm may exist | No new quantum speedup; Shor still optimal at O(n^3) |
| H-PSEUDO TRUE (confirmed) | No sub-rho algorithm via known methods | Quantum lower bound Omega(sqrt(N)) unaffected; no tightening |
| C ~ p^{0.079} measured | Fourier bias consistent with pseudorandomness | No direct quantum query complexity consequence |

The key separation: H-PSEUDO is a **classical structural property** of the
x-coordinate sequence.  Quantum algorithms for ECDLP (Shor) bypass the
classical structure entirely by working over the abstract group.

---

## Analysis B: Literature search results

### B1. Search command and results

Command executed:
```
grep -r "additive.energy\|EC.*exponent\|structured.*set.*elliptic\|H-PSEUDO\|DL.*pseudorandom" knowledge/literature/ -l
```

Files matching (14 results):
- KN-LIT-1340.md — "ADDITIVE RIGIDITY FOR x-COORDINATES OF RATIONAL POINTS ON ELLIPTIC CURVES" (Choi, arXiv:2510.03828, 2025)
- KN-LIT-4717.md — "Lifting and Elliptic Curve Discrete Logarithms"
- KN-LIT-47b29b.md — ECDLP result assessment (fragment match)
- KN-LIT-7613.md — modular polynomials (fragment match, not directly relevant)
- KN-LIT-7565.md, KN-LIT-7605.md, KN-LIT-7615.md, KN-LIT-138.md — fragment matches on "ECDLP exponent"
- KN-LIT-2134.md, KN-LIT-3813.md — side channel / ECDSA (not relevant to additive energy)
- KN-LIT-7655.md — radical isogenies (fragment match)
- KN-LIT-4548.md, KN-LIT-102.md, KN-LIT-3005.md — general EC / lattice references

### B2. Directly relevant: KN-LIT-1340

**KN-LIT-1340** (Choi 2025, arXiv:2510.03828) is the only corpus entry that
directly addresses additive structure of x-coordinates on elliptic curves.
Its abstract states:

> "We show that if a d-dimensional proper generalized arithmetic progression
> in Q contains the x-coordinates of rational points on E/Q with positive
> proportion ρ, then the number of such points is bounded by A(E,d,ρ)^r.
> As an application, we obtain restrictions on sets of rational points whose
> x-coordinates have small sumsets or large additive energy."

**Assessment vs. H-PSEUDO:**  
This paper addresses additive rigidity of x-coordinates over Q (characteristic
zero, Mordell-Weil rank r >= 1), not over F_p (prime field, finite group).
The techniques are height theory, gap principles, and spherical code bounds —
none of which directly translate to the finite-field setting of H-PSEUDO.
Moreover, it bounds points in arithmetic progressions, not the character sum
|sum chi(k * x([j]G))| over a DL sequence.  The connection is conceptual
(both study additive structure of EC x-coordinates) but not technically
applicable to H-PSEUDO.

**Caveat (KN-OPEN-3f7a21):** KN-LIT-1340 carries `citation_verified: read`
and notes it was generated from the "first two pages" during the 2026-07-24
bulk seeding pass.  Per KN-OPEN-3f7a21, 97% of corpus entries are at this
level; `downloads/` never existed in the repository.  The abstract-level
claim above is relayed from the seeded text and has not been independently
verified against the full paper.

### B3. No papers found on H-PSEUDO or structured EC additive energy in F_p

No corpus entry mentions:
- "H-PSEUDO" (an internal program-specific label)
- "DL pseudorandom" in the sense of the DL character sum bound
- Fourier transform of the indicator 1_F for EC x-coordinates in F_p
- EC additive energy E(F,F) for factor bases in F_p

This absence is expected: H-PSEUDO was identified in this research program
(BATCH-073..079) as a new open question.  It is unlikely to appear by name
in external literature.

**Absence is not definitive** (per KN-OPEN-3f7a21): the corpus covers
approximately 7666 entries at abstract-seed level, with no verified backing
artifacts.  Papers specifically addressing E(F,F) for EC factor bases in F_p
may exist in the 2024-2026 arXiv/ePrint literature and simply not be indexed
here.

### B4. Related areas not in corpus

The following areas are adjacent to H-PSEUDO but not currently indexed:

1. **EC exponential sum bounds over F_p**: The literature on
   |sum_{x in S} chi(f(x))| for structured sets S on curves over F_p
   (e.g., Shparlinski's work on exponential sums on curves, or
   Korobov-type bounds for multiplicative characters on EC x-coordinates).
   This is the closest existing body of work to H-PSEUDO.

2. **Additive combinatorics in F_p for EC points**: Sum-product theory
   applied to EC x-coordinate sets (Bourgain-Katz-Tao style results in F_p,
   or Shkredov's additive energy bounds for multiplicative subgroups).

3. **Pseudorandomness of DL sequences**: Friedlander-Shparlinski-type
   results on the distribution of x([j]G) mod k; these directly address the
   character sum in H-PSEUDO but for the standard DLP sequence, not
   necessarily for the small-B factor-base regime.

These represent potential literature directions if the corpus is expanded.

---

## Conclusion: Any new direction identified?

### Quantum (Analysis A)

**No new direction from quantum theory.**  The quantum landscape is fully
characterised:

- H-PSEUDO is independent of Shor's algorithm in both the TRUE and FALSE cases.
- The Omega(sqrt(N)) quantum lower bound (QGGM) is not tightened by H-PSEUDO.
- The Fourier structure of 1_F does not directly bear on quantum query
  complexity lower bounds for ECDLP in the standard oracle models.
- C ~ p^{0.079} is a classical number-theoretic quantity with no known
  quantum complexity interpretation.

The classical and quantum ECDLP problems sit in structurally different
regimes: H-PSEUDO is the exact condition for classical sub-rho; Shor bypasses
classical structure entirely.

### Literature (Analysis B)

**One potentially relevant paper, one direction for expanded search.**

1. KN-LIT-1340 (Choi 2025) addresses additive rigidity of EC x-coordinates
   over Q, not F_p.  It is conceptually related but not technically
   applicable to H-PSEUDO as stated.  **Action:** If the corpus is expanded,
   the full paper (arXiv:2510.03828) should be read for techniques that may
   adapt to the finite-field setting.

2. **Exponential sum bounds for EC x-coordinate sequences over F_p**
   (Shparlinski-type) is the most likely place where partial results on
   H-PSEUDO-type bounds exist.  Searching the arXiv for
   "exponential sums elliptic curve x-coordinates" or
   "character sums elliptic curve factor base" could identify relevant
   2024-2026 papers not in the current corpus.

### Net verdict for BATCH-093

Both analyses confirm that no new technical direction emerges from quantum
theory or the current literature corpus.  The open problem H-PSEUDO remains
the program's central question.  The most productive next step identified
here is a targeted literature expansion: search arXiv/ePrint for EC
exponential sum papers that bound character sums over small-B EC x-coordinate
sets, which is the closest technical neighbourhood of H-PSEUDO not currently
covered by the corpus.

**Corpus integrity caveat:** All negative corpus results carry the
KN-OPEN-3f7a21 qualification — absence is not proof of absence.

---

*Analyst note: This analysis is conducted under the executor-mechanical role.
No new ECDLP claim is made.  All statements about quantum lower bounds are
standard results cited from KN-TECH-005, KN-TECH-037, and KN-LIT-7581.
The corpus search results are factual observations against the indexed tree.*
