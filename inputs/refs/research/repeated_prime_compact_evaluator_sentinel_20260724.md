# Repeated-prime compact-evaluator sentinel

Date: 2026-07-24

## Claim

The accepted repeated-prime algebraic-basis ascent path is not an admitted compact evaluator. Under a runtime sentinel forbidding high-torsion acquisition and withheld-path custody helpers, the path is blocked before it can return.

Status: `NEGATIVE CONTROL / SENTINEL-GATED / ACCEPTED PATH USES BANNED HIGH-TORSION ACQUISITION / NOT-A-BREAK`

## Scope

This is a repository-state and fixture-level admission gate for the repeated-prime divided-orientation branch. It does not establish a general isogeny-complexity improvement, a SCALLOP attack, or an ECDLP consequence.

Fixture:

- Field: `F_577`
- Curve: `y^2 = x^3 + 2x + 1`
- Trace: `-11`
- Frobenius discriminant: `-2187`
- Source conductor: `27`
- Repeated prime: `ell = 3`, exponent `3`

## Sentinel Rule

The candidate is rejected if it calls any of:

- `find_algebraic_basis_guided_orientation_lift`
- `find_basis_guided_orientation_lift`
- `find_single_compatible_orientation_lift`
- `full_torsion_points`
- `full_torsion_points_with_stats`
- `build_withheld_ascending_path`
- `build_withheld_path_via_class_polynomial`

The first implementation attempt patched the `runpy` result dictionary, not the constructor's function globals, and therefore failed to intercept helper resolution. That failed harness output is preserved as:

- `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_v1_monkeypatch_scope_failure.json`

The repaired harness patches `construct_algebraic_basis_repeated_prime_ascending_path.__globals__`.

## Evidence

Commands:

```bash
python3 -m py_compile experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_verify.py
env DOT_SAGE=/private/tmp/sage-codex /usr/local/bin/sage -python experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel.sage.py
python3 -B experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_verify.py
```

Result:

- Sentinel status: `PASS`
- Verifier status: `PASS`
- Blocked call: `find_algebraic_basis_guided_orientation_lift`
- Exception: `SentinelViolation: sentinel blocked find_algebraic_basis_guided_orientation_lift`
- Result scientific SHA-256: `618de5655737ff24ea828c9fab7acbc71266c6b55f222bc2a8a960c5032321c1`
- Verifier scientific SHA-256: `1c5fc2dadd560b2f3344233c9f16ce3620dd37fceca75aae4ac83232ec4fde64`

File hashes:

| File | SHA-256 |
|---|---|
| `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel.sage.py` | `7f6efa1bb9b35ac7d2b4b6c348d1ba8f58cc0edab2874e96eb33a11c472a4b4a` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_result.json` | `d5b981dce2bf5a77aaa8a4c9e655d70db85de42378eb8c3122fa54ada3a9f1ab` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_verify.py` | `2d30692b5136ef5b56b2391a2f2c9adfe9470bff743914b55f20d4a16887eb02` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_verify.json` | `7cb4c3daec9795215152320212478f2f19e62e62c3a59ca683f6c860f56c0b9c` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_sentinel_v1_monkeypatch_scope_failure.json` | `84ad748c40e2d60f0cd8fff11909c6ccee79c9402eabf77101ee04a70f14f328` |

## Interpretation

The existing accepted path is useful as a control, but it cannot support a compact-evaluator or complexity-improvement claim. A valid breakthrough candidate on this branch must recover the fixture while the sentinel remains active.

## Next Action

Implement candidate repeated-prime divided-orientation evaluators as separate functions and require them to pass this sentinel before any cost or cryptographic claim is considered.
