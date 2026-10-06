# Derivation note — V(β) ≤ 0 for ρ ≥ 1 (HOLD-U)

Experiment: EXP-BINSTD-b7344f / TASK-20261001-8c14b5 / H-BINSTD-32867d.

## Closed form

With IC deterministic at μ_IC = ρ · μ_ρ and rho completion time exponential,
a budget share β to IC gives (μ_ρ normalized to 1):

```
V(β) = 1 - (1/(1-β)) · (1 - exp(-ρ·(1-β)/β))
```

## Non-positivity for ρ ≥ 1

V(β) ≤ 0 for all β ∈ (0,1) whenever ρ ≥ 1 reduces to:

```
(1-β)/β ≥ -ln(β)    i.e.    t - 1 ≥ ln t    at t = 1/β
```

For t > 1, f(t) = t - 1 - ln t has f(1) = 0 and f'(t) = 1 - 1/t ≥ 0, so
f(t) ≥ 0. Equality only at t = 1 (β → 1, degenerate). Thus max_β V(β) ≤ 0
on the Stage-0 grid for every ρ ≥ 1 (numerical check within 1e-9).

## Scope

Modeled / derived only. No ECDLP attack run. No break / exponent / CDCL /
positive-portfolio claim. Stage 1 is a controlled null on the W4 instrument.
