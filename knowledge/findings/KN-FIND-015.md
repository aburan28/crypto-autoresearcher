---
id: KN-FIND-015
type: internal_finding
title: Under pinned MATZOV costing, Kyber dual_hybrid does not beat primal_bdd and
  does not reproduce Carrier/MATZOV-2022 dual headlines; primal_bdd still undercuts
  NIST classical cutoffs
tags:
- dual-attack
- primal-bdd
- matzov
- kyber
- ml-kem
- concrete-security
- cost-model
- contested
- lattice
- kn-open-016
confidence: provisional
internal_refs:
- EV-MLKEM-015
- DEC-20260731-007
- EXP-MLKEM-015
- H-MLKEM-014
- RUN-MLKEM-015-001
proof_status: empirical_only
proof_refs:
- experiments/EXP-MLKEM-015/runs/RUN-MLKEM-015-001/results.json
- experiments/EXP-MLKEM-015/source-lock.yaml
added: 2026-07-31
superseded_by: null
---

## What is established, and at what level

**Empirical / estimate level (not a cryptanalytic certificate).** Using
lattice-estimator commit `3e48ef421ec256afddb3e7d2249a77eab6e9ba12` and
`schemes.Kyber{512,768,1024}` under `RC.MATZOV`:

| set | NIST | primal_bdd | dual_hybrid+fft | best | Carrier claim | MATZOV-2022 claim |
|---|---:|---:|---:|---|---:|---:|
| Kyber512 | 143 | 140.20 | 143.79 | primal_bdd | 139.5 | 137.5 |
| Kyber768 | 207 | 200.96 | 203.79 | primal_bdd | 195.1 | 193.5 |
| Kyber1024 | 272 | 270.72 | 273.82 | primal_bdd | 259.7 | 257.8 |

Official `pq-crystals/security-estimates` Kyber.py classical core-SVP column
(118 / 183 / 256) is reproduced by `primal_usvp` under `RC.ADPS16` within
1 bit.

## Why it matters

1. **Dual does not win under the public MATZOV instrument.** Headline dual
   superiority is not visible in lattice-estimator's `dual_hybrid` once the
   comparison is matched inside `RC.MATZOV`.
2. **Published dual shortfalls are not reproduced.** Carrier's claimed costs
   sit 4.3 / 8.7 / 14.1 bits below this dual instrument; MATZOV-2022 sits
   6.3 / 10.3 / 16.0 bits below. Those gaps are the residual of KN-OPEN-016
   after this finding: they must come from ingredients beyond the public
   MATZOV dual, from a different cost arithmetic, or from overclaim.
3. **Category pressure already appears in the primal.** Under MATZOV gate
   counts, `primal_bdd` alone is 2.8 / 6.0 / 1.3 bits below NIST classical
   cutoffs. Dual-attack drama is not required for that pressure.

## What this does *not* establish

- Not a break of ML-KEM / FIPS 203; no key recovery; no solution certificate.
- Not a validation or falsification of Carrier polar-decoding heuristics
  (KN-LIT-7617); that paper was not fully re-derived here (ePrint PDF was
  network-blocked during the run; abstract claims used as comparison targets).
- Not a statement that NIST categories are operationally broken — only that
  under this named cost model the estimated `log2(rop)` figures land where
  the table says.

## Next measurement that would raise confidence

Independent recomputation of Carrier Table 5.1 / Appendix C from primary text,
or a small-dimension polar-decode experiment that can falsify the repaired
heuristic in the Ducas–Pulles sense (KN-LIT-111).
