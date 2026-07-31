# TASK-20260730-011 — Q(B)-faithful RT35-CTRL-2 re-run

Driver: `experiments/EXP-STR-006/driver/rt35_probe.py`  
Results: `experiments/EXP-STR-006/results/probe_results.json`

## Change from BATCH-015
`num_targets` set to `Q(B)` from EXP-STR-004 (`max(60, B+10)` / table values), not `R_base`.

## Outcomes
- CTRL-1: `PASS_CTRL4` (retained)
- CTRL-2: `PASS_SUPPLY` — zero cells with shortfall ≥ 2; zero FB shorts
- `stand_down_basis_defective_on_committed_code`: **false**

## Claim boundary
Toy. No H-STR-002 mechanism test. No attack improvement. Elapsed ~2.2 s.
