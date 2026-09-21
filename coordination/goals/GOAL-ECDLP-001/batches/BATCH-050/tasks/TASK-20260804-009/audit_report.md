# IDEA-e88120 Proof-Search-Map Audit

**Proposal:** IDEA-20260804-e88120 — Class group DLP reduction via CM theory  
**Auditor task:** TASK-20260804-009 (BATCH-050)  
**Source:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-049/tasks/TASK-20260804-006/proposals.yaml`  
**Date:** 2026-08-04  
**Role:** Mathematical analyst (Coordinator authority, read-only on hypothesis status)

---

## Audit 1: Exact Baseline Reproduction

### Can we compute the Cl(O_K) DLP at bits=20 efficiently?

**Yes, as a standalone problem.** For an ordinary E/F_p at bits=20 (p ~ 2^20):

- Trace t satisfies |t| ≤ 2*sqrt(p) ~ 2^11, so t is small
- CM discriminant D = t² − 4p, with |D| ~ 4p ~ 2^22
- By the analytic class number formula, h(D) ~ sqrt(|D|)/(2π) * L(1, χ_D) ~ 2^10 on average
- Baby-step giant-step on Cl(O_K) of order h(D) ~ 2^10 costs ~ sqrt(h(D)) ~ 2^5 = 32 ideal
  composition operations
- Each ideal composition in O_K of discriminant |D| ~ 2^22 costs O((log|D|)²) ~ O(22²) ~ 484 bit
  operations
- **Total class group DLP cost: ~32 × 484 ~ 15,500 bit operations — trivially fast**

Pollard rho for ECDLP at bits=20:
- N ~ p ~ 2^20
- Cost: sqrt(N) ~ 2^10 = 1024 EC group operations, each O((log p)²) ~ O(400) bit ops
- **Total: ~400,000 bit operations**

**The class group DLP at bits=20 is ~25× cheaper than Pollard rho in bit operations.**

### What does the baseline cost look like at crypto scale?

At bits=256 (p ~ 2^256):

- h(D) ~ sqrt(p) ~ 2^128
- Class group index calculus (Hafner-McCurley / Jacobson / Biasse-Fieker):
  L_{h(D)}[1/2, c] = exp(c · sqrt(log(2^128) · log log(2^128)))
  = exp(c · sqrt(128 ln 2 · ln(128 ln 2)))
  = exp(c · sqrt(88.7 · 4.49))
  = exp(c · 19.95)
  For c ≈ 0.963: exp(19.2) ≈ **2^27.7 ideal operations**
  Each operation: O((log|D|)²) ~ O(256²) ~ 2^16 bit ops
  **Total: ~2^44 bit operations**

- Pollard rho for ECDLP at bits=256: ~2^128 EC operations × 2^17 bit ops = **~2^145 bit
  operations**

**IMPORTANT CORRECTION TO THE PROPOSAL:** The proposal states "No improvement at crypto scale with
standard algorithms." This is incorrect. At bits=256, class group index calculus on Cl(O_K) of
order 2^128 costs ~2^44 bit operations, versus Pollard rho at ~2^145. IF the reduction were valid,
the class group route would be ~2^101 times faster. This would be a genuine cryptographic break.

### The baseline obstruction: no reduction algorithm exists

The critical gap: **the class group DLP and the ECDLP are different problems.**

- ECDLP: given G, Q ∈ E(F_p), find k ∈ Z/NZ with [k]G = Q
- Class group DLP: given E, E' isogenous over F_p, find ideal class [a] ∈ Cl(O_K) with [a]·E = E'

These live in different mathematical objects. The baseline cost comparison above (32 ops vs 1024
ops) is vacuous because there is no known algorithm that converts an ECDLP instance (G, Q, E) into
a class group DLP instance. The "baseline" cannot be reproduced because the reduction step has no
specified algorithm.

**Baseline audit result:** CANNOT REPRODUCE. The class group DLP is feasible as a standalone
problem at bits=20, but the connecting reduction is undefined.

---

## Audit 2: Observation-Collision Search

### Literature review: is a reduction from ECDLP to class group DLP known?

**Galbraith-Smart 1999** ("A Cryptographic Application of Weil Descent," ANTS 1999): This paper
addresses ECDLP over *extension fields* via Weil restriction of scalars — not ECDLP over F_p via
class group methods. Weil descent maps ECDLP on E(F_{p^n}) to a DLP on an abelian variety over
F_p. No class group DLP reduction is given.

A separate body of Galbraith's work (including "Constructing isogenies between elliptic curves over
finite fields," 1999) gives algorithms for computing isogenies. The relevant observation attributed
to Galbraith and Smart in the task prompt — that ECDLP on CM curves reduces to DLP in the
principal ideal class — would require: (a) explicit CM (known endomorphism ring), and (b) the CM
endomorphism as a rational map. For a *generic* random curve over F_p with CM discriminant
D ~ 4p, computing the explicit CM endomorphism requires O(sqrt(p)) composed small-degree isogeny
steps, matching Pollard rho in cost.

**Biasse-Jacobson-Silvester** (e.g., "Analysis of the Reduction Algorithms for the Principal Ideal
Problem in Imaginary Quadratic Number Fields"): This body of work achieves L[1/2] for class group
computation and the principal ideal problem in imaginary quadratic fields. It provides the
algorithmic foundation for class group DLP. **No ECDLP reduction is given or implied.**

**Couveignes-Rostovtsev-Stolbunov (CRS) scheme** (Couveignes 2006, Rostovtsev-Stolbunov 2006):
Uses the class group action Cl(O_K) on ordinary elliptic curves over F_p for a key exchange
protocol. The *security* of CRS rests on the class group DLP being hard — explicitly treated as a
*separate* hard problem from the ECDLP on the same curves. If ECDLP reduced to class group DLP,
CRS would not be a new hard problem. This has been understood since 2006 without anyone noting a
reduction.

**CSIDH** (Castryck-Lange-Martindale-Panny-Renes 2018): Supersingular analogue of CRS. Uses
Cl(Z[sqrt(-p)]) acting on supersingular curves over F_p. Security analysis treats the class group
action problem as distinct from ECDLP. The same ECDLP on the supersingular curve E (find k with
[k]P = Q) is solvable in Pollard rho O(sqrt(p)) and has no known reduction to the CSIDH class
group DLP. Confirms the separation in the most structured available case.

**Joux-Naccache**: No published paper by Joux and Naccache jointly proposes an ECDLP → class
group DLP reduction. (Joux's relevant work is on pairings, DLP in F_{p^k}*, and discrete logarithm
records. Naccache's work is primarily on side channels and algorithmic number theory. No overlap on
class group ECDLP reduction is known to this analyst.)

**Boneh-Venkatesan** ("Hardness of Computing the Most Significant Bits of Secret Keys in DH and
Related Schemes," CRYPTO 1996): Addresses bit security of Diffie-Hellman, not class group
reductions.

### The 20-year absence argument

The CRS/CSIDH literature spanning 2006–2025 explicitly uses the class group action on ordinary and
supersingular curves as a *new* hard problem, separate from ECDLP. If a polynomial-time reduction
from ECDLP to class group DLP existed, it would have been noted: it would immediately imply that
CRS/CSIDH provided NO additional hardness over ECDLP. The absence of this observation across ~20
years of community work is strong circumstantial evidence that no such reduction is known.

### Key references and their conclusions

| Reference | Relevant result | Implication |
|---|---|---|
| Galbraith-Smart 1999 | Weil descent for extension field ECDLP | No class group reduction for F_p |
| Couveignes 2006 | Class group acts on ordinary curves; security = class group DLP | ECDLP ≠ class group DLP |
| CSIDH 2018 | Class group acts on supersingular curves; classically L[1/2] | Nearby-object control: separation confirmed |
| Biasse et al. | L[1/2] for class group DLP | Confirms class group DLP is easier than ECDLP, no reduction |

**Verdict: NOT KNOWN in the literature as a valid reduction. The proposal conflates two distinct
DLP problems. The absence of a reduction after 20 years of CRS/CSIDH work is near-conclusive
evidence it does not exist in the form stated.**

---

## Audit 3: Quantifier-Order Statement

### Precise statement of the proposed reduction

The proposal claims:

> "FOR ALL primes p (or density-1 set), there EXISTS an efficient reduction from ECDLP on E/F_p
> to DLP in Cl(O_K(D)), where the reduction must NOT require solving ECDLP as an intermediate
> step."

More concretely: given (E/F_p, G, Q) with Q = [k]G and G of prime order N ~ p, there exists an
efficient algorithm R that outputs a class group DLP instance (Cl(O_K), a_1, a_2) such that
solving log_{a_1}(a_2) in Cl(O_K) efficiently recovers k.

### Is the reduction circular?

**Technically no.** The class group action [a]·E can be computed without solving the ECDLP:

- Given an ideal a = (ℓ, ω - m) of norm ℓ (a small prime), the isogeny φ_a: E → E_a is
  computed via Elkies modular polynomial method in O(ℓ^{1/2} log p) time, using only arithmetic
  on E — no ECDLP oracle needed.
- Composing O(log h(D)) such prime ideal isogenies gives the full class group action in
  O(log h(D) · sqrt(ℓ_max) · log p) = O((log p)² ) time, which is polynomial in log p.

The forward direction (apply ideal class → get isogenous curve) is efficient and non-circular.

### Why the reduction is nonetheless INVALID

The obstruction is an information-theoretic mismatch, not circularity:

**Group order mismatch:**
- |E(F_p)| = N ~ p (the ECDLP group)
- |Cl(O_K)| = h(D) ~ sqrt(p) ~ sqrt(N) (the class group)

The scalar k ∈ Z/NZ. For any map φ: Z/NZ → Cl(O_K), since |Cl(O_K)| ~ sqrt(N) << N, the map
is at least sqrt(N)-to-one. Solving the class group DLP recovers the IMAGE of k under φ, which
corresponds to at least sqrt(N) ~ 2^128 different values of k at bits=256. Recovering the true k
from the class group DLP solution requires an exhaustive search over sqrt(N) candidates — exactly
as expensive as Pollard rho.

**Formally:** Any algorithm that:
1. Takes (E/F_p, G, Q = [k]G) and outputs a class group DLP instance
2. Recovers k from the class group DLP solution
must perform at least Omega(sqrt(N)) work unless it implicitly solves the ECDLP by another means.
This follows from the pigeonhole principle: N ~ p class-group-DLP-distinct inputs (values of k)
map to only h(D) ~ sqrt(p) class-group elements.

**What can legitimately be said:**
The class group structure, via the CM endomorphism ω (once explicit), allows a GLV-type
decomposition: k = a + b·ω in the CM order, where a, b ~ sqrt(N). This reduces the 1D DLP of
size N to a 2D DLP of dimension sqrt(N) × sqrt(N). Pollard rho on the 2D lattice costs
~ sqrt(det) = sqrt(N) — **no asymptotic speedup**. The endomorphism ω has degree |D|/4 ~ p,
so computing it explicitly via composed small-degree isogenies costs O(sqrt(p)) steps — matching
Pollard rho in cost before the "speedup" is even applied.

**Quantifier-order summary:**

| Claim | Status |
|---|---|
| ∀ p, ∃ efficient R converting ECDLP to class group DLP | **FALSE** — information-theoretic obstruction |
| The reduction is circular (requires ECDLP oracle) | **FALSE** in the strict sense — forward direction is non-circular |
| The reduction is invalid (cannot recover k) | **TRUE** — many-to-one mapping, loses log(N/h(D)) ~ 128 bits at b=256 |
| Computing [a]·E is efficient | **TRUE** — polynomial in log p via Vélu + Elkies |
| Translating (G, Q, k) → class group DLP element | **No known algorithm** |

The correct label for the obstruction is **INVALID_REDUCTION** (information loss), not CIRCULAR.

---

## Audit 4: Method Ceiling + Nearby-Object Control

### Ceiling of class group index calculus at |D| ~ p

The best known algorithm for DLP in Cl(O_K) for imaginary quadratic fields is index calculus in
the Hafner-McCurley/Jacobson/Biasse-Fieker family:

**Complexity:** L_{h(D)}[1/2, c] where c ≈ 0.963 (heuristically; rigorous bound has larger c)

This means: exp(c · sqrt(log h(D) · log log h(D)))

At b = 256 bits (p ~ 2^256, h(D) ~ 2^128):
```
exp(0.963 · sqrt(128 · ln2 · ln(128 · ln2)))
= exp(0.963 · sqrt(88.7 · 4.49))
= exp(0.963 · 19.95)
= exp(19.2)
≈ 2^27.7  ideal operations
```
With each operation costing O(b²) ~ 2^16 bit ops: **total ~2^44 bit operations**.

The L[1/2] complexity is the known ceiling for imaginary quadratic class group DLP. No L[o(1)]
algorithm is known or conjectured for this problem. There is no subexponential-in-b^{1/2}
algorithm; the sqrt in the exponent of L[1/2] is believed optimal for this problem class.

### Is L[1/2] of h(D) ~ sqrt(p) faster than Pollard rho?

**YES, unconditionally, at all security levels b.**

The comparison in operations:
- L[1/2] for class group: ~exp(c/sqrt(2) · sqrt(b) · sqrt(log b)) group ops  
- Pollard rho for ECDLP: ~exp(b/2 · ln 2) = 2^{b/2} group ops

For large b: 2^{b/2} grows much faster than exp(c · sqrt(b · log b)), so class group index
calculus is always faster in terms of group operations.

At specific security levels (b = log₂ p, h(D) ~ 2^{b/2}):

| b (bits) | Pollard rho (ops) | Cl(O_K) index calc (ops) | Speedup factor |
|---|---|---|---|
| 40 | 2^20 | ~2^11 | ~2^9 |
| 80 | 2^40 | ~2^18 | ~2^22 |
| 128 | 2^64 | ~2^22 | ~2^42 |
| 256 | 2^128 | ~2^28 | ~2^100 |
| 512 | 2^256 | ~2^36 | ~2^220 |

The speedup grows superpolynomially. IF the reduction were valid, ECDLP at 256-bit security would
be reduced to a computation requiring ~2^28 class group operations — a catastrophic break.

**Note:** Even though the class group index calculus is faster, it still requires solving the class
group DLP, which is the problem class of the CRS/CSIDH problem. Breaking ECDLP via this route
would simultaneously break CSIDH at the same security level — a significant corollary that has not
been observed despite sustained CSIDH cryptanalysis.

### Nearby-object control: supersingular analogue (CSIDH)

The best available nearby-object control is the CSIDH setting:

**Control object:** Supersingular elliptic curves E over F_p with End(E) ≅ maximal order in
Q(sqrt(-p)).

- Class group Cl(Z[sqrt(-p)]) acts simply-transitively on the set of supersingular j-invariants
  over F_p. The CSIDH class group DLP is: given E = [a]·E₀ and E' = [b]·E₀, find [a·b^{-1}].
- **Classical complexity of CSIDH class group DLP:** L[1/2] via BKS (Biasse-Fieker-Jacobson-style
  sieving), consistent with the imaginary quadratic ceiling above.
- **ECDLP on the same supersingular curves:** For P, Q ∈ E(F_{p²}) of prime order N ~ p,
  Pollard rho costs O(sqrt(N)) ~ O(sqrt(p)).

**Control result (decisive):** In the CSIDH setting — the most structured case available, where
the class group action is maximally explicit and efficiently computable — there is NO known
reduction from the ECDLP on the curve to the class group DLP. Despite 6 years of CSIDH
cryptanalysis (2018–2024), the ECDLP on supersingular curves is solved by Pollard rho, while the
CSIDH problem is solved by class group sieving. These are treated as distinct computational
problems throughout the literature.

The CSIDH control falsifies the general claim that "the class group DLP route gives a speedup for
ECDLP": it confirms that even when the class group DLP is efficiently solvable (L[1/2]), the
ECDLP on the same curves remains at its full Pollard rho cost. The two problems are
computationally independent.

**Instrument check (null object):** If the ECDLP → class group DLP reduction were real, applying
it to the CSIDH supersingular setting would immediately break CSIDH-256 with ~2^28 operations.
CSIDH-256 has no known break faster than ~2^60 classically (Adj-Cervantes-Jao-Menezes 2018 and
improvements). No such break exists. The reduction instrument does not detect the signal it
claims to detect.

---

## Overall Verdict

**INVALID_REDUCTION**

The class group DLP and the ECDLP are distinct computational problems. The proposed reduction is
not circular but is information-theoretically invalid: any map from ECDLP scalars (in Z/NZ, N~p)
to class group elements (in Cl(O_K), |Cl| ~ sqrt(p)) discards ~(1/2)log(p) bits of information,
making the ECDLP scalar irrecoverable from the class group DLP solution without an additional
exhaustive search that matches Pollard rho in cost.

**Summary of findings by audit:**

| Audit | Finding |
|---|---|
| 1. Baseline reproduction | Class group DLP (standalone) is feasible at bits=20 (~32 ops vs 1024 for rho). The connecting reduction algorithm does not exist; baseline cannot be reproduced. |
| 2. Literature search | No known reduction in CRS/CSIDH/Galbraith literature spanning 20 years. Absence is strong negative evidence. Closest work (CSIDH) explicitly treats the problems as separate. |
| 3. Quantifier order | Reduction statement is false: the many-to-one mismatch (N >> h(D)) makes k unrecoverable from class group DLP. NOT circular, but INVALID. |
| 4. Method ceiling | L[1/2] for class group is faster than Pollard rho IF reduction valid (2^28 vs 2^128 ops at b=256). CSIDH control directly falsifies the implied instrument: no ECDLP break from class group DLP in any known case. |

**Recommended next step:**

Before any Executor dispatch, the proposer must exhibit a concrete algorithm that resolves the
group-order mismatch: a map from ECDLP instances (k ∈ Z/NZ, N ~ p) to class group DLP instances
(in Cl(O_K) of order h(D) ~ sqrt(p)) that is information-theoretically *invertible*. The burden
is heavy: this would require h(D) ≥ N, or a reduction that uses the class group as an
intermediate in a different way than a direct DLP mapping (e.g., a covering-map approach, or a
structured decomposition of k over the class group that preserves injectivity).

If no such algorithm can be specified, the correct classification is **BLOCKED_AT_SPECIFICATION**:
the mechanism is neither novel nor known to be false, but it lacks a well-defined reduction
algorithm, and the group-order obstruction provides a clear reason why the natural formulation
fails.

**Novelty assessment:** The class group action on ordinary curves is known (CRS); the class group
index calculus is known (Hafner-McCurley). What would be novel is the reduction, but that novel
claim is the one blocked by the information-theoretic argument above. Marking `novelty_status:
known` for the underlying components and `novelty_status: blocked` for the proposed reduction.

---

*Conjectures explicitly labeled:*  
- **[CONJECTURE]** The exact threshold at which class group index calculus matches Pollard rho
  in *total wall-clock time* (accounting for constant factors in ideal operations vs EC operations)
  is estimated to be around b ~ 40-50 bits. Below this threshold, Pollard rho is competitive even
  in the class group setting.
- **[CONJECTURE]** Computing the CM endomorphism ω as an explicit rational map on E/F_p for
  generic D ~ p requires Ω(sqrt(p)) composed small-isogeny steps. A proof of this lower bound
  would establish a formal obstruction to the proposed reduction.

*This report makes no hypothesis status transitions and proposes no experiments.*
