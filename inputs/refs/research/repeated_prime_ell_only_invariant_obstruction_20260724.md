# Repeated-prime E[ell]-only invariant obstruction

Date: 2026-07-24

## Claim

Visible `E[ell]` operations and Frobenius-on-`E[ell]` signatures do not identify the next ascending line after the first repeated-prime ascent in the current nine-fixture suite.

Status: `NEGATIVE RESULT / ELL-TORSION-ONLY INVARIANT OBSTRUCTION / MODEL-BOUND / NOT-A-BREAK`

## Model

The audit allows:

- construction of a basis of `E_r[ell]`;
- enumeration of the `ell+1` projective lines in `E_r[ell]`;
- Frobenius action on `E_r[ell]`;
- evaluation of the original imaginary Frobenius element `omega_0` on `E_r[ell]`;
- Weil pairings `e_ell(P, omega_0(P))`;
- base-field descent of the degree-`ell` kernel polynomial.

The audit uses the already accepted algebraic-basis recovery result only as a verifier-side label for the correct ascending line. It does not allow that label to enter the tested signatures.

## Theory Boundary

For `r > 0`, the oriented order chain gives

```text
omega_0 = ell^r omega_r in End(E_r).
```

Therefore `omega_0` kills `E_r[ell]`. The visible Frobenius module on `E_r[ell]` is scalar in the ramified repeated-prime case, so every line is Frobenius-stable. The missing object is the first nonzero `ell`-adic digit

```text
N_r = omega_0 / ell^r mod ell,
```

equivalently the Bockstein/divided-orientation operator. The accepted lift-based construction computes this by choosing `Q in E_r[ell^(r+1)]` with `[ell^r]Q=P` and setting `N_r(P)=omega_0(Q)`.

## Evidence

Commands:

```bash
python3 -m py_compile experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit_verify.py
env DOT_SAGE=/private/tmp/sage-codex /usr/local/bin/sage -python experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit.sage.py
python3 -B experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit_verify.py
```

Result:

- Fixture count: `9`
- Later-step torsion indistinguishability count: `12`
- Later-step visible-signature indistinguishability count: `12`
- Each later-step collision count: `4 = ell + 1`
- Result scientific SHA-256: `07d02479c5869f22354a4c9fb9325262932eeea26f018d207cb9ed74b8cc8d57`
- Verifier scientific SHA-256: `99567a39173b36b11d19ce1c7b2bc03b8562dbe4ce3eefc543adab56147753f7`

Coverage:

| Stratum | Fixtures | Later-step result |
|---|---:|---|
| conductor `9`, exponent `2` | `p in {67,73,103}` | all four lines collide |
| conductor `27`, exponent `3` | `p in {577,619,757}` | all four lines collide at both later steps |
| non-special CM conductor `9`, exponent `2` | `p in {163,211,223}` | all four lines collide |

File hashes:

| File | SHA-256 |
|---|---|
| `experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit.sage.py` | `7ec70dab263c19b52ab62873a1ebf0d45a40cc2cd17eb667c4df3c88da659d25` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit_result.json` | `c24144451e4e90bf1796c6088e9857c9bb8c7bfd116b2066e60a2a7678ed7efe` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit_verify.py` | `6827aa23462723b100583232c9a3604f8ec59dca471a1440b1ed935b4afd1d57` |
| `experiments/ecdlp_isogeny/iso_repeated_prime_ell_only_invariant_audit_verify.json` | `70111ae09d6e454195acab4601bc0d946c4842387279f56cfa77dfeaa9f00bf7` |

## Interpretation

This rules out the simplest compact-evaluator escape: a selector based only on the reduced `ell`-torsion module, visible Frobenius, and base-descent signatures. The repeated-prime branch still has possible escapes, but they must obtain the Bockstein digit from a source outside bare `E[ell]`, such as a genuinely compact higher-division evaluator, a modular-polynomial derivative invariant, or protocol-side leakage.

Claim gates:

```text
compact_evaluator_admitted = false
general_isogeny_complexity_improvement = false
scallop_break = false
ecdlp_consequence = false
```

## Next Action

Test whether modular-polynomial local data at `(j(E_r), j(E_{r+1}))`, such as derivative or root-multiplicity signatures, provides the Bockstein digit without `E[ell^(r+1)]` torsion. If it also collides, record it as the next obstruction and pivot away from repeated-prime compact evaluation.
