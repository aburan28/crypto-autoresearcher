---
id: KN-FIND-014
type: internal_finding
title: Carrier verifyModel Pwrong scores are FFT/k_fft while Pgood scores are raw
  cosine sums; scale-aligned Fig 4.1 coverage gap remains (fraction_inside=0)
tags:
- dual-attack
- carrier
- pwrong
- score-scale
- verifyModel
- kyber
- kn-open-016
- erratum
confidence: provisional
internal_refs:
- EV-MLKEM-013
- EXP-MLKEM-013
- H-MLKEM-013
- EV-MLKEM-011
- RUN-MLKEM-013-001
- DEC-20260731-005
proof_status: empirical_only
proof_refs:
- experiments/EXP-MLKEM-013/runs/RUN-MLKEM-013-001/results.json
- experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py
added: 2026-07-31
superseded_by: null
---

## What is established

In `kevin-carrier/CodedDualAttack` @ `9c1367f`:

- **Pwrong path:** `numpy.fft.fftn(T).real / k_fft`
- **Pgood path:** `sum cos(·)` with **no** `/k_fft`
- Synthetic identity: raw cosine sum = `fftn.real`; factor is exactly `k_fft`

On the Fig 4.1 left-panel archives, after dividing Pgood by `k_fft=3`:

| quantity | value |
|---|---|
| Pgood min/median (aligned) | ≈ 2223 / 3988 |
| Pwrong last-positive T | 1802 |
| fraction inside | **0** |
| T-gap (aligned) | ≈ 421 |

So H-MLKEM-011 / KN-FIND-012’s qualitative claim survives; the raw T-gap was
overstated by factor 3.

## Non-claims

Not a Kyber break. Does not change Table 5.1 arithmetic (KN-FIND-016).
