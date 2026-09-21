# EXP-SEMAEV-001 — implementation note

## What was built
- `harness/toycurve.py` — exact F_p elliptic-curve arithmetic, naive point
  counting, deterministic ECDLP instance generation, and the independent
  certificate verifier.
- `harness/rho.py` — Teske r-adding Pollard-rho baseline (public data only).
- `harness/semaev.py` — S_3 summation polynomial and the length-2
  point-decomposition Groebner measurement + decomposition certificate.
- `harness/runner.py` / `harness/run.py` — run wrapper and entry point.

## Command
```
python -m harness.run --experiment EXP-SEMAEV-001
```
producing 12 runs = {bits 8,10,12} x {seeds 1,2} x {rho baseline, gb measurement}.

## Deviations from the approved protocol
None. Bit sizes, seeds, factor-base size (14), and decomposition length (2)
match specification.yaml v1.

## Notes / honesty flags
- `groebner_basis_max_degree_proxy` is the reduced-basis max total degree, an
  implementation-bound proxy, NOT the theoretical degree of regularity
  (KN-TECH-004). sympy uses an unoptimized Buchberger/F5 routine.
- Decomposition depends on whether the target Q happens to be a sum of two
  factor-base points; 3 of 6 gb runs found a decomposition, all certified.
- rho baseline group operations are recorded as matched context, not equated
  to Groebner cost (baseline discipline).
