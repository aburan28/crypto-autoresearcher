# EXP-BINSTD-6f3434 Stages 0–1 results

**Experiment:** `EXP-BINSTD-6f3434`  
**Hypothesis:** `H-BINSTD-3b1f2d`  
**Decision / plan:** `DEC-20261003-bc5802` / `trial-plan-v1.json`  
**Task / claim:** `TASK-20261003-9f89f3` epoch 1 (`executor-run-6f3434-9d55`)  
**Branch tip at run:** `cursor/run-binstd-6f3434-stages01-9d55`  
**Amazon Bedrock:** NOT SELECTED. No AUXIN / Magma / Sage provisioned.

## Coverage

| Trial | Run ID | Driver outcome | Receipt |
| --- | --- | --- | --- |
| `stage0-schedule-api-freeze` | `RUN-BINSTD-95b5eb` | `S0-FREEZE-OK` | `output_validated` |
| `stage1-n17-charged-cost` | `RUN-BINSTD-970fc9` | `O-IMPEDIMENT` | `output_validated` |

`tools/experiment_execution.py` coverage: `measurement_complete: true` (2/2 `output_validated`).

## Stage 0

Freeze artifacts written under `stage0/`:

- `schedule-api.json` — band `0.85`, cells `(n,ℓ)∈{(17,3),(17,4)}`, pin `xorsat-pin-BINSTD-6f3434-v1`, seed `20261003161102`
- `preregistered-predictions.json`

Zero scientific charged-cost ratios before freeze (protocol satisfied).

## Stage 1

Outcome label: **`O-IMPEDIMENT`**

Reason (from `stage1/charged-cost-n17.json`): live XOR-SAT pin not available; S₃/S₄ encoder paths were probed (`experiments/EXP-BINSTD-89d952/implementation/…`) but the scientific schedule bake-off is not authorized without the frozen solver pin.

A meter self-test fixture was recorded separately and **asserts nothing** about `HEUR-BINSTD-161102-H1`.

No `E-S4-CHEAPER` / `E-S4-NOT-CHEAPER` / `E-INCONCLUSIVE` scientific label. No break / exponent / n≥131 / rho claim.

## Scope

Observations only for Stages 0–1 on the approved toy cells. Infrastructure absence is not negative mathematical evidence (AGENTS.md rule 3).
