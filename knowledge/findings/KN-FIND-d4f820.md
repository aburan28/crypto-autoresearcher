---
id: KN-FIND-d4f820
type: internal_finding
title: H-PSEUDO empirical measurement — DL character sum constant C(p) ~ p^{0.055} at toy prime-field scale
tags: [hpseudo, character-sum, fourier, discrete-log, semaev, factor-base, toy-scale, scaling]
confidence: preliminary_empirical
evidence_level: toy_measurement
source_refs: [BATCH-073, BATCH-074, BATCH-076, BATCH-077, EV-BGT-816536, EV-PSEUDO-28f914, EV-PSEUDO-65a7ea, EV-PSEUDO-6b3146, H-PSEUDO-83817b]
internal_refs: [EV-BGT-816536, EV-PSEUDO-28f914, EV-PSEUDO-65a7ea, EV-PSEUDO-6b3146, H-PSEUDO-83817b]
proof_status: empirical_only
proof_refs: []
added: '2026-08-04'
superseded_by: null
---

## Finding

**H-PSEUDO**: For F = {P ∈ E(F_p) : x(P) < t} (small-x factor base with |F| = B),
the additive character sum:
max_{k=1,...,N-1} |Σ_{P ∈ F} e^{2πi k·DL_G(P)/N}|
has been empirically measured at p ∈ {1009, 2003, 4001} via full-range DFT.

## Empirical result (4-point scaling, BATCH-073..077)

The constant C = max|hat{1_F}(k)| / sqrt(B) (full k-range DFT):

| p | C (mean) | log2(p) |
|---|---------|---------|
| 1009 | 3.0 | 10.0 |
| 4001 | 3.5 | 11.9 |
| 9001 | 3.7 | 13.1 |
| 50021 | 3.84 | 15.6 |

**Best fit: C(p) ~ p^{0.055}** (very slow power law, consistent with O((log p)^{0.5}) or O(log log p)).
The C ratio from p=1009 to p=50021 is 3.84/3.0 = 1.28; the log(p) ratio would be 1.56 → C grows slower than log(p).

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
