# Analysis — Autolab prime-field: round009_exp017_abelian_surface

## Observation
failed

Source excerpt / raw summary:

```
# EXP-017 — Weil-restricted ABELIAN SURFACE summation polynomial (H14)

**Round** 9  **Role** Experiment-Engineer  **Timestamp** 2026-05-31
All numbers below are read back from `round009_exp017_abelian_surface_result.json`
produced by the final clean run (rc=0). No value in this file is hand-entered.

**Artifacts**
- `round009_exp017_abelian_surface.sage` (self-contained, parses+runs under Sage 10.9)
- `round009_exp017_abelian_surface.log`
- `round009_exp017_abelian_surface_result.json`
- `round009_exp017_abelian_surface_result.md` (this file)
- loaded gate: `round007_exp012_localization_gate.sage` -> `meter_gated`, `meter_local`, `build_*`

## VERDICT: `failed` — H14 CLOSED as a bankable NEGATIVE

`RESTRICTED THEOREM (empirical, toy p<=509, m in {2,3})` / `NEGATIVE RESULT`:
For the SCALAR Weil restriction A = Res_{F_{p^2}/F_p}(E) realized by splitting the
Semaev relation over the F_p-basis {1, w}, the A-summation polynomial has the SAME
per-variable degree as the elliptic-curve Semaev relation for the same number of
variables (S_2: 1=1, S_3: 2=2). The Weil split is an F_p-LINEAR isomorphism on the
coefficient space; it re-packs total degree across the doubled coordinates but cannot
lower the per-variable degree of the underlying F_q relation. **Semaev per-variable
degree is a restriction invariant** (the algebraic shadow of "Semaev degree is an
isogeny invariant", since the norm/Verschiebung structure relating A and E is an
isogeny). No D_reg advantage exists, so the H14 "slower-than-4^(m-1) surface summation
degree" conjecture is FALSE for the scalar-restriction realization.

A gate-meaningful early fall DID occur at m=3 (d_ff=5 < D_reg=11) — but it is the KNOWN
POS-C Weil-S_3 phenomenon reproduced on the 6-variable surface system, NOT a new
prime-field positive: with EQUAL degree it confers no D_reg advantage.

## 1. Meter self-validation (MANDATORY — inline) — PASS

| control | meter | d_ff | D_reg | fires | gate_passes | gate_meaningful | expected | ok |
|---|---|---|---|---|---|---|---|---|
| POS-A (3 cubics, shared quad, seed 101) | meter_local | 4 | 7 | True | n/a | n/a | fire d_ff=4<7 | YES |
| NEG-1 (generic quadrics, seed 11) | meter_local | None | 4 | False | n/a | n/a | quiet | YES |
| NEG-2 (generic cubics, seed 22) | meter_local | None | 7 | False | n/a | n/a | quiet | YES |
| e-ring m=3 Semaev | meter_gated | 3 | 7 | True | False | **False** | FAIL gate (artifact) | YES |
| POS-C Weil S_3 / F_{p^2} | meter_gated | 4 | 9 | True | True | **True** | PASS gate | YES |
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
