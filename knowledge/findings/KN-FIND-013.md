---
id: KN-FIND-013
type: internal_finding
title: Carrier CC NIST shortfalls are erased by ≈10–15 bits of Pwrong underestimation
  under a stated second-term payment heuristic
tags:
- dual-attack
- carrier
- pwrong
- cost-sensitivity
- kyber
- ml-kem
- kn-open-016
- conditional
confidence: provisional
internal_refs:
- EV-MLKEM-012
- EXP-MLKEM-012
- H-MLKEM-012
- RUN-MLKEM-012-001
- DEC-20260731-004
proof_status: derivation
proof_refs:
- experiments/EXP-MLKEM-012/runs/RUN-MLKEM-012-001/cost_sensitivity.json
added: 2026-07-31
superseded_by: null
---

## What is established (conditional)

Under **HEUR-S1** — an underestimation of `log2(Pwrong)` by Δ bits is paid as
`+Δ` in `log2(R·(N·Tdec+TFFT))` inside Theorem 4.1 — the minimal Δ that brings
Carrier CC totals to NIST classical cutoffs is:

| set | baseline CC | NIST | Case A crossover Δ |
|---|---:|---:|---:|
| Kyber-512 | 139.5 | 143 | ≈ 9.5 |
| Kyber-768 | 195.1 | 207 | ≈ 14.4 |
| Kyber-1024 | 259.7 | 272 | ≈ 14.8 |

KN-FIND-012's toy→Kyber-512 Pwrong floor gap is ~84 bits — an order of magnitude
larger than these crossovers as an *upper reference*, not a measured error.

## Non-claims

Conditional sensitivity only. Not a corrected security level. Not an ML-KEM break.
