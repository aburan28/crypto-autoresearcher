# EXP-ECTD-9e4248 driver -- MANIFEST

See `../implementation.md` for the full derivation, dead ends, and disclosed
scoping decisions. This file is a short module map.

Pure Python 3 standard library only (no SageMath, no external CAS at runtime),
matching EXP-ECTD-001's environment constraint.

## Module map

| file | purpose |
|---|---|
| `reused/*.py` | byte-identical copies of 12 EXP-ECTD-001 driver files (verified via diff/sha256) |
| `run_common.py` | byte-identical copy of EXP-ECTD-001's run_common.py, relocated (its REPO_ROOT logic is path-relative) |
| `fp_sampler.py` | D3 fix: genuine per-seed varying bit-length prime sampling |
| `cm.py` | Hilbert-class-polynomial-route (class-number-1 special case) vertical-edge (crater) construction, class number enumerator, known-j validation, small-prime feasibility filtering |
| `divpoly_ext.py` | general division polynomials for ell up to 31 (reused/divpoly.py only covers 2..7) |
| `vertical_isogeny.py` | vertical (conductor-q) Velu kernel-finding, built on reused/isogeny.py's fully-general find_all_roots/velu_codomain/verify_order_preserved |
| `vertical.py` | per-edge orchestration: floor/crater construction, CTRL-END-RING-CERTIFICATE, CTRL-HORIZONTAL-BASELINE, CTRL-COORDINATE-NULL, CTRL-GLV-CHANNEL |
| `ks.py` | two-sample KS statistic + asymptotic critical value (primary decision statistic) |
| `decision.py` | the frozen 5-branch decision table |
| `orchestrate.py` | shared pipeline: seed-policy retries, permutation stability, decision assembly |
| `run_impl.py` | RUN-ECTD-9e4248-impl entry point (1-edge smoke) |
| `run_screen.py` | RUN-ECTD-9e4248-screen entry point (>=8-edge screen) |
| `selftest_cm.py` | independent validation of cm.py before any real run |
| `selftest_divpoly_ext.py` | independent validation of divpoly_ext.py before any real run |

## Self-tests (run before any real run)

```
cd experiments/EXP-ECTD-9e4248
python3 -m driver.selftest_cm
python3 -m driver.selftest_divpoly_ext
```

Both passed (all assertions) before RUN-ECTD-9e4248-impl was executed.
