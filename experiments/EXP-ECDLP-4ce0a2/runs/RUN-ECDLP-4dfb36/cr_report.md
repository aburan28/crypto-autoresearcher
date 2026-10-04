# EXP-ECDLP-4ce0a2 — cross-ratio family (level, anchor-constancy) profile

Run RUN-ECDLP-4dfb36, specification v1 (approved DEC-20260921-b22088),
canonical probability normalisation, the census's primary ladder.

| row | lambda | SE | n |
|---|---|---|---|
| CR | 0.4998 | 0.0002 | 10 |
| CR2 | 0.4998 | 0.0002 | 10 |
| CR3 | 0.4997 | 0.0002 | 10 |
| CR4 | 0.4997 | 0.0002 | 10 |
| CR5 | 0.4998 | 0.0002 | 10 |
| CRM | 0.4997 | 0.0002 | 10 |
| R08 | 0.5000 | 0.0000 | 10 |
| C01 | 0.5159 | 0.0054 | 10 |
| C02A | 0.4982 | 0.0006 | 10 |
| C02B | 0.5014 | 0.0006 | 10 |

delta vs C02A: 0.0016; delta vs R08: -0.0002; anchor spread: 0.0001 (within 2SE: True)

## Controls

| control | result |
|---|---|
| C01_numerically_zero | PASS |
| C02A_parseval_band | PASS |
| C02_seed_agreement | PASS |
| R08_boundary_reproduction | PASS |
| vhat0_equals_1_all_ok_cells | PASS |

CRM equivalence at the smallest prime: CRM is a further family member (its induced anchor triple is outside the frozen sweep); recorded, equivalence check not applicable at this sweep (matches: [])

## Verdict

**stable_flat**

The Gauss-flat finding extends through the invariant
coordinate: the cross-ratio family is anchor-constant AT the
random/boundary level. The cross-ratio lane is scoped out for
set statistics; the Kloosterman-cancellation reading is
recorded as the obstruction; the synthetic lane narrows to
the non-set escape hatch (IDEA-20260921-4af08b) and the
partition row class (IDEA-20260921-b03306).

Per-cell values, anchors, wall times, RSS: cr_registry.json.

