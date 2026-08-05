---
id: KN-FIND-d4f820
type: internal_finding
title: H-PSEUDO empirical measurement — DL character sum constant C ≈ 3 at toy prime-field scale
tags: [hpseudo, character-sum, fourier, discrete-log, semaev, factor-base, toy-scale]
confidence: preliminary_empirical
evidence_level: toy_measurement
source_refs: [BATCH-073, BATCH-074, EV-BGT-816536, EV-PSEUDO-28f914, H-PSEUDO-83817b]
added: '2026-08-04'
superseded_by: null
---

## Finding

**H-PSEUDO**: For F = {P ∈ E(F_p) : x(P) < t} (small-x factor base with |F| = B),
the additive character sum:
max_{k=1,...,N-1} |Σ_{P ∈ F} e^{2πi k·DL_G(P)/N}|
has been empirically measured at p ∈ {1009, 2003, 4001} via full-range DFT.

## Empirical result

The constant C = max|hat{1_F}(k)| / sqrt(B):
- p=1009, B_frac=0.05: C ≈ 3.2 (full k-range)
- p=1009, B_frac=0.10: C ≈ 2.8 (full k-range)
- p=2003, B_frac=0.05: C ≈ 2.6 (partial k=1..300)
- p=4001, B_frac=0.05: C ≈ 2.9 (partial k=1..300)

**No systematic growth of C with p** across the tested range p=1009..4001.

## Significance

If H-PSEUDO holds with constant C (no growth), then:
1. The Semaev yield satisfies: Pr[T ∈ m·F] ≤ B^m/(m!N) + O(C^m * B^{m/2} / N^{m/2 + 1/2})
2. The error term is negligible for the parameter range used in index calculus
3. Together with the Bezout no-go for algebraic factor bases, this provides
   (conditional on H-PSEUDO) a tight upper bound on Semaev index calculus complexity:
   exp(c·sqrt(log N · log log N)) is the ceiling

## Caveats

- Toy scale only (p ≤ 4001)
- Partial k-range at p=2003, 4001 (k=1..300, not full N-1)
- Not a proof; H-PSEUDO cannot be proved by current techniques (DL circularity)
- A crypto-scale version of this measurement would require solving ECDLP (circular)
