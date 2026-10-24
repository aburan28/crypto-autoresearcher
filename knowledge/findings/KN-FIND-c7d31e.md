---
id: KN-FIND-c7d31e
type: internal_finding
title: BKK Speedup Theorem — Semaev sparse check provably achieves (m+1)/2 speedup
tags: [bkk, semaev, speedup-theorem, combinatorics, index-calculus, proved]
confidence: proved
evidence_level: theorem
source_refs: [BATCH-119, KN-FIND-2a8b7e]
internal_refs: [DEC-20260804-1825ea]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-c7d31e.md]
added: '2026-08-04'
superseded_by: null
---

## Theorem

**BKK Speedup Theorem**: For a Semaev m-fold decomposition with i.i.d. Uniform{1,...,B}
indices and the BKK sparse check (testing (B/2)^{m-1} pairs instead of B^{m-1}):

    gamma_m ≥ (m+1) / 2^m    (provable lower bound on yield retention)
    speedup ≥ (m+1) / 2      (provable speedup over standard Semaev)

## Proof

**Lemma**: The BKK check iterates (m-1)-tuples from F[:B/2]^{m-1} and finds
decomposition T = P_{a_1}+...+P_{a_m} iff at least m-1 of the m indices lie in {1,...,B/2}.

**Theorem**: With indices i.i.d. Uniform{1,...,B}, the number in the first half is
Binomial(m, 1/2). Therefore:

    gamma_m = Pr[at least m-1 of m indices in {1,...,B/2}]
            = Σ_{k=m-1}^{m} C(m,k) / 2^m
            = (m + 1) / 2^m

    Speedup = gamma_m × (B^{m-1} / (B/2)^{m-1}) = gamma_m × 2^{m-1}
            = (m+1) / 2^m × 2^{m-1}
            = (m+1) / 2

## Verification (at p=1009, near-optimal B)

| m | gamma lb | gamma empirical | speedup lb | speedup empirical |
|---|----------|-----------------|------------|-------------------|
| 2 | 0.750 | 0.86 | **1.5x** | 1.72x |
| 3 | 0.500 | 0.66 | **2.0x** | 2.62x |
| 4 | 0.313 | 0.35 | **2.5x** | 2.82x |
| 5 | 0.188 | 0.27 | **3.0x** | 4.24x |

EC group law gives ~0.1 bonus in gamma above the theoretical floor.

## Cryptographic significance

At N=2^256 (m_opt ≈ 4-5): **guaranteed speedup ≥ 2.5-3.0x** (theorem), observed ~3.3x.

This is the FIRST PROVABLE speedup for prime-field ECDLP Semaev index calculus
from the BKK mixed-volume theory. The theorem provides the combinatorial foundation
for the empirical improvements in KN-FIND-2a8b7e.

## Correction 2026-10-24 (CORR-20261024-851c82)

Scoped to two claims only; the theorem is unaffected.

1. The last sentence of "Cryptographic significance" above, that the theorem
   "provides the combinatorial foundation for the empirical improvements in
   KN-FIND-2a8b7e", is refuted. EV-FALSIFY-67150b (2026-08-08) found the
   geometric growth law of KN-FIND-2a8b7e confounded with shrinking B, and the
   geometric and linear laws cannot both hold. KN-FIND-2a8b7e is superseded by
   KN-FIND-921fbf under CORR-20261024-851c82. The "observed ~3.3x" at N=2^256
   is that finding's refuted extrapolation.
2. The "gamma empirical" column of the verification table above (0.86, 0.66,
   0.35, 0.27) is a per-target success measurement, not per-decomposition
   retention, so the statement "EC group law gives ~0.1 bonus in gamma above the
   theoretical floor" is an estimand artefact and is withdrawn (EV-FALSIFY-67150b
   O-6: measured per-decomposition retention is 0.7497 at m=2 and 0.5000 at m=3,
   against the proved (m+1)/2^m = 0.75 and 0.50). The "speedup empirical" column
   inherits this and is likewise not a measurement of the speedup in the theorem.
   Read the column as per-target success at the B of each row.

What stands: the derivation of per-decomposition retention (m+1)/2^m and the
resulting speedup (m+1)/2. EV-FALSIFY-67150b matches the retention exactly at
m=2,3. At m=4,5 the measured values exceed it and shrink toward it as B grows
(m=5: 0.2309, 0.2182, 0.2113 at B = 12, 18, 24, against 0.1875), so the theorem
is reproduced to within a B-dependent residual there, not exactly.
