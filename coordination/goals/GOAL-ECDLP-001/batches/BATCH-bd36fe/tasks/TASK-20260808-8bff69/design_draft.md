# Successor instrument design — oracle-vs-exhaustive-search and the MITM true-null control

- Task: TASK-20260808-8bff69 (BATCH-bd36fe), role: coordinator, policy `coordinator-orchestration-code`
- Design drafting only. Nothing in this file approves, freezes, authorizes, or records anything; no executor task, run, data, evidence, or ledger-state update exists because of it.
- Ground truth consulted: `ledger/decisions/DEC-20260808-6a7ac4.yaml`, `ledger/evidence/EV-ECDLP-65b004.yaml`, `ledger/hypotheses/H-XOR-d1a480.yaml`, `experiments/EXP-SEMAEV-f48dd1/specification.yaml`, `experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`, `experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/`.

## 1. What the evidence leaves open

EV-ECDLP-65b004 + DEC-20260808-6a7ac4 established, within their exact toy scope (m=3, p in {101,103,107,211}, b in {0.4,0.5}, 5 seeds, n=8 independent groups):

- Y_A = Y_B exactly (relations per enumeration space |F|^m, 40/40 configurations) — the x-oracle does **not** add yield over exhaustive search on the same space.
- Y_B ≫ Y_C (Δ=0.01202 vs the uninformative PRNG predictor) measures "structured search beats a random null", not oracle-specific yield.
- No charged cost model exists; "faster"/"speedup" is currently undefined (red-team MODERATE objections, preserved in the decision).

The remaining honest question is **cost, not yield**: on a *charged* model (field operations), does MITM-with-oracle (Arm B) reach the same relations cheaper than exhaustive (Arm A)? And is any such cheapness owed to the oracle's information, or to the MITM structure itself? The second part is exactly what the red-team's "Arm D: random-from-F_p MITM (true null)" probes.

## 2. Structural note: Y_A = Y_B is mechanical, not a lucky coincidence

Over the frozen machinery (factor base `F` of size `B = floor(p^b)`, complete MITM over the same pairs):

- Arm A enumerates all `|F|^3` triples at 2 adds each → cost ≈ `2·|F|^3` field adds; `R` = relations (triples summing to O). Note `|F|` counts the point entries in the impl's `points` list (approximately 2× the x-base size, since each x lifts to two points mod ±1). The frozen grid yielded `Y_A ≈ Y_B ≈ 0.01213` over the `|F|^3` space, so `R ≈ 0.01213 · |F|^3`.
- Arm B builds the right-half table with `|F|²` adds, then for each left element performs one query and, when the query x matches `x(P2+P3)` of the table, verifies the candidate with 2 adds. For exact matching lookups over the same element set, *every* relation triple is found exactly once (the left x matches exactly when the triple sums to O), and **no uninformative candidates are examined beyond the table bucket for a genuine match**.
- Consequently `Y_B = Y_A` holds structurally for any complete MITM with exact lookups over the same factor base — replicating it in a successor global adds confirmation that the machinery was correctly built (a control, tracked as CTRL below) rather than a new finding. This design therefore treats the A-vs-B *yield* comparison as a **machinery control**, and the *cost* comparison as the carrying instrument.

So: this design executes the successor question with three arms:

| Arm | Query source | What it isolates |
|---|---|---|
| A | — (full enumeration) | baseline exhaustive cost at fixed yield R |
| B | exact `x of the sum` lookup (the x-oracle) | oracle-guided MITM |
| D | uniform random value from F_p, same query count and same table | true-null: MITM **structure** with no oracle information |
| (C, retained) | PRNG ≈ as frozen | historical control for continuity with EV-ECDLP-65b004 |

## 3. Design contract (pre-registered, candidate to be frozen by /design-experiment)

**Hypothesis (provisional, for the successor):** H-XOR-COST-<suffix> — in the frozen toy universe, with a charged cost model, the oracle-guided MITM arm reaches the complete relation set with strictly fewer field operations than exhaustive search, and strictly fewer than the random-null MITM arm: `C_A > C_D > C_B` per cell, where `C` is total field additions as counted by the implementation.

**Mechanism / accounting (the charged model — FIRST, per red-team objection):**
Charge every arm in a single unit: **one field operation = one `E.add` evaluation as performed by the implementation** (the frozen `harness.toycurve` add). Declared accounting:
- Arm A: `2|F|^3` (each triple = lhs add + rhs add).
- Arms B and D: `|F|^2` (right-half table construction, every bit adds) + `Q` oracle queries + `2 × candidates_verified` (each verified candidate costs 2 adds) + 0 hash ops (hash table probing is charged in the secondary wall-clock meters: table lookups measured and reported, NOT in the primary charge — so the primary charge is the conservative one for the oracle).
- Queries: B's query is `x(P2+P3)` of the left element (zero extra computation — the x-coordinate is a free attribute of the stored element; the oracle in the implementation is a field accessor, not a charged query). The genuine cost contrast lives in the **candidate-verification count**, not in the query value itself: B verifies only true-match candidates (expected ≈ R), D verifies candidates when a random value happens to collide with a table bucket (expected ≈ #distinct-keys-in-table/p per query — chance-level).
**Predicted scaling:** `C_A ≈ 2|F|³` (two adds per triple); `C_B ≈ |F|² + 2·R` (one add per pair in the table, two adds per true-match candidate); `C_D ≈ |F|² + 2·(#chance collisions)` where expected collisions ≈ `Q · (|distinct keys| / p) · avg bucket size` — strictly `C_B < C_D < C_A`: the predicted ranking, to be matched to measured in the run's analysis.yaml.

**Predictions:**
1. `C_B < C_D` in every cell (the decisive claim: oracle-guided verification is strictly cheaper than chance-collision verification, isolating the oracle's information as load-bearing).
2. `C_D < C_A` in every cell (MITM structure alone, even with random queries, beats full enumeration; both arms' verification loads are tiny relative to exhaustive search).
3. `R_A = R_B ≥ R_D` (per cell): B finds the complete relation set exactly like A; D, with the same query count but random query values, finds the subset of relations whose matching buckets a random draw happens to hit — expected fraction ≈ `Q · (|distinct table keys| / p)`, a direct measurement of how much of the space the null sees. `R_D/R_B` is the null's information rate and the reason the true-null arm exists.

**Test boundary (fixed universe, frozen-identical):**
- m=3; p ∈ {101, 103, 107, 211}; b ∈ {0.4, 0.5}; seeds {1..5}; cell = (p, b) group with 5 seeds → n=8 groups total, exactly the analysis structure that produced the corrected n=8 statistics; NEVER pseudo-replicate cells together.
- Same curve construction rule (deterministic first nonsingular curve with 2m−1 = 5 point of order ≥ 5, exactly `harness/toycurve` calls) — reproducibility binding enforced by `git`-pinned blobs at archive (the `CTRL-BLOB` gate).

**Controls:**
- CTRL-QUERY-COUNT: arms B and D execute exactly the same oracle-query count (the existing CTRL-SMOKE-QUERY-MATCH equality, extended to D).
- CTRL-PRNG-NO-COLLISION: arm D's PRNG is collision-free within the run (existing control, extended).
- CTRL-BLOB: implementation byte-identical to the frozen blob at its archived `sha256` (the no-reimplementation gate).
- CTRL-YIELD-REF: B reproduces `R_A = R_B` (the Y_A=Y_B equality re-derived per-config as a machinery control).

**Metrics:** primary per cell (`p,b` averaged over seeds): C_A, C_B, C_D (field adds), R_A/R_B/R_D relation counts, and R_D/R_B (null information rate); secondary: hash-table probes, wall-clock per arm, memory. No other metric is a hypothesis driver.

**Stopping and early-exit rules:**
- Fixed set of 24 cells (4 primes × 2 b × [A, B, D]) = 24 runs × 5 seeds = 120 arm-runs, ≤ 60 min wall budget total.
- Early-exit: stop and escalate if in ≥2 of the first 4 cells `C_D ≤ C_B` — that falsifies prediction 1 immediately (the oracle is not load-bearing), record as a negative result, close the successor.
- Any infrastructure failure is recorded as failed_infrastructure, not as a result (AGENTS.md rule 5).

**Falsification criteria (registration-adopted):**
- F1: in any cell `C_B ≥ C_A` → the oracle+MITM does not beat exhaustive in the charged model → scoped rejection of H-XOR-COST-<suffix>.
- F2: in any cell `C_B ≥ C_D` → MITM structure alone reaches the same point cheaper or equally; the oracle is the wrong carrier of the benefit → hypothesis scoped-rejected (close the lane with the honest structure-vs-information breakdown).
- F3 (partial-success terminal boundary): `C_D` relation-match rate `R_D/R_B < 0.95` at the B-equal query count → null arm is a discriminative control (as designed); `R_D/R_B ≥ 0.95` would indicate the oracle provides no information (would converge the finding to near-null).
- Controls that trip = invalid run, never evidence.

**Required artifacts (to be listed in the frozen spec; all archive-bound):** spec `experiments/EXP-XOR-COST-*/specification.yaml` + amendments dir; implementation blob; runs/`RUN-XOR-COST-*/` manifest.json, raw-results.json, analysis.yaml; snapshot commit post-run, ledger commit after reviews; models: at least reviewer + validator + red-team (this is a first charged-cost artifact, review is mandatory, policy `review-adversarial`).

**Charged-cost declaration (hard gate from the red-team MODERATE objection):** ANY subsequent "speedup" or operator derived from this run MUST be defined as `(C_A − C_B)/C_A` under the declared accounting, live-operated, with spread ± measurement noise at n=8; toy amplitude only; no crypto-scale extrapolation (AGENTS.md rule 7).

## 4. Pareto honesty

- `dominated_by`: **null** — checked against the effort frontier. Rows considered: time (cost model adds a charged-measurement dimension the yield-only predecessor does not carry — not dominated), memory (unchanged toy footprint; no competitor offers lower memory for the same measurement), data/queries (the true-null arm D is new surface; no existing design covers R_D/R_B), and evidence strength (no predecessor offers a pre-registered charged cost claim for this lane). Nothing on the frontier dominates this contract; conversely nothing new is claimed beyond it.
- `sota_delta`: none claimed at design stage. The run's honest payoff is a *charged cost model + oracle-vs-null* measurement at toy scale — the first charged-cost artifact in this lane, above what EV-ECDLP-65b004 recorded (which had no cost model and no null arm); a future delta must be measured, not asserted.

## 5. Open follow-through (for the Coordinator in a subsequent dispatch)

- Route this design through `/design-experiment` for a freeze decision, or a fresh `/propose-ideas` pass if a different successor is preferred; this draft freezes nothing.
- Prefer one contract carrying all arms (arms A/B/C ride along; the charged battery + D null are the actual substance) under a single new minted id.
- No executor decision happens here; approval gates live in /design-experiment per policy, not in this draft.
