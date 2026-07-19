# harness — executable spine

Minimal, correct ECDLP experiment substrate. Everything here is toy-scale,
deterministic, and independently verifiable.

| module | role |
|---|---|
| `toycurve.py` | F_p short-Weierstrass arithmetic, exact point counting, deterministic ECDLP instance generation. Also the **independent verifier** for certificates. |
| `rho.py` | Pollard rho (Teske r-adding walk) — the matched generic baseline (KN-TECH-001). Recovers k using public data only. |
| `semaev.py` | Semaev summation polynomials S_2/S_3/S_4 and the S_3 point-decomposition Groebner measurement (KN-TECH-002/003/004). |
| `runner.py` | Run wrapper: captures commit/env/timing/resources, re-verifies every certificate independently, and writes the immutable run record. Refuses to overwrite a run id. |
| `run.py` | Experiment entry point (EXP-SEMAEV-001). `python -m harness.run --experiment EXP-SEMAEV-001`. |

Run tests with `python -m pytest -q`. Metrics honesty: the Groebner
`*_max_degree_proxy` is the reduced-basis max degree, an implementation-bound
proxy, **not** the theoretical degree of regularity (see KN-TECH-004). Only
trends versus parameters are interpreted; absolute timings are not crypto-scale.
