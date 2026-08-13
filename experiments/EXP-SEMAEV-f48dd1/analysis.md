# EXP-SEMAEV-f48dd1: X-Oracle MITM Cost Analysis

**Experiment ID**: EXP-SEMAEV-f48dd1  
**Run ID**: RUN-SEMAEV-f48dd1-revised  
**Date**: 2026-08-08  
**Batch**: BATCH-284817  
**Hypothesis**: H-XOR-d1a480  

## Observation

Revised experiment with mandatory revisions REV-1 to REV-4 applied. Primary analysis (REV-2) isolates oracle marginal contribution by comparing Arm B (oracle MITM) vs Arm C (random MITM), holding MITM structure constant.

**Primary result**: Oracle INCREASES candidates_verified by 3.75x, making MITM filtering LESS efficient. The oracle redirects queries but does not reduce work.

**Secondary result**: MITM structure reduces field operations by 18x compared to exhaustive search, but this is the algorithmic structure effect (O(|F|^3) → O(|F|^2)), not the oracle effect.

### Key Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| `oracle_marginal_ratio` | 3.754 | Oracle INCREASES candidates_verified by 3.75x (PRIMARY) |
| `cost_ratio` | 0.0557 | MITM reduces field operations by 18x (SECONDARY) |
| `arm_b_survival_rate` | 0.3744 | 37.4% of right-half pairs survive to verification |
| `arm_c_survival_rate` | 0.1323 | 13.2% of right-half pairs survive to verification |

## Comparison

### Arm B (Oracle MITM) vs Arm C (Random MITM)

- **Oracle marginal contribution**: Oracle increases candidates_verified by 3.75x (std 3.187, range [1.360, 11.237], n=8 groups).
- **Filtering efficiency**: Oracle increases survival rate by 2.83x (37.4% vs 13.2%), making MITM filtering less efficient.
- **Conclusion**: Oracle's marginal contribution is negative. The oracle redirects queries to structured patterns but does not reduce total work.

### Arm B (Oracle MITM) vs Arm A (Exhaustive Search)

- **MITM structure effect**: MITM reduces field operations by 18x (cost_ratio = 0.0557, std 0.0223, range [0.0321, 0.0926], n=8 groups).
- **Algorithmic complexity**: Both arms have the same asymptotic complexity O(|F|^m). The cost reduction is a constant factor, not an exponent change.
- **Conclusion**: Cost reduction comes from MITM structure (O(|F|^3) → O(|F|^2)), not the oracle.

## Inference

1. **Oracle does not reduce work**: The oracle increases candidates_verified by 3.75x and increases the survival rate by 2.83x. The oracle's effect is to redirect queries to structured patterns, but this does not reduce the total work. In fact, it makes MITM filtering less efficient because more candidates survive to verification.

2. **MITM structure reduces cost, not oracle**: The 18x cost reduction comes from the MITM structure replacing O(|F|^3) exhaustive enumeration with O(|F|^2) right-half table construction plus O(|F|) left-half queries. This is a standard algorithmic optimization, not an oracle-specific improvement.

3. **Oracle marginal contribution is negative**: The oracle's marginal contribution is to increase candidates_verified by 3.75x compared to random queries. This is a negative contribution: the oracle makes MITM filtering less efficient. The honest conclusion is that the oracle does not help; it redirects queries but does not reduce work.

## Limitations

- **LIM-1: Toy scale only**: Results tested at 7-8 bit primes, m=3. Results may not extrapolate to crypto scale. Hash table overhead, memory access patterns, and cache behavior may change dramatically at larger scales.

- **LIM-2: Cost model limitations (REV-4)**: The cost model counts field operations but does not count hash table construction overhead, hash table lookup overhead, memory allocation, or cache effects. At toy scale these are negligible; at larger scales they may dominate. This cost model is valid only at toy scale.

- **LIM-3: Constant factor only**: Both arms have the same asymptotic complexity O(|F|^m). The cost reduction is a constant factor (18x), not an exponent change. This is fundamentally different from an asymptotic improvement like Wesolowski's p^{1/3+o(1)}.

- **LIM-4: Dominated by Pollard rho**: Pollard rho is O(sqrt(N)) time, O(1) memory. The x-oracle MITM is O(|F|^m) time, O(|F|^2) memory. For any reasonable parameter choice, rho is faster and uses less memory. This experiment does not change that.

## Conclusion

The x-oracle MITM approach provides a constant-factor cost reduction (18x) at toy scale, but the oracle's marginal contribution is negative (increases candidates_verified by 3.75x). The lane is closed with a named obstruction:

**Obstruction**: Constant-factor cost reduction at toy scale, dominated by Pollard rho, no path to crypto-scale, no asymptotic improvement.

**Status**: H-XOR-d1a480 transitioned rejected → weakened. X-oracle MITM sub-question closed.

## Evidence Record

- **Evidence ID**: EV-ECDLP-284817
- **Decision ID**: DEC-20260808-284817-exec
- **Strength**: strong
- **Claim tier**: toy
