# Extension-Field Semaev vs. Prime-Field H-PSEUDO: Structural Analysis

**Task:** TASK-20260804-130  
**Batch:** BATCH-095  
**Goal:** GOAL-ECDLP-001  
**Date:** 2026-08-04  
**Analyst model:** amazon-bedrock/us.anthropic.claude-sonnet-4-6  

---

## 1. Setup: Two settings, one polynomial family

The Semaev summation polynomial S_m(x_1, ..., x_m) is defined over any field and
characterises m-tuples of EC x-coordinates that sum to zero. The polynomial is the
same in both settings. What differs is the **factor base** chosen and whether that
choice is algebraically describable.

| | Extension-field Semaev | Prime-field Semaev |
|---|---|---|
| Curve | E/F_{p^n}, n >= 2 | E/F_p |
| Factor base | F = {P in E(F_{p^n}) : x(P) in F_p} | F = {P in E(F_p) : x(P) < t} |
| Base condition | x(P)^p = x(P) (Frobenius) | x(P) < t (archimedean) |
| Size of F | ~p | ~p = ~N^{1/n} (relative to N ~ p^n) |
| Algebraic? | **Yes** | **No** |

---

## 2. Why extension-field Semaev works: the Frobenius condition is algebraic

### 2.1 The factor base as an algebraic variety

For E over F_{p^n}, the condition "x(P) lies in F_p" is exactly the Frobenius
fixed-point condition on the x-coordinate:

    x(P) in F_p  <=>  x(P)^p = x(P)  <=>  x(P)^p - x(P) = 0

This is a polynomial equation of degree p in x(P). The locus

    V = {Q in A^1(F_{p^n}) : Q^p - Q = 0}

is an algebraic subvariety of A^1 over F_{p^n} — a union of p points (the elements
of F_p viewed inside F_{p^n}). Its preimage on E is the factor base F:

    F = {P in E(F_{p^n}) : x(P)^p = x(P)}

This is an algebraically-described set. Its size is controlled by the number of
F_{p^n}-rational points on E with x-coordinate in V: approximately 2p ~ 2 * N^{1/n}.

### 2.2 Yield analysis via the Frobenius structure

The yield probability for the m-sum decomposition Q = P_1 + ... + P_m with P_i in F
is, heuristically:

    Pr[yield] = |F|^m / (m! * N) = (2p)^m / (m! * p^n)

For m = n:

    Pr[yield] = (2p)^n / (n! * p^n) = 2^n / n!  (a constant, independent of p)

This constant probability means the index-calculus algorithm succeeds in expected
O(n!) trials per relation — independent of p. The complexity in terms of the group
order N = p^n is:

    O(N^{2/n + o(1)})  (Gaudry for n=2, Diem for general n, Joux-Vitse for abelian varieties)

which is subexponential in N for n >= 3 and polynomial in p. This beats sqrt(N)
(Pollard rho) whenever n >= 3.

### 2.3 Why the Weil bound applies here

To prove the yield bound rigorously (not just heuristically), one must bound the
Fourier coefficients of the indicator 1_F:

    hat{1_F}(k) = sum_{P in F} chi(k, P)

where chi is a character of E(F_{p^n}).

For extension fields, the key structural fact is:

**The character chi can be realised as an algebraic function.**

Specifically:
- The group E(F_{p^n}) has order N ~ p^n.
- For a character of order N, chi(P) = e^{2pi i * DL_G(P) / N}.
- When the full N-torsion E[N] lies in E(F_{p^n}) — which happens precisely when n
  equals the embedding degree k_emb of the curve — the Weil pairing
  e_N : E[N] x E[N] -> mu_N(F_{p^n})
  gives chi(P) = e_N(P, T) for a fixed T in E[N].
- The Weil pairing is a **bilinear algebraic map** defined over F_{p^n}.
- Therefore chi is an algebraic character: a rational function of the coordinates
  of P over F_{p^n}.

With chi algebraic and the indicator 1_F defined by the algebraic condition x^p = x,
the character sum hat{1_F}(k) is a standard exponential sum over an algebraic variety
in characteristic p. The Weil-Deligne bounds (Katz-Sarnak, etale cohomology) give:

    |hat{1_F}(k)| = O(sqrt(|F|)) = O(sqrt(p))

for each non-trivial k. This is the rigorous analogue of H-PSEUDO for extension fields,
and it **follows from the Weil bound** precisely because both the factor base and the
character are algebraic.

The heuristic yield bound is thereby confirmed rigorously (up to constants) for
extension-field Semaev whenever the embedding degree n divides n (i.e., always in the
relevant construction).

---

## 3. Why this proof strategy fails for prime fields: the Bezout no-go

### 3.1 Algebraic factor bases over F_p are too small

For E over F_p, consider any algebraically defined factor base:

    F_alg = {P in E(F_p) : f(x(P), y(P)) = 0}

where f is a polynomial of degree d (not identically zero and not defining all of E).

By Bezout's theorem, the intersection of the curve E with the plane curve {f=0} has
at most deg(E) * deg(f) = 2d points (counted with multiplicity, over the algebraic
closure). Over F_p:

    |F_alg| <= 2d

For index calculus to beat Pollard rho, one needs:

    B = |F| >> N^{1/2 + o(1)} = p^{1/2 + o(1)}

But the Bezout bound gives |F_alg| = O(d) — **independent of p** — for any fixed
polynomial predicate of bounded degree d. No algebraic factor base of fixed degree
can contain more than O(d) = O(1) points (in p), far short of the p^{1/2 + o(1)}
required.

To get |F_alg| ~ p^{alpha} for any alpha > 0, one would need a polynomial of degree
d ~ p^{alpha}, but then:
- The polynomial itself has p^{alpha} coefficients (storage cost ~p^{alpha}).
- Membership testing requires evaluating a degree-p^{alpha} polynomial (cost ~p^{alpha}).
- These costs must be charged against the algorithm's complexity, and they already
  dominate the sqrt(p) target.

**Conclusion (Bezout no-go):** Over prime fields, every algebraically defined factor
base is either trivially small (|F| = O(1)) or costs more to use than the rho bound
it attempts to beat. There is no algebraic factor base of sufficient size for index
calculus to work over prime fields.

This is the content of the bounded-degree factor base theorem recorded in
ideas/artifacts/IDEA-20260801-021/ and formalised in KN-OPEN-020.

### 3.2 The non-algebraic factor base is forced, not chosen

The prime-field factor base F = {P in E(F_p) : x(P) < t} is the only natural
choice of size B ~ p^{1/2} (by taking t ~ p^{1/2}). The condition x(P) < t is:

- **Non-algebraic over F_p:** The ordering relation "<" is not expressible as a
  polynomial equation or inequality in F_p. There is no polynomial f such that
  f(x) = 0 iff x < t.
- **Forced by Bezout:** The Bezout no-go shows that any algebraically defined set
  of adequate size either doesn't exist (for bounded-degree f) or is too expensive
  to exploit. The "small x" condition is the canonical non-algebraic workaround.
- **Geometrically natural:** The x-coordinates of E(F_p) are approximately uniformly
  distributed in [0, p-1] (by the Weil bound on complete character sums). Taking
  the first B of them by magnitude gives a factor base of the right size.

This non-algebraic character is not a limitation of our proof techniques; it is a
mathematical necessity imposed by Bezout.

---

## 4. The connection to H-PSEUDO: what extension-field success reveals

### 4.1 What H-PSEUDO asks

H-PSEUDO (KN-FIND-e7a3b1, H-PSEUDO-83817b) asks:

> For F = {P in E(F_p) : x(P) < t} with |F| = B, does
>   max_{k != 0} |sum_{P in F} e^{2pi i k * DL_G(P) / N}| <= C(p) * sqrt(B)?

This is the Fourier flatness condition for the indicator 1_F: the DFT of the
membership function of F must have no large Fourier modes.

The character sum in H-PSEUDO has two components:
1. **The indicator 1_F:** defined by the non-algebraic condition x(P) < t.
2. **The character chi(P) = e^{2pi i k * DL_G(P) / N}:** involves DL_G(P), a
   non-algebraic function of P (over F_p) for cryptographic curves.

### 4.2 The extension-field case is two algebraic objects; the prime-field case is two non-algebraic objects

In extension-field Semaev, the analogous character sum decomposes cleanly:

    sum_{P: x(P) in F_p} e_N(P, [k]T)

- Indicator: x(P)^p - x(P) = 0 — **algebraic** (Frobenius condition).
- Character: e_N(P, [k]T) — **algebraic** (Weil pairing, defined by EC group law).

Both factors are algebraic. The Weil bound applies. H-PSEUDO is provable (proved).

In prime-field Semaev, the analogous character sum is:

    sum_{P: x(P) < t} e^{2pi i k * DL_G(P) / N}

- Indicator: x(P) < t — **non-algebraic** (archimedean ordering).
- Character: e^{2pi i k * DL_G(P) / N} — **non-algebraic** for curves with large
  embedding degree (the cryptographically relevant case; see KN-FIND-3a7d42).

Both factors are non-algebraic. The Weil bound does not apply (DL circularity,
KN-FIND-c93d45). H-PSEUDO is unproved and may be genuinely hard.

### 4.3 The embedding degree exception confirms the pattern

KN-FIND-3a7d42 establishes that H-PSEUDO IS provable for embedding-degree-2 curves.
The proof works precisely because, for k_emb = 2, the character chi can be expressed
as a Weil pairing over F_{p^2} — making it algebraic. This is exactly the
extension-field mechanism applied to the k=2 case.

The proof fails for large-embedding-degree curves (cryptographic ones) because
accessing the N-torsion in F_{p^{N/2}} would require solving ECDLP — the problem
is circular. The algebraic character is inaccessible precisely for the curves where
ECDLP is hard.

This is not coincidence: the same structural property (large embedding degree) that
makes ECDLP cryptographically hard also makes H-PSEUDO unprovable by algebraic methods.

### 4.4 Precise statement of what H-PSEUDO asserts

H-PSEUDO can now be read as:

> **The non-algebraic "small x" factor base of E(F_p) behaves, for character sum
> purposes, as if it were an algebraic factor base of the extension-field type.**

More precisely: H-PSEUDO asserts that even though 1_{x(P)<t} is not a polynomial
in x(P), and even though DL_G(P) is not a rational function of P, their combination
satisfies the same sqrt(B) Fourier bound that would follow from algebraicity.

This is a highly non-trivial assertion. The extension-field case shows that when both
factors ARE algebraic, the bound follows from standard machinery. H-PSEUDO claims the
bound survives the removal of algebraicity from both factors simultaneously, which
requires new mathematics.

---

## 5. Structural summary

### 5.1 Why extension-field Semaev succeeds (schematically)

    Algebraic FB + Algebraic character
    => Weil bound applies
    => hat{1_F}(k) = O(sqrt(p))
    => Yield bound proved
    => Subexponential complexity proved

### 5.2 Why prime-field Semaev is hard to prove

    Non-algebraic FB (Bezout-forced) + Non-algebraic character (embedding-degree-forced)
    => Weil bound inapplicable (DL circularity obstruction, KN-FIND-c93d45)
    => hat{1_F}(k) bounded only empirically (C ~ p^{0.055..0.079}, BATCH-073..079)
    => Yield bound holds only heuristically / conditionally on H-PSEUDO
    => Complexity claim exp(c sqrt(log N log log N)) is tight but unproved

### 5.3 The non-algebraic character is a mathematical necessity, not a gap

The two sources of non-algebraicity are independently forced:

1. **Non-algebraic FB** is forced by Bezout (KN-OPEN-020): no algebraic FB of
   adequate size exists over F_p. The "small x" condition is the only known way
   to get B ~ p^{1/2} points without paying p^{1/2} just to describe the set.

2. **Non-algebraic character** is forced by the embedding degree (KN-FIND-3a7d42):
   for cryptographic curves (k_emb >> 1), accessing the N-torsion algebraically
   requires working in F_{p^{k_emb}} ~ F_{p^{N/2}}, which is infeasible. The
   algebraic character is inaccessible.

Both obstructions are intrinsic to the prime-field setting. They are not artifacts
of our proof strategy or the current state of additive combinatorics. An approach
that resolves H-PSEUDO would need to work with both non-algebraic objects
simultaneously.

---

## 6. What the extension-field comparison does NOT say

**It does not say H-PSEUDO is false.** The extension-field success demonstrates
that character sums over algebraic factor bases satisfy the bound; it says nothing
about non-algebraic ones.

**It does not say H-PSEUDO cannot be proved.** The proof barrier (DL circularity)
closes all known algebraic proof routes, but proof routes that do not require
algebraic access to the DL character — for instance, additive combinatorics
approaches, Fourier-analytic methods on F_p independent of the group structure,
or number-theoretic bounds on max|hat{1_F}(k)| via multiplicative structure —
are not ruled out by the extension-field comparison.

**It does not change the empirical status.** H-PSEUDO holds at all tested p with
C(p) ~ p^{0.055..0.079} (KN-FIND-d4f820). The characterisation is tight up to the
proof of H-PSEUDO (KN-FIND-f8c290).

---

## 7. Conclusion

**The extension-field Semaev success is explained by the algebraic factor base.**

The Frobenius condition x^p - x = 0 is a polynomial equation over F_{p^n}. This
makes the factor base algebraically defined, makes the Weil/Katz-Sarnak bound
applicable to the character sum, and converts the heuristic yield bound into a
theorem. The subexponential complexity result for extension-field Semaev is a
consequence of algebraic structure, not a phenomenon that generalises.

**The prime-field setting is structurally different in both obstructions:**

1. Bezout prevents algebraic factor bases of adequate size (KN-OPEN-020).
2. Large embedding degree prevents algebraic realisation of the DL character
   (KN-FIND-3a7d42, KN-FIND-c93d45).

**H-PSEUDO is the precise open question at the intersection of these two obstructions.**

It asks whether the non-algebraic "small x" factor base (forced by Bezout) satisfies
the same Fourier flatness that an algebraic factor base would satisfy via Weil. The
extension-field case confirms that algebraic flatness is achievable; H-PSEUDO asks
whether non-algebraic flatness holds despite the absence of algebraic machinery.

The extension-field comparison does not make H-PSEUDO easier. It clarifies why H-PSEUDO
is hard: it is asking for a phenomenon that, in the only setting where the analogous
statement is proved, is proved by means that are unavailable in the prime-field setting.
H-PSEUDO is a genuinely new open problem requiring new techniques.

**Evidence citations:** KN-FIND-e7a3b1, KN-FIND-c93d45, KN-FIND-3a7d42,
KN-FIND-d4f820, KN-FIND-f8c290, KN-OPEN-001, KN-OPEN-020.

---

*Analyst note: This document is a structural / mathematical analysis under the
executor-mechanical role. No new ECDLP claim is made. No hypothesis status is
changed. The analysis is consistent with the Bezout no-go (KN-OPEN-020), the DL
circularity obstruction (KN-FIND-c93d45), and the embedding-degree obstruction
(KN-FIND-3a7d42) as already recorded in the ledger. It provides conceptual
synthesis but no new experiment or result.*
