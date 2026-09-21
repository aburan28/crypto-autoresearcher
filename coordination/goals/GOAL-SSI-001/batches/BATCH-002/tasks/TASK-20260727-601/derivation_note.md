# Derivation Note: Full-Cost Re-Baselining of Classical Supersingular Isogeny Path-Finding

**Task:** `TASK-20260727-601` - **Goal:** `GOAL-SSI-001` - **Batch:** `BATCH-002`
**Candidate:** `IDEA-20260725-001`
**Date:** 2026-07-27
**Role:** idea-generator
**Type:** Pure derivation -- zero curve or isogeny computation

---

## 0. Scope and claim strength

This note re-baselines the classical cost of supersingular-isogeny path-finding
under the Wiener full-cost model (KN-LIT-094, KN-TECH-035). It produces a
matched-baseline recommendation for two regimes (F_{p^2} and F_p) and defines
a low-memory distinguished-point collision-search analogue on the isogeny
graph. It makes no breakthrough claim, claims no sub-p^{1/4} break, and changes
no official state. Claim strength is capped at matched-baseline recommendation
/ KN-TECH update.

---

## 1. Setup: the supersingular l-isogeny graph

Let G_l denote the supersingular l-isogeny graph over F_{p^2} (l != p prime).

- **Vertices:** supersingular j-invariants in F_{p^2}; |V| ~ p/12 (KN-TECH-024,
  KN-LIT-063).
- **Edges:** l-isogenies; G_l is (l+1)-regular.
- **Expansion:** G_l is Ramanujan -- non-trivial adjacency eigenvalues satisfy
  |lambda| <= 2*sqrt(l) (KN-TECH-024). Spectral gap >= 1 - 2*sqrt(l)/(l+1),
  giving mixing time O(log |V|) = O(log p).

**Path-finding problem:** given two supersingular curves E_0, E_1 (j-invariants
j_0, j_1), find a path in G_l connecting them, i.e., a composition of
l-isogenies phi: E_0 -> E_1.

The problem is equivalent to endomorphism-ring computation under GRH
(KN-LIT-074, KN-TECH-028). No torsion images are assumed (survivor regime;
SIDH/SIKE is out of scope).

---

## 2. MITM on the full F_{p^2} graph

### Algorithm

Grow two isogeny trees: a forward tree from E_0 and a backward tree from E_1,
each to depth r. Each tree has up to (l+1)^r vertices. A collision (shared
j-invariant) gives a connecting path of length 2r.

For the trees to collide with constant probability (birthday bound), we need
the product of tree sizes to be ~ |V|:

  (l+1)^{2r} ~ |V| ~ p/12  ==>  (l+1)^r ~ sqrt(p/12)

So r = O(log_l p) and each tree has ~ sqrt(p/12) ~ p^{1/2} vertices.

### Step-count exponents (F_{p^2} regime)

| Resource | Exponent | Expression |
|----------|----------|------------|
| Time (isogeny evaluations) | 1/2 | O~(p^{1/2}) |
| Space (stored j-invariants) | 1/2 | O~(p^{1/2}) |

This is the standard MITM baseline recorded in KN-TECH-029 and KN-LIT-078.

---

## 3. Delfs-Galbraith on the F_p-rational subgraph

### Algorithm

When both E_0 and E_1 are defined over F_p (F_p-rational), Delfs-Galbraith
(KN-LIT-078) descends to the F_p-rational subgraph G_l^{F_p} subset G_l, whose
vertices are F_p-rational supersingular curves.

- **Subgraph size:** |V^{F_p}| ~ sqrt(p) (related to the class number of the
  imaginary quadratic order; KN-LIT-078, KN-TECH-029).

MITM on G_l^{F_p} requires trees of size ~ sqrt(|V^{F_p}|) ~ p^{1/4}.

### Step-count exponents (F_p regime)

| Resource | Exponent | Expression |
|----------|----------|------------|
| Time | 1/4 | O~(p^{1/4}) |
| Space | 1/4 | O~(p^{1/4}) |

This already dominates MITM on the full graph (p^{1/4} < p^{1/2}) in step
count, as noted in KN-TECH-029 and confirmed by the BATCH-001 red team
(RT-20260725-503, objection F2).

---

## 4. Wiener full-cost accounting applied to the MITM table

### The Wiener model (KN-LIT-094, KN-TECH-035)

Full cost = hardware x wall-clock time, where:

- **Hardware** is the number of gates (volume in 3D VLSI). Storage of S
  entries requires volume O(S).
- **3D wiring bound:** S entries packed in 3D have linear dimension S^{1/3},
  so random access takes time O(S^{1/3}) per lookup (signal must cross the
  device).
- **Clock cycle** is set by the longest signal path: tau = S^{1/3} for a
  table of S entries.
- **Parallelization:** with P processors, each doing W/P of the W total
  steps, wall-clock = (W/P) x tau (each step takes one clock cycle).

**Proven result (Wiener, KN-LIT-094):** BSGS in a cyclic group of order n has
step count n^{1/2+o(1)} but full cost n^{2/3+o(1)}. The derivation: table of
sqrt(n) entries, optimal P = sqrt(n) processors, clock cycle n^{1/6},
wall-clock n^{1/6}, hardware sqrt(n), full cost sqrt(n) x n^{1/6} = n^{2/3}.

The key insight: the sqrt(n)-element table cannot be reached in unit time.
This raises the exponent from 1/2 (step count) to 2/3 (full cost).

### Application to F_{p^2} MITM

The isogeny MITM is structurally identical to BSGS: a table of p^{1/2}
j-invariants with p^{1/2} lookups. Substituting N = |V| ~ p for the group
order n:

| Quantity | Value |
|----------|-------|
| Table size S | p^{1/2} |
| Linear dimension S^{1/3} | p^{1/6} |
| Clock cycle tau | p^{1/6} |
| Optimal processors P | p^{1/2} |
| Wall-clock | p^{1/6} |
| Hardware | p^{1/2} |
| **Full cost** | **p^{1/2} x p^{1/6} = p^{2/3}** |

**F_{p^2} MITM: step-count exponent 1/2, full-cost exponent 2/3.**

The full-cost exponent (2/3) strictly exceeds the step-count exponent (1/2).
This is a qualitative Wiener-style separation: the MITM table is large enough
that wiring penalty raises the cost exponent.

### Application to F_p Delfs-Galbraith

DG is MITM on the F_p subgraph of N' ~ sqrt(p) vertices. Table size
S = (N')^{1/2} = p^{1/4}. Substituting N' = sqrt(p):

| Quantity | Value |
|----------|-------|
| Table size S | p^{1/4} |
| Linear dimension S^{1/3} | p^{1/12} |
| Clock cycle tau | p^{1/12} |
| Optimal processors P | p^{1/4} |
| Wall-clock | p^{1/12} |
| Hardware | p^{1/4} |
| **Full cost** | **p^{1/4} x p^{1/12} = p^{1/3}** |

**F_p DG: step-count exponent 1/4, full-cost exponent 1/3.**

Again, the full-cost exponent (1/3) strictly exceeds the step-count exponent
(1/4). The same qualitative separation applies: the DG table is large enough
that the wiring penalty raises the cost exponent.

---

## 5. Low-memory distinguished-point collision search: definition

### The group-setting precedent (van Oorschot-Wiener, KN-LIT-012)

In a cyclic group of order n, parallel collision search with distinguished
points gives O~(sqrt(n)) time with **polynomial** space. The walk iterates a
pseudo-random function on the group; only distinguished points (encoding
satisfies a predicate, e.g., leading d bits zero) are stored. When two walks
collide, they merge; the next distinguished point is reported by both,
detecting the collision. Per-processor storage is O(1); the shared table has
O(sqrt(n) / 2^d) entries, tunable to polynomial.

Wiener (KN-LIT-094) confirms that parallel collision search retains its
asymptotic advantage over BSGS under full cost, because per-processor storage
stays small.

### Isogeny-graph analogue: definition

We define the analogue on the supersingular l-isogeny graph G_l. This is the
main technical content of this note.

**Walk model.** The state is a supersingular elliptic curve E (represented by
its j-invariant j(E) and a canonical model). At each step:

1. Enumerate the (l+1) subgroups of order l in E[l] (the l-torsion).
2. Select one subgroup K deterministically via hash(j(E)) mod (l+1).
3. Compute the l-isogeny phi_K: E -> E/K via Velu's formulas.
4. Set E <- E/K and continue.

This is a deterministic random walk on G_l, exactly as in the group setting.
The walk function is fixed and shared by all processors.

**Ramanujan mixing.** Since G_l is Ramanujan with mixing time O(log p), after
O(log p) steps the walk distribution is close to uniform on V. The birthday
bound applies: a collision between two walks is expected after O~(sqrt(|V|))
= O~(p^{1/2}) total walk steps across all processors.

**Distinguished-point predicate.** A j-invariant j in F_{p^2} is
distinguished if its canonical binary encoding has d leading zero bits, where
d is a tunable parameter. The predicate is O(1)-time to evaluate.

**Collision detection.** Run P independent walks from different starting
curves (including E_0 and E_1). Each walk stores only its starting curve and
current curve. When a walk reaches a distinguished point, it writes
(j-value, starting curve, step count) to the shared table. When two walks
report the same distinguished j-value, a collision has occurred: the walks
merged at some earlier vertex and followed the same path to the distinguished
point.

**Collision-to-path reconstruction.** Given a collision between walk A (from
E_0) and walk B (from E_1) at distinguished point j*:

1. Re-run walk A from E_0 and walk B from E_1, recording distinguished points
   along each path. The distinguished points partition each path into
   segments of expected length 2^d.

2. Identify the first matching distinguished point on both paths (the
   earliest point after the merge). This narrows the merge to a segment pair.

3. Re-run the two segments (length O(2^d) each) step-by-step, comparing
   j-invariants at each step. The first match is the merge vertex j_m.

4. The connecting path is: phi_A (from E_0 to j_m) composed with the dual of
   phi_B (from E_1 to j_m). The dual isogeny is computed step-by-step from
   the kernels (Velu duals). The isomorphism sigma: E_A -> E_B for curves at
   the same j-invariant (trivial over F_{p^2} for j != 0, 1728; bounded
   correction for special j) bridges the two paths.

**Result: the collision-to-path reconstruction is well-defined.** It uses
only:
- Velu's formulas (l-isogeny computation from a kernel) -- standard,
  polynomial-time.
- Velu duals (dual isogeny from the kernel) -- standard, polynomial-time.
- The isomorphism between curves with the same j-invariant -- standard,
  polynomial-time.

**No uncharged oracles are required.** The walk, the distinguished predicate,
and the reconstruction use only standard isogeny operations available in the
same cost model as the MITM steps.

### Reconstruction storage

The reconstruction stores O(sqrt(p) / 2^d) distinguished points per walk
(polynomial with appropriate d), plus O(2^d) temporary storage for the final
segment comparison. With 2^d = p^{1/4}, this is O(p^{1/4}) -- polynomial.

The output path has O(sqrt(p)) isogeny steps, each described in O(log p) bits.
This output is inherent to the problem (the path is long) and is common to all
algorithms. It is written to sequential storage (not random-access) and is
not charged under the Wiener model, which prices only the random-access table
requiring 3D wiring.

### F_p subgraph caveat

The F_p-rational subgraph G_l^{F_p} is NOT known to be Ramanujan. The VW
collision search on G_l^{F_p} requires rapid mixing for the birthday bound to
hold. Delfs-Galbraith uses BFS-based MITM, which does not require mixing. The
VW analogue on the F_p subgraph therefore rests on a **stronger heuristic
assumption** (rapid mixing of the F_p subgraph) than Delfs-Galbraith. This is
a caveat, not a falsification -- the subgraph is expected to have reasonable
expansion as a subgraph of a Ramanujan graph, but this is unproven.

---

## 6. Full cost of the low-memory collision search

### F_{p^2} regime

State space N ~ p. Total walk steps O~(sqrt(N)) = O~(p^{1/2}).

Set 2^d = p^{1/4} (distinguished parameter). Then:

| Quantity | Value |
|----------|-------|
| Shared table size S | O(sqrt(N) / 2^d) = O(p^{1/4}) |
| Table linear dimension S^{1/3} | p^{1/12} |
| Clock cycle tau | p^{1/12} |
| Processors P | p^{1/4} |
| Walk steps per processor | p^{1/2} / p^{1/4} = p^{1/4} |
| Distinguished accesses per processor | O(1) |
| Wall-clock | O~(p^{1/4}) (dominated by local computation) |
| Hardware | p^{1/4} (processors) + p^{1/4} (table) = p^{1/4} |
| **Full cost** | **p^{1/4} x O~(p^{1/4}) = O~(p^{1/2})** |

**F_{p^2} VW collision search: step-count exponent 1/2, full-cost exponent
1/2.** No qualitative separation -- the low-memory property means the full
cost equals the step count.

### F_p regime

State space N' ~ sqrt(p). Total walk steps O~(sqrt(N')) = O~(p^{1/4}).

Set 2^d = p^{1/8}. Then:

| Quantity | Value |
|----------|-------|
| Shared table size S | O(p^{1/4} / p^{1/8}) = O(p^{1/8}) |
| Table linear dimension S^{1/3} | p^{1/24} |
| Clock cycle tau | p^{1/24} |
| Processors P | p^{1/8} |
| Walk steps per processor | p^{1/4} / p^{1/8} = p^{1/8} |
| Wall-clock | O~(p^{1/8}) |
| Hardware | p^{1/8} |
| **Full cost** | **p^{1/8} x O~(p^{1/8}) = O~(p^{1/4})** |

**F_p VW collision search: step-count exponent 1/4, full-cost exponent 1/4.**
No qualitative separation (subject to the F_p mixing caveat of section 5).

---

## 7. Regime comparison and matched-baseline recommendation

### Summary table

| Regime | Algorithm | Step-count exp | Full-cost exp | Space |
|--------|-----------|---------------|--------------|-------|
| F_{p^2} | MITM | 1/2 | **2/3** | p^{1/2} |
| F_{p^2} | VW collision search | 1/2 | **1/2** | poly |
| F_p | Delfs-Galbraith (MITM) | 1/4 | **1/3** | p^{1/4} |
| F_p | VW collision search | 1/4 | **1/4** | poly |
| F_p | Full-graph MITM | 1/2 | 2/3 | p^{1/2} |

### F_{p^2} regime

- MITM full cost p^{2/3} strictly exceeds VW full cost p^{1/2}.
- The qualitative Wiener separation (step count 1/2 vs full cost 2/3) applies
  to MITM but NOT to VW, because VW has polynomial space.
- **Matched baseline: VW distinguished-point collision search at full cost
  O~(p^{1/2}).** MITM is relegated to a high-memory footnote under full cost.

### F_p regime

- Delfs-Galbraith full cost p^{1/3} strictly exceeds VW full cost p^{1/4}
  (subject to the mixing caveat).
- Under step-count accounting, DG and VW are tied at p^{1/4}. Under full cost,
  VW dominates DG.
- **Matched baseline: VW distinguished-point collision search on the F_p
  subgraph at full cost O~(p^{1/4}), conditional on the mixing assumption.**
  If the mixing assumption is rejected, DG at p^{1/3} full cost remains the
  baseline.

### Decision-relevance

Full-cost accounting changes **which algorithm is the matched baseline** in
both regimes (from MITM/DG to VW) but does **not** change the step-count
exponent of the baseline (still p^{1/2} for F_{p^2}, p^{1/4} for F_p). The
best-known full cost equals the best-known step count, achieved by the
low-memory VW variant.

This is decision-relevant because it raises the bar for novelty: a candidate
claiming to improve path-finding must beat the VW full cost (p^{1/2} F_{p^2},
p^{1/4} F_p), not the easier MITM full cost (p^{2/3}) or DG full cost
(p^{1/3}). Under step-count accounting, all three are tied; under full cost,
they separate.

This is a matched-baseline recommendation, not a material ranking change in
the problem hardness. No sub-p^{1/4} break is claimed.

---

## 8. Limitations and verification honesty

1. **No computation performed.** This is a derivation note. No isogeny, curve,
   or graph computation was executed. All exponents follow from the Wiener
   model (KN-LIT-094), the Ramanujan property (KN-TECH-024), and standard
   birthday/collision-search analysis (KN-LIT-012).

2. **Wiener model is asymptotic.** The full-cost exponents carry o(1) terms
   with unextracted constants (KN-LIT-094, KN-TECH-035). They settle
   exponent-level comparisons, not constant-factor claims.

3. **F_p subgraph mixing is unproven.** The VW collision search on the F_p
   subgraph requires rapid mixing, which is not proven for G_l^{F_p}. This is
   a heuristic gap beyond what Delfs-Galbraith requires (DG uses BFS, not
   walks). The F_{p^2} result rests on the proven Ramanujan property.

4. **Twist ambiguity is bounded.** Over F_{p^2}, each j-invariant (except j=0,
   1728) corresponds to a unique isomorphism class, so the collision-to-path
   reconstruction is well-defined up to bounded special-case corrections.

5. **Output size is inherent.** The connecting path has O(sqrt(p)) isogeny
   steps. This output is common to all algorithms and is not charged under
   the Wiener model (sequential output, not random-access).

6. **No knowledge-spine entry was freshly verified against a primary PDF.**
   The derivation relies on the repository knowledge spine (KN-LIT-094,
   KN-LIT-012, KN-TECH-024, KN-TECH-029, KN-TECH-035) as cited.

7. **No breakthrough claim, no state change.** This note does not close
   KN-OPEN-013, does not claim a sub-p^{1/4} attack, and does not count toward
   GOAL-SSI-001 completion criteria.
