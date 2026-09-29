# Implementation — EXP-ECDLP-a5f766 v2 (TASK-20260906-b7628e)

Single approved run `RUN-ECDLP-a5f766-001` of the frozen contract
`experiments/EXP-ECDLP-a5f766/approved-contract-v2.yaml`
(sha256 `a81b1476954d80d8042d697299f2522a6658431b17380f3ef423cb5403c6c79d`).

## Modules

- `source/direct_dual_numbers.py` — implementation D. Direct dual-number
  arithmetic over `F_p[eps]/eps^2`: a `Dual` pair `(a, b) = a + b*eps` with
  add/mul/scalar/integer-power/inverse (inverse defined only when `a != 0`,
  `(1/a, -b/a^2)`), plus the active gauge action computed by multiplying with
  the dual unit `u = u0*(1 + v*eps)` (`x' = u^2 x`, `y' = u^3 y`, `A' = u^4 A`,
  `B' = u^6 B`) and the pullback `eps -> c*eps` (scale every first component).
  `F = x^2 * A^{-1}` is evaluated purely with these pair operations; no
  closed-form jet formula appears in this module.
- `source/coefficient_reference.py` — implementation R. Independent
  coefficient-formula implementation: `F0 = x0^2/A0`,
  `J = 2*x0*x1/A0 - x0^2*A1/A0^2`, the gauge transform written as explicit
  coefficient formulas (`x0' = u0^2 x0`, `x1' = u0^2 (x1 + 2 v x0)`,
  `A0' = u0^4 A0`, `A1' = u0^4 (A1 + 4 v A0)`, etc.) and the pullback as
  multiplication of first-order coefficients by `c`. It does not import or
  call implementation D and vice versa (contract control
  `independent_coefficient_arithmetic`; sharing would trigger the contract's
  invalidation rule).
- `source/symbolic_audit.py` — symbolic certificate driver and stage
  orchestrator. Imports D and R (a driver importing both is not a shared
  implementation of the checked expression). Runs the four budgeted stages,
  enforces stage/total wall ceilings and every contract stop rule, and writes
  all run artifacts. Symbolic groups 1–5 run over `QQ` with sympy exact
  rational functions; identities are checked by expanding numerators after
  clearing denominators (residual must be the zero polynomial). No floating
  point enters any certificate.

## Control-to-module map

| Contract control | Where enforced |
| --- | --- |
| constant_family | Stage 3: all 32 C rows, expected `J = 0` after every action |
| pure_model_gauge | Stage 3: G built by D's dual `u = 1+eps` action on C; raw `x1 = 6` recorded before further actions; `J = 0` on all 32 G rows |
| varying_flex_known_false_control | Stage 1 (special-fiber order-3 via explicit point arithmetic), stage 2 group 5 (on-curve, tangency residual `(x-3)^3`, discriminant `3375 + 5400*eps`), stage 3 (`J = -6` pre-pullback, `-6*c` final on all 32 V rows). The blanket zero-derivative rule is the known-false object; its rejection is recorded as an expected positive control |
| parameter_convention | Stage 2 group 3 (`J(c*x1, c*A1) - c*J == 0`, `F0` unchanged) and stage 3 covariance check; active convention only |
| independent_coefficient_arithmetic | Stage 3: D vs R agreement on `F0` and `J` for all 96 rows |
| order_zero_and_collision | Stage 3: `F0 = x0^2/A0` recomputed both ways; C/G jet equality with differing raw coordinate motion; `P` vs `-P` same-x/same-F collisions recorded, no injectivity claim |
| ordinary_eligibility | Stage 1: exhaustive point counts per prime, `t = p+1-#E`, eligibility `p ∤ t`, independent Hasse coefficient of `x^(p-1)` in `(x^3+3x-11)^((p-1)/2)`; agreement required; no prime replacement |
| invalid_input_rejections | Stage 1: four independent predicate tests (p=3; A0=0; n=p; singular A0=-3,B0=2), rejected before any jet interpretation |

## Stages and ceilings (contract-frozen, no borrowing)

1. `preconditions_and_eligibility` — 120 s
2. `symbolic_certificates_and_scoped_lemma` — 600 s
3. `finite_controls` — 240 s
4. `immutable_artifact_production` — 240 s

Total 1200 s, 2 GiB nominal (measured via `ru_maxrss`; macOS `RLIMIT_AS`
unavailable, recorded as nominal-only), exactly one run, one worker,
deterministic (no randomness, no seeds).

## Stop-rule handling

Any invalid primary precondition, eligibility-method disagreement, arithmetic
inconsistency, unexpected nonzero null, failed expected identity, exhausted
stage/total/memory ceiling, or lost provenance raises a typed stop; the driver
preserves all prior rows and partial artifacts and writes a partial terminal
receipt. A stop is classified per `agents/executor.md` and is never
interpreted as mathematical evidence.
