# Class-Invariant Analysis: Ordinary Isogenies and Trace Preservation
## TASK-20260804-002 / BATCH-048

**Role:** Idea Generator (mathematical analysis only)  
**Claim ceiling:** Theoretical analysis; no crypto-scale claim; no H-IT-001 status change.  
**All theorems cited explicitly; all conjectures labeled.**

---

## Section 1: The Trace-Preservation Theorem

### 1.1 Setting

Let p be a prime, F_p the prime field. Let E and E' be ordinary elliptic curves
over F_p. The Frobenius endomorphism of E over F_p is the morphism π_E defined
by (x, y) ↦ (x^p, y^p). The **trace of Frobenius** is the integer t such that

    #E(F_p) = p + 1 - t,    |t| ≤ 2√p   (Hasse bound).

For an ordinary curve, the characteristic polynomial of π_E acting on the
ℓ-adic Tate module T_ℓ(E) (any prime ℓ ≠ p) is

    χ_E(T) = T² - t·T + p,    with discriminant t² - 4p < 0.

The curve E is ordinary iff p ∤ t, equivalently iff t² - 4p is not divisible
by p to an even power that would make the Frobenius unramified. For an ordinary
curve, the endomorphism ring End(E) is an order in the imaginary quadratic
field K = Q(√(t² - 4p)).

### 1.2 The main theorem

**Theorem (Tate, 1966; Silverman AEC Ch. V Thm. 3.1).**
_Let E, E' be elliptic curves over a finite field F_q. The following are
equivalent:_

1. _E and E' are isogenous over F_q (there exists a nonzero morphism φ: E → E'
   defined over F_q)._
2. _#E(F_q) = #E'(F_q)._
3. _E and E' have the same characteristic polynomial of Frobenius._
4. _E and E' have the same zeta function._

**Proof sketch (conditions 1 ⟹ 2 and 3):**

Let φ: E → E' be an isogeny defined over F_q. Since φ is defined over F_q,
its coefficient functions lie in F_q, so applying the q-power Frobenius map
to both sides of φ(P) = Q yields:

    π_{E'} ∘ φ = φ ∘ π_E

as morphisms E → E' (here π_E and π_{E'} denote the respective Frobenius
endomorphisms). This is an identity of morphisms of curves over F̄_q; it holds
for all points in E(F̄_q).

Now fix a prime ℓ with ℓ ∤ q and ℓ ∤ deg(φ). The isogeny φ induces an
injective Z_ℓ-linear map

    φ_* : T_ℓ(E) ↪ T_ℓ(E'),

which becomes an isomorphism after tensoring with Q_ℓ:

    φ_* ⊗ Q_ℓ : T_ℓ(E) ⊗ Q_ℓ ⟶ T_ℓ(E') ⊗ Q_ℓ.

The commutation relation π_{E'} ∘ φ = φ ∘ π_E translates to:

    (π_{E'})_* ∘ (φ_* ⊗ Q_ℓ) = (φ_* ⊗ Q_ℓ) ∘ (π_E)_*,

so (π_{E'})_* and (π_E)_* are conjugate as linear operators on the two-
dimensional Q_ℓ-vector space. Conjugate matrices have the same characteristic
polynomial; therefore:

    χ_{E'}(T) = T² - t·T + p = χ_E(T),

and in particular trace(Frob_{E'}) = trace(Frob_E) = t. By the Weil
conjectures (proved by Weil for elliptic curves),
#E'(F_q) = q + 1 - t = #E(F_q). □

**Remark on the degree-coprimality hypothesis.** The argument above uses
ℓ ∤ deg(φ) to ensure φ_* is injective on T_ℓ(E). Since there are infinitely
many primes ℓ, for any isogeny φ of finite degree d we can always choose ℓ
with ℓ ∤ d, so the argument applies to isogenies of ANY degree (coprime to p
or not). The result holds unconditionally for all isogenies over F_p.

**Remark on separability.** The theorem does not require φ to be separable.
In particular, the Frobenius isogeny π_E: E → E^{(p)} (degree p, inseparable)
trivially preserves the trace since E and E^{(p)} are isomorphic over F_p.

**Primary references:**
- Tate, J. (1966). Endomorphisms of abelian varieties over finite fields.
  *Inventiones Mathematicae* 2(2), 134–144.
- Silverman, J.H. *The Arithmetic of Elliptic Curves.* GTM 106, Springer.
  Chapter V, §3, Theorem 3.1 and Corollary 3.2.
- Waterhouse, W.C. (1969). Abelian varieties over finite fields.
  *Ann. Sci. École Norm. Sup.* (4) 2, 521–560. (Full classification of
  F_q-isogeny classes.)

### 1.3 Isogeny classes over F_p

**Corollary (isogeny class = trace class).** For ordinary elliptic curves
over F_p, the F_p-isogeny class of E is completely determined by the trace t.
Two ordinary curves are F_p-isogenous iff they have the same trace t.

This is the forward direction of Tate's equivalence (1 ⟺ 2). The number of
F_p-isomorphism classes in the isogeny class with trace t is finite and equals
the class number h(t² - 4p) of the imaginary quadratic order of discriminant
t² - 4p (up to cofactors); see Waterhouse §4.

### 1.4 Volcano structure within a trace class

Within a fixed trace class (fixed t, hence fixed K = Q(√(t² - 4p))), the
structure of the ℓ-isogeny graph is described by the **Delfs–Galbraith
volcano model** (Delfs & Galbraith, 2016; Fouquet & Morain, 2002):

- Curves with End(E) ≅ O_K (the maximal order) form the **surface** (rim) of
  the volcano.
- Curves with End(E) ≅ O_f (the order of conductor f) sit at depth v_ℓ(f)
  in the volcano (where v_ℓ is the ℓ-adic valuation).
- An ℓ-isogeny from a surface curve leads to exactly ℓ+1 neighbors: ℓ-1
  horizontal neighbors at the surface, and 2 descending neighbors (when ℓ
  is inert or ramified in K/Q). More precisely: (ℓ+1) neighbors total
  partitioned according to whether ℓ splits, ramifies, or is inert in K.

**Key point:** the conductor f of the CM order CAN change along an ordinary
ℓ-isogeny (going up or down the volcano). Thus the conductor is NOT itself
an isogeny-class invariant — it is an intra-class variable. The genuine
invariant is the trace t (equivalently, the imaginary quadratic field K and
the discriminant t² - 4p). This corrects the phrasing in EV-IT-aefd12 O-6,
which says "ordinary ell-isogenies preserve the conductor ring"; the correct
statement is that they preserve the **trace** (equivalently the isogeny class
over F_p), while the conductor can vary within that class.

**References:**
- Delfs, C. & Galbraith, S.D. (2016). Computing isogenies between supersingular
  elliptic curves over F_p. *Designs, Codes and Cryptography* 78(2), 425–440.
- Fouquet, M. & Morain, F. (2002). Isogeny volcanoes and the SEA algorithm.
  *Algorithmic Number Theory Symposium* (ANTS-V), LNCS 2369, 276–291.
- Kohel, D.R. (1996). Endomorphism rings of elliptic curves over finite fields.
  PhD thesis, University of California, Berkeley.

---

## Section 2: Implications for H-IT-001

### 2.1 The anomalous family is an isogeny-class invariant

An anomalous curve E/F_p satisfies:

    trace(Frob_E) = 1    ⟺    #E(F_p) = p.

A "generic" (random) curve E'/F_p satisfies trace(Frob_{E'}) = t' for some
t' ≠ 1 drawn roughly uniformly from the Hasse interval {t : |t| ≤ 2√p}
(under the Sato–Tate measure; each trace value occurs with probability
roughly 1/(2√p) for the prime-count normalization).

By the Tate isogeny theorem, E' is F_p-isogenous to E iff #E'(F_p) = #E(F_p).
Since #E(F_p) = p ≠ p + 1 - t' (for t' ≠ 1), E' is **not** isogenous to E
over F_p.

**Conclusion (Theorem, conditional on Tate 1966):** For any ordinary elliptic
curve E'/F_p with trace t' ≠ 1, there is **no ordinary isogeny path** of any
finite length connecting E' to any anomalous curve E (trace = 1) via F_p-
rational isogenies. The two trace classes are entirely disconnected in the
ordinary F_p-isogeny graph.

This is not a "path is exponentially long" result; it is a disconnection
result: the two sets of curves live in different connected components of the
ordinary F_p-isogeny graph. The distance is **infinite**, not merely large.

### 2.2 Correction of EV-IT-aefd12 O-6

EV-IT-aefd12 O-6 states: "reaching an anomalous endpoint requires a path of
length at least p/(ell^2) in the isogeny graph — exponentially long at any
fixed ell."

This framing is **incorrect** and understates the structural obstruction. The
Tate theorem gives a stronger conclusion: no finite path exists. The two
isogeny classes (trace = 1 and trace ≠ 1) are entirely disconnected over F_p,
not merely distant. Recording this correction explicitly: O-6's observation
that rho_special = 0 is consistent with the correct theorem, but the
attributed reason ("exponentially long path") should read "no path of any
finite length exists" (the sets are disconnected).

O-6 is correct that the structural concern requires mathematical analysis;
it is correct that rho_special = 0 is not a finite-scale artifact. The
corrected explanation is: rho_special = 0 because the ordinary F_p-isogeny
graph is disconnected between trace classes, and the anomalous class (trace = 1)
is a separate connected component from any non-anomalous class.

### 2.3 Is rho_special = 0 expected for ALL prime fields at ALL sizes?

**YES** — this follows unconditionally from the Tate theorem, not from any
heuristic or finite-scale artifact. For any prime p and any ordinary ell-
isogeny graph over F_p:

- If a random starting curve E has trace t ≠ 1, then EVERY curve reachable
  from E by any sequence of ordinary F_p-isogenies also has trace t ≠ 1.
- Anomalous curves (trace 1) are unreachable from E at any scale, for any
  choice of ell (coprime to p).

There is no class of primes p for which this fails. The only exception would
be if the starting curve itself is anomalous (trace = 1), in which case ALL
curves in its isogeny class are also anomalous — but that is a tautology, not
an exception.

**The planted path positive control failure in BATCH-047 (RT-047-B1) is a
necessary consequence of this theorem.** Any planted path ending at an
anomalous curve MUST start from an anomalous (or at minimum trace-1) curve.
A non-anomalous generic starting curve cannot reach an anomalous endpoint via
ordinary isogenies. This is a mathematical certainty, not a design bug.

### 2.4 Scope of the mechanistic gap

H-IT-001's mechanism statement reads: "Special-curve ECDLP algorithms
(Smart–Araki–Satoh–Semaev anomalous; MOV; GHS Weil descent on weak extension
fields) beat rho only on sparse families. An isogeny is a group homomorphism
on the N-primary part when deg is coprime to N, so logs transfer as
log_E(Q) = log_{E'}(phi(Q)) * (deg-scaling)."

The log-transfer identity is correct as stated for separable isogenies of
degree coprime to N. The mechanistic gap is in the unstated assumption that
the anomalous endpoint E' is reachable from a generic E via ordinary F_p-
isogenies. The Tate theorem shows it is not.

H-IT-001 as currently specified therefore has a **mechanistic gap** for the
ordinary isogeny transfer route: the log-transfer formula is valid, but the
prerequisite (the existence of an ordinary isogeny path from a generic to an
anomalous curve) is mathematically impossible. The mechanism requires either:
(a) a supersingular intermediate (addressed in Section 3 and Section 5), or
(b) a different special family whose "special" property is not an isogeny-
class invariant (addressed in Section 5), or
(c) a fundamentally different mathematical mechanism.

---

## Section 3: MOV Targets and Embedding Degree

### 3.1 Embedding degree as an isogeny-class invariant

Let E/F_p be an elliptic curve with prime-order subgroup G of order N. The
**MOV embedding degree** k is the smallest positive integer such that N | p^k - 1,
i.e., k = ord_N(p) (the multiplicative order of p modulo N).

**Claim:** k is an isogeny-class invariant over F_p.

**Proof:** By the Tate theorem, any F_p-isogenous curve E' has #E'(F_p) =
#E(F_p). For a prime-order curve, N = #E(F_p) is the same for all isogenous
curves. The embedding degree k = ord_N(p) depends only on N and p, both of
which are determined by t (since N = p + 1 - t for a prime-order curve).
Therefore k is constant across the isogeny class. □

If #E(F_p) is not prime (cofactor h > 1), the prime subgroup order N = #E(F_p)/h
might differ between isogenous curves if the cofactor h differs. However, the
total group order is fixed (#E(F_p) = #E'(F_p) for isogenous E, E'), and the
cofactor h = #E(F_p)/N is determined by N, which is the largest prime factor
of the group order. Since the group order is preserved, so is N (and h), and
hence the embedding degree k.

**Conclusion:** MOV-vulnerable curves (k ≤ 20 or similar practical threshold)
form a specific set of isogeny classes. A generic curve (large k ≈ p) is in
a completely different isogeny class. No ordinary F_p-isogeny path from a
generic curve can reach a MOV-vulnerable curve.

### 3.2 The Luca–Shparlinski result on generic embedding degree

It is a known result (Luca & Shparlinski, 2005; see also Balasubramanian &
Koblitz, 1998) that for a "random" prime-order elliptic curve over F_p, the
embedding degree satisfies k > (log p)^C with high probability (for some
constant C). For standardized NIST or Brainpool curves, the embedding degree
is explicitly chosen to be the full group order, so k ≈ N. This confirms that
generic curves are far from MOV-vulnerable and that their isogeny class does
not intersect the MOV-vulnerable class.

**References:**
- Balasubramanian, R. & Koblitz, N. (1998). The improbability that an elliptic
  curve has subexponential discrete log under the Menezes-Okamoto-Vanstone
  algorithm. *Journal of Cryptology* 11(2), 141–145.
- Luca, F. & Shparlinski, I.E. (2005). Elliptic curves with low embedding
  degree. *Journal of Cryptology* 19(4), 553–562.

---

## Section 4: Weil Descent / GHS Targets

### 4.1 GHS attack and Frobenius eigenvalues

The Gaudry–Hess–Smart (GHS) Weil descent attack (Gaudry et al., 2002) applies
to an elliptic curve E/F_{p^n} where the Weil restriction Res_{F_{p^n}/F_p}(E)
is an abelian variety with a Jacobian component of manageable genus g ≤ n-1.
For curves E/F_p being considered for GHS-descent to F_p^n-vulnerabilities,
the attack asks whether E/F_{p^n} (the base extension) is GHS-vulnerable.

**Claim:** GHS vulnerability of E/F_p is an F_p-isogeny-class invariant.

**Proof:** The Frobenius eigenvalues α, ᾱ of E over F_p satisfy α·ᾱ = p and
α + ᾱ = t. For the extension E/F_{p^n}, the Frobenius eigenvalues are α^n, ᾱ^n,
so #E(F_{p^n}) = p^n + 1 - (α^n + ᾱ^n). Since α and ᾱ are determined by
(t, p), the entire sequence (#E(F_{p^k}))_{k≥1} is determined by t and p.

The GHS vulnerability depends on properties of E over F_{p^n}, which are
determined by the sequence #E(F_{p^k}) — all of which are isogeny-class
invariants. Therefore, GHS vulnerability is also an isogeny-class invariant
over F_p. □

**Conclusion:** A GHS-vulnerable curve (with appropriate n) lives in a specific
isogeny class. A generic curve in a different isogeny class cannot reach it via
ordinary F_p-isogenies.

**Reference:**
- Gaudry, P., Hess, F. & Smart, N.P. (2002). Constructive and destructive
  facets of Weil descent on elliptic curves. *Journal of Cryptology* 15(1), 19–46.

---

## Section 5: What IS Reachable via Ordinary F_p-Isogenies?

### 5.1 Structure of ordinary F_p-isogeny classes

Given an ordinary elliptic curve E/F_p with trace t, the ordinary F_p-isogeny
class of E consists of all ordinary curves E'/F_p with #E'(F_p) = p + 1 - t.
This is a finite set of F_p-isomorphism classes. Within this set:

- All curves share the trace t, the imaginary quadratic field K = Q(√(t²-4p)),
  and the set of Frobenius eigenvalues {α, ᾱ}.
- The curves vary in their CM conductor: End(E') = O_f for varying f | ∞
  (orders of increasing conductor), organized into a volcano.
- The volcano surface consists of curves with maximal CM order O_K (conductor 1).
- The volcano has ℓ+1 isogenies from each surface vertex (ℓ horizontal + 0 or
  2 descending) and ℓ isogenies from each non-surface vertex going up, plus
  ℓ going horizontally at the same depth.

**What changes within the class:** CM conductor, j-invariant, Weierstrass model.

**What does NOT change within the class:** trace t, #E(F_p) = N, embedding
degree k = ord_N(p), GHS vulnerability, and any property depending on the
Frobenius eigenvalues.

### 5.2 Cross-class transfer requires changing the trace

To move from a generic curve (trace t ≠ 1) to an anomalous curve (trace = 1),
one needs an operation that **changes the trace**. Ordinary F_p-isogenies
cannot do this.

The only known operations that can change the trace are:

1. **Field extension**: E/F_p extended to E/F_{p^n} has a different "trace"
   (specifically α^n + ᾱ^n instead of α + ᾱ), but this is a different curve
   over a different field — it doesn't produce an ordinary isogeny over F_p.

2. **Quadratic twist**: E^d/F_p (the twist by d ∈ F_p*/(F_p*)²) has trace -t
   over F_p. The twist maps t ↦ -t. Twisting cannot make trace -t equal to 1
   unless t = -1 (trace -(-1) = 1), which is a specific sub-case. Twists are
   not isogenies (they are isomorphisms over F_{p²} but not F_p in general).

3. **Supersingular isogenies**: Supersingular curves over F_p (with p > 3) have
   trace t = 0. The supersingular ℓ-isogeny graph is well-studied (Pizer, 1990;
   Mestre, 1986) and is a connected, Ramanujan-like expander graph. But:

   - Ordinary and supersingular curves are in different F_p-isogeny classes
     (trace ≠ 0 vs trace = 0 for p > 3).
   - There is no F_p-isogeny from an ordinary curve to a supersingular curve
     (the Tate theorem applies equally: they have different #E(F_p) in general).
   - "Bridges" from ordinary to supersingular over F_p do not exist.

4. **Higher-extension isogenies**: One could consider isogenies defined over
   F_{p^k} for k > 1. Over F_{p^k}, two ordinary curves E/F_p and E'/F_p that
   are not F_p-isogenous can become F_{p^k}-isogenous if #E(F_{p^k}) =
   #E'(F_{p^k}). This requires α^k + ᾱ^k = α'^k + ᾱ'^k, which is a Diophantine
   condition on the Frobenius eigenvalues. Such coincidences exist in specific
   cases (e.g., CM curves with related fields), but are not generically
   available and would require an isogeny defined over the extension field F_{p^k},
   NOT over F_p. This falls outside the scope of H-IT-001's ordinary F_p-
   isogeny framework.

### 5.3 Can supersingular isogenies provide a bridge? (Qualitative)

**Conjecture (for recording; not proved here):** A "bridge" strategy of the
form E_ordinary → (F_p-isogeny) → E_ss → (ss-isogeny) → E'_ordinary is not
achievable via F_p-defined isogenies, because the first step E_ordinary →
E_ss already requires an F_p-isogeny between curves of different trace — which
the Tate theorem forbids.

Over the algebraic closure F̄_p, every ordinary curve is connected to some
supersingular curve (via an isogeny defined over some extension field), but
this requires extending the field, which is not within the H-IT-001 framework
(ordinary F_p-isogenies, degree coprime to p).

The cost of such a bridge, even if constructible over some extension field,
would include at minimum the cost of finding an isogeny to a curve that becomes
supersingular over some extension — a problem not known to be easier than
Pollard rho. This is a conjecture, not a proved lower bound.

---

## Section 6: Summary and H-IT-001 Implications

### 6.1 Definitive conclusions (conditional on Tate 1966)

**C1 (Proven, classical).** For any ordinary elliptic curve E/F_p and any
isogeny φ: E → E' defined over F_p, the trace of Frobenius satisfies
trace(Frob_{E'}) = trace(Frob_E). This is a classical consequence of the
Tate isogeny theorem.

**C2 (Proven, classical).** The anomalous family (trace = 1), the MOV-
vulnerable family (k = ord_N(p) small), and the GHS/Weil-descent-vulnerable
family are all **isogeny-class invariants** over F_p: two F_p-isogenous ordinary
curves have the same anomalous status, the same embedding degree k, and the same
GHS vulnerability profile.

**C3 (Proven, classical).** No ordinary F_p-isogeny path of ANY finite length
connects a non-anomalous ordinary curve to an anomalous ordinary curve over F_p.
The ordinary F_p-isogeny graph is disconnected between distinct trace classes.
rho_special = 0 is not a finite-scale artifact; it is a mathematical certainty
for ANY non-anomalous starting curve at ANY bit size, for ANY ordinary ell.

**C4 (Mechanistic gap, derived from C1–C3).** H-IT-001's mechanism — using
an ordinary isogeny path from a generic curve to an anomalous, MOV, or GHS
endpoint — is **structurally infeasible** for all three named special families.
The log-transfer formula (log_E(Q) = log_{E'}(φ(Q)) × deg-scaling) is correct
as stated, but the prerequisite (existence of such a path) fails mathematically.
This is a **scoped mechanistic refutation of the ordinary isogeny route** for
the three named families.

**C5 (Scope qualification).** This analysis addresses ordinary isogenies over
F_p with degree coprime to p. It does not address:
- Supersingular isogenies (which lie in a separate graph component for p > 3).
- Isogenies defined over extension fields F_{p^k} with k > 1.
- Other potential mechanisms not involving ordinary F_p-isogenies.

**C6 (H-IT-001 status).** H-IT-001 remains at `specified` per the task
constraint. The mechanistic gap identified here is not automatically a full
rejection: the experiment was never executed cleanly, and the hypothesis could
potentially be reformulated to a mechanism that does not rely on ordinary
isogenies crossing trace-class boundaries.

### 6.2 Open questions

**Q1.** Are there special curve families where the "special" property is NOT
an isogeny-class invariant over F_p? Such a family would be required for any
positive version of H-IT-001 via ordinary isogenies.

Answer (conjecture, not proved here): Most cryptographically interesting
special families (anomalous, MOV, CM with specific CM field, GHS) are defined
by arithmetic properties that depend only on #E(F_p) or the Frobenius
eigenvalues — which are isogeny-class invariants. A counterexample would need
to be a family defined by something that varies WITHIN an isogeny class (e.g.,
the CM conductor f, or the j-invariant, or the specific Weierstrass model).
It is unclear whether any such family has cryptographic significance.

**Q2.** Do supersingular isogenies provide a trace-changing path? Over F_p,
no (ordinary curves and supersingular curves are in distinct F_p-isogeny
classes by Tate's theorem). Over F_{p^k}, the question is more subtle and
remains open as a potential mechanism direction.

**Q3.** Can H-IT-001 be reformulated to ask a meaningful question WITHIN a
single isogeny class? For example: within the isogeny class of a random curve
(specific t ≠ 1), are there curves with weak DLP structure not captured by
the known special families? This is a well-defined question but requires
identifying a new weakness that correlates with CM conductor or j-invariant
within the class.

### 6.3 Pareto assessment

All three named special families (anomalous, MOV, GHS) require an ordinary
isogeny path from a generic curve — which this analysis proves impossible.
The ONLY paths that could beat Pollard rho on a generic curve via isogeny
transfer would require either:
(a) A new special family whose weakness is not an isogeny-class invariant, or
(b) A transfer mechanism not based on ordinary F_p-isogenies.

No algorithm achieving this is currently known. The analysis is **dominated by
Pollard rho at exponent 1/2** for generic prime-field ECDLP; this analysis
does not move the asymptotic frontier.

---

*Analysis completed by Idea Generator role, TASK-20260804-002.*  
*No experiment, no code, no hypothesis status change.*
