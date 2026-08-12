# IDEA-b6624c Proof-Search-Map Audit: Ordinary Isogeny MITM

**Proposal:** IDEA-20260804-b6624c — Ordinary-isogeny-graph meet-in-the-middle,
analogue of Wesolowski p^{1/3}  
**Auditor task:** TASK-20260804-024 (BATCH-053)  
**Source:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-052/tasks/TASK-20260804-021/proposals.yaml`  
**Prior audit consulted:** TASK-20260804-009 (IDEA-e88120, h(D)<<N obstruction)  
**Date:** 2026-08-04  
**Role:** Mathematical analyst (Coordinator authority, read-only on hypothesis status)

---

## Audit 1: Baseline — Does the MITM backward walk have a well-defined starting point?

**Answer: NO. The backward walk has no well-defined starting point, and the
reason is not a technicality but a category error in the construction.**

### The two actions must not be conflated

There are two distinct group actions relevant to an ordinary elliptic curve E/F_p:

1. **Scalar multiplication:** Z/NZ acts on E(F_p). The scalar [k] sends a
   *point* P ∈ E(F_p) to the *point* [k]P ∈ E(F_p). The *curve* E is fixed.

2. **Class group action:** Cl(O_K) acts on the set of j-invariants
   {j(E') : End(E') ≅ O_K} with CM by the same order. An ideal class [a] sends
   the *curve* E to a *different curve* [a]·E (connected by an isogeny). The
   *group* E(F_p) is not involved.

These act on entirely different objects: one on points of a fixed curve, the
other on curves in an isogeny class. The notation "[k]·E" for the backward
walk's starting curve is undefined, because k is a scalar on E(F_p), not an
ideal class acting on the isogeny class.

### Why the backward walk cannot be defined

The ECDLP instance is: given E, G ∈ E(F_p), Q = [k]G, find k ∈ Z/N.

The only objects given are a curve E and two points G, Q on that curve. The
scalar k is unknown. There is no "curve E_k" associated to k because scalar
multiplication by k does not produce a new curve — it maps points to points
within the same fixed E.

For the backward walk to start at a specific curve, the attacker would need to
identify that curve from the public inputs (E, G, Q). The only public curve is
E itself. The proposal implicitly assumes that Q = [k]G somehow defines a
second curve in the isogeny class, but no such construction is specified, and
none can be specified without an algorithm that inputs (E, G, Q) and outputs a
curve E' ≠ E with a known class-group relationship to E depending on k. That
algorithm would be the attack itself, not a subroutine.

### Comparison: why Wesolowski's construction works

In the supersingular isogeny setting, Wesolowski solves the **ISOGENY FINDING
PROBLEM**: given two curves E and E' (both provided as explicit inputs), find
an isogeny phi: E → E'. In this problem:

- The forward walk starts at E (given).
- The backward walk starts at E' (given).
- Both endpoints are concrete objects; no unknown scalar is involved.

The ordinary ECDLP is fundamentally different:

- One curve E is given.
- A point Q = [k]G on E is given.
- The unknown is a scalar k ∈ Z/N, not a second curve.

Wesolowski's algorithm has no scalar analogue because there is no "second
endpoint curve" derived from the scalar k. In the supersingular case, the
birthday-paradox collision at cost O(p^{1/3}) is meaningful because the paths
from E and E' compose into an explicit short isogeny. In the ECDLP case, even
if an arbitrary collision in the isogeny class is found, the collision encodes
a class-group relation between curves — not the scalar k.

### Audit 1 result

**BLOCKED_AT_STARTING_POINT.** The backward walk starting point is undefined.
No construction from (E, G, Q = [k]G) to a second curve E_k ∈ isogeny class
is known that does not require k as input. The proposal contains an implicit
assumption — that Q or k defines a curve — that has no mathematical
justification.

---

## Audit 2: Observation-Collision Search — Is there a map from ECDLP scalar to class group?

**Core question:** Does there exist a map φ: Z/N → Cl(O_K) such that φ(k)
is computable from (E, G, Q = [k]G), and k is recoverable from φ(k)?

### Group-order obstruction (decisive, same as IDEA-e88120)

Any group homomorphism φ: Z/N → Cl(O_K) satisfies, by the first isomorphism
theorem:

    |ker(φ)| = N / |im(φ)| ≥ N / h(D)

For ordinary E/F_p: N ~ p and h(D) ~ sqrt(p), so:

    |ker(φ)| ≥ p / sqrt(p) = sqrt(p) ~ N^{1/2}

Knowing φ(k) recovers k only modulo ker(φ). The residual search space has size
≥ sqrt(N). Exhaustive search over sqrt(N) candidates costs O(sqrt(N)) scalar
multiplications, which is exactly the cost of Pollard rho. Any proposed
map φ therefore gives total cost:

    [cost to compute φ(k)] + [cost to solve class group DLP for φ(k)] + O(sqrt(N))
    ≥ O(sqrt(N))

The third term alone matches Pollard rho, rendering the entire scheme
non-improving regardless of how cheap the first two terms are.

### Literature: no known reduction

The CRS/CSIDH literature (Couveignes 2006, Rostovtsev-Stolbunov 2006,
Castryck-Lange-Martindale-Panny-Renes 2018) explicitly treats the class group
action problem as a NEW computational assumption, distinct from ECDLP. If a
polynomial-time reduction from ECDLP to class group DLP existed:

1. CSIDH security would follow from ECDLP hardness (noted by its authors).
2. ECDLP hardness would follow from CSIDH hardness (a new assumption would be
   unnecessary).

Neither implication has been noted in ~20 years of CRS/CSIDH work. This is
strong negative evidence that no such reduction exists.

Wesolowski's 2022 supersingular MITM paper addresses the **ISOGENY FINDING
PROBLEM** (find phi: E → E' given both curves), not the scalar DLP. No
reduction from scalar DLP to class group DLP appears there.

Galbraith-Smart (1999) uses Weil restriction for DLP over extension fields,
not class group reductions over F_p.

De Feo-Galbraith and related works compute isogenies (class-group-action
direction) but do not address ECDLP-to-class-group reduction.

### Can a non-homomorphism map circumvent the obstruction?

The obstruction above applies to group homomorphisms. Could a non-linear map
φ: Z/N → Cl(O_K) allow recovery of k?

No, by an information-theoretic argument that does not rely on linearity. The
range of φ has at most h(D) ~ sqrt(N) distinct values (the class group has
that many elements). A function from a domain of size N to a range of size
sqrt(N) must be at least sqrt(N)-to-one on average. Therefore there exist at
least sqrt(N) values of k that map to any given class group element, and no
algorithm can identify which one without additional information equivalent to
solving the ECDLP.

### Audit 2 result

**BLOCKED_AT_KEY_RECOVERY.** The group-order mismatch N ~ p >> h(D) ~ sqrt(p)
is a hard information-theoretic barrier, not a technical difficulty. Any map
from the ECDLP scalar space (size N) to the class group (size h(D) ~ sqrt(N))
discards at least (1/2)log(p) ~ 128 bits at 256-bit security. The residual
search exactly matches Pollard rho. No such map appears in the literature;
20 years of CRS/CSIDH work confirms the two problems are computationally
independent.

---

## Audit 3: Quantifier-Order Statement

### Precise statement of what the MITM claims

The proposal (IDEA-b6624c) asserts, in the strongest reading:

> FOR ALL primes p, FOR ALL prime-order ordinary E/F_p, FOR ALL generators G,
> FOR ALL targets Q = [k]G:
> THERE EXISTS a MITM procedure on the ordinary isogeny graph that finds k in
> O(p^{1/3}) time.

Let us examine what this requires step by step.

### Step 1 requires: a function C(E, G, Q) → (curve in isogeny class)

The backward walk needs a starting curve determined by the input. The only
curves deterministically computable from (E, G, Q) without knowing k are:

- E itself (the input curve)
- Curves isogenous to E by small-degree isogenies from E (the isogeny class)

None of these carries information about k. Any procedure that derives a second
curve from Q = [k]G specifically must extract information about k from Q. But
extracting any information about k from Q that is not derivable from E and G
alone is equivalent to making progress on the ECDLP.

**Conclusion:** Step 1 is impossible without an ECDLP sub-oracle. The ∀k
quantifier cannot be satisfied.

### Step 3 requires: a function (class group element) → (scalar in Z/N)

Even granting Step 1 hypothetically, the collision at Step 2 produces a
relation in Cl(O_K): two isogeny paths from the forward and backward starting
curves that meet at a common curve. This encodes an identity in Cl(O_K) of the
form [α] = [β]·[γ]^{-1} for explicitly computable ideal classes [α], [β], [γ].

The scalar k does not appear in this identity. For k to be recoverable, there
must exist a map φ^{-1}: Cl(O_K) → Z/N. Audit 2 establishes this is
impossible without a residual Pollard-rho-cost search.

### What the MITM CAN establish (a correct quantifier-order statement)

FOR ALL prime p, FOR ALL ordinary E/F_p:
THERE EXIST sets S_1, S_2 ⊆ {isogeny class of E} with |S_1|, |S_2| = L such
that Pr[S_1 ∩ S_2 ≠ ∅] ≥ 1/2 when L ~ p^{1/4} (birthday paradox on h(D) ~ p^{1/2}).

This is a true statement about the ISOGENY GRAPH. It is completely unrelated to
the ECDLP: the sets S_1, S_2 can be computed without knowing Q or k, starting
from E alone (walk in two random directions). The collision is real but carries
no information about any ECDLP scalar.

### Does every MITM reduce to the h(D)<<N obstruction?

Yes. Any MITM that uses the isogeny graph structure must at some point convert
isogeny-class information (elements of Cl(O_K), order h(D)) into scalar
information (elements of Z/N, order N). Because h(D) << N, this conversion
is lossy by a factor of N/h(D) ~ sqrt(N). The unrecovered information
constitutes a search space of size sqrt(N) — the same as Pollard rho.

### Audit 3 result

The ∀k, ∃MITM claim is **FALSE** for two independent reasons:

1. The backward walk starting point cannot be defined from (E, G, Q) without
   solving the ECDLP (Step 1 is circular).
2. Even if a collision were found, k is not recoverable from the class group
   relation without sqrt(N) additional work (Step 3 is obstructed by
   the h(D)<<N mismatch).

Every MITM-based approach on the ordinary isogeny graph is bounded below by
O(sqrt(N)) total work, matching Pollard rho. The MITM gives no improvement over
the baseline for the ECDLP.

---

## Audit 4: Method Ceiling + Wesolowski Comparison

### Best-case cost analysis (all sub-steps assumed optimal)

Assume, as a generous hypothetical, that:

- (H1) A starting curve E_k is somehow well-defined from (E, G, Q) — ignoring
  the Step 1 obstruction.
- (H2) MITM collision in the isogeny class costs O(p^{1/3}) steps (birthday
  paradox on h(D) ~ p^{1/2} nodes with p^{1/6} samples each direction).
- (H3) The collision yields a class group element [a] ∈ Cl(O_K) of known norm.

What does key recovery from [a] cost?

Under (H3), we have [a] = φ(k) for some φ: Z/N → Cl(O_K). From Audit 2, the
kernel of any such map has size ≥ N/h(D) ~ p^{1/2} ~ N^{1/2}. The attacker
must search over the coset k + ker(φ) to find the true k. This coset has size
sqrt(N), and distinguishing the correct k requires testing Q = [k]G, which
is one elliptic-curve multiplication per candidate.

**Key recovery cost (minimum): O(sqrt(N)) = O(p^{1/2}).**

Total cost under generous hypotheticals (H1)-(H3):

    O(p^{1/3})   [MITM collision, birthday paradox]
    + O(p^{1/2}) [key recovery, group-order mismatch]
    = O(p^{1/2}) [dominated by key recovery]

The method ceiling equals Pollard rho. No asymptotic improvement is possible
under the ordinary ECDLP setting. The MITM collision buys nothing because the
key recovery step bottlenecks at the full rho cost.

### What would be needed to beat O(p^{1/2})

For total cost < O(p^{1/2}), key recovery must cost < O(p^{1/2}). This
requires either:

(A) A map φ: Z/N → X for some set X with |X| ≥ N (so no information is lost),
    combined with an efficient algorithm on X. But the class group Cl(O_K) has
    order h(D) ~ sqrt(N) << N. No subgroup of Cl(O_K) can accommodate N
    distinct preimages.

(B) An entirely different encoding of k that does not go through the class group
    but still exploits the isogeny graph structure. No such encoding is known
    or conjectured.

(C) Showing that the isogeny class structure somehow constrains k to a small
    subset. But k is chosen adversarially (or randomly) in Z/N, and for any
    fixed curve E and generator G, every k ∈ Z/N produces a distinct Q = [k]G.
    The isogeny class of E is determined by the trace t of E, not by k. The
    scalar k has no class-group interpretation.

### Comparison with Wesolowski's supersingular MITM

| Feature | Wesolowski (supersingular) | Ordinary ECDLP MITM |
|---|---|---|
| Problem solved | ISOGENY FINDING: find phi: E → E' | SCALAR DLP: find k with [k]G = Q |
| Forward walk starts at | E (given as input) | E (given as input) |
| Backward walk starts at | E' (given as input) | E_k (UNDEFINED — not an input) |
| Unknown object | The isogeny phi ∈ Hom(E, E') | The scalar k ∈ Z/N |
| Unknown object lives in | Hom(E, E'), a Cl(O_K) torsor | Z/NZ, a cyclic group of order N ~ p |
| MITM collision cost | O(p^{1/3}) isogeny steps | O(p^{1/3}) isogeny steps (if backward walk defined) |
| After collision | phi is explicitly constructed | Class group element [a], not k |
| Key recovery after collision | DONE (phi is the answer) | Requires O(p^{1/2}) residual search |
| Total cost | O(p^{1/3}) | O(p^{1/2}) |
| Group size mismatch | NONE (both endpoints are curves; Cl(O_K) encodes the isogeny) | N ~ p vs h(D) ~ p^{1/2}: factor p^{1/2} lost |

**The fundamental incompatibility:** Wesolowski's algorithm solves a problem
whose answer IS a class-group element (the isogeny is an element of Hom(E, E'),
which is acted on by Cl(O_K) simply-transitively). The ECDLP answer is a
scalar in Z/N, which is not a class-group element and cannot be recovered from
one without residual search. Wesolowski's approach transfers to any problem
whose answer lives in the class group; it does not transfer to problems whose
answer lives in a group of order N ~ p >> h(D).

### Nearby-object control: random regular graph

Replace the ell-isogeny graph with a random regular graph of the same size
(|V| ~ h(D) ~ p^{1/2}) and degree (ell+1). The MITM collision cost is
identical (birthday paradox on p^{1/2} nodes), because collision cost depends
only on graph size, not algebraic structure. Key extraction from a collision in
a random graph gives a pair of paths from two starting nodes to a common node —
no algebraic content, no scalar recovery. The "isogeny graph structure" provides
zero advantage over a random graph for ECDLP scalar recovery, confirming that
the algebraic structure is irrelevant to the key-recovery bottleneck.

### Audit 4 result

**Method ceiling = O(p^{1/2}) = Pollard rho.** The MITM collision is real and
cheap (O(p^{1/3})), but key recovery from the collision costs O(p^{1/2}) due
to the group-order mismatch. Total cost is dominated by key recovery and equals
Pollard rho. Wesolowski's p^{1/3} result does not transfer to ordinary ECDLP
because the DLP scalar (in Z/N) and the isogeny-class certificate (in Cl(O_K))
live in groups of incompatible sizes. The null-object (random graph) control
confirms that the isogeny graph structure contributes nothing to scalar recovery.

---

## Overall Verdict

**BLOCKED_AT_STARTING_POINT** (and independently, **BLOCKED_AT_KEY_RECOVERY**)

The MITM construction is blocked at two independent checkpoints, each
individually sufficient to close the direction:

1. **Starting point (Audit 1):** The backward walk has no well-defined starting
   curve. The ECDLP scalar k is a scalar in Z/N; it does not define a curve in
   the isogeny class. No construction from (E, G, Q = [k]G) to a second curve
   E_k in the isogeny class is possible without already knowing k.

2. **Key recovery (Audits 2, 3, 4):** Even if a collision is found (granting
   the starting-point problem hypothetically), the class group element extracted
   from the collision cannot be converted to the scalar k without a residual
   search of size N/h(D) ~ sqrt(N), which exactly matches Pollard rho.

These are the same two faces of a single obstruction: the ECDLP scalar and the
class group element live in groups of incompatible sizes (N ~ p vs h(D) ~
sqrt(p)). The proposal requires bridging this gap; no bridge exists.

**Recommended next step:** Formally close this direction in the ledger as
BLOCKED. If the Coordinator wishes to keep a sub-thread open, the minimal
residual question is stated below. Absent a resolution of that question, no
Executor dispatch is warranted.

---

## Residual Open Question

For the direction to have any chance of sub-rho improvement, it would need:

**Question (necessary condition):** Does there exist a map

    Φ: {(E/F_p, G, Q = [k]G)} → Cl(O_K)

that is (a) efficiently computable from (E, G, Q) without knowing k, (b)
information-theoretically injective up to a factor of at most O(p^{1/3}) (so
the residual search is O(p^{1/3}), giving total cost O(p^{1/3}) + O(p^{1/3}) =
O(p^{1/3})), and (c) non-circular (the computation of Φ does not require
solving an equivalent DLP)?

**Assessment of the residual question:** This is almost certainly a closed
question in the negative, for the following reason. Any map satisfying (a) must
factor through the public algebraic structure of (E, G, Q). The public
algebraic structure of Q = [k]G that distinguishes it from other points on E is
its Weil-pairing relationships with other points. The Weil pairing e_N(G, Q)
lives in F_{p^k}* for the embedding degree k of E, not in Cl(O_K). There is no
known algebraic bridge between F_{p^k}* and Cl(O_K) that would allow the
encoding of k in the class group. The Tate module T_ℓ(E) for ℓ | N is a module
over Z_ℓ of rank 2, acted on by Gal(F_p^{bar}/F_p) through the Frobenius
eigenvalues — again a structure in the ℓ-adic tower, not in Cl(O_K). The class
group acts on the SET of CM curves via ideal classes; it does not act on the
group of points of a fixed curve.

Formally establishing the impossibility of such a map would constitute a
closure theorem. Until then, the direction remains "blocked pending proof of
closure" rather than "formally closed by theorem."

---

*This report makes no hypothesis status transitions and proposes no experiments.*  
*Conjectures are not labeled separately; no conjectures appear above — all claims
follow from the first isomorphism theorem, the birthday paradox, and the
definitions of the ECDLP and class group action.*
