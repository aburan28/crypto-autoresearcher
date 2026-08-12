# Repeated-prime modular-derivative obstruction

Date: 2026-07-24

## Claim

Coarse structural data from the classical modular polynomial does not provide a reliable compact selector for later repeated-prime ascending lines in the current nine-fixture suite.

Status: `NEGATIVE RESULT / COARSE MODULAR-DERIVATIVE OBSTRUCTION / MODEL-BOUND / NOT-A-BREAK`

## Model

For every projective `E_r[ell]` line, the audit computes the corresponding degree-`ell` quotient and evaluates coarse local data of `Phi_ell(X,Y)` at `(j(E_r), j(E_r/L))`:

- target `j` base-rationality;
- root multiplicity via `Phi_Y`;
- derivative zero pattern for `Phi_X`, `Phi_Y`, `Phi_XX`, `Phi_XY`, `Phi_YY`, and Hessian determinant;
- square classes of those derivative values.

Raw derivative values are intentionally not treated as a structural selector. They can label individual roots, but without a derived criterion they do not supply the missing divided-orientation/Bockstein operator.

## Evidence

Commands:

```bash
python3 -m py_compile experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit_verify.py
env DOT_SAGE=/private/tmp/sage-codex /usr/local/bin/sage -python experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit.sage.py
python3 -B experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit_verify.py
```

Result:

- Fixture count: `9`
- Later steps tested: `12`
- Later steps distinguished by coarse derivative signatures: `10`
- Later steps with full collision: `2`
- Collision examples: conductor-27 middle steps for `p=577` and `p=619`, where the hidden line has collision class size `4 = ell+1`
- Result scientific SHA-256: `206de3a66bc63074707cd0ebfd3465b7b7df346a25c987a6a558b5550eba5850`
- Verifier scientific SHA-256: `0676cf78e5f8cbec55a8cdfc2922377179922e79f8dcc16428074f45bafabd88`

File hashes:

| File | SHA-256 |
|---|---|
| `experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit.sage.py` | `3f61439bcfc6af246004b4f67f93dc7635ec4cd9f4b6ee7bc3c706c25f0ddeb9` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit_result.json` | `41b6db0a1da7764616403c47a041b032b6daf333d4fe7022af56738f84971bb9` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit_verify.py` | `3da30906e9ead0eae6034bb6198ea1e234b05d98448b47191953c446caf9ab74` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_modular_derivative_audit_verify.json` | `74a37cfd0feeebe3450dbf415e5cd0ae09fc5623c127db948a165472906c9e4a` |

## Interpretation

The audit produces a partial signal, not a selector. Several later steps are uniquely classified by coarse derivative square-class data, but the signal fails on two conductor-27 middle steps and has no consistent rule across the non-special rows. This is not enough to claim a compact divided-orientation evaluator, let alone a general isogeny-complexity improvement or SCALLOP consequence.

Claim gates:

```text
coarse_modular_derivative_signatures_distinguish_all_later_steps = false
compact_evaluator_admitted = false
general_isogeny_complexity_improvement = false
scallop_break = false
ecdlp_consequence = false
```

## Next Action

Do not promote modular-derivative signatures without a formula for the raw derivative values that provably equals the Bockstein digit. The repeated-prime compact-evaluator branch should now be deprioritized in favor of a different isogeny-recovery lead.
