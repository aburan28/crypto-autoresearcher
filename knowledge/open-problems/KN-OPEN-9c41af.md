---
id: KN-OPEN-9c41af
type: open_problem
title: Is there a practical open-source-solvable exact (or certified near-exact) method for minimum depth-reducing vertex-deletion sets on sparse, log-degree "doubling-distance" DAGs at n around 64?
tags: [depth-robust-graphs, vertex-deletion, ilp, cbc, branch-and-bound, calibration, memory-hard-functions, argon2, tooling-gap, open]
confidence: reported
status: open
source_refs: [EV-ARGON-43acd9, DEC-20260906-3b6bdc, EXP-ARGON-2608c2]
added: 2026-09-06
superseded_by: null
---

## The observation

`GOAL-ARGON-001`'s `EXP-ARGON-2608c2` needed an INDEPENDENT-of-the-greedy-
heuristic exact reference value on two small synthetic calibration graph
families, to bound the greedy eps-depth-reducing-set heuristic's own
systematic error before trusting any Argon2-derived measurement built on
it (`IDEA-20260809-bcf891`'s calibration design, `DEC-20260812-03fa10`).
One family — `family_B_pure_chain` (no reference edges at all) — is
exact-trivial at every tested size (minimum removal set is always exactly
1 node, the chain's own midpoint; CBC proves this in under 0.02s even at
q=64). The other — `family_A_doubling_graph` (a chain plus a reference
edge from each node `j` to `j - 2^k` for every `k` with `1 <= 2^k < j`,
i.e. `O(log q)` degree per node, deliberately chosen to be "depth-robust-
leaning" without importing an unverified external construction) — certified
cleanly at q=16 (minimum 5, 5.3s) and q=32 (minimum 8, 39.3s), but at q=64
the only ILP tooling available in this environment (`pulp` 3.3.2 / bundled
CBC 2.10.3, no commercial solver reachable) could not close the
branch-and-bound optimality gap within a 150s declared budget nor a 300s
diagnostic extension: incumbent 17 (a genuine, independently
`verify_ok: true` upper bound), dual bound only 4.433 (rounds to 5). The
true minimum is known only to lie in `[5, 17]`.

## Why this reads as a genuine tractability wall, not an implementation bug

Three independently attempted formulations converge on the same
qualitative picture (`experiments/EXP-ARGON-2608c2/implementation.md`,
"Exact-computation tractability finding"):

1. A naive big-`M` MILP (`M = n+2` uniformly): LP relaxation root bound
   ≈0.24–0.35 against integer optima of 5–21 — extremely weak.
2. A lazy cutting-plane / Benders-style formulation (path-hitting
   constraints added iteratively): defeated by LP-degenerate ties among
   many equally-good single-node cuts, an artifact of the family's own
   symmetry — still exploring 2-element subsets after 130+ rounds on a
   16-node graph.
3. Two from-scratch branch-and-bound implementations (path-length
   branching; then include/forbid-pivot branching with a vertex-disjoint-
   path-packing lower bound): both *improved* the incumbent over the
   greedy heuristic's starting bound but neither *proved* optimality for
   q>=32 within a 90s budget.

The formulation actually used for the reported numbers (a tight-`M` MILP
with per-edge and per-node `M` values, `graphs.exact_min_removal_ilp`) is
provably correct (proof in its docstring) and reproduces the exact values
independently confirmed by brute force at q=16 for both families
(family_A: 5, family_B: 1) — the gap is CBC's ability to close
branch-and-bound within budget on this specific family at q=64, not a
formulation or correctness defect.

One genuinely important, separately noteworthy finding surfaced along the
way: `pulp`'s `LpStatus[status] == "Optimal"` does **not** by itself mean
CBC proved optimality — `contextlib.redirect_stdout` does not capture
CBC's subprocess-level log, so an early version of the solver wrapper
silently mis-classified a time-limited run as `proven_optimal`. The fix
(redirect OS file descriptor 1 directly, parse the captured text for
"Stopped on time limit") is a reusable lesson for anyone wrapping CBC via
`pulp` and trusting its status field at face value.

## Why this generalizes beyond Argon2

`family_A_doubling_graph` is a generic, minimal example of a sparse
`O(log n)`-degree depth-robust-leaning construction — it has no Argon2-
specific content. Any future calibration design (in this program or
elsewhere) that wants an independent EXACT reference value for a
node-removal / depth-reduction quantity on a similarly sparse,
many-overlapping-path DAG at `n` in the few-tens-to-hundred range, using
only open-source ILP tooling, is likely to hit the same wall for the same
structural reason (weak LP relaxation from symmetric long-range edges).
This is worth knowing BEFORE designing a calibration gate that requires
exact certification at a specific size, rather than discovering it after
spending the budget.

## Open questions

- **Q1.** Is there a combinatorial-structure-specific exact algorithm for
  minimum depth-reducing vertex-deletion sets on a "doubling-distance"
  DAG (e.g. exploiting the recursive self-similarity of powers-of-two
  back-edges) that beats generic MILP branch-and-bound at n~64?
- **Q2.** Would a commercial solver (Gurobi, CPLEX) close this specific
  gap within a comparable time budget, or does the weak LP relaxation
  defeat cutting-plane strengthening regardless of solver?
- **Q3.** Is there a tighter MILP formulation (stronger valid inequalities
  exploiting the doubling structure specifically, e.g. clique or
  odd-cycle cuts derived from overlapping power-of-two paths) not yet
  tried here?
- **Q4.** For calibration purposes specifically, is a CERTIFIED BRACKET
  (upper via incumbent, lower via dual bound) an acceptable substitute for
  a point-value ratio in a gate like `bcf891`'s, and if so what bracket
  width should such a gate tolerate before treating the cell as
  uncertified? (`DEC-20260906-3b6bdc` treats the current [1.235, 4.20]
  bracket as failing to satisfy a point-in-[1.0,1.5] gate; a differently
  designed gate could in principle be built around bracket width instead.)

## Concrete successor action

Cheapest first step: try Q3 (stronger valid inequalities exploiting the
doubling structure) before reaching for Q2 (commercial solver, an
environment/licensing dependency) or Q4 (a gate redesign, which needs a
Coordinator-approved protocol_amendment). None of this is undertaken by
filing this entry; `GOAL-ARGON-001`'s impediment IMP-1
(`ledger/goals/GOAL-ARGON-001.yaml`) names the three routes considered and
defers the choice to whoever picks up that lane next.
