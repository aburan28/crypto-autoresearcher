# Experiment Contract EXP-MONO-001

```yaml
handoff:
  id: TASK-20260718-001
  from: coordinator
  to: executor
  objective: >
    Determine whether Frobenius cycle-type (Chebotarev) census of the toy
    decomposition cover predicts relation-relevant rates a priori, and whether
    any non-excluded ordinary toy curve deviates from full-monodromy
    (quasirandom) predictions beyond the Weil floor.
  inputs:
    - research_directions_20260718.md (candidate A1; two-sided with C2/D2)
    - experiments/EXP-MONO-001/mono_census.py (phase 1, executed)
  constraints:
    - generated toy ordinary curves only; prime-order group (cofactor 1); no production targets
    - exclude anomalous, supersingular, j=0/1728 from random controls (analyze separately if sampled)
    - fixed seeds; all results machine-readable; no fabrication of runs or rates
  deliverables:
    - phase-1 results JSON (DONE: experiments/EXP-MONO-001/smoke_results.json)
    - phase-2 m=3 Semaev S3 factorization census across >=3 toy sizes
    - audit script recomputing every rate from stored raw counts
    - ledger entry proposal
  budget:
    wall_clock_seconds: 7200
    memory_gb: 2
    maximum_runs: 60
  completion_gate:
    - phase-2 gate: measured m=3 split-rate deviation from the full-monodromy
      Chebotarev prediction exceeds 3x Weil floor on a non-excluded family at
      >=3 sizes, OR exceptional families appear at rate >=1/20; else archive as
      calibration record + two-sided barrier evidence for ECFG-RT-1524
```

## Validity criteria
- Positive control (planted factor-base window relation) must fire at rate 1.0.
- Uniform negative control must match W/p within 0.02; shuffled negative within 0.03.
- A run failing controls is `failed_infrastructure` or `invalid`, never evidence (lab rule 5).
- Timeout/crash is not evidence against the hypothesis (lab rule 5).

## Phases
1. Phase 1 (DONE 2026-07-18): m=2 harness validation, p ∈ {101, 211, 431}, seed 20260718. Controls passed. Result: rates match exact toy predictions within ±0.0012; naive independence prediction documented as an artifact, not signal.
2. Phase 2 (the substantive gate): Semaev S₃(x₁,x₂,T) census, p ∈ {211, 431, 809, 1601}, ≥20 random ordinary prime-order curves per size, ≥3 sizes, both cycle-type histograms and joint rates. Budget note: IMON-001 smoke needed 162 s at p=101 with brute-force scans; phase 2 requires factoring cubics (root scan + discriminant) — estimated feasible within budget only with the optimized factor routine.

## First executable command
```
python3 experiments/EXP-MONO-001/mono_census.py --primes 101 211 431 --seed 20260718 --samples 30000 --window 4
```

## Reproduction artifacts
- implementation: `experiments/EXP-MONO-001/mono_census.py`
- results: `experiments/EXP-MONO-001/smoke_results.json`
- audit script (to write): `experiments/EXP-MONO-001/audit_mono.py`
- proposed ledger ID: ECFG-RT-1514
