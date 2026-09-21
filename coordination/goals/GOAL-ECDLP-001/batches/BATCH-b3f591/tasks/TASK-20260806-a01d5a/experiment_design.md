# Experiment Design — X-Oracle Semaev Yield Discrimination (Toy Scale)

**Task:** TASK-20260806-a01d5a (Producer D), BATCH-b3f591, GOAL-ECDLP-001
**Candidate experiment id:** `EXP-SEMAEV-f48dd1` (reserved; `allocate_id.py --check` confirmed free 2026-08-06)
**Status:** design only — no specification.yaml committed; contract frozen by subsequent ledger decision
**Date:** 2026-08-06
**Open question sourced from:** DEC-20260806-08b9ed (x-oracle-alone question, O_D ≡ x-oracle)
**Corridor reconciled with:** DEC-20260806-26c0e8, DEC-20260806-bba4bf (corridor emptiness not re-litigated)

---

## 0. Scope statement (rule 7 — toy vs crypto)

This experiment is **toy-scale only**. It tests whether an x-coordinate oracle
during Semaev relation collection moves relation yield above a run-matched null
on curves of order N < 200. No result from this experiment, regardless of
outcome, is presented as evidence about crypto-scale ECDLP, sub-rho attacks,
or the asymptotic power of the x-oracle class. Toy evidence can motivate or
falsify a mechanism at toy scale; transferring to crypto scale requires a
separate correspondence argument (which does not currently exist for this
question).

---

## 1. Question and hypothesis

**Question (from DEC-20260806-08b9ed §exact_next_action item D).**
An oracle O_x returning x(P) for queried points P — algebraically equivalent
to the halving oracle O_D — is the only surviving open direction from the
BATCH-e0ccb2 audit. Does access to O_x during Semaev relation collection move
the relation yield above a run-matched null?

**Hypothesis H-XOR-YIELD (falsifiable, toy scope).**
For fixed toy curve E/F_p, factor base F, and Semaev arity m, the relation
yield (relations found per m-tuple enumerated) under an x-oracle-guided
enumeration strategy is strictly greater than the yield under an identical
enumeration strategy driven by a random predictor of the same query shape.

**Null hypothesis H0.** Yield(x-oracle) = Yield(random predictor), i.e. the
x-coordinate information is not exploitable by the pre-registered strategy at
the tested parameters.

**Falsification criteria.**
Reject H-XOR-YIELD if any of:
1. Yield(x-oracle) − Yield(random) is not statistically different from zero at
   α = 0.01 (two-sided) on every completed cell.
2. Yield(x-oracle) ≤ Yield(no-oracle) on every completed cell (oracle is
   strictly no better than blind enumeration under this strategy).
3. The x-oracle and random predictor yields are both equal to the no-oracle
   yield within the pre-registered equivalence margin δ = 0.005 (oracle
   information is inert at these parameters).

A timeout or implementation failure is not evidence against H-XOR-YIELD
(AGENTS.md rule 5).

---

## 2. Mechanism

In Semaev relation collection over factor base F with arity m, enumerate
m-tuples (P_1, ..., P_m) ∈ F^m and test whether P_1 + ... + P_m = O.

The x-oracle arm implements a pre-registered meet-in-the-middle (MITM)
splitting strategy that uses x-coordinate queries at the split boundary:

- For m = 4: split into left half (P_1, P_2) and right half (P_3, P_4).
  Pre-compute a hash table H mapping x(P_3 + P_4) → list of right-half tuples
  for all (B choose 2) + B^2 right-half pairs. During left-half enumeration,
  compute S_2 = P_1 + P_2, query O_x(S_2) = x(S_2), and look up in H. A hit
  yields a candidate relation; verify the full sum.

- For m = 3: split 1 + 2. Pre-compute H mapping x(P_2 + P_3) → list for all
  right-half pairs. During left-half enumeration of singletons P_1, query
  O_x(P_1) and look up in H for x(P_2 + P_3) = x(−P_1) = x(P_1).

The random predictor arm runs the **identical** MITM structure with the same
hash table, the same enumeration order, and the same number of oracle queries,
but O_x(P) is replaced by a deterministic PRNG output keyed on the query point
(collision-free within each run by construction). The no-oracle arm runs
exhaustive enumeration without MITM splitting (all m-tuples checked directly).

The discrimination is between arms B and C, which are run-matched in every
respect except the truth value of the oracle responses. Arm A is the baseline
for context.

---

## 3. Parameter cells (corridor-compatible)

The corridor-emptiness findings of DEC-20260806-26c0e8 and
DEC-20260806-bba4bf are accepted as settled. This experiment does not test
the rescue window, does not claim K*(std) = ∞ vs K*(BKK) < ∞, and does not
exercise any parameter cell in the proven-empty corridor. Parameter cells are
chosen from the ranges actually exercised by the cell-grid run
(RUN-MTBK-306bdb-cellgrid) and the Semaev experiments (EXP-SEMAEV-001/002).

| Factor | Levels | Basis |
|---|---|---|
| Arity m | 3, 4 | tested in EXP-SEMAEV-002; corridor-empty for m=5 at all planned N |
| Prime p | 101, 103, 107, 211 | EXP-SEMAEV-002 curve set |
| Factor-base exponent b | 0.4, 0.5 | cellgrid-tested range; b=0.6 retained as optional extension |
| Factor-base size B | ⌊p^b⌋, threshold-adjusted | deterministic per (p, b) |
| Seeds | 5 per cell | deterministic, recorded |

Total cells: 2 (m) × 4 (p) × 2 (b) × 5 (seeds) = 80 config-run combinations.
Each combination runs all three arms (A, B, C), so 240 arm-runs.

**Cell exclusion rule.** If B^m / N < 0.05 or > 0.8 for a (m, p, b) cell, the
cell is dropped and the exclusion recorded. A dropped cell is a scoped
negative, not evidence (per EXP-MTIC-001 precedent).

---

## 4. Controls — null-object triple (pre-registered)

Three arms with identical sampling, identical curve instances, identical factor
bases, and identical seed sequences:

| Arm | Oracle | Query shape | Response |
|---|---|---|---|
| A: no-oracle | none | none | exhaustive enumeration, no MITM |
| B: x-oracle | O_x(P) = x(P) | one query per left-half tuple | true x-coordinate |
| C: random predictor | O_rand(P) = PRNG(key‖P) | one query per left-half tuple | deterministic pseudo-random field element |

Arms B and C are **run-matched**: same code path, same branching, same number
of queries, same hash-table lookups. The only difference is the response
value. This is the inventor-protocol "controls before belief" requirement
(DEC-20260806-bba4bf §inventor): any reported signal is an artifact until the
identical measurement has been run against a null object of the same shape.

**Control pass conditions:**
1. Arms B and C must execute the same number of oracle queries per config
   (verified by counter in raw JSON). Mismatch → cell invalid.
2. Arm C's PRNG must be collision-free within each run (verified by
   post-run check). Collision → cell invalid.
3. Arm A's yield must be consistent with the Semaev random-model prediction
   Y_A ≈ B^m / N (within factor 2). Large deviation → implementation review.

---

## 5. Pre-registered metric

**Primary metric:** relation yield Y_arm = (number of verified relations found)
/ (number of m-tuples enumerated or attempted) per (cell, arm, seed).

**Derived metric:** Δ = Y_B − Y_C (x-oracle yield minus random-predictor yield)
per cell, averaged over seeds.

**Secondary metrics:**
- Hash-table hit rate per arm (hits / queries).
- False-positive rate: fraction of hash-table hits that do not yield a verified
  relation.
- Enumeration cost per relation (m-tuple attempts / relations found).
- Wall-clock seconds per cell per arm (reported, never used as the primary
  metric — field-operation counts are the cost unit).

---

## 6. Stopping rule

1. **Per-cell wall-clock cap:** 300 seconds per (cell, arm, seed). Exceeded
   cells are recorded as `timed_out` and never synthesized into Δ (rule 5:
   timeouts are not evidence).
2. **Total budget cap:** 48 hours core-time across all 240 arm-runs. If
   reached, remaining cells are `cancelled_by_budget`.
3. **Memory cap:** 4 GB per run (hash table for m=4 at B ≈ 100 is
   ~100^2 × 32 bytes ≈ 320 KB; well within cap).
4. **Smoke gate:** one smoke run (m=3, p=101, b=0.4, seed=1, all three arms)
   must complete and pass control checks (§4) before the full dataset runs.
   Smoke review by review-adversarial before extension.
5. **Early stop on separation:** if after 50% of cells the 99% CI for Δ
   excludes zero and the direction is consistent, the remaining cells still
   run (pre-registered completeness), but the analysis may report the
   early-stop point.

---

## 7. Artifacts list

All artifacts under `experiments/EXP-SEMAEV-f48dd1/`:

| Artifact | Path | Content |
|---|---|---|
| Specification | `specification.yaml` | frozen contract (written only after ledger decision) |
| Frozen instances | `frozen-instances.yaml` | curves, factor bases, seeds, SHA-256 |
| Implementation | `implementation/` | source code, oracle interface, PRNG, MITM logic |
| Smoke manifest | `runs/RUN-SEMAEV-f48dd1-smoke/manifest.yaml` | git head, dirty state, command, env |
| Smoke raw JSON | `runs/RUN-SEMAEV-f48dd1-smoke/raw-result.json` | per-arm yield, query counts, timings |
| Per-cell manifests | `runs/RUN-SEMAEV-f48dd1-cell-<id>/manifest.yaml` | one per (cell, arm, seed) |
| Per-cell raw JSON | `runs/RUN-SEMAEV-f48dd1-cell-<id>/raw-result.json` | yield, hits, false positives, cost, timestamps |
| Stats table | `analysis/stats.json` | Y_A, Y_B, Y_C, Δ, CI per cell |
| Analysis | `analysis.md` | pre-registered comparison, control checks, outcome classification |
| Execution report | `execution-report.yaml` | git provenance, model/policy, machine details |

**Raw JSON schema (per cell):**
```json
{
  "cell_id": "m3_p101_b0.4_seed1",
  "arm": "B",
  "oracle_type": "x_coordinate",
  "m": 3, "p": 101, "b": 0.4, "B": 10, "N": 104,
  "tuples_enumerated": 1000,
  "oracle_queries": 100,
  "hash_table_hits": 12,
  "relations_found": 3,
  "relations_verified": 3,
  "false_positives": 0,
  "yield": 0.003,
  "wall_clock_seconds": 1.23,
  "field_operations": 45000,
  "status": "completed",
  "control_checks": {
    "query_count_match": true,
    "prng_collision_free": true,
    "baseline_consistency": true
  }
}
```

---

## 8. Outcome classification (pre-registered)

| Outcome | Condition | Action |
|---|---|---|
| **Oracle-exploitable** | Δ > 0 with p < 0.01 on ≥ 3 cells, direction consistent | Supports H-XOR-YIELD at toy scale; motivates correspondence argument for larger scale |
| **Oracle-inert** | Δ not significantly different from 0 on all cells | Weakens H-XOR-YIELD at toy scale; x-oracle does not improve yield under this strategy |
| **Strategy-artifact** | Y_B ≈ Y_C but both > Y_A | MITM structure itself improves yield, not the oracle information; re-scope hypothesis |
| **Inconclusive** | Cells dropped or timed out below analysis threshold | No conclusion; report scoped negative |

No outcome is presented as crypto-scale evidence (rule 7).

---

## 9. Corridor reconciliation statement

This experiment does **not** test:
- The rescue-window claim (corridor proven empty by DEC-20260806-26c0e8 / bba4bf).
- K*(std) vs K*(BKK) crossover (unreachable at planned sizes per corridor emptiness).
- The BKK speedup factor β = 2/(m+1) (tested separately under EXP-MTBK-306bdb).

This experiment **does** test:
- Whether x-coordinate information, accessed via an oracle interface during
  Semaev relation collection, improves relation yield above a run-matched null
  at toy scale.

The parameter cells are drawn from the ranges validated by the cell-grid run
(m ∈ {3,4}, p ∈ {101,103,107,211}, b ∈ {0.4,0.5}), which are the ranges where
the geometric first-success descent model has review-backed evidence standing
(DEC-20260806-bba4bf D2). No cell exercises the proven-empty corridor.

---

## 10. Coordination notes

- Design produced under TASK-20260806-a01d5a (Producer D).
- Experiment id `EXP-SEMAEV-f48dd1` is reserved, not committed.
- No specification.yaml is written; the contract is frozen by a subsequent
  ledger decision after review.
- No run executes; no run record is minted.
- References: DEC-20260806-08b9ed (x-oracle question), DEC-20260806-26c0e8
  (corridor emptiness), DEC-20260806-bba4bf (corrected corridor derivation),
  EXP-SEMAEV-001/002 (Semaev pipeline), EXP-MTBK-306bdb (cell-grid ranges).
- Status for Coordinator: `design_submitted`. RD to review and grant EXP ID.
