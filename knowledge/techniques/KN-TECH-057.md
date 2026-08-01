---
id: KN-TECH-057
type: technique
title: >-
  Full-cost matched baselines for classical supersingular path-finding
  (Wiener 3D wiring model applied to MITM, Delfs-Galbraith, and van
  Oorschot-Wiener collision search on the isogeny graph)
tags: [isogeny-problem, path-finding, full-cost, wiener-model, mitm, delfs-galbraith, van-oorschot-wiener, collision-search, distinguished-points, matched-baseline, cost-model, isogeny]
confidence: derivation_confirmed
complexity: >-
  MITM full cost O~(p^{2/3}) (F_{p^2}); Delfs-Galbraith full cost O~(p^{1/3})
  (F_p); VW distinguished-point collision search full cost O~(p^{1/2})
  (F_{p^2}) and O~(p^{1/4}) (F_p, conditional on unproven F_p subgraph mixing).
  All under Wiener 3D wiring AT^2 model (KN-LIT-094).
applicability: >-
  Classical path-finding between two supersingular curves with no torsion
  images (survivor regime: CGL, SQIsign foundations). Sets the matched
  baselines against which any new classical attack candidate must be measured.
source_refs: [KN-LIT-094, KN-TECH-024, KN-TECH-029, KN-TECH-035]
added: 2026-07-28
superseded_by: null
promoted_from: [EV-SSI-003, DEC-20260728-004]
---

## Method

This entry applies the Wiener full-cost (3D wiring AT^2) model of
KN-LIT-094 to the three classical algorithms for supersingular isogeny
path-finding, and defines the van Oorschot-Wiener (VW) distinguished-point
collision search analogue on the supersingular ℓ-isogeny graph. It fills
the gap in KN-TECH-029, which records step-count exponents only.

### Wiener 3D wiring model (KN-LIT-094)

Full cost = hardware × wall-clock. In 3D, a table of S entries occupies
volume S, giving a clock cycle τ = S^{1/3} (longest signal path). Parallel
processors P share the table; wall-clock = (work per processor) × τ.
Full cost = P × wall-clock = P × (W/P) × τ = W × τ.

Key insight: a low-memory algorithm with per-processor storage O(1) has
τ = O(1), so full cost equals step count. A high-memory algorithm with
a table of S entries pays τ = S^{1/3} on top of its step count.

### Algorithms and full-cost exponents

**MITM (F_{p^2} regime):**
- Table of p^{1/2} j-invariants, p^{1/2} lookups.
- Step count: O~(p^{1/2}).
- Clock cycle: τ = (p^{1/2})^{1/3} = p^{1/6}.
- Optimal P = p^{1/2}, wall-clock = p^{1/6}.
- Full cost: p^{1/2} × p^{1/6} = **p^{2/3}**.
- Matches Wiener's BSGS result with group order n = |V| ~ p.

**Delfs-Galbraith (F_p regime):**
- DG is MITM on the F_p-rational subgraph of |V^{F_p}| ~ √p vertices.
- Table of p^{1/4} entries, p^{1/4} lookups.
- Step count: O~(p^{1/4}).
- Clock cycle: τ = (p^{1/4})^{1/3} = p^{1/12}.
- Full cost: p^{1/4} × p^{1/12} = **p^{1/3}**.

**VW distinguished-point collision search (both regimes):**

Walk model: at each vertex (supersingular curve E), select one of (ℓ+1)
order-ℓ subgroups of E[ℓ] via a seeded hash h_i(j(E)) = H(i || j(E))
mod (ℓ+1), where i is the processor seed. Compute the ℓ-isogeny via Vélu.
ℓ is a small fixed prime (ℓ=2 for CGL). Computing E[ℓ] and its subgroups
is polynomial in log p for fixed ℓ.

Parallelization (F1 fix): assign P/2 distinct seeds to walks from E_0
and P/2 distinct seeds to walks from E_1. Each processor explores a
different path from its endpoint. A collision between any E_0-walk and
any E_1-walk yields a path E_0 → E_1. Walks diverge after O(1) steps
with probability 1 - (1/(ℓ+1))^t.

Distinguished predicate: j-invariant with d leading zero bits in
canonical F_{p^2} encoding (d tunable; set 2^d = p^{1/4} for optimal
full cost on F_{p^2}, 2^d = p^{1/8} for F_p).

Collision-to-path reconstruction: re-run both walks from their starting
curves using the same seeded hash function, using distinguished-point
segmenting to locate the merge vertex in polynomial space. Compose one
path with the dual of the other (Vélu duals from recomputed kernels)
plus the F_{p^2}-isomorphism for curves at the same j-invariant. No
uncharged oracles. Reconstruction must record which walk function
(processor seed) produced each distinguished point.

Clock cycle: set by per-processor storage O(1), not the shared table,
because the table is accessed only at distinguished points (amortized
cost O(p^{-1/6}) per step, subconstant). Wall-clock = O~(p^{1/4}) for
F_{p^2}, O~(p^{1/8}) for F_p.

- F_{p^2}: P = p^{1/4} useful processors, p^{1/4} steps each.
  Full cost: p^{1/4} × O~(p^{1/4}) = **p^{1/2}**.
- F_p: P = p^{1/8} useful processors, p^{1/8} steps each.
  Full cost: p^{1/8} × O~(p^{1/8}) = **p^{1/4}** (conditional on mixing).

### Mixing assumption (N4, NF2)

The O~(√|V|) birthday bound assumes O(log p) mixing steps have occurred
(Ramanujan property for F_{p^2}). The birthday bound on a Ramanujan graph
is heuristic (birthday paradox on mixed walks), not a direct transfer of
Wiener's group-theorem. The exponent is unaffected if collision occurs
before mixing (only the constant may differ).

For F_p: the F_p-rational subgraph G_ℓ^{F_p} is NOT known to be Ramanujan.
VW on F_p requires rapid mixing for the birthday bound — a stronger
assumption than DG's BFS-based MITM, which needs no mixing. If the mixing
assumption fails, DG at full cost p^{1/3} remains the matched baseline.

## Matched-baseline recommendation

Under Wiener full-cost accounting, the honest matched classical baseline
is **VW distinguished-point collision search**, not MITM or Delfs-Galbraith:

| Regime | MITM full cost | DG full cost | VW full cost | Matched baseline |
|--------|---------------|-------------|-------------|-----------------|
| F_{p^2} | p^{2/3} | n/a | **p^{1/2}** | VW |
| F_p | p^{2/3} | p^{1/3} | **p^{1/4}** (cond. mixing) | VW (cond. mixing) / DG (fallback) |

The full-cost exponent of the matched baseline equals the step-count
exponent because VW's polynomial space eliminates the 3D wiring penalty.
Full-cost accounting changes *which algorithm is the baseline* (MITM/DG →
VW) but does not change the hardness exponent (p^{1/2} for F_{p^2},
p^{1/4} for F_p).

## Decision relevance

This is decision-relevant for novelty screening: future candidates must
beat the VW full cost (p^{1/2} F_{p^2}, p^{1/4} F_p conditional on mixing),
not the easier MITM p^{2/3} or DG p^{1/3} full cost. A high-memory candidate
pays the wiring penalty on top of its step count; a low-memory candidate
must beat the VW polynomial-space baseline directly.

## Applicability limits

- This is a matched-baseline correction, not an attack. It does not improve
  the cost of attacking any surviving supersingular hardness assumption.
- The F_p VW variant is conditional on unproven F_p subgraph mixing.
- The birthday bound on the Ramanujan graph is heuristic (NF2).
- Full-cost constants from KN-LIT-094 are asymptotic with unextracted o(1) terms.
- Does not address CSIDH quantum costs (KN-OPEN-014), orientation (KN-OPEN-013),
  or SQIsign transcript leakage.
- ℓ must be a small fixed prime; large ℓ changes per-step costs.
