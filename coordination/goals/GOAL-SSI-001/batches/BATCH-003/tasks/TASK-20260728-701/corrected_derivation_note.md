# Corrected Derivation Note: Full-Cost Re-Baselining of Classical Supersingular Isogeny Path-Finding

**Task:** `TASK-20260728-701` - **Goal:** `GOAL-SSI-001` - **Batch:** `BATCH-003`
**Candidate:** `IDEA-20260725-001`
**Date:** 2026-07-28
**Role:** idea-generator
**Type:** Pure derivation -- zero curve or isogeny computation
**Supersedes:** `BATCH-002/tasks/TASK-20260727-601/derivation_note.md` (BATCH-002, snapshot `65e5bdb8`)
**Fixes applied:** F1 (fatal: per-processor walk-function variation), N1-N4 (nonfatal: clock cycle, kernel phrasing, degree specification, mixing-time assumption)

---

## 0. Scope and claim strength

This note corrects the BATCH-002 derivation note in response to the BATCH-002
red-team review (RT-20260727-603, verdict REVISE). It applies the fatal
objection F1 fix (per-processor walk-function variation for VW
parallelization), reconciles nonfatal objections N1-N4, and re-derives the van
Oorschot-Wiener (VW) full-cost exponents under the corrected parallelization
scheme. The MITM and Delfs-Galbraith (DG) full-cost exponents are restated
unchanged — they were confirmed correct by independent red-team review
(RT-20260727-603, checks 2a and 2b).

This note produces a matched-baseline recommendation for two regimes (F_{p^2}
and F_p) under the Wiener full-cost model (KN-LIT-094, KN-TECH-035). It makes
no breakthrough claim, claims no sub-p^{1/4} break, and changes no official
state. Claim strength is capped at matched-baseline recommendation / KN-TECH
update. It does not count toward GOAL-SSI-001 completion criteria.

**No computation was performed.** This is a pure derivation. No isogeny, curve,
or graph computation was executed. All exponents follow from the Wiener model
(KN-LIT-094), the Ramanujan property (KN-TECH-024), standard birthday /
collision-search analysis (KN-LIT-012), and standard isogeny operation costs.

---

## 1. Setup: the supersingular l-isogeny graph

Let G_l denote the supersingular l-isogeny graph over F_{p^2}.

- **Isogeny degree (N3 fix):** l is a small fixed prime, l != p. The canonical
  choice is l = 2 for CGL (KN-TECH-024, KN-LIT-063). Computing E[l] via the
  l-division polynomial and enumerating its (l+1) subgroups of order l is
  polynomial in log p for fixed small l. All per-step costs in this note
  assume fixed small l; the exponents are in p, not in l.

- **Vertices:** supersingular j-invariants in F_{p^2}; |V| ~ p/12
  (KN-TECH-024, KN-LIT-063).

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
**Unchanged from BATCH-002; confirmed correct by RT-20260727-603.**

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

**Unchanged from BATCH-002; confirmed correct by RT-20260727-603.**

---

## 4. Wiener full-cost accounting: MITM and DG

### The Wiener model (KN-LIT-094, KN-TECH-035)

Full cost = hardware x wall-clock time, where:

- **Hardware** is the number of gates (volume in 3D VLSI). Storage of S
  entries requires volume O(S).
- **3D wiring bound:** S entries packed in 3D have linear dimension S^{1/3},
  so random access takes time O(S^{1/3}) per lookup (signal must cross the
  device).
- **Clock cycle** is set by the longest signal path that must be traversed
  per step. For algorithms that access a table of S entries at every step,
  the clock cycle is tau = S^{1/3}. For algorithms with only local (O(1))
  per-step storage, the clock cycle is O(1).
- **Parallelization:** with P processors, each doing W/P of the W total
  steps, wall-clock = (W/P) x tau (each step takes one clock cycle).

**Proven result (Wiener, KN-LIT-094):** BSGS in a cyclic group of order n has
step count n^{1/2+o(1)} but full cost n^{2/3+o(1)}. The derivation: table of
sqrt(n) entries, optimal P = sqrt(n) processors, clock cycle n^{1/6}
(set by the table), wall-clock n^{1/6}, hardware sqrt(n), full cost
sqrt(n) x n^{1/6} = n^{2/3}.

Wiener also proves that parallel collision search (KN-LIT-012) retains its
asymptotic advantage over BSGS under full cost, because per-processor storage
stays small — the clock cycle is set by per-processor storage, not the shared
table (KN-LIT-094, KN-TECH-035). This point is central to the N1
reconciliation in section 6.

### Application to F_{p^2} MITM

The isogeny MITM is structurally identical to BSGS: a table of p^{1/2}
j-invariants with p^{1/2} lookups. Each step accesses the table, so the clock
cycle is set by the table. Substituting N = |V| ~ p for the group order n:

| Quantity | Value |
|----------|-------|
| Table size S | p^{1/2} |
| Linear dimension S^{1/3} | p^{1/6} |
| Clock cycle tau | p^{1/6} (set by table; every step accesses it) |
| Optimal processors P | p^{1/2} |
| Wall-clock | p^{1/6} |
| Hardware | p^{1/2} |
| **Full cost** | **p^{1/2} x p^{1/6} = p^{2/3}** |

**F_{p^2} MITM: step-count exponent 1/2, full-cost exponent 2/3.**
**Unchanged from BATCH-002; confirmed correct by RT-20260727-603.**

### Application to F_p Delfs-Galbraith

DG is MITM on the F_p subgraph of N' ~ sqrt(p) vertices. Table size
S = (N')^{1/2} = p^{1/4}. Each step accesses the table:

| Quantity | Value |
|----------|-------|
| Table size S | p^{1/4} |
| Linear dimension S^{1/3} | p^{1/12} |
| Clock cycle tau | p^{1/12} (set by table; every step accesses it) |
| Optimal processors P | p^{1/4} |
| Wall-clock | p^{1/12} |
| Hardware | p^{1/4} |
| **Full cost** | **p^{1/4} x p^{1/12} = p^{1/3}** |

**F_p DG: step-count exponent 1/4, full-cost exponent 1/3.**
**Unchanged from BATCH-002; confirmed correct by RT-20260727-603.**

In both cases, the full-cost exponent strictly exceeds the step-count exponent
because the table is large enough that the 3D wiring penalty raises the cost
exponent. This is the qualitative Wiener separation that applies to
memory-heavy algorithms.

---

## 5. Low-memory distinguished-point collision search: corrected definition

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
stays small (the clock cycle is O(1), not S^{1/3}).

### Isogeny-graph analogue: corrected definition

We define the analogue on the supersingular l-isogeny graph G_l, with l a
small fixed prime (N3 fix; e.g., l = 2 for CGL). This is the main technical
content of this note. The definition corrects the F1 fatal objection and
reconciles N2, N3, N4.

#### Walk model (corrected)

The state is a supersingular elliptic curve E (represented by its j-invariant
j(E) and a canonical model). Fix a small prime l (e.g., l = 2). At each step:

1. Enumerate the (l+1) subgroups of order l in E[l] (the l-torsion). For
   fixed small l, this is polynomial in log p (N3 fix): the l-division
   polynomial has degree O(l^2) = O(1) in l, and its roots over F_{p^2} are
   found in polynomial time.
2. Select one subgroup K deterministically via h_i(j(E)) mod (l+1), where
   h_i is a hash function from a family {h_1, h_2, ...} of independent hash
   functions (see F1 fix below).
3. Compute the l-isogeny phi_K: E -> E/K via Velu's formulas. For fixed l,
   Velu's formulas involve O(l) = O(1) field operations.
4. Set E <- E/K and continue.

**Retraction (F1 fix).** The BATCH-002 derivation stated "the walk function
is fixed and shared by all processors." **This is retracted.** With a fixed
deterministic walk function (a single hash h), all walks from E_0 follow the
same path and all walks from E_1 follow the same path -- only 2 useful walks
exist, not P = p^{1/4}. Walks from random starting curves produce paths
between random curves, not E_0 -> E_1. This is the fatal objection F1 from
RT-20260727-603.

#### Per-processor walk-function variation (F1 fix)

Assign P/2 distinct hash functions to walks starting from E_0, and P/2
distinct hash functions to walks starting from E_1:

- Processor i (i = 1, ..., P/2) runs a walk from E_0 using walk function
  h_i (selecting edge h_i(j(E)) mod (l+1) at each step).
- Processor j (j = P/2+1, ..., P) runs a walk from E_1 using walk function
  h_j (selecting edge h_j(j(E)) mod (l+1) at each step).

Each processor explores a different deterministic path from its endpoint,
because different hash functions select different edges at each vertex. A
collision between any E_0-walk (using h_i) and any E_1-walk (using h_j)
yields a path E_0 -> E_1. This gives P useful processors, not 2.

The hash functions {h_1, ..., h_P} are independent pseudo-random functions
on F_{p^2} -> {0, 1, ..., l}. They can be constructed from a single hash
function H and a seed: h_i(x) = H(i || x) mod (l+1). Each h_i is O(1)-time
to evaluate.

#### Mixing-time assumption (N4)

The O~(sqrt(|V|)) birthday bound assumes that O(log p) mixing steps have
occurred before a collision is expected (Ramanujan property of G_l,
KN-TECH-024). After O(log p) steps, the walk distribution is close to
uniform on V, and the birthday bound applies. If a collision occurs before
mixing (short paths), the birthday constant may differ, but the exponent is
unaffected: the O~(sqrt(|V|)) bound is an expected-time bound that assumes
mixing has occurred. This is a standard caveat in collision-search analysis
and does not change the asymptotic exponent. It is noted here for
completeness (N4 reconciliation).

#### Distinguished-point predicate

A j-invariant j in F_{p^2} is distinguished if its canonical binary encoding
has d leading zero bits, where d is a tunable parameter. The predicate is
O(1)-time to evaluate. **Unchanged from BATCH-002.**

#### Collision detection (corrected)

Each processor runs its assigned walk (from E_0 or E_1 with its assigned hash
function h_i) and stores only its starting curve, walk-function index, and
current curve (per-processor storage O(1)). When a walk reaches a
distinguished point, it writes

  (j-value, starting curve, walk-function index, step count)

to the shared table. **The walk-function index is required for
reconstruction** (F1 fix): to re-run the correct deterministic walk, one must
know which hash function h_i produced the path. When two walks report the
same distinguished j-value, a collision has occurred: the walks merged at
some earlier vertex and followed the same path to the distinguished point.

A useful collision is one between an E_0-walk and an E_1-walk. Collisions
between two E_0-walks or two E_1-walks are detected but do not yield an
E_0 -> E_1 path; they are discarded. With P/2 walks from each endpoint, the
expected number of useful collisions before a useless collision is
O(P/2) / O(P/2) = O(1), so the overhead from useless collisions is constant.

#### Collision-to-path reconstruction (corrected: N2 fix, walk-function tracking)

Given a useful collision between walk A (from E_0, using h_i) and walk B
(from E_1, using h_j) at distinguished point j*:

1. Re-run walk A from E_0 using h_i and walk B from E_1 using h_j, recording
   distinguished points along each path. The distinguished points partition
   each path into segments of expected length 2^d.

2. Identify the first matching distinguished point on both paths (the
   earliest point after the merge). This narrows the merge to a segment pair.

3. Re-run the two segments (length O(2^d) each) step-by-step, comparing
   j-invariants at each step. The first match is the merge vertex j_m.

4. The connecting path is: phi_A (from E_0 to j_m) composed with the dual of
   phi_B (from E_1 to j_m). At each step, the kernel K is **recomputed**
   from h_i(j(E)) mod (l+1) (for walk A) or h_j(j(E)) mod (l+1) (for walk B)
   -- kernels are not stored (N2 fix). The dual isogeny is computed via
   Velu duals from the recomputed kernel. The isomorphism
   sigma: E_A -> E_B for curves at the same j-invariant (trivial over
   F_{p^2} for j != 0, 1728; bounded correction for special j) bridges the
   two paths.

**Result: the collision-to-path reconstruction is well-defined.** It uses
only:
- Velu's formulas (l-isogeny computation from a kernel) -- standard,
  polynomial-time for fixed l.
- Velu duals (dual isogeny from a recomputed kernel) -- standard,
  polynomial-time for fixed l.
- The isomorphism between curves with the same j-invariant -- standard,
  polynomial-time.

**No uncharged oracles are required.** The walk, the distinguished predicate,
and the reconstruction use only standard isogeny operations available in the
same cost model as the MITM steps.

**N2 reconciliation:** The BATCH-002 YAML said "Velu duals from stored
kernels," which could imply storing one kernel per walk step
(O(sqrt(p) * polylog) bits -- exponential in log p, not polynomial). The
derivation note's prose already correctly described recomputation. Both the
prose and the YAML now use "recomputed kernels" / "kernels recomputed during
reconstruction" throughout. Kernels are recomputed from the hash function at
each step during the reconstruction re-run; no per-step kernel storage is
required.

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
expansion as a subgraph of a Ramanujan graph, but this is unproven. If the
mixing assumption is rejected, DG at p^{1/3} full cost remains the baseline.

---

## 6. Full cost of the low-memory collision search: corrected derivation

### N1 reconciliation: clock cycle is set by per-processor storage

Under the Wiener model, the clock cycle is set by the longest signal path
that must be traversed **per step**. The key distinction between MITM and VW
is what each step accesses:

- **MITM:** every step performs a random-access table lookup. The clock
  cycle is set by the table's linear dimension, tau = S^{1/3}. This is why
  the MITM full cost exceeds the step count.

- **VW parallel collision search:** every step is a local isogeny
  computation that accesses only per-processor storage O(1). The shared
  distinguished-point table is accessed only when a distinguished point is
  found -- once every 2^d steps on average. The clock cycle is therefore
  set by per-processor storage O(1), **not** by the shared table. This is
  Wiener's explicit theorem: "parallel collision search retains its
  asymptotic advantage [over BSGS] because per-processor storage is small"
  (KN-LIT-094, KN-TECH-035).

The amortized cost of table access per walk step is O(S^{1/3} / 2^d), where
S is the table size and 2^d is the distinguished-point interval. With
S = O(p^{1/4}) and 2^d = p^{1/4}, this is O(p^{1/12} / p^{1/4}) = O(p^{-1/6}),
which is subconstant and does not affect the clock cycle. Even if the table
access is charged at O(S^{1/3}) = O(p^{1/12}) per access, it occurs only
O(1) times per processor (each processor finds O(1) distinguished points),
contributing O(p^{1/12}) to the wall-clock -- dominated by the O~(p^{1/4})
walk steps.

**This reconciles the BATCH-002 inconsistency (N1):** the tau = p^{1/12}
entry in the BATCH-002 table referred to the shared table's linear dimension,
but for VW the clock cycle is not set by the shared table. The clock cycle is
O(1) (per-processor storage), and the wall-clock is O~(p^{1/4}) (p^{1/4}
walk steps at O(1) per step, plus negligible table access). The result
(full cost p^{1/2}) is correct by Wiener's theorem; the reasoning is now
consistent.

### F_{p^2} regime (with F1 fix)

State space N ~ p. Total walk steps O~(sqrt(N)) = O~(p^{1/2}).

With the F1 fix: P = p^{1/4} useful processors (P/2 distinct hash functions
from E_0, P/2 from E_1). Each processor runs p^{1/2} / p^{1/4} = p^{1/4}
walk steps.

Set 2^d = p^{1/4} (distinguished parameter). Then:

| Quantity | Value |
|----------|-------|
| Shared table size S | O(sqrt(N) / 2^d) = O(p^{1/4}) |
| Table linear dimension S^{1/3} | p^{1/12} (does NOT set clock cycle) |
| Clock cycle tau | O(1) (set by per-processor storage; N1 reconciliation) |
| Useful processors P | p^{1/4} (F1 fix: P/2 from E_0, P/2 from E_1) |
| Walk steps per processor | p^{1/2} / p^{1/4} = p^{1/4} |
| Distinguished accesses per processor | O(1) |
| Wall-clock | O~(p^{1/4}) (walk steps dominate; table access negligible) |
| Hardware | p^{1/4} (processors) + p^{1/4} (table) = O(p^{1/4}) |
| **Full cost** | **p^{1/4} x O~(p^{1/4}) = O~(p^{1/2})** |

**F_{p^2} VW collision search: step-count exponent 1/2, full-cost exponent
1/2.** No qualitative Wiener separation -- the low-memory property (clock
cycle O(1) from per-processor storage) means the full cost equals the step
count.

**Comparison with the unfixed (BATCH-002) specification:** without per-
processor walk-function variation, only 2 useful walks exist (one from E_0,
one from E_1). Each runs O~(p^{1/2}) steps (birthday bound for 2 walks on
~p vertices). Wall-clock = O~(p^{1/2}), hardware = O(p^{1/4}), full cost =
O~(p^{3/4}) -- worse than MITM's p^{2/3}. The F1 fix is what restores
P = p^{1/4} useful processors and brings the full cost down to p^{1/2}.

### F_p regime (with F1 fix, conditional on mixing)

State space N' ~ sqrt(p). Total walk steps O~(sqrt(N')) = O~(p^{1/4}).

With the F1 fix: P = p^{1/8} useful processors (P/2 distinct hash functions
from E_0, P/2 from E_1, on the F_p subgraph). Each processor runs
p^{1/4} / p^{1/8} = p^{1/8} walk steps.

Set 2^d = p^{1/8} (distinguished parameter). Then:

| Quantity | Value |
|----------|-------|
| Shared table size S | O(p^{1/4} / p^{1/8}) = O(p^{1/8}) |
| Table linear dimension S^{1/3} | p^{1/24} (does NOT set clock cycle) |
| Clock cycle tau | O(1) (set by per-processor storage; N1 reconciliation) |
| Useful processors P | p^{1/8} (F1 fix: P/2 from E_0, P/2 from E_1) |
| Walk steps per processor | p^{1/4} / p^{1/8} = p^{1/8} |
| Wall-clock | O~(p^{1/8}) |
| Hardware | O(p^{1/8}) |
| **Full cost** | **p^{1/8} x O~(p^{1/8}) = O~(p^{1/4})** |

**F_p VW collision search: step-count exponent 1/4, full-cost exponent 1/4.**
No qualitative Wiener separation (subject to the F_p mixing caveat of
section 5). The F1 fix applies identically: without per-processor
walk-function variation, only 2 useful walks exist on the F_p subgraph,
giving full cost O~(p^{3/8}) -- worse than DG's p^{1/3}.

---

## 7. Regime comparison and matched-baseline recommendation

### Summary table (corrected)

| Regime | Algorithm | Step-count exp | Full-cost exp | Space | Clock cycle set by |
|--------|-----------|---------------|--------------|-------|-------------------|
| F_{p^2} | MITM | 1/2 | **2/3** | p^{1/2} | Table (S^{1/3} = p^{1/6}) |
| F_{p^2} | VW collision search | 1/2 | **1/2** | poly | Per-processor O(1) |
| F_p | Delfs-Galbraith (MITM) | 1/4 | **1/3** | p^{1/4} | Table (S^{1/3} = p^{1/12}) |
| F_p | VW collision search | 1/4 | **1/4** | poly | Per-processor O(1) |
| F_p | Full-graph MITM | 1/2 | 2/3 | p^{1/2} | Table (p^{1/6}) |

### F_{p^2} regime

- MITM full cost p^{2/3} strictly exceeds VW full cost p^{1/2}.
- The qualitative Wiener separation (step count 1/2 vs full cost 2/3) applies
  to MITM but NOT to VW, because VW has polynomial space and the clock cycle
  is O(1) (per-processor storage), not S^{1/3} (table).
- **Matched baseline: VW distinguished-point collision search at full cost
  O~(p^{1/2}), with per-processor walk-function variation (F1 fix).** MITM
  is relegated to a high-memory footnote under full cost.

### F_p regime

- Delfs-Galbraith full cost p^{1/3} strictly exceeds VW full cost p^{1/4}
  (subject to the mixing caveat).
- Under step-count accounting, DG and VW are tied at p^{1/4}. Under full cost,
  VW dominates DG.
- **Matched baseline: VW distinguished-point collision search on the F_p
  subgraph at full cost O~(p^{1/4}), with per-processor walk-function
  variation (F1 fix), conditional on the mixing assumption.** If the mixing
  assumption is rejected, DG at p^{1/3} full cost remains the baseline.

### Decision-relevance

Full-cost accounting changes **which algorithm is the matched baseline** in
both regimes (from MITM/DG to VW) but does **not** change the step-count
exponent of the baseline (still p^{1/2} for F_{p^2}, p^{1/4} for F_p). The
best-known full cost equals the best-known step count, achieved by the
low-memory VW variant with per-processor walk-function variation.

This is decision-relevant because it raises the bar for novelty: a candidate
claiming to improve path-finding must beat the VW full cost (p^{1/2} F_{p^2},
p^{1/4} F_p), not the easier MITM full cost (p^{2/3}) or DG full cost
(p^{1/3}). Under step-count accounting, all three are tied; under full cost,
they separate.

This is a matched-baseline recommendation, not a material ranking change in
the problem hardness. No sub-p^{1/4} break is claimed.

---

## 8. Reconciliation of BATCH-002 objections

| Objection | Type | Fix applied | Section |
|-----------|------|-------------|---------|
| F1: VW parallelization fails with fixed walk function | Fatal | Per-processor walk-function variation: P/2 distinct hash functions from E_0, P/2 from E_1. "The walk function is fixed and shared by all processors" retracted. Reconstruction records walk-function index. | 5, 6 |
| N1: Clock-cycle inconsistency between MITM and VW | Nonfatal | Clock cycle for VW is set by per-processor storage O(1), not the shared table, because the table is accessed only at distinguished points. tau column reconciled: table dimension p^{1/12} does not set the clock cycle; clock cycle is O(1). | 6 |
| N2: "Stored kernels" phrasing implies non-polynomial storage | Nonfatal | Corrected to "recomputed kernels" / "kernels recomputed during reconstruction" throughout. Kernels are recomputed from the hash function at each step during the reconstruction re-run. | 5 |
| N3: Isogeny degree l not specified | Nonfatal | l specified as a small fixed prime (l = 2 for CGL). Computing E[l] and its subgroups is polynomial in log p for fixed small l. | 1, 5 |
| N4: Birthday bound assumes mixing | Nonfatal | O~(sqrt(|V|)) bound assumes O(log p) mixing steps (Ramanujan property). If collision occurs before mixing, constant may differ but exponent is unaffected. | 5 |

### Effect on VW full-cost exponents

The F1 fix **confirms** the VW full-cost exponents at the values claimed in
BATCH-002:

| Regime | VW full-cost exponent (BATCH-002, as specified) | VW full-cost exponent (BATCH-003, with F1 fix) | Confirmed? |
|--------|--------------------------------------------------|-------------------------------------------------|------------|
| F_{p^2} | p^{1/2} | p^{1/2} | Yes |
| F_p | p^{1/4} | p^{1/4} | Yes (conditional on mixing) |

The BATCH-002 derivation reached the correct exponent values but via an
incorrect parallelization specification (fixed walk function). With the F1
fix (per-processor walk-function variation), the derivation is correct: P =
p^{1/4} useful processors (F_{p^2}) or P = p^{1/8} (F_p), each running the
appropriate number of walk steps, with clock cycle O(1) from per-processor
storage, giving full cost p^{1/2} (F_{p^2}) and p^{1/4} (F_p).

Without the F1 fix, the VW full cost would be O~(p^{3/4}) (F_{p^2}) and
O~(p^{3/8}) (F_p) -- both worse than the respective MITM/DG baselines. The F1
fix is essential for the VW advantage to hold.

### Effect on MITM and DG full-cost exponents

**No change.** The MITM full-cost exponent p^{2/3} (F_{p^2}) and DG full-cost
exponent p^{1/3} (F_p) were confirmed correct by RT-20260727-603 (checks 2a
and 2b) and are restated in section 4 unchanged.

---

## 9. Limitations and verification honesty

1. **No computation performed.** This is a derivation note. No isogeny,
   curve, or graph computation was executed. All exponents follow from the
   Wiener model (KN-LIT-094), the Ramanujan property (KN-TECH-024),
   standard birthday / collision-search analysis (KN-LIT-012), and standard
   isogeny operation costs for fixed small l.

2. **Wiener model is asymptotic.** The full-cost exponents carry o(1) terms
   with unextracted constants (KN-LIT-094, KN-TECH-035). They settle
   exponent-level comparisons, not constant-factor claims.

3. **F_p subgraph mixing is unproven.** The VW collision search on the F_p
   subgraph requires rapid mixing, which is not proven for G_l^{F_p}. This
   is a heuristic gap beyond what Delfs-Galbraith requires (DG uses BFS, not
   walks). The F_{p^2} result rests on the proven Ramanujan property. The
   F_p result is conditional, with DG at p^{1/3} as the unconditional
   fallback.

4. **Mixing-time assumption (N4).** The O~(sqrt(|V|)) birthday bound assumes
   O(log p) mixing steps have occurred. If collision occurs before mixing,
   the constant may differ but the exponent is unaffected.

5. **Per-processor walk-function variation is heuristic.** The F1 fix
   assumes that distinct hash functions produce sufficiently independent
   walks. This is the standard assumption in parallel collision search
   (KN-LIT-012) and is consistent with the Ramanujan mixing property: after
   O(log p) steps, each walk is near-uniform regardless of its hash
   function, so different hash functions explore different regions. A formal
   proof that the P/2 + P/2 walks cover the birthday bound would require
   analysis of the joint distribution, which is beyond this derivation.

6. **Twist ambiguity is bounded.** Over F_{p^2}, each j-invariant (except
   j=0, 1728) corresponds to a unique isomorphism class, so the
   collision-to-path reconstruction is well-defined up to bounded
   special-case corrections.

7. **Output size is inherent.** The connecting path has O(sqrt(p)) isogeny
   steps. This output is common to all algorithms and is not charged under
   the Wiener model (sequential output, not random-access).

8. **No knowledge-spine entry was freshly verified against a primary PDF.**
   The derivation relies on the repository knowledge spine (KN-LIT-094,
   KN-LIT-012, KN-TECH-024, KN-TECH-029, KN-TECH-035) as cited.

9. **No breakthrough claim, no state change.** This note does not close
   KN-OPEN-013, does not claim a sub-p^{1/4} attack, and does not count
   toward GOAL-SSI-001 completion criteria. It is a matched-baseline
   correction with capped claim strength.

---

## 10. Knowledge promotion readiness

The complete matched-baseline package is now ready for KN-TECH promotion:

1. **MITM full-cost exponent** p^{2/3} (F_{p^2}) -- confirmed correct by
   RT-20260727-603, unchanged.
2. **Delfs-Galbraith full-cost exponent** p^{1/3} (F_p) -- confirmed correct
   by RT-20260727-603, unchanged.
3. **VW distinguished-point collision search analogue** on the supersingular
   l-isogeny graph -- walk model (random l-isogeny steps with per-processor
   hash-function variation, F1 fix), distinguished predicate (leading-zero-
   bits on j-invariant), collision-to-path reconstruction (distinguished-
   point segmenting + Velu duals from recomputed kernels, walk-function
   tracking), no uncharged oracles.
4. **VW full-cost exponents** p^{1/2} (F_{p^2}), p^{1/4} (F_p conditional on
   mixing) -- re-derived with F1 fix, confirmed at the BATCH-002 values.
5. **Matched-baseline recommendation** -- VW, not MITM/DG, under full cost;
   F_p conditional on mixing with DG fallback at p^{1/3}.

This fills the gap identified in the BATCH-001 candidate report: KN-TECH-029
records step-count exponents but does not apply Wiener full-cost accounting,
and the isogeny-graph VW analogue was not present in the spine.

**Recommendation:** Promote the complete package (items 1-5) to a KN-TECH
entry (new entry or update to KN-TECH-029) in a single coherent promotion.
Promoting the MITM/DG exponents without the VW context would be misleading:
the matched-baseline recommendation depends on all three algorithms being
correctly costed. With the F1 fix applied and all nonfatal objections
reconciled, the VW side of the ranking is now correct, and the complete
package is coherent.

**This recommendation is for the Coordinator's decision.** The Idea Generator
does not change official state or create knowledge-spine entries. The
Coordinator must verify the promotion gates (archived proof decomposition,
validated heuristics, independent review, red-team pass) before promoting.
