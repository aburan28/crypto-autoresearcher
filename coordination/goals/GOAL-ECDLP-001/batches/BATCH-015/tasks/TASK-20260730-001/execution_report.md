# TASK-20260730-001 execution report

## Probe
`experiments/EXP-STR-005/driver/rt35_probe.py` against committed
`harness/endomorphism_la.py`.

## Outcomes
- **RT35-CTRL-1:** `PASS_CTRL4` at B=192 and B=193 on CURVE-J12S1
  (`len(F)==B`, orbit-block identity holds; not a short list).
- **RT35-CTRL-2:** `FAIL_SUPPLY_OR_FB_SHORT` — three arm-cells with
  shortfall ≥ 2:
  - L12 / E_prime_random_fb: shortfall 4
  - L13 / A_prime_phi_invariant_fb: shortfall 2
  - L13 / E_prime_random_fb: shortfall 4
- **Pre-registered falsification:** `stand_down_basis_defective_on_committed_code: true`

## Claim boundary
Toy-tier probe of committed code only. No alpha, ladder, driver, rank, cost,
or H-STR-002 mechanism adjudication. Elapsed ~0.65 s.

## Inference
Executor session: cursor-grok-4.5-high-fast fallback after preferred policies
unavailable; recorded honestly. Not a completion-level claim.
