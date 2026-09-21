# Non-Quaternion Framework Analysis: MSI as Potential Sub-p^{1/3} Channel

**Task**: TASK-20260804-55952a (GOAL-SSI-001/BATCH-046)  
**Status**: ONE VIABLE DIRECTION IDENTIFIED (unverified)

## The MSI (Modular Symbol Inversion) Direction

### Source: KN-LIT-1662 (Colò 2026, arXiv:2603.29789)

The paper establishes:
1. A computable map: {O-oriented ss curves} → H₁(X₀(N), cusps, Z) (modular symbols)
2. ℓ-adic period computation: pairing modular symbols with weight-2 cusp forms via Coleman integration
3. This yields: short combinatorial path → truncated vector in (Z/ℓ^m Z)^d

The MSI problem: recover a short homology representative from truncated ℓ-adic period data.

### Why this MIGHT circumvent the p^{1/3} barrier

The quaternion lattice barrier is specific to the REDUCED NORM metric on the
rank-3 traceless sublattice. The Petersson/period metric on modular symbols is
a DIFFERENT metric on essentially the same underlying space (via Jacquet-Langlands).

**The key mathematical question**: Does the map
  quaternion_element → modular_symbol → ℓ-adic_period_vector
introduce NON-UNIFORM metric distortion?

If YES: "short" in the period metric ≠ "short" in the reduced-norm metric.
The p^{1/3} bound applies to REDUCED NORM, not to PERIOD NORMS. A vector that
is long under Nrd (≥ p^{1/3}) might be short under the period metric, and
finding it via MSI inversion might be computationally cheaper.

If NO: the metrics are uniformly equivalent and p^{1/3} still applies.

### The Gross-Waldspurger connection

The relationship between the two metrics is governed by the Gross-Waldspurger formula:
  ||Φ_f||²_Petersson ∝ L(f, 1/2) · ||f||²

where f ranges over Hecke eigenforms. The factor L(f, 1/2) (the central L-value)
varies with f. This means:

- Different eigenspaces have different metric scaling
- The "shortest vector" under the period metric may lie in an eigenspace where
  L(f, 1/2) is anomalously large (amplifying the Petersson norm relative to Nrd)
- In such an eigenspace, quaternion elements of norm p^{1/3} would have LARGER
  period-norm, while elements of norm < p^{1/3} (below the quaternion minimum)
  might have detectable period signatures

### What needs to be checked (decisive test)

1. **Read Gross 1987 "Heights and special values of L-series"**:
   Does the norm comparison ||·||_Petersson vs Nrd have UNIFORM or
   EIGENSPACE-DEPENDENT distortion?

2. **Read Colò 2026 (arXiv:2603.29789) Section on MSI complexity**:
   What is the claimed or conjectured complexity of MSI?
   Does the paper suggest sub-p^{1/3} is achievable?

3. **The falsification**: If ||α||²_Petersson = c(f) · Nrd(α) where c(f) = L(f,1/2)/⟨f,f⟩
   varies by at most polynomial factors (i.e., c_min/c_max = p^{o(1)}), then
   the metrics are polynomially equivalent and p^{1/3} still applies.
   But if c(f) varies by p^{Ω(1)} factors (exponential in log p), there's room.

### Preliminary assessment: metric discrepancy likely EXISTS

Known facts from analytic number theory:
- L(f, 1/2) for weight-2 newforms of level p varies in [0, O(log p)] (on average ~1)
- The Lindelöf hypothesis gives |L(f, 1/2)| ≤ p^{ε} for all ε > 0
- The Generalized Riemann Hypothesis gives L(f, 1/2) ≥ 0 with the possibility L(f, 1/2) = 0 (vanishing)
- Vanishing L-values correspond to eigenspaces where the Petersson norm
  COLLAPSES relative to Nrd — these are "blind spots" in the period encoding

This means: the metric distortion is at most polynomial (Lindelöf: ≤ p^ε).
For sub-p^{1/3}: we need distortion ≥ p^{1/3} in some eigenspace.
Under Lindelöf: distortion ≤ p^ε for any ε. This means...

**THE LIKELY CONCLUSION**: Under standard conjectures (GRH/Lindelöf),
the metric distortion is sub-polynomial (p^{o(1)}), which means the two
metrics are polynomially equivalent and p^{1/3} applies to BOTH.

However: this is CONDITIONAL on Lindelöf. Without Lindelöf, larger L-values
are not ruled out. The unconditional bound is L(f, 1/2) ≤ p^{1/4+ε} (subconvexity).

### Open question (not yet resolved)

Could the MSI problem be solvable WITHOUT using the L-value scaling?
I.e., could the COMPUTATIONAL STRUCTURE of Coleman integration provide
a different handle than the metric comparison suggests?

This remains genuinely open and requires reading the Colò paper in full.

## Other directions (all closed)

- Direction A (Dieudonné): rank_Z_p(M(E)) = 4, same lattice geometry as quaternion
- Direction B (canonical lift): supersingular E has no lift to elliptic curve in char 0
- Direction C (Rapoport-Zink): computing Gross-Hopkins period requires End(E)
- Direction D (crystalline): identical to Dieudonné by Dieudonné-Manin

## Verdict

**ONE direction remains genuinely open**: The MSI problem (KN-LIT-1662).
The metric discrepancy argument is likely killed by Lindelöf (distortion ≤ p^{ε}),
but the COMPUTATIONAL structure of Coleman integration might provide a channel
not captured by the metric comparison. This requires reading the full paper.

**This is the last remaining candidate for sub-p^{1/3} in the SSI campaign.**
