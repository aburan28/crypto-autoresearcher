# EXP-SEMBIN-509d41 RESULTS (Stages 0–2)

Recorded at: 2026-10-03T01:12:17Z  
Stage 2 task: `TASK-20261002-d67dd7` · Admission: `DEC-20261003-054ae8` · Archive: `TASK-20261003-2e4a0a`  
Expand prior: `DEC-20261003-c77494` / `EV-SEMBIN-d1cf99`  
Approved by: `DEC-20261002-15b02c` · Stage-2 plan: `trial-plan-stage2-v1.json`  
Historical Stages 0–1 plan: `trial-plan-v1.json` (byte-identical; not rewritten)

## Outcome label

Exactly one primary label: **`O-IMPEDIMENT`**

HEUR-TOP verdict: **`SKIPPED_IMPEDIMENT`** (no admitted Groebner/Macaulay backend on host).

This is never negative mathematical evidence against (C1)–(C5). Stage-1 `S1-INVARIANTS-OK` remains intact.

## Outcomes by run

| Run | Stage | Outcome | Status |
|---|---|---|---|
| `RUN-SEMBIN-9000a8` | 0 | `S0-FREEZE-OK` | `output_validated` |
| `RUN-SEMBIN-bd538f` | 1 | `S1-INVARIANTS-OK` | `output_validated` |
| `RUN-SEMBIN-ee4b22` | 2 | `O-IMPEDIMENT` / `SKIPPED_IMPEDIMENT` | `output_validated` |

## Stage 0–1 (unchanged)

Frozen Stage-0 worksheet and Stage-1 combinatorial re-enumeration / DAG known-false control as archived under `TASK-20261003-caff4e` / tip `0e279b09c5`. Tree counts `(2t-3)!!`, invariant hold rate 1.0, design figures OK. See prior RESULTS content in git history at that tip.

## Stage 2 (HEUR-TOP cell)

Cell: `(n,t,k)=(16,5,4)`, `N_boolean=68`, master seed `20261002c94`.

Shape binding (`stage2/shape-binding.json`), per `DEC-20261003-c77494`:

| Arm | Tree | sigma_top |
|---|---|---|
| path | `((((0, 1), 2), 3), 4)` | 52480 |
| cherry_caterpillar | `((((0, 1), 2), 3), 4)` | 52480 |
| **balanced (near-worst)** | `(0, ((1, 2), (3, 4)))` | **91648** (= max) |
| mid-split (rejected) | `((0, 1), (2, (3, 4)))` | 39424 (= min; not used) |
| random_boolean_null | — | — |

Backend probe (`stage2/backend-probe.json`): sage / magma / M2 / Singular **absent**. Sympy groebner present but **not** admitted as Semaev success path for `N=68`.

Instances completed per arm: **0** (impediment before timing).  
Peak RSS (probe): **51163136** bytes. Wall (probe): **≈0.154 s**.

Artifacts: `stage2/per-instance.jsonl`, `stage2/arm-summaries.json`, `stage2/shape-binding.json`, `stage2/backend-probe.json`, `stage2/impediment.md`.

## Scope / non-claims

No Magma/Sage/AUXIN success path. Amazon Bedrock: **NOT SELECTED**.  
No exponent move, IC-vs-rho, FIPS verdict, or deployed-curve ECDLP claim.  
No second `(n,t,k)`. Observations only — no hypothesis status change in this packet.  
Ready for `/review-evidence`.
