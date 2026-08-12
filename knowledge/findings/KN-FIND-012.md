---
id: KN-FIND-012
type: internal_finding
title: Carrier Fig 4.1 Pwrong simulations do not cover the Pgood≈1/2 threshold; Kyber-scale
  Pwrong is ~84+ bits beyond the toy floor
tags:
- dual-attack
- carrier
- pwrong
- polar-code
- kyber
- ml-kem
- extrapolation
- contested
- kn-open-016
- heuristic-validation
confidence: provisional
internal_refs:
- EV-MLKEM-011
- EXP-MLKEM-011
- H-MLKEM-011
- RUN-MLKEM-011-001
- DEC-20260731-003
proof_status: empirical_only
proof_refs:
- experiments/EXP-MLKEM-011/runs/RUN-MLKEM-011-001/pwrong_scope_gap.json
- experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out
- experiments/EXP-MLKEM-011/vendor-lock/data/Pgood_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out
added: 2026-07-31
superseded_by: null
---

## What is established

On the authors' archived Fig 4.1 left-panel outputs
(`Pwrong_*beta032_beta144_N25971.out`, `Pgood_*` same stem):

| quantity | value |
|---|---|
| last T with Pwrong>0 | 1802 |
| log2(Pwrong) at that floor | ≈ −35.70 |
| Pgood min / median / max (n=4000) | ≈ 6668 / 11964 / 17823 |
| fraction of Pgood with T ≤ 1802 | **0** |
| Kyber-512 CC log2(Pwrong) (Table C.2) | −119.57 |
| bits below toy floor | ≈ 84 |

So the experimental backup of Approximation 4.9 measures Pwrong only on a
T-interval that **does not meet** the Pgood≈½ operating threshold, even before
any jump to Kyber dimensions.

## Why it matters for KN-OPEN-016

KN-FIND-016 showed Table 5.1 arithmetic is consistent. This finding shows the
empirical pillar under that table does not cover the threshold regime that sets
ε = R·q^{k_fft}·Pwrong. That is a heuristic-coverage failure mode in the same
family as KN-LIT-111's objections — not a transcription bug.

## Non-claims

- Does not compute a corrected Kyber security level.
- Does not prove Approx 4.9 false in the bulk; it bounds what Fig 4.1 covers.
- Not a key-recovery break of ML-KEM / FIPS 203.
- Fresh G6K replication was unavailable in this environment.
