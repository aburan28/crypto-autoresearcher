# RT-20260803-022 — Objections (RC-45 smoke)

**Snapshot:** `e7d14020ca711729e76bbf420d4ec24184a4a7a0` (TASK-20260803-020)  
**Run:** `RUN-IT-001-rc45-smoke` under `PA-IT-001-v3-rc45-repair-5`  
**Open:** `DEC-20260803-003` · Design PASS: `RT-20260803-013`  
**Claim ceiling:** toy · No crypto-scale / asymptotic support / lane death / STR reopen

## Verdict

**PASS_SCOPED** — observations package usable as toy evidence with explicit voids/forbids. Executor admission hygiene holds (RC-45 text untouched; exact frozen smoke command; `c_smart=8` applied, not leftover `1`). Scientific transition from smoke alone is **forbidden**.

## Blocking interpretation (RT-046-B1–B3)

| ID | Title |
|----|--------|
| RT-046-B1 | Forbid sub-rho / transfer-gate / HEUR-ISO-1 support from this smoke |
| RT-046-B2 | Smoke alone insufficient for any scientific transition (measure absent) |
| RT-046-B3 | Planted-path + null-plant positives are packaging theater — void |

## Major / carryovers

| ID | Title |
|----|--------|
| RT-046-M1 | `execution_report` / manifest still emit BATCH-030 / TASK-20260801-143 |
| RT-046-M2 | `c_smart=8` set, but CTRL-ANOMALOUS-TRACE1 never exercised |
| RT-046-D3 | Density null-decay still missing (RT-045-D3 carryover) |
| RT-046-D4 | `c_smart` unit conversion still thin (RT-045-D4 carryover) |

## Informational

- **RT-046-I1:** Snapshot path hashes match; dirty-tree at run disclosed (D2 wiring).

## Checklist (adversarial)

| # | Check | Result |
|---|-------|--------|
| 1 | Illicit sub-rho / transfer / HEUR support? | **FORBIDDEN** — `observations_only`; `rate_iso_1_pass=false`; `n_unplanted_R_xfer_lt_0.7_with_cert=0`; expected cost unbounded |
| 2 | Executor mutate frozen RC-45? | **NO** — blob `8e1441b49a45…` identical at design + run snapshots |
| 3 | Exact frozen command? | **YES** — `command.txt` byte-exact |
| 4 | `c_smart=8` applied (not leftover 1)? | **YES** — runtime sets const=8.0; report `c_smart=8`, calib value 160 |
| 5 | Null plant / planted path real? | **THEATER** — MOV/direct-solve; `edge_ledger=[]`; null gate skipped |
| 6 | Density null-decay (RT-045-D3)? | **STILL MISSING** |
| 7 | Measure executed / smoke enough? | **ABSENT / NO** |
| 8 | Cheapest falsifications | Planted MOV→1284 fails; measure absent; empty ledger voids plant; amendment hash stable |

## Observed (snapshot)

| Field | Value |
|-------|-------|
| Command | frozen smoke string exact |
| `c_smart` | 8 (`C_special_smart`, calib 160 @ 2^20) |
| `rho_special` | 0.0 at {20,24,28} |
| `rate_iso_1_pass` | false |
| cert-bearing R_xfer&lt;0.7 unplanted | 0 |
| Measure run | absent |
| RC-45 text mutated | no |

## Pareto

- **dominated_by:** Pollard rho exponent 1/2  
- **sota_delta:** `not_applicable` / `non_solver_scope` (toy smoke; no solver claim)

## Flags

`official_research_state_changed: false` · `experiments_performed: true` (smoke) · novelty/sota/support/closure/breakthrough all **false**

## Coordinator next

Adopt PASS_SCOPED + B1–B3 voids in EV-IT-008 / DEC-20260803-004; keep H-IT-001 unchanged; schedule measure + anomalous control + null-decay **or** pause with no transition. Red Team does **not** commit.
