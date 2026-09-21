# C_t Minimality Lemma — Formalization of Corrected Claim C

**Task:** TASK-20260805-008  
**Batch:** BATCH-122  
**Goal:** GOAL-ECDLP-001  
**Role:** Mathematical Analyst (Coordinator-authorized)  
**Date:** 2026-08-05  
**Requested policy:** coordinator-orchestration-code  
**Dispatch:** DEC-20260805-364e9e (formalization of Corrected Claim C as a standalone lemma/theorem)  
**Primary source:** TASK-20260805-004 (BATCH-121), Corrected Claim C  
**Status:** analysis artifact; no record IDs minted; awaits independent review before promotion

---

## 1. Precise statement of the theorem

**Setting.** p prime, E/F_p an elliptic curve, ⟨G⟩ = E(F_p) the full group of prime
order N (the case used by the program). x: E(F_p) → F_p ∪ {∞} is the Weierstrass
x-coordinate, with x(O) = ∞. The set X(E) = x(E(F_p) \ {O}) has size (N−1)/2, and
every x ∈ X(E) has exactly two preimages P, −P (N is odd, so no 2-torsion; each
x-value's preimage pair is {P, −P} ⊂ E(F_p)). For t ∈ F_p define the **threshold
factor base**

    F_t = {P ∈ E(F_p) : x(P) < t},   t ∈ {1, …, p−1},

where < is the canonical integer order on representatives {0, …, p−1}. Since
|F_t| = 2·|[0, t) ∩ X(E)|, B = |F_t| is always even.

**Definition of the oracle.** For t ∈ F_p,

    C_t(P) = 1 ⟺ x(P) < t,   C_t(O) = 0.

**Theorem 1 (C_t-minimality, formal).** Let E/F_p, N, G, t be as above with the
non-degeneracy condition

    ∅ ≠ F_t ≠ E(F_p)      (equivalently: C_t is not constant on E(F_p)).

Then:

**(a) Identification.** C_t identifies the threshold factor base F_t: for every
P ∈ E(F_p), C_t(P) = 1 ⟺ P ∈ F_t, and the test costs exactly one oracle query.

**(b) Non-simulability.** C_t is not GGM-simulable. It is a Tier-3 oracle in the
BATCH-060 taxonomy: non-simulable, encoding-dependent, and publicly computable
(does not require the discrete log k).

**(c) Query-cost minimality.** Any oracle that identifies F_t must transmit at
least one bit per queried point; C_t transmits exactly one bit.

**(d) Uniqueness in the order-based class.** Up to bit complement, C_t is the
unique order-based oracle identifying F_t: if O is order-based and
O(P) = 1_{P ∈ F_t} for all P, then O = C_t or O = ¬C_t on E(F_p).

**(e) No strictly weaker order-based identifier.** No order-based 1-bit oracle
strictly weaker than C_t identifies F_t; the only order-based oracles strictly
weaker than C_t (in the pointwise information order, Definition 5) are the two
constant oracles, and no constant oracle identifies a non-empty, non-full F_t.

**Corollary (the corrected claim, precisely scoped).** C_t is the minimal
non-simulable order-based oracle enabling threshold factor-base membership
identification: minimal in query cost (one bit, clause c), unique in the
order-based class (clause d), with no strictly weaker order-based identifier
(clause e).

**Reading of "minimal".** The word "minimal" is only well-defined when the three
clauses (c)–(e) are stated separately. Clause (e) is the precise content of the
informal "there is no strictly weaker non-trivial threshold oracle between 0-bit
and C_t": in the pointwise information order the interval of oracles strictly
between a constant and C_t is empty. It is essential to read "between" correctly
(see Lemma 5 and Section 5): distinct thresholds are **incomparable**, not
comparable, so there is no chain along which C_t would be the "weakest".

---

## 2. Formal definitions

**Definition 1 (GGM instance, handles).** A Shoup-style GGM instance is
(Z/N, +) together with an injective encoding σ: Z/N → {0,1}^κ (random labels).
The adversary holds labels ("handles") and may (i) compute σ(a+b) from σ(a), σ(b)
by the group oracle, (ii) test equality of labels, (iii) read the public
parameters (p, N, the Weierstrass equation of E). It receives G and Q = [k]G as
labeled inputs; k is secret. A *generic algorithm* is one that operates only
through these interfaces. [BATCH-060 §Formal Setup]

**Definition 2 (comparison oracle and factor base).** With the notation of
Section 1, C_t(P) = [x(P) < t] is the **threshold (comparison) oracle**. The
canonical order < on F_p is part of the *finite-field encoding*: the abstract
group Z/N carries no order, and the order is not invariant under the group law.
This is the property that makes C_t encoding-dependent.

**Definition 3 (order-based oracle).** A 1-bit oracle O: E(F_p) → {0,1} is
**order-based** if there exist τ ∈ {0, …, p} and ε ∈ {0,1} such that

    O(P) = 1_{x(P) < τ} ⊕ ε

for all P — i.e., the 1-set is a prefix {x < τ} (ε = 0) or a suffix {x ≥ τ}
(ε = 1) of the ordered x-values. Constants arise exactly for τ = 0 (prefix
empty) and τ > max X(E) (prefix contains all of X(E)). Two thresholds τ, τ′
define the *same* oracle on E(F_p) iff no curve point has x-coordinate in the
open strip between them; oracles are identified as functions on E(F_p).

**Definition 4 (simulable / non-simulable / encoding-dependent / Tier 3).**
An augmented oracle O is **GGM-simulable** if there exists a generic algorithm S
(the simulator) that answers every O-query from the transcript (labels, group-op
results, public parameters) with O(1) overhead per query, such that for every
instance and query sequence S's answers are distributed identically to O's on
the real instance. O is **non-simulable** if no such S exists; equivalently,
there exist two instances that are GGM-indistinguishable (identical abstract
group structure and identical query-transcript distribution) on which O's
answers differ — the *witness pair*. O is **encoding-dependent** if its answers
depend on the concrete coordinate functions (x, y) of the Weierstrass model
beyond the group structure. The BATCH-060 taxonomy: Tier 1 = simulable; Tier 2 =
non-simulable and *privately computable* (evaluating O requires the secret k,
e.g., the jet oracle); Tier 3 = non-simulable, encoding-dependent, and *publicly
computable* (evaluable from the concrete model without k, e.g., the elliptic-net
and x-coordinate oracles). [BATCH-060 §Formal Setup, §Three-tier taxonomy]

**Definition 5 (pointwise information order).** For oracles O₁, O₂ write
O₂ ≼ O₁ iff O₂ = h ∘ O₁ for some h: {0,1} → {0,1}: O₂'s answer on each point is
a function of O₁'s answer on that point ("O₂ is determined by O₁"). Write
O₂ ≺ O₁ for strict, and O₁ ≡ O₂ iff both hold. This is the coarsest reasonable
"O₂ is weaker than O₁" relation for single-query oracles; it matches the IC
usage (one membership bit per point). Section 4.5 states what the theorem does
not claim about adaptive multi-query orders.

**Definition 6 (identification task).** The **threshold factor-base membership
identification task** at threshold t is: given P, compute 1_{P ∈ F_t}. An oracle
O *performs* the task iff O = 1_{F_t} as functions on E(F_p); it *enables* the
task iff it can perform it within the intended query budget (here: one query).

---

## 3. Lemmas and proof sketch

### Lemma 1 (identification). For every t, C_t performs the membership task at
threshold t with exactly one query per point.

*Proof.* Immediate from the definitions: F_t = {P : x(P) < t} = {P : C_t(P) = 1}.
The query returns the membership bit directly; no further queries, no group
operations, no binary search. Ref: TASK-20260805-004 §Q1 ("one C_{B/p} call"),
Corrected Claim C.

### Lemma 2 (non-simulability, Tier 3). If ∅ ≠ F_t ≠ E(F_p), C_t is not
GGM-simulable, and it is publicly computable without k.

*Proof sketch.* **Witness construction (same curve, two secrets).** Since
F_t ≠ ∅ and F_t ≠ E(F_p), there exist scalars k₁, k₂ ∈ {1, …, N−1} with
x([k₁]G) < t ≤ x([k₂]G). Consider the two instances (E, G, Q₁ = [k₁]G) and
(E, G, Q₂ = [k₂]G). Their GGM transcripts are identically distributed: labels
are uniform random injections, and the group-oracle answers depend only on the
abstract group law, which is the same. Yet the handle Q is queried as [k_i]G and
C_t answers 1 in instance 1 and 0 in instance 2 at the same transcript point. No
deterministic (or randomized) simulator can be correct on both, since its
answers are functions of a transcript that does not distinguish the instances.
Hence C_t is non-simulable. **Public computability.** C_t(P) is evaluated from
the concrete point P's x-coordinate; no knowledge of k is required. By the
BATCH-060 taxonomy this is Tier 3 (encoding-dependent, like the x-coordinate
control oracle and the elliptic-net oracle, of which C_t is a 1-bit coarsening).
Ref: TASK-20260805-004 §Q3 (non-simulability witness and Tier-3 classification),
BATCH-060 §Encoding control, §Three-tier taxonomy, Oracle B.

*Remark (encoding witness).* BATCH-060-style witnesses may instead use two
curves E₁, E₂ with #E₁ = #E₂ = N and matched labels; the same-curve k-witness
above is stronger (it needs no second curve) and its existence condition is
exactly the non-degeneracy condition ∅ ≠ F_t ≠ E(F_p). See correction C4.

*Boundary condition.* If F_t = ∅ or F_t = E(F_p), C_t is constant on the curve,
hence trivially simulable (as a constant). The non-degeneracy condition is
therefore not an artifact: it is the exact condition under which non-simulability
holds. For the IC factor base, |F_t| = B with 2 ≤ B ≤ N−2 by construction, so
the condition holds. Ref: TASK-20260805-004 §Q3 (straddling requirement).

### Lemma 3 (one bit is necessary). Any oracle performing the membership task at
threshold t with ∅ ≠ F_t ≠ E(F_p) transmits at least one bit per point; C_t
transmits exactly one.

*Proof.* F_t and its complement are both non-empty, so the answer to
"P ∈ F_t?" takes both values; a constant oracle cannot perform the task, and a
1-bit response is the minimal positive information content. C_t attains it.
Ref: TASK-20260805-004 §Q3 ("0-bit (trivial) oracle provides no information").

### Lemma 4 (uniqueness in the order-based class). If O is order-based and
performs the membership task at threshold t, then O = C_t or O = ¬C_t on
E(F_p).

*Proof.* O = 1_{x < τ} ⊕ ε for some (τ, ε). Requiring O(P) = 1_{P ∈ F_t} for all
P forces {x(P) : O(P) = 1} ∩ X(E) = [0, t) ∩ X(E). Hence [0, τ) ∩ X(E) =
[0, t) ∩ X(E) (if ε = 0) or X(E) \ [0, τ) = [0, t) ∩ X(E) (if ε = 1), giving
τ with the same effective cut as t; i.e., O ≡ C_t on E(F_p), concretely O = C_t
(ε = 0) or O = ¬C_t (ε = 1). Ref: Definition 3, Definition 6.

### Lemma 5 (no strictly weaker order-based identifier; structure of the
threshold family).

**(i) Interval structure.** For every non-constant oracle O, the interval
(O′ : 0 ≺ O′ ≺ O) in the pointwise order (Definition 5) is empty: the
predecessors of O are exactly {0, 1, O, ¬O} (h: {0,1} → {0,1} has four values),
so nothing lies strictly between a constant and O. This holds for **every**
non-constant 1-bit oracle — including random hashes — so the "nothing between
trivial and C_t" statement is true but *vacuous* unless combined with
Lemma 4 (see correction C1).

**(ii) Thresholds form an antichain.** For two thresholds s < t with an
effective cut in between (∃P with x(P) ∈ [s, t)), the oracles C_s and C_t are
incomparable: taking points A, B, C with x < s, s ≤ x < t, x ≥ t respectively,
their oracle pairs are (C_s, C_t) = (1,1), (0,1), (0,0). Then A, B witness
C_s ⊀ C_t (same C_t value 1, differing C_s), and B, C witness C_t ⊀ C_s (same
C_s value 0, differing C_t); hence neither oracle is a function of the other. If
[s, t) contains no
x-value of the curve, then C_s ≡ C_t as oracles on E(F_p).

**(iii) Consequence.** The only order-based oracles identifying F_t are C_t and
¬C_t (Lemma 4); neither is strictly below C_t (¬C_t ≡ C_t, and C_t itself is not
strict); every strict predecessor of C_t is constant (i) and no constant
identifies F_t (Lemma 3). Therefore no order-based oracle strictly weaker than
C_t identifies F_t — under the pointwise order, and in fact under any order that
refines "O₂'s answers are determined by O₁'s answers" (the only candidate
identifiers are C_t, ¬C_t). Ref: TASK-20260805-004 §Q3 ("there is no strictly
weaker non-trivial threshold oracle between 0-bit and C_t"), corrected per
Section 5.

### Theorem 1. Conjunction of Lemmas 1–5; the Corollary is clause-by-clause.

*Proof of the Corollary.* (a)+(c) give "minimal in query cost"; (d) gives
"unique order-based identifier"; (b) gives "non-simulable (Tier 3)"; (e) gives
"no strictly weaker order-based identifier". The conjunction is exactly the
corrected claim. Note the theorem is **unconditional**: it does not invoke
H-PSEUDO, ECCG, or any heuristic, and no complexity claim about index calculus is
made here. The IC-level consequence is cited, not reproved (Section 4.4).

---

## 4. Scope — what the theorem does and does not claim

### 4.1 The claim lives in the order-based class

Minimality (d)+(e) is a statement about the family {C_τ, ¬C_τ} ∪ {constants}
only. Nothing in Theorem 1 constrains oracles that are not order-based
1-bit functions of x.

### 4.2 Random 1-bit hash of x — equally minimal, not order-based

Let h: F_p → {0,1} be a balanced random function and g(P) = h(x(P)).

| Oracle | 1 bit | order-based | non-simulable | identifies F_t? | verdict |
|---|---|---|---|---|---|
| C_t | yes | **yes** | yes (Tier 3) | **yes** | minimal order-based identifier |
| ¬C_t | yes | yes (suffix) | yes | no (identifies the complement) | ≡ C_t |
| constant 0/1 | 0 bits | trivially | no (simulable) | no | strictly weaker, useless |
| g = h∘x (random hash) | yes | **no** | yes (for all but a 2^{−Ω(N)}-fraction of h) | no: Pr_h[g = 1_{F_t} on E(F_p)] = 2^{−N} | equally minimal in oracle complexity, **not order-based**, task-failing |
| x(·) (full coordinate) | ⌈log₂ p⌉ bits | no (multi-bit) | yes (Tier 3, control) | yes (trivially) | strictly more informative |

Consequences: (i) g is as cheap as C_t and as non-simulable, so "minimality"
*without* the order-based qualifier is false — the honest statement restricts to
the order-based class; (ii) g's 1-set is a random subset of X(E), so its
correlation with F_t is O(N^{−1/2}) for random h and its identification
probability is 2^{−N}: it cannot certify factor-base membership at any scale
(the "g-IC is not sub-rho" control of IDEA-62ef74's minimality prediction is
consistent with this exact statement). Ref: TASK-20260805-004 §Q3 ("a random-1-bit
hash … equally minimal in oracle complexity but less useful for IC"), scoped here
to the identification task.

### 4.3 Multi-bit oracles and the parameterized family

The theorem says nothing about multi-bit oracles: the full x-coordinate oracle is
strictly more informative than C_t (and than any fixed threshold oracle). The
*family* {C_s : s ∈ F_p} recovers the full coordinate in O(log p) adaptive
queries (binary search on s). A **fixed** C_t cannot (correction C3). Both
statements are outside Theorem 1; the fixed-vs-family distinction matters only
for coordinate recovery, not for membership identification.

### 4.4 The IC-level consequence is cited, not proved

"Enables IC" (the full claim in TASK-20260805-004's Claim C) rests on Corrected
Claim A of TASK-20260805-004: with the factor-base threshold t chosen so
|F_t| = B, membership costs one C_t query per point, adding O(1) overhead per
relation check and leaving Semaev IC at L[1/2, c] << sqrt(N) unconditionally
(sub-rho with heuristic yield). Theorem 1 supplies the oracle-level ingredient
(identification, minimality, non-simulability) of that claim and nothing more;
it is not a complexity theorem about index calculus.

### 4.5 Explicitly not claimed

- No claim about adaptive multi-query information orders (e.g., computing C_s
  from group combinations of C_t-queried handles); the pointwise order is the
  theorem's scope, matching the one-bit-per-point IC usage.
- No claim that every encoding-dependent oracle is a function of x alone: oracles
  depending on y (e.g., the sign oracle y(P) < 0) or on the full point exist and
  are not order-based in the sense of Definition 3 (correction C7).
- No claim that "minimal" holds among *all* 1-bit oracles — it does not
  (Section 4.2).
- No heuristic dependence of any kind (Section 3, Theorem 1 remark).

---

## 5. Corrections to the Claim C framing in TASK-20260805-004

The corrected claim is directionally right; the formalization above required the
following corrections to its framing:

| # | Item in TASK-20260805-004 (or its source IDEA-62ef74) | Correction |
|---|---|---|
| C1 | "C_t is the MINIMAL non-simulable 1-bit oracle enabling IC" / "there is no strictly weaker non-trivial threshold oracle between 0-bit and C_t" | Under the natural pointwise order, *every* non-constant 1-bit oracle (including a random hash) has an empty interval between the trivial oracle and itself (Lemma 5(i)). "Minimality" is vacuous without (i) the order-based restriction and (ii) the task-specific reading (uniqueness, Lemma 4). The theorem's clauses (c)–(e) are the precise replacement. |
| C2 | "the weakest ORDER-BASED non-simulable oracle" / "between 0-bit and C_t" | Thresholds at distinct effective cuts are *incomparable* (Lemma 5(ii)): {C_s} is an antichain, not a chain, so "weakest" has no meaning as a chain-theoretic term; the tight statement is "unique (up to complement) and one-bit-minimal with no strictly weaker order-based identifier". |
| C3 | Q1: "Full x-coordinate recovery costs O(log p) adaptive C_t calls" (same claim in IDEA-62ef74 §mechanism) | False for a fixed threshold: C_t(P) is constant under repeated queries, and binary search requires queries C_s with varying s — i.e., the *parameterized family* {C_s}. Fixed-C_t coordinate recovery via multiplication maps (x([a]P) = φ_a(x)/ψ_a(x)² is rational in x(P); cf. TASK-20260805-005 §A.1 for a = 2) is a different, non-binary-search problem and is not O(log p). The membership-bit usage is unaffected (IC needs only C_{B·p/N}-style single thresholds). |
| C4 | Q3: "Such pairs exist for any t in (0,p)" (two-curve witness) | The asserted universal existence is unproved; the formal non-simulability condition is exactly ∅ ≠ F_t ≠ E(F_p) via the *same-curve* k-witness (Lemma 2), which needs no second curve. The two-curve (encoding) witness exists generically but need not hold for pathological (E, t); when F_t ∈ {∅, E(F_p)} C_t is constant on the curve and *is* simulable. |
| C5 | Claim C merges two levels: "minimal non-simulable order-based oracle **enabling** threshold factor-base membership identification" | "Identification" (task level: Theorem 1) is the formalizable claim; "enabling IC" (algorithmic level) is Corrected Claim A's content and is cited (Section 4.4). Non-simulability (a model property) and minimality (a task-information property) are a conjunction of separate lemmas, not a single lattice fact. |
| C6 | Q3: "any 1-bit threshold enables IC" | Imprecise: only the threshold t matching the chosen factor base identifies *that* F_t (Lemma 4); every other threshold identifies a different prefix. The precise statement is the bijection between effective cuts and order-based identifiers. |
| C7 | IDEA-62ef74: "every non-simulable oracle in the GGM context encodes some function f(x(h))" | False in general: y-dependent oracles (e.g., sign of y(P)) are encoding-dependent, non-simulable, and not functions of x alone. The corrected claim survives because it is restricted to the order-based class. |

None of C1–C7 affects Corrected Claims A, B, or D of TASK-20260805-004, which
are outside this lemma's scope.

---

## 6. Proof-architecture audits (inventor protocol §8)

- **Baseline reproduction.** The theorem formalizes exactly Corrected Claim C of
  TASK-20260805-004; each clause is a lemma whose proof references the
  corresponding §Q1/§Q3 argument, reproduced and tightened. No new claims are
  introduced beyond the framing corrections of Section 5.
- **Observation collision.** The main collision risk — "minimal 1-bit oracle" —
  was found and reported as C1/C2: the naive statement is satisfied vacuously by
  *every* non-constant 1-bit oracle, including the random-1-bit-hash control.
  The nearby-object control (Section 4.2, random hash) is the required
  discrimination test and separates the order-based claim from the vacuous one.
- **Quantifier order.** The theorem is ∀(E, G, t) [∅ ≠ F_t ≠ E(F_p) ⟹ (a)–(e)]
  with witnesses for non-simulability (∃k₁, k₂, Lemma 2) and for incomparability
  (∃A, B, C, Lemma 5(ii)) constructed explicitly from the non-degeneracy
  condition; the uniqueness clause is ∀O [order-based ∧ identifies ⟹ O ∈
  {C_t, ¬C_t}]. No quantifier swap is hidden anywhere; in particular the
  non-simulability witness's *existence* precedes any use of the oracle, and the
  theorem asserts no uniqueness of the witness pair.
- **Method ceiling.** The strongest claim certified here is identification-task
  minimality (Theorem 1). The "enables IC / complexity-equivalence" level is
  *not* certified by this proof and is explicitly deferred to Corrected
  Claim A (Section 4.4). Adaptive-query-order minimality is out of scope
  (Section 4.5) and is a genuine open refinement, not a claimed result.

---

## 7. References

- TASK-20260805-004 (BATCH-121): `oracle_hpseudo_analysis.md` — Corrected
  Claims A–D, §Q1 (one-call membership, IC complexity), §Q3 (non-simulability
  witness, Tier-3 classification, oracle minimality).
- IDEA-20260805-62ef74 (BATCH-120, TASK-20260805-002): mechanism, oracle
  minimality, minimality control (random-hash g).
- BATCH-060/TASK-20260804-051: `ggm_analysis.md` — simulability definition,
  encoding (x-coordinate) control oracle, three-tier taxonomy, k-witness style
  (Oracle A).
- TASK-20260805-005 (BATCH-121): `closure_and_multi_target.md` §A.1 — x([a]P)
  rational in x(P) via division polynomials (used in correction C3).
- KN-FIND-9d2f56: Betti–Yield duality (context only; not used in Theorem 1).
- H-PSEUDO-83817b: hypothesis text (explicitly unused; the theorem is
  unconditional).
- DEC-20260805-364e9e: dispatching decision (per handoff).

---

*Formalized by mathematical analyst, TASK-20260805-008, BATCH-122, GOAL-ECDLP-001.*  
*Next step: independent review of Theorem 1 and Section 5 before any promotion.*
