# Analysis: lopsided batch decomposition for relation collection

## Relevance claim (the point)

Point decomposition $R = P + Q$ is $P + Q + (-R) = 0$: a 3SUM-shaped
3-term relation. The paper's chain runs 3SUM / Exact Triangle $\to$
lopsided All-Edges Sparse Triangle (= offline Set Disjointness) $\to$
wanted entries of a thin product. Our MITM table-lookup join is an offline
set-intersection workload of exactly that shape, so the paper is directly
relevant to relation collection: batched decomposition converts to
lopsided wanted-pairs instances, and the thin-product oracle resolves them.
This task builds that conversion with a clean oracle seam and proves the
conversion itself is exact.

## Measured results (`results.json`, deterministic seeds)

- **Exactness gate: PASS.** Baseline, lopsided+hash, lopsided+scan return
  bit-identical relation sets on all 3 instances (244, 256, 123 relations;
  planted + random targets). No discrepancies by construction (exact
  counting in `count_chunk`) and machine-checked (`exact_agreement: true`).
- **Strassen kernel: 204/204 exact** (200 randomized + zero/identity/
  big-int controls), 7 vs 8 mults. Mechanism-class demonstration only.
- **Form overhead (hash seam): exactly $g$** (8.0, 20.0, 4.0 = chunk
  counts). The lopsided reorganization multiplies hash probes by the chunk
  count — this is the price the future oracle must pay for, and it tells
  the integration exactly what saving factor is needed ($> g$ per chunk).
- **Scan seam totals $T \cdot F^2$ regardless of chunking** (4.0M / 4.0M):
  reorganization alone saves nothing under linear scan — the win must come
  from the algebraic oracle, consistent with the paper (its win is the
  pruned Schönhage recursion, not the tiling).

## Regime map (analytic, 256-bit group order)

| $m$ | $\varepsilon = \log|F|/\log N$ | oracle-eligible (general, $\le 0.1204$) | strict Thm 5 ($\le 1/18$) |
|---|---|---|---|
| 2–7 | 0.50–0.15 | no | no |
| 9 | 0.115 | **yes** | no |
| 12–18 | 0.089–0.063 | yes | only 18 |

The $|W|$ density condition is slack for us (our query load is far sparser
than the paper's ceiling; Theorem 25 covers sparser $W$). Thinness binds.

## Conclusion for the program

1. **Integration seam exists and is verified exact.** `count_chunk` is the
   plug-in point; any future thin-product oracle drops in without touching
   relation semantics, and today's exact seam keeps every downstream
   certificate (harvest-style verification) green.
2. **Payoff cell is high arity ($m \ge 9$).** Current engines run $m \le 7$,
   where the factor base is too large to be a thin middle. The paper is
   therefore a forward pointer: it motivates pushing decomposition arity up
   (unexplored territory — §5 arity ladder stops at $m = 7$) AND integrating
   the oracle there, as a paired advance. Neither half alone pays.
3. **No speedup claimed today.** The oracle is assumed, not implemented;
   its op units (word-RAM mult-adds) are incomparable with our cost columns
   ($S_3$ solves, membership tests); the paper's constants are stated
   enormous, so no crossover is asserted at any concrete size.
4. **Negative byproduct, recorded honestly:** a hand-transcribed Schonhage
   10-product kernel failed its own randomized check and was deleted, not
   repaired — correct transcription is deferred to the paper source / Lean
   formalization (`anthropics/formal-math/.../3sum-apsp`, not yet checked
   out here). Next actions: (a) check out + build that Lean repo; (b) design
   experiment for $m \ge 9$ decomposition feasibility (relation rate at
   thin $|F|$ comes first — the oracle is useless without relations).

Scope: toy synthetic group $\mathbb{Z}_M$, not curve points; numbers are
op counts, never wall time.
