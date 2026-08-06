# H-GGM-001 Simulability Analysis

**Task:** TASK-20260804-051 (BATCH-060)  
**Hypothesis:** H-GGM-001  
**Source:** KN-OPEN-005, KN-TECH-005, KN-TECH-009  
**GGM variant:** Shoup encoding-based model (opaque random labels, group-operation oracle, equality tests)

---

## Formal Setup

In Shoup's GGM every group element [j]G is assigned a random opaque label
sigma([j]G). A *generic algorithm* learns nothing beyond:

1. The labels sigma(P), sigma(Q) for input points.
2. Results of group operations: sigma(P + Q) from sigma(P), sigma(Q).
3. Equality tests: sigma(P) = sigma(Q)?

An augmented oracle O supplements this. O is **SIMULABLE** if a GGM simulator can
answer every O-query using only group operations and equality tests with O(1)
overhead (constant independent of the group order N). It is **NON-SIMULABLE** if
there exists an encoding pair (E_1, E_2) that are GGM-indistinguishable (same
group structure, same labels on queried points) but yield different O-answers; the
pair is the *witness*.

Public data: curve parameters (a, b, p, N) and any endomorphism computable from them.

---

## Control Oracle Calibration (from H-GGM-001 predictions)

Before the four augmented oracles, the control verdicts anchor the test:

| Control oracle | Expected verdict | Reason |
|---|---|---|
| Pure-generic: (P, Q) → P+Q | SIMULABLE, C=1 | Is the group operation itself |
| Public-curve: () → (a,b,p,N) | SIMULABLE, C=0 | No group ops needed |
| DLP: (P, Q) → k s.t. Q=[k]P | NON-SIMULABLE | k unreconstructable from labels |
| Encoding: P → x-coord(P) | NON-SIMULABLE | Coordinate encoding-dependent |

These are consistency checks. The four augmented oracle verdicts follow below.

---

## Oracle A: First-jet / Dual-number Oracle

### Specification

On instance (G, Q = [k]G), the oracle takes a tangent vector dG ∈ T_G(E) as
input (an element of the formal tangent space, concretely a pair (dx, dy)
satisfying the linearized Weierstrass equation at G: 2y·dy = (3x²+a)·dx) and
returns dQ = the corresponding tangent vector at Q.

The dual-number calculation: in E(F_p[ε]/ε²), with ε² = 0,

    G_ε = G + ε·dG,   Q_ε = [k](G_ε).

The scalar multiplication [k] is an endomorphism of E(F_p[ε]) and its differential
is multiplication by k in the invariant differentials (this follows from [k]*(ω) = k·ω
for the Néron differential ω = dx/(2y)). Therefore:

    Q_ε = [k](G + ε·dG) = [k]G + ε·(k·dG) = Q + ε·dQ

where **dQ = k · dG**.

### Simulability verdict: NON-SIMULABLE

**Argument.** A GGM simulator has labels sigma(G) and sigma(Q) and can form
sigma([m]G + [n]Q) for integer (m,n) by group operations. It cannot:

(a) Extract the concrete Weierstrass coordinates of G or Q (encoding-dependent).
(b) Compute k (requires solving DLP).

Since dG lies in the concrete tangent space (depends on (x,y) coordinates of G
via the linearized curve equation) and dQ = k·dG, the oracle's output requires
*both* concrete coordinate access *and* knowledge of k. Neither is available to
the GGM simulator.

**Witness.** Take any two instances:

    I_1: (E, G, Q = [k_1]G)   I_2: (E, G, Q = [k_2]G)  with k_1 ≠ k_2.

Arrange the GGM encodings so sigma([k_1]G) = sigma([k_2]G) (same label for Q in
both instances — achievable since GGM labels are arbitrary, and the GGM only
distinguishes elements by the group law, not by which k-value produced them with
respect to G). Both instances are GGM-indistinguishable (same abstract group, same
labels on G and Q). But the jet oracle returns k_1·dG ≠ k_2·dG, so the two
instances yield different oracle answers. This is the GGM non-simulability witness.

**Key structural classification.** The jet oracle is NON-SIMULABLE but also
**privately computable**: computing dQ = k·dG requires knowing k. An external
attacker (who does not know k) cannot evaluate the oracle on a fresh dG. This
places Oracle A in the same category as the DLP control oracle — it *encodes k
directly* (dQ/dG = k in the invariant differential) and is equivalent in power to
the DLP oracle itself. It provides no useful asymmetric advantage to an attacker:
if you can query it, you already have k.

**Implication for H-GGM-001.** NON-SIMULABLE verdict: Oracle A identifies
genuinely non-generic, k-dependent information (rule from H-GGM-001 §interpretation_limits).
But it is NOT a breakthrough signal because the oracle is not a publicly computable
augmented oracle — it requires k to evaluate. Exploiting Oracle A is logically
equivalent to the assumption that the DLP is already solved.

---

## Oracle B: Elliptic Net / Somos Values Oracle

### Specification

For the pair (G, Q = [k]G) on E/F_p, the *elliptic net* W: Z² → F_p is the
bi-indexed sequence satisfying the Somos-4-type quadratic recurrence (Stange,
KN-LIT-018):

    W(m,n)² · W(m+r,n-s) · W(m-r,n+s)
      = W(m+r,n) · W(m-r,n) · W(m,n+s) · W(m,n-s)

with W(1,0) = 1, W(0,1) = 1 (normalization at the base points G and Q). The
oracle answers queries (m,n) → W(m,n) for arbitrary integer inputs.

### Connection to division polynomials

Since Q = [k]G, the point m·G + n·Q = [m + nk]G. The net value W(m,n) is the
elliptic net term associated to the point [m + nk]G, which equals (up to a unit)
the evaluation of the division polynomial ψ_{m+nk} at the base point G. Thus:

    W(m,n) = W_{m + nk}

where W_j is the j-th term of the 1-dimensional elliptic divisibility sequence
(EDS) attached to G on E. This is an algebraic function of the Weierstrass
coordinates of [m+nk]G — concretely, a polynomial in the x-coordinate of [j]G.

### Simulability verdict: NON-SIMULABLE

**Argument.** W(m,n) = W_{m+nk} is a polynomial in the x-coordinate of [m+nk]G.
The GGM simulator can form the label sigma([m+nk]G) by group operations (m
operations on G, n on Q, one addition). But the x-coordinate of [m+nk]G is
encoding-dependent: it is NOT recoverable from the opaque label sigma([m+nk]G).
Therefore the net value W(m,n) is encoding-dependent and NON-SIMULABLE — it
falls in the same class as the x-coordinate encoding control oracle.

**Witness.** Two curves E_1, E_2 with the same abstract group structure (prime
order N, same group law on abstract elements) but different Weierstrass equations.
The GGM labels can be matched: sigma_1([j]G_1) = sigma_2([j]G_2) for all j.
Yet the net values W_1(m,n) = (division poly of E_1 at [m+nk]G_1) differ from
W_2(m,n) in general, since distinct Weierstrass models assign distinct x-coordinates
to abstract group elements. Any such pair is a concrete witness.

**The universal-identities kill argument (KN-TECH-009).** The Somos recurrence
holds for ALL k — it is a tautological identity encoding the group law, not a
k-specific constraint. Concretely:

- The *structure* (which polynomial identities hold among W(m,n)) is universal and
  simulable.
- The *values* W(m,n) are encoding-dependent and k-dependent.

The k-dependence is real: W(m,n) = W_{m+nk} encodes the index m+nk mod N. But
extracting k from the sequence {W_{m+nk}} for attacker-chosen (m,n) reduces to the
following: given oracle access to the function j ↦ W_j (the EDS values at the
j-th point [j]G), find k. This is no easier than standard ECDLP, because:

1. W_j is a deterministic function of the x-coordinate of [j]G (the division
   polynomial evaluation).
2. The attacker can probe j = m+nk for any (m,n) they choose, but each probe
   requires them to know j = m+nk, which requires knowing k (circular).
3. Without knowing k, the attacker's queries have the form (m,n) → W_{m+nk},
   which amounts to: "given oracle access to EDS values at unknown-index points,
   find k." The birthday lower bound applies because finding k from such values
   is information-theoretically equivalent to standard DLP.

**Conclusion.** Oracle B is NON-SIMULABLE (encoding-dependent) but provides no
sub-birthday ECDLP advantage. It is equivalent in power to the encoding (x-coordinate)
control oracle. The Somos identities are universally satisfied and carry no k-specific
information. Finding k from net values is DLP-hard.

---

## Oracle C: Incidence Reporting Oracle

### Specification

Given a factor-base set F = {P_1, ..., P_m} ⊂ E(F_p) and Q = [k]G, the oracle
reports the incidence structure: for any queried subset I ⊆ {1,...,m}, the oracle
answers whether Σ_{i ∈ I} P_i = Q (and generalizes to linear combinations with
small coefficients).

### Simulability verdict: SIMULABLE

**Argument.** The oracle's output for a queried subset I is determined entirely by:

1. The group sum R_I = Σ_{i ∈ I} P_i, computable by |I|-1 ≤ m-1 group operations.
2. The equality test R_I = Q?, requiring one equality test.

Both operations are available to the GGM simulator. For a query of size |I| = r,
the simulator uses r-1 group additions and one equality test — overhead O(m) per
query, which is O(1) for fixed factor-base size m. The Oracle's answer is fully
determined by the group law and the equality relation; it requires no concrete
coordinate data and no knowledge of k beyond sigma(Q).

**No encoding dependence.** Unlike Oracle A (requires k to compute dQ) and
Oracle B (requires x-coordinates of [j]G), the incidence check P_{i1}+...+P_{ir} = Q
uses only the abstract group operation and equality in the GGM labels. The GGM
simulator can reproduce the oracle exactly.

**No GGM witness exists.** Any two GGM-indistinguishable instances (same labels,
same group law) will yield identical incidence reports, because incidence is
determined by sigma(Σ P_i) = sigma(Q)?, which depends only on the labels and
group law.

**Implication for H-GGM-001.** SIMULABLE verdict: the Shoup/Corrigan-Gibbs-Kogan
lower bound applies (KN-TECH-005). Any algorithm that uses only incidence-oracle
queries (together with group operations and equality tests) needs Ω(√N) total
operations for ECDLP on a prime-order group of order N. Index-calculus strategies
built on incidence reporting provide no sub-birthday advantage over generic methods
in this model.

**Caveat on computational cost.** The oracle may be *computationally expensive*
to evaluate (finding all smooth subsets requires checking 2^m subsets, the hard
step of index calculus). But "computationally expensive" and "non-simulable" are
distinct: the oracle's output is determined by the group law, so the GGM lower
bound applies regardless of the oracle evaluator's computational cost.

---

## Oracle D: Endomorphism Images Oracle

### Specification

Given a computable endomorphism φ of E, the oracle provides φ(G) and φ(Q).
The oracle is parameterized by the endomorphism specification (as a map on E).

### Algebraic fact: all endomorphisms act as scalar multiplications on E(F_p)

For any elliptic curve E/F_p with #E(F_p) = N (prime), the group E(F_p) ≅ Z/NZ.
Every endomorphism φ ∈ End_{F_p}(E) — the ring of F_p-rational endomorphisms
that preserve E(F_p) — acts on E(F_p) via the ring homomorphism:

    End_{F_p}(E) → End(Z/NZ) ≅ Z/NZ

The image of φ under this homomorphism is some [m] ∈ Z/NZ (since Z/NZ is a field
for prime N, every nonzero endomorphism acts invertibly as multiplication by some
scalar). Therefore, for all P ∈ E(F_p):

    φ(P) = [m]P

for some integer m determined by φ.

This holds for ALL prime-order E/F_p, including CM curves:

- **Ordinary prime-order curves**: End_{F̄_p}(E) is an order in an imaginary
  quadratic field. The Frobenius π ∈ End_{F̄_p}(E) satisfies π² - tπ + p = 0.
  However, for P ∈ E(F_p) one has π(P) = (x^p, y^p) = (x, y) = P (by Fermat's
  little theorem), so π acts as [1] on E(F_p). Any other CM endomorphism φ
  satisfies a polynomial relation over Z, and its action on E(F_p) is again a
  scalar in Z/NZ.

- **Supersingular curves**: End_{F̄_p}(E) is a maximal order in a quaternion
  algebra, but the action on E(F_p) factors through Z/NZ. Same conclusion.

### Simulability verdict: SIMULABLE

**Argument.** Since φ(G) = [m]G and φ(Q) = [m]Q for some publicly computable m:

    - φ(G) = [m]G: computable by m group doublings/additions in O(log m) group ops.
    - φ(Q) = [m]Q: computable by the same operations on sigma(Q).

The GGM simulator computes sigma([m]G) from sigma(G) and sigma([m]Q) from sigma(Q)
using standard square-and-multiply (O(log m) group ops). This is O(1) overhead for
any fixed endomorphism.

**No encoding dependence.** The endomorphism images are group elements (not
coordinate values), accessible via GGM labels.

**Does φ(Q) help find k?** φ(Q) = [m][k]G = [mk]G. The attacker knows sigma([mk]G)
and sigma([m]G). Finding k from this pair is equivalent to finding the DLP of
[mk]G in base [m]G — the same problem with the same exponent k (since gcd(m,N)=1
for invertible endomorphisms). This gives no advantage.

**Implication for H-GGM-001.** SIMULABLE verdict: Shoup lower bound applies.
Endomorphism-augmented ECDLP (for generic prime-order curves over F_p) is closed
at exponent 1/2.

---

## Overall Verdict

| Oracle | Verdict | Reason | Implication for H-GGM-001 |
|---|---|---|---|
| **A: First-jet** | **NON-SIMULABLE** | dQ = k·dG requires k (privately computable) | k-dependent but = DLP oracle; no public advantage |
| **B: Elliptic net** | **NON-SIMULABLE** | W(m,n) encodes x-coord([m+nk]G); encoding-dependent | Equivalent to x-coord oracle; DLP-hard to invert |
| **C: Incidence** | **SIMULABLE** | Subset sums checkable by group ops + equality | Closed at exponent 1/2 by Shoup/CK lower bound |
| **D: Endomorphism** | **SIMULABLE** | All φ ∈ End_{F_p}(E) act as [m] on E(F_p) | Closed at exponent 1/2 by Shoup/CK lower bound |

### Three-tier taxonomy

The analysis reveals a taxonomy more refined than the binary SIMULABLE / NON-SIMULABLE split:

1. **Simulable (C, D):** Output determined by group law alone. Shoup lower bound
   closes these candidates at exponent 1/2. No further analysis needed.

2. **Non-simulable and privately computable (A):** Requires k to evaluate. Equivalent
   in power to the DLP oracle. Not a publicly usable augmented oracle; provides no
   asymmetric advantage.

3. **Non-simulable and encoding-dependent (B):** Does not require k to evaluate
   (given a concrete curve and its coordinates, W(m,n) is computable without
   knowing k for fixed m,n). Encoding-dependent. BUT the k-dependent information
   is equivalent to x-coordinate access at arbitrary group elements, which does not
   give sub-birthday advantage because finding k from the net values reduces to DLP.

Only tier 3 oracles are candidates for genuine non-generic advantage. Oracle B is
the only tier-3 oracle here, and the argument shows it provides no sub-birthday
advantage beyond coordinate access.

### Implications for KN-OPEN-005

KN-OPEN-005 asks whether the augmented representations are GGM-simulable or supply
k-dependent relations below the birthday bound.

- Oracles C and D: **closed** by simulability. Birthday bound applies by theorem.
- Oracle A: **non-simulable** but no advantage; privately computable = requires k.
  Not a feasible augmentation for a sub-birthday attack.
- Oracle B: **non-simulable** (encoding-dependent), but the k-dependent information
  is no more useful than x-coordinate access. The Somos identities are universal
  tautologies on a fixed k-fiber. **No sub-birthday advantage established.**

The strongest claim that follows from this analysis: Oracles C and D are formally
closed at exponent 1/2 for all prime-order curves over F_p. Oracles A and B carry
non-generic structure but neither provides a demonstrated pathway to sub-birthday
ECDLP, consistent with the "no sub-rho EDS/net DLOG mechanism is known" caveat
in KN-TECH-009.

### What this does NOT settle

- Whether a MORE CLEVERLY SPECIFIED jet oracle (e.g., one using structured jet
  data from an isogeny or CM action rather than a free tangent vector) could be
  both non-simulable and publicly computable with genuine k-dependent advantage.
  The analysis here applies to the canonical first-jet specification.
- Whether combining multiple non-simulable oracles (e.g., A + B) could amplify
  the non-generic signal.
- KN-OPEN-001 (whether index calculus beats rho for prime-field ECDLP) — per
  H-GGM-001 §interpretation_limits, this analysis settles KN-OPEN-005 for the
  tested oracles only.

---

*Analysis performed under TASK-20260804-051, BATCH-060, GOAL-ECDLP-001.*  
*Sources: H-GGM-001 (hypothesis text), KN-OPEN-005, KN-TECH-005, KN-TECH-009.*
