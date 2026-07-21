# Experiment Contract EXP-XEDN-001

```yaml
handoff:
  id: TASK-20260718-002
  from: coordinator
  to: executor
  objective: >
    Measure the lift probability P_lift of the function-field xedni
    representation (elliptic-surface Mordell-Weil sections over F_p(t)) at toy
    scale, and fit its trend against the classical xedni-collapse prediction
    (Jacobson-Koblitz-Silverman-Stein-Teske, DCC 20:41-64, 2000).
    Correctness of section arithmetic is necessary but NOT the gate; the gate
    is the P_lift trend.
  inputs:
    - research_directions_20260718.md (candidate B2)
    - experiments/EXP-XEDN-001/xedni_sections.py (harness, executed at p=101)
  constraints:
    - generated toy surfaces only; no production targets
    - iso-trivial surfaces must be detected and excluded from census counts
    - planted and random surfaces clearly separated; fixed seeds
  deliverables:
    - harness results JSON (DONE: experiments/EXP-XEDN-001/smoke_results.json)
    - section census at p in {101, 211, 431, 809} with deg-2 monic sections
    - fitted exponent alpha in P_lift ~ p^-alpha with 95% CI
    - ledger entry proposal (outcome-dependent ID)
  budget:
    wall_clock_seconds: 14400
    memory_gb: 2
    maximum_runs: 40
  completion_gate:
    - promotion: alpha < 1/2 with 95% CI excluding the classical prediction
      fitted at the same sizes, across >=3 toy sizes
    - closure: alpha >= 1/2 or CI includes the classical prediction =>
      scoped negative ECFG-NR-1518 with the fitted values archived
```

## Validity criteria
- Planted-section control must recover the planted section (DONE at p=101: recovered, unique).
- Negative control (random sextics): square-hit rate must not exceed 10x the naive p^-3 prediction (DONE: 0 hits in 200 000).
- Square detection is verified by re-squaring: zero false positives by construction; false negatives for non-squarefree sextics are logged as a harness limitation.
- Toy evidence is not crypto-scale validation (lab rule 7); only the *trend* promotes.

## Phase-2 requirements
- >=3 toy sizes, exhaustive section enumeration on >=200 random surfaces per size (or exact counted sampling with recorded coverage), >=1000 planted surfaces total across sizes for the recovery-rate baseline.
- The census must record b(t) degree, section degree, and per-surface section counts in machine-readable form.

## First executable command
```
python3 experiments/EXP-XEDN-001/xedni_sections.py --p 101 --seed 20260718 --samples 200000
```

## Reproduction artifacts
- implementation: `experiments/EXP-XEDN-001/xedni_sections.py`
- results: `experiments/EXP-XEDN-001/smoke_results.json`
- audit script (to write): `experiments/EXP-XEDN-001/audit_xedn.py`
- proposed ledger ID: ECFG-P1518 (promotion) / ECFG-NR-1518 (closure)
