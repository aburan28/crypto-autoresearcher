# Analysis — Autolab prime-field: round002_exp003_multitarget

## Observation
**Category**: 8 AMORTIZATION — NOT an ECDLP exponent break

Source excerpt / raw summary:

```
# EXP-003: Multi-target Pollard Rho Amortization

**Category**: 8 AMORTIZATION — NOT an ECDLP exponent break
**Date**: 20260530_203022
**Seed**: 42
**Claim label**: OBSERVATION (toy-parameter, ~24-bit prime fields; not a theorem)
**Model**: Generic walk model over prime-field EC groups; no special structure assumed

---

## Hypothesis

**H1**: Shared-DP-table multi-target Pollard rho solves T targets in total
~c*sqrt(T*n) group ops (genuine sqrt(T) amortization), with fitted log-log
slope in [0.45, 0.65] and total ops < T * independent-rho ops for T>=4.

**H0**: Slope >= 0.8 OR multi-target ops consistently >= independent-rho ops.

---

## Curves Used

All three curves are 24-bit prime-order short Weierstrass curves.

- **solinas**: p=8388673 (2^23+2^6+1, Solinas-shaped), a4=8388670 (=-3 mod p), a6=8303516, n=8389351 (prime)
- **random**: p=14434307 (random 24-bit prime), a4=13420883, a6=12752202, n=14433691 (prime)
- **negctrl**: p=11452213 (random 24-bit prime), a4=1636082, a6=566036, n=11456083 (prime)

sqrt(n): solinas~2896, random~3799, negctrl~3385.

---

## Sweep Table

Measurements: mean over 20 draws (T=1,4), 10 draws (T=16), 5 draws (T=64).
theta_bits: DP threshold (point is DP if x mod 2^theta == 0).
Multi ops: total group operations for shared-DP-table multi-target rho.
Indep ops: T * independent single-target rho (T<=4: measured; T>4: 0.886*sqrt(n)*T theoretical).
Solved%: fraction of T targets solved within max_ops budget.
Correct%: fraction of solved targets that pass k*P==Q verification (100% throughout).
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
