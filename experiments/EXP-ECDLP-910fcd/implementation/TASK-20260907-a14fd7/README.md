# EXP-ECDLP-910fcd executable backend

This package writes the prospective backend for the frozen Tate-character calibration. It creates no fixture, pairing, control, timing, or run artifact by default. Its final corrected runner is static-parse-only because this task's allowed 20 synthetic cases were already consumed before the correction:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 driver.py --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 tests.py
```

`driver.py` loads the byte-bound predecessor only for its polynomial-basis arithmetic, short-Weierstrass law, binary shifted-divisor Miller loop, SHA-256 streams, and bounded BSGS primitives. This task adds an actual Rabin/Frobenius witness computation, deterministic extension-field square roots and point candidates, retained bounded T/shift search, a public-only evaluator child process, executed controls, cost charging, authenticated launch verification, typed failure preservation, and atomic canonical run-package writing.

The prospective `--launch-lock` path requires all of `--coordinator-public-key`, `--execution-plan`, and an allocated `--run-id`. The lock binds this source hash, the plan hash, frozen specification hash, exact 8 GiB/one-worker/one-run resource limits, runtime record, and a detached signature verified by `openssl pkeyutl` against a separately supplied Coordinator public key. No such key or lock is in this package. Missing one fails closed and does not launch.

The runner maps frozen obligations as follows:

| Frozen obligation | Executable code |
| --- | --- |
| Increasing-I polynomial search and certificate | `select_certified_modulus`, `rabin_irreducibility_certificate` |
| Polynomial field, roots, extension points | `PolynomialField`, `extension_sqrt`, `extension_point_candidates` |
| Bounded T and shifted divisor | `public_t_candidates`, `bounded_t_search`, `evaluate_shifted_tate` |
| Final exponent and decoders | `evaluate_shifted_tate`, bounded BSGS wrappers |
| Withheld scalar boundary | `PublicEvaluatorInput`, `invoke_public_evaluator`, `_evaluate_public_payload` |
| Exact, injection, isotropy, coordinate, decoder controls | control functions in `driver.py` |
| Full cost and artifact pipeline | `_future_cell`, `ChargingLedger`, `execute_authorized_run`, `write_run_package`; canonical `command.txt`, `environment.json`, `raw-result.json`, and required experiment artifacts |

The independent implementation review must examine both this package and the explicitly hash-bound predecessor before any signed measurement lock. `_future_cell` implements the frozen seven alternating timing blocks and repeat-to-resolution policy; an implementation package, synthetic checks, or a successful signature verification is not a scientific result.
