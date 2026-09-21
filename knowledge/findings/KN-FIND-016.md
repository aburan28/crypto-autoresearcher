---
id: KN-FIND-016
type: internal_finding
title: Carrier Table 5.1 CC dual costs are Theorem-4.1-consistent; Table C.2 CN/Kyber-512
  log2(Tsample)=143.30 is a transcription error for ≈134.30
tags:
- dual-attack
- carrier
- matzov
- kyber
- ml-kem
- concrete-security
- table-erratum
- cost-model
- kn-open-016
confidence: provisional
internal_refs:
- EV-MLKEM-016
- EXP-MLKEM-010
- H-MLKEM-010
- RUN-MLKEM-010-001
- DEC-20260731-008
proof_status: empirical_only
proof_refs:
- experiments/EXP-MLKEM-010/runs/RUN-MLKEM-010-001/results.json
- experiments/EXP-MLKEM-010/vendor-lock/optimized_withExperimentalPolar.pkl
- experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf
added: 2026-07-31
superseded_by: null
---

## What is established

Against HAL `hal-05406481` (Carrier et al., ePrint 2022/1750) and commit
`9c1367f` of `kevin-carrier/CodedDualAttack`:

1. **Table 5.1 stands.** All nine Algorithm-3.1 cells match
   `optimized_withExperimentalPolar.pkl` within 0.05 bits. Theorem 4.1
   `T = Tsample + R·(N·Tdec + TFFT)` recomputed from pickle intermediates
   matches the pickle totals.
2. **Abstract CC shortfalls are the CC column.** NIST − {139.5, 195.1, 259.7}
   = {3.5, 11.9, 12.3}. Those numbers are arithmetically supported given the
   authors' intermediates.
3. **Table C.2 typo.** Printed `log2(Tsample)=143.30` for CN/Kyber-512 should
   be ≈`134.30` (pickle: 134.295). The paper-only Thm-4.1 check that produced
   an 8.8-bit anomaly is resolved by this correction; Table 5.1's CN claim
   134.5 is the consistent figure.

## What remains open (KN-OPEN-016)

Whether the intermediates themselves are justified — polar decoding distortion,
`Pwrong` / `Pgood`, short-vector sampling under GSA/GH, and the named C0/CC/CN
cost models — is untouched. EV-MLKEM-015 still shows the public
lattice-estimator MATZOV dual does not beat primal_bdd and does not match these
CC dual headlines.

## Non-claims

Not a break of ML-KEM. Not a validation of polar heuristics. Not a NIST
operational finding.
