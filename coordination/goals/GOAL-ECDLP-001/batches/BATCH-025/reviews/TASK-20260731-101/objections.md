# RT-20260731-101 — Objections (structure-null-r2)

**Snapshot:** `a5aaf5d3` (TASK-099)  
**Control:** CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2 @ `0d13ad5a`  
**Approval:** `b27db960` / DEC-027  
**Prior:** EV-DS-007 / RT079-B3  

## Verdict

Honest `structure_direction_fail` with primary `R_null≈0.016≪0.9` is **protocol success for honesty**, not structure credit. No S1_met / support / asymptotic / lane death.

## Blocking (RT101-B1–B6)

| ID | Title |
|----|--------|
| RT101-B1 | Forbid stronger-than-toy readings (keeps RT079-B1) |
| RT101-B2 | Honest fail ≠ structure credit; RT079-B3 tell confirmed |
| RT101-B3 | Unreplicated empirical_only forbids reject_scoped / lane death |
| RT101-B4 | Do not cherry-pick advantageous ladder cells without R_null |
| RT101-B5 | No theater / EXP-IT launder |
| RT101-B6 | RT047 / proxy / CI / Pareto residuals still bind |

## Major / info

- **RT101-M1:** Primary has `advantageous_R=false`; fail still correct via gate/ladder predicates.
- **RT101-M2:** Dirty-tree / assume-unchanged driver / wall-timing caveats.
- **RT101-M3:** Manifest `discrete_log` certificate is not crypto/S1 credit.
- **RT101-I1/I2:** Package hygiene OK; inference fallback recorded.

## TASK-102 recommendation

- **DISPOSITION:** `inconclusive` (preferred) or `weaken-scoped` only on structure-claim eligibility  
- **H-DS-001:** keep `analyzed`  
- **Gates:** OPEN  
- **knowledge_promotion:** `not_warranted`  
- **Evidence / DEC:** EV-DS-008 + free DEC (prefer DEC-029 if DEC-028 reserved by RC-25b)
