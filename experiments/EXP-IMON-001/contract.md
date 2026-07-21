# Experiment Contract EXP-IMON-001

```yaml
handoff:
  id: TASK-20260718-003
  from: coordinator
  to: executor
  objective: >
    Compute exact factorization cycle-type censuses of decomposition covers on
    toy ordinary curves and test the full-monodromy (wreath) hypothesis.
    Two-sided by design: discovery of a non-full group with an exploitable
    block system promotes candidate C2 (resolvent decomposition attack);
    established fullness promotes barrier candidate D2 and closes C2.
  inputs:
    - research_directions_20260718.md (candidates C2, D2; shares A1 census)
    - experiments/EXP-IMON-001/imon_group.py (harness, executed at p=101)
  constraints:
    - generated toy ordinary prime-order curves only; no production targets
    - >=20 random curves per size; excluded families logged, never silently dropped
    - optimized factorization required before p > 431 (smoke took 162 s at p=101)
  deliverables:
    - harness results JSON (DONE: experiments/EXP-IMON-001/smoke_results.json)
    - m=2 census at p in {101, 211, 431, 809, 1601, 4099} with per-curve histograms
    - phase-2 m=3 Semaev cover census (joint with EXP-MONO-001 phase 2)
    - primitivity/block-system test on any deviant cover
    - ledger entry proposal
  budget:
    wall_clock_seconds: 21600
    memory_gb: 4
    maximum_runs: 80
  completion_gate:
    - C2 promotion: non-full group on a non-excluded ordinary family at >=3
      sizes with Chebotarev-consistent densities AND a measured resolvent
      advantage growing with m
    - D2 establishment: full-group agreement within Weil error at >=3 sizes,
      >=2 m values, >=20 curves per size, zero unexplained exceptions
    - mixed outcome: archive exact deviant list as scoped record
```

## Validity criteria
- Product-cover control (g₂·g₃) must be flagged non-full (DONE: flagged; only block-respecting types observed).
- Random deg-5 control must match Chebotarev S₅ rates (DONE: 5-cycles 0.2034 vs 0.2; 4+1 0.2494 vs 0.25).
- The coded joint-split census at m=2 is deterministic given the marginal split rate; this is a recorded harness limitation — the nontrivial joint test requires the m=3 cover (phase 2).
- Any curve-level deviation beyond 3x Weil error must be re-verified with an independent factorization routine before being recorded as an exception (lab rule 9).

## First executable command
```
python3 experiments/EXP-IMON-001/imon_group.py --p 101 --seed 20260718 --samples 20000
```

## Reproduction artifacts
- implementation: `experiments/EXP-IMON-001/imon_group.py`
- results: `experiments/EXP-IMON-001/smoke_results.json`
- audit script (to write): `experiments/EXP-IMON-001/audit_imon.py`
- proposed ledger IDs: ECFG-RT-1521 (C2 census) / ECFG-RT-1524 (D2 barrier record)
