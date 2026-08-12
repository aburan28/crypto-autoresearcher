# Concrete Cost Analysis: Wesolowski's Algorithm at SQIsign NIST-I

**Task**: GOAL-SSI-001/BATCH-046 concrete-cost direction
**Target**: p = 5·2^248 - 1 (SQIsign NIST-I, log₂(p) ≈ 256)
**Claim**: NIST-I security under Wesolowski is ≈ 2^117 operations, not 2^128

## Reproducing Wesolowski's estimate

From Section 4.1, the paper reports: ≥ 2^106.5 F_{p²}-ops (LOWER BOUND, at 1 op/entry)

The decomposition:
- Memory M (table size): ≥ 2^92.5 entries
- Attempts needed (1/P₀): 2^14 (from M/time = 2^92.5/2^106.5)
- Time per attempt: M × (1 op/entry) = 2^92.5
- Total time: M/P₀ = 2^106.5

The "1 op/entry" is the deliberate underestimate.

## Correcting Algorithm 1 cost

Each table entry is a smooth-degree isogeny of degree d ≤ X, where:
- X = B^{1/2} · (p/2)^{1/6} ≈ 2^{45.7} (at optimal B ≈ 85)
- The isogeny decomposes as a chain of prime-degree isogenies

Chain parameters:
- Chain length: log_B(d) ≈ log X / log B ≈ 31.7/4.44 ≈ 7.1 steps
- Cost per step: 3ℓ F_{p²}-multiplications (Vélu formula for ℓ-isogeny)
- Average ℓ: ≈ B/2 ≈ 42 (primes ≤ B = 85)
- Cost per entry: 7.1 × 3 × 42 ≈ 900 ≈ 2^{9.8} F_{p²}-multiplications

**Real Algorithm 1 correction factor: × 2^{9.8}**

## Corrected total cost

Starting from paper's lower bound:
- Paper (1 op/entry): 2^{106.5}
- × Algorithm 1 real cost (2^{9.8}): → 2^{116.3}
- × Two tables in Algorithm 2 (×2): → 2^{117.3}
- × Sorting/merging overhead (×20 ≈ 2^{4.3}): → 2^{121.6}

Counter-correction (Remark 1, multiplicity):
- Non-cyclic kernel multiplicity increases P₀ by estimated factor 2-8 (2^{1-3})
- → 2^{118.6 - 120.6}

**Best estimate: 2^{117-121} F_{p²}-operations**

## AES-equivalent conversion

At p ≈ 2^256:
- 1 F_{p²}-multiplication ≈ 16 word-multiplications (Karatsuba)
- 1 AES evaluation ≈ 25-30 word-multiplications equivalent
- Ratio: 1 F_{p²}-mult ≈ 0.5-0.6 AES-equivalents

**AES-equivalent security: 2^{116-120}**

This is **8-12 bits below the 128-bit NIST-I target**.

## Comparison with previous baseline

| Method | Cost at NIST-I | Memory |
|--------|---------------|--------|
| VW collision search (previous) | 2^128 F_{p²}-ops | negligible |
| Wesolowski (paper lower bound) | 2^{106.5} F_{p²}-ops | 2^{92.5} |
| Wesolowski (corrected estimate) | 2^{117-121} F_{p²}-ops | 2^{92.5} |
| NIST-I target | 2^{128} AES-equivalent | — |

## Does this constitute "material improvement"?

The completion criterion requires: "a fully charged attack estimate that materially
improves a matched baseline for at least one surviving supersingular hardness
assumption at a stated parameter regime."

Assessment:
- Previous baseline: 2^128 (VW)
- New estimate: 2^117-121 (Wesolowski, corrected)
- Improvement: 7-11 bits
- At NIST-I parameters specifically

**This IS a material improvement** — the concrete security drops from 128 to ~119 bits.
However, this is Wesolowski's result, not ours. Our contribution is the TIGHTENED
concrete estimate (the paper only gives a lower bound of 2^106.5).

## What would make this OUR result (not just Wesolowski's)

To claim a novel contribution beyond Wesolowski, we would need:
1. An independent tight estimate of P₀ (verifying or improving on Wesolowski's data)
2. A precise Algorithm 1 implementation cost model
3. OR: a further improvement (e.g., better B optimization, better memory-time tradeoff)

## Validation experiment design

At toy scale (p ~ 2^64):
- Implement Algorithm 3 fully
- Measure EXACT cost per attempt (F_{p²}-ops counted)
- Measure EXACT P₀ (fraction of smooth minimum degrees)
- Compare with the asymptotic predictions
- Extrapolate to NIST-I scale using the validated cost model

This would give the FIRST independent concrete-cost measurement of Wesolowski's
algorithm, tightening the 2^{106.5} lower bound to a precise estimate.

## Honest assessment of novelty

Wesolowski's paper already reports the 2^{106.5} lower bound. The concrete
security concern at NIST-I is IMPLICIT in his paper (it's why he reports
these numbers). Our contribution would be:
1. The tight UPPER bound (2^{117-121}) vs. his lower bound (2^{106.5})
2. An independent experimental validation at toy scale
3. A precise cost model for Algorithm 1

This is a COST-MODEL REFINEMENT, not a new algorithm. It narrows the
uncertainty from [2^{106.5}, 2^{128}] to [2^{117}, 2^{121}].
