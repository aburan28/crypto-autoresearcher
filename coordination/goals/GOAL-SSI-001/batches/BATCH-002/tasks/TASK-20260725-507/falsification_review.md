# Red-team falsification review — GOAL-SSI-001 BATCH-002

Task `TASK-20260725-507` · Snapshot `cc5b7744b2c1efc87454358138dd4410d158924b`  
Verdict: **CONFIRM**

## Checks against DEC-20260725-002 caps

| Requirement | Result |
| --- | --- |
| \(\mathbb{F}_{p^2}\) vs \(\mathbb{F}_p\) split | Present and used in the disposition |
| Low-memory analogue defined or falsified | Defined (claw-finding DP-PCS); not falsified |
| No breakthrough / completion claim | Held |
| Cap at matched-baseline recommendation | Held |

## Objections

No fatal objections. Nonfatal: Wiener→MITM map is analogy; PCS is modelled
hygiene; DG full-cost \(p^{1/3}\) sketch is optional; review independence
weakened by same-lineage fallback.

## Knowledge

A short `KN-TECH` baseline note is warranted with the hedges above. Not a
`KN-FIND`.

## Next gate

Close the cost-model lane. BATCH-003 should novelty-screen a typed mechanism
against a survivor under these matched baselines.
