# Publicly Computable Non-Simulable Oracle: Search and Closure

## Task: TASK-20260804-053, BATCH-061

## Context

BATCH-060 established:
- Oracle C (incidence) and Oracle D (endomorphism): GGM-SIMULABLE → closed at exp 1/2
- Oracle A (first-jet / dual-number): NON-SIMULABLE but PRIVATELY COMPUTABLE (requires k)
- Oracle B (elliptic net): NON-SIMULABLE but no k-recovery below standard DLP

The open question: is there a PUBLICLY COMPUTABLE, NON-SIMULABLE oracle for prime-field ECDLP?

## Analysis of Candidate Oracles

### Candidate 1: Frobenius twist oracle

The Frobenius map F_p: (x,y) → (x^p, y^p) maps E(F_p) to E^{(p)}(F_p).
For Q = [k]G: F_p(Q) = (x_Q^p, y_Q^p) on E^{(p)}, and F_p(Q) = [k]F_p(G) on E^{(p)}.

Is this publicly computable? YES — computing (x^p mod p, y^p mod p) is trivial.

Is it NON-SIMULABLE? **NO.** In the GGM, the Frobenius oracle maps group labels to new group labels on the twist. The GGM simulator models this as: "G → G', Q → Q'" where G' and Q' are fresh labels with Q' = [k]G' (since k is unchanged). The simulation preserves all group relations. The Frobenius oracle is **GGM-SIMULABLE**.

**Verdict: SIMULABLE → closed by Shoup lower bound.**

### Candidate 2: p-adic height / formal group log

For E/F_p, the formal group logarithm λ: E_1(Z_p) → Z_p satisfies:
λ([N]Q_lift) = k · λ([N]G_lift)

where G_lift, Q_lift are lifts to E(Z_p). This gives k = λ([N]Q_lift) / λ([N]G_lift).

Is this publicly computable? YES — the canonical lift is computable in O(log^2 p) via Satoh's algorithm; the formal group log requires a p-adic lift.

Is it NON-SIMULABLE? **YES** — it depends on the concrete p-adic encoding, not just the group structure.

Does it give k? ONLY IF λ([N]G_lift) ≢ 0 mod p.

- For ANOMALOUS curves (N=p): λ([p]G_lift) ≡ const ≢ 0 mod p (generically). This IS Smart's attack. Works.
- For NON-ANOMALOUS curves (N≠p): λ([N]G_lift) ≡ 0 mod p (the formal group log of [N]G_lift lies in p^2 Z_p for non-anomalous curves, because [N]G_lift has smaller formal parameter than for anomalous). This gives 0/0.

**The p-adic height oracle is non-simulable but gives k mod gcd(N,p) = k mod 1 = no information for non-anomalous prime-order curves. Equivalent to Smart's attack restricted to the anomalous class.**

### Candidate 3: Coleman integral

Coleman's p-adic line integral ∫_G^Q ω for the invariant differential ω.
This is equivalent to the formal group log for points G, Q in E(Z_p).
Same analysis as Candidate 2: provides k only for anomalous curves (equivalent to Smart's attack).

### Candidate 4: Arithmetic-geometric mean (AGM) oracle

The AGM method (Mestre, Satoh) computes #E(F_p) from the curve parameters. The AGM converges to a p-adic number encoding the Frobenius trace. For the ECDLP oracle: can the AGM sequence reveal k?

The AGM computes the TRACE of Frobenius (a property of the curve E itself, independent of any specific point). The trace does not encode k (the DLP scalar is a property of a specific pair of points G, Q, not of the curve alone). **SIMULABLE** at the trace level.

### Candidate 5: Higher Weil pairing / n-th order pairing

The n-th order Weil pairing e_{N^n}: E[N^n] × E[N^n] → μ_{N^n} over F_{p^k} where k = ord_N(p).
For generic prime-field curves: k is exponentially large, making this infeasible.
For special curves: MOV applies (already known).

**No new non-simulable publicly computable oracle from higher pairings.**

## The Three-Tier Classification (confirmed)

| Oracle | Tier | Sub-category |
|--------|------|--------------|
| Frobenius twist | Simulable | GGM simulator applies [k] to both |
| p-adic height / Coleman | Non-simulable | Privately computable (requires anomalous, not non-anomalous) |
| Incidence (from BATCH-060) | Simulable | Shoup lower bound applies |
| Endomorphism (from BATCH-060) | Simulable | Shoup lower bound applies |
| AGM / trace | Simulable | Trace is curve property, not point property |

## Overall Conclusion

**No publicly computable, non-simulable oracle is known for prime-field ECDLP.**

All known candidates are either:
1. GGM-simulable (closed at exp 1/2 by Shoup)
2. Non-simulable but privately computable (require k — only useful to DLP solver)
3. Non-simulable but provide only k mod gcd(N,p) = 0 information (non-anomalous case)

The existence of such an oracle remains an OPEN PROBLEM (KN-OPEN-005). Given the GGM lower bound, any candidate must escape the generic group model via a concrete algebraic property of the specific representation. No such property has been identified despite systematic search.

**Impact on GOAL-ECDLP-001**: The search for a publicly computable non-simulable oracle is a genuine theoretical open problem. Without a new structural ingredient (analogous to Wesolowski's bound on the minimal isogeny degree for supersingular curves), sub-rho prime-field ECDLP remains out of reach by the examined mechanisms.

**Proposed closing action**: Mark the "publicly computable non-simulable oracle" direction as having a named obstruction — the GGM lower bound combined with the failure of all known p-adic/algebraic constructions to give k for non-anomalous curves. Record this as a KN-FIND.
